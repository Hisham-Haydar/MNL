# JMP Multi-Year Pipeline — Stage M1 Implementation Plan

**Document:** JMP_multi_year_stage_M1_implementation_plan_v2.md  
**Supersedes:** docs/JMP_multi_year_stage_M1_implementation_plan_v1.md  
**Date:** 2026-05-19  
**Revision:** Targeted corrections to UID naming (`stacked_hh_uid`/`stacked_person_uid`), clustering column name (`cluster_id`), and implementation prompt stacking rule. No substantive changes to sequencing, authorisations, or configurations.  
**Audit basis:** Results/JMP_multi_year_feasibility_audit_v1.md, Results/JMP_multi_year_feasibility_audit_addendum_v1.md, Results/JMP_multi_year_feasibility_audit_addendum_v2.md  
**Strategy reference:** docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md  

---

## 1. Purpose of Stage M1

Stage M1 is the data-engineering layer that transforms single-year processed microdata into a pooled, longitudinally coherent dataset ready for multi-year RURO estimation. It does not run any estimation. It produces:

1. A CPI/HICP harmonisation utility that deflates nominal income variables to a common price base.
2. A stacked-ID utility that assigns each observation a globally unique identifier encoding its source year (`stacked_hh_uid` at household level; `stacked_person_uid` at person level).
3. A raw-ID preservation step that retains the original EU-SILC household and person identifiers alongside the stacked UIDs.
4. A repeated-household clustering support layer that annotates each row with its canonical clustering key for downstream cluster-robust inference.

Stage M1 ends when a pooled parquet file for the chosen configuration is written, all ID and CPI fields are verified, and the validation checklist (Section 17) is signed off. Stage M1 does **not** include pooled estimation, welfare computation, welfare scaffolding, canonical MNL promotion, or GSUR Stage B.

---

## 2. Current Feasibility Status

Condition summary as of 2026-05-19, drawing from addendum v2:

| Condition | 2015 | 2016 | 2017 | 2018 |
| --- | --- | --- | --- | --- |
| F1: EUROMOD system | ✓ | ✓ | ✓ | ✓ |
| F2: EU-SILC microdata | ✓ | ✓ | ✓ | ✓ |
| F3: Eurostat GSUR denominators | ✗ | ✓ | ✗ | ✗ |
| F4: INSEE benchmark | ✗ | ✓ | ✗ | ✗ |
| F5: INSEE CPI | ✗ | ✓ | ✗ | ✗ |
| F6: EUROMOD comparability | ✓ | ✓ | ✓ | ✓ *(ISF flag)* |

**Stage M1 is mechanically executable for a 2015+2016+2017 configuration** provided:
- The CPI source decision (Section 7) is made before running harmonisation.
- Eurostat GSUR denominators for 2015 and 2017 are downloaded (single API call).
- INSEE benchmark for 2015 and 2017 are retrieved from BDM series 001688526.

These are acquisition tasks, not implementation tasks. Stage M1 implementation can be coded in parallel with acquisition and executed once all inputs are present.

**P3b (2015+2016+2018) is not execution-ready** pending the ISF/`tpr` comparability check (Section 16).

---

## 3. Inputs

### Required for P3a (primary)

