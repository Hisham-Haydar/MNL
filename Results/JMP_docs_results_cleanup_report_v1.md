# JMP Docs/Results Cleanup Report v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Cleanup verdict

**COMPLETE — 15 superseded documents archived. All 16 required active files
confirmed present. No data files, sidecars, scripts, or YAML configs were
modified.**

| Category | Count | Action |
|----------|-------|--------|
| `docs/` archived | 9 | Moved to `docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/` |
| `Results/` archived | 6 | Moved to `Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/` |
| KEEP (active, canonical, uncertain) | Remainder | Left in place |
| Required active files confirmed | 16 / 16 | All present before archiving |

---

## 2. Active file verification

All 16 required active files were confirmed present before any move was
executed. Had any been absent, archiving would have been blocked (BLOCKED
status in this report). All are present; archiving proceeded.

| # | File | Status |
|---|------|--------|
| 1 | `docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md` | PRESENT |
| 2 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | PRESENT |
| 3 | `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md` | PRESENT |
| 4 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | PRESENT |
| 5 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | PRESENT |
| 6 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | PRESENT |
| 7 | `docs/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` | PRESENT |
| 8 | `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md` | PRESENT |
| 9 | `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` | PRESENT |
| 10 | `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md` | PRESENT |
| 11 | `docs/RURO_GSUR_external_acquisition_decision_v2.md` | PRESENT |
| 12 | `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` | PRESENT |
| 13 | `docs/RURO_occ_M1_naive_robustness_verdict_v1.md` | PRESENT |
| 14 | `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` | PRESENT |
| 15 | `docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` | PRESENT |
| 16 | `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` | PRESENT |

---

## 3. Files archived from `docs/`

All nine files moved via `git mv` to
`docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/`.

| File | Superseded by | Chain summary |
|------|---------------|---------------|
| `RURO_GSUR_rebuild_specification_v1.md` | `v2_1` | v1 → v2 → v2_1 (canonical); v1 and v2 archived |
| `RURO_GSUR_rebuild_specification_v2.md` | `v2_1` | Same chain as above |
| `RURO_GSUR_external_acquisition_decision_v1.md` | `v2` | v1 → v2 (3 corrections applied); v1 archived |
| `JMP_multi_year_and_cross_validation_strategy_memo_v1.md` | `v3_1` | v1 → v2 → v3 → v3_1 (canonical); v1 and v2 archived |
| `JMP_multi_year_and_cross_validation_strategy_memo_v2.md` | `v3_1` | Same chain as above |
| `JMP_welfare_measurement_decisions_memo_v1.md` | `v2` | v1 → v2 (corrections applied); v1 archived |
| `JMP_welfare_scaffolding_design_memo_v1.md` | `v2` | v1 → v2 (corrections applied); v1 archived |
| `JMP_multi_year_stage_M1_implementation_plan_v1.md` | `v2` | Revised plan; v1 archived |
| `RURO_occ_M1_clean_design_memo_v1.md` | `v2` | Revised design memo; v1 archived |

---

## 4. Files archived from `Results/`

All six files moved via `git mv` to
`Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/`.

| File | Superseded by | Chain summary |
|------|---------------|---------------|
| `JMP_multi_year_feasibility_audit_addendum_v1.md` | `v2` | v1 → v2 (correction); v1 archived |
| `JMP_multi_year_stage_M1_static_validation_report_v1.md` | `v3` | v1 → v2 → v3 (canonical); v1 and v2 archived |
| `JMP_multi_year_stage_M1_static_validation_report_v2.md` | `v3` | Same chain as above |
| `JMP_multi_year_stage_M1_readiness_addendum_v1.md` | `v2` | v1 → v2 (correction); v1 archived |
| `JMP_multi_year_stage_M1_P3a_execution_report_v1.md` | `full_execution_report_v1` | Partial couples-only execution; full singles+couples report is canonical |
| `JMP_GSURv2_MNL_rebuild_report_v1.md` | `v2` | Stem naming and heading correction applied in v2; v1 archived |

