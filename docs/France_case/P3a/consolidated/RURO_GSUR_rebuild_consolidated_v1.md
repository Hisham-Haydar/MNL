# RURO GSUR Rebuild — Consolidated v1

**Consolidation date:** 2026-05-25
**Scope:** France case (EUROMOD FR 2016 → GSUR v2 rebuild — Stage A authorization, implementation, and per-decision resolutions)
**Authoring rule:** structural merge of six pre-existing memos. No content rewritten in this pass.

> **Standalone document kept separate (not merged):** `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md` is the governing specification and remains untouched. This consolidation covers the decision/authorization/sign-off chain *around* that spec.

---

## 1. Sources merged

All six sources are archived at `docs/archive/2026-05-25_docs_supersession/merged_sources/gsur_rebuild/`. Their original location was `docs/`.

| Original filename | Date | Role |
|---|---|---|
| `RURO_GSUR_StageA_authorization_v1.md` | — | Stage A authorization memo — formal go/no-go for the v2 rebuild's Stage A. |
| `RURO_GSUR_v2_stageA_implementation_report_v1.md` | — | Stage A implementation report — what was actually built, against the authorization. |
| `RURO_GSUR_O2_denominator_resolution_v1.md` | — | Per-decision resolution memo for O2 (denominator choice and fallback handling). |
| `RURO_GSUR_O7_crosswalk_signoff_request_v1.md` | — | Sign-off request for the O1/O7 crosswalk file before its merge into MNL parquets. |
| `RURO_GSUR_O7_crosswalk_signoff_v1.md` | — | Sign-off decision (response to the above request). |
| `RURO_GSUR_v2_1_open_decisions_resolution_v1.md` | — | Resolution of all open decisions standing against the v2.1 spec at the time. |

## 2. Chain logic

The six memos collectively turn the v2.1 specification (kept standalone) into an executable build:

1. **Open decisions resolution** clears the spec-level ambiguities for the v2.1 build.
2. **O2 denominator resolution** decides primary vs fallback paths cell-by-cell.
3. **O7 crosswalk sign-off request → sign-off** completes the gated approval before the crosswalk file is merged into MNL parquets.
4. **Stage A authorization** is granted on the basis of items 1–3.
5. **Stage A implementation report** records what was built against the authorization.

The **v2.1 spec is the authoritative methodology document**; the **Stage A implementation report is the authoritative reference for what currently exists in code and data**; the **O7 sign-off is the authoritative gate for the crosswalk file**; this consolidated doc is the entry point.

## 3. Pointers (per-source)

For substantive content, read the archived source. Each archived file has a top-of-file note pointing back here and to the manifest.

- O2 denominator choices, suppression handling, fallback rationale → `gsur_rebuild/RURO_GSUR_O2_denominator_resolution_v1.md`.
- Crosswalk file schema and cell-by-cell sign-off content → `gsur_rebuild/RURO_GSUR_O7_crosswalk_signoff_v1.md`.
- Stage A built artifacts (parquets, scripts, validation outputs) → `gsur_rebuild/RURO_GSUR_v2_stageA_implementation_report_v1.md`.
- Open decision resolutions (one per O3, O5, O6, O8, O10, etc.) → `gsur_rebuild/RURO_GSUR_v2_1_open_decisions_resolution_v1.md`.

## 4. Relationship to other consolidations

- The **external acquisition chain** (decision_v2 / report / verification / completion) is consolidated separately at `docs/France_case/consolidated/RURO_GSUR_external_acquisition_consolidated_v1.md`. That chain identifies and acquires the external assets (NUTS workbook, Eurostat extracts, INSEE benchmark) that this rebuild chain consumes.
- The **v2.1 specification** itself is the upstream governing document and is kept standalone at `docs/France_case/RURO_GSUR_rebuild_specification_v2_1.md`.

## 5. Open items

- Authorial pass: rewrite this consolidation into a single coherent narrative (out of scope for the 2026-05-25 reorganization).
- Confirm whether any Stage B authorization / implementation chain emerges; if so, consolidate similarly into `..._stageB_consolidated_v1.md`.

## 6. Manifest reference

See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md` for source paths, archive paths, and commit SHAs.