| Input | Source | Status |
| --- | --- | --- |
| `FR_2015_a2.txt` | `Z:\Hisham\EUROMOD-STORAGE\Data\FR\` | Present |
| `FR_2016_a3.txt` | Same | Present |
| `FR_2017_a2.txt` | Same | Present |
| EUROMOD output for FR_2015 | Not yet run | Absent |
| EUROMOD output for FR_2016 | Not yet run for multi-year run | Absent |
| EUROMOD output for FR_2017 | Not yet run | Absent |
| MNL parquet for 2015 | Requires prep script run for FR_2015 | Absent |
| MNL parquet for 2016 | Present (existing `fr_2016_RURO_mnl_job_gmm`) | Present |
| MNL parquet for 2017 | Requires prep script run for FR_2017 | Absent |
| `lfst_r_lfsd2pop` 2015, 2017 | Eurostat API re-download | Absent |
| `lfst_r_lfp2acedu` 2015, 2017 | Eurostat API re-download | Absent |
| INSEE BDM 001688526 for 2015, 2017 | BDM web service | Absent |
| CPI/HICP series (see Section 7) | HICPCONFIG.xml or INSEE | Decision pending |
| `FR_gsur_ruro.parquet` (v1) | Present in `Data/external/` | Present (2015, 2017, 2018 rows exist) |
| `FR_gsur_ruro_v2_stageA.parquet` extended | Requires GSUR v2 script re-run | Absent (2016 only) |

### Additional inputs for P3b robustness branch (contingent)

| Input | Status |
| --- | --- |
| `FR_2018_a2.txt` | Present |
| EUROMOD output for FR_2018 | Absent |
| MNL parquet for 2018 | Absent |
| ISF/`tpr` comparability check memo | Not written |
| `lfst_r_lfsd2pop` 2018, `lfst_r_lfp2acedu` 2018 | Absent |
| INSEE BDM 001688526 for 2018 | Absent |

---

## 4. Outputs

Stage M1 produces the following files. All paths are under the project root `U:\Desktop\Nizam_Hisham\MNL\`.

| Output file | Description |
| --- | --- |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | Vertically stacked single-year parquets for 2015+2016+2017 with raw IDs, `stacked_hh_uid`, and `stacked_person_uid` appended |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | P3a with CPI-deflated income columns added (`*_real` suffix), `cluster_id` column appended |
| `Data/processed/fr/pooled/fr_p3b_stacked_raw.parquet` | Same for 2015+2016+2018 (written only after P3b is activated; see Section 16) |
| `Data/processed/fr/pooled/fr_p3b_harmonised.parquet` | P3b harmonised (contingent) |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | Authoritative φ_t factor table for the project; one row per year; signed off at Section 7 decision |
| `Results/M1_stacked_id_manifest_<UTC>.csv` | Row-count audit: per-year individual and household counts, `stacked_hh_uid` and `stacked_person_uid` range, duplicate-UID check |
| `Results/M1_raw_id_preservation_check_<UTC>.csv` | Confirms `idorighh` and `idorigperson` present and non-null in pooled file |
| `Results/M1_cluster_key_check_<UTC>.csv` | Confirms `cluster_id` column populates correctly; cross-tabulation of repeat vs unique households by year-pair |
| `Results/M1_identity_validation_summary.md` | One-line per year-pair: pass/fail on suspicious-record threshold (≤ 0.20%) |
| `Results/M1_cpi_harmonisation_check_<UTC>.csv` | Distribution summary of `*_real` variables before and after deflation; confirms φ_t applied per year |

---

## 5. Primary Year Configurations

Two configurations are tracked. Only P3a is authorised for immediate implementation. P3b requires the ISF check before activation.

| Configuration | Years | HH-rows | Unique HH | Repeat HH | Repeat HH / total | T1 required |
| --- | --- | --- | --- | --- | --- | --- |
| P2 | 2015+2016 | 22,849 | 22,849 | 0 | 0.0% | No |
| **P3a (primary)** | **2015+2016+2017** | **33,917** | **25,121** | **8,796** | **25.9%** | **Yes** |
| P3b (robustness, contingent) | 2015+2016+2018 | 33,725 | 26,660 | 7,065 | 20.9% | Yes |
| P4 (not a priority) | 2015+2017+2018 | 33,334 | 24,813 | 8,521 | 25.6% | Yes |

P3a is the implementation target throughout this document. P3b instructions are marked **(P3b contingent)** where they differ.

P2 (2015+2016) is a valid sub-configuration of P3a and requires no additional infrastructure beyond what P3a needs. Its pooled file can be derived from P3a by year-filter.

P4 is not a priority. No implementation effort is allocated to it in Stage M1.

---

## 6. Treatment of 2018 as a Robustness Branch

`FR_2018_a2.txt` is present and confirmed compatible with the B=10^11 UID scheme (max idperson=499,180,001, well below B=10^11). FR_2018 is installed in EUROMOD J1.0+. GSUR rates for 2018 exist in `FR_gsur_ruro.parquet`. The mechanical acquisition gaps for 2018 (Eurostat denominators, INSEE benchmark) are identical to those for 2015 and 2017 and can be resolved in the same single API call (Section 15).

Despite this, P3b is **not** activated in Stage M1 for two reasons:

1. **ISF/`tpr` comparability:** `tpr` is absent in 2016 and 2017 but present in 2018 (and 2015). The 2018 EUROMOD system simulates the ISF wealth tax, which enters `ils_tax` and therefore `ils_dispy`. This creates an income-definition asymmetry between the 2018 and 2016/2017 observations in any pooled dataset. The asymmetry must be quantified before P3b can be used for estimation (Section 16).

2. **Logical consistency with v3.1 memo:** The v3.1 memo names 2015, 2016, 2017 as the primary three-year window throughout. Extending to 2018 requires a deliberate revision to the strategy document.

**When P3b can be activated:** After (a) the ISF comparability memo is written and concludes the ISF contribution to `ils_dispy` is negligible or can be stripped, (b) the v3.1 memo is updated or a supplement is written, and (c) 2018 EUROMOD outputs and MNL parquet are produced.

The Stage M1 scripts must be written to accept a `--config {p3a,p3b,p4}` argument so that P3b and P4 stacks can be built later without code changes.

---

## 7. CPI / HICP Source Decision

**Status: decision required before Stage M1 can run harmonisation.**

### The problem

The v3.1 memo specifies "INSEE domestic CPI" as the deflator. The file `Data/external/cpi.xlsx` contains `prc_ppp_ind__custom_19205378` — Eurostat PPP price-level indices (base EU15=100). This is a cross-country comparator, not a domestic time-series deflator; it cannot serve as the v3.1 CPI requirement. F5 is currently unsatisfied.

### Available options

**Option A — Retrieve INSEE domestic CPI.** Download the INSEE Indice des prix à la consommation (IPC), all-items, metropolitan France, annual average, base 2015=100, from INSEE BDM or data.gouv.fr. This is the literal specification in v3.1. Preferred if the series is readily retrievable.

**Option B — Formally adopt EUROMOD HICP as proxy.** `HICPCONFIG.xml` contains France HICP values from Eurostat/AMECO (base 2015=100):

| Year | HICP index (base 2015=100) | φ_t = 100.31 / index |
| --- | --- | --- |
| 2015 | 100.00 | 1.0031 |
| 2016 | 100.31 | 1.0000 (base year) |
| 2017 | 101.47 | 0.9886 |
| 2018 | 103.60 | 0.9682 |

The φ_t factors are small (maximum deviation < 3.2% over the 2015–2018 window) and are directionally consistent with expectations (mild French inflation). Using HICP as a proxy is defensible and common in EUROMOD multi-country studies.

**If Option B is chosen**, the adoption must be documented explicitly:
- `Data/external/cpi_hicp_fr_harmonisation.csv` is the authoritative source.
- `docs/JMP_multi_year_stage_M1_implementation_plan_v1.md` (this document) records the decision and rationale.
- A note must appear in the estimation results section of the JMP draft: "Nominal income variables are deflated to 2016 prices using France HICP values from EUROMOD's HICPCONFIG.xml (Eurostat/AMECO 2023 spring forecasts, base 2015=100), adopted in lieu of the INSEE domestic CPI specified in the strategy memo."

**Stage M1 must not silently substitute HICP for INSEE CPI.** The φ_t values must not be hard-coded in a script without the decision being documented. If Option A is retrieved, the `cpi_hicp_fr_harmonisation.csv` is populated from that series instead.

---

## 8. Monetary Variables to Harmonise

All variables entering the RURO utility function that are expressed in nominal euros must be deflated. The deflation factor φ_t multiplies each variable, converting it to 2016 prices.

| Variable | Role | Notes |
| --- | --- | --- |
| `ils_dispy` | Full household disposable income | Primary income measure in the budget constraint |
| `ils_earns` | Labour earnings | Used to construct wage offers and opportunity income |
| `yem` | Employee income | Component of earnings |
| `yse` | Self-employment income | Component of earnings |
| `ypen` | Pension income | Used in non-employment income computation |
| `ypt` | Private transfers | Component of non-labour income |
| `ils_ben` | Social benefits | Total benefits aggregate |
| Wage-imputed variables (if present) | Any variable derived from `ils_earns` in prep scripts | Apply deflation before imputation or confirm imputation is done on real values |

Variables are deflated by adding a `_real` column: `{var}_real = {var} × φ_t` where `φ_t` is looked up from `cpi_hicp_fr_harmonisation.csv` by year. Original nominal columns are preserved alongside the real columns; no column is deleted.

The GSUR rates in `FR_gsur_ruro.parquet` are dimensionless shares (employment/unemployment rates); they do not require deflation.

---

## 9. Variables Not to Harmonise

The following variables must **not** be deflated:

| Variable | Reason |
| --- | --- |
| All quantity/binary/categorical variables | `dgn`, `dag`, `dms`, `deh`, `drgn1`, occupation codes, employment-status codes — no monetary dimension |
| `idhh`, `idperson`, `idorighh`, `idorigperson` | Identifiers; numeric values are structural, not monetary |
| `dwt` (survey weight) | Dimensionless ratio; must not be scaled |
| GSUR rates (`gsur_*`, `gsur_v2_*`) | Dimensionless probabilities |
| Year dummies and year indicator | Fixed effects; deflation is applied per-year, not to the year variable itself |
| `tpr` (ISF wealth tax, 2015 and 2018 only) | Do not deflate; flag for ISF check (Section 16). If pooling includes 2015 or 2018, document presence explicitly |
| `stacked_hh_uid`, `stacked_person_uid`, `cluster_id`, `year_tag` | Structural columns added by Stage M1 |

---

## 10. Stacked-ID Rule

A single base B = 10^11 is used for both household- and person-level UIDs:

```
stacked_hh_uid     = year_tag × B + idhh
stacked_person_uid = year_tag × B + idperson
```

where:
- `year_tag` is an integer: 2015 → 1, 2016 → 2, 2017 → 3, 2018 → 4.
- `idhh` is the within-year EUROMOD household identifier.
- `idperson` is the within-year EUROMOD person identifier.
- B = 100,000,000,000 (10^11).

**Why B = 10^11 is sufficient for both IDs:**

The binding constraint is the largest raw identifier across all years. For `idhh` that is 93,789,900 (2016); for `idperson` it is 9,378,990,002 (2016). Both are strictly less than 10^11 = 100,000,000,000:

```
93,789,900       < 100,000,000,000   ✓  (household IDs: ~3 orders below B)
9,378,990,002    < 100,000,000,000   ✓  (person IDs: binding constraint, still below B)
```

**Household-level verification:**

| Year | `idhh` max | `year_tag × B` | max `stacked_hh_uid` | Next year's base |
| --- | --- | --- | --- | --- |
| 2015 | 1,478,400 | 1 × 10^11 | 100,001,478,400 | 2 × 10^11 = 200,000,000,000 |
| 2016 | 93,789,900 | 2 × 10^11 | 200,093,789,900 | 3 × 10^11 = 300,000,000,000 |
| 2017 | 4,671,300 | 3 × 10^11 | 300,004,671,300 | 4 × 10^11 = 400,000,000,000 |
| 2018 | 4,991,800 | 4 × 10^11 | 400,004,991,800 | — |

**Person-level verification:**

| Year | `idperson` max | `year_tag × B` | max `stacked_person_uid` | Next year's base |
| --- | --- | --- | --- | --- |
| 2015 | 147,840,002 | 1 × 10^11 | 100,147,840,002 | 2 × 10^11 = 200,000,000,000 |
| 2016 | 9,378,990,002 | 2 × 10^11 | 209,378,990,002 | 3 × 10^11 = 300,000,000,000 |
| 2017 | 467,130,003 | 3 × 10^11 | 300,467,130,003 | 4 × 10^11 = 400,000,000,000 |
| 2018 | 499,180,001 | 4 × 10^11 | 400,499,180,001 | — |

In every case, `max stacked_person_uid < next year's base`. No cross-year collision is possible. Both series are `int64` (max value ~4×10^11, well within int64 range of ~9.2×10^18).

