# JMP Multi-Year — External Assets Inventory

**Document:** Results/JMP_multi_year_external_assets_inventory_v1.md
**Date:** 2026-05-19
**Execution-readiness context:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Plan reference:** docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §3, §15

All paths inspected relative to repo root `\\crc\users\hisham\Desktop\Nizam_Hisham\MNL` (local) and `Z:\hisham\EUROMOD-STORAGE` (shared storage). Inspection performed 2026-05-19 without network access to Eurostat API or INSEE BDM.

---

## Summary verdict

**INCOMPLETE — acquisition gaps prevent Stage M1 execution.**

Four external assets required for P3a are absent. One (CPI/HICP CSV) was resolved in this session. Three remain absent: Eurostat denominators for 2015 and 2017, INSEE BDM benchmark for 2015 and 2017, and the GSURv2 stageA parquet extended to 2015 and 2017.

---

## 1. CPI/HICP deflator

| Asset | Required for | Local path | Status |
| --- | --- | --- | --- |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | `m1_harmonise_cpi.py` (all configs) | `Data/external/cpi_hicp_fr_harmonisation.csv` | **PRESENT** (created 2026-05-19; Option B adopted) |

Decision memo: `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`.

---

## 2. Eurostat labour market denominators

Required for GSUR rate computation (unemployment rate denominators by NUTS2 region, education, sex). Two separate datasets:

| Asset | Dataset ID | Years available locally | Years needed for P3a | Status |
| --- | --- | --- | --- | --- |
| `Data/external/lfst_r_lfsd2pop_FR_2016.tsv` | `lfst_r_lfsd2pop` | 2016 only | 2015, 2016, 2017 | **PARTIAL — 2015 and 2017 absent** |
| `Data/external/lfst_r_lfp2acedu_FR_2016.tsv` | `lfst_r_lfp2acedu` | 2016 only | 2015, 2016, 2017 | **PARTIAL — 2015 and 2017 absent** |
| `Data/external/lfst_r_lfsd2pop_2016_full.csv` | Full-download companion | 2016 (full EU) | — | Present (not directly used) |
| `Data/external/lfst_r_lfp2acedu_2016_full.csv` | Full-download companion | 2016 (full EU) | — | Present (not directly used) |

**Gap:** FR-filtered TSVs for 2015 and 2017 are absent. The 2016 full-download CSVs contain all years for all countries — the FR rows for 2015 and 2017 can be extracted from the full-download files without a new API call, subject to confirming the 2015/2017 year codes are present in the files.

**Acquisition task (one-off):** Filter `lfst_r_lfsd2pop_2016_full.csv` and `lfst_r_lfp2acedu_2016_full.csv` for `geo\TIME_PERIOD` rows matching `FR` with year columns 2015 and 2017. Write to `Data/external/lfst_r_lfsd2pop_FR_2015.tsv`, `lfst_r_lfsd2pop_FR_2017.tsv`, `lfst_r_lfp2acedu_FR_2015.tsv`, `lfst_r_lfp2acedu_FR_2017.tsv`. If those year columns are absent from the 2016-vintage full downloads, a fresh Eurostat API call is needed.

---

## 3. INSEE benchmark employment counts

Required for GSUR denominator cross-checking (BDM series 001688526 — emploi total par région et sexe).

| Asset | Years available locally | Years needed | Status |
| --- | --- | --- | --- |
| `Data/external/insee_001688526_2016.csv` | 2016 (and possibly multi-year — not confirmed) | 2015, 2016, 2017 | **UNCERTAIN — 2015/2017 coverage not confirmed** |

**Gap:** The existing `insee_001688526_2016.csv` may already contain 2015 and 2017 rows (INSEE time-series files typically include multi-year data). Requires inspection before declaring it absent. If 2015 and 2017 rows are present, no additional download is needed.

**Acquisition task (if needed):** Download BDM series 001688526 from https://www.insee.fr/fr/statistiques/serie/001688526 for years 2015 and 2017.

---

## 4. GSUR v2 stageA parquet — year extension

