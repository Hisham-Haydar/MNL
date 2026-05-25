# JMP Docs/Results Cleanup Plan v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Purpose

This document records the cleanup plan for `docs/` and `Results/` markdown
and CSV artefacts following the completion of the Stage M1 P3a GSURv2
stacking rebuild and post-rebuild verdict (2026-05-20). The cleanup archives
unambiguously superseded intermediate documents while preserving all active
authorizations, verdicts, reports, and design documents. No parquet files,
sidecars, scripts, or YAML configs are in scope.

---

## 2. Scope

**In scope:** Markdown (`.md`) and CSV (`.csv`) files under `docs/` and
`Results/` only.

**Out of scope (not touched):**

- All parquet files (`.parquet`)
- All sidecar JSON files (`__mnlmeta.json`, `__stageA_meta.json`, etc.)
- All Python scripts (`scripts/`, `Results/_canary_*.py`, `Results/_validation_*.py`)
- All YAML configs (`config/`, `scripts/enhanced/`)
- All HTML and PNG outputs under `outputs/`
- `docs/archive/` (sealed historical snapshot)
- `docs/ACKNOWLEDGEMENTS.md`
- `stijn/` (R-notebook authorship; not touched)
- Z: drive paths (shared storage; outside repo)

---

## 3. Active file requirements (must be present before any archiving)

The following 16 files are required to be present and active. All 16 were
confirmed present before any archiving proceeded.

| # | File | Confirmed present |
|---|------|-------------------|
| 1 | `docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md` | YES |
| 2 | `docs/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | YES |
| 3 | `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md` | YES |
| 4 | `docs/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | YES |
| 5 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | YES |
| 6 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | YES |
| 7 | `docs/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` | YES |
| 8 | `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md` | YES |
| 9 | `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` | YES |
| 10 | `docs/RURO_GSUR_rebuild_specification_v2_1.md` | YES |
| 11 | `docs/RURO_GSUR_external_acquisition_decision_v2.md` | YES |
| 12 | `docs/JMP_GSUR_year_alignment_decision_v1.md` | YES |
| 13 | `docs/RURO_occ_M1_naive_robustness_verdict_v1.md` | YES |
| 14 | `docs/JMP_welfare_measurement_decisions_memo_v2.md` | YES |
| 15 | `docs/JMP_welfare_scaffolding_design_memo_v2.md` | YES |
| 16 | `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` | YES |

All 16 confirmed present. Archiving proceeds.

---

## 4. Supersession chains and archive decisions

### 4.1 `docs/` — unambiguously superseded (ARCHIVE)

| Superseded file | Superseded by | Reason |
|----------------|---------------|--------|
| `RURO_GSUR_rebuild_specification_v1.md` | `v2` → `v2_1` | Replaced by two successive corrections; v2_1 is canonical |
| `RURO_GSUR_rebuild_specification_v2.md` | `v2_1` | Replaced by final correction |
| `RURO_GSUR_external_acquisition_decision_v1.md` | `v2` | Three corrections applied; v2 is canonical |
| `JMP_multi_year_and_cross_validation_strategy_memo_v1.md` | `v2` → `v3` → `v3_1` | Successive corrections; v3_1 is canonical |
| `JMP_multi_year_and_cross_validation_strategy_memo_v2.md` | `v3` → `v3_1` | Superseded by further corrections |
| `JMP_welfare_measurement_decisions_memo_v1.md` | `v2` | Superseded by corrected version |
| `JMP_welfare_scaffolding_design_memo_v1.md` | `v2` | Superseded by corrected version |
| `JMP_multi_year_stage_M1_implementation_plan_v1.md` | `v2` | Superseded by revised plan |
| `RURO_occ_M1_clean_design_memo_v1.md` | `v2` | Superseded by revised design memo |

### 4.2 `Results/` — unambiguously superseded (ARCHIVE)

