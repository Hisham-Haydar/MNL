# JMP Docs/Results Cleanup — Second Pass Report v1

*France 2014–2015–2016 | v1 | 2026-05-21*

---

## 1. Audit verdict

**AUDIT COMPLETE. No files moved. 10 CLEAR archive candidates identified;
10 additional CONDITIONAL candidates identified; 3 files require user decision.**

| Category | docs/ | Results/ | Total |
|----------|-------|----------|-------|
| CLEAR archive candidates | 8 | 2 | **10** |
| CONDITIONAL archive candidates | 8 | 2 | **10** |
| UNCERTAIN / user decision required | 3 | 0 | **3** |
| ACTIVE_KEEP (must not archive) | 41 | 26 | **67** |
| HISTORICAL_KEEP (keep in place) | 3 | 5 | **8** |

No files were moved in this task. This is a planning and classification
document only. The manifest is in
`Results/JMP_docs_results_cleanup_second_pass_manifest_v1.csv`.

---

## 2. Files inspected

**docs/ — all `.md` files:** 97 files scanned (excluding `docs/archive/`
and `docs/ACKNOWLEDGEMENTS.md`). Of these, ~90 remain after first-pass
archiving.

**Results/ — all `.md` files:** 57 files scanned (excluding
`Results/archive/`). Of these, ~55 remain after first-pass archiving.

Key files read in full for classification:

- All correction and fix documents in the GSURv2 multi-year chain
  (remediation authorization correction, final wording fix, construction
  authorization correction, script remediation documentation fix,
  provenance lock plan correction)
- Multi-year strategy memo v3 and v3.1 (revision histories)
- Stage M1 execution readiness reports v1 and v2 (supersession explicit)
- Single-year command plans v1, v2, and addendum
- GSURv2 implementation audit and addendum
- Stage M1 P3a full execution report and addendum
- M1 identity validation summary
- Sample construction descriptives report and correction
- All three GSUR acquisition chain documents (acquisition report,
  adversarial verification, O2 resolution, O7 sign-off request,
  O7 sign-off, Stage A authorization, open decisions resolution)
- M0c_b2 and M0c_b2_GSURv2 verdict documents
- M1-clean verdict and all cited diagnostics documents

---

## 3. Clear archive candidates

These 10 files are recommended for immediate archiving without any user
decision. All corrections have been applied in-place to their parent
documents; parent documents are the live authoritative versions.

### docs/ — 8 files

| File | Category | Why archivable |
|------|----------|----------------|
| `JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md` | CORRECTION_INCORPORATED | C1–C12 applied to parent; parent is live |
| `JMP_GSURv2_multi_year_extension_remediation_authorization_final_wording_fix_v1.md` | CORRECTION_INCORPORATED | F1–F3 applied to parent; second-layer fix; parent is live |
| `JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md` | CORRECTION_INCORPORATED | F1–F2 applied to parent; parent is live |
| `JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md` | CORRECTION_INCORPORATED | Heading and scope corrections applied to parent; parent is live |
| `JMP_GSURv2_script_remediation_documentation_fix_v1.md` | CORRECTION_INCORPORATED | F1–F2 applied to two parent docs; both parents are live |
| `JMP_multi_year_sample_construction_descriptives_correction_report_v1.md` | CORRECTION_INCORPORATED | C1–C4 applied to parent; parent is live |
| `JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | CLEAR_SUPERSEDED | v2 explicitly states "Supersedes v1"; v1 = NOT AUTHORIZED; v2 = READY |
| `JMP_single_year_replication_2015_2017_command_plan_v1.md` | CLEAR_SUPERSEDED | v2 explicitly states "Supersedes v1"; CLI flags corrected |

### Results/ — 2 files

| File | Category | Why archivable |
|------|----------|----------------|
| `M1_identity_validation_summary.md` | ADDENDUM_INCORPORATED | Low-level output captured verbatim in `full_execution_report_v1.md` §13 |
| `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md` | ADDENDUM_INCORPORATED | Corrections to §30 and welfare authorization status fully captured in `P3a_construction_verdict_v1.md`; construction verdict is the accepted synthesizing document |

---

## 4. Conditional archive candidates

These 10 files are archivable on substantive grounds but carry a secondary
reference or provenance consideration. They are recommended for archiving
but a user confirmation is appropriate.

### docs/ — 8 conditional files

| File | Reason for conditional status |
|------|-------------------------------|
| `JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | Prerequisites now satisfied; addendum cited in remediation authorization header. Archiving removes a one-hop reference but the remediation authorization is self-contained |
| `JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` | GSUR keying correction incorporated into executed rebuild reports; command plan v2 + addendum together form the authoritative command; archiving addendum leaves v2 alone, which is sufficient |
| `RURO_GSUR_O7_crosswalk_signoff_request_v1.md` | Request satisfied by sign-off; no decision content; pure process overhead |
| `RURO_GSUR_external_acquisition_completion_v1.md` | PARTIAL ACQUISITION SUCCESS; fully resolved by O2 resolution + Stage A authorization; historical provenance only |
| `RURO_GSUR_O2_denominator_resolution_v1.md` | O2 findings incorporated into open-decisions resolution memo as binding amendment |
| `RURO_GSUR_external_acquisition_report_v1.md` | *See §7 — user decision required* |
| `RURO_GSUR_external_acquisition_verification_claude_v1.md` | *See §7 — user decision required* |
| `RURO_GSUR_O7_crosswalk_signoff_v1.md` | *See §7 — user decision required* |

