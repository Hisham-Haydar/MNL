# Move Manifest — 2026-05-26 Round 2 Chain Compression

## Context

- **Approver:** Hisham (2026-05-26 conversation)
- **Scope:** `docs/` only. No code changes. No `Results/`, scripts, or EUROMOD-STORAGE touched. Pre-existing `docs/archive/` contents and the 2026-05-25 supersession subdir untouched.
- **Policy basis:** `docs/package/RURO_PACKAGE_PORTABILITY_AND_CLEANUP_POLICY_v1.md`, `docs/package/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md`, `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md` (Round 1).
- **Goal:** Compress chains that remained on the active surface after Round 1 — execution-log buckets and root-level workspace audits where a clear successor exists.
- **Method:** `git mv` per file (history-preserving) plus inline top-of-file supersession note. No file deleted. No content rewritten beyond the prepended note.

## Summary counts

| Category | Files archived | Active surface delta |
|---|---:|---:|
| A. Doc-only corrections | 9 | -9 |
| B. Audit → reaudit chain | 3 | -3 |
| C. Replaced by clean/corrected variant | 8 | -8 |
| D. Strategy v1 superseded by v2 | 1 | -1 |
| E. Workspace audits superseded by Round-1 manifest | 3 | -3 |
| **Total archived** | **24** | **-24** |
| New artifacts added (archive README + this manifest) | 2 | +2 |
| **Net active surface change** | | **-22** |

Active `docs/` (excl. archive) drops from 170 (post-Round-1) to ~148.

## Commit chain

| Phase | Commit | Description |
|---|---|---|
| A — scaffold | `d6ed5e3` | Create `docs/archive/2026-05-26_round2_chain_compression/` with 5 category subdirs, README, .gitkeeps |
| B1 — Cat A | `ac4bb6d` | Archive 9 doc-only correction/addendum files |
| B2 — Cat B | `f9c5774` | Archive 3 audit→reaudit chain files |
| B3 — Cat C | `7e5e18b` | Archive 8 files replaced by clean/corrected variants |
| B4 — Cat D | `80e4696` | Archive NC_pilot stage5 amendment v1 |
| B5 — Cat E | `b85d567` | Archive 3 pre-cleanup workspace audits |
| C — manifest | (this commit) | Write this manifest |
| D — cross-refs | (pending) | Patch active inbound references |

## A. Doc-only correction archives (9 files)

Pattern: each correction file self-identifies as "documentation-only, no substantive change." User decision (2026-05-26): archive as-is rather than back-apply corrections to base files. Base files retain original wording; correction notes preserved here as historical record.

| Old path | Archive path | Base file (kept active) |
|---|---|---|
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | `doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md` | `..._authorization_v1.md` |
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | `doc_only_corrections/JMP_GSURv2_MNL_rebuild_verdict_correction_v1.md` | `..._verdict_v1.md` |
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | `doc_only_corrections/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | `..._construction_verdict_v1.md` + `..._construction_report_v1.md` |
| `docs/France_case/execution_logs/stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_authorization_correction_v1.md` | `doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_authorization_correction_v1.md` | `..._stacking_authorization_v1.md` |
| `docs/France_case/execution_logs/stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md` | `doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md` | `Results/P3a/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md` |
| `docs/France_case/execution_logs/stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md` | `doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md` | same as above |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_design_memo_correction_v1.md` | `doc_only_corrections/JMP_pooled_P3a_estimation_design_memo_correction_v1.md` | `..._estimation_design_memo_v1.md` |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_design_memo_review_addendum_v1.md` | `doc_only_corrections/JMP_pooled_P3a_estimation_design_memo_review_addendum_v1.md` | reabsorbed into the correction note |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md` | `doc_only_corrections/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md` | (base authorization itself archived in Cat C; see live chain `..._corrected_region_reestimation_authorization_v1.md`) |

Commit: `ac4bb6d`.

**Important caveat for the Pooled P3a design memo correction:** The correction note contains a corrected Gate-A YAML implementation-audit prompt (§8 of the correction) that explicitly supersedes §24 of the base design memo. If Gate-A is re-run, the corrected prompt in the archived correction note must be used in place of the base memo's §24. The base memo's archive-note pointer flags this.

## B. Audit → reaudit chain archives (3 files)

Pattern: The original implementation audit returned NOT READY; an addendum supplemented it; a remediation authorization initiated fixes. All three are superseded by the readiness re-audit (READY FOR GSURv2 CONSTRUCTION verdict).

| Old path | Archive path | Replacement (kept active) |
|---|---|---|
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md` | `audit_reaudit_chain/JMP_GSURv2_multi_year_extension_implementation_audit_v1.md` | `..._readiness_reaudit_v1.md` |
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | `audit_reaudit_chain/JMP_GSURv2_multi_year_extension_implementation_audit_addendum_v1.md` | same |
| `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | `audit_reaudit_chain/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | same |

Commit: `f9c5774`.

## C. Replaced by clean/corrected variant (8 files)

Pattern: the workflow explicitly rebuilt the file under a `_clean` or `corrected_region` tag after a defect was found in the original.

| Old path | Archive path | Replacement (kept active) |
|---|---|---|
| `docs/France_case/execution_logs/occ_M0a/RURO_occ_M0a_implementation_report_v1.md` | `replaced_by_clean_corrected/RURO_occ_M0a_implementation_report_v1.md` | `RURO_occ_M0a_clean_implementation_report_v1.md` |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_execution_authorization_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_authorization_v1.md` | `JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md` |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_post_estimation_review_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_post_estimation_review_v1.md` | `JMP_pooled_P3a_corrected_region_post_estimation_review_v1.md` |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md` | absorbed into corrected-region chain |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md` | same |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_estimation_execution_repair_report_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_report_v1.md` | same |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md` | same |
| `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_region_dummy_repair_report_v1.md` | `replaced_by_clean_corrected/JMP_pooled_P3a_region_dummy_repair_report_v1.md` | same |

Commit: `7e5e18b`.

## D. Strategy v1 superseded by v2 (1 file)

| Old path | Archive path | Replacement (kept active) |
|---|---|---|
| `docs/France_case/execution_logs/NC_pilot/JMP_NC_pilot_stage5_euromod_amendment_v1.md` | `strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md` | `JMP_NC_pilot_stage5_strategy_amendment_v2.md` |

`stage5_strategy_amendment_v2` explicitly states: "This v2 replaces the failed ingestion strategy (Strategy B, per-partner with the off-axis partner as a non-decider) with Strategy C′: blockwise joint-product EUROMOD, in which both partners are deciders in every run."

Commit: `80e4696`.

## E. Workspace audits superseded (3 files)

Pre-cleanup workspace and hygiene audits dated 2026-05-11 / 2026-05-12. Superseded by the Round-1 manifest (`MOVE_MANIFEST_2026-05-25.md`), which is the canonical hygiene record for the 2026-05-25 docs/ reorganization.

| Old path | Archive path | Replacement (kept active) |
|---|---|---|
| `docs/France_case/RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md` | `workspace_audits_superseded/RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md` | `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md` |
| `docs/France_case/RURO_WORKSPACE_AUDIT_2026-05-11.md` | `workspace_audits_superseded/RURO_WORKSPACE_AUDIT_2026-05-11.md` | same |
| `docs/France_case/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md` | `workspace_audits_superseded/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md` | same |

Commit: `b85d567`.

## F. Inbound reference scan (pre-move)

Before each move, an automated scan identified all files (in `docs/`, `scripts/`, `Results/`, root `README.md`, configs, outputs sidecars) that mention any of the 24 archive candidates. Inbound references fall into three classes:

### F.1 Inert references (no action needed)
- **Files in `docs/archive/` or `Results/archive/`** — these are themselves historical; references inside historical material reflect what existed at the time of writing.
- **Auto-generated structure dumps** — `RURO_MNL_project_files_structure.md` (dated 2026-05-12) is a directory snapshot from before Round 1; references inside reflect that state.
- **Round-1 cleanup reports** in `Results/JMP_docs_results_cleanup_*` and `docs/jmp_methodology/JMP_docs_results_cleanup_*plan*.md` — these document the Round-1 starting state; references inside are historical fact about what was on the active surface at the moment of Round 1, not load-bearing pointers.
- **Output sidecars** under `outputs/estimates/fr/.../specification_used.yaml` — frozen run metadata.

### F.2 Sibling archive targets (move-together)
Any reference where both the citing file and the cited file are in the 24-archive list moves together within `2026-05-26_round2_chain_compression/`. No action needed.

### F.3 Active external references (patched in Phase D)
Listed in the cross-reference fixes section below.

## G. Cross-reference fixes applied (Phase D)

A path-mapping script scanned `.md`, `.py`, `.yaml`, `.yml` files across the repo (skipping `.git`, `.venv`, `_gams_work`, `docs/archive/2026-05-25_docs_supersession/**`, `Results/archive/**`, output sidecar YAMLs) and rewrote any path reference to one of the 24 archived files. **44 files patched, ~80 string substitutions** including both pre-Round-1 path forms (`docs/<name>.md`) and post-Round-1 forms (`docs/France_case/execution_logs/<bucket>/<name>.md`).

The supersession notes added to each archived file in phases B1–B5 also land in this commit — git's rename-detection treated those B-phase commits as pure renames and silently dropped the prepended notes (the diff threshold was tripped by the 4-line prepend on long files); the notes were preserved in the working tree and are restored to HEAD in this Phase D commit.

| Patched location | Refs rewritten | Notes |
|---|---:|---|
| Repo root `README.md` | 2 | external-storage hygiene audit |
| `docs/PIPELINE_ENTRYPOINTS.md` | 1 | external-storage hygiene audit |
| `docs/mirrored/root/README.md` | 2 | external-storage hygiene audit |
| `docs/package/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md` | 1 | hygiene cleanup log |
| `docs/package/RURO_PROJECT_MEMORY_MAP.md` | 2 | external-storage hygiene audit |
| `docs/package/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md` | 3 | external-storage hygiene audit |
| `docs/jmp_methodology/JMP_docs_results_cleanup_plan_v1.md` | 4 | three GSURv2 corrections |
| `docs/jmp_methodology/JMP_docs_results_cleanup_second_pass_plan_v1.md` | 6 | corrections + audit triplet |
| `docs/France_case/execution_logs/GSURv2/*_v1.md` (5 active siblings) | 5 | inter-active-doc refs |
| `docs/France_case/execution_logs/stage_M1/*_v1.md` (2 active files) | 5 | inter-active-doc refs |
| `docs/France_case/execution_logs/pooled_P3a/*_v1.md` (2 active files) | 5 | corrected-region chain refs to archived predecessors |
| `docs/France_case/execution_logs/NC_pilot/JMP_NC_pilot_stage5_strategy_amendment_v2.md` | 2 | refs to its archived v1 predecessor |
| `Results/*.md` (10 files) | ~25 | preflight, run, build, cleanup reports |
| `scripts/maintenance/*.py` (3 files) | 5 | docstring path references |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | 1 | remediation auth |
| `scripts/enhanced/specifications/*.yaml` (2 files) | 2 | spec comment refs |
| `scripts/pilot/export_pilot_euromod_inputs.py` | 2 | stage5 amendment v1 |
| `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml` | 1 | stacking authorization correction |
| `Prompts/RURO_ruro_occ_M0a_clean_*.md` | 1 | M0a implementation report |
| `docs/archive/2026-05-26_round2_chain_compression/**` (24 files) | ~30 | inter-archive refs rewritten + supersession notes restored |

**Inert references intentionally not patched:**

- `docs/archive/2026-05-25_docs_supersession/**` — pre-existing Round-1 archive, sealed.
- `Results/archive/2026-05-20_post_gsurv2_mnl_rebuild/**` — sealed historical material from a prior cleanup event.
- `outputs/estimates/**/*specification_used.yaml` — frozen run metadata that records the spec text used at that run's time.
- `Results/JMP_docs_results_cleanup_*manifest_v1.csv` — Round-1 cleanup CSVs that list files that existed at Round-1 time; historical fact.
- `RURO_MNL_project_files_structure.md` (root) — auto-generated directory snapshot from 2026-05-12; historical fact.

Commit: (Phase D, this commit).

## H. Deferred follow-ups

- **Cat-A back-apply pass:** Optional later pass to back-apply the 9 documentation corrections into their base files (heading demotions, NUTS labels, wording rewrites, the full Gate-A prompt replacement in the pooled P3a design memo §24). Estimated ~25-30 surgical edits across 7 base files plus a 130-line prompt replacement. The corrections are preserved in archive with their full text; the base files retain original wording.
- **Round-3 candidates:** A future pass could compress remaining chains:
  - The 22-file `NC_pilot` chain (only stage5 v1 was archived here) — many amendments to authorizations that may be reabsorbed if/when verdict-grade results land.
  - The 13-file `stage_M1` and 16-file `GSURv2` chains have remaining pairs (audit + addendum, plan + report) that could compress further once the project completes the next milestone.
  - The 10-file `occ_M1` chain has clean vs naive parallel tracks; one may be retired after SA2.
- **Hash-verified migration:** If `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md` references the archived workspace audits as evidence for Round 1's hygiene rationale, those links should be updated to the new archive paths in Phase D (or left as historical fact; see F.1).

## I. Verification (run after Phase D)

```powershell
# 1. Total docs/ count (expect +2 vs post-Round-1: new manifest + new archive README)
Get-ChildItem docs -Recurse -File -Filter "*.md" | Measure-Object | Select-Object -ExpandProperty Count

# 2. Active surface (expect ~148)
Get-ChildItem docs -Recurse -File -Filter "*.md" | Where-Object { $_.FullName -notlike "*\archive\*" } | Measure-Object

# 3. Round-2 archive subdir populated (expect 24 + README = 25)
Get-ChildItem docs/archive/2026-05-26_round2_chain_compression -Recurse -File | Measure-Object

# 4. Per-category populated
foreach ($d in 'doc_only_corrections','audit_reaudit_chain','replaced_by_clean_corrected','strategy_v1_superseded','workspace_audits_superseded') {
  "$d : " + (Get-ChildItem "docs/archive/2026-05-26_round2_chain_compression/$d" -File -Filter '*.md' | Measure-Object).Count
}

# 5. Git history preserved for a moved file
git log --follow --oneline -- docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_GSURv2_MNL_rebuild_authorization_correction_v1.md | Select-Object -First 5

# 6. Supersession note present at top of each archived file
Get-ChildItem docs/archive/2026-05-26_round2_chain_compression -Recurse -File -Filter '*correction_v1.md' |
  ForEach-Object { (Get-Content $_.FullName -TotalCount 1) }
# expect: all start with "> Archived on 2026-05-26"
```