| Superseded file | Superseded by | Reason |
|----------------|---------------|--------|
| `JMP_multi_year_feasibility_audit_addendum_v1.md` | `v2` | Corrected version exists |
| `JMP_multi_year_stage_M1_static_validation_report_v1.md` | `v2` → `v3` | Two successive corrections; v3 canonical |
| `JMP_multi_year_stage_M1_static_validation_report_v2.md` | `v3` | Superseded by final correction |
| `JMP_multi_year_stage_M1_readiness_addendum_v1.md` | `v2` | Corrected version exists |
| `JMP_multi_year_stage_M1_P3a_execution_report_v1.md` | `full_execution_report_v1` | Partial (couples-only) execution; superseded by full singles+couples report |
| `JMP_GSURv2_MNL_rebuild_report_v1.md` | `v2` | Superseded by corrected report with required headings and authorized stems |

### 4.3 `docs/` — KEEP (active, canonical, or uncertain)

All files not listed in §4.1 are KEEP. Uncertain files (e.g.,
`RURO_GSUR_O7_crosswalk_signoff_v1.md`) are KEEP: they have no confirmed
canonical successor with identical scope.

### 4.4 `Results/` — KEEP (active, standalone, or uncertain)

All files not listed in §4.2 are KEEP. Standalone reports (single-year
replication reports, EUROMOD readiness, external assets inventory, GSURv2
remediation, GSURv2 extension validation, etc.) have no v2 successors and
are KEEP. The `full_execution_addendum_v1` is an addendum (supplements,
not supersedes, `full_execution_report_v1`) and is KEEP alongside its base.

---

## 5. Archive target directories

| Source root | Archive directory |
|-------------|-------------------|
| `docs/` | `docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/` |
| `Results/` | `Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/` |

---

## 6. Operations

**Docs to archive** (copy to archive directory, then remove from `docs/`):

1. `docs/RURO_GSUR_rebuild_specification_v1.md`
2. `docs/RURO_GSUR_rebuild_specification_v2.md`
3. `docs/RURO_GSUR_external_acquisition_decision_v1.md`
4. `docs/JMP_multi_year_and_cross_validation_strategy_memo_v1.md`
5. `docs/JMP_multi_year_and_cross_validation_strategy_memo_v2.md`
6. `docs/JMP_welfare_measurement_decisions_memo_v1.md`
7. `docs/JMP_welfare_scaffolding_design_memo_v1.md`
8. `docs/JMP_multi_year_stage_M1_implementation_plan_v1.md`
9. `docs/RURO_occ_M1_clean_design_memo_v1.md`

**Results to archive** (copy to archive directory, then remove from `Results/`):

1. `Results/JMP_multi_year_feasibility_audit_addendum_v1.md`
2. `Results/JMP_multi_year_stage_M1_static_validation_report_v1.md`
3. `Results/JMP_multi_year_stage_M1_static_validation_report_v2.md`
4. `Results/JMP_multi_year_stage_M1_readiness_addendum_v1.md`
5. `Results/JMP_multi_year_stage_M1_P3a_execution_report_v1.md`
6. `Results/JMP_GSURv2_MNL_rebuild_report_v1.md`

---

## 7. Constraints

- No parquet, sidecar, script, YAML, HTML, or PNG file is touched.
- No `docs/archive/` contents are modified (sealed snapshot).
- No `docs/ACKNOWLEDGEMENTS.md` is modified.
- Files are moved via `git mv` (copy then remove from original location) to
  preserve git history.
- All UNCERTAIN files remain in their original location.

---

## 8. Verification

After archiving:

1. All 16 required active files confirmed present in their original locations.
2. Archive directories contain exactly the files listed in §6.
3. `git status` shows only expected renames (moved files) and new archive-
   directory entries.
4. No parquet, sidecar, script, or YAML changes in `git diff`.

---

## 9. What this cleanup does NOT authorize

- No estimation run.
- No welfare computation or implementation.
- No GSURv2 stacking re-run execution.
- No canonical promotion of any MNL parquet.
- No modification to any Result, sidecar, or script.

The Stage M1 P3a GSURv2 stacking re-run authorization memo remains the
immediate next authorized task (per `docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md`
as corrected by `docs/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md`).

---

## 10. Cleanup status

**COMPLETE** — all operations in §6 executed 2026-05-20. Manifest recorded in
`Results/JMP_docs_results_cleanup_manifest_v1.csv`. Report in
`Results/JMP_docs_results_cleanup_report_v1.md`.