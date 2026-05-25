# JMP GSURv2 Multi-Year Extension — Validation Report v1

*France 2014–2015–2016 | v1 | 2026-05-20*

Authorization: `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`
Construction report: `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_report_v1.md`

---

## 1. Validation verdict

**GSURv2 multi-year lookup construction PASSED.**

All validation checks pass for all three opportunity years (2016, 2015,
2014). The y2016 value-identity gate passed with a maximum absolute
`gsur` difference of **0.0** (exact). The y2015 and y2014 lookups pass
all required validation checks. Six output files are present on disk
with the expected structure, schema, and sidecar provenance.

| Check category | y2016 | y2015 | y2014 |
|----------------|-------|-------|-------|
| Row count | PASS | PASS | PASS |
| Unique-key check | PASS | PASS | PASS |
| drgn1 support | PASS | PASS | PASS |
| educ3 × sex support | PASS | PASS | PASS |
| Missing-value check | PASS | PASS | PASS |
| Proportion-unit check | PASS | PASS | PASS |
| Benchmark check (L5) | PASS | PASS | PASS |
| IDF parity check | PASS | PASS | PASS |
| Denominator-source flags | PASS | PASS | PASS |
| Sidecar metadata | PASS | PASS | PASS |
| Value-identity gate | **PASS (0.0)** | n/a | n/a |

---

## 2. Opportunity years covered

| Opportunity year | Survey year | Benchmark (%) | Output parquet |
|-----------------|-------------|--------------|----------------|
| 2016 | FR_2017 | 9.725 | `FR_gsur_ruro_v2_stageA_y2016.parquet` |
| 2015 | FR_2016 | 10.025 | `FR_gsur_ruro_v2_stageA_y2015.parquet` |
| 2014 | FR_2015 | 9.9 | `FR_gsur_ruro_v2_stageA_y2014.parquet` |

Year–survey alignment per `docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md`:
EUROMOD system year lags survey year by one year (FR_2016 uses
opportunity year 2015, etc.).

---

## 3. Row counts

Each output parquet contains exactly **54 rows**:
- 48 active rows: drgn1 ∈ {1, 2, 3, 4, 5, 6, 7, 8} × educ3 ∈ {0, 1,
  2} × sex ∈ {F, M} = 8 × 3 × 2 = 48.
- 6 stub rows: drgn1 = 9, educ3 ∈ {0, 1, 2} × sex ∈ {F, M} = 6.

| Year | Row count | Active rows | Stub rows (drgn1=9) |
|------|-----------|-------------|---------------------|
| 2016 | 54 | 48 | 6 |
| 2015 | 54 | 48 | 6 |
| 2014 | 54 | 48 | 6 |

Result: **PASS** for all three years. Authorization requires 54 rows
(§13, checks Y2015-1, Y2014-1).

---

## 4. Unique-key checks

Keys are `(drgn1, educ3, sex)` within each year-tagged parquet
(each file covers a single opportunity year, so `year` is constant
within each file). No duplicate keys in any file.

| Year | Duplicate keys | Result |
|------|---------------|--------|
| 2016 | 0 | **PASS** |
| 2015 | 0 | **PASS** |
| 2014 | 0 | **PASS** |

The L1 (`L1_unique_keys`) validation check run by the script reported
PASS for all three years.

---

## 5. drgn1 support

All eight active drgn1 values (1–8) are present in each parquet, plus
the drgn1=9 stub group.

| Year | drgn1 values present | Result |
|------|---------------------|--------|
| 2016 | 1, 2, 3, 4, 5, 6, 7, 8, 9 | **PASS** |
| 2015 | 1, 2, 3, 4, 5, 6, 7, 8, 9 | **PASS** |
| 2014 | 1, 2, 3, 4, 5, 6, 7, 8, 9 | **PASS** |

The L3 (`L3_drgn1_support`) check reported PASS for all three years.

---

## 6. educ3 × sex support

