# JMP GSURv2 External File Remediation Report v1

*France 2014–2015 inputs | v1 | 2026-05-20*

---

## 1. Retrieval verdict

**All six required external files retrieved and written.** No file is
missing. All four Eurostat denominator TSVs and both INSEE benchmark
CSVs are present in `Data/external/` and parse without error. Provenance
entries have been appended to `gsur_denominator_source.txt` and
`gsur_benchmark_source.txt`. The A2 and A3 audit conditions are now
satisfied for both y2014 and y2015.

| Condition | Status before | Status after |
|-----------|--------------|--------------|
| A2 — y2014/y2015 denominator files | FAIL (absent) | PASS |
| A3 — y2014/y2015 benchmark files | FAIL (absent) | PASS |
| A4 — NUTS-2016 vintage | CONDITIONAL | PASS (verified) |

---

## 2. Files requested

| # | File | Role |
|---|------|------|
| 1 | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | D2 population denominator, opportunity year 2014 |
| 2 | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | D1 active-population denominator, opportunity year 2014 |
| 3 | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | D2 population denominator, opportunity year 2015 |
| 4 | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | D1 active-population denominator, opportunity year 2015 |
| 5 | `Data/external/insee_001688526_2014.csv` | National UR benchmark, opportunity year 2014 |
| 6 | `Data/external/insee_001688526_2015.csv` | National UR benchmark, opportunity year 2015 |

---

## 3. Files successfully retrieved

All six files retrieved and written on 2026-05-20.

| File | Bytes | Lines (incl. header) | Method |
|------|-------|----------------------|--------|
| `lfst_r_lfsd2pop_FR_2014.tsv` | 357,116 | 4,059 | Eurostat SDMX-CSV API → filter to FR NUTS-2 |
| `lfst_r_lfp2acedu_FR_2014.tsv` | 88,241 | 989 | Eurostat SDMX-CSV API → filter to FR NUTS-2 |
| `lfst_r_lfsd2pop_FR_2015.tsv` | 354,590 | 4,028 | Eurostat SDMX-CSV API → filter to FR NUTS-2 |
| `lfst_r_lfp2acedu_FR_2015.tsv` | 87,404 | 979 | Eurostat SDMX-CSV API → filter to FR NUTS-2 |
| `insee_001688526_2014.csv` | 479 | 6 | INSEE BDM API → XML parse → CSV write |
| `insee_001688526_2015.csv` | 484 | 6 | INSEE BDM API → XML parse → CSV write |

For reference, the 2016 files are: `lfst_r_lfsd2pop_FR_2016.tsv` (357,080
bytes, 4,058 lines), `lfst_r_lfp2acedu_FR_2016.tsv` (88,055 bytes, 987
lines), `insee_001688526_2016.csv` (477 bytes, 6 lines). The 2014 and 2015
file sizes are within normal inter-year variation.

---

## 4. Files not retrieved

None. All six required files are present.

---

## 5. Source URLs and extraction parameters

### Eurostat denominator files

All four files retrieved from the same SDMX-CSV API endpoint family as
the existing 2016 files. Full (all-country) downloads were obtained first,
then filtered to the same 22 French NUTS-2 codes used in the 2016 reference.

**lfst_r_lfsd2pop** (D2 population denominator):

| Year | Full-download URL | Full rows | FR rows |
|------|-------------------|-----------|---------|
| 2014 | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfsd2pop?format=SDMX-CSV&startPeriod=2014&endPeriod=2014` | 82,159 | 4,058 |
| 2015 | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfsd2pop?format=SDMX-CSV&startPeriod=2015&endPeriod=2015` | 82,141 | 4,027 |
| 2016 (ref) | `…startPeriod=2016&endPeriod=2016` | — | 4,057 |

**lfst_r_lfp2acedu** (D1 active-population denominator):

| Year | Full-download URL | Full rows | FR rows |
|------|-------------------|-----------|---------|
| 2014 | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfp2acedu?format=SDMX-CSV&startPeriod=2014&endPeriod=2014` | 19,484 | 988 |
| 2015 | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_r_lfp2acedu?format=SDMX-CSV&startPeriod=2015&endPeriod=2015` | 19,427 | 978 |
| 2016 (ref) | `…startPeriod=2016&endPeriod=2016` | — | 986 |

**France filter:** rows where `geo` ∈ {FR10, FRB0, FRC1, FRC2, FRD1, FRD2,
FRE1, FRE2, FRF1, FRF2, FRF3, FRG0, FRH0, FRI1, FRI2, FRI3, FRJ1, FRJ2,
FRK1, FRK2, FRL0, FRM0} — identical to the 2016 reference geo set.

**Delimiter conversion:** API returns comma-separated CSV; converted to
tab-separated TSV matching the 2016 reference file format.

### INSEE benchmark files

