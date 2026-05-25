# Move Manifest — 2026-05-27 Round 3 Track Restructure

## Context

- **Approver:** Hisham (2026-05-27 conversation)
- **Scope:** `docs/France_case/` reorganization into tracks (job_model / P3a / NC_pilot / _shared). No `docs/` root files changed (those were settled in Rounds 1-2). No `Results/`, scripts, or EUROMOD-STORAGE touched. Pre-existing `docs/archive/` contents untouched.
- **Policy basis:** Round 1 manifest, Round 2 manifest, plus user direction (2026-05-27): "either the file is general for the package or it is for the france case, when we go to france case we have either job model... or the p3a... NC... and for both cases for singles we draw 100. EUROMOD reference is an index of input output variables definitions. GSUR is for group specific unemployment rate."
- **Goal:** make France_case browsable by track — anyone reading the France case immediately sees "this paper has 3 tracks; here's what's active and what's archived per track."
- **Method:** `git mv` per file (history-preserving). One commit per phase. No within-track content archival in this pass (Round 2 already handled the obvious supersession cases; reading confirmed no clear new candidates).

## Summary counts

| Bucket | Files moved | Net delta |
|---|---:|---|
| _shared/ (EUROMOD ref + GSUR + data audits + notes + results + governance) | 23 | 0 (relocation, not archival) |
| job_model/ (from job_choice/) | 3 | 0 (relocation) |
| NC_pilot/ (design memos split out) | 21 (4 to design/, 17 to execution_logs/) | 0 (relocation) |
| P3a/ (design + single_year_baseline + multi_year_stage_M1 + pooled_P3a + GSURv2 + Bpool + canary + consolidated) | 75 | 0 (relocation) |
| New READMEs | +4 | +4 active |
| Manifest | +1 | +1 |
| **Subdirs removed** (jmp/, canary_reports/, job_choice/, notes/, results/, euromod_reference/, consolidated/, execution_logs/) | 8 | n/a |

Active surface unchanged (~147). This is a restructure, not a compression.

## Commit chain

| Phase | Commit | Description |
|---|---|---|
| A — scaffold | (pending) | Create new subdirs + 4 new READMEs + manifest skeleton + update France_case top-level README |
| B1 — _shared/ moves | (pending) | EUROMOD ref + GSUR + data audits + notes + results + governance (23 mvs) |
| B2 — job_model moves | (pending) | from `job_choice/` (3 mvs) |
| B3 — NC_pilot moves | (pending) | 21 mvs (4 design, 17 execution_logs) |
| B4a — P3a single_year_baseline moves | (pending) | M0a/b/c + M1 chains (~18 mvs) |
| B4b — P3a multi_year + pooled + GSURv2 + Bpool moves | (pending) | ~30 mvs |
| B4c — P3a design + canary + consolidated moves | (pending) | ~11 mvs |
| C — Cross-track See-also links | (pending) | Add See-also lines in cross-track references |
| D — patch inbound refs | (pending) | path-mapping script run |
| E — remove emptied subdirs | (pending) | jmp/, canary_reports/, job_choice/, notes/, results/, euromod_reference/, consolidated/, execution_logs/ |
| F — fill manifest with SHAs | (pending) | this manifest |

## Per-file mapping

### A. _shared/ moves (23)