### Results/ — 2 conditional files

| File | Reason for conditional status |
|------|-------------------------------|
| `JMP_multi_year_stage_M1_static_validation_report_v3.md` | Final surviving document in the v1→v2→v3 chain; v1 and v2 archived in first pass; v3 is canonical for generalization validation. Its status is captured in the full execution report, but archiving it removes the only dedicated generalization validation document |
| `JMP_multi_year_stage_M1_execution_readiness_v1.md` | Dry-run NOT FOUND output; its referencing parent (readiness report v1) was archived in first pass; operationally superseded by full execution |

---

## 5. Active files kept

67 files classified ACTIVE_KEEP. These include:

- All 22 required next-gate files from §3 of the plan.
- All GSURv2 multi-year extension chain documents: design memo, implementation
  audit, readiness re-audit, remediation authorization, construction
  authorization, construction report, construction verdict (+ correction).
- All MNL rebuild chain documents: authorization (+ correction), verdict
  (+ correction), rebuild report v2, correction report.
- All Stage M1 construction chain documents: implementation plan v2,
  implementation report, generalization report + fix, execution readiness
  v2, readiness addendum v2, static validation report v3 (see §4 for
  conditional note), full execution report, P3a construction verdict.
- All single-year rebuild and replication execution records (FR_2015,
  FR_2016, FR_2017) and the consolidated readiness verdict.
- All M1-clean and M1-naive estimation records (gate A, estimation,
  diagnostics, verdict, design memo, implementation audit, YAML reports).
- All M0c_b2 and M0c_b2_GSURv2 evidence chain documents.
- All GSURv2 external-file remediation, static validation, and multi-year
  extension validation records.
- RURO_GSUR Stage A authorization chain (StageA_authorization,
  open_decisions_resolution, local_O1_evidence_audit, v2_stageA_
  implementation_report, GSUR_SOURCE_AND_MERGE_AUDIT).
- Welfare: measurement decisions v2, scaffolding design v2.
- Strategy: multi-year strategy memo v3 and v3.1.
- Operational references: GSUR specification v2_1, acquisition decision v2,
  year alignment decision, RURO_GSUR_DATA_AND_MERGE_NOTE, prep_mnl_gsur_
  year_support_report, CPI decision.

---

## 6. Historical files kept

These 8 files are kept in their current locations as accessible historical
references, not archived:

| File | Reason to keep in place |
|------|-------------------------|
| `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3.md` | v3 and v3.1 form a complete revision trail; both cited in downstream documents |
| `docs/France_case/_shared/data_audits/RURO_FR2016_CONTINUOUS_DATA_BUILD_AUDIT_v1.md` | Comprehensive 2016 data build audit; referenced by M1-clean implementation audit |
| `docs/RURO_GSUR_external_acquisition_report_v1.md` | Pending user decision (§7); treated as KEEP until decision |
| `Results/JMP_multi_year_stage_M1_static_validation_report_v3.md` | Canonical surviving document in v1→v2→v3 chain; only dedicated generalization validation record |
| `Results/JMP_multi_year_EUROMOD_output_readiness_v1.md` | Pre-Stage-M1 EUROMOD readiness; documents FR_2015/FR_2017 absence state |
| `Results/JMP_multi_year_external_assets_inventory_v1.md` | Pre-remediation external assets gap state; not superseded by a v2 |
| `Results/JMP_multi_year_single_year_MNL_readiness_v1.md` | Pre-rebuild MNL readiness (NOT READY); documents pre-rebuild state |
| `Results/JMP_multi_year_stage_M1_execution_readiness_v1.md` | Dry-run NOT FOUND point-in-time record |

