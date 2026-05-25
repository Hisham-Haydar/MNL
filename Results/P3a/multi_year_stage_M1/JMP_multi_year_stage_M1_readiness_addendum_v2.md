# JMP Multi-Year Stage M1 — Readiness Addendum v2

**Document:** Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_readiness_addendum_v2.md
**Date:** 2026-05-19
**Supersedes:** Results/JMP_multi_year_stage_M1_readiness_addendum_v1.md
**Addendum to:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Change from v1:** Issue 2 corrected — `twl` is present and non-zero in FR_2016 and FR_2017 raw input files. The v1 characterisation that 2015 `tpr` was a one-year asymmetry was incorrect. The correct interpretation is a low-incidence tax-field pattern across all four years. Issues 1 and 3 are unchanged.

---

## Issue 1 — HICP adoption is provisional, not a permanent replacement of INSEE CPI

*(Unchanged from v1.)*

### Status

**Execution-ready, not final.**

The HICP CSV was created to unblock Stage M1 from a CPI-file perspective. The φ_t values are:

| Year | φ_t |
| --- | --- |
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |
| 2018 | 0.9682 (P3b only) |

Maximum deviation across 2015–2017 window: 0.0031 (0.31%) between 2015 and 2016. All three φ_t values are within 1.2% of 1.0.

### What provisional means

- The HICP CSV **may be used** to run Stage M1 harmonisation. There is no methodological barrier to doing so.
- If the INSEE IPC (all-items, metropolitan France, annual average) is later retrieved and any φ_t differs from the HICP value by more than 0.5 percentage points, the CSV must be rewritten and all harmonised parquets must be rebuilt from the stacked raw parquets.
- Given the small magnitude of φ_t (maximum 3.2% deviation over 2015–2018), the probability of a material difference is low. The JMP paper must include the disclosure note in `docs/France_case/_shared/governance/JMP_multi_year_CPI_HICP_source_decision_v1.md §1`.
- The HICP decision does **not** require re-authorisation before Stage M1 execution. It is already authorised by this package.

### Condition to make it final

Retrieve INSEE IPC (BDM series accessible at data.gouv.fr or the INSEE API). If retrieved: compare row-by-row with HICP φ_t; if max difference < 0.5 pp, replace the `notes` column in the CSV with "INSEE IPC confirmed consistent with HICP; adoption permanent"; if difference ≥ 0.5 pp on any year, rewrite φ_t values and rebuild harmonised parquets.

---

## Issue 2 — `tpr`/`twl` tax-field pattern across P3a years (corrected)

### Correction to v1

The v1 addendum stated that FR_2016 and FR_2017 raw input files have no `tpr` or `twl` column, and characterised the asymmetry as "2015 has property tax; 2016/2017 have no comparable tax field." This was incomplete. Inspection of FR_2016 and FR_2017 raw files shows that `twl` (wealth tax, ISF) is present and non-zero in both years.

### Empirical findings from raw input files (inspected 2026-05-19)

All four raw EU-SILC input files inspected: `FR_2015_a2.txt`, `FR_2016_a3.txt`, `FR_2017_a2.txt`, `FR_2018_a2.txt`.

| Year | `tpr` column in raw file | `tpr` non-zero (total) | `tpr` non-zero (working-age 18–64) | WA incidence |
| --- | --- | --- | --- | --- |
| 2015 | YES | 108 / 26,558 | 53 / 15,414 | 0.344% |
| 2016 | absent | — | — | — |
| 2017 | absent | — | — | — |
| 2018 | YES | 102 / 24,620 | 40 / 14,050 | 0.285% |

| Year | `twl` column in raw file | `twl` non-zero (total) | `twl` non-zero (working-age 18–64) | WA incidence |
| --- | --- | --- | --- | --- |
| 2015 | absent | — | — | — |
| 2016 | YES | 107 / 26,560 | 44 / 15,389 | 0.286% |
| 2017 | YES | 101 / 25,309 | 43 / 14,564 | 0.295% |
| 2018 | absent | — | — | — |

### Variable nomenclature (from EUROMOD ILS definitions)

The EUROMOD standard income concepts file (`Data/documentation/euromod_fr_2015_2017_standard_income_concepts.csv`) establishes:

- `tpr` = **"Property taxes"** (taxe foncière, taxe de propriété). Enters `ils_tax` → reduces `ils_dispy`.
- `twl` = **"Wealth tax (ISF)"** — Impôt de Solidarité sur la Fortune. Also enters `ils_tax` → reduces `ils_dispy`.

