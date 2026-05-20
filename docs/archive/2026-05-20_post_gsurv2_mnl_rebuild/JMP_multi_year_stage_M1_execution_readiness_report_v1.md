# JMP Multi-Year Stage M1 — Execution Readiness Report

**Document:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Date:** 2026-05-19
**Prepared by:** Stage M1 execution-readiness audit session (2026-05-19)
**Task documents:**
- CPI decision: `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`
- External assets: `Results/JMP_multi_year_external_assets_inventory_v1.md`
- EUROMOD readiness: `Results/JMP_multi_year_EUROMOD_output_readiness_v1.md`
- MNL readiness: `Results/JMP_multi_year_single_year_MNL_readiness_v1.md`
- Dry-run results: `Results/JMP_multi_year_stage_M1_execution_readiness_v1.md`

---

## 1. Readiness verdict

**Stage M1 execution is NOT authorized.**

Three required P3a inputs are absent. Until they are produced, `m1_stack_years.py --config p3a` will remain blocked. The CPI source was resolved in this session (Option B adopted, CSV written). The remaining gaps are: (a) EUROMOD outputs for FR_2015 and FR_2017 not produced, (b) MNL parquets for 2015 and 2017 not produced, (c) 2016 MNL parquet not placed in the M1 input directory. P3b and P4 are blocked by independent gates and are not execution candidates.

---

## 2. What was inspected

| Item | Inspection method |
| --- | --- |
| `Data/external/cpi_hicp_fr_harmonisation_TEMPLATE.csv` | Read; all φ_t = 0.0 (PLACEHOLDER) |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | Checked for existence: **absent before this session** |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\` | Directory listing: `2016/` folder only |
| `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\` | Directory listing: `2016/`, `scenarios_2016/`, `scenarios_2016_reduced/` only |
| `Z:\hisham\EUROMOD-STORAGE\Data\FR\` | Directory listing: FR_2015_a2.txt, FR_2016_a3.txt, FR_2017_a2.txt present |
| `Z:\hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\...\Output\` | DE outputs and log files only; no FR outputs |
| `Data/external/FR_gsur_ruro.parquet` | Column check and year coverage: 2007–2024, all required years present |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | Year coverage: 2016 only |
| `Data/processed/fr/` (local) | Contents: `pooled/` subdirectory only; no parquets |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet` | Column check: all required ID and monetary columns present; 335,200 rows × 974 cols |
| `config/multi_year/fr_p3a_stage_m1.yaml` | Full read: input_parquet_dir resolves to repo-local path |
| `docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §7` | HICP φ_t values read for Option B |
| Dry-run: `m1_stack_years.py --config p3a/p2/p3b/p4 --dry-run` | All four configs executed; results documented |

---

## 3. CPI/HICP source decision

**Status: RESOLVED (Option B adopted, 2026-05-19).**

The CPI template (`cpi_hicp_fr_harmonisation_TEMPLATE.csv`) had all φ_t = 0.0 (PLACEHOLDER). No `cpi_hicp_fr_harmonisation.csv` existed. The INSEE domestic CPI (Option A) was not retrieved in this session.

**Action taken:** Option B adopted — EUROMOD HICP values from `HICPCONFIG.xml` (Eurostat/AMECO, base 2015=100, normalised to 2016 = 1.0000).

φ_t values written to `Data/external/cpi_hicp_fr_harmonisation.csv`:

| Year | HICP index (base 2015=100) | φ_t |
| --- | --- | --- |
| 2015 | 100.00 | 1.0031 |
| 2016 | 100.31 | 1.0000 |
| 2017 | 101.47 | 0.9886 |
| 2018 | 103.60 | 0.9682 |

Decision rationale and disclosure language: `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`.

This decision unblocks `m1_harmonise_cpi.py` from a CPI-file perspective. `m1_harmonise_cpi.py` remains blocked pending MNL parquet availability.

---

## 4. External assets inventory

**Status: INCOMPLETE — three acquisition gaps remain.**

