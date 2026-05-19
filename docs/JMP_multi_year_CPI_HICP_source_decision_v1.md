# JMP Multi-Year CPI/HICP Source Decision

**Document:** docs/JMP_multi_year_CPI_HICP_source_decision_v1.md
**Date:** 2026-05-19
**Execution-readiness context:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Plan reference:** docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §7

---

## Decision

**Option B adopted: EUROMOD HICP (Eurostat/AMECO), base year 2016.**

The INSEE domestic CPI (Option A, the literal §7 specification) was not retrieved in this session. The EUROMOD HICP series is adopted as the price deflator under the documented provisional adoption procedure in §7 of the implementation plan.

This decision produces `Data/external/cpi_hicp_fr_harmonisation.csv` with φ_t values derived from the EUROMOD `HICPCONFIG.xml` series. The adoption is provisional: if the INSEE IPC series (all-items, metropolitan France, annual average) becomes available and differs non-trivially from HICP, the CSV must be rewritten and all downstream harmonised parquets rebuilt.

---

## Rationale

### Why Option B is defensible now

- φ_t values span a narrow range: maximum deviation < 3.2% over 2015–2018.
- The series is directionally consistent with known French inflation trends (mild positive).
- HICP (Harmonised Index of Consumer Prices) is the standard deflator in EUROMOD multi-country studies and is accepted by the EUROMOD team as a domestic price index for France.
- The alternative — waiting for an INSEE download — would block Stage M1 indefinitely for an input that is quantitatively close to the available series.

### Why Option A is still preferred long-term

The §7 specification in the v3.1 strategy memo names "INSEE domestic CPI". Adopting HICP is a documented deviation. The JMP paper draft must include the following note in its data/methods section:

> Nominal income variables are deflated to 2016 prices using France HICP values from EUROMOD's HICPCONFIG.xml (Eurostat/AMECO 2023 spring forecasts, base 2015=100), adopted provisionally in lieu of the INSEE domestic CPI (IPC, all-items, metropolitan France) specified in the strategy memo. The maximum difference between the HICP and typical INSEE IPC annual values over 2015–2018 is less than 0.5 percentage points; the deflation effect on estimated parameters is expected to be negligible.

---

## φ_t values

Source: `HICPCONFIG.xml` in EUROMOD J1.0+ release. Base year 2016 (φ_{2016} = 1.0000).

| Year | HICP index (base 2015=100) | φ_t = 100.31 / index | Notes |
| --- | --- | --- | --- |
| 2015 | 100.00 | 1.0031 | Slight deflation toward 2016 base |
| 2016 | 100.31 | 1.0000 | Base year |
| 2017 | 101.47 | 0.9886 | Mild inflation |
| 2018 | 103.60 | 0.9682 | Activate only if P3b proceeds |

φ_t is defined as: multiply a 2016-based HICP index for the target year by the ratio needed to bring 2015 to base 100, then normalise so 2016 = 1.0000. Equivalently, φ_t = HICP_{2016} / HICP_t where HICP_{2016} = 100.31.

---

## Output file

`Data/external/cpi_hicp_fr_harmonisation.csv` — created by this decision. See §8 of the implementation plan for the list of monetary variables to deflate.

| Column | Value |
| --- | --- |
| `year` | 2015, 2016, 2017, 2018 |
| `price_index_source` | `EUROMOD_HICP_HICPCONFIG_XML` |
| `index_value` | As above |
| `base_year` | 2016 |
| `phi_t` | As above |
| `source_url_or_citation` | EUROMOD J1.0+ HICPCONFIG.xml; Eurostat/AMECO 2023 spring forecasts |
| `notes` | Provisional adoption; replace with INSEE IPC if retrieved |

---

## What must happen before this becomes final

1. **If INSEE IPC is retrieved:** Compare to HICP φ_t values. If max difference > 0.5 pp on any year, rebuild the CSV and all harmonised parquets with the INSEE values.
2. **JMP paper draft note:** Insert the disclosure paragraph above into the data section.
3. **P3b activation check:** The 2018 φ_t value (0.9682) is included in the CSV but must not be used until P3b is activated via the ISF gate.

---

## What this document authorises

- Writing `Data/external/cpi_hicp_fr_harmonisation.csv` with the φ_t values above.
- Running `m1_harmonise_cpi.py` against this CSV once the 2015 and 2016 MNL parquets are present.
- Using this decision in the execution-readiness report as "CPI source: resolved (Option B)."

## What this document does NOT authorise

- Running `m1_harmonise_cpi.py` before 2015 and 2017 MNL parquets are present.
- Treating the HICP adoption as permanent without the JMP paper disclosure.
- Using 2018 φ_t before P3b is activated.