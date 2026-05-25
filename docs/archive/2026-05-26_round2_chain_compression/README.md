# 2026-05-26 Round 2 — Chain Compression Archive

This subdirectory holds files archived in the second cleanup pass on 2026-05-26.

## Scope

Round 1 (2026-05-25) reorganized the `docs/` tree into package-topical subfolders plus a `France_case/` empirical case (see `docs/archive/2026-05-25_docs_supersession/`). Round 2 compresses the chains that remained on the active surface after that pass — execution-log buckets in `France_case/execution_logs/` and workspace audits at `France_case/` root that have since been superseded.

## What's archived here

24 files across five categories:

- **`doc_only_corrections/`** (9 files) — `*_correction_v1` and `*_addendum_v1` files that self-identify as "documentation-only, no substantive change to the base file." Each base file remains active and authoritative for its substantive content; the correction note is preserved here as historical record.
- **`audit_reaudit_chain/`** (3 files) — The original implementation audit, its addendum, and the remediation authorization for the GSURv2 multi-year extension. All three are superseded by the readiness reaudit, which resolved the NOT READY verdict to READY.
- **`replaced_by_clean_corrected/`** (8 files) — Earlier versions of files that the workflow explicitly rebuilt under a `_clean` or `corrected_region` tag. Includes the M0a original (replaced by M0a-clean) and the pooled-P3a pre-repair chain (replaced by the corrected-region chain).
- **`strategy_v1_superseded/`** (1 file) — NC pilot Stage 5 EUROMOD amendment v1 (per-partner Strategy B), explicitly superseded by `stage5_strategy_amendment_v2` (Strategy C′: blockwise joint-product EUROMOD).
- **`workspace_audits_superseded/`** (3 files) — Pre-cleanup workspace and hygiene audits dated 2026-05-11 / 2026-05-12. Superseded by the Round-1 manifest, which is the canonical record of the 2026-05-25 cleanup event.

## Manifest

Full per-file provenance with old paths, new paths, supersession rationale, and commit SHAs: `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

## Policy

No file was deleted. Each archived file carries an inline top-of-file note pointing to the canonical replacement and to the manifest. Pre-existing archive contents are unchanged. This pass adds only this dated subdirectory.