| Asset | Status |
| --- | --- |
| CPI/HICP deflator CSV | **PRESENT** (created 2026-05-19) |
| EU-SILC microdata FR_2015, FR_2016, FR_2017 | **PRESENT** on Z: |
| Eurostat `lfst_r_lfsd2pop` — 2015, 2017 FR rows | **ABSENT** (2016 only present) |
| Eurostat `lfst_r_lfp2acedu` — 2015, 2017 FR rows | **ABSENT** (2016 only present) |
| INSEE BDM 001688526 — 2015, 2017 | **UNCERTAIN** (inspect existing `insee_001688526_2016.csv` for multi-year rows) |
| NUTS crosswalk | **PRESENT** |
| `FR_gsur_ruro.parquet` (v1, all years) | **PRESENT** (2015, 2016, 2017 rows verified) |
| `FR_gsur_ruro_v2_stageA.parquet` — 2015, 2017 | **ABSENT** (2016 only) |

Full inventory: `Results/JMP_multi_year_external_assets_inventory_v1.md`.

The Eurostat gaps may be resolvable without a new API call — the existing 2016 full-download CSVs (`lfst_r_lfsd2pop_2016_full.csv`, `lfst_r_lfp2acedu_2016_full.csv`) may contain 2015 and 2017 year columns. This must be checked before initiating new downloads.

---

## 5. EUROMOD output readiness

**Status: INCOMPLETE — FR_2015 and FR_2017 not run.**

| Year | EUROMOD output | Status |
| --- | --- | --- |
| FR_2015 | `interim/ruro/fr/2015/.../combined_draws_em.parquet` | **ABSENT — EUROMOD run not executed** |
| FR_2016 | `interim/ruro/fr/2016/job_model_gmm/scenarios/combined_draws_em.parquet` | **PRESENT** (2026-02-08) |
| FR_2017 | `interim/ruro/fr/2017/.../combined_draws_em.parquet` | **ABSENT — EUROMOD run not executed** |

EU-SILC microdata is present for all three years. EUROMOD J1.0+ is installed with FR_2015, FR_2016, FR_2017. EUROMOD system comparability (F6) is confirmed for 2015–2017. No mechanical barrier prevents running FR_2015 and FR_2017; the runs have simply not been executed.

Full EUROMOD readiness detail: `Results/JMP_multi_year_EUROMOD_output_readiness_v1.md`.

---

## 6. Single-year MNL readiness

**Status: NOT READY — all three years absent from M1 input directory.**

| Year | MNL parquet | Location | Status |
| --- | --- | --- | --- |
| 2015 | `fr_2015_RURO_mnl_job_gmm__singles.parquet` | Nowhere | **ABSENT** |
| 2016 | `fr_2016_RURO_mnl_job_gmm__singles.parquet` | Z: drive only | **EXISTS ON Z: — NOT IN M1 INPUT DIR** |
| 2017 | `fr_2017_RURO_mnl_job_gmm__singles.parquet` | Nowhere | **ABSENT** |

The M1 config (`fr_p3a_stage_m1.yaml`) sets `input_parquet_dir: Data/processed/fr`, which resolves to the repo-local path. That directory contains only `pooled/`. The 2016 parquet exists on Z: and must be copied to `Data/processed/fr/`. The 2015 and 2017 parquets must be produced first (upstream dependency: EUROMOD runs + prep script).

The 2016 singles parquet column profile was verified: all required M1 columns present (`idhh`, `idperson`, `idorighh`, `idorigperson`, `dag`, `deh`, `drgn1`, `ils_dispy`, `ils_earns`, `gsur`, `year`, `tpr`, `dwt`). Shape: 335,200 rows × 974 columns.

Full MNL readiness detail: `Results/JMP_multi_year_single_year_MNL_readiness_v1.md`.

---

## 7. Metadata sidecar readiness