**Series:** INSEE BDM 001688526 (ILO unemployment rate, SA, Metropolitan
France, quarterly).

**API endpoint:** `https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526`

The full series was retrieved as SDMX-XML (205 observations covering all
available quarters). The 2014-Q1 through 2015-Q4 values were extracted from
the XML `Obs` elements. The CSV files were written in the exact format of
`insee_001688526_2016.csv` (columns: `series_id`, `period`, `freq`,
`value_pct`, `obs_status`, `note`).

| Year | Access date | OBS_STATUS all quarters |
|------|-------------|------------------------|
| 2014 | 2026-05-20 | A (final/accepted) for all 4 quarters |
| 2015 | 2026-05-20 | A (final/accepted) for all 4 quarters |
| 2016 (ref) | 2026-05-17 | A for all 4 quarters |

---

## 6. Denominator files: structure check

### D2 files (lfst_r_lfsd2pop) — operative denominator

| Attribute | 2014 | 2015 | 2016 reference | Match? |
|-----------|------|------|----------------|--------|
| Columns (12) | DATAFLOW, LAST UPDATE, freq, isced11, sex, age, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS | same | same | ✓ |
| Separator | tab | tab | tab | ✓ |
| Geo codes (count) | 22 | 22 | 22 | ✓ |
| Geo codes (set) | FR10…FRM0 | FR10…FRM0 | FR10…FRM0 | ✓ |
| Age bands (12) | Y15-24, Y25-34, Y35-44, Y45-54, Y55-64, Y15-74, Y20-64, Y15-64, Y25-64, Y_GE15, Y_GE25, Y_GE65 | same | same | ✓ |
| ISCED categories | ED0-2, ED3_4, ED5-8, NRP, TOTAL, UNK | same | same | ✓ |
| Sex values | F, M, T | same | same | ✓ |
| Data rows | 4,058 | 4,027 | 4,057 | ✓ (normal variation) |
| Y20-64 rows present | 330 | 326 | 330 | ✓ |
| NUTS vintage (geo codes) | NUTS-2016 | NUTS-2016 | NUTS-2016 | ✓ |

### D1 files (lfst_r_lfp2acedu) — diagnostic denominator

| Attribute | 2014 | 2015 | 2016 reference | Match? |
|-----------|------|------|----------------|--------|
| Columns (12) | DATAFLOW, LAST UPDATE, freq, unit, sex, age, isced11, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS | same | same | ✓ |
| Separator | tab | tab | tab | ✓ |
| Geo codes (count) | 22 | 22 | 22 | ✓ |
| Age bands (3) | Y_GE15, Y15-74, Y25-64 | same | same | ✓ |
| ISCED categories | ED0-2, ED3_4, ED5-8, NRP, TOTAL | same | same | ✓ |
| Narrow-age bands (Y15-24 etc.) | ABSENT | ABSENT | ABSENT | ✓ (structural limitation, year-invariant) |
| Data rows | 988 | 978 | 986 | ✓ (normal variation) |

**NUTS-2016 vintage confirmed (A4 PASS).** All geo codes in the 2014 and
2015 D2 files are the standard NUTS-2016 four-character French codes
(FR10…FRM0), identical to the 2016 reference set. The A4 condition
(conditional in the audit) is now resolved: PASS.

---

## 7. Benchmark files: structure check

All three benchmark CSV files (2014, 2015, 2016) have identical structure:
6 lines (1 header + 4 quarterly observations + 1 annual-average row).

| Column | All files |
|--------|-----------|
| `series_id` | 001688526 |
| `period` | YYYY-QN or YYYY |
| `freq` | quarterly / — |
| `value_pct` | numeric, 1 decimal |
| `obs_status` | A (accepted) for all quarters; "computed" for annual average |
| `note` | "ILO unemployment rate, SA, Metropolitan France" / computation note |

| Year | Q1 | Q2 | Q3 | Q4 | Annual average | BENCHMARK_PCT (C5) |
|------|----|----|----|-----|----------------|---------------------|
| 2014 | 9.8% | 9.8% | 9.9% | 10.1% | **9.900%** | 9.9 |
| 2015 | 10.0% | 10.2% | 10.0% | 9.9% | **10.025%** | 10.025 |
| 2016 (ref) | 9.9% | 9.7% | 9.6% | 9.7% | **9.725%** | 9.725 |

All quarterly values carry `obs_status=A` (final, accepted by INSEE).
The annual averages are computed as simple means of the four quarterly SA
values, consistent with the 2016 reference methodology.

---

## 8. Flags and missing-cell inventory

### D2 (lfst_r_lfsd2pop) — operative denominator

**Suppression flag pattern (OBS_FLAG=u, unreliable):**