**Distinguishing household and person UIDs:**

`stacked_hh_uid` is unique per household-year, not per row of a person-level file. In a person-level pooled dataset, every member of the same household in the same year shares the same `stacked_hh_uid`. `stacked_person_uid` is unique per person-year row. Both columns are written to the pooled file. Uniqueness assertions in validation (Section 17) are applied to the correct column for the unit of analysis.

The `year_tag` column is retained as a separate integer column. Neither UID is used as the clustering key (see Section 12).

---

## 11. Raw ID Preservation

Before stacking, the following four original EU-SILC identifiers must be preserved as separate columns in the pooled file:

| Column | Type | Source | Role |
| --- | --- | --- | --- |
| `idorighh` | int64 | Raw EU-SILC household ID | Clustering key (Section 12); panel identity |
| `idorigperson` | int64 | Raw EU-SILC person ID | Person-identity validation; longitudinal tracking |
| `idhh` | int64 | EUROMOD within-year household ID | Used in `stacked_hh_uid` construction |
| `idperson` | int64 | EUROMOD within-year person ID | Used in `stacked_person_uid` construction |

None of these four columns may be renamed, overwritten, or dropped during stacking. The stacking script must assert their presence and non-nullity before writing the pooled file.

The identity-validation diagnostics in addendum v2 confirm that `idorigperson` reliably identifies the same physical person across waves (suspicious-record rate ≤ 0.13% in all overlapping year pairs). The `idorighh` column is the primary cross-wave key for households and the clustering key.

