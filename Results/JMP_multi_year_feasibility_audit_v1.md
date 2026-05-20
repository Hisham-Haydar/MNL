# JMP Multi-Year Feasibility Audit

**Document:** JMP_multi_year_feasibility_audit_v1.md  
**Date:** 2026-05-19  
**Reference memo:** docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md  
**Scope:** Feasibility of implementing the 2015–2017 pooled-estimation pipeline as specified in the v3.1 memo. No estimation, no data modification, no parquet rebuilds were performed.

---

## 1. Scope and Audit Method

This audit checks whether all preconditions for the pooled multi-year estimation pipeline are satisfied. The v3.1 memo defines six formal feasibility conditions (F1–F6) and three estimation configurations: P1 (2016 alone, the baseline already completed), P2 (2015 + 2016, disjoint years), and P3 (2015 + 2016 + 2017, with 2016–2017 panel overlap). Each condition below was verified by direct inspection of files at `Z:\Hisham\EUROMOD-STORAGE\` and `U:\Desktop\Nizam_Hisham\MNL\`.

**Not checked:** Welfare-measurement scaffolding, EUROMOD budget constraint runs for 2015/2017, MNL parquet construction for 2015/2017, or estimation itself.

---

## 2. F1 — EUROMOD Tax-Benefit Systems for FR 2015, 2016, 2017

**Condition:** EUROMOD FR system files for all three target years must be present and runnable.

**Finding: SATISFIED.**

The EUROMOD J1.0+ release at `Z:\Hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+\XMLParam\Countries\FR\` contains `FR.xml` with all 19 systems from FR_2006 through FR_2024. The systems `FR_2015`, `FR_2016`, and `FR_2017` are present. The `FR_DataConfig.xml` and `FR.png` country configuration files are also present. The EUROMOD software itself (J1.0+ installer) is in the same release tree with full documentation.

**Note:** No EUROMOD output files for FR_2015 or FR_2017 currently exist in the project's processed-data directories — only 2016 has been run and its output is the current MNL parquet. Running FR_2015 and FR_2017 through EUROMOD is required before MNL parquets for those years can be built.

---

## 3. F2 — EU-SILC Microdata for FR 2015, 2016, 2017

**Condition:** Raw EU-SILC input files (`FR_2015_a2.txt`, `FR_2016_a3.txt`, `FR_2017_a2.txt`) must exist and have the expected structure.

**Finding: SATISFIED.**

All three microdata files are present at `Z:\Hisham\EUROMOD-STORAGE\Data\FR\`:

| File | Size (bytes) | Row count (incl. header) | Column count |
| --- | --- | --- | --- |
| `FR_2015_a2.txt` | 9,826,418 | 26,559 | 122 |
| `FR_2016_a3.txt` | 10,056,505 | 26,561 | 124 |
| `FR_2017_a2.txt` | 9,822,839 | 25,310 | 128 |

Net individual counts: 2015 = 26,558; 2016 = 26,560; 2017 = 25,309.

**Version suffixes:** `FR_2015_a2` (survey wave a, release 2), `FR_2016_a3` (survey wave a, release 3), `FR_2017_a2` (survey wave a, release 2). These are the standard EUROMOD-distributed EU-SILC extracts. A separate 2015 file `FR_2015_a2_2015_03_e2.txt` (36.4 MB, 3× size) is also present; this is the e2 edition with extended variables. The main audit uses the base `a2` and `a3` files, consistent with EUROMOD system configurations.

---

## 4. F3 — Identifier Availability: `drgn1`, `deh`, `dgn`, `dag`, `idhh`, `idperson`, `idpartner`, `idorighh`, `idorigperson`

**Condition:** All RURO-critical identifier and demographic variables must exist in all three microdata files.

**Finding: SATISFIED.**

Direct header inspection confirmed all critical columns present in all three files:

| Variable | 2015 | 2016 | 2017 |
| --- | --- | --- | --- |
| `idhh` | ✓ | ✓ | ✓ |
| `idperson` | ✓ | ✓ | ✓ |
| `idpartner` | ✓ | ✓ | ✓ |
| `idfather` | ✓ | ✓ | ✓ |
| `idmother` | ✓ | ✓ | ✓ |
| `idorighh` | ✓ | ✓ | ✓ |
| `idorigperson` | ✓ | ✓ | ✓ |
| `dag` | ✓ | ✓ | ✓ |
| `dgn` | ✓ | ✓ | ✓ |
| `deh` | ✓ | ✓ | ✓ |
| `dms` | ✓ | ✓ | ✓ |
| `drgn1` | ✓ | ✓ | ✓ |
| `drgn2` | ✓ | ✓ | ✓ |
| `dwt` | ✓ | ✓ | ✓ |

All EUROMOD labour-market and income output variables relevant to RURO (`yem`, `bun`, `pdi`, `poa`, `yse`, `lhw`, `yem00`, `yemxp`, `lfs`, `lcs`, `les`) are present in all three files.

---

## 5. Identifier Maxima and UID Encoding Verification

**Condition (v3.1 Table 2):** Person identifiers must fit within the `B = 10^11` stacking base used to generate collision-free pooled UIDs. The v3.1 memo specifies that person IDs reach up to ~9.38 × 10⁹ and household IDs up to ~9.38 × 10⁷.

**Finding: SATISFIED.**

Computed directly from the three microdata files:

| File | `idhh` max | `idperson` max | `idorighh` max | `idorigperson` max |
| --- | --- | --- | --- | --- |
| FR_2015_a2 | 1,478,400 | 147,840,002 | 1,478,400 | 147,840,002 |
| FR_2016_a3 | 93,789,900 | 9,378,990,002 | 93,789,900 | 9,379,830,001 |
| FR_2017_a2 | 4,671,300 | 467,130,003 | 4,671,300 | 9,379,750,001 |

The maximum `idperson` value across all years is 9,379,830,001 (≈ 9.38 × 10⁹), confirming the v3.1 Table 2 entry exactly. With `B = 10^11`:

- Year-tag 1 (2015/2016 stacking) max UID: `1 × 10^11 + 93,789,900 = 100,093,789,900`
- Year-tag 2 (2017 stacking) max UID: `2 × 10^11 + 4,671,300 = 200,004,671,300`
- Year-tag 1 max < Year-tag 2 min: **True** — no collisions possible.
- All values fit within int64 max (9.2 × 10^18): **Yes**.

The `B = 10^11` scheme is sufficient for all three years.

---

## 6. Cross-Year Identifier Overlap Structure

**Condition:** The v3.1 memo specifies that 2015 and 2016 are disjoint (different EU-SILC panels), that 2016 and 2017 share a rotating panel with approximately 8,796 repeat households, and that 2015 and 2017 are also disjoint.

**Finding: CONFIRMED EXACTLY.**

Computed from `idorighh` (original household ID, raw EU-SILC) across all three files:

| Year pair | Shared `idorighh` (households) | Shared `idorigperson` (individuals) |
| --- | --- | --- |
| 2015 ∩ 2016 | **0** | 0 |
| 2016 ∩ 2017 | **8,796** | 19,904 |
| 2015 ∩ 2017 | **0** | 0 |
| 2015 ∩ 2016 ∩ 2017 | 0 | 0 |

This matches the v3.1 memo specification exactly: P2 (2015+2016) is fully disjoint; P3 (2015+2016+2017) contains one overlapping pair (2016–2017 with 8,796 repeat households). The overlap design for P3 requires cluster-robust standard errors at the household level (inference strategy T1 in the v3.1 memo).

**Implication for P2:** A pooled 2015+2016 dataset is simply a vertically stacked cross-section (total 11,390 + 11,459 = 22,849 unique households). No clustering correction is needed for P2 beyond the standard survey-weight design.

**Implication for P3:** The stacked 2015+2016+2017 dataset has 11,390 + 11,459 + 11,068 = 33,917 household-level rows (= individuals at RURO household unit), of which 8,796 appear in both 2016 and 2017. Cluster-robust SEs at `idhh` level (T1) are required.

---

## 7. F4 — Eurostat GSUR Source Availability for 2015 and 2017

**Condition:** Eurostat unemployment-rate data (`lfst_r_lfu3rt` or comparable) and population-denominator data (`lfst_r_lfsd2pop`) must be available for 2015 and 2017 to extend the GSUR lookup beyond 2016.

**Finding: PARTIALLY SATISFIED — rates available, denominators require re-download.**

**GSUR rates (FR_gsur.xlsx):**  
The file `Data/external/FR_gsur.xlsx` (downloaded from Eurostat, 122 sheets, all sex × education × age-group combinations) covers years 2007–2024. The processed lookup `Data/external/FR_gsur_ruro.parquet` (2,160 rows, 18 years) confirms 2015 and 2017 are both present with complete regional × education × sex coverage:

```
Years in FR_gsur_ruro.parquet:
2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
```

The GSUR-rate lookup is immediately usable for 2015 and 2017 by year-filtering — no re-download required.

**GSUR v2 (enh_prepare_FR_gsur_v2.py):**  
The v2 script has `YEAR = 2016` hardcoded at line 44. It is **not** parameterized by year. Generating a 2015 or 2017 GSUR v2 lookup requires either (a) changing this constant and re-running, or (b) adding a `--year` CLI argument. The script architecture supports multi-year extraction (it uses `_find_year_col(df_raw, year)` internally), so the change is a one-line edit plus optional argparse extension.

**Population denominators (lfst_r_lfsd2pop):**  
The file `Data/external/lfst_r_lfsd2pop_2016_full.csv` covers only `TIME_PERIOD = 2016`. The file is named for 2016 and its download URL was targeted at 2016 only. To build GSUR v2 for 2015 and 2017, the population denominators for those years must be re-downloaded from Eurostat (`lfst_r_lfsd2pop?startPeriod=2015&endPeriod=2017`). The Eurostat API endpoint is documented in `Data/external/gsur_denominator_source.txt`. This is a mechanical download task, not a structural gap.

**Labour-force denominators (lfst_r_lfp2acedu):**  
Same situation — current download covers 2016 only. Re-download needed for 2015/2017.

**National benchmark (INSEE BDM 001688526):**  
`Data/external/insee_001688526_2016.csv` covers only 2016. INSEE BDM API queries for 2015 (`?startPeriod=2015&endPeriod=2015`) and 2017 are straightforward. Published values are public. **Not yet downloaded.**

---

## 8. F5 — INSEE Benchmark (Series 001688526) for 2015 and 2017

**Condition:** Annual average ILO unemployment rate for metropolitan France is required for GSUR v2 Stage A benchmark verification in 2015 and 2017.

**Finding: NOT YET SATISFIED — download required.**

The current file `insee_001688526_2016.csv` contains only 2016 quarterly values (Q1–Q4 2016, annual average 9.725%). INSEE BDM API calls for 2015 and 2017 have not been made. The API endpoint is documented in `Data/external/gsur_benchmark_source.txt`:

```
https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688526
```

This series is publicly available with no authentication requirement for historical data. Approximate known values (from OECD/Eurostat cross-reference):

- 2015: ~10.4% (France metropolitan, ILO SA annual average)
- 2017: ~9.4% (France metropolitan, ILO SA annual average)

These must be verified directly from the INSEE BDM API before use. A new file `insee_001688526_2015_2017.csv` (or two separate files following the existing naming convention) should be created following the same format as the 2016 file.

---

## 9. F6 — Eurostat PPP/CPI Data for 2015 and 2017

**Condition:** Price level indices for cross-year income deflation are required.

**Finding: SATISFIED.**

The file `Data/external/cpi.xlsx` contains the Eurostat dataset `prc_ppp_ind__custom_19205378` (Purchasing Power Parities, Price Level Indices, EU15=100, Actual Individual Consumption), last updated 10/07/2025. France values are present for all years 2007–2020 (years 2021–2024 show `:` = not available in this custom extract):

| Year | France PLI (EU15=100) |
| --- | --- |
| 2013 | 99.8 |
| 2014 | 98.7 |
| **2015** | **96.6** |
| **2016** | **98.2** |
| **2017** | **99.9** |
| 2018 | 100.1 |
| 2019 | 98.5 |
| 2020 | 97.8 |

Both 2015 (PLI = 96.6) and 2017 (PLI = 99.9) are available. The v3.1 memo specifies using 2016 as the numeraire (PLI = 98.2), so the deflation factors are:

- 2015 → 2016: 96.6 / 98.2 = 0.9837
- 2017 → 2016: 99.9 / 98.2 = 1.0173

No additional download is required for CPI/PPP deflation.

---

## 10. EUROMOD Output Variable Comparability: FR_2015, FR_2016, FR_2017

**Condition:** The standard output policy (`output_std_fr`) must produce the same income variable groups and standardised income lists across all three systems, so that the same budget constraint can be computed uniformly.

**Finding: SATISFIED — output structure is identical across all three systems.**

The `euromod_fr_2015_2017_output_variable_index.csv` documents the standard output policies for FR_2015, FR_2016, and FR_2017. The `output_std_fr` policy in all three systems includes identical variable groups (`id*`, `d*`, `l*`, `y*`, `p*`, `b*`, `t*`, `x*`, `a*`, `k*`, `s*`, `i_*`, `ils_*`, `il_*`) and the same set of six tax-unit `UnitInfo` blocks. The output filename differs only by year suffix (`FR_2015_std`, `FR_2016_std`, `FR_2017_std`).

The `euromod_fr_2015_2017_standard_income_concepts.csv` documents 34 standardised income concepts (`ils_earns`, `ils_origy`, `ils_dispy`, `ils_ben`, `ils_tax`, etc.). Zero differences were found across the three systems — every concept has the same component list and signs in all three years. The core budget-constraint aggregate `ils_dispy` is fully comparable across 2015, 2016, and 2017.

---

## 11. Raw Microdata Column Differences Across Years

**Finding: Three structural differences; none affect RURO-critical variables.**

| Column | 2015 | 2016 | 2017 | Note |
| --- | --- | --- | --- | --- |
| `tpr` (ISF wealth tax) | ✓ | ✗ | ✗ | 2015 only; ISF abolished in 2018. Not used in RURO utility. |
| `dmb` (month of birth) | ✗ | ✓ | ✓ | Available from 2016 onward. Not used in RURO. |
| `twl` (flat corporate welfare tax) | ✗ | ✓ | ✓ | Introduced 2016. Not used in RURO. |
| `yptmp` | ✗ | ✓ | ✓ | 2016 onward. Not used in RURO. |
| `ltr` | ✗ | ✗ | ✓ | 2017 only (training indicator). Not used in RURO. |
| `ymwdt` | ✗ | ✗ | ✓ | 2017 only (wage subsidy). Not used in RURO. |
| `bchba` | ✗ | ✗ | ✓ | 2017 only (childcare benefit). Enters `ils_ben`, comparable. |
| `bsawk` | ✗ | ✗ | ✓ | 2017 only. Enters `ils_ben`, comparable. |

All RURO pipeline variables (`idhh`, `idperson`, `idorighh`, `idorigperson`, `drgn1`, `deh`, `dgn`, `dag`, `dms`, `dwt`, `yem`, `bun`, `pdi`, `poa`, `yse`, `lhw`, `yem00`, `yemxp`, `lfs`, `lcs`, `les`) are present in all three years. The year-specific additions in 2016 and 2017 (`bchba`, `bsawk`) enter the standardised `ils_ben` aggregate rather than the RURO utility function directly, so `ils_dispy` remains comparable across years.

---

## 12. Processed MNL Parquet Availability

**Condition:** Processed MNL parquets for 2015 and 2017 must exist (or a plan to build them must be feasible) to begin pooled estimation.

**Finding: NOT YET AVAILABLE — only 2016 parquets exist.**

Processed RURO MNL parquets in `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\`:

| Path | Description | Status |
| --- | --- | --- |
| `2016/ruro_occ/scenarios/combined_draws_em.parquet` | Active 2016 MNL parquet | ✓ Present (487.9 MB) |
| `2016/job_model_gmm/scenarios/combined_draws_em.parquet` | 2016 GMM variant | ✓ Present (457.8 MB) |
| `2016/job_model/scenarios/combined_draws_em.parquet` | 2016 older variant | ✓ Present (206.5 MB) |
| `2015/...` | 2015 MNL parquet | **✗ Absent** |
| `2017/...` | 2017 MNL parquet | **✗ Absent** |

The RURO1 archive (`Z:\hisham\EUROMOD-STORAGE\RURO1\`) contains 2016 and 2021 parquets from earlier pipeline iterations but no 2015 or 2017 data.

**To build 2015 and 2017 MNL parquets:** (1) Run EUROMOD FR_2015 and FR_2017 systems to generate budget-constraint output files; (2) run `enh_RURO_prep_mnl_basic.py` for each year; (3) run `enh_RURO_mnl_rebuild_GSURv2_stageA.py` (or equivalent) to merge GSUR v2 rates for 2015/2017 and produce the MNL draws. Steps 1–3 are the entire data pipeline — none of this is blocked by missing inputs (F1–F6 are all satisfiable), but each step requires explicit execution.

---

## 13. GSUR v2 Lookup Extension to 2015 and 2017

**Condition:** The GSUR v2 lookup (`FR_gsur_ruro_v2_stageA.parquet`) currently covers 2016 only and must be extended.

**Finding: One hardcoded year constant and one re-download required.**

Current state of `Data/external/FR_gsur_ruro_v2_stageA.parquet`:
- Shape: (54, 11) — 54 rows for 2016 only (9 regions × 3 educ × 2 sex)
- `year` column: `[2016]` only

Required changes to generate 2015 and 2017 entries:

1. **Re-download Eurostat denominators** (`lfst_r_lfsd2pop`, `lfst_r_lfp2acedu`) with `startPeriod=2015&endPeriod=2017`. The current files (`lfst_r_lfsd2pop_2016_full.csv`, `lfst_r_lfp2acedu_2016_full.csv`) cover 2016 only.

2. **Edit `enh_prepare_FR_gsur_v2.py` line 44:** Change `YEAR = 2016` to accept a year parameter. The internal logic already supports multi-year extraction via `_find_year_col(df_raw, year)`. The rate source (`FR_gsur.xlsx`) already covers 2015 and 2017.

3. **Run the script** for years 2015 and 2017 to produce year-specific lookup files, then concatenate into an extended `FR_gsur_ruro_v2_stageA.parquet` covering all three years.

The v1 GSUR lookup (`FR_gsur_ruro.parquet`) already covers years 2007–2024 with complete coverage for 2015 and 2017, so if GSUR v1 is acceptable for pooled estimation, no extension work is needed. The gap applies only to GSUR v2 (weighted-denominator variant).

---

## 14. Prep Script Parameterization

**Condition:** `enh_RURO_prep_mnl_basic.py` must support year parameterization to run the preprocessing pipeline for 2015 and 2017.

**Finding: PARTIALLY PARAMETERIZED — GSUR merge is year-aware, but data paths are hardcoded.**

The script already has a year-aware GSUR merge (uses a `year` column from the data), but the main data paths are hardcoded to 2016:

- Line 17 (argparse default): `--mnl-base "U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl"`
- Line 18: `--output-dir "outputs/estimation/FR_2016"`

To run for 2015 or 2017, these paths must be passed as CLI arguments pointing to the corresponding EUROMOD output files for those years. Since the 2015/2017 EUROMOD output files do not yet exist (they must be run first), this is a sequencing dependency rather than a script limitation. Once EUROMOD output for 2015/2017 exists at appropriate paths, the prep script can be invoked with the correct `--mnl-base` argument.

The `_ensure_year_column()` helper (lines 136–162) correctly handles year extraction from column fallbacks (`year_for_ruro`, `data_year`). The GSUR merge logic (`merge_gsur_v2` function) is fully year-generic.

---

## 15. Estimation Script Parameterization

**Condition:** `enh_RURO_estimate_FR.py` must accept multi-year stacked parquet input.

**Finding: NOT YET VERIFIED — but no architectural obstacle identified.**

The estimation script accepts `--mnl-base` pointing to the processed parquet directory. For pooled estimation, the P2/P3 stacked parquet would be the input. The main estimation engine (`estimation_engine.py`, `gamspy_estimation_vectorized.py`) operates on in-memory arrays from the parquet — it has no year-specific logic. Cluster-robust SE computation (T1 strategy) requires the `idhh` cluster variable to be present in the estimation input, which it will be given the standard prep output.

No structural changes to the estimation engine itself are needed for pooled estimation. The only new requirement is (a) a pooled parquet builder (not yet written) that stacks 2015/2016 or 2015/2016/2017 parquets with UID remapping per the `B = 10^11` scheme, and (b) a `cluster_id` column passed to the SE computation. These are new pipeline components, not modifications to the existing estimator.

---

## 16. P2 Configuration: 2015 + 2016

**Summary assessment:** Feasible pending data pipeline execution.

| Prerequisite | Status |
| --- | --- |
| FR_2015 EUROMOD system | ✓ Available (J1.0+ FR.xml) |
| FR_2015 microdata | ✓ Available (`FR_2015_a2.txt`, 26,558 individuals) |
| FR_2016 MNL parquet | ✓ Exists |
| FR_2015 MNL parquet | ✗ Requires EUROMOD run + prep |
| GSUR v2 for 2015 | ✗ Requires denominator re-download + script edit |
| GSUR v1 for 2015 | ✓ Already in `FR_gsur_ruro.parquet` |
| INSEE benchmark 2015 | ✗ Requires API call |
| CPI deflator 2015 → 2016 | ✓ 96.6 / 98.2 = 0.9837 |
| Overlap structure | ✓ P2 fully disjoint (2015 ∩ 2016 = ∅) |
| UID encoding B=10^11 | ✓ Sufficient |
| Income concept comparability | ✓ Identical across 2015, 2016 |

Estimated pooled P2 sample: ~22,849 households (11,390 + 11,459). No cluster-robust correction needed (fully disjoint years; standard survey weighting applies).

---

## 17. P3 Configuration: 2015 + 2016 + 2017

**Summary assessment:** Feasible pending data pipeline execution; one additional inference design requirement.

| Prerequisite | Status |
| --- | --- |
| FR_2017 EUROMOD system | ✓ Available (J1.0+ FR.xml) |
| FR_2017 microdata | ✓ Available (`FR_2017_a2.txt`, 25,309 individuals) |
| FR_2017 MNL parquet | ✗ Requires EUROMOD run + prep |
| GSUR v2 for 2017 | ✗ Requires denominator re-download + script edit |
| GSUR v1 for 2017 | ✓ Already in `FR_gsur_ruro.parquet` |
| INSEE benchmark 2017 | ✗ Requires API call |
| CPI deflator 2017 → 2016 | ✓ 99.9 / 98.2 = 1.0173 |
| Overlap structure | ✓ 8,796 repeat households (2016 ∩ 2017) |
| Cluster-robust SEs (T1) | ✗ Not yet implemented in estimation engine |
| UID encoding B=10^11 | ✓ Sufficient |
| Income concept comparability | ✓ Identical across 2016, 2017 |

Estimated pooled P3 sample: ~33,917 household rows (11,390 + 11,459 + 11,068), of which 8,796 are repeat households in 2016–2017. Cluster-robust standard errors at household level (T1) are a required inference change for P3.

---

## 18. Temporal Validation: 2016 Estimates → 2017 Holdout

**Condition:** The v3.1 memo proposes using 2016 estimates to predict 2017 labour-supply outcomes and computing a pseudo-R² holdout score.

**Finding: Feasible pending 2017 MNL parquet.**

The 2016 estimates (M1-clean selected) are available in `outputs/estimates/fr/spec/ruro_occ/`. Applying them to the 2017 parquet is a forward-prediction pass, not a re-estimation — it requires only that the 2017 parquet exists with the same variable schema as 2016. The schema compatibility check in Section 11 confirms all RURO variables are present in FR_2017_a2. The post-estimation script (`RURO_post_estimation_styled.py`) would need a `--holdout-year` or `--prediction-only` mode to suppress re-estimation and output only log-likelihood and confusion matrix statistics. This is a new script mode, not yet written.

---

## 19. Script Reuse Assessment

| Script | 2015/2017 ready? | What changes |
| --- | --- | --- |
| `enh_RURO_prep_mnl_basic.py` | Mostly | Change CLI default paths; no logic change |
| `enh_prepare_FR_gsur_v2.py` | No | Change line 44 `YEAR = 2016` to CLI arg; add `--year` |
| `enh_prepare_FR_gsur.py` | Yes | Already year-agnostic (reads all years from xlsx) |
| `enh_RURO_estimate_FR.py` | Yes | Accepts any `--mnl-base`; no year logic |
| `enh_RURO_mnl_rebuild_GSURv2_stageA.py` | Not verified | Likely needs `--year` arg; not inspected here |
| Post-estimation script | Partial | Needs `--prediction-only` mode for temporal validation |
| **New: pooled-parquet builder** | Not written | Required: stacks parquets, applies B-encoding, adds `year` column |
| **New: cluster-SE wrapper** | Not written | Required for P3 T1 inference |

---

## 20. Open Data Acquisition Items

Items not yet available that block P2/P3 implementation:

| Item | Action required | Complexity |
| --- | --- | --- |
| FR_2015 EUROMOD budget-constraint output | Run FR_2015 system in EUROMOD J1.0+ | Medium (1–2 hours) |
| FR_2017 EUROMOD budget-constraint output | Run FR_2017 system in EUROMOD J1.0+ | Medium (1–2 hours) |
| `lfst_r_lfsd2pop` 2015 & 2017 denominators | Eurostat SDMX-CSV API re-download with `startPeriod=2015&endPeriod=2017` | Low (minutes) |
| `lfst_r_lfp2acedu` 2015 & 2017 denominators | Same API, different dataset | Low (minutes) |
| INSEE BDM 001688526 for 2015 & 2017 | INSEE BDM API call | Low (minutes) |
| `enh_prepare_FR_gsur_v2.py` year parameterization | Edit line 44; add `--year` argparse | Low (< 1 hour) |
| Pooled-parquet builder script | New script: stack, UID-remap, deflate | High (new development) |
| Cluster-robust SE wrapper (T1) | Add to estimation engine or post-processing | High (new development) |

---

## 21. Verdict: F1–F6 Summary

| Condition | Description | Status |
| --- | --- | --- |
| F1 | EUROMOD systems (FR_2015, FR_2016, FR_2017) available | ✓ SATISFIED |
| F2 | EU-SILC microdata for all three years present | ✓ SATISFIED |
| F3 | All RURO-critical identifiers and demographic variables present | ✓ SATISFIED |
| F4 | Eurostat GSUR sources for 2015 and 2017 available | ⚠ PARTIALLY SATISFIED (rates available, denominators require re-download for v2) |
| F5 | INSEE national benchmark for 2015 and 2017 available | ✗ NOT SATISFIED (API call required) |
| F6 | CPI/PPP data for 2015 and 2017 available | ✓ SATISFIED |

Blocking gaps: F4 (partial) and F5 (absent). Both are mechanical data-acquisition tasks requiring Eurostat API and INSEE API calls — no structural obstacles, no schema problems, no missing variables.

---

## 22. Feasibility Conclusion

**P2 (2015 + 2016) is feasible.** All structural preconditions are met. Three data-acquisition tasks (INSEE benchmark 2015, Eurostat denominators 2015, GSUR v2 script edit) and one pipeline execution task (EUROMOD FR_2015 run + MNL parquet build) must complete before estimation can begin. The P2 stacked sample is fully disjoint; no new inference machinery is needed beyond what exists for P1.

**P3 (2015 + 2016 + 2017) is feasible but requires two new software components.** On top of the P2 requirements, P3 also needs (a) EUROMOD FR_2017 run + 2017 MNL parquet, (b) GSUR v2 extension for 2017, and (c) the cluster-robust SE wrapper (T1) to handle the 8,796 repeat households in the 2016–2017 overlap. Items (a)–(b) are execution tasks; (c) is new development.

**Temporal validation (2016 → 2017 holdout) is feasible** once the 2017 MNL parquet is built, with the addition of a `--prediction-only` mode in the post-estimation script.

**Recommended sequencing:**

1. Acquire three small data files (INSEE BDM 2015/2017, Eurostat denominators 2015/2017) — < 1 hour.
2. Parameterize `enh_prepare_FR_gsur_v2.py` by year — < 1 hour.
3. Run EUROMOD FR_2015 and FR_2017 — 2–4 hours.
4. Build MNL parquets for 2015 and 2017 (prep + GSUR merge) — 2–4 hours.
5. Write pooled-parquet builder script (stacking + UID remapping + CPI deflation) — new development.
6. For P3: write cluster-robust SE wrapper.
7. Run P2 estimation.
8. Run P3 estimation (after cluster-robust SE is available).

---

## 23. Appendix: Key File Locations

| Asset | Path |
| --- | --- |
| FR_2015 microdata | `Z:\Hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` |
| FR_2016 microdata | `Z:\Hisham\EUROMOD-STORAGE\Data\FR\FR_2016_a3.txt` |
| FR_2017 microdata | `Z:\Hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` |
| EUROMOD J1.0+ FR.xml | `Z:\...\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+\XMLParam\Countries\FR\FR.xml` |
| Active 2016 MNL parquet | `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\stijn_occ\scenarios\combined_draws_em.parquet` |
| GSUR rates lookup (v1, all years) | `U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet` |
| GSUR v2 lookup (2016 only) | `U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro_v2_stageA.parquet` |
| GSUR xlsx (raw, all years) | `U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur.xlsx` |
| CPI/PPP data | `U:\Desktop\Nizam_Hisham\MNL\Data\external\cpi.xlsx` |
| INSEE benchmark (2016) | `U:\Desktop\Nizam_Hisham\MNL\Data\external\insee_001688526_2016.csv` |
| Eurostat population denominators (2016) | `U:\Desktop\Nizam_Hisham\MNL\Data\external\lfst_r_lfsd2pop_2016_full.csv` |
| EUROMOD output variable index | `U:\Desktop\Nizam_Hisham\MNL\Data\documentation\euromod_fr_2015_2017_output_variable_index.csv` |
| Income concepts comparability | `U:\Desktop\Nizam_Hisham\MNL\Data\documentation\euromod_fr_2015_2017_standard_income_concepts.csv` |
| GSUR v2 prep script | `U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_prepare_FR_gsur_v2.py` |
| Prep MNL script | `U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py` |
| Main estimation script | `U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_estimate_FR.py` |
| v3.1 strategy memo | `U:\Desktop\Nizam_Hisham\MNL\docs\JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` |