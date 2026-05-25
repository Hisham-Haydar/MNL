# JMP Multi-Year — EUROMOD Output Readiness

**Document:** Results/P3a/multi_year_stage_M1/JMP_multi_year_EUROMOD_output_readiness_v1.md
**Date:** 2026-05-19
**Execution-readiness context:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Plan reference:** docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_implementation_plan_v2.md §3

All paths inspected at `Z:\hisham\EUROMOD-STORAGE`. Inspection performed 2026-05-19.

---

## Summary verdict

**INCOMPLETE — FR_2015 and FR_2017 EUROMOD outputs absent.**

FR_2016 EUROMOD output is present in the form of `combined_draws_em.parquet` (produced by the existing pipeline run via `enh_RURO_euromod.py`). FR_2015 and FR_2017 outputs have not been produced. All three EU-SILC microdata inputs are present on Z:. EUROMOD J1.0+ is available. FR_2015 and FR_2017 EUROMOD runs must be executed before Stage M1 can proceed.

---

## 1. EUROMOD system readiness

| Item | Status |
| --- | --- |
| EUROMOD J1.0+ release | **PRESENT** at `Z:\hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+\` |
| `EM3Translation/`, `Input/`, `Log/`, `Output/`, `XMLParam/` folders | **PRESENT** (standard EUROMOD release structure) |
| EUROMOD system comparability across FR_2015/2016/2017 | **CONFIRMED** per addendum v2 (F6 = ✓ for 2015, 2016, 2017) |
| FR_2018 ISF/tpr comparability check | NOT YET RUN (P3b contingent) |

**Note:** The `Output/` folder currently contains only DE outputs and three EUROMOD log files from October 2025 runs. No FR outputs are present in the release output folder. FR_2016 outputs exist as a processed parquet on the Z: `Data/processed/fr/2016/` path, produced via the `enh_RURO_euromod.py` post-processing pipeline, not as a raw EUROMOD `.txt` output.

---

## 2. EU-SILC microdata availability

| File | Path | Status |
| --- | --- | --- |
| `FR_2015_a2.txt` | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` | **PRESENT** |
| `FR_2015_a2_2015_03_e2.txt` | `Z:\hisham\EUROMOD-STORAGE\Data\FR\` | **PRESENT** (alternate version) |
| `FR_2016_a3.txt` | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2016_a3.txt` | **PRESENT** |
| `FR_2017_a2.txt` | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` | **PRESENT** |

All three microdata files needed for P3a are present.

---

## 3. EUROMOD output status by year

### FR_2016

| Item | Path | Status |
| --- | --- | --- |
| `combined_draws_em.parquet` (job_gmm spec) | `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em.parquet` | **PRESENT** (2026-02-08) |
| `combined_draws_em__euromodmeta.json` | Same folder | **PRESENT** |
| `combined_draws_em.parquet` (ruro_occ spec) | `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\stijn_occ\scenarios\combined_draws_em.parquet` | **PRESENT** (2026-05-13) |
| Raw EUROMOD output txt for FR_2016 | `Z:\hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\...\Output\` | **ABSENT** (not retained; processed form present) |

**FR_2016 verdict:** EUROMOD output is present in processed parquet form (via the job_gmm scenario run). This is the form consumed by `enh_RURO_prep_mnl_basic.py`. The raw `.txt` output was not retained, but the downstream processed files are present and were used to produce the canonical 2016 MNL parquets.

### FR_2015

| Item | Status |
| --- | --- |
| `combined_draws_em.parquet` for any FR_2015 scenario | **ABSENT** — no FR_2015 folder in `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\` |
| FR_2015 EUROMOD run (any form) | **NOT EXECUTED** |

**FR_2015 verdict:** No EUROMOD output exists for FR_2015. EUROMOD J1.0+ has FR_2015 installed; the microdata `FR_2015_a2.txt` is present. A EUROMOD run is required.

### FR_2017

| Item | Status |
| --- | --- |
| `combined_draws_em.parquet` for any FR_2017 scenario | **ABSENT** — no FR_2017 folder in `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\` |
| FR_2017 EUROMOD run (any form) | **NOT EXECUTED** |

**FR_2017 verdict:** No EUROMOD output exists for FR_2017. EUROMOD J1.0+ has FR_2017 installed; the microdata `FR_2017_a2.txt` is present. A EUROMOD run is required.

---

## 4. EUROMOD comparability check (F6)

Per the implementation plan v2 §2, F6 (EUROMOD comparability across years) is confirmed:

| Year | F6 status | Notes |
| --- | --- | --- |
| 2015 | ✓ | Same EUROMOD J1.0+ system; FR_2015 installed |
| 2016 | ✓ | Confirmed working — canonical MNL produced |
| 2017 | ✓ | Same system; FR_2017 installed |
| 2018 | ✓ *(ISF flag)* | P3b contingent; ISF wealth tax creates `tpr` asymmetry |

The ISF (`tpr`) asymmetry between 2015 and 2018 vs. 2016 and 2017 is documented in §6 of the plan. For P3a (2015+2016+2017), 2015 has `tpr` present. Its inclusion in the pooled P3a dataset must be documented and handled explicitly in the harmonisation step.

---

## 5. What must be run before Stage M1 can execute

### Step 1 — FR_2015 EUROMOD run

Execute EUROMOD for FR_2015 using the same scenario configuration as the FR_2016 job_gmm run. Produce:

```
Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\<scenario_name>\scenarios\combined_draws_em.parquet
Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\<scenario_name>\scenarios\combined_draws_em__euromodmeta.json
```

### Step 2 — FR_2017 EUROMOD run

Execute EUROMOD for FR_2017 using the same scenario configuration. Produce:

```
Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\<scenario_name>\scenarios\combined_draws_em.parquet
Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\<scenario_name>\scenarios\combined_draws_em__euromodmeta.json
```

**Note on scenario configuration:** The scenario name and parameter settings must match the FR_2016 job_gmm run to ensure cross-year comparability. Inspect `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\job_model_gmm\scenarios\combined_draws_em__euromodmeta.json` for the exact scenario parameters used in 2016 and replicate for 2015 and 2017.

---

## 6. Cross-year variable comparability checks required after EUROMOD runs

Before running `enh_RURO_prep_mnl_basic.py` for 2015 or 2017, confirm:

- `ils_dispy`, `ils_earns`, `yem`, `yse`, `ypen`, `ypt`, `ils_ben` present in all three years' EUROMOD outputs.
- `idhh`, `idperson`, `idorighh`, `idorigperson` present and non-null.
- `dgn`, `dag`, `deh`, `drgn1`, `dms` present.
- `tpr`: present in FR_2015 (ISF applies); absent from FR_2016 and FR_2017. This is expected and documented; do not treat FR_2016/2017 absence as an error.
- `dwt` (survey weight) present in all years.

These checks are part of the prep script's existing validation logic and will surface as errors if columns are missing.