---

## 7. Uncertain files requiring user decision

Three files cannot be classified without a user decision:

**Decision A — Is the M0c_b2_GSURv2 evidence chain still active?**

`docs/RURO_GSUR_O7_crosswalk_signoff_v1.md` is the single-year O7
sign-off approving the un-tagged `FR_gsur_ruro_v2_stageA.parquet` and
the `(drgn1, educ3, sex)` merge key for single-year GSURv2 MNL writes.
It is cited by `RURO_occ_M0c_b2_GSURv2_verdict_v1.md`.

- If the M0c_b2_GSURv2 estimation chain is still considered part of the
  active evidence record (i.e., its results will be cited or compared in
  the paper): **KEEP** this sign-off.
- If M0c_b2_GSURv2 is considered a historical stepping stone only and the
  M1-clean 2016 verdict is the sole active single-year baseline: **ARCHIVE**
  this sign-off (the multi-year O7 `JMP_GSURv2_O7_crosswalk_signoff_v1.md`
  supersedes it for all current work).

**Decision B — Acquisition report: archive or keep in docs/?**

`docs/RURO_GSUR_external_acquisition_report_v1.md` contains the initial
O1/O2/O9 source identification analysis. Its O1 reasoning had factual errors
corrected by the adversarial verification. The O2 and O9 source identification
reasoning is not reproduced in detail in later documents.

- If the acquisition provenance trail is considered complete via the
  authorization chain: **ARCHIVE** to `HISTORICAL_KEEP` in archive.
- If the O2/O9 source-path reasoning may need re-examination during paper
  revision: **KEEP** in `docs/`.

**Decision C — Adversarial verification: archive or keep in docs/?**

`docs/RURO_GSUR_external_acquisition_verification_claude_v1.md` corrected
factual errors in the acquisition report and informed the open-decisions
resolution. It is not in the authorization chain.

- If the O1/O2/O9 source identification is considered settled: **ARCHIVE**
  to `HISTORICAL_KEEP` in archive.
- If re-auditing the external data sources is a plausible future task:
  **KEEP** in `docs/`.

---

## 8. Risks

| Risk | Mitigation |
|------|-----------|
| Correction memo archived before the parent document is confirmed as the live version | All corrections in the CLEAR list were verified to have been applied in-place to the parent before this audit. Parent documents are confirmed live (read and checked in this session) |
| `JMP_multi_year_stage_M1_P3a_full_execution_addendum_v1.md` archived but its corrections not fully reflected in a kept document | The construction verdict (`P3a_construction_verdict_v1.md`) explicitly incorporates the addendum's findings in §§3–5 of the verdict. The full execution report itself (kept) is the primary execution record |
| `JMP_multi_year_stage_M1_execution_readiness_report_v1.md` archived while still cited somewhere | The only document that cited v1 as authoritative was the execution itself; v2 is now the authoritative readiness record |
| `M1_identity_validation_summary.md` archived but the validation result is needed | The validation data is reproduced in full execution report §13; identity-validation PASS is also recorded in the construction verdict §4 |
| Conditional candidates archived before user decisions received | Conditional candidates are NOT moved in this task. The plan document records them; execution awaits a separate authorization |
| Stacking re-run authorization memo requires reference to a file later archived | All 22 required next-gate files (§3) are classified ACTIVE_KEEP and are not touched in either the clear or conditional archive lists |

---

## 9. What was not executed

- No files were moved.
- No files were deleted.
- No parquet, sidecar, script, YAML, HTML, or PNG file was touched.
- No estimation was run.
- No welfare computation was performed.
- No pipeline step was executed.
- `docs/archive/` pre-existing contents were not modified.
- `docs/ACKNOWLEDGEMENTS.md` was not modified.

---

## 10. Exact next task

**Immediate next authorized task (no user decision needed):**

Execute the 10 CLEAR archive candidates listed in §3 via `git mv` and
commit with message `cleanup(docs/Results): second-pass archive — correction and addendum memos incorporated`.

**After user decisions on §7 (three decisions):**

Execute up to 10 additional CONDITIONAL archive candidates in a second commit.
The three decisions in §7 can be deferred without blocking the stacking
re-run authorization memo, which is the active next gate.

**The active next gate remains unchanged:**

Writing the Stage M1 P3a GSURv2 stacking re-run authorization memo, as
stated in `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_v1.md` (corrected by
`docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md`). The second-pass
cleanup does not change this status.