The suppression pattern is structurally year-invariant: the same NUTS-2
regions with small populations or statistical uncertainty carry the `u`
flag in 2014, 2015, and 2016.

| Region | Nature of suppression | 2014 | 2015 | 2016 |
|--------|----------------------|------|------|------|
| FRM0 (Corse) | All ED0-2/ED3_4/ED5-8 cells at Y20-64 flagged `u`; heavily suppressed overall | ✓ | ✓ | ✓ |
| NRP category | Flagged `u` across most regions at all age bands (year-invariant; NRP=no response persons) | ✓ | ✓ | ✓ |
| FRI2 (Limousin) | Second-most suppressed in 2014 (53 cells); small region | ✓ | ✓ | ✓ |

**Y20-64 operative-band suppression counts:**

| Year | Y20-64 total rows | Flagged `u` | Empty OBS_VALUE |
|------|------------------|-------------|-----------------|
| 2014 | 330 | 74 (22.4%) | 11 |
| 2015 | 326 | 70 (21.5%) | 6 |
| 2016 (ref) | 330 | 73 (22.1%) | 12 |

The suppressed Y20-64 cells are dominated by (a) FRM0 for ED0-2/ED3_4/ED5-8
categories and (b) NRP categories across all regions. Neither FRM0 nor NRP
cells are used in the operative GSUR construction (which uses ED0-2, ED3_4,
ED5-8 for the three ISCED groups); the NRP suppression does not affect
usable cells.

**Construction impact:** The same D3 (approximate_uniform) fallback with
reviewer sign-off that applies to FRM0 narrow-age ED cells in 2016 applies
equally to 2014 and 2015. No new suppression pattern discovered.

### D1 (lfst_r_lfp2acedu) — diagnostic denominator

| Year | Total rows | Flagged `u` | Empty OBS_VALUE |
|------|-----------|-------------|-----------------|
| 2014 | 988 | 226 (22.9%) | 42 |
| 2015 | 978 | 213 (21.8%) | 32 |
| 2016 (ref) | 986 | 220 (22.3%) | 44 |

As in 2016: FRM0 all ED cells flagged `u`; NRP category flagged `u` across
most regions. The broad age bands (Y15-74, Y25-64) for the ED0-2/ED3_4/ED5-8
usable cells are generally available for all 22 regions.

### Benchmark files

No flags. All quarterly values carry `obs_status=A` (final and accepted).
No missing cells.

---

## 9. Provenance entries updated or prepared

Both provenance text files have been extended and committed (`e4dd6c2`).

### gsur_denominator_source.txt

Added four new asset entries (Assets 3–6), each recording:
- Dataset name and title
- Eurostat SDMX-CSV API URL with `startPeriod`/`endPeriod` parameters
- Download date (2026-05-20)
- Full-download filename and line count
- Filter applied (same 22 NUTS-2 codes as 2016)
- Output filename and data row count
- Schema confirmation (identical to 2016 reference)
- NUTS-2016 vintage confirmation
- Age-band availability
- Cell-suppression inventory for the Y20-64 operative band
- Construction impact note

### gsur_benchmark_source.txt

Added two new asset entries (2014 and 2015), each recording:
- Series ID and titles
- INSEE BDM API URL
- Access date (2026-05-20)
- Series metadata (FREQ, REF_AREA, UNIT_MEASURE)
- Four quarterly SA values
- Annual average (simple mean) = **BENCHMARK_PCT** value for C5
- Usage note (C5 parameter value for parameterised script)

**BENCHMARK_PCT values recorded:**
- y2014: 9.9% (mean of 9.8, 9.8, 9.9, 10.1)
- y2015: 10.025% (mean of 10.0, 10.2, 10.0, 9.9)
- y2016 (existing): 9.725% (mean of 9.9, 9.7, 9.6, 9.7)

---

## 10. Whether y2014 external inputs are ready

**Yes.** All three y2014 inputs required by the parameterised GSURv2
script are present and verified:

| Input | File | Status |
|-------|------|--------|
| D2 population denominator (C3) | `Data/external/lfst_r_lfsd2pop_FR_2014.tsv` | PRESENT, NUTS-2016, Y20-64 operative band available |
| D1 active-population denominator (C4) | `Data/external/lfst_r_lfp2acedu_FR_2014.tsv` | PRESENT, NUTS-2016, broad-age bands only (diagnostic use) |
| National UR benchmark (C5) | `Data/external/insee_001688526_2014.csv` | PRESENT, BENCHMARK_PCT=9.9, all quarters status=A |
| Unemployment-rate workbook (C2) | `Data/external/FR_gsur.xlsx` | PRE-EXISTING (covers 2007–2019, A1 PASS) |

The A4 (NUTS-vintage) condition is confirmed PASS for y2014.

---

## 11. Whether y2015 external inputs are ready

**Yes.** All three y2015 inputs required by the parameterised GSURv2
script are present and verified:

