# JMP Multi-Year — Stage M1 Dry-Run Execution Readiness

**Document:** Results/JMP_multi_year_stage_M1_execution_readiness_v1.md
**Date:** 2026-05-19
**Execution-readiness context:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md

All dry-run commands executed from repo root `\\crc\users\hisham\Desktop\Nizam_Hisham\MNL` using `.\.venv\Scripts\python.exe`. No PYTHONPATH set. No parquets written.

---

## Dry-run results

### P3a — `--config p3a --dry-run`

```
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml

Inputs:
  [2015]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2016]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2017]  NOT FOUND  (searched ...\Data\processed\fr/)

Planned output: ...\Data\processed\fr\pooled\fr_p3a_stacked_raw.parquet

Status: BLOCKED -- one or more inputs missing

UID scheme (B=100,000,000,000):
  year=2015  tag=1  stacked range = [100,000,000,001 to 199,999,999,999]
  year=2016  tag=2  stacked range = [200,000,000,001 to 299,999,999,999]
  year=2017  tag=3  stacked range = [300,000,000,001 to 399,999,999,999]

Raw IDs to preserve: ['idorighh', 'idorigperson', 'idhh', 'idperson']
No parquet written (dry-run mode).
```

**Exit code: 0** (blocked status reported; dry-run itself succeeds)

**Verdict: BLOCKED — all three year inputs absent from M1 input directory**

---

### P2 — `--config p2 --dry-run`

```
DRY RUN -- config=p2  years=[2015, 2016]
Config YAML: ...\config\multi_year\fr_p2_stage_m1.yaml

Inputs:
  [2015]  NOT FOUND  (searched ...\Data\processed\fr/)
  [2016]  NOT FOUND  (searched ...\Data\processed\fr/)

Planned output: ...\Data\processed\fr\pooled\fr_p2_stacked_raw.parquet

Status: BLOCKED -- one or more inputs missing

UID scheme (B=100,000,000,000):
  year=2015  tag=1  stacked range = [100,000,000,001 to 199,999,999,999]
  year=2016  tag=2  stacked range = [200,000,000,001 to 299,999,999,999]

Raw IDs to preserve: ['idorighh', 'idorigperson', 'idhh', 'idperson']
No parquet written (dry-run mode).
```

**Exit code: 0** (blocked status reported; dry-run itself succeeds)

**Verdict: BLOCKED — both year inputs absent from M1 input directory**

---

### P3b — `--config p3b --dry-run`

```
ERROR  Config 'p3b' is not authorised for execution:
P3b is blocked until Results/M1_ISF_tpr_comparability_check_2018.md
concludes 'proceed'. See §16 of the Stage M1 plan.
```

**Exit code: 1**

**Verdict: CORRECTLY BLOCKED — ISF gate triggers before dry-run**

---

### P4 — `--config p4 --dry-run`

```
ERROR  Config 'p4' is not authorised for execution:
P4 is not a priority configuration. No authorisation in Stage M1.
```

**Exit code: 1**

**Verdict: CORRECTLY BLOCKED — not-a-priority gate triggers**

---

## Gate summary

| Config | Dry-run exit | Inputs found | Execution gate | Status |
| --- | --- | --- | --- | --- |
| p3a | 0 | 0 / 3 | Input parquets absent | **BLOCKED** |
| p2  | 0 | 0 / 2 | Input parquets absent | **BLOCKED** |
| p3b | 1 | — | ISF gate (hard block) | **CORRECTLY BLOCKED** |
| p4  | 1 | — | Not-a-priority gate | **CORRECTLY BLOCKED** |

---

## No pooled parquets written

Confirmed: `Data/processed/fr/pooled/` contains no `.parquet` files after all four dry-runs.

```
Get-ChildItem "Data\processed\fr\pooled\" → (empty)
```

---

## Notes on the "2016 NOT FOUND" result

The 2016 MNL parquet (`fr_2016_RURO_mnl_job_gmm__singles.parquet`) exists at:
`Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet`

The M1 config searches `Data/processed/fr/` (repo-local), not Z:. This is the root cause of the 2016 NOT FOUND result. The 2016 parquet must be copied to `Data/processed/fr/` before m1_stack_years.py can find it. See `Results/JMP_multi_year_single_year_MNL_readiness_v1.md §5 Step C` for the exact copy command.