---

## 12. Household-Clustering Key

For all configurations involving 2016+2017, 2016+2018, or 2017+2018 overlap (P3a, P3b, P4), cluster-robust standard errors must be estimated with households clustered at the **original EU-SILC household identifier `idorighh`**.

**Why `idorighh` and not `idhh`:** EUROMOD assigns `idhh` independently within each year. Two rows from different years with the same `idorighh` will have different `idhh` values. The `idorighh` is the stable cross-wave identifier that links repeat households. Using `idhh` for clustering would fail to recognise repeat households.

**Implementation in the pooled file:** A column named `cluster_id` is added to the harmonised pooled file:

```
cluster_id = idorighh
```

This is a direct copy; no encoding is applied. The variance estimator for T1 cluster-robust SEs clusters on `cluster_id`.

**P2 exception:** For the 2015+2016 configuration, `idorighh` overlaps are zero (confirmed: 2015 is a different EU-SILC panel). Standard SEs are sufficient; the `cluster_id` column is still written (equal to `idorighh`) but the clustering flag in the estimation config is set to `null`.

**Singleton clusters:** Households appearing in only one year are singleton clusters (no between-wave dependence). The cluster-robust variance estimator handles singletons automatically; no special treatment is needed.

---

## 13. Person-Identity Validation Rule