---

## 5. Files confirmed KEEP

The following categories of files were audited and left in place.

**`docs/` — KEEP (canonical, active authorization, design, or uncertain):**

- All JMP GSURv2 MNL rebuild chain: `_authorization_v1`, `_authorization_correction_v1`,
  `_verdict_v1`, `_verdict_correction_v1` — canonical authorization/verdict chain; KEEP
- All GSURv2 multi-year extension chain: `_design_memo_v1`, `_implementation_audit_v1`,
  `_implementation_audit_addendum_v1`, `_remediation_authorization_v1`,
  `_remediation_authorization_correction_v1`, `_remediation_authorization_final_wording_fix_v1`,
  `_script_remediation_report_v1`, `_script_remediation_documentation_fix_v1`,
  `_y2016_provenance_lock_plan_v1`, `_y2016_provenance_lock_plan_correction_v1`,
  `_readiness_reaudit_v1`, `_construction_authorization_v1`,
  `_construction_authorization_correction_v1`, `_construction_verdict_v1`,
  `_construction_verdict_correction_v1`, `_construction_report_v1` — active chain; KEEP
- `RURO_GSUR_rebuild_specification_v2_1.md` — canonical specification; KEEP
- `RURO_GSUR_external_acquisition_decision_v2.md` — canonical acquisition decision; KEEP
- `RURO_GSUR_O7_crosswalk_signoff_v1.md` — UNCERTAIN: single-year scope (FR_2016 only);
  referenced by `RURO_occ_M0c_b2_GSURv2_verdict_v1.md`; no confirmed multi-year successor;
  KEEP in place
- `JMP_GSURv2_O7_crosswalk_signoff_v1.md` — multi-year O7; active; KEEP
- `JMP_multi_year_and_cross_validation_strategy_memo_v3.md` — active; KEEP
- `JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` — canonical; KEEP
- `JMP_welfare_measurement_decisions_memo_v2.md` — canonical; KEEP
- `JMP_welfare_scaffolding_design_memo_v2.md` — canonical; KEEP
- `JMP_multi_year_stage_M1_implementation_plan_v2.md` — active plan; KEEP
- `JMP_multi_year_stage_M1_execution_readiness_report_v1.md` — pre-stage readiness; KEEP
- `JMP_multi_year_stage_M1_execution_readiness_report_v2.md` — active readiness; KEEP
- `JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` — canonical P3a verdict; KEEP
- `JMP_multi_year_stage_M1_generalization_report_v1.md` — standalone; KEEP
- `JMP_multi_year_stage_M1_generalization_fix_report_v1.md` — standalone fix; KEEP
- `JMP_multi_year_stage_M1_implementation_report_v1.md` — standalone implementation; KEEP
- `JMP_GSUR_year_alignment_decision_v1.md` — required active file; KEEP
- `RURO_occ_M1_naive_robustness_verdict_v1.md` — required active file; KEEP
- `RURO_occ_M1_clean_design_memo_v2.md` — active design; KEEP
- All RURO_occ_M0/M0a/M0b/M0c/M1 implementation reports, audits, verdicts — sequential
  development history; KEEP
- All other single-year replication authorization and command plan documents — KEEP
- All other operational/reference docs (`RURO_ACTIVE_RESULTS_REGISTRY.md`,
  `MIRRORED_DOCUMENTS_INDEX.md`, `RURO_METHODS_AND_PIPELINE_MANUAL_v1.md`,
  `PIPELINE_ENTRYPOINTS.md`, etc.) — KEEP

**`Results/` — KEEP (standalone, active, addendum, or uncertain):**