| Asset | Years in file | Years needed for P3a | Status |
| --- | --- | --- | --- |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | **2016 only** (54 rows) | 2015, 2016, 2017 | **INCOMPLETE — 2015 and 2017 absent** |
| `Data/external/FR_gsur_ruro.parquet` (v1) | 2007–2024 (all years) | 2015, 2016, 2017 | **PRESENT** (all needed years present) |

**Note:** `FR_gsur_ruro.parquet` (v1) contains rows for all years including 2015, 2016, and 2017. `FR_gsur_ruro_v2_stageA.parquet` is the improved version (uses matched Eurostat denominators, corrects age-band alignment) but only covers 2016.

**Gap:** GSURv2 rates for 2015 and 2017 are absent. The v2 computation requires Eurostat denominators (item 2 above) for the target years, so this gap is downstream of the Eurostat gap.

**Acquisition task:** Once Eurostat denominators for 2015 and 2017 are available, re-run `enh_prepare_FR_gsur_v2.py` (or the relevant section) for years 2015 and 2017 to extend `FR_gsur_ruro_v2_stageA.parquet`.

---

## 5. EU-SILC microdata and DRD files

| Asset | Years | Local path | Status |
| --- | --- | --- | --- |
| `FR_2015_a2.txt` | 2015 | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` | **PRESENT** |
| `FR_2015_a2_2015_03_e2.txt` | 2015 (alt version) | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2_2015_03_e2.txt` | **PRESENT** |
| `FR_2016_a3.txt` | 2016 | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2016_a3.txt` | **PRESENT** |
| `FR_2017_a2.txt` | 2017 | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` | **PRESENT** |
| DRD_FR_2015_a2.xls | 2015 data documentation | `Z:\hisham\EUROMOD-STORAGE\Data\FR\DRD_FR_2015_a2.xls` | **PRESENT** |
| DRD_FR_2016_a3.xls | 2016 data documentation | `Z:\hisham\EUROMOD-STORAGE\Data\FR\DRD_FR_2016_a3.xls` | **PRESENT** |
| DRD_FR_2017_a2.xls | 2017 data documentation | `Z:\hisham\EUROMOD-STORAGE\Data\FR\DRD_FR_2017_a2.xls` | **PRESENT** |

All EU-SILC microdata required for P3a are present on the Z: drive.

---

## 6. NUTS crosswalk

| Asset | Status |
| --- | --- |
| `Data/external/NUTS2013-NUTS2016.xlsx` | **PRESENT** |
| `Data/external/fr_drgn1_to_nuts2_crosswalk.csv` | **PRESENT** |

---

## 7. Completeness summary for P3a

| External asset | Status |
| --- | --- |
| CPI/HICP deflator CSV | **PRESENT** (created 2026-05-19) |
| Eurostat lfst_r_lfsd2pop — 2015, 2017 | **ABSENT** |
| Eurostat lfst_r_lfp2acedu — 2015, 2017 | **ABSENT** |
| INSEE BDM 001688526 — 2015, 2017 | **UNCERTAIN** (inspect existing file) |
| FR_gsur_ruro_v2_stageA — 2015, 2017 | **ABSENT** (downstream of Eurostat gap) |
| EU-SILC microdata — 2015, 2016, 2017 | **PRESENT** |
| NUTS crosswalk | **PRESENT** |

**Three required acquisition tasks remain before Stage M1 can execute.**

---

## 8. Acquisition tasks — ordered by dependency

1. **Inspect `insee_001688526_2016.csv`** for 2015/2017 rows. If present, no download needed. If absent, download from INSEE BDM.
2. **Extract Eurostat 2015/2017 FR rows** from the existing full-download CSVs, or re-download the Eurostat API if the existing files lack those years.
3. **Re-run `enh_prepare_FR_gsur_v2.py`** for years 2015 and 2017 once Eurostat denominators are available, to extend `FR_gsur_ruro_v2_stageA.parquet`.

These three tasks can be completed in a single session once external downloads are resolved. They do not require EUROMOD runs.