| Year | Sidecar file | Status |
| --- | --- | --- |
| 2016 | `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | **EXISTS ON Z: — NOT IN M1 INPUT DIR** |
| 2015 | Not yet produced | **ABSENT** |
| 2017 | Not yet produced | **ABSENT** |

The sidecar is written by `enh_RURO_prep_mnl_basic.py` alongside the parquet. It is not consumed by `m1_stack_years.py` directly but is required by `m1_validate.py` for completeness checks. The 2016 sidecar should be copied to `Data/processed/fr/` alongside the 2016 parquet.

---

## 8. GSURv2 year-dependency status

| Year | `FR_gsur_ruro_v2_stageA.parquet` coverage | `FR_gsur_ruro.parquet` (v1) coverage |
| --- | --- | --- |
| 2015 | **ABSENT** | Present |
| 2016 | **PRESENT** (54 rows) | Present |
| 2017 | **ABSENT** | Present |

`FR_gsur_ruro_v2_stageA.parquet` covers 2016 only. GSURv2 rates for 2015 and 2017 cannot be computed until Eurostat denominators for those years are available.

**Resolution path:** Use `FR_gsur_ruro.parquet` (v1) for 2015 and 2017 in the initial prep run. The v1 file covers all needed years. GSURv2 extension for 2015/2017 is a post-acquisition step and is not blocking for Stage M1 execution if v1 rates are accepted.

**Note on column naming:** The 2016 GSURv2 parquet (`fr_2016_RURO_mnl_GSURv2__singles.parquet`) uses column name `gsur` (not `gsur_v2`) even though the methodology is v2. The YAML config's `variables_excluded_from_deflation` list includes `gsur_v2` — this is a column name that may not exist in any of the per-year parquets. `m1_stack_years.py` does not filter columns (it stacks the full parquet), so this mismatch does not block the stack step. It should be reviewed before running `m1_harmonise_cpi.py`.

---

## 9. P3a readiness

**P3a (2015+2016+2017): NOT EXECUTION-READY.**

Blocking gaps:

1. EUROMOD output for FR_2015: absent.
2. EUROMOD output for FR_2017: absent.
3. MNL parquet for 2015 (`fr_2015_RURO_mnl_job_gmm__singles.parquet`): absent.
4. MNL parquet for 2016: present on Z: but not in M1 input directory.
5. MNL parquet for 2017 (`fr_2017_RURO_mnl_job_gmm__singles.parquet`): absent.

Non-blocking items resolved:

- CPI/HICP deflator CSV: written (Option B, 2026-05-19).
- Stage M1 scripts: all five reusable scripts work without PYTHONPATH (verified in Stage M1 v3 validation, 2026-05-19).
- `--config p3a` resolves correctly to `fr_p3a_stage_m1.yaml`.
- Dry-run exits 0 and reports BLOCKED (correct behaviour).

---

## 10. P2 readiness

**P2 (2015+2016): NOT EXECUTION-READY.**

P2 is a sub-configuration of P3a. Its two blocking gaps (2015 and 2016 parquets not in M1 input directory) are a strict subset of P3a's gaps. Once both 2015 and 2016 parquets are available in `Data/processed/fr/`, P2 becomes executable independently of the 2017 work.

`--config p2` dry-run: exit 0, BLOCKED, correct YAML resolved, planned output `fr_p2_stacked_raw.parquet` confirmed.

---

## 11. P3b blocked status

**P3b (2015+2016+2018): HARD-BLOCKED. Do not activate.**

The `m1_stack_years.py --config p3b --dry-run` command exits 1 with:

```
ERROR  Config 'p3b' is not authorised for execution:
P3b is blocked until Results/M1_ISF_tpr_comparability_check_2018.md
concludes 'proceed'. See §16 of the Stage M1 plan.
```

The `blocked_configs` gate in `fr_p3b_stage_m1.yaml` fires before any parquet search. This is correct. P3b cannot be unblocked in this session.

Additional P3b gaps (not resolved here): FR_2018 EUROMOD output absent; MNL parquet for 2018 absent; `M1_ISF_tpr_comparability_check_2018.md` not written.

---

## 12. P4 blocked status

**P4 (2015+2017+2018): HARD-BLOCKED. Not a priority.**

The `m1_stack_years.py --config p4 --dry-run` command exits 1 with:

```
ERROR  Config 'p4' is not authorised for execution:
P4 is not a priority configuration. No authorisation in Stage M1.
```

The `blocked_configs` gate fires. No activation path exists for P4 in Stage M1.

---

## 13. Dry-run results

| Config | Exit code | Inputs found | Planned output | Gate triggered |
| --- | --- | --- | --- | --- |
| p3a | 0 | 0 / 3 | `fr_p3a_stacked_raw.parquet` | None (dry-run shows BLOCKED) |
| p2  | 0 | 0 / 2 | `fr_p2_stacked_raw.parquet` | None (dry-run shows BLOCKED) |
| p3b | 1 | — | — | `blocked_configs["p3b"]` gate |
| p4  | 1 | — | — | `blocked_configs["p4"]` gate |

No parquets written. `Data/processed/fr/pooled/` remains empty.

Full dry-run output: `Results/JMP_multi_year_stage_M1_execution_readiness_v1.md`.

---

## 14. Missing inputs

The following inputs are absent and must be produced before Stage M1 can execute:

| # | Missing input | Blocks |
| --- | --- | --- |
| 1 | EUROMOD run + `combined_draws_em.parquet` for FR_2015 | MNL parquet for 2015 |
| 2 | EUROMOD run + `combined_draws_em.parquet` for FR_2017 | MNL parquet for 2017 |
| 3 | `fr_2015_RURO_mnl_job_gmm__singles.parquet` (from prep script) | P3a and P2 stack |
| 4 | `fr_2016_RURO_mnl_job_gmm__singles.parquet` in `Data/processed/fr/` | P3a and P2 stack (exists on Z: but not in M1 input dir) |
| 5 | `fr_2017_RURO_mnl_job_gmm__singles.parquet` (from prep script) | P3a stack |

Additionally noted (not hard blocking for stack step, but needed for full pipeline):

| # | Noted gap | Blocks |
| --- | --- | --- |
| 6 | Eurostat `lfst_r_lfsd2pop` / `lfst_r_lfp2acedu` FR rows for 2015 and 2017 | GSURv2 extension for 2015/2017 |
| 7 | INSEE BDM 001688526 for 2015 and 2017 (coverage uncertain) | GSUR denominator cross-check |
| 8 | `FR_gsur_ruro_v2_stageA.parquet` extended to 2015 and 2017 | Improved GSUR rates (v1 is a fallback) |

---

## 15. Future commands if inputs become available

These commands must NOT be run until all upstream inputs are ready. They are documented here for planning only.

### Gate 1 — EUROMOD runs for FR_2015 and FR_2017

Run EUROMOD J1.0+ for FR_2015 and FR_2017 using the same scenario configuration as the 2016 job_gmm run. Inspect the 2016 euromodmeta sidecar for parameters. Produces `combined_draws_em.parquet` under `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\` and `2017\`.

### Gate 2 — MNL prep for FR_2015 and FR_2017

```powershell
# FR_2015
.\.venv\Scripts\python.exe scripts\enhanced\enh_RURO_prep_mnl_basic.py `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\<scenario_name>\scenarios\combined_draws_em.parquet" `
    --out-base "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm" `
    --drawsmeta "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file Data\external\FR_gsur_ruro.parquet `
    --year 2015
