# JMP Docs/Results Cleanup — Second Pass Plan v1

*France 2014–2015–2016 | v1 | 2026-05-21*

---

## 1. Purpose

This document records the candidate audit for a second-pass cleanup of `docs/`
and `Results/` markdown artefacts. The first pass (2026-05-20, commit `59d3b00`)
archived 15 unambiguously superseded files. This second pass audits what remains,
classifies every file, and identifies additional archive candidates.

No files are moved in this document. This is an audit and plan only.
Implementation of the moves is a separate, subsequent task.

---

## 2. Why a second pass is needed

The first pass archived only the clearest cases: version chains with an
unambiguous final version (v2_1, v3_1, etc.) and one partial execution report
superseded by a full one. Several additional archive candidates remain:

1. **Correction memos whose content is fully incorporated into the parent
   document** — three correction chains (`remediation_authorization_correction`,
   `remediation_authorization_final_wording_fix`, `y2016_provenance_lock_plan_correction`,
   `construction_authorization_correction`, `script_remediation_documentation_fix`,
   `sample_construction_descriptives_correction`) edited the parent document
   in-place. The correction memo records what changed; once the corrected parent
   is the accepted live document, the correction memo's operational value is
   as a historical record only.

2. **Addendum memos whose content was incorporated into a later authoritative
   document** — the GSURv2 implementation audit addendum was incorporated into
   the remediation authorization; the FR_2015 replication addendum corrected the
   replication report and sidecar (now done); the Stage M1 P3a full execution
   addendum corrected §30 of the full execution report (now done).

3. **Pre-execution readiness reports superseded by v2** — the Stage M1 execution
   readiness report v1 (NOT AUTHORIZED verdict) was superseded by v2 (READY
   verdict). The v1 document records a pre-execution state; all its substance is
   contextualised by v2.

4. **Single-year command plans superseded by v2** — command plan v1 had wrong
   CLI flags; v2 corrected them. The addendum then corrected v2's GSUR keying.

5. **Legacy intermediate GSUR-chain docs** whose findings are now fully superseded
   by the multi-year GSURv2 chain — the standalone single-year O7 sign-off request,
   the Stage A sign-off for the un-tagged y2016 parquet, the external acquisition
   report, the adversarial verification, and the O2 denominator resolution memo
   were all stepping stones to the multi-year GSURv2 construction authorization.
   Their findings are preserved in the authorization chain itself.

6. **Results files that are intermediate diagnostics within a complete chain** —
   `JMP_multi_year_stage_M1_static_validation_report_v3.md` was generated during
   generalization; the generalization fix report superseded its blocker context.
   The identity validation summary `M1_identity_validation_summary.md` is a
   low-level output captured in the full execution report §13.

---

## 3. Active next-gate files that must remain

The following files are required as active references for the immediate next
authorized task (writing the Stage M1 P3a GSURv2 stacking re-run authorization
memo) and for the complete active authorization chain. All must remain in place.