All three educ3 levels (0 = low, 1 = medium, 2 = high) and both sex
categories (F, M) are present across all active rows in each parquet.

| Year | educ3 values | sex values | Cross-cells (active) | Result |
|------|-------------|------------|---------------------|--------|
| 2016 | 0, 1, 2 | F, M | 48 | **PASS** |
| 2015 | 0, 1, 2 | F, M | 48 | **PASS** |
| 2014 | 0, 1, 2 | F, M | 48 | **PASS** |

---

## 7. Missing-value checks

For drgn1 1–8 (active rows): `gsur` is non-null for all 48 active rows
in each parquet. For drgn1=9 (stub rows): `gsur` is NaN for all 6 stub
rows in each parquet.

| Year | Active rows with null gsur | Stub rows with non-null gsur | Result |
|------|---------------------------|------------------------------|--------|
| 2016 | 0 | 0 | **PASS** |
| 2015 | 0 | 0 | **PASS** |
| 2014 | 0 | 0 | **PASS** |

The `missing_values` check reported PASS for all three years.

---

## 8. Proportion-unit checks

`gsur` values for active rows (drgn1 1–8) are in proportion units
(0 < gsur ≤ 1). No active row has a `gsur` value outside this range.

| Year | gsur min (active) | gsur max (active) | All in (0, 1] | Result |
|------|------------------|------------------|---------------|--------|
| 2016 | 0.047036 | 0.234 | Yes | **PASS** |
| 2015 | 0.053183 | 0.225 | Yes | **PASS** |
| 2014 | 0.053647 | 0.261 | Yes | **PASS** |

The L2 (`L2_proportion_units`) check reported PASS for all three years.

---

## 9. Benchmark checks

Benchmark values are read from year-specific INSEE BDM 001688526 CSVs
(C5 parameterisation). The L5 national-benchmark check compares the
constructed weighted-average national GSUR against the INSEE annual
figure. The L5 check is a consistency diagnostic; the benchmark
difference is recorded but does not invalidate the cell-level rates.

| Year | Benchmark (%) | Sidecar `benchmark_pct` | L5 check | benchmark_difference_pct | Result |
|------|--------------|------------------------|----------|--------------------------|--------|
| 2016 | 9.725 | 9.725 | PASS | 0.1718 ppt | **PASS** |
| 2015 | 10.025 | 10.025 | PASS | 0.0943 ppt | **PASS** |
| 2014 | 9.9 | 9.9 | PASS | 0.0494 ppt | **PASS** |

Benchmark values match the authorization memo §12 Table 4 exactly.
The L5 (`L5_national_benchmark`) check reported PASS for all three
years. Benchmark differences (0.05–0.17 ppt) are within the expected
range for the population-weighted NUTS-2 → national aggregation
versus the direct INSEE BDM national figure.

---

## 10. IDF parity checks

The IDF parity check confirms that the population-weighted aggregation
for drgn1=1 (Île-de-France, a single-NUTS2-component group comprising
only FR10) reduces to the FR10 source value exactly. Because drgn1=1 is
a single-component group, the weighted average is the value itself, so
the constructed drgn1=1 GSUR must match the FR10 source rates exactly.
A non-zero IDF parity difference indicates a weighting or crosswalk
error.

| Year | idf_parity_difference | Result |
|------|----------------------|--------|
| 2016 | 0.0 | **PASS** |
| 2015 | 0.0 | **PASS** |
| 2014 | 0.0 | **PASS** |

The `IDF_parity` check reported PASS for all three years. The L4
(`L4_idf_crosswalk_sanity`) check also reported PASS for all three
years.

---

## 11. Denominator-source and fallback checks

The D2 operative denominator provides population weights for the Y20-64
age-band aggregation at NUTS-2 level. The D1 diagnostic is a Y15-74
age-band check only (D1 does not publish Y20-64 at NUTS-2, a year-
invariant Eurostat limitation).

The `L7_weighting_source` check reported PASS for all three years,
confirming the D2 weighting was applied correctly.