- `JMP_GSURv2_MNL_rebuild_report_v2.md` — active canonical; KEEP
- `JMP_GSURv2_MNL_rebuild_correction_report_v1.md` — active; KEEP
- `JMP_GSURv2_external_file_remediation_report_v1.md` — standalone remediation; KEEP
- `JMP_GSURv2_script_remediation_static_validation_v1.md` — standalone validation; KEEP
- `JMP_GSURv2_multi_year_extension_validation_report_v1.md` — active validation; KEEP
- `JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` — canonical execution; KEEP
- `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md` — addendum to above; KEEP
- `JMP_multi_year_feasibility_audit_addendum_v2.md` — active; KEEP
- `JMP_multi_year_feasibility_audit_v1.md` — standalone feasibility; KEEP
- `JMP_multi_year_stage_M1_static_validation_report_v3.md` — canonical; KEEP
- `JMP_multi_year_stage_M1_readiness_addendum_v2.md` — active; KEEP
- `JMP_multi_year_stage_M1_execution_readiness_v1.md` — standalone dry-run; KEEP
- `JMP_multi_year_EUROMOD_output_readiness_v1.md` — standalone EUROMOD readiness; KEEP
- `JMP_multi_year_external_assets_inventory_v1.md` — standalone inventory; KEEP
- `JMP_multi_year_single_year_MNL_readiness_v1.md` — standalone readiness; KEEP
- `JMP_single_year_FR2015_replication_report_v1.md` — standalone replication; KEEP
- `JMP_single_year_FR2015_replication_addendum_v1.md` — addendum; KEEP
- `JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md` — standalone rebuild; KEEP
- `JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md` — standalone rebuild; KEEP
- `JMP_single_year_FR2017_replication_report_v1.md` — standalone replication; KEEP
- `JMP_single_year_2016_local_mirror_report_v1.md` — standalone mirror; KEEP
- `JMP_single_year_consolidated_readiness_verdict_v1.md` — standalone verdict; KEEP

---

## 6. Files left UNCERTAIN

| File | Reason for UNCERTAIN |
|------|---------------------|
| `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md` | Single-year FR_2016 scope only; referenced by `RURO_occ_M0c_b2_GSURv2_verdict_v1.md`; no confirmed same-scope successor; left in `docs/` |

---

## 7. Archive contents verification

**`docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/`** — 9 files:
- `RURO_GSUR_rebuild_specification_v1.md`
- `RURO_GSUR_rebuild_specification_v2.md`
- `RURO_GSUR_external_acquisition_decision_v1.md`
- `JMP_multi_year_and_cross_validation_strategy_memo_v1.md`
- `JMP_multi_year_and_cross_validation_strategy_memo_v2.md`
- `JMP_welfare_measurement_decisions_memo_v1.md`
- `JMP_welfare_scaffolding_design_memo_v1.md`
- `JMP_multi_year_stage_M1_implementation_plan_v1.md`
- `RURO_occ_M1_clean_design_memo_v1.md`

**`Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/`** — 6 files:
- `JMP_multi_year_feasibility_audit_addendum_v1.md`
- `JMP_multi_year_stage_M1_static_validation_report_v1.md`
- `JMP_multi_year_stage_M1_static_validation_report_v2.md`
- `JMP_multi_year_stage_M1_readiness_addendum_v1.md`
- `JMP_multi_year_stage_M1_P3a_execution_report_v1.md`
- `JMP_GSURv2_MNL_rebuild_report_v1.md`

---

## 8. What was not changed

- No parquet file was modified, moved, or deleted.
- No sidecar JSON was modified.
- No script (Python or other) was modified.
- No YAML configuration was modified.
- No HTML or PNG output file was modified.
- No `docs/archive/` pre-existing contents were modified.
- `docs/ACKNOWLEDGEMENTS.md` was not modified.
- The `stijn/` directory was not modified.
- No Z: drive path was modified.

---

## 9. Authorization status (unchanged by cleanup)

**Pooled stacking re-run execution is NOT authorized.**
The immediate next authorized task is to write the Stage M1 P3a GSURv2
stacking re-run authorization memo. This cleanup does not change that status.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**Welfare implementation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced only by a future
SA2 verdict explicitly promoting a final pooled specification.

---

## 10. Cleanup manifest

Full per-file manifest with source path, archive path, category, reason,
superseded-by, safe-to-archive flag, and notes:

`Results/JMP_docs_results_cleanup_manifest_v1.csv`