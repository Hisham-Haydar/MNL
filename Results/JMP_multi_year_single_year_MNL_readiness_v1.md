# JMP Multi-Year — Single-Year MNL Readiness

**Document:** Results/JMP_multi_year_single_year_MNL_readiness_v1.md
**Date:** 2026-05-19
**Execution-readiness context:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Plan reference:** docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §3

---

## Summary verdict

**NOT READY — all three years' MNL parquets absent from Stage M1 input directory.**

`m1_stack_years.py` searches `Data/processed/fr/` (repo-local path) for per-year MNL parquets. That directory currently contains only a `pooled/` subdirectory with no parquet files. The canonical 2016 MNL parquets exist on Z: drive but are not placed in the M1 input directory. MNL parquets for 2015 and 2017 do not exist anywhere.

---

## 1. What Stage M1 expects

Per `config/multi_year/fr_p3a_stage_m1.yaml`:

```yaml
input_parquet_dir: Data/processed/fr
input_parquet_patterns:
  - "*{year}*RURO*mnl*job*gmm*.parquet"
  - "*{year}*RURO*mnl*job*.parquet"
  - "*{year}*RURO*mnl*.parquet"
  - "*{year}*mnl*.parquet"
```

`m1_stack_years.py` resolves `input_parquet_dir` to:
`\\crc\users\hisham\Desktop\Nizam_Hisham\MNL\Data\processed\fr\`

The glob search for pattern `*2016*RURO*mnl*job*gmm*.parquet` in that directory returns nothing because the directory is empty (contains only `pooled/`).

**Important:** This is not a script bug. The YAML config path is intentionally local. Parquets must be placed in `Data/processed/fr/` or the YAML `input_parquet_dir` must be updated to point to Z:.

---

## 2. Year-by-year MNL parquet status

### 2016 — canonical parquet exists on Z:, absent locally

| Parquet | Path on Z: | Columns present | Status |
| --- | --- | --- | --- |
| `fr_2016_RURO_mnl_job_gmm__singles.parquet` | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\` | `idhh`, `idperson`, `idorighh`, `idorigperson`, `dag`, `deh`, `drgn1`, `ils_dispy`, `ils_earns`, `gsur`, `year`, `tpr`, `dwt` — all present (974 cols total) | **EXISTS ON Z: — NOT IN M1 INPUT DIR** |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | Same Z: folder | `idhh`, `idperson`, `idorighh`, `idorigperson`, `dag`, `deh`, `drgn1`, `ils_dispy`, `ils_earns`, `gsur`, `year`, `dwt` present; `tpr` absent (correct — ISF not in 2016); `gsur_v2` absent (column name is `gsur` in GSURv2 file; methodology is v2) | **EXISTS ON Z: — NOT IN M1 INPUT DIR** |

**Recommended parquet for 2016:** `fr_2016_RURO_mnl_job_gmm__singles.parquet` (matches the `*job*gmm*` pattern, highest priority). The GSURv2 version would need to be verified as consistent.

**Shape:** 335,200 rows × 974 columns (singles, job_gmm).

**Gap:** The 2016 parquet must be copied or symlinked from Z: to `Data/processed/fr/`, or the YAML `input_parquet_dir` must be changed to `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr` and the pattern adjusted. The copy approach is preferred to avoid Z: path dependency in the repo config.

### 2015 — does not exist anywhere

| Parquet | Status |
| --- | --- |
| Any `fr_2015*RURO*mnl*.parquet` on Z: | **ABSENT** — no `2015/` folder under `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\` |
| Any `fr_2015*mnl*.parquet` locally | **ABSENT** |

**Gap:** EUROMOD must be run for FR_2015 → `enh_RURO_euromod.py` → `enh_RURO_prep_mnl_basic.py`.

### 2017 — does not exist anywhere

| Parquet | Status |
| --- | --- |
| Any `fr_2017*RURO*mnl*.parquet` on Z: | **ABSENT** — no `2017/` folder under `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\` |
| Any `fr_2017*mnl*.parquet` locally | **ABSENT** |

**Gap:** EUROMOD must be run for FR_2017 → `enh_RURO_euromod.py` → `enh_RURO_prep_mnl_basic.py`.

---

## 3. Dry-run output confirming the gap

```
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml

Inputs:
  [2015]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2016]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2017]  NOT FOUND  (searched ...\Data\processed\fr/)

Status: BLOCKED -- one or more inputs missing
```

All three years show NOT FOUND because `Data/processed/fr/` has no parquet files.

---

## 4. Metadata sidecar readiness

Each year's MNL parquet must have an accompanying `*__mnlmeta.json` sidecar for Stage M1 validation and manifest building.

| Year | Sidecar | Status |
| --- | --- | --- |
| 2016 | `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` present on Z: | **EXISTS ON Z: — NOT IN M1 INPUT DIR** |
| 2015 | Not produced yet | **ABSENT** |
| 2017 | Not produced yet | **ABSENT** |

The sidecar is written by `enh_RURO_prep_mnl_basic.py` alongside the parquet. It contains `year`, `timestamp`, `inputs`, `prior_parameters`, `sample_sizes`, `normalization`, `columns`. M1 validation scripts use it; its absence is not a hard blocker for `m1_stack_years.py` but it is required for `m1_validate.py` completeness checks.

---

## 5. Future commands for 2015 and 2017 MNL parquets

These commands must NOT be run now. They require EUROMOD outputs (Task C gap) to be produced first. When EUROMOD outputs for FR_2015 and FR_2017 are available, run the following (from repo root):

### Step A — RURO draws for 2015

Replicate the draws generation that was used for 2016. The exact command depends on the scenario configuration in `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model_gmm\` — inspect the 2016 euromodmeta sidecar for draw parameters. Produce:

```
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws__drawsmeta.json
```

(Analogous output paths for 2017.)

### Step B — MNL prep for 2015

```powershell
.\.venv\Scripts\python.exe scripts\enhanced\enh_RURO_prep_mnl_basic.py `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\<scenario_name>\scenarios\combined_draws_em.parquet" `
    --out-base "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm" `
    --drawsmeta "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file Data\external\FR_gsur_ruro.parquet `
    --year 2015
```

(Analogous command for 2017 — replace all `2015` references with `2017`.)

**Note on `--gsur-file`:** Use `FR_gsur_ruro.parquet` (v1, present, covers 2015/2017). If GSURv2 rates for 2015/2017 become available before this step, use `FR_gsur_ruro_v2_stageA.parquet` instead.

### Step C — Copy parquets to M1 input directory

Once parquets are produced, copy (or symlink) to the M1 input directory:

```powershell
# 2015
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"

# 2016 (already exists — copy from Z:)
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"

# 2017 (analogous to 2015 once produced)
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"
```

**Alternative:** Update `config/multi_year/fr_p3a_stage_m1.yaml` field `input_parquet_dir` from `Data/processed/fr` to the Z: path. This avoids file copying but introduces Z: dependency in the repo config, which may be undesirable for portability and reproducibility.

---

## 6. Couples parquets

`m1_stack_years.py` uses a `_find_parquet` function that prefers files containing `combined` in their name or files that are neither `singles` nor `couples`. The singles parquet is the fallback if no combined/neutral name is found. The M1 stack operates on the flat per-observation file (job offers × draws), not on separate singles/couples splits. Confirm which form the 2015/2017 prep output takes before running the copy step.

---

## 7. GSURv2 year-dependency status

The `FR_gsur_ruro_v2_stageA.parquet` covers only 2016. The 2016 MNL parquets (`fr_2016_RURO_mnl_GSURv2__singles.parquet`) were built using the v2 GSUR rates, but the column is named `gsur` (not `gsur_v2`) in that file. The YAML config's monetary variable list and `variables_excluded_from_deflation` section both reference `gsur_v2` as a column to preserve — this must be confirmed to be present in the actual parquets used as M1 input, or the YAML must be updated to match the actual column name.

**Blocking status:** Not a hard blocker for the stack step (m1_stack_years.py does not filter columns; it stacks the full parquet). It is a potential issue for downstream estimation if the YAML exclusion list is used to select columns.