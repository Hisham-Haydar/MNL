# JMP Docs/Results Cleanup — Second Pass Execution Report v1

*France 2014–2015–2016 | v1 | 2026-05-21*

---

## 1. Execution verdict

**COMPLETE. 10 files archived. 0 files deleted. 3 user-decision files
left in place. All 22 active next-gate files confirmed present.**

| Item | Count |
|------|-------|
| Files archived (`docs/`) | 8 |
| Files archived (`Results/`) | 2 |
| Files archived (total) | **10** |
| User-decision files left in place | 3 |
| Files deleted | 0 |
| Data parquets / sidecars modified | 0 |
| Scripts / YAML configs modified | 0 |

---

## 2. Files archived

All 10 files moved via `git mv` to
`docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/` (8 files) and
`Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/` (2 files).

### docs/ — 8 files

| File | Category | Incorporated into |
|------|----------|-------------------|
| `JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md` | CORRECTION_INCORPORATED | `JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` |
| `JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md` | CORRECTION_INCORPORATED | `JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` |
| `JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md` | CORRECTION_INCORPORATED | `JMP_GSURv2_y2016_provenance_lock_plan_v1.md` |
| `JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md` | CORRECTION_INCORPORATED | `JMP_GSURv2_multi_year_extension_construction_authorization_v1.md` |
| `JMP_GSURv2_script_remediation_documentation_fix_v1.md` | CORRECTION_INCORPORATED | `JMP_GSURv2_script_remediation_report_v1.md` + `Results/P3a/gsurv2/JMP_GSURv2_script_remediation_static_validation_v1.md` |
| `JMP_multi_year_sample_construction_descriptives_correction_report_v1.md` | CORRECTION_INCORPORATED | `JMP_multi_year_sample_construction_descriptives_report_v1.md` |
| `JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | CLEAR_SUPERSEDED | `JMP_multi_year_stage_M1_execution_readiness_report_v2.md` |
| `JMP_single_year_replication_2015_2017_command_plan_v1.md` | CLEAR_SUPERSEDED | `JMP_single_year_replication_2015_2017_command_plan_v2.md` |

### Results/ — 2 files

| File | Category | Incorporated into |
|------|----------|-------------------|
| `M1_identity_validation_summary.md` | ADDENDUM_INCORPORATED | `JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` §13 |
| `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md` | ADDENDUM_INCORPORATED | `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` |

---

## 3. Files explicitly not archived

The following files were in scope for the second-pass audit but are
classified KEEP or HISTORICAL_KEEP and were not moved:

| File | Reason not archived |
|------|---------------------|
| `Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_static_validation_report_v3.md` | HISTORICAL_KEEP: canonical surviving document in the v1→v2→v3 chain; only dedicated generalization validation record |
| `Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_execution_readiness_v1.md` | HISTORICAL_KEEP: dry-run point-in-time record; no v2 successor with same scope |
| `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md` | HISTORICAL_KEEP: v3 and v3.1 together form the complete revision trail |
| `docs/France_case/_shared/data_audits/RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md` | HISTORICAL_KEEP: comprehensive 2016 data build audit; referenced by M1-clean audit |
| `Results/JMP_multi_year_EUROMD_output_readiness_v1.md` | HISTORICAL_KEEP: pre-Stage-M1 EUROMOD readiness state; not superseded by a v2 |
| `Results/P3a/multi_year_stage_M1/JMP_multi_year_external_assets_inventory_v1.md` | HISTORICAL_KEEP: pre-remediation external assets gap state; not superseded by a v2 |
| `Results/P3a/multi_year_stage_M1/JMP_multi_year_single_year_MNL_readiness_v1.md` | HISTORICAL_KEEP: pre-rebuild MNL readiness state; not superseded by a v2 |

The following conditional candidates were also left in place, awaiting
user decisions or requiring further confirmation before archiving:

| File | Reason deferred |
|------|-----------------|
| `docs/archive/2026-05-26_round2_chain_compression/audit_reaudit_chain/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | Conditional: cited in remediation authorization header; decision deferred |
| `docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` | Conditional: companion to command plan v2; decision deferred |
| `docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` | Conditional: process record; decision deferred |
| `docs/RURO_GSUR_external_acquisition_completion_v1.md` | Conditional: superseded by Stage A authorization; decision deferred |
| `docs/RURO_GSUR_O2_denominator_resolution_v1.md` | Conditional: incorporated into open-decisions resolution; decision deferred |

---

## 4. User-decision files left in place

These three files are explicitly excluded from this task and were not
touched. They remain at their current locations in `docs/`:

| File | Decision pending |
|------|-----------------|
| `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md` | Decision A: is the M0c_b2_GSURv2 evidence chain still active? |
| `docs/RURO_GSUR_external_acquisition_report_v1.md` | Decision B: archive or keep in `docs/`? |
| `docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` | Decision C: archive or keep in `docs/`? |

---

## 5. Active next-gate files preserved

All 22 required active next-gate files were confirmed in place before
and after the archive moves. None were touched.

| # | File | Status |
|---|------|--------|
| 1 | `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_v1.md` | PRESENT |
| 2 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | PRESENT |
| 3 | `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_authorization_v1.md` | PRESENT |
| 4 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | PRESENT |
| 5 | `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | PRESENT |
| 6 | `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | PRESENT |
| 7 | `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` | PRESENT |
| 8 | `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` | PRESENT |
| 9 | `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md` | PRESENT |
| 10 | `docs/RURO_GSUR_external_acquisition_decision_v2.md` | PRESENT |
| 11 | `docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md` | PRESENT |
| 12 | `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_naive_robustness_verdict_v1.md` | PRESENT |
| 13 | `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` | PRESENT |
| 14 | `docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` | PRESENT |
| 15 | `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md` | PRESENT |
| 16 | `docs/archive/2026-05-26_round2_chain_compression/audit_reaudit_chain/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | PRESENT |
| 17 | `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_report_v1.md` | PRESENT |
| 18 | `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` | PRESENT |
| 19 | `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` | PRESENT |
| 20 | `Results/P3a/gsurv2/JMP_GSURv2_MNL_rebuild_report_v2.md` | PRESENT |
| 21 | `Results/P3a/gsurv2/JMP_GSURv2_MNL_rebuild_correction_report_v1.md` | PRESENT |
| 22 | `Results/P3a/multi_year_stage_M1/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` | PRESENT |

---

## 6. Archive directories used

Both archive directories were created in the first-pass cleanup
(commit `59d3b00`, 2026-05-20). The second pass appended files to
the same directories.

| Directory | Files added this pass | Cumulative total |
|-----------|----------------------|-----------------|
| `docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/` | 8 | 17 (9 first pass + 8 second pass) |
| `Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/` | 2 | 8 (6 first pass + 2 second pass) |

---

## 7. Git status summary

`git status --short` before commit showed exactly 10 rename entries
(`R` status) and no other changes:

```
R  Results/JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md -> Results/archive/.../JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md
R  Results/P3a/multi_year_stage_M1/M1_identity_validation_summary.md -> Results/archive/.../M1_identity_validation_summary.md
R  docs/JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md -> docs/archive/...
R  docs/JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md -> docs/archive/...
R  docs/JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md -> docs/archive/...
R  docs/JMP_GSURv2_script_remediation_documentation_fix_v1.md -> docs/archive/...
R  docs/JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md -> docs/archive/...
R  docs/JMP_multi_year_sample_construction_descriptives_correction_report_v1.md -> docs/archive/...
R  docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md -> docs/archive/...
R  docs/JMP_single_year_replication_2015_2017_command_plan_v1.md -> docs/archive/...
```

No new files, no deletions, no modifications — only renames.

---

## 8. What was not executed

- No files were deleted.
- No data parquets were modified, moved, or deleted.
- No sidecar JSON files were modified.
- No Python scripts were modified.
- No YAML configuration files were modified.
- No HTML or PNG output files were modified.
- No `docs/archive/` pre-existing contents were modified.
- `docs/ACKNOWLEDGEMENTS.md` was not modified.
- The `stijn/` directory was not modified.
- No Z: drive paths were touched.
- No pipeline step was executed.
- No pooled stacking was run.
- No estimation was run.
- No welfare computation was performed.
- No welfare implementation was performed.
- The three user-decision files (`RURO_GSUR_O7_crosswalk_signoff_v1.md`,
  `RURO_GSUR_external_acquisition_report_v1.md`,
  `RURO_GSUR_external_acquisition_verification_claude_v1.md`) were not
  touched.
- The five conditional candidates deferred to a third pass were not
  touched.

---

## 9. Final status

Only the 10 clear candidates identified in
`docs/jmp_methodology/JMP_docs_results_cleanup_second_pass_plan_v1.md` §8 were archived.
No user-decision files were archived. No files were deleted. No data
parquets, sidecars, configs, or scripts were modified. No pipeline,
stacking, estimation, or welfare task was run.

**Pooled stacking re-run execution is NOT authorized.**

The immediate next authorized task is to write the Stage M1 P3a GSURv2
stacking re-run authorization memo, as stated in
`docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_v1.md` (corrected by
`docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md`). This cleanup
execution does not change that status.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**Welfare implementation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced only by a
future SA2 verdict explicitly promoting a final pooled specification.