The identity-validation diagnostics from addendum v2 define the acceptance thresholds applied during Stage M1 data preparation. These thresholds must be re-verified when the actual pooled file is built (the addendum computed them from the raw EU-SILC files; the prep pipeline may drop records).

**Acceptance thresholds for each overlapping year pair:**

| Criterion | Threshold | Fail action |
| --- | --- | --- |
| Sex stability (`dgn` unchanged) | ≥ 99.90% of repeat persons | Warn; write to manifest; do not block |
| Age progression within ±1 of expected gap | ≥ 99.50% of repeat persons | Warn; write to manifest; do not block |
| Suspicious records (sex mismatch OR age off-track by >1) | ≤ 0.20% of repeat persons | Warn if exceeded; block if > 1.00% |
| Household continuity (`idorighh` unchanged) | ≥ 97.00% of repeat persons | Warn; write to manifest; do not block |

**Repeat-person identification:** A person is classified as repeat if their `idorigperson` appears in both years of a pair. The validation script iterates over all year-pairs present in the pooled file, not just those with expected overlap.

**Output:** `Results/M1_identity_validation_summary.md` — one row per year-pair, with pass/fail status on each criterion and the suspicious-record count and percentage.

---

## 14. Missing Relationship Identifiers

The audit confirmed that `idpartner` is absent from all four raw EU-SILC files for France. The RURO couple-matching logic (identifying working-age couples in the choice set) relies on either `idpartner` or household-structure reconstruction from `dms`, `dag`, `dgn`, and household membership.

**Stage M1 does not implement the couple-matching fix.** This is a pre-existing constraint inherited from the 2016-only pipeline. The 2016 M1-clean single-year results were produced under this constraint. Stage M1 preserves the same approach for pooled data.

**What Stage M1 does:** Retains `dms` (marital/cohabitation status) and all demographic variables required for couple identification. The `idpartner` absence is noted in the stacking manifest. No new code is written to reconstruct `idpartner`.

**What is deferred:** Any change to couple-identification logic requires a separate task after Stage M1 is complete. This is not a blocking issue for Stage M1.

---

## 15. GSURv2 Denominator and Benchmark Dependencies

### Eurostat GSUR denominators

The GSUR v2 computation (`scripts/enhanced/enh_prepare_FR_gsur_v2.py`) reads two Eurostat datasets:
- `lfst_r_lfsd2pop` (working-age population denominators by NUTS2 × sex × education)
- `lfst_r_lfp2acedu` (labour force participation denominators)

`Data/external/lfst_r_lfsd2pop_2016_full.csv` contains 2016 only. Both files must be re-downloaded for 2015, 2017, and 2018.

**Acquisition task:** One Eurostat API call with `startPeriod=2015&endPeriod=2018` retrieves all four years for both datasets. This is a mechanical retrieval; no methodological decision is required.

### INSEE benchmark

`Data/external/insee_001688526_2016.csv` contains the 2016 annual average unemployment rate (9.725%, metropolitan France). The 2015 and 2017 values must be retrieved from INSEE BDM series 001688526. If 2018 is later activated, the 2018 value is retrieved in the same call.

**Acquisition task:** BDM REST endpoint for series 001688526, fetching quarterly values for 2015–2018 and computing annual averages.

