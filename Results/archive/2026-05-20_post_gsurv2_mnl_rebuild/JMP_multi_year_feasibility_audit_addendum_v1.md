# JMP Multi-Year Feasibility Audit — Addendum v1

**Document:** JMP_multi_year_feasibility_audit_addendum_v1.md  
**Supersedes (partially):** Results/JMP_multi_year_feasibility_audit_v1.md  
**Date:** 2026-05-19  
**Reference memo:** docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md §4  

---

## Purpose of This Addendum

The initial audit report (`JMP_multi_year_feasibility_audit_v1.md`) contained three problems:

1. **Wrong F-label mapping.** The report assigned its own F1–F6 labels that do not match the six conditions defined in v3.1 §4. The original F3 (Eurostat GSUR sources), F4 (INSEE benchmark), F5 (INSEE CPI), and F6 (EUROMOD output comparability) were remapped to different positions.

2. **Incorrect CPI source.** The report assessed F5 against the Eurostat PPP file (`cpi.xlsx`, dataset `prc_ppp_ind__custom_19205378`, price level indices EU15=100). The v3.1 memo specifies the **INSEE CPI** (Indice des prix à la consommation, moyenne annuelle, ensemble des ménages, France métropolitaine) as the canonical source for CPI harmonisation. These are distinct series; the PPP price-level index is not a substitute for the domestic consumer price index.

3. **Overstatement of feasibility.** The report concluded "P2 is feasible" and "P3 is feasible" without qualification. Both configurations are **conditionally feasible** — structural preconditions are met but execution is blocked by missing data and unwritten software components.

This addendum corrects the record. Substantive findings from the initial audit that were accurate are preserved and cross-referenced; only the three problems above are revised.

---

## Corrected F1–F6 Assessment

### F1 — EUROMOD installation (FR_2015, FR_2016, FR_2017 systems)

**Status: SATISFIED.**

As documented in the initial audit §2, the EUROMOD J1.0+ release at `Z:\Hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\...` contains `FR.xml` with 19 systems covering FR_2006 through FR_2024. `FR_2015`, `FR_2016`, and `FR_2017` are all present. The country configuration files (`FR_DataConfig.xml`) and the EUROMOD software infrastructure are in place.

**Caveat retained from initial audit:** No EUROMOD *run* for FR_2015 or FR_2017 has been executed. The systems are installed and invocable, but the budget-constraint output files that feed the MNL prep pipeline do not yet exist for those two years.

---

### F2 — Raw EU-SILC microdata (FR_2015, FR_2016, FR_2017)

**Status: SATISFIED.**

As documented in the initial audit §3, all three microdata files are present:

| File | Individuals | Households | Column count |
| --- | --- | --- | --- |
| `FR_2015_a2.txt` | 26,558 | 11,390 | 122 |
| `FR_2016_a3.txt` | 26,560 | 11,459 | 124 |
| `FR_2017_a2.txt` | 25,309 | 11,068 | 128 |

All RURO-critical identifier and demographic columns (`idhh`, `idperson`, `idpartner`, `idorighh`, `idorigperson`, `drgn1`, `deh`, `dgn`, `dag`, `dms`, `dwt`, and all labour/income variables) are present in all three files. No version mismatches were identified.

---

### F3 — Eurostat sources for GSUR (`lfst_r_lfu3rt__custom_19204794` and `lfst_r_lfsd2pop`)

**Status: PARTIALLY SATISFIED.**

**Rate source — SATISFIED.** The Eurostat unemployment-rate data is available. `Data/external/FR_gsur.xlsx` covers years 2007–2024 across 122 sheets (all sex × education × age-group combinations). The processed v1 lookup `Data/external/FR_gsur_ruro.parquet` confirms 2015 and 2017 are present with full regional × education × sex coverage.

**Population-denominator source — NOT SATISFIED for 2015/2017.**

- `Data/external/lfst_r_lfsd2pop_2016_full.csv`: covers `TIME_PERIOD = 2016` only (82,188 rows). The API download was targeted at 2016. Re-download for `startPeriod=2015&endPeriod=2017` is required.
- `Data/external/lfst_r_lfp2acedu_2016_full.csv`: same — 2016 only.

