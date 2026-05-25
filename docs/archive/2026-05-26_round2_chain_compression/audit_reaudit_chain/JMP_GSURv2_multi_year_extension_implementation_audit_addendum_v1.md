> Archived on 2026-05-26 — supplements the original audit which is itself superseded by the readiness re-audit.
> Replacement (kept active): `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_readiness_reaudit_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP GSURv2 Multi-Year Extension — Implementation Audit Addendum v1

**Document:** `docs/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md`
**Supplements:** `docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md`
**Date:** 2026-05-20
**Governing design memo:** `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md`
**Authorisation status:** Construction NOT authorised. This addendum does not authorise
GSURv2 construction, MNL parquet rebuilding, pooled estimation, or welfare computation.

---

## 1. Audit verdict

**NOT READY — CODE CHANGES REQUIRED**

GSURv2 construction for opportunity years 2014 and 2015 cannot proceed in the current
state. The construction script (`scripts/enhanced/enh_prepare_FR_gsur_v2.py`) lacks the
`--opportunity-year` argument and all seven parameterisation changes (C1–C7) specified
in the design memo §9. Even if those changes were implemented, four Eurostat denominator
files and two INSEE benchmark files are absent for y2014 and y2015. The existing y2016
GSURv2 lookup lacks its sidecar JSON (K1 fail) and has an unresolved O7 crosswalk
sign-off (K3 fail), so it cannot be promoted to final status without remediation.

Construction is not authorised by this addendum. The next authorised operational step
is a remediation authorisation memo (§24) that resolves the naming decisions, authorises
external-file retrieval, and authorises script implementation.

---

## 2. Files inspected

The following files were read or inspected to produce this addendum. No file was
modified.

**Specification and decision documents:**
- `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md` — governing design spec
- `docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md` — prior audit
- `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` — alignment rule and final-build requirements

**Construction script:**
- `scripts/enhanced/enh_prepare_FR_gsur_v2.py` (782 lines) — full read; hardcoded
  year-specific values identified at lines 42–45, 192, 209, 165

**External data assets (presence and structure verified):**
- `Data/external/FR_gsur_ruro_v2_stageA.parquet` — 54 rows × 11 cols, year=2016
- `Data/external/FR_gsur_ruro_v2_stageA__sidecar.json` — ABSENT
- `Data/external/FR_gsur.xlsx` — present; Structure sheet confirmed time range 2007–2019+
- `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` — 22 rows, all verified
- `Data/external/NUTS2013-NUTS2016.xlsx` — present
- `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` — present; NUTS2016 codes confirmed
- `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` — present
- `Data/external/insee_001688526_2016.csv` — present; 9.725% annual average
- `Data/external/gsur_benchmark_source.txt` — present
- `Data/external/gsur_denominator_source.txt` — present
- `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` — ABSENT
- `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` — ABSENT
- `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` — ABSENT
- `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` — ABSENT
- `Data/external/insee_001688526_2014.csv` — ABSENT
- `Data/external/insee_001688526_2015.csv` — ABSENT

**MNL parquets and meta (presence and provenance confirmed):**
- `Data/processed/fr/fr_2015_RURO_mnl_v1gsurY2014__mnlmeta.json` — gsur_version: v1_fallback
- `Data/processed/fr/fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json` — gsur_version: v1_fallback
- `Data/processed/fr/fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` — gsur_version: v1_fallback
- `Data/processed/fr/pooled/fr_p3a_harmonised__stage_m1_meta.json` — provisional label confirmed

**Configuration:**
- `config/multi_year/fr_p3a_stage_m1.yaml` — lists `gsur_v2` in `variables_excluded_from_deflation`

---

## 3. Current GSURv2 2016 implementation status

The y2016 GSURv2 lookup exists as
`Data/external/FR_gsur_ruro_v2_stageA.parquet` (54 rows × 11 columns). Confirmed
schema: `year`, `drgn1`, `educ3`, `sex`, `gsur`, `weighting_source`,
`gsur_age_band_used`, `gsur_legacy_misaligned`, `denom_flag`, `n_components`,
`gsur_unreliable`. All year values = 2016. drgn1 range 1–9. The lookup was built by
the Stage A construction documented in
`docs/RURO_GSUR_v2_stageA_implementation_report_v1.md`.

Three provenance issues prevent reuse in final pooled estimation without remediation:

| Requirement | Status | Detail |
|:---|:---:|:---|
| K1 — sidecar JSON present | **FAIL** | `FR_gsur_ruro_v2_stageA__sidecar.json` absent |
| K2 — column-name convention | **FLAG** | Parquet column `gsur`; config YAML lists `gsur_v2`; convention unresolved |
| K3 — O7 crosswalk sign-off | **FAIL** | Implementation report §O7 states PENDING; no MNL merge test run |

The lookup has not been integrated into any MNL parquet. All three survey-year parquets
currently use `FR_gsur_ruro.parquet` (v1 fallback) as the GSUR source, confirmed by
meta JSON inspection. The y2016 GSURv2 lookup is formally built but not yet promoted.

---

## 4. Whether the existing GSURv2 script is parameterizable by opportunity year

**Yes.** The design memo §8 confirms, and direct code inspection corroborates, that
`scripts/enhanced/enh_prepare_FR_gsur_v2.py` can be parameterised by opportunity year
without any modification to the year-invariant construction logic.

The year-invariant logic — population-weighted aggregation over NUTS-2 components per
drgn1 group, education alignment (educ3 to ISCED ED0-2 / ED3_4 / ED5-8), age-band
selection (Y20-64), drgn1=9 stub handling, IDF parity check, benchmark validation, and
eleven-column output schema — contains no year-specific references beyond the seven
items listed in §5. Adding one `--opportunity-year` argument and making the six targeted
edits driven by that argument (§5) is sufficient to support any opportunity year for
which the required inputs exist.

One notable finding from FR_gsur.xlsx inspection reduces the code change scope: the
unemployment-rate workbook already covers years 2007 through at least 2019. The script's
`_find_year_col(df_raw, YEAR)` function (line 165) already selects the year-specific
column within the workbook. No new workbook file is needed for y2014 or y2015; C2 (the
UR-input change) is functionally satisfied by C1 without any additional code edit to
`load_gsur_workbook()`.

---

## 5. Required code changes

Seven parameterisation changes must be made to
`scripts/enhanced/enh_prepare_FR_gsur_v2.py` before construction can be run for any
year other than 2016. None of these changes may be made in this audit session. They
require a code-change authorisation in the remediation memo (§24).

| Code | Location | Current hardcoded value | Required change |
|:---|:---|:---|:---|
| C1 | Line 44 | `YEAR = 2016` | Add `argparse` `--opportunity-year` (integer, required); set `YEAR` from argument |
| C2 | Line 165 | `_find_year_col(df_raw, YEAR)` uses global `YEAR` | Satisfied by C1 — no additional edit needed; `_find_year_col` already parameterises correctly once `YEAR` is set from the argument |
| C3 | Line 192, `load_d2()` | `"lfst_r_lfsd2pop_FR_2016.tsv"` | Replace `2016` literal with `{YEAR}` f-string |
| C4 | Line 209, `load_d1()` | `"lfst_r_lfp2acedu_FR_2016.tsv"` | Replace `2016` literal with `{YEAR}` f-string |
| C5 | Line 45 | `BENCHMARK_PCT = 9.725` | Read from `Data/external/insee_001688526_{YEAR}.csv`; compute mean of quarterly values |
| C6 | Line 42 | `"FR_gsur_ruro_v2_stageA.parquet"` | Replace with year-tagged path `"FR_gsur_ruro_v2_stageA_y{YEAR}.parquet"` |
| C7 | Absent | No sidecar output block | Add sidecar JSON write at end of `__main__`; fields per §13 |

C1 is the root change; C2 requires no additional edit; C3, C4, C5, C6 are each a
single-line substitution; C7 adds a new sidecar output block. Total net edits: fewer
than 30 lines across all seven changes. The year-invariant construction logic is not
touched.

**C6 naming decision:** The year-tagged scheme
(`FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`) requires updating all references to the
existing un-tagged y2016 file. Alternatively, new-year outputs are tagged while the
existing y2016 file retains its current name; this must be documented explicitly.
The remediation memo must record the adopted convention before code changes begin.

---

## 6. Required external assets for opportunity year 2014

The following external inputs are required to run the parameterised script with
`--opportunity-year 2014`. All are absent from `Data/external/`.

| Asset | Required path | Status | Retrieval source |
|:---|:---|:---:|:---|
| D2 population denominator | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | **MISSING** | Eurostat SDMX-CSV API, dataset `lfst_r_lfsd2pop`, `startPeriod=2014&endPeriod=2014`, filtered to FR NUTS-2 (same endpoint as 2016 file; documented in `gsur_denominator_source.txt`) |
| D1 active-population denominator | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | **MISSING** | Eurostat SDMX-CSV API, dataset `lfst_r_lfp2acedu`, same endpoint |
| National benchmark | `Data/external/insee_001688526_2014.csv` | **MISSING** | INSEE BDM API, series 001688526, year 2014 (same endpoint documented in `gsur_benchmark_source.txt`) |

Provenance entries for each file must be added to `Data/external/gsur_denominator_source.txt`
and `Data/external/gsur_benchmark_source.txt` at retrieval time, recording the API
call parameters, download date, raw quarterly values (for the benchmark), and computed
annual average.

The unemployment-rate workbook (`Data/external/FR_gsur.xlsx`) already covers 2014 and
is confirmed reusable. No additional workbook retrieval is needed.

---

## 7. Required external assets for opportunity year 2015

The following external inputs are required to run the parameterised script with
`--opportunity-year 2015`. All are absent from `Data/external/`.

| Asset | Required path | Status | Retrieval source |
|:---|:---|:---:|:---|
| D2 population denominator | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | **MISSING** | Eurostat SDMX-CSV API, dataset `lfst_r_lfsd2pop`, `startPeriod=2015&endPeriod=2015`, filtered to FR NUTS-2 |
| D1 active-population denominator | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | **MISSING** | Eurostat SDMX-CSV API, dataset `lfst_r_lfp2acedu`, same endpoint |
| National benchmark | `Data/external/insee_001688526_2015.csv` | **MISSING** | INSEE BDM API, series 001688526, year 2015 |

The same provenance-documentation requirement applies: add entries to
`gsur_denominator_source.txt` and `gsur_benchmark_source.txt` at retrieval time.

The unemployment-rate workbook already covers 2015 and is confirmed reusable.

---

## 8. Required provenance lock for opportunity year 2016

The existing `Data/external/FR_gsur_ruro_v2_stageA.parquet` may be reused as the
y2016 lookup only after all three provenance-lock requirements (K1, K2, K3 from design
memo §15) are satisfied.

**K1 — Sidecar JSON.** A sidecar file
`Data/external/FR_gsur_ruro_v2_stageA__sidecar.json` (or `_y2016__sidecar.json` if
renamed) must be written with the fields specified in §13. This is a documentation
step, not a data rebuild. It may be written post-hoc from the implementation report, or
it may be produced by rebuilding y2016 under the parameterised script with
`--opportunity-year 2016`. The rebuild path is preferred because it also resolves K3.

**K2 — Column-name convention.** The decision between `gsur` (current parquet column)
and `gsur_v2` (config YAML forward-reference in `variables_excluded_from_deflation`)
must be recorded before any parquet rebuild. The three options are: (a) rename the
Stage A output column to `gsur_v2` in the parameterised script; (b) update
`fr_p3a_stage_m1.yaml` to list `gsur`; (c) confirm the prep script renames the column
on merge. The remediation memo must record the adopted option.

**K3 — O7 crosswalk sign-off.** The implementation report §O7 records the crosswalk
sign-off as PENDING. O7 requires a merge test: after any GSURv2 lookup is constructed
(or confirmed reusable), merge it with the corresponding MNL draw-expanded parquet and
verify that `gsur` values are non-null and plausible across all drgn1 cells. O7 must be
run for each opportunity year at construction time, not deferred.

Until K1, K2, and K3 are resolved, the y2016 lookup's provenance is not locked and it
cannot be promoted to final status.

---

## 9. Crosswalk availability and stability

`Data/external/fr_drgn1_to_nuts2_crosswalk.csv` is present (22 rows, 5 columns). All
22 rows carry `verified_against_eurostat=YES`. The crosswalk maps `drgn1` (1–8) to
NUTS2016 codes:

| drgn1 | NUTS-2 components |
|:---:|:---|
| 1 | FR10 (Île-de-France) — single component |
| 2 | FRB0, FRC1, FRD1, FRD2, FRE2, FRF2 (6 components) |
| 3 | FRE1 (Nord-Pas-de-Calais) — single component |
| 4 | FRC2, FRF1, FRF3 (3 components) |
| 5 | FRG0, FRH0, FRI3 (3 components) |
| 6 | FRI1, FRI2, FRJ2 (3 components) |
| 7 | FRK1, FRK2 (2 components) |
| 8 | FRJ1, FRL0, FRM0 (3 components) |
| 9 | DOM stub — zero components; NaN-filled in output |

The crosswalk is year-invariant. The drgn1-to-NUTS-2 mapping is a function of the EUROMOD
regional definition and the 2016 NUTS reform correspondence, neither of which depends on
the opportunity year. The crosswalk applies identically to the 2014, 2015, and 2016
Eurostat extracts without modification.

NUTS-vintage compatibility: the 2016 denominator TSV and the FR_gsur.xlsx Structure
sheet both confirm NUTS2016 codes (FRB0, FRD2, FRE2, etc.) are used throughout,
including historical years. Eurostat applies retroactive NUTS revision, so the 2014 and
2015 extracts retrieved from the current Eurostat API are expected to use NUTS2016 codes
compatible with the crosswalk. The L-vintage check must confirm this at retrieval time.

`Data/external/NUTS2013-NUTS2016.xlsx` is present as a fallback if any vintage mismatch
is discovered.

---

## 10. Denominator availability

| File | Year | Status | Notes |
|:---|:---:|:---:|:---|
| `lfst_r_lfsd2pop_FR_2016.tsv` | 2016 | PRESENT (357,080 bytes) | D2 denominator; NUTS2016 codes confirmed |
| `lfst_r_lfp2acedu_FR_2016.tsv` | 2016 | PRESENT (88,055 bytes) | D1 denominator; NUTS2016 codes confirmed |
| `lfst_r_lfsd2pop_FR_2015.tsv` | 2015 | **MISSING** | Must be retrieved |
| `lfst_r_lfp2acedu_FR_2015.tsv` | 2015 | **MISSING** | Must be retrieved |
| `lfst_r_lfsd2pop_FR_2014.tsv` | 2014 | **MISSING** | Must be retrieved |
| `lfst_r_lfp2acedu_FR_2014.tsv` | 2014 | **MISSING** | Must be retrieved |

**Structural note (from `gsur_denominator_source.txt`):** The `lfst_r_lfp2acedu` table
(D1 active-population denominator) does not publish 10-year age bands (Y20-29, Y30-39,
etc.) at NUTS-2 level. Only broad bands Y15-74, Y25-64, Y_GE15 are available. This is a
structural limitation of the Eurostat publication, unchanged across years. The Stage A
construction uses the D2 population denominator (`lfst_r_lfsd2pop`) as the operational
denominator for all cells; this design decision is year-invariant and carries over to
y2014 and y2015 without change.

Reliability-flag caveat: the 2014 and 2015 D2 files may carry different `u` / `u_u`
flag patterns from 2016. The construction must record year-specific flags in `denom_flag`
and `gsur_unreliable`; it must not assume the 2016 flag pattern carries over.

---

## 11. Benchmark availability

| File | Year | Status | Annual-average value |
|:---|:---:|:---:|:---:|
| `insee_001688526_2016.csv` | 2016 | PRESENT | **9.725%** (Q1=9.9, Q2=9.7, Q3=9.6, Q4=9.7) |
| `insee_001688526_2015.csv` | 2015 | **MISSING** | Unknown — must be retrieved |
| `insee_001688526_2014.csv` | 2014 | **MISSING** | Unknown — must be retrieved |

INSEE BDM series 001688526 is the ILO unemployment rate (SA, metropolitan France).
The endpoint is documented in `Data/external/gsur_benchmark_source.txt`. The 2014 and
2015 annual-average values are unknown until retrieval; they must be computed from
quarterly data. The design memo §12 notes that the French national unemployment rate
rose from 2014 to 2015 and declined toward 2016, so the y2014 and y2015 benchmarks are
expected to be distinct from 9.725%.

The benchmark is a validation check (L5), not a construction input. The constructed
GSUR national aggregate must be consistent with the benchmark; the benchmark does not
enter the cell-level aggregation formula. Missing benchmark files block the L5 check
but not the aggregation itself.

---

## 12. Expected GSURv2 output files

After construction is complete (all inputs present, C1–C7 implemented, K1–K3 resolved),
the expected GSURv2 lookup files are:

| Output file | Opportunity year | Required by survey year | Status |
|:---|:---:|:---:|:---:|
| `Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet` | 2014 | FR_2015 | **TO BE BUILT** |
| `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` | 2015 | FR_2016 | **TO BE BUILT** |
| `Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet` (or current un-tagged path) | 2016 | FR_2017 | EXISTING — provenance lock required |

Each lookup must replicate the eleven-column schema of the existing y2016 lookup:
`year`, `drgn1`, `educ3`, `sex`, `gsur`, `weighting_source`, `gsur_age_band_used`,
`gsur_legacy_misaligned`, `denom_flag`, `n_components`, `gsur_unreliable`.

Expected row count per lookup: 54 (48 active cells: drgn1 ∈ {1–8} × educ3 ∈ {0,1,2}
× sex ∈ {M,F} = 8 × 3 × 2; plus 6 drgn1=9 NaN stubs: educ3 ∈ {0,1,2} × sex ∈ {M,F}).

**Note on column name for downstream use (K2):** The `gsur` column name in the lookup
must be consistent with the column name that the prep script (`enh_RURO_prep_mnl_basic.py`)
will write into the MNL parquet, and with the name listed in
`config/multi_year/fr_p3a_stage_m1.yaml` `variables_excluded_from_deflation`. The
config currently lists `gsur_v2`. This discrepancy must be resolved before construction
(§8, K2).

---

## 13. Expected sidecar metadata files

Each GSURv2 lookup must be accompanied by a sidecar JSON file carrying full build
provenance. The design memo §14 specifies the required schema.

| Sidecar file | Lookup it documents |
|:---|:---|
| `Data/external/FR_gsur_ruro_v2_stageA_y2014__sidecar.json` | y2014 lookup |
| `Data/external/FR_gsur_ruro_v2_stageA_y2015__sidecar.json` | y2015 lookup |
| `Data/external/FR_gsur_ruro_v2_stageA_y2016__sidecar.json` (or `_stageA__sidecar.json`) | y2016 lookup |

Required fields in each sidecar (design memo §14):

| Field | Content |
|:---|:---|
| `opportunity_year` | Integer; e.g. 2014 |
| `gsur_source` | `"GSURv2"` |
| `construction_script` | `"enh_prepare_FR_gsur_v2.py"` + version/commit |
| `input_unemployment_rate_file` | Path to FR_gsur.xlsx + Eurostat dataset ID |
| `input_population_denominator_file` | Path to `lfst_r_lfsd2pop_FR_{year}.tsv` |
| `input_national_benchmark_file` | Path to `insee_001688526_{year}.csv` + annual-average value |
| `crosswalk_file` | `"fr_drgn1_to_nuts2_crosswalk.csv"` + `verified_against_eurostat = YES` |
| `nuts_vintage` | NUTS vintage of extract + L-vintage check result |
| `denominator_type` | `"D2_population"` |
| `age_band` | `"Y20-64"` |
| `reliability_flags` | Year-specific `denom_flag` and `gsur_unreliable` summary |
| `validation_results` | Per-year L-check results (L-vintage, L1, L4, L5, L-coverage, L-flag, L-range) |
| `construction_timestamp` | ISO-8601 UTC timestamp |

The sidecar for the y2016 lookup may be written post-hoc from the implementation
report rather than via a data rebuild, provided K3 (O7 sign-off) is concurrently
resolved. The sidecars for y2014 and y2015 are produced by the parameterised script
run (C7).

---

## 14. Required validation checks

Each new opportunity-year lookup must pass the following checks before it is accepted,
per the design memo §13 and the GSUR rebuild specification v2.1 §13.

| Check | Description | Pass criterion |
|:---|:---|:---|
| L-vintage | NUTS-vintage compatibility | Year-specific Eurostat extract uses NUTS2016 codes matching the crosswalk; no old-NUTS-2013 codes present |
| L1 | Schema integrity | Exactly 11 columns; exactly 54 rows (48 active + 6 NaN stubs) |
| L4 | Île-de-France parity | drgn1=1 (FR10 single component): constructed `gsur` values match FR10 source values to tolerance ≤ 0.001 for all 6 educ3 × sex cells |
| L5 | National-benchmark consistency | Population-weighted national GSUR within tolerance of the year-specific INSEE BDM 001688526 annual average; benchmark value cited |
| L-coverage | Cell coverage | All 48 active cells carry non-null `gsur`; all 6 drgn1=9 stubs carry NaN |
| L-flag | Reliability flagging | `denom_flag` and `gsur_unreliable` columns record year-specific Eurostat `u` / `u_u` flags correctly |
| L-range | Rate plausibility | All `gsur` values in [0, 1]; age-profile and education-gradient diagnostics recorded as diagnostic flags, not pass/fail rules |

L4 (Île-de-France parity) is the load-bearing correctness check: it fails if the
population-weighting aggregation or NUTS crosswalk application is incorrect. L-vintage
is the prerequisite check; a vintage mismatch would corrupt the crosswalk mapping.

The O7 MNL-merge check (K3) is a post-construction validation, not a pre-acceptance
check for the lookup file itself. It is run after the lookup is accepted, at the
downstream MNL-merge step.

---

## 15. Whether construction of y2014 is ready

**No. Construction of y2014 is blocked.**

| Condition | Status |
|:---|:---:|
| FR_gsur.xlsx contains y2014 unemployment-rate data | PASS |
| Crosswalk present and reusable | PASS |
| `lfst_r_lfsd2pop_FR_2014.tsv` present | **FAIL — MISSING** |
| `lfst_r_lfp2acedu_FR_2014.tsv` present | **FAIL — MISSING** |
| `insee_001688526_2014.csv` present | **FAIL — MISSING** |
| C1–C7 code changes implemented | **FAIL — ALL UNIMPLEMENTED** |
| K2 column-name convention resolved | **FAIL — UNRESOLVED** |

y2014 construction cannot begin until: (1) the three missing external files are
retrieved, (2) the C1–C7 code changes are made to the script, and (3) the K2 naming
decision is recorded. Items (2) and (3) require authorisation from the remediation
memo (§24).

---

## 16. Whether construction of y2015 is ready

**No. Construction of y2015 is blocked.**

| Condition | Status |
|:---|:---:|
| FR_gsur.xlsx contains y2015 unemployment-rate data | PASS |
| Crosswalk present and reusable | PASS |
| `lfst_r_lfsd2pop_FR_2015.tsv` present | **FAIL — MISSING** |
| `lfst_r_lfp2acedu_FR_2015.tsv` present | **FAIL — MISSING** |
| `insee_001688526_2015.csv` present | **FAIL — MISSING** |
| C1–C7 code changes implemented | **FAIL — ALL UNIMPLEMENTED** |
| K2 column-name convention resolved | **FAIL — UNRESOLVED** |

Identical blocking conditions as y2014. The code changes (C1–C7) apply to both years
simultaneously; once the script is parameterised and the y2015 external files are
present, the script can be run with `--opportunity-year 2015`.

---

## 17. Whether y2016 provenance lock is ready

**No. The y2016 provenance lock is not ready.**

| Requirement | Status |
|:---|:---:|
| K1 — sidecar JSON present | **FAIL — absent** |
| K2 — column-name convention resolved | **FLAG — unresolved** |
| K3 — O7 crosswalk sign-off | **FAIL — PENDING** |

The existing y2016 lookup is structurally sound (correct schema, 54 rows, L4 parity
confirmed in the implementation report). It is not eligible for promotion to final
status until K1 and K3 are resolved and K2 is decided.

The preferred path is to rebuild y2016 under the parameterised script
(`--opportunity-year 2016`) after C1–C7 are implemented. The rebuild produces a clean
sidecar (K1), gives a natural point to run O7 (K3), and adopts whatever naming
convention is decided for K2/C6. The rebuild does not change the lookup values if the
same inputs are used; it provides provenance parity with the y2014 and y2015 lookups.

If a post-hoc sidecar approach is preferred (avoiding a rebuild), K1 can be satisfied by
writing the sidecar from the implementation report, and K3 must be resolved separately
via a merge check. In either case the K2 naming decision must be made first.

---

## 18. Whether MNL parquets should be rebuilt after GSURv2 construction

**Yes — all three survey-year MNL parquets must be rebuilt after GSURv2 construction
is complete and validated.** This rebuild is a downstream step, separately gated, and
not authorised by this addendum.

| MNL parquet stem | Survey year | Opportunity year | Action |
|:---|:---:|:---:|:---|
| `fr_2015_RURO_mnl_v1gsurY2014__` | FR_2015 | 2014 | Rebuild with `FR_gsur_ruro_v2_stageA_y2014.parquet` once constructed |
| `fr_2016_RURO_mnl_v1gsurY2015__` | FR_2016 | 2015 | Rebuild with `FR_gsur_ruro_v2_stageA_y2015.parquet` once constructed |
| `fr_2017_RURO_mnl_v1gsurY2016__` | FR_2017 | 2016 | Rebuild with y2016 lookup once provenance lock (K1–K3) is resolved |

Rebuilt MNL parquets must adopt a filename stem encoding the GSURv2 source and the
opportunity year — e.g., `fr_2015_RURO_mnl_GSURv2_y2014__` — to distinguish them from
the provisional v1-fallback stems. The harmonised P3a parquet
(`fr_p3a_harmonised.parquet`) must be regenerated after all three survey-year MNL
parquets are rebuilt; the provisional label `provisional_v1_fallback_opportunity_year_aligned`
drops only at that point.

No MNL parquet rebuild is authorised by this addendum. The rebuild gate opens only
after the GSURv2 lookups pass their validation battery and O7 is signed off.

---

## 19. Whether pooled estimation remains blocked

**Yes. Pooled estimation remains blocked.**

Final pooled estimation is blocked by the GSUR year-alignment decision §6:

> *Final pooled estimation requires GSURv2 rebuilt for each opportunity year (2014,
> 2015, 2016) before any year's parquet is promoted to final status. Until GSURv2
> opportunity-year-aligned parquets exist for all three survey years, no pooled result
> may be labelled final.*

The current state satisfies none of the final-estimation prerequisites:
- GSURv2 lookups for y2014 and y2015 do not exist.
- The y2016 GSURv2 provenance lock (K1–K3) is not resolved.
- No GSURv2-based MNL parquet exists for any survey year.
- The P3a harmonised parquet carries the provisional v1-fallback label.
- The cluster-robust SE wrapper and the pooled estimation specification are not
  authorised (construction verdict §17).

A provisional v1-fallback pooled dry-run is a separately gated path (design memo §18)
that requires its own explicit authorisation memo. That authorisation is not granted
here and is not the recommended critical-path activity. The recommended critical path is
to complete the GSURv2 extension first.

---

## 20. Whether welfare remains blocked

**Yes. Welfare computation remains blocked and explicitly not authorised.**

The P3a construction verdict §22 records:

> *`welfare_computation_authorized: false`*

The P3a harmonised meta JSON confirms:

> *`welfare_computation_authorized: false`*

Welfare computation requires, at minimum, a final GSURv2-based pooled dataset, a
final pooled estimation run, and a separate welfare-authorisation memo. None of these
prerequisites exist. Welfare is not in scope for the GSURv2 extension and is not
authorised by any document in this pipeline at this stage.

---

## 21. Missing inputs

All items below are absent from `Data/external/` and are required before GSURv2
construction can proceed for y2014 and y2015. None of these files may be created or
downloaded within this audit session.

**Eurostat denominator files (4 files):**
1. `lfst_r_lfsd2pop_FR_2014.tsv` — D2 population denominator, opportunity year 2014
2. `lfst_r_lfp2acedu_FR_2014.tsv` — D1 active-population denominator, opportunity year 2014
3. `lfst_r_lfsd2pop_FR_2015.tsv` — D2 population denominator, opportunity year 2015
4. `lfst_r_lfp2acedu_FR_2015.tsv` — D1 active-population denominator, opportunity year 2015

**INSEE benchmark files (2 files):**
5. `insee_001688526_2014.csv` — national unemployment-rate benchmark, opportunity year 2014
6. `insee_001688526_2015.csv` — national unemployment-rate benchmark, opportunity year 2015

**Provenance sidecar (1 file — y2016 provenance lock):**
7. `FR_gsur_ruro_v2_stageA__sidecar.json` (or `_y2016__sidecar.json` if renamed) — required
   for K1; absent from `Data/external/`

Retrieval of items 1–6 requires the Eurostat SDMX-CSV API and the INSEE BDM API (both
documented in `Data/external/gsur_denominator_source.txt` and
`Data/external/gsur_benchmark_source.txt`). Retrieval requires external API access and
must be authorised explicitly (§24). Item 7 may be written from the implementation
report or produced by a rebuild; it requires the K2 naming decision and, if post-hoc,
a separate documentation step.

---

## 22. Implementation risks

The following risks apply to the GSURv2 extension after the missing inputs are resolved
and the code changes are authorised.

**R1 — Reliability-flag differences across years.** The existing y2016 build documents
`u` flags for drgn1 groups 2, 4, 5, 6, 7, 8 and `u_u` flags for drgn1=8 Méditerranée.
The y2014 and y2015 extracts may carry different flag patterns. Risk: if a new year has
more suppressed cells, the constructed GSUR for some (drgn1, educ3, sex) cells may rely
on a single contributing NUTS-2 region or a fallback, changing the precision of the
estimate. Mitigation: record year-specific `denom_flag` values; inspect the flag
distribution before accepting the lookup.

**R2 — NUTS-vintage mismatch (low probability).** FR_gsur.xlsx and the 2016 TSV files
already use NUTS2016 codes. Newly retrieved 2014/2015 TSV files are expected to use the
same vintage (Eurostat applies retroactive revision). Risk: if a future API release
changes the vintage encoding, the crosswalk would not apply directly. Mitigation: run
L-vintage check before crosswalk application; `NUTS2013-NUTS2016.xlsx` is available
as a fallback.

**R3 — Benchmark sensitivity for L5 check.** Annual-average French national
unemployment rates for 2014 and 2015 are unknown until retrieved. If the constructed
national GSUR aggregate deviates substantially from the benchmark (as opposed to the
within-tolerance ±0.001 accepted for y2016), the L5 check may require diagnostic
investigation. Risk: the L5 check is a consistency diagnostic, not a construction input,
so a deviation does not invalidate the cell-level rates; it does require an explanation.
Mitigation: cite the benchmark and document the deviation per the rebuild specification
§13.

**R4 — K2 column-name propagation.** If the K2 naming decision (`gsur` vs `gsur_v2`)
is made after the script is modified but before the YAML config is updated (or vice
versa), the harmonised P3a parquet could be produced with an unlisted column that
escapes CPI deflation silently. Mitigation: resolve K2 and update the YAML config
atomically in the same remediation commit.

**R5 — C6 output-path collision.** Running the un-parameterised script for y2016
(current state, no `--opportunity-year` argument) writes to
`FR_gsur_ruro_v2_stageA.parquet` (line 42). If the parameterised script also writes
to a year-tagged path but the old un-tagged file is not deleted, references to the
un-tagged path in the canary and validation scripts would silently continue using the
old file. Mitigation: adopt the year-tagged naming for all three years; update all
references in a single commit.

---

## 23. Recommended next action

**Issue a remediation authorisation memo** before any code is changed, any file is
downloaded, or any construction is attempted. This addendum does not authorise any of
those actions.

The remediation memo must accomplish three things:

1. **Resolve the two naming decisions** that are prerequisites for all subsequent work:
   - K2 / C6: decide whether the GSURv2 output column is named `gsur` or `gsur_v2` and
     whether the output files use year-tagged stems (`_y2014`, `_y2015`, `_y2016`) for
     all three years or retain the un-tagged stem for y2016.
   - Record both decisions explicitly; they gate the YAML config update and the script
     parameterisation.

2. **Authorise retrieval of the six missing external files** (items 1–6 in §21), naming
   each file path and its Eurostat/INSEE source explicitly. The retrieval must also
   produce updated `gsur_denominator_source.txt` and `gsur_benchmark_source.txt` entries.

3. **Authorise implementation of C1–C7** in `scripts/enhanced/enh_prepare_FR_gsur_v2.py`
   as a code-change task, with explicit reference to this addendum's code-change table
   (§5) and the naming decisions made in item 1 above.

The remediation memo is a construction-precondition document, not a construction
authorisation. It authorises the preparatory steps (naming decisions, file retrieval,
script changes) that must be completed before construction can be authorised separately.

---

## 24. Exact construction authorization needed

Before any GSURv2 construction run is executed, a construction authorisation must be
issued as a standalone document. The construction authorisation must state the following
items explicitly:

**Construction authorisation checklist:**

1. The six missing external files (§21 items 1–6) are present in `Data/external/`,
   with provenance entries added to the source-documentation text files.

2. C1–C7 have been implemented in `enh_prepare_FR_gsur_v2.py` and the changes have
   been committed to the repository.

3. The K2 column-name decision has been implemented in both the script (the Stage A
   output column name) and `config/multi_year/fr_p3a_stage_m1.yaml`
   (`variables_excluded_from_deflation`) in the same commit.

4. The C6 output-naming scheme has been adopted and all references to the old un-tagged
   path `FR_gsur_ruro_v2_stageA.parquet` in the canary/validation scripts have been
   updated.

5. The construction is authorised to run for opportunity years **2014** and **2015**
   using `python scripts/enhanced/enh_prepare_FR_gsur_v2.py --opportunity-year {year}`.

6. Each construction run must produce the output parquet and its sidecar JSON (C7) in
   `Data/external/`.

7. Each construction run must be followed immediately by the L-vintage, L1, L4, L5,
   L-coverage, L-flag, and L-range validation checks, with results recorded in the
   sidecar and in a per-year validation report.

8. O7 (crosswalk sign-off) is authorised to run against each new lookup as a merge
   check with the corresponding MNL draw-expanded parquet.

9. If y2016 is rebuilt under the parameterised script, the existing un-tagged
   `FR_gsur_ruro_v2_stageA.parquet` must be retired (or renamed) in the same session;
   both files must not coexist under different names without explicit documentation.

10. This construction authorisation does not authorise MNL-parquet rebuilding, pooled
    estimation, or welfare computation. Those steps require separate authorisations.

**What this addendum does NOT authorise:** script modification, external file retrieval,
GSURv2 construction of any year, MNL parquet rebuilding, pooled estimation (provisional
or final), welfare computation, or any modification to data files. The next authorised
action is the remediation authorisation memo described in §23.

---

*Addendum generated by Claude Code Sonnet, 2026-05-20. No scripts modified, no data
modified, no external APIs called, no models estimated, no construction performed.*