### GSUR v2 script year-parameterisation

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` line 44 contains:

```python
YEAR = 2016
```

This must be changed to accept a `--year` CLI argument (or a `YEAR` environment variable). The internal `_find_year_col(df_raw, year)` function is already year-generic; only line 44 requires modification.

**Stage M1 implementation task:** Edit line 44 and add `argparse` argument `--year` (int, required). Run the script once per year (2015, 2017; plus 2018 if P3b is activated) after the Eurostat denominator files are present.

### GSUR Stage B

Age-specific GSUR weights (GSUR Stage B) are **not** authorised in Stage M1. The GSUR v1 parquet (`FR_gsur_ruro.parquet`) covers 2015, 2017, and 2018 and is sufficient for Stage M1. GSUR v2 Stage A extension for 2015/2017 is required; GSUR Stage B is deferred.

---

## 16. ISF / `tpr` Comparability Check for 2018

`tpr` is the EUROMOD variable for the ISF (Impôt de solidarité sur la fortune), France's wealth tax. It is present in FR_2015 and FR_2018 but absent from FR_2016 and FR_2017 (ISF was replaced by IFI in 2018, but the tax appeared in both the last year of ISF and the first year of IFI within the EUROMOD system).

**Why this matters:** In 2018, the ISF is simulated by EUROMOD. The simulated ISF value enters `ils_tax` (total tax), which reduces `ils_dispy` (disposable income). For the RURO sample (working-age employees and unemployed), the ISF is a wealth tax affecting very high-net-worth households; most RURO-sample households pay zero ISF. The concern is whether the non-zero ISF observations create a systematic shift in the 2018 `ils_dispy` distribution relative to 2016 and 2017.

**Required check before P3b activation:**

1. Compute the distribution of `tpr` in FR_2018 EUROMOD output for the RURO sample. Report the share of households with `tpr > 0` and the 90th, 95th, 99th percentile of `tpr` (in 2016 euros).
2. Compute the implied impact on `ils_dispy`: for each RURO-sample household, `Δils_dispy = −tpr`. Report the share of households affected and the mean and maximum absolute impact.
3. Re-run the `ils_dispy` comparability check (analogous to the F6 check in the audit) comparing the 2018 distribution against 2016 and 2017 after stripping `tpr` from 2018 `ils_dispy`.
4. Write a one-page memo: `Results/M1_ISF_tpr_comparability_check_2018.md`. Conclude with one of:
   - "ISF impact negligible: proceed with P3b."
   - "ISF impact non-negligible: P3b requires income-concept adjustment (specify adjustment)."
   - "ISF impact non-negligible: P3b not recommended."

This check is a prerequisite for P3b execution but not for P3a. It can be performed in parallel with P3a implementation as soon as FR_2018 EUROMOD output is available.

---

## 17. Validation Checks

The following checks must all pass before Stage M1 is declared complete.

### V1 — Stacked-UID uniqueness

For a **person-level** pooled file:

```python
# stacked_person_uid must be unique per row
assert pooled_df['stacked_person_uid'].nunique() == len(pooled_df)

# stacked_hh_uid is unique per household-year, not per row
# expected duplicates = persons per household; assert no within-year household duplicates
assert pooled_df.groupby(['year_tag', 'stacked_hh_uid']).ngroups == \
       pooled_df[['year_tag', 'idhh']].drop_duplicates().shape[0]