| Old path | New path |
|---|---|
| `docs/France_case/euromod_reference/DRD_FR_2016_a3_export.txt` | `docs/France_case/_shared/euromod_reference/DRD_FR_2016_a3_export.txt` |
| `docs/France_case/euromod_reference/DRD_FR_2016_index.jsonl` | `docs/France_case/_shared/euromod_reference/DRD_FR_2016_index.jsonl` |
| `docs/France_case/euromod_reference/FR_2015_all_tables_compact.md` | `docs/France_case/_shared/euromod_reference/FR_2015_all_tables_compact.md` |
| `docs/France_case/euromod_reference/FR_2015_index.jsonl` | `docs/France_case/_shared/euromod_reference/FR_2015_index.jsonl` |
| `docs/France_case/euromod_reference/FR_2015_index.md` | `docs/France_case/_shared/euromod_reference/FR_2015_index.md` |
| `docs/France_case/euromod_reference/euromod_fr_2015_2017_input_output_reference.md` | `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_output_reference.md` |
| `docs/France_case/euromod_reference/euromod_fr_2015_2017_input_variables.csv` | `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_variables.csv` |
| `docs/France_case/euromod_reference/euromod_fr_2015_2017_output_variable_index.csv` | `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_output_variable_index.csv` |
| `docs/France_case/euromod_reference/euromod_fr_2015_2017_standard_income_concepts.csv` | `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_standard_income_concepts.csv` |
| `docs/France_case/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` | `docs/France_case/_shared/gsur/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` |
| `docs/France_case/RURO_GSUR_local_O1_evidence_audit_v1.md` | `docs/France_case/_shared/gsur/RURO_GSUR_local_O1_evidence_audit_v1.md` |
| `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md` | `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md` |
| `docs/France_case/consolidated/RURO_GSUR_external_acquisition_consolidated_v1.md` | `docs/France_case/_shared/gsur/RURO_GSUR_external_acquisition_consolidated_v1.md` |
| `docs/France_case/RURO_data_audit_v1.md` | `docs/France_case/_shared/data_audits/RURO_data_audit_v1.md` |
| `docs/France_case/RURO_data_audit_v1_addendum.md` | `docs/France_case/_shared/data_audits/RURO_data_audit_v1_addendum.md` |
| `docs/France_case/RURO_sample_funnel_v1.md` | `docs/France_case/_shared/data_audits/RURO_sample_funnel_v1.md` |
| `docs/France_case/RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md` | `docs/France_case/_shared/data_audits/RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md` |
| `docs/France_case/RURO_prep_mnl_gsur_year_support_report_v1.md` | `docs/France_case/_shared/data_audits/RURO_prep_mnl_gsur_year_support_report_v1.md` |
| `docs/France_case/notes/EUROMO_sys_france_2015.md` | `docs/France_case/_shared/notes/EUROMO_sys_france_2015.md` |
| `docs/France_case/notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md` | `docs/France_case/_shared/notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md` |
| `docs/France_case/results/KEEP_RESULTS.md` | `docs/France_case/_shared/results/KEEP_RESULTS.md` |
| `docs/France_case/RURO_spec_redesign_decisions_v2.md` | `docs/France_case/_shared/governance/RURO_spec_redesign_decisions_v2.md` |
| `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` | `docs/France_case/_shared/governance/JMP_GSUR_year_alignment_decision_v1.md` |
| `docs/France_case/JMP_multi_year_CPI_HICP_source_decision_v1.md` | `docs/France_case/_shared/governance/JMP_multi_year_CPI_HICP_source_decision_v1.md` |

### B. job_model/ moves (3, from job_choice/)

| Old path | New path |
|---|---|
| `docs/France_case/job_choice/README_job_model.md` | `docs/France_case/job_model/README_job_model.md` |
| `docs/France_case/job_choice/ACCEPTANCE_TESTS.md` | `docs/France_case/job_model/ACCEPTANCE_TESTS.md` |
| `docs/France_case/job_choice/Commands_job.txt` | `docs/France_case/job_model/Commands_job.txt` |

### C. NC_pilot/ moves (21)

Design memos to `NC_pilot/design/` (4):
- `JMP_NC_pilot_spec_contract_v1.md`
- `JMP_NC_pilot_vectorized_estimator_design_contract_v1.md`
- `JMP_NC_pilot_optimizer_multistart_design_memo_v1.md`
- `JMP_NC_pilot_beta_l0_m_specification_review_v1.md`

Rest to `NC_pilot/execution_logs/` (17):
- The remaining JMP_NC_pilot_* execution logs, amendments, verdicts

### D. P3a/ moves (75 across 3 sub-phases)

**D1. P3a/execution_logs/single_year_baseline/ — 18 mvs:**

`M0a-clean/` (2 + 1 reshuffled from M0):
- From `execution_logs/occ_M0a/`: `RURO_occ_M0a_clean_implementation_report_v1.md`, `RURO_occ_M0a_clean_post_estimation_patch_report_v1.md`
- From `execution_logs/occ_M1/` (misfiled): `RURO_ruro_occ_M0_estimation_run_2026-05-13.md`

`M0b/` (3): all from `execution_logs/occ_M0b/`

`M0c/` (3): all from `execution_logs/occ_M0c/`

`M1/` (9, one misfile relocated):
- From `execution_logs/occ_M1/`: `RURO_occ_M1_clean_YAML_implementation_report_v1.md`, `..._design_memo_v2.md`, `..._implementation_audit_v1.md`, `..._verdict_v1.md`, `..._naive_YAML_implementation_report_v1.md`, `..._naive_robustness_verdict_v1.md`, `RURO_post_estimation_M1_diagnostics_implementation_report_v1.md`, `RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md`
- `RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md` moves to `pooled_P3a/` instead (D2)

**D2. P3a/execution_logs/{multi_year_stage_M1,pooled_P3a,GSURv2,Bpool}/ — 30 mvs:**