These denominators are required to extend the GSUR v2 lookup (`FR_gsur_ruro_v2_stageA.parquet`, currently 54 rows, 2016 only) to 2015 and 2017. This is a mechanical download, not a structural gap.

**GSUR v2 script — minor change required.** `enh_prepare_FR_gsur_v2.py` has `YEAR = 2016` hardcoded at line 44. Adding a `--year` CLI argument is a one-line edit; the internal `_find_year_col(df_raw, year)` logic is already year-generic.

**Implication for GSUR v1 path:** If GSUR v1 (not v2) is acceptable for the initial pooled estimation runs, F3 is fully satisfied — `FR_gsur_ruro.parquet` already covers 2015 and 2017. The v3.1 memo does not explicitly require GSUR v2 for the first pooled run; it requires whichever GSUR version was used in the accepted M1-clean baseline. M1-clean used GSUR v2, so v2 parity is required for any pooled run that claims continuity with M1-clean.

---

### F4 — INSEE national benchmark (BDM series 001688526) for 2015 and 2017

**Status: NOT SATISFIED.**

`Data/external/insee_001688526_2016.csv` contains only the 2016 national unemployment-rate benchmark (Q1–Q4 2016, annual average 9.725%, source: INSEE BDM API). No file for 2015 or 2017 exists.

This benchmark is required for the GSUR v2 Stage A L5 national-benchmark validation step, which checks that the implied national weighted average of regional GSUR rates matches the INSEE headline figure within the agreed tolerance (±0.001 absolute, per O8 resolution). Without 2015 and 2017 values, Stage A validation cannot be completed for those years.

The INSEE BDM API endpoint (`https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526`) is public and the series is published continuously. The retrieval for additional years follows the same procedure documented in `Data/external/gsur_benchmark_source.txt`. Approximate expected values for reference only (must be verified from API before use):

- 2015: approximately 10.4% (ILO unemployment rate, SA, metropolitan France)
- 2017: approximately 9.4%

**Action required:** Two API calls to the INSEE BDM endpoint, producing files `insee_001688526_2015.csv` and `insee_001688526_2017.csv` in the format of the existing 2016 file.

---

### F5 — INSEE CPI series (annual, all-items, metropolitan France)

**Status: NOT SATISFIED — wrong source used in initial audit.**

The initial audit assessed this condition against `Data/external/cpi.xlsx`, which contains Eurostat dataset `prc_ppp_ind__custom_19205378` (Purchasing Power Parities, Price Level Indices, EU15=100, Actual Individual Consumption). This is **not** the required series.

The v3.1 memo §5 Decision D2 specifies:

> *The CPI source is the INSEE consumer price index, annual average, all-items, all-household (Indice des prix à la consommation, moyenne annuelle, ensemble des ménages, France métropolitaine).*

The Eurostat PPP price-level index (EU15=100) measures relative price levels across countries at a point in time. The INSEE all-items CPI measures domestic price changes over time within France. They serve different purposes and produce materially different deflation factors. Using the PPP series would be a specification error.

**What exists as a partial substitute:** The EUROMOD J1.0+ configuration file `HICPCONFIG.xml` contains France HICP values (Eurostat HICP, AMECO 2023 spring series, base 2015=100) for all relevant years:

| Year | EUROMOD HICP value (2015=100) | Source |
| --- | --- | --- |
| 2015 | 100.00 | Eurostat/AMECO (J1.0+ config) |
| 2016 | 100.31 | Eurostat/AMECO (J1.0+ config) |
| 2017 | 101.47 | Eurostat/AMECO (J1.0+ config) |

The EUROMOD HICP is the Eurostat Harmonised Index of Consumer Prices — closely related to but distinct from the INSEE domestic CPI. The v3.1 memo explicitly names the INSEE domestic series. **The EUROMOD HICP values cannot be substituted without a deliberate decision to use that source instead.**