| Input | File | Status |
|-------|------|--------|
| D2 population denominator (C3) | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | PRESENT, NUTS-2016, Y20-64 operative band available |
| D1 active-population denominator (C4) | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | PRESENT, NUTS-2016, broad-age bands only (diagnostic use) |
| National UR benchmark (C5) | `Data/external/insee_001688526_2015.csv` | PRESENT, BENCHMARK_PCT=10.025, all quarters status=A |
| Unemployment-rate workbook (C2) | `Data/external/FR_gsur.xlsx` | PRE-EXISTING (covers 2007–2019, A1 PASS) |

The A4 (NUTS-vintage) condition is confirmed PASS for y2015.

---

## 12. What remains blocked

The external file retrieval (remediation step A3) is complete. The
remaining remediation prerequisites are:

| Prerequisite | Status |
|-------------|--------|
| A1 — K2 column-naming decision config update | Not yet executed (pending C1–C7 implementation) |
| A2 — C6 output-naming scheme in parameterised script | Not yet executed (pending C1–C7 implementation) |
| A4 — C1–C7 script parameterisation | Not yet implemented |
| A5 — y2016 provenance lock plan document | Not yet prepared |
| A6 — O7 crosswalk sign-off request | Not yet assembled |
| A7 — Post-remediation validation V1–V7 | Not yet run |

Nothing among these remaining steps requires additional external data.
No external file is missing or unretrievable. The one remaining external-
resource question — the NUTS-vintage crosswalk for A4 — is resolved: the
retrieved files use NUTS-2016 codes natively and require no
`NUTS2013-NUTS2016.xlsx` conversion.

GSURv2 construction itself (running the parameterised script with
`--opportunity-year 2014` or `--opportunity-year 2015`) remains not
authorized by the remediation authorization and requires the separate
construction authorization memo.

---

## 13. Whether script remediation may proceed

**Yes.** The external file retrieval unblocks the C1–C7 script
parameterisation task. Before this retrieval, the parameterised script
could not be used for y2014 or y2015 because the D2 path (C3), D1 path
(C4), and benchmark CSV (C5) did not exist locally. Those inputs now
exist. The C1–C7 implementation may proceed with confirmed inputs.

The NUTS-vintage check (V2, the L-vintage verification) is pre-resolved:
all retrieved files use NUTS-2016 codes, matching the crosswalk. V2 can
be confirmed immediately as PASS without any further retrieval.

Conditions for C1–C7 implementation to proceed:
- ✓ D2 files for y2014 and y2015 present
- ✓ D1 files for y2014 and y2015 present (diagnostic completeness)
- ✓ Benchmark CSVs for y2014 and y2015 present; BENCHMARK_PCT values computed
- ✓ NUTS-2016 vintage confirmed for all retrieved files
- ✓ Provenance text files updated

---

## 14. Exact next task

The next remediation task is C1–C7 script parameterisation plus the config
update and the y2016 provenance lock plan, per §§8, 11 A1–A5, and 15
(steps 3–6) of
`docs/archive/2026-05-26_round2_chain_compression/audit_reaudit_chain/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md`.

Specifically, the next Claude Code task should execute:

**Step 3 — Implement C1–C7** in
`scripts/enhanced/enh_prepare_FR_gsur_v2.py`:
- C1: add `--opportunity-year` argument (integer, required); set `YEAR` from it
- C2: no additional edit (workbook already multi-year)
- C3: parameterise D2 path → `lfst_r_lfsd2pop_FR_{YEAR}.tsv`
- C4: parameterise D1 path → `lfst_r_lfp2acedu_FR_{YEAR}.tsv`
- C5: read BENCHMARK_PCT from `insee_001688526_{YEAR}.csv` (annual_average row)
- C6: year-tag output path → `FR_gsur_ruro_v2_stageA_y{YEAR}.parquet`
- C7: add sidecar JSON write with fields per §9 of the authorization
- Do NOT run the script

**Step 4 — Update config YAML**: change `gsur_v2` → `gsur` in
`config/multi_year/fr_p3a_stage_m1.yaml`
`variables_excluded_from_deflation`; commit atomically with step 3.

**Step 5 — Static parameterisation check (V4)**: confirm imports, `--help`,
path templates (`y{YEAR}` pattern), C7 block presence — no script
invocation with `--opportunity-year`.

**Step 6 — Prepare lock-plan document**:
`docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` with sidecar field
specification and lock procedure per §9 of the authorization.

**BENCHMARK_PCT values to hard-code as C5 defaults or read from CSV:**
- y2014: 9.9
- y2015: 10.025
- y2016: 9.725 (existing)

**Do NOT**: run the script, write any parquet, retire any existing file,
rebuild MNL parquets, run pooled estimation, or compute welfare.