Both are raw **observed EU-SILC inputs** (not EUROMOD simulations) in the years where they appear. They are separate tax instruments: `tpr` is a property tax levied on real estate owners; `twl` is a net-wealth tax levied on high-net-worth households.

The implementation plan §16 uses "`tpr`" loosely to mean "ISF-type wealth/property tax." The correct variable mapping is: `tpr` = property tax (2015, 2018); `twl` = ISF wealth tax (2016, 2017). The two variables appear to alternate across years in the EU-SILC data extracts: 2015 and 2018 carry `tpr`; 2016 and 2017 carry `twl`.

### Revised interpretation

The P3a income-definition question is not a one-year-only asymmetry. It is a **low-incidence tax-field pattern** across years:

- Each year has exactly one of `tpr` or `twl` as an observed non-zero input (the other is absent).
- Working-age incidence is below 0.35% in every year.
- The EUROMOD ILS aggregate `ils_tax` includes both variables as additive components in all years; the non-present variable simply contributes zero.
- The practical effect is that in any given year, a small number of high-net-worth or high-property-value households carry a non-zero tax deduction in `ils_dispy`. The identity of the instrument differs by year (`tpr` vs `twl`) but the economic mechanism (additional tax reducing disposable income) is the same.

This is consistent with the French ISF/property-tax history: ISF was reformed and renamed multiple times over 2015–2018, and its representation in EU-SILC data extracts varies depending on which instrument was active and reported in each survey year.

### Does P3a require a gate analogous to the P3b ISF check?

**No.** The P3b ISF check (§16) was motivated by the concern that a EUROMOD-simulated wealth tax in 2018 could create a systematic income-level shift relative to 2016/2017. The present finding is different: the tax-field asymmetry in P3a is:

1. **Symmetric in incidence across years** — 0.28–0.34% in each P3a year. No single year is systematically elevated.
2. **Observed EU-SILC inputs, not EUROMOD simulations** — EUROMOD is not introducing new wealth relative to the survey data; it is passing through observed values.
3. **Below any practically meaningful threshold** — fewer than 55 working-age rows per year carry non-zero values; the pooled P3a draw file will have these diluted across multiple draws.

### Required validation annotation

When P3a parquets are built, the M1 validation report (`Results/P3a/multi_year_stage_M1/M1_identity_validation_summary.md` or a companion section) must include:

| Year | `tpr` non-zero rows (RURO sample) | `twl` non-zero rows (RURO sample) | Note |
| --- | --- | --- | --- |
| 2015 | report count | — | Property tax observed input |
| 2016 | — | report count | Wealth tax (ISF) observed input |
| 2017 | — | report count | Wealth tax (ISF) observed input |

Report expected values roughly matching the raw-file incidence adjusted for RURO sample coverage (≤55 rows per year). If any year's count materially exceeds 1% of the RURO sample, escalate to a formal comparability check before estimation.

### JMP paper note

The JMP draft should note: "The P3a panel includes, in each year, a small number of working-age households (< 0.4%) with non-zero property or wealth tax as an observed EU-SILC input (`tpr` in 2015, `twl` in 2016 and 2017), which enters household disposable income through the EUROMOD standardised tax aggregate. The incidence is below 0.35% per year and is treated as a data-quality annotation rather than an income-concept correction."

---

## Issue 3 — 2016 MNL input: copy locally vs. update YAML

*(Unchanged from v1.)*

### Recommendation: **Option L (copy locally)**

Copy the 2016 MNL parquet and sidecar from Z: to `Data/processed/fr/`:

```powershell
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"
```

When 2015 and 2017 parquets are produced, place them in the same directory. The Z: originals remain as the authoritative storage copy. Do not point the YAML `input_parquet_dir` at Z: — this breaks portability.

---

## Summary

| Issue | v1 status | v2 correction | Blocking? |
| --- | --- | --- | --- |
| HICP provisional adoption | Execution-ready; INSEE IPC retrieval deferred | Unchanged | Not blocking |
| `tpr`/`twl` tax-field pattern in P3a | v1: 2015 has tpr, 2016/2017 have none | v2: each year has one of tpr or twl at <0.35% incidence; symmetric; no gate needed | Not blocking |
| 2016 MNL local copy vs. YAML | Copy to `Data/processed/fr/` recommended | Unchanged | Not blocking (either option works) |

**Final readiness classification: NOT AUTHORIZED — unchanged.**

The readiness package is now clean. Stage M1 execution remains blocked on EUROMOD outputs for FR_2015/FR_2017 and MNL parquets for all three years (including 2016 placement). The tax-field asymmetry across P3a years is real, below 0.35% incidence in each year, symmetric in mechanism, and handled as a validation annotation rather than a gate.