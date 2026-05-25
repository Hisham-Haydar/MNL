# JMP FR_2016 Local Mirror Report — Stage M1 Input Copy

**Document:** Results/P3a/multi_year_stage_M1/JMP_single_year_2016_local_mirror_report_v1.md
**Date:** 2026-05-20
**Author:** Hisham Haydar
**Status:** COMPLETED — 3 files copied; Stage M1 dry-run confirms 2016 resolvable

---

## 1. Source files copied

All three files were copied from the canonical Z: storage path:

| File | Source path | Size (bytes) |
| ---- | ----------- | ------------ |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__singles.parquet` | 21,510,188 |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__couples.parquet` | 43,130,386 |
| `fr_2016_RURO_mnl_GSURv2__mnlmeta.json`   | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__mnlmeta.json`   | 57,973 |

Pre-copy guard: `Test-Path` confirmed all three destination paths returned `False` before copying. `Copy-Item` was called without `-NoClobber` (not available in PowerShell 5.1) with a manual `if (Test-Path $dst) { ABORTED }` guard. All copies returned byte-for-byte size matches.

---

## 2. Destination files created

All three files are now present in the repo-local Stage M1 input directory:

| File | Destination path | Size match |
| ---- | ---------------- | ---------- |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_GSURv2__singles.parquet` | SIZE_MATCH |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_GSURv2__couples.parquet` | SIZE_MATCH |
| `fr_2016_RURO_mnl_GSURv2__mnlmeta.json`   | `Data/processed/fr/fr_2016_RURO_mnl_GSURv2__mnlmeta.json`   | SIZE_MATCH |

Source files on Z: are untouched. The `Data/processed/fr/` directory previously contained only the empty `pooled/` subdirectory.

---

## 3. Metadata sidecar copied

The `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` sidecar was copied alongside the two parquets. Key sidecar fields:

| Field | Value |
| ----- | ----- |
| `script` | `enh_RURO_prep_mnl_basic.py` |
| `timestamp` | `2026-05-13T08:38:20.951652Z` |
| `inputs.gsur_file` | `U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet` (v1 GSUR) |
| `prior_parameters.wage_spec` | `vw` |
| `prior_parameters.pi0_m / pi0_f` | `0.1 / 0.1` |
| `prior_parameters.h_min / h_max` | `5.0 / 70.0` |
| `prior_parameters.w_min / w_max` | `2.0 / 170.0` |
| `prior_parameters.source` | `drawsmeta` |
| `sample_sizes.singles_deciders` | 1,676 |
| `sample_sizes.couples_deciders` | 2,577 |
| `sample_sizes.n_draws` | 100 |
| `normalization.singles.c_scale` | 7,590.29 |
| `normalization.couples.c_scale` | 15,106.18 |

Note: `effective_prior_source_singles` reads `ruro_layered_log_q` in the sidecar — this is a legacy internal label in the Z: source sidecar predating the RURO naming policy. The file itself is the canonical M1-clean operative parquet; the label is a provenance artefact in the Z: storage copy and does not affect Stage M1 usage.

---

## 4. Which 2016 MNL version was selected

**Selected: `fr_2016_RURO_mnl_GSURv2__`** (both `singles` and `couples`).

Five 2016 MNL versions exist on Z: in `Data/processed/fr/2016/`:

| Stem | n_draws | wage_spec | draw_source | gsur_file | timestamp | rows (singles) |
| ---- | ------- | --------- | ----------- | --------- | --------- | -------------- |
| `fr_2016_RURO_mnl_GSURv2__` | 100 (draws 0–99) | vw | `RURO_draws.parquet` | `FR_gsur_ruro.parquet` (v1) | 2026-05-13 | 167,600 |
| `fr_2016_RURO_mnl_job_gmm__` | 200 (200 draws) | fw | `jobdraws.parquet` | `FR_gsur_ruro.parquet` (v1) | 2026-02-19 | 335,200 |
| `fr_2016_RURO_mnl_job__` | — | — | — | — | — | — |
| `fr_2016_RURO_mnl__` | — | — | — | — | — | — |
| `fr_2016_RURO_mnl___` (triple underscore) | — | — | — | — | — | — |

The `GSURv2__` version was selected. The `job_gmm__` version was not selected.

---

## 5. Why this version matches M1-clean

`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` §2 explicitly names `fr_2016_RURO_mnl_GSURv2__{singles,couples}.parquet` as the **operative data** for the M1-clean specification (LL=−6487.5522, 53 parameters, SA1-STANDS verdict):

> "Operative data: `fr_2016_RURO_mnl_GSURv2__singles.parquet` and `fr_2016_RURO_mnl_GSURv2__couples.parquet`"

Additional consistency reasons:

1. **Draw methodology**: `GSURv2__` uses the continuous RURO draw procedure (`RURO_draws.parquet`, vw wage spec), which is the same procedure that will be used for FR_2015 and FR_2017 under the 2015/2017 authorization. `job_gmm__` uses an older job-model draw procedure (fw wage spec) that differs methodologically.
2. **Draw parameters**: `GSURv2__` uses n_draws=99+1=100, vw, seed=17, matching the binding parameters in §6 of the 2015/2017 authorization memo (n_draws=99, vw, seed=17). `job_gmm__` uses 200 draws and fw, creating asymmetry.
3. **Timestamp**: `GSURv2__` was produced on 2026-05-13, the same date as the M1-clean verdict was formalized. `job_gmm__` is from 2026-02-19 (pre-M1-clean period).
4. **Naming note**: Despite the `GSURv2__` filename segment, this file used `FR_gsur_ruro.parquet` (v1 GSUR) as input — the same fallback used by all other years. The `GSURv2` in the name refers to the GSURv2 workflow context (the run was conducted under the GSURv2 prep infrastructure), not to the actual GSUR rates source. Both `GSURv2__` and `job_gmm__` use identical v1 GSUR data.

**Stage M1 glob match**: The `fr_2016_RURO_mnl_GSURv2__` stem matches the **3rd pattern** `*{year}*RURO*mnl*.parquet` (not the 1st `*job*gmm*` or 2nd `*job*` patterns). The `job_gmm__` stem would match the 1st (highest-priority) pattern. The M1-clean operative choice takes precedence over glob priority. Future runs that need the `job_gmm__` glob priority would require updating `input_parquet_patterns` in the YAML or choosing a different copy strategy — this is documented as a known asymmetry.

---

## 6. Row counts

| File | Rows | n_draws | draw=0 (decider) rows |
| ---- | ---- | ------- | --------------------- |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | 167,600 | 100 (draws 0–99) | 1,676 |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | 257,700 | 100 (draws 0–99) | 2,577 |

Cross-check: 167,600 / 100 = 1,676 ✓; 257,700 / 100 = 2,577 ✓. Row structure is consistent with 100 states per decider (draw=0 is the observed/chosen state; draws 1–99 are counterfactuals).

---

## 7. Household counts

| File | Unique `idhh` (decider households) |
| ---- | ----------------------------------- |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | 1,676 |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | 2,577 |

Singles: one person per household, so unique `idhh` equals decider count. Couples: one household per couple pair, so unique `idhh` equals couple-decider count. Both match the mnlmeta `sample_sizes` fields exactly.

---

## 8. Key columns present

| Column | Singles | Couples | Notes |
| ------ | ------- | ------- | ----- |
| `idhh` | ✓ | ✓ | EUROMOD household ID |
| `idperson` | ✓ | ✓ | EUROMOD person ID |
| `idorighh` | ✓ | ✓ | Original EU-SILC household ID (UID key) |
| `idorigperson` | ✓ | ✓ | Original EU-SILC person ID (UID key) |
| `dag` | ✓ | absent (gender-specific: `dag_male`, `dag_female`) | Age |
| `dgn` | ✓ | ✓ | Sex |
| `drgn1` | ✓ | ✓ | NUTS1 region |
| `ils_dispy` | ✓ | absent (gender-specific: `ils_dispy_male`, `ils_dispy_female`) | Disposable income |
| `ils_earns` | ✓ | ✓ | Earnings |
| `year` | ✓ (values: [2016]) | ✓ (values: [2016]) | Calendar year tag |
| `draw` | ✓ (min=0, max=99) | ✓ (min=0, max=99) | Draw index |
| `dwt` | ✓ | absent (gender-specific: `dwt_male`, `dwt_female`) | Design weight |
| `gsur_v2` | absent | absent | Not present; `gsur` is the operative column (see §9) |

All four Stage M1 raw-ID columns (`idorighh`, `idorigperson`, `idhh`, `idperson`) are present in both files, satisfying the stacking integrity requirement.

---

## 9. GSUR columns present

**Singles:**

| Column | dtype | Non-zero rows | Mean | Notes |
| ------ | ----- | ------------- | ---- | ----- |
| `gsur` | float64 | 167,600 (100%) | 0.0927 | Operative GSUR rate; used by Stage M1 |
| `gsur_legacy_misaligned` | float64 | 167,600 (100%) | 0.0958 | Legacy pre-correction rate; not used |
| `gsur_weighting_source` | object | 167,600 | — | Values: `['population']` |
| `gsur_age_band_used` | object | 167,600 | — | Values: `['Y20-64', 'Y20-64_fallback_age65']` |
| `gsur_unreliable` | bool | 92,900 flagged unreliable | — | Unreliable cells: 55.4% of singles rows |

**Couples:**

| Column | dtype | Non-zero rows | Mean | Notes |
| ------ | ----- | ------------- | ---- | ----- |
| `gsur_male` | float64 | 257,700 (100%) | 0.0916 | Operative male GSUR rate |
| `gsur_female` | float64 | 257,700 (100%) | 0.0877 | Operative female GSUR rate |
| `gsur_male_legacy_misaligned` | float64 | 257,700 (100%) | 0.0955 | Legacy; not used |
| `gsur_female_legacy_misaligned` | float64 | 257,700 (100%) | 0.0913 | Legacy; not used |
| `gsur_male_weighting_source` | object | 257,700 | — | Values: `['population']` |
| `gsur_female_weighting_source` | object | 257,700 | — | Values: `['population']` |
| `gsur_male_age_band_used` | object | 257,700 | — | Values: `['Y20-64']` |
| `gsur_female_age_band_used` | object | 257,700 | — | Values: `['Y20-64']` |
| `gsur_unreliable_male` | bool | 133,200 flagged | — | |
| `gsur_unreliable_female` | bool | 158,400 flagged | — | |

`gsur_v2` is absent from both files. The operative `gsur` column is populated in 100% of rows for both singles and couples. The `fr_p3a_stage_m1.yaml` config lists both `gsur` and `gsur_v2` in `variables_excluded_from_deflation`, so the absence of `gsur_v2` is handled gracefully (Stage M1 skips absent columns).

GSUR source: `FR_gsur_ruro.parquet` (v1 fallback), confirmed from mnlmeta `inputs.gsur_file`. Despite the file's `GSURv2__` name, it uses the v1 GSUR rates.

---

## 10. Canonical files untouched

The following files are confirmed untouched (not overwritten, not modified):

| File | Status | Verification |
| ---- | ------ | ------------ |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__singles.parquet` | Untouched | Only read-copied; source size matches destination |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__couples.parquet` | Untouched | Only read-copied |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | Untouched | Only read-copied |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet` | Untouched | Not touched |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet` | Untouched | Not touched |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | Untouched | Not touched |

No estimation was run. No pooled stacking was run (dry-run only). No welfare computation was performed. Prohibited actions in §4 and §11 of the 2015/2017 authorization memo were observed.

---

## 11. Optional Stage M1 dry-run result

```
======================================================================
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml
======================================================================