| # | File | Role |
|---|------|------|
| 1 | `docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md` | Active post-rebuild verdict |
| 2 | `docs/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | Verdict correction record |
| 3 | `docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md` | Active rebuild authorization |
| 4 | `docs/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | Authorization correction record |
| 5 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | Active GSURv2 construction verdict |
| 6 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | Verdict correction record |
| 7 | `docs/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` | Active P3a construction verdict |
| 8 | `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md` | Canonical strategy memo |
| 9 | `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md` | Canonical GSUR specification |
| 10 | `docs/RURO_GSUR_external_acquisition_decision_v2.md` | Canonical acquisition decision |
| 11 | `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` | Active alignment rule |
| 12 | `docs/RURO_occ_M1_naive_robustness_verdict_v1.md` | Active M1-naive robustness verdict |
| 13 | `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md` | Canonical welfare decisions |
| 14 | `docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` | Canonical welfare scaffolding design |
| 15 | `docs/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md` | Active construction authorization |
| 16 | `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | Active remediation authorization |
| 17 | `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md` | Active construction report |
| 18 | `docs/RURO_occ_M1_clean_verdict_v1.md` | Active M1-clean verdict (active JMP baseline) |
| 19 | `docs/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` | Active M0c_b2 GSURv2 verdict |
| 20 | `Results/JMP_GSURv2_MNL_rebuild_report_v2.md` | Active rebuild report |
| 21 | `Results/JMP_GSURv2_MNL_rebuild_correction_report_v1.md` | Active correction report |
| 22 | `Results/JMP_multi_year_stage_M1_P3a_full_execution_report_v1.md` | Active full execution report |

---

## 4. Clear archive candidates

These files are unambiguously archivable: the correction or fix they record has
been fully applied to the parent document, which remains active. The correction
memo's residual value is historical provenance only.

### 4.1 docs/ — CLEAR candidates

| File | Category | Superseded by / incorporated into |
|------|----------|----------------------------------|
| `JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md` | CORRECTION_INCORPORATED | Corrections C1–C12 applied directly to `remediation_authorization_v1.md`; the parent document is the live corrected version |
| `JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md` | CORRECTION_INCORPORATED | Fixes F1–F3 applied directly to `remediation_authorization_v1.md`; this is the second-layer fix document; the parent is live |
| `JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md` | CORRECTION_INCORPORATED | Fixes F1–F2 applied directly to `y2016_provenance_lock_plan_v1.md`; the parent is live |
| `JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md` | CORRECTION_INCORPORATED | Corrections applied directly to `construction_authorization_v1.md`; the parent is live |
| `JMP_GSURv2_script_remediation_documentation_fix_v1.md` | CORRECTION_INCORPORATED | Fixes F1–F2 applied directly to `script_remediation_report_v1.md` and `Results/JMP_GSURv2_script_remediation_static_validation_v1.md`; the parent is live |
| `JMP_multi_year_sample_construction_descriptives_correction_report_v1.md` | CORRECTION_INCORPORATED | Corrections C1–C4 applied directly to `sample_construction_descriptives_report_v1.md`; the parent is live |
| `JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | CLEAR_SUPERSEDED | Explicitly superseded by v2 (v2 header states "Supersedes: v1"); v1 verdict was NOT AUTHORIZED; v2 is READY |
| `JMP_single_year_replication_2015_2017_command_plan_v1.md` | CLEAR_SUPERSEDED | Superseded by v2 (CLI flag corrections); v2 header states it supersedes v1 |

### 4.2 Results/ — CLEAR candidates

| File | Category | Superseded by / incorporated into |
|------|----------|----------------------------------|
| `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md` | ADDENDUM_INCORPORATED | Corrections to §30 of `full_execution_report_v1.md` and welfare authorization status documented; substance fully incorporated into `P3a_construction_verdict_v1.md`. Addendum remains a supplementary record — see §5 for conditional status |
| `M1_identity_validation_summary.md` | ADDENDUM_INCORPORATED | Low-level output captured verbatim in `full_execution_report_v1.md` §13 identity-validation section; no independent substance |

---

## 5. Conditional archive candidates

These are archivable but carry a residual reference risk or provenance
consideration that makes a user decision preferable.