```

(Replace all `2015` with `2017` for the 2017 run. Replace `<scenario_name>` with the actual scenario folder name from the EUROMOD run.)

### Gate 3 — Copy parquets to M1 input directory

```powershell
# 2016 (already on Z:)
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"

# 2015 (after prep script run)
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"

# 2017 (after prep script run)
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl_job_gmm__singles.parquet" `
    "Data\processed\fr\"
Copy-Item "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl_job_gmm__mnlmeta.json" `
    "Data\processed\fr\"
```

### Gate 4 — Stage M1 P3a execution (authorised only after Gates 1–3)

```powershell
# Verify dry-run shows all 3 inputs FOUND
.\.venv\Scripts\python.exe scripts\multi_year\m1_stack_years.py --config p3a --dry-run

# If all inputs FOUND, run without --dry-run
.\.venv\Scripts\python.exe scripts\multi_year\m1_stack_years.py --config p3a
```

Subsequent steps (once stacked raw parquet is produced):

```powershell
.\.venv\Scripts\python.exe scripts\multi_year\m1_harmonise_cpi.py --config p3a
.\.venv\Scripts\python.exe scripts\multi_year\m1_add_cluster_key.py --config p3a
.\.venv\Scripts\python.exe scripts\multi_year\m1_validate.py --config p3a
.\.venv\Scripts\python.exe scripts\multi_year\m1_identity_validation.py --config p3a
```