- `multi_year_stage_M1/`: all 10 from `execution_logs/stage_M1/`
- `pooled_P3a/`: all 5 from `execution_logs/pooled_P3a/` + `RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md` (reshuffled from occ_M1)
- `GSURv2/`: all 10 from `execution_logs/GSURv2/`
- `Bpool/`: all 4 from `execution_logs/Bpool/`

**D3. P3a/{design,canary_reports,consolidated}/ — 11 mvs:**

To `design/` (8):
- From France_case root: `FR2016_RURO_pipeline_report.md`, `RURO_ruro_occ_baseline_spec_v1.md`, `RURO_ruro_occ_baseline_implementation_report_v1.md`, `RURO_ruro_occ_M0_rebuild_command_plan_v1.md`, `RURO_ruro_occ_M0_file_sync_check_v1.md`, `RURO_ruro_occ_post_estimation_report_fix_v1.md`
- From `execution_logs/` root: `JMP_next_cycle_opportunity_respecification_plan_v1.md`
- From `execution_logs/pooled_P3a/`: `JMP_pooled_P3a_estimation_design_memo_v1.md` (design memo, fits better under design/; execution_logs/pooled_P3a/ keeps the run reports)

To `canary_reports/` (1):
- From `canary_reports/`: `RURO_ruro_occ_M0_rebuild_canary_report_v1.md`

To `consolidated/` (3):
- From `consolidated/`: `JMP_multi_year_2015_2017_consolidated_v1.md`, `RURO_GSUR_rebuild_consolidated_v1.md`
- From France_case root: `RURO_pilot_gsurv2_verification_v1.md` (cross-track verification: GSURv2 + NC pilot spec; see-also link from NC_pilot/README.md)

### E. Cross-track See-also links

The `RURO_pilot_gsurv2_verification_v1.md` doc verifies both P3a (GSURv2) and NC pilot. Placed in `P3a/consolidated/`; a See-also reference in `NC_pilot/README.md` already points to it.

### F. Subdirs removed at end (Phase E)

After all moves, these emptied subdirs are removed:
- `docs/France_case/jmp/` (was already empty)
- `docs/France_case/canary_reports/`
- `docs/France_case/job_choice/`
- `docs/France_case/notes/`
- `docs/France_case/results/`
- `docs/France_case/euromod_reference/`
- `docs/France_case/consolidated/`
- `docs/France_case/execution_logs/` and its 9 bucket subdirs

### G. Cross-reference fixes (Phase D)

Path-mapping script run — same approach as Round 2. To be filled with results after Phase D commit.

| Patched location | Refs rewritten | Notes |
|---|---:|---|

### H. Deferred follow-ups

- Within-track content consolidation: read confirmed no clear archive candidates this pass. The `_clean` vs `_naive` and `M1_clean` cascade chains in P3a/M1 are sequential gates, not duplicates. The `generalization_report` + `generalization_fix_report` pair documents distinct cumulative changes. Future pass can revisit when work stabilizes.
- Inside-archive "verify" pass: Round 2's archive supersession notes may use old paths (pre-Round-3) for some inter-archive cross-references. Round 3's path-mapping script will catch any inter-archive ref that points to a now-moved active file. Refs pointing to fellow archive files within Round 2 are unchanged.

### I. Verification (run after Phase F)

```powershell
# 1. France_case top-level contains only the 4 track folders + _shared + cleanup + README
Get-ChildItem docs/France_case -Force | Where-Object { $_.Name -notin '.','..' } | Sort-Object Name

# 2. Each track populated
foreach ($t in 'P3a','NC_pilot','job_model','_shared') {
  "$t : " + (Get-ChildItem "docs/France_case/$t" -Recurse -File -Filter '*.md' | Measure-Object).Count
}

# 3. P3a sub-buckets populated
foreach ($d in 'design','canary_reports','consolidated','execution_logs/single_year_baseline/M0a-clean','execution_logs/single_year_baseline/M0b','execution_logs/single_year_baseline/M0c','execution_logs/single_year_baseline/M1','execution_logs/multi_year_stage_M1','execution_logs/pooled_P3a','execution_logs/GSURv2','execution_logs/Bpool') {
  "$d : " + (Get-ChildItem "docs/France_case/P3a/$d" -File -Filter '*.md' 2>$null | Measure-Object).Count
}

# 4. Old subdirs gone
foreach ($d in 'jmp','canary_reports','job_choice','notes','results','euromod_reference','consolidated','execution_logs') {
  if (Test-Path "docs/France_case/$d") { "STILL PRESENT: $d" } else { "removed: $d" }
}

# 5. Git history preserved
git log --follow --oneline -- docs/France_case/P3a/design/FR2016_RURO_pipeline_report.md | Select-Object -First 5
git log --follow --oneline -- docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md | Select-Object -First 5
```