If the project adopts the EUROMOD HICP as the CPI source (a reasonable pragmatic choice given its availability and its use in EUROMOD's own uprating procedures), the deflation factors would be:

- φ_2015 = CPI_2016 / CPI_2015 = 100.31 / 100.00 = **1.0031**
- φ_2016 = 1.0000 (base year)
- φ_2017 = 100.31 / 101.47 = **0.9886**

These are small adjustments (< 1.2% in either direction), reflecting near-price-stability in France 2015–2017.

**Action required for strict F5 compliance:** Retrieve the INSEE CPI series for 2015, 2016, and 2017 from the INSEE BDM API or INSEE website (series code for all-items CPI, metropolitan France, annual average — typically INSEE BDM series 001759971 or equivalent). Alternatively, the project may elect to use the EUROMOD HICP values already available, with a documented decision to that effect.

---

### F6 — EUROMOD output variable comparability (FR_2015, FR_2016, FR_2017)

**Status: SATISFIED.**

As documented in the initial audit §10 and §11:

- All 34 standardised income concepts in `euromod_fr_2015_2017_standard_income_concepts.csv` are **identical** across FR_2015, FR_2016, and FR_2017. Zero component differences found.
- The `output_std_fr` policy structure (vargroups, ilgroups, UnitInfo blocks) is identical across all three systems in `euromod_fr_2015_2017_output_variable_index.csv`.
- The core disposable-income aggregate `ils_dispy` has the same component structure in all three years.

Six structural column differences exist between years at the microdata level, but none affect RURO-critical variables (see initial audit §11 for the full table). The year-specific additions in 2016 (`twl`, `dmb`) and 2017 (`bchba`, `bsawk`, `ltr`, `ymwdt`) either feed into the comparable `ils_ben` aggregate or are irrelevant to the RURO utility function.

---

## Corrected Feasibility Characterisation

### P2 (2015 + 2016): Conditionally Feasible — Not Execution-Ready

P2 is structurally sound: F1 and F2 are satisfied, F6 is satisfied, identifier encoding (B=10^11) is verified, and the 2015–2016 overlap is confirmed zero (fully disjoint panels). However, four gaps must close before estimation can begin:

**Hard blockers (require execution or new development):**

1. **FR_2015 EUROMOD run not executed.** No budget-constraint output for 2015 exists. This is the single longest-lead-time item (requires running the EUROMOD software with the FR_2015 system and the FR_2015_a2.txt microdata).
2. **FR_2015 MNL parquet does not exist.** Follows from item 1 via the prep pipeline (`enh_RURO_prep_mnl_basic.py` + GSUR merge).
3. **Pooled-parquet builder not written.** A new script is required to stack 2015 and 2016 parquets, apply the B=10^11 UID remapping, add a `year` column, and apply the CPI deflation factor φ_2015 to monetary variables.

**Mechanical acquisition gaps (short-lead-time):**

4. **Eurostat denominators for 2015** (`lfst_r_lfsd2pop`, `lfst_r_lfp2acedu`): Eurostat API re-download.
5. **INSEE benchmark 2015** (BDM series 001688526): single API call.
6. **INSEE CPI for 2015–2017** (or decision to adopt EUROMOD HICP): one API call or one authorisation decision.
7. **GSUR v2 script year-parameterisation**: one-line edit to `enh_prepare_FR_gsur_v2.py`.

Note on cluster correction for P2: Because 2015 and 2016 are fully disjoint EU-SILC panels (zero shared households confirmed), no **repeated-household** cluster correction is required. Standard survey-weighted inference at household level applies. Year fixed effects are needed but do not require new inference machinery.

### P3 (2015 + 2016 + 2017): Conditionally Feasible — Blocked by Additional Hard Items

P3 inherits all P2 blockers plus:

**Additional hard blockers:**

1. **FR_2017 EUROMOD run not executed.** Same as the FR_2015 situation.
2. **FR_2017 MNL parquet does not exist.**
3. **Cluster-robust SE wrapper (T1) not written.** The 2016–2017 overlap (8,796 repeat households, confirmed) requires cluster-robust inference at the household level. The current estimation engine does not implement this.

**Additional mechanical gaps:**

4. **Eurostat denominators for 2017**: same API re-download as for 2015.
5. **INSEE benchmark 2017**: single API call.
6. **GSUR v2 for 2017**: same script edit as for 2015.

### Temporal Validation (2016 → 2017 holdout): Conditionally Feasible

Feasible once the 2017 MNL parquet exists. Requires a `--prediction-only` mode in the post-estimation script (not yet written). No re-estimation; the 2016 M1-clean estimates are already available.

---

## Revised F1–F6 Summary Table

| Condition | Description | Status | Blocker type |
| --- | --- | --- | --- |
| F1 | EUROMOD FR_2015/2016/2017 systems installed | ✓ SATISFIED | — |
| F2 | EU-SILC microdata present for all three years | ✓ SATISFIED | — |
| F3 | Eurostat GSUR sources for 2015 and 2017 | ⚠ PARTIAL | Denominator re-download (mechanical) |
| F4 | INSEE unemployment benchmark for 2015 and 2017 | ✗ NOT SATISFIED | API call (mechanical) |
| F5 | INSEE CPI series for 2015–2017 | ✗ NOT SATISFIED | API call or source-adoption decision |
| F6 | EUROMOD output variable comparability | ✓ SATISFIED | — |

Three conditions are satisfied; F3 is partial (rate source satisfied, denominator source not); F4 and F5 are not satisfied but are blocked only by data-acquisition tasks, not structural gaps.

---

## What Can Be Authorised Now

Given the corrected audit findings, the following are appropriate next authorisations:

**Authorise immediately:**

1. **Data and source acquisition:** Download Eurostat denominators (`lfst_r_lfsd2pop`, `lfst_r_lfp2acedu`) for 2015 and 2017; retrieve INSEE BDM series 001688526 for 2015 and 2017; resolve the CPI source question (INSEE CPI vs EUROMOD HICP adoption decision).
2. **GSUR v2 script year-parameterisation:** Add `--year` CLI argument to `enh_prepare_FR_gsur_v2.py` (one-line edit, straightforward).
3. **Multi-year implementation planning:** Produce a Stage M1 implementation plan covering the pooled-parquet builder specification, the EUROMOD run procedure for FR_2015 and FR_2017, and the cluster-robust SE design for P3.

**Do not yet authorise:**

- Pooled estimation (P2 or P3): execution-blocked by missing parquets and unwritten components.
- Temporal validation: execution-blocked by missing 2017 parquet.
- Cluster-robust SE implementation: design must be reviewed before implementation begins.

**Recommended sequence after authorisation:**

1. Close F4, partial-F3, and F5 acquisition gaps (< 1 day).
2. Run EUROMOD FR_2015 and FR_2017; build MNL parquets for each year (< 1 week).
3. Extend GSUR v2 to 2015/2017; Stage A validation for both years (< 1 day each).
4. Write pooled-parquet builder; implement P2 stacking and CPI deflation (new development, ~1 day).
5. Implement P2 estimation (no cluster correction needed).
6. Write cluster-robust SE wrapper; implement P3 stacking (new development, ~1–2 days).
7. Implement P3 estimation.
8. Implement temporal validation (2016 → 2017).

---

## Errata to Initial Audit

| Section in v1 | Error | Correction |
| --- | --- | --- |
| §6 (F4 label) | Called "F4 — Eurostat GSUR Source" | Correct label: F3 — Eurostat GSUR Sources |
| §7 (F5 label) | Called "F5 — INSEE benchmark" | Correct label: F4 — INSEE benchmark |
| §9 (F6 label) | Called "F6 — INSEE CPI / PPP" | Correct label: F5 — INSEE CPI series; and the file assessed (Eurostat PPP) is the **wrong source** |
| §10 (unlabelled) | EUROMOD output comparability treated as separate section | Correct label: F6 — EUROMOD output variable comparability |
| §16 "no cluster correction needed for P2" | Ambiguous — could be read as dismissing all inference concerns | Corrected: no *repeated-household* cluster correction needed; year fixed effects and survey-weight design still apply |
| §16 "P2 is feasible" | Overstatement | Corrected: P2 is conditionally feasible, not execution-ready |
| §17 "P3 is feasible" | Overstatement | Corrected: P3 is conditionally feasible, blocked by multiple hard items |
| §9 (F6/CPI) | Concluded CPI satisfied using Eurostat PPP | Corrected: F5 (INSEE CPI) is **not satisfied**; `cpi.xlsx` is not the specified source |