The `L8_approximation_flags` check reported PASS for all three years.
Approximation flags (`denom_flag`, `gsur_unreliable`) are populated in
the output parquets where the script applies the `approximate_uniform`
fallback for suppressed denominator cells (e.g., FRM0 Corse, FRI2
Limousin). This fallback is year-invariant and is attested in the output
parquet via the flag columns.

D2 row counts: 1,584 (y2016), 1,583 (y2015), 1,584 (y2014). Variation
in y2015 D2 row count (1,583 vs 1,584) is consistent with minor
year-to-year differences in Eurostat denominator publication; the
construction proceeded to 48 active rows in all three years, confirming
no active cell was lost.

NUTS-2016 vintage confirmed for all three D2 files (geo codes FR10
through FRM0) at retrieval (re-audit §3); recorded in sidecar
`nuts_vintage = "NUTS2016"` for all three years.

---

## 12. Sidecar metadata checks

Each sidecar contains exactly 14 fields as specified in authorization
memo §12 Table 4.

| Field | y2016 required | y2016 actual | y2015 required | y2015 actual | y2014 required | y2014 actual | All PASS |
|-------|---------------|-------------|---------------|-------------|---------------|-------------|----------|
| `opportunity_year` | 2016 | 2016 | 2015 | 2015 | 2014 | 2014 | PASS |
| `gsur_column_name` | `"gsur"` | `"gsur"` | `"gsur"` | `"gsur"` | `"gsur"` | `"gsur"` | PASS |
| `benchmark_pct` | 9.725 | 9.725 | 10.025 | 10.025 | 9.9 | 9.9 | PASS |
| `row_count` | 54 | 54 | 54 | 54 | 54 | 54 | PASS |
| `idf_parity_difference` | ≈ 0.0 | 0.0 | ≈ 0.0 | 0.0 | ≈ 0.0 | 0.0 | PASS |
| `nuts_vintage` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` | `"NUTS2016"` | PASS |
| `script_version` | commit hash | `178ca72bcb…` | commit hash | `178ca72bcb…` | commit hash | `178ca72bcb…` | PASS |
| `build_timestamp` | UTC ISO | `2026-05-20T19:06:59Z` | UTC ISO | `2026-05-20T19:08:21Z` | UTC ISO | `2026-05-20T19:09:10Z` | PASS |
| `benchmark_difference_pct` | recorded | 0.1718 | recorded | 0.0943 | recorded | 0.0494 | PASS |
| `output_path` | `…_y2016.parquet` | ✓ | `…_y2015.parquet` | ✓ | `…_y2014.parquet` | ✓ | PASS |
| `input_d2` | `…_FR_2016.tsv` | ✓ | `…_FR_2015.tsv` | ✓ | `…_FR_2014.tsv` | ✓ | PASS |
| `input_d1` | `…_FR_2016.tsv` | ✓ | `…_FR_2015.tsv` | ✓ | `…_FR_2014.tsv` | ✓ | PASS |
| `input_benchmark_csv` | `…_2016.csv` | ✓ | `…_2015.csv` | ✓ | `…_2014.csv` | ✓ | PASS |
| `input_unemployment_workbook` | `FR_gsur.xlsx` | ✓ | `FR_gsur.xlsx` | ✓ | `FR_gsur.xlsx` | ✓ | PASS |

All 14 fields present and correct for all three years.

---

## 13. y2016 value-identity check

The y2016 year-tagged lookup was compared key-aligned against the
existing untagged baseline `FR_gsur_ruro_v2_stageA.parquet` on keys
`(year, drgn1, educ3, sex)`. The check is NaN-aware: stub rows (drgn1=9)
must be NaN in both files; the maximum-absolute-difference computation
is performed over the 48 active (non-null) cells only.

| Condition | Specification | Result |
|-----------|--------------|--------|
| G1 — row counts | Both files exactly 54 rows | new: 54, old: 54 — **PASS** |
| G2 — key match | All 54 key tuples match exactly | All match — **PASS** |
| G3 — no duplicates | 0 duplicate keys in either file | new: 0, old: 0 — **PASS** |
| G4 — max absolute diff | ≤ 1e-12 over 48 active cells | **0.0 exactly — PASS** |
| NaN alignment | drgn1=9 rows NaN in both files | 6 stubs NaN in both — **PASS** |

Maximum absolute `gsur` difference: **0.0**

The y2016 year-tagged parquet is byte-identical to the untagged baseline
(both SHA-256 `19ac53143fb404f3de44f4e2abc3313b0946eda835261496720bc511358c24ef`,
7,444 bytes). The parameterised script reproduces the existing validated
y2016 lookup exactly. The value-identity gate licensed the y2015 and
y2014 construction.

---

## 14. Comparison to v1 fallback where available

A v1-fallback GSURv2 baseline (the untagged `FR_gsur_ruro_v2_stageA.parquet`)
exists only for y2016. No v1-fallback exists for y2015 or y2014.

| Year | v1-fallback available | Comparison |
|------|-----------------------|-----------|
| 2016 | Yes (untagged baseline) | Byte-identical: max diff = 0.0 |
| 2015 | No | New construction; no baseline to compare |
| 2014 | No | New construction; no baseline to compare |

For y2015 and y2014, the IDF parity check (0.0 for both) and the L5
benchmark check (PASS for both) serve as the primary construction-
correctness indicators in the absence of an external reference.

---

## 15. PASS / FAIL by opportunity year

| Check | y2016 | y2015 | y2014 |
|-------|-------|-------|-------|
| Output parquet exists | PASS | PASS | PASS |
| Sidecar exists | PASS | PASS | PASS |
| Row count = 54 | PASS | PASS | PASS |
| Unique-key check | PASS | PASS | PASS |
| drgn1 support (1–9 present) | PASS | PASS | PASS |
| educ3 × sex support | PASS | PASS | PASS |
| No missing gsur for drgn1 1–8 | PASS | PASS | PASS |
| drgn1=9 stub NaN | PASS | PASS | PASS |
| gsur in proportion units (0,1] | PASS | PASS | PASS |
| L5 benchmark check | PASS | PASS | PASS |
| IDF parity (idf_parity_difference ≈ 0.0) | PASS | PASS | PASS |
| Denominator-source flags present | PASS | PASS | PASS |
| Sidecar 14 fields complete | PASS | PASS | PASS |
| opportunity_year correct | PASS | PASS | PASS |
| gsur_column_name = "gsur" | PASS | PASS | PASS |
| Value-identity gate (G1–G4) | **PASS (0.0)** | n/a | n/a |

**Overall per year:**

| Year | Verdict |
|------|---------|
| 2016 | **PASS** |
| 2015 | **PASS** |
| 2014 | **PASS** |

---

## 16. Overall PASS / FAIL

**Overall: PASS**

**GSURv2 multi-year lookup construction PASSED.**

All 15 validation checks pass for all three opportunity years. The
y2016 value-identity gate passed with maximum absolute `gsur` difference
of 0.0. The y2015 and y2014 lookups pass all required checks. The six
output files are present on disk with the expected structure, 11-column
schema, 54 rows, and complete 14-field sidecar provenance.

---

**MNL parquet rebuild is NOT authorized.**
The merge of the GSURv2 lookups into the MNL parquets is downstream of
the lookup construction, requires its own authorization, and requires
the O7 crosswalk sign-off.

**Pooled estimation is NOT authorized.**
No pooled estimation, provisional or final, is authorized by this
construction.

**Welfare computation is NOT authorized.**
No welfare implementation or computation is authorized by this
construction.

**M1-clean 2016 remains the active JMP baseline.**
The GSURv2 lookup construction produces opportunity-side lookups; it
does not produce any estimation result and does not displace the
M1-clean baseline. M1-clean remains active until a future SA2 verdict
on a final pooled specification determines otherwise.

---

*Validation completed: 2026-05-20.*
*Construction report: `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_report_v1.md`*