```

For a **household-level** pooled file:

```python
assert pooled_df['stacked_hh_uid'].nunique() == len(pooled_df)
```

No cross-year UID collisions are possible given B = 10^11 (verified in Section 10).

### V2 — Row-count agreement

For P3a: total rows = 33,917 household-rows (or ~97,000 person-rows, depending on unit of analysis). Cross-check against per-year file row counts. Deviations > ±10 rows require investigation.

### V3 — Raw-ID completeness

```
assert pooled_df[['idorighh', 'idorigperson', 'idhh', 'idperson']].notna().all().all()
```

### V4 — Year-tag coverage

```
assert set(pooled_df['year_tag']) == {1, 2, 3}   # for P3a
```

### V5 — CPI deflation correctness

For each year t, sample 100 rows and verify:

```
assert abs(row['ils_dispy_real'] - row['ils_dispy'] * phi_t) < 1e-6
```

Also verify that the `ils_dispy_real` distributions for each year are plausible: mean disposable income for the RURO sample should be in the range 25,000–55,000 euros per year in 2016 prices.

### V6 — Clustering key integrity

```python
assert (pooled_df['cluster_id'] == pooled_df['idorighh']).all()
```

For P3a, count repeat households: `idorighh` values appearing in both year_tag=2 (2016) and year_tag=3 (2017) rows. Expected: approximately 8,796 unique `idorighh` values. Deviation > ±200 requires investigation.

### V7 — Person-identity validation

Run the thresholds in Section 13 on the pooled file. All criteria must pass at the warn level; none may reach the block level.

### V8 — GSUR coverage

For every row in the pooled file, the GSUR merge must produce a non-null `gsur` value. Zero missing GSUR values allowed.

### V9 — No `stijn` token in any output file

```
grep -ri "stijn" Data/processed/fr/pooled/
```

Must return zero matches. Naming conventions follow the RURO package standard (Section 18, script naming).

### V10 — ISF check (P3b only)

If P3b pooled file is written, the ISF comparability memo (Section 16) must exist and conclude "proceed" before V10 is checked off.

---

## 18. Required Scripts

The following scripts must be created or modified for Stage M1. All new scripts go under `scripts/multi_year/`.

### New scripts

| Script | Purpose |
| --- | --- |
| `scripts/multi_year/m1_stack_years.py` | Reads per-year MNL parquets, adds `year_tag`, `stacked_hh_uid`, `stacked_person_uid`, preserves raw IDs, writes `fr_p{config}_stacked_raw.parquet`. CLI: `--config {p3a,p3b,p4}`. |
| `scripts/multi_year/m1_harmonise_cpi.py` | Reads `cpi_hicp_fr_harmonisation.csv`, deflates monetary columns by year, writes `fr_p{config}_harmonised.parquet`. CLI: `--config`, `--cpi-source {hicp,insee}`. |
| `scripts/multi_year/m1_add_cluster_key.py` | Adds `cluster_id = idorighh` column. Can be merged into `m1_harmonise_cpi.py` if preferred; listed separately for testability. |
| `scripts/multi_year/m1_validate.py` | Runs V1–V9 checks on a harmonised pooled file; writes `Results/M1_*` manifests and summary. CLI: `--config`, `--file`. |
| `scripts/multi_year/m1_identity_validation.py` | For a pooled stacked-raw file, runs the Section 13 diagnostics for all year-pairs; writes `Results/M1_identity_validation_summary.md`. |
| `scripts/multi_year/m1_isf_check_2018.py` | Runs the Section 16 ISF check using the FR_2018 EUROMOD output; writes `Results/M1_ISF_tpr_comparability_check_2018.md`. Run only when FR_2018 EUROMOD output is present. |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | Not a script; the φ_t table written after the Section 7 decision. Created manually or by a small helper; treated as a project input, not a generated output. |

### Modified scripts

| Script | Change |
| --- | --- |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | Line 44: change `YEAR = 2016` to `argparse` `--year` argument. No other changes. |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | CLI defaults that are hardcoded to 2016 paths must accept `--year` override. No logic changes. |

### Orchestration

A top-level runner `scripts/multi_year/run_m1_p3a.sh` (or `.ps1`) documents the ordered call sequence:

1. Acquire Eurostat denominators and INSEE benchmark (manual or via helper script).
2. Write `cpi_hicp_fr_harmonisation.csv` (after Section 7 decision).
3. Run EUROMOD for FR_2015, FR_2016, FR_2017 (manual EUROMOD UI steps; output written to Z: drive).
4. Run `enh_RURO_prep_mnl_basic.py` for 2015 and 2017 to produce MNL parquets.
5. Run `enh_prepare_FR_gsur_v2.py --year 2015` and `--year 2017`.
6. Run `m1_stack_years.py --config p3a`.
7. Run `m1_identity_validation.py --config p3a`.
8. Run `m1_harmonise_cpi.py --config p3a`.
9. Run `m1_add_cluster_key.py --config p3a` (or confirm it is embedded in step 8).
10. Run `m1_validate.py --config p3a`.

---

## 19. Required Output Files

The following files must exist and pass validation for Stage M1 to be complete for P3a:

| File | Written by |
| --- | --- |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | Manual (after Section 7 decision) |
| `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet` | `m1_stack_years.py` |
| `Data/processed/fr/pooled/fr_p3a_harmonised.parquet` | `m1_harmonise_cpi.py` |
| `Results/M1_stacked_id_manifest_<UTC>.csv` | `m1_validate.py` |
| `Results/M1_raw_id_preservation_check_<UTC>.csv` | `m1_validate.py` |
| `Results/M1_cluster_key_check_<UTC>.csv` | `m1_validate.py` |
| `Results/M1_identity_validation_summary.md` | `m1_identity_validation.py` |
| `Results/M1_cpi_harmonisation_check_<UTC>.csv` | `m1_validate.py` |

For P3b (contingent on ISF check):

| File | Written by |
| --- | --- |
| `Results/M1_ISF_tpr_comparability_check_2018.md` | `m1_isf_check_2018.py` |
| `Data/processed/fr/pooled/fr_p3b_stacked_raw.parquet` | `m1_stack_years.py` |
| `Data/processed/fr/pooled/fr_p3b_harmonised.parquet` | `m1_harmonise_cpi.py` |

---

## 20. What Not to Change

The following must not be modified during Stage M1:

| Item | Reason |
| --- | --- |
| `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` | Stage M1 does not touch the estimation spec. M0 baseline is unchanged. |
| `scripts/enhanced/enh_RURO_estimate_FR.py` | The estimation engine is not modified in Stage M1. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Same. |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Post-estimation outputs are not modified in Stage M1. |
| `outputs/estimates/fr/spec/ruro_occ/` | Existing M0/M1-clean single-year results must not be overwritten. |
| `outputs/post_estimation/fr/spec/ruro_occ/` | Same. |
| `stijn/` | Safe haven (R notebook authorship). |
| `docs/archive/` | Sealed historical snapshot. |
| `docs/ACKNOWLEDGEMENTS.md` | Personal acknowledgement; not touched. |
| GSUR v1 parquet `FR_gsur_ruro.parquet` | Existing v1 rates are inputs; they are read, not modified. |
| Any Z: drive paths | Out of scope for Stage M1 scripts; Z: contains raw storage, not project repo state. |

---

## 21. What Remains Blocked After Stage M1

Stage M1 completion unlocks pooled-data availability but does not unblock the following:

| Item | Blocking condition |
| --- | --- |
| **Pooled estimation (P3a)** | Requires pooled parquet (unblocked by M1) AND cluster-robust SE wrapper (not yet written) AND estimation spec for pooled model (not yet written). Blocked on both. |
| **Pooled estimation (P3b)** | Additionally blocked on ISF check and v3.1 memo revision. |
| **Welfare computation** | Blocked on welfare scaffolding design decision (see `docs/JMP_welfare_scaffolding_design_memo_v2.md`). Stage M1 makes no welfare progress. |
| **Welfare scaffolding implementation** | Not authorised in Stage M1. |
| **Canonical MNL model promotion** | Not authorised in Stage M1. The M1-clean single-year (2016) result remains the canonical baseline. |
| **GSUR Stage B (age-specific weights)** | Not authorised in Stage M1. Stage B is deferred to a later data-engineering stage. |
| **EUROMOD output runs for FR_2015, FR_2017** | Manual EUROMOD UI steps; not automatable within Stage M1 scripts. Must be completed as a prerequisite. |
| **P4 configuration** | Not a priority; no authorisation given. |
| **Cross-validation estimation** | Requires pooled estimation to be unblocked first; also requires a cross-validation script not yet written. |

---

## 22. Implementation Prompt for Claude Code

Use the following prompt to resume Stage M1 implementation in a future session. Copy verbatim.

---

**Stage M1 implementation session — pooled data engineering for RURO multi-year pipeline**

**Working directory:** `U:\Desktop\Nizam_Hisham\MNL`

**Primary reference:** `docs/JMP_multi_year_stage_M1_implementation_plan_v2.md`

**Task:** Implement the Stage M1 scripts listed in Section 18 of the implementation plan. The target configuration is P3a (2015+2016+2017). Start with `scripts/multi_year/m1_stack_years.py`.

**Preconditions to verify before writing any code:**

1. `Data/external/cpi_hicp_fr_harmonisation.csv` exists (Section 7 decision completed).
2. MNL parquets for 2015 and 2017 are present under `Data/processed/fr/`.
3. `FR_gsur_ruro_v2_stageA.parquet` has been extended to 2015 and 2017.
4. Check Section 2 of the plan to confirm all F-conditions are satisfied.

**Stacking rule** (single base B = 10^11 for both levels; see Section 10):

```python
B = 10**11
stacked_hh_uid     = year_tag * B + idhh      # unique per household-year
stacked_person_uid = year_tag * B + idperson   # unique per person-year row
```

Both IDs are `int64`. B = 10^11 is sufficient: max `idperson` across all years is 9,378,990,002 < 10^11. For year_tag=2: 2 × 10^11 + 9,378,990,002 = 209,378,990,002 < 3 × 10^11. No cross-year collision.

**Raw IDs to preserve:** `idorighh`, `idorigperson`, `idhh`, `idperson`. See Section 11.

**Clustering key:** `cluster_id = idorighh`. See Section 12.

**CPI deflation:** Read φ_t from `Data/external/cpi_hicp_fr_harmonisation.csv`. Deflate variables listed in Section 8. Add `_real` suffix; do not drop nominal columns. See Sections 7–9.

**Do not implement:**
- Pooled estimation or any model-fitting code.
- Welfare scaffolding or welfare computation.
- GSUR Stage B.
- Any modification to the estimation spec YAML.
- Anything for P3b until the ISF check in `Results/M1_ISF_tpr_comparability_check_2018.md` concludes "proceed."

**Validation:** After writing the pooled file, run `m1_validate.py` and confirm all V1–V9 checks pass (Section 17). Write results to `Results/M1_*` manifests.

**Naming convention:** All output files and script names use `ruro_occ` (not `stijn_occ`). See `docs/RURO_NAMING_AND_PACKAGE_SCOPE_v1.md`.

---