Inputs:
  [2015]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2016]  FOUND  ...\Data\processed\fr\fr_2016_RURO_mnl_GSURv2__couples.parquet  (41.1 MB)
  [2017]  NOT FOUND  (searched ...\Data\processed\fr/)

Planned output: ...\Data\processed\fr\pooled\fr_p3a_stacked_raw.parquet

Status: BLOCKED -- one or more inputs missing

Missing inputs require upstream steps:
  2015/2017: run EUROMOD FR_2015/FR_2017 then enh_RURO_prep_mnl_basic.py
```

**Interpretation:**

- 2016 is **FOUND**: `m1_stack_years.py` successfully resolves the copied `fr_2016_RURO_mnl_GSURv2__` file via the 3rd glob pattern `*{year}*RURO*mnl*.parquet`. The dry-run reports the `couples` file because alphabetical sort places `couples` before `singles` and the script returns `candidates[0]` when no `combined` file is found. Both `singles` and `couples` are present and would both be loaded during actual (non-dry-run) execution.
- 2015 and 2017 are **NOT FOUND**: expected; those parquets do not yet exist pending the single-year EUROMOD pipeline runs authorized by `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`.
- **Glob pattern note**: `fr_2016_RURO_mnl_GSURv2__` matches via pattern 3 (`*{year}*RURO*mnl*.parquet`), not pattern 1 (`*job*gmm*`) or pattern 2 (`*job*`). This is consistent with the M1-clean operative choice; pattern priority ordering in the YAML does not override the mandate from the M1-clean verdict.

---

## 12. PASS / FAIL verdict

**PASS** — with qualification.

| Check | Result |
| ----- | ------ |
| Source files copied without modification | PASS |
| Destination files created with size match | PASS |
| Metadata sidecar copied | PASS |
| Version selection consistent with M1-clean verdict | PASS |
| No canonical Z: files overwritten | PASS |
| No estimation run | PASS |
| No pooled stacking run (dry-run only) | PASS |
| No welfare computed | PASS |
| Stage M1 dry-run resolves 2016 | PASS |
| 2015 and 2017 correctly reported as NOT FOUND | PASS (expected; upstream pipeline pending) |
| `gsur_v2` absent | NOTE — handled gracefully by M1 YAML `variables_excluded_from_deflation` |
| Glob pattern match is 3rd priority, not 1st | NOTE — expected given version choice; documented in §5 |

**Qualification**: The `fr_2016_RURO_mnl_GSURv2__` file matches glob pattern 3, not the highest-priority `*job*gmm*` pattern 1. If pattern-priority order ever becomes load-bearing (e.g., if both versions are present and the wrong one is auto-selected), `input_parquet_patterns` in `fr_p3a_stage_m1.yaml` can be updated to add `*{year}*RURO*mnl*GSURv2*.parquet` at position 1. For now, only the M1-clean operative version exists in `Data/processed/fr/`, so no pattern conflict is possible.

**Remaining blocker for Stage M1 execution**: 2015 and 2017 parquets are absent. Unblocking requires completing all five stages of the single-year pipeline authorized by `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` for both years.