### Optional Gate 2a — P2 sub-stack

After Gate 3 (2015 and 2016 parquets in place), P2 can be built independently:

```powershell
.\.venv\Scripts\python.exe scripts\multi_year\m1_stack_years.py --config p2
```

---

## 16. What was not executed

The following actions were authorised but NOT performed in this session:

| Action | Reason not executed |
| --- | --- |
| `m1_stack_years.py` without `--dry-run` | Inputs absent — blocked |
| `m1_harmonise_cpi.py` | Depends on stacked raw parquet — not yet produced |
| `m1_add_cluster_key.py` | Depends on harmonised parquet |
| `m1_validate.py` | Depends on harmonised parquet |
| `m1_identity_validation.py` | Depends on stacked raw parquet |
| `enh_RURO_prep_mnl_basic.py` for 2015 or 2017 | Not authorised in this session; EUROMOD outputs absent |
| EUROMOD runs for FR_2015 or FR_2017 | Not authorised in this session |
| Any estimation or welfare computation | Not authorised at any point in Stage M1 |
| P3b or P4 activation | Not authorised; blocked gates confirmed functional |

---

## 17. Whether Stage M1 execution is authorized

**Stage M1 execution is NOT authorized.**

Required inputs are absent. Specifically:

- EUROMOD outputs for FR_2015 and FR_2017 have not been produced.
- MNL parquets for 2015 and 2017 do not exist anywhere.
- The 2016 MNL parquet is not in the M1 input directory (`Data/processed/fr/`).

Until gaps 1–5 in §14 are closed, no Stage M1 non-dry-run command should be executed. The dry-run infrastructure is fully functional (exit 0 for p3a/p2, exit 1 for p3b/p4). The CPI/HICP file is in place. Stage M1 will be ready to execute in a single session once the EUROMOD and prep-script steps are completed.

---

## 18. Exact next task

**Priority order for the session that will unblock Stage M1:**

1. **Inspect `Data/external/insee_001688526_2016.csv`** for multi-year coverage. If it contains 2015 and 2017 rows, the INSEE gap closes. If not, download from INSEE BDM.

2. **Extract Eurostat 2015/2017 FR rows** from `Data/external/lfst_r_lfsd2pop_2016_full.csv` and `Data/external/lfst_r_lfp2acedu_2016_full.csv`. Check whether those files contain 2015/2017 year columns. If present, filter and write `lfst_r_lfsd2pop_FR_2015.tsv`, `lfst_r_lfsd2pop_FR_2017.tsv`, `lfst_r_lfp2acedu_FR_2015.tsv`, `lfst_r_lfp2acedu_FR_2017.tsv` to `Data/external/`.

3. **Run EUROMOD for FR_2015 and FR_2017** using EUROMOD J1.0+ (same scenario as 2016 job_gmm). Produce `combined_draws_em.parquet` for each year in `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\` and `2017\`.

4. **Run `enh_RURO_prep_mnl_basic.py`** for FR_2015 and FR_2017 (commands in §15 Gate 2). Produces MNL parquets on Z: for each year.

5. **Copy parquets** for 2015, 2016, and 2017 from Z: to `Data/processed/fr/` (commands in §15 Gate 3).

6. **Verify dry-run** for p3a: `m1_stack_years.py --config p3a --dry-run` should report all 3 inputs FOUND.

7. **Run Stage M1 P3a** once dry-run confirms all inputs found (commands in §15 Gate 4).

**Steps 1–2 can be done without EUROMOD access. Steps 3–4 require EUROMOD J1.0+ to be running. Steps 5–7 follow from steps 3–4.**