| File | Category | Reason for conditional status |
|------|----------|-------------------------------|
| `docs/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | ADDENDUM_INCORPORATED | Addendum specified remediation prerequisites (C1–C7 + external files). These prerequisites are now fully satisfied and documented in the remediation authorization chain. However, the addendum is cited in the remediation authorization v1 header as a reference document; some users may want it traceable |
| `docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` | ADDENDUM_INCORPORATED | GSUR keying correction now incorporated into executed rebuild reports. However, it is still referenced as a companion in those reports; and command plan v2 + this addendum together represent the full authoritative command |
| `docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md` | CORRECTION_INCORPORATED | The request was satisfied by `RURO_GSUR_O7_crosswalk_signoff_v1.md`. The request memo itself carries no decision content; it is pure process overhead. However, the active single-year O7 sign-off itself (`RURO_GSUR_O7_crosswalk_signoff_v1.md`) is uncertain — see §7 |
| `docs/RURO_GSUR_external_acquisition_completion_v1.md` | CLEAR_SUPERSEDED | PARTIAL ACQUISITION SUCCESS verdict; O2 gap was resolved separately by `RURO_GSUR_O2_denominator_resolution_v1.md`; the full acquisition status is synthesised in `RURO_GSUR_StageA_authorization_v1.md`. Standalone provenance value only |
| `docs/RURO_GSUR_O2_denominator_resolution_v1.md` | CORRECTION_INCORPORATED | O2 resolution findings incorporated into `RURO_GSUR_v2_1_open_decisions_resolution_v1.md` as an amendment; that memo is the binding record |
| `docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` | HISTORICAL_KEEP | Adversarial verification of O1/O2/O9 source paths; findings informed the open-decisions resolution but contain independent factual corrections. Useful if the O1 crosswalk is ever re-audited |
| `Results/JMP_multi_year_stage_M1_static_validation_report_v3.md` | HISTORICAL_KEEP | Final version of the static validation chain (v1→v2→v3). v1 and v2 were archived in first pass. v3 is the surviving document in the chain and records the generalization validation. However, the relevant validation status is now captured in the full execution report |
| `Results/JMP_multi_year_stage_M1_execution_readiness_v1.md` | HISTORICAL_KEEP | Dry-run output report (NOT FOUND for all years). Superseded operationally by the full execution, but records a point-in-time readiness assessment cited by the v1 readiness report |

---

## 6. Files to keep despite older versions

These files look like they might be candidates but are KEEP for substantive reasons.

| File | Reason to KEEP |
|------|----------------|
| `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md` | v3 and v3.1 are both referenced in downstream documents. v3.1 corrects two internal inconsistencies but does not supersede v3 as a historical record; together they form the complete revision trail from v2 |
| `docs/JMP_GSURv2_multi_year_extension_readiness_reaudit_v1.md` | Active: this is the READY FOR CONSTRUCTION verdict that enabled the construction authorization. Required in the authorization chain |
| `docs/JMP_GSURv2_multi_year_extension_design_memo_v1.md` | Active governing design memo for the multi-year extension; cited in every downstream authorization |
| `docs/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md` | Active: NOT READY verdict that established the remediation requirement; cited in remediation authorization |
| `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md` | UNCERTAIN — see §7 |
| `docs/JMP_GSURv2_O7_crosswalk_signoff_v1.md` | Active: multi-year O7 sign-off approving the three y2014/y2015/y2016 lookups and the `(drgn1, educ3, sex)` merge key. Required for the MNL rebuild authorization chain |
| `docs/RURO_GSUR_StageA_authorization_v1.md` | Active: reconciles the contradiction between completion memo and open-decisions resolution; is the authoritative authorization source for Stage A. Required by construction authorization chain |
| `docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md` | Active: binding record of all O1–O10 resolutions; required by Stage A authorization |
| `docs/France_case/RURO_GSUR_local_O1_evidence_audit_v1.md` | Active: documents local O1 evidence (actual file inspection); informs the open-decisions resolution and is not superseded |
| `docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md` | Active: READY verdict; cited by full execution report |
| `docs/RURO_occ_M0c_b2_verdict_v1.md` | Active: terminal verdict in the M0a→M0b1→M0b2→M0c_b→M0c_b2 ladder; cited by M0c_b2_GSURv2 verdict |
| `docs/JMP_multi_year_stage_M1_implementation_report_v1.md` | Active: scaffolding completion record for Stage M1; cited by construction verdict |
| `docs/JMP_multi_year_stage_M1_generalization_report_v1.md` | Active: generalization of Stage M1 scripts; cited by generalization fix report |
| `docs/JMP_multi_year_stage_M1_generalization_fix_report_v1.md` | Active: two blocker fixes applied post-generalization; required for the static validation v3 context |
| `docs/France_case/RURO_prep_mnl_gsur_year_support_report_v1.md` | Active: documents `--gsur-year` CLI flag patch to `enh_RURO_prep_mnl_basic.py`; required context for single-year rebuild reports |
| `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` | Active: authorization for the FR_2015 and FR_2017 replications; cited by readiness report v2 |
| `docs/JMP_multi_year_stage_M1_implementation_plan_v2.md` | Active: governing plan for Stage M1; cited throughout |
| `docs/France_case/JMP_multi_year_CPI_HICP_source_decision_v1.md` | Active: CPI source decision (Option B); required for harmonization |
| `docs/JMP_multi_year_sample_construction_descriptives_report_v1.md` | Active: descriptives and sample-construction documentation for all three years |
| `docs/RURO_GSUR_v2_stageA_implementation_report_v1.md` | Active: Stage A implementation record for single-year y2016; cited by construction authorization |
| `docs/France_case/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` | Active: GSUR merge audit; cited by M0c_b2 verdict |
| `docs/RURO_occ_M1_clean_implementation_audit_v1.md` | Active: pre-estimation audit for M1-clean; cited by M1-clean verdict |
| `docs/RURO_occ_M1_clean_YAML_implementation_report_v1.md` | Active: M1-clean YAML implementation record |
| `docs/RURO_occ_M1_clean_design_memo_v2.md` | Active: canonical M1-clean design memo |
| `docs/RURO_post_estimation_M1_diagnostics_implementation_report_v1.md` | Active: implementation record for M1-clean diagnostics script |
| `docs/RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md` | Active: implementation record for M1-naive diagnostics script |
| `docs/RURO_occ_M1_naive_YAML_implementation_report_v1.md` | Active: M1-naive YAML derivation record |
| `docs/JMP_GSURv2_script_remediation_report_v1.md` | Active: remediation completion record for C1–C7; cited by construction authorization chain |
| `docs/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` | Active: lock plan required by construction authorization; now corrected in-place |
| `docs/RURO_GSUR_external_acquisition_report_v1.md` | HISTORICAL_KEEP: initial acquisition analysis; long, detailed, contains O1/O2/O9 reasoning not reproduced elsewhere |
| `docs/France_case/RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md` | HISTORICAL_KEEP: comprehensive audit of the 2016 data build pipeline; referenced by M1-clean audit |
| `Results/JMP_multi_year_feasibility_audit_v1.md` | Active: feasibility assessment for P3a/P3b/P4; cited by addendum v2 |
| `Results/JMP_multi_year_feasibility_audit_addendum_v2.md` | Active: P3b/P4 branches and 2018 assessment |
| `Results/JMP_single_year_FR2015_replication_report_v1.md` | Active: FR_2015 replication execution record |
| `Results/JMP_single_year_FR2015_replication_addendum_v1.md` | Active: correction addendum now executed; documents sidecar updates |
| `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md` | Active: FR_2015 GSUR-aligned rebuild execution record |
| `Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md` | Active: FR_2016 GSUR-aligned rebuild execution record |
| `Results/JMP_single_year_FR2017_replication_report_v1.md` | Active: FR_2017 replication execution record |
| `Results/JMP_single_year_2016_local_mirror_report_v1.md` | Active: FR_2016 local mirror record |
| `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` | Active: consolidated Stage M1 input readiness verdict |
| `Results/RURO_GSUR_v2_stageA_lookup_validation_report_v1.md` | Active: Stage A lookup validation; cited by M0c_b2 GSURv2 verdict |
| `Results/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md` | Active: Stage A MNL rebuild record; cited by M0c_b2 GSURv2 verdict |
| `Results/JMP_GSURv2_external_file_remediation_report_v1.md` | Active: external file retrieval record; cited by construction authorization |
| `Results/JMP_GSURv2_script_remediation_static_validation_v1.md` | Active: static validation record; cited by remediation authorization chain |
| `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md` | Active: construction validation record; cited by construction verdict |
| `Results/RURO_occ_M0c_b2_GSURv2_estimation_input_check_v1.md` | Active: pre-estimation input check for M0c_b2_GSURv2 |
| `Results/RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md` | Active: M0c_b2_GSURv2 estimation record |
| `Results/RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md` | Active: M0c_b2_GSURv2 diagnostics; cited by M1-clean diagnostics |
| `Results/RURO_occ_M1_clean_gate_A_parse_report_v1.md` | Active: M1-clean Gate A parse |
| `Results/RURO_occ_M1_clean_estimation_report_v1.md` | Active: M1-clean estimation record |
| `Results/RURO_occ_M1_clean_standard_post_estimation_diagnostics_v1.md` | Active: M1-clean standard diagnostics |
| `Results/RURO_occ_M1_clean_supplementary_diagnostics_v1.md` | Active: M1-clean supplementary diagnostics |
| `Results/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md` | Active: M1-clean composite diagnostics; cited by M1-clean verdict |
| `Results/RURO_occ_M1_naive_gate_A_parse_report_v1.md` | Active: M1-naive Gate A parse |
| `Results/RURO_occ_M1_naive_estimation_report_v1.md` | Active: M1-naive estimation record |
| `Results/RURO_occ_M1_naive_post_estimation_diagnostics_v1.md` | Active: M1-naive diagnostics |
| `Results/RURO_occ_M1_naive_supplementary_diagnostics_v1.md` | Active: M1-naive supplementary diagnostics |

---

## 7. Files requiring user decision

These files cannot be classified unambiguously without a user decision.

| File | REVIEW reason |
|------|---------------|
| `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md` | Single-year O7 sign-off approving `FR_gsur_ruro_v2_stageA.parquet` (the un-tagged y2016 file) and the `(drgn1, educ3, sex)` merge key for single-year GSURv2 MNL writes. The multi-year O7 (`JMP_GSURv2_O7_crosswalk_signoff_v1.md`) supersedes this for multi-year purposes, but the single-year document was cited by `RURO_occ_M0c_b2_GSURv2_verdict_v1.md`. If the M0c_b2_GSURv2 estimation result is still considered part of the active evidence chain, this sign-off remains in scope. If M0c_b2_GSURv2 is considered a historical stepping stone only, it can be archived. **User decision needed: is M0c_b2_GSURv2 evidence chain still active or historical?** |
| `docs/RURO_GSUR_external_acquisition_report_v1.md` | Long initial acquisition analysis. Its O1 reasoning contained factual errors corrected by the adversarial verification. However, it contains detailed O2/O9 source identification reasoning not reproduced in later documents. If the acquisition provenance trail is considered complete via the authorization chain, this is HISTORICAL_KEEP. If source-path reasoning may need re-examination, it should stay in docs/. **User decision: treat as HISTORICAL_KEEP in archive, or keep in docs/?** |
| `docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` | Adversarial verification correcting factual errors in the acquisition report. It informs `RURO_GSUR_v2_1_open_decisions_resolution_v1.md` but is not cited in the authorization chain. **User decision: archive as HISTORICAL_KEEP, or keep in docs/?** |

---

## 8. Archive strategy

### Proposed second-pass archive directory

All second-pass archives go to the same dated directory:

```
docs/archive/2026-05-20_post_gsurv2_mnl_rebuild/
Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/
```

(Already created in first pass. Second-pass files are appended to the same
directory — same cleanup event, same provenance date.)

### Two-step execution (as with first pass)

1. `git mv` each file to its archive destination.
2. Commit with message `cleanup(docs/Results): second-pass archive — correction/addendum memos incorporated`.

### Clear candidates to move (no user decision needed)

**docs/ — CLEAR (8 files):**
1. `JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md`
2. `JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md`
3. `JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md`
4. `JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md`
5. `JMP_GSURv2_script_remediation_documentation_fix_v1.md`
6. `JMP_multi_year_sample_construction_descriptives_correction_report_v1.md`
7. `JMP_multi_year_stage_M1_execution_readiness_report_v1.md`
8. `JMP_single_year_replication_2015_2017_command_plan_v1.md`

**Results/ — CLEAR (2 files):**
1. `M1_identity_validation_summary.md`
2. `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md`

### Conditional candidates — await user decision

**docs/ — CONDITIONAL (move only after user confirms):**
- `JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md`
- `JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md`
- `RURO_GSUR_O7_crosswalk_signoff_request_v1.md`
- `RURO_GSUR_external_acquisition_completion_v1.md`
- `RURO_GSUR_O2_denominator_resolution_v1.md`
- `RURO_GSUR_external_acquisition_verification_claude_v1.md` (user decision §7)
- `RURO_GSUR_external_acquisition_report_v1.md` (user decision §7)
- `RURO_GSUR_O7_crosswalk_signoff_v1.md` (user decision §7)

**Results/ — CONDITIONAL:**
- `JMP_multi_year_stage_M1_static_validation_report_v3.md`
- `JMP_multi_year_stage_M1_execution_readiness_v1.md`

---

## 9. What not to archive

The following categories must not be archived regardless of age:

- Any file containing an active authorization, verdict, or design decision
  cited by the immediate next-gate task (writing the stacking re-run
  authorization memo).
- Any file in the M1-clean and M1-naive estimation chain
  (`RURO_occ_M1_*`, `RURO_occ_M0c_b2_GSURv2_*`, `RURO_occ_M0c_b2_verdict_v1.md`)
  — M1-clean 2016 remains the active JMP baseline.
- Any single-year rebuild execution report (`JMP_single_year_*`) — these are
  the provenance records for the parquets used in Stage M1 P3a.
- Any parquet, sidecar, script, YAML, HTML, or PNG file.
- `docs/archive/` pre-existing contents.
- `docs/ACKNOWLEDGEMENTS.md`.
- `stijn/` directory.
- Any file in the M0a/M0b/M0c chain that is the terminal verdict or cited
  by a later verdict — these are the historical identification ladder steps.

---

## 10. Recommended next archival task

**Immediate next step:** Execute the clear candidates (10 files listed in §8)
via `git mv` and commit. This requires no user decision and reduces `docs/`
by 8 files and `Results/` by 2 files.

**After user decisions on §7:** Execute the conditional candidates (up to 10
additional files) in a second commit once the three user decisions are made:

1. Is the M0c_b2_GSURv2 evidence chain still active, or historical? (Affects
   `RURO_GSUR_O7_crosswalk_signoff_v1.md`)
2. Should `RURO_GSUR_external_acquisition_report_v1.md` be archived or kept
   in `docs/` as an accessible reference?
3. Should `RURO_GSUR_external_acquisition_verification_claude_v1.md` be
   archived or kept?

These decisions do not affect the immediate next authorized task (writing the
stacking re-run authorization memo) and can be deferred.