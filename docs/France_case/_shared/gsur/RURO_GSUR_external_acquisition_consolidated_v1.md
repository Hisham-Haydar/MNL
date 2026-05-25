# RURO GSUR External Acquisition — Consolidated v1

**Consolidation date:** 2026-05-25
**Scope:** France case (EUROMOD FR 2016 → GSUR build, external assets for O1 / O2 / O9)
**Authoring rule for this doc:** structural merge of the four pre-existing memos listed in §1. No content has been rewritten or synthesized in this pass; section §2 — §6 of the canonical chain are pointers into the archived sources, not paraphrases. Extracting country-agnostic prose is a separate authorial pass (see manifest "Deferred follow-ups").

---

## 1. Sources merged

All four sources are archived at `docs/archive/2026-05-25_docs_supersession/merged_sources/gsur_external_acquisition/`. Their original location was `docs/`.

| Original filename | Date | Role in chain |
|---|---|---|
| `RURO_GSUR_external_acquisition_report_v1.md` | 2026-05-17 | ChatGPT Deep Research acquisition report — first identification of official sources for O1, O2, O9. Recommended verdict: "acquisition-ready, but not yet execution-ready." |
| `RURO_GSUR_external_acquisition_verification_claude_v1.md` | 2026-05-17 | Claude adversarial verification of the above. Confirms the file-level identifications, flags four factual corrections (NUTS-2 not realigned in 2021; `lfst_r_lfu3pers` has no duration dim; Eurostat `FR` includes the four DOM, not métropole; EUROMOD `drgn1` codebook not publicly documented). |
| `RURO_GSUR_external_acquisition_decision_v2.md` | 2026-05-17 | Final binding decision memo. Reconciles the report, verification, and local `RURO_GSUR_local_O1_evidence_audit_v1.md` (NOT archived — see §5). Adopts the conservative-interpretation rule. Authoritative resolutions for O1, O2, O3, O5, O7, O8, O9, O10. Status: acquisition-ready, implementation NOT authorized; three external files must be acquired first. |
| `RURO_GSUR_external_acquisition_completion_v1.md` | 2026-05-17 | Outcome of the acquisition task. **PARTIAL ACQUISITION SUCCESS.** O1 and O9 resolved; O2 remains unresolved (Eurostat suppression at the four-dimensional cross-tab forced a fallback decision still pending). Stage A implementation remains NOT authorized. |

## 2. Canonical chain (chronological)

1. **Report** (ChatGPT Deep Research) identifies official sources at the file level.
2. **Verification** (Claude adversarial) confirms file identifications, lists four factual corrections.
3. **Decision v2** reconciles report + verification + local O1 audit into a binding methodology and a three-file acquisition list.
4. **Completion** records the outcome of the acquisition task.

The **decision v2 memo is the authoritative reference for methodology**; the **completion memo is the authoritative reference for current asset status.** Read them in that order if you need detail.

## 3. What is resolved

- **O1 crosswalk methodology:** EUROMOD `drgn1` → old NUTS-2 (via local DRD) → new NUTS 2016 letter codes (via Eurostat `NUTS2013-NUTS2016.xlsx`) → GSUR row (via `FR_gsur_full.csv`). See decision_v2 §5.
- **O2 denominator methodology:** Primary `lfst_r_lfp2acedu`; fallback A `lfst_r_lfsd2pop` (same 4-D grid, clean substitute); fallback B approximate-uniform; unaggregatable cells flagged for v2.1 schema clarification. See decision_v2 §7–§8.
- **O9 benchmark methodology:** INSEE BDM série `001688526` (Taux de chômage BIT — France métropolitaine — CVS, annual average of 2016 quarters). NOT Eurostat `FR` (which includes DOM). See decision_v2 §9.
- **Sample perimeter:** metropolitan France only, confirmed by three independent paths (MNL parquet evidence, raw EUROMOD input evidence, DRD-documented derivation). See decision_v2 §10.
- **O3, O5, O7, O8, O10:** locally resolved per decision_v2 §14.

## 4. What is unresolved

Per completion_v1 §1:
- **O2 cell-suppression status** at the four-dimensional cross-tab is non-trivial; the fallback path is methodologically defined but cell-by-cell resolution and the choice between primary/fallback-A is still pending file inspection.
- **Stage A implementation remains NOT authorized** until O2 is fully cleared.

## 5. Files referenced but NOT in this merge

- `RURO_GSUR_local_O1_evidence_audit_v1.md` — referenced as an input by decision_v2 but kept as a standalone audit doc under `docs/France_case/` (it is empirical evidence specific to the local DRD inspection, not a decision memo in the same chain).
- `RURO_GSUR_rebuild_specification_v2_1.md` — the governing specification, kept standalone at `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md`. This consolidation does not replace it.

## 6. Open items

- Resolve O2 cell suppression (download `lfst_r_lfp2acedu` extract, run inventory, decide per-cell between primary and fallback A).
- If unaggregatable cells exist, issue v2.1 schema clarification for `gsur_weighting_source` (decision_v2 §8 F4).
- Authoritative authorial pass: rewrite this consolidation as a single coherent narrative (out of scope for the 2026-05-25 reorganization).

## 7. Manifest reference

See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md` for source paths, archive paths, and commit SHAs.
