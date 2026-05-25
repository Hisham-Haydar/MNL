# JMP GSURv2 Multi-Year Extension Construction Authorization — Correction v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Purpose

This document records a narrow structural and scope correction applied
to `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`.
Two issues were identified after the authorization was drafted: (a) the
memo contained a 21st heading (`## Required final statements`) that
was not listed among the 20 required section headings, and (b) the memo
authorized post-construction cleanup actions — retiring the un-tagged
y2016 parquet, running `git mv`, updating canary and validation scripts,
and migrating references — that are separately gated and should not
appear as construction-step authorizations.

No code was changed. No script was run. No parquet was written.
The core Option B construction authorization is unchanged.

---

## 2. Issue corrected

Two issues are corrected by this document.

**Issue 1 — Extra heading (structural).** The memo had 20 numbered
sections (§1–§20) followed by a 21st heading `## Required final
statements`. The memo's own introduction (§1) specifies exactly 20
sections; the 21st heading was inconsistent with that specification
and rendered the `## Required final statements` block as an
unintended section rather than a closing statement under §20.

**Issue 2 — Scope creep (authorization boundary).** Several passages
in the memo authorized post-construction cleanup actions as part of
the construction:

- Retiring the existing un-tagged y2016 lookup
  (`FR_gsur_ruro_v2_stageA.parquet`) to `Data/external/archive/` via
  `git mv`.
- Updating references to the un-tagged path in the canary and
  validation scripts to the year-tagged y2016 path.

These actions appear in the memo in at least seven locations: §4
(scope paragraph), §8 (y2014 terminal step), §10 Step 8 (the
executor prompt), §11 (required output files), §15 A7 and A8
(authorized actions list and closing sentence), §19 R5 (construction
report requirements), and §20 Step 8 (the executor prompt, second
occurrence). Authorizing cleanup and reference migration inside the
construction memo conflates the construction gate with the cleanup
gate; the two are separately gated in the project's authorization
discipline.

---

## 3. Heading correction

**Before:**

The text after the §20 closing paragraph and horizontal rule read:

```
## Required final statements

The following statements are made explicitly, as required.
```

This was a `##`-level heading, making it the memo's 21st heading.

**After:**

The `##` heading marker is removed; the text is now:

```
**Required final statements**

The following statements are made explicitly, as required.
```

The block is now plain bold text under §20, consistent with the 20-
section structure. The statements themselves (Option B authorization,
MNL rebuild NOT authorized, pooled stacking NOT authorized, pooled
estimation NOT authorized, welfare NOT authorized, M1-clean 2016
remains active) are unchanged.

---

## 4. Scope correction

The following eight passages were edited. In all cases the edits
remove the authorization for cleanup actions and replace with
deferred language. The construction authorization (Option B runs,
value-identity check, commit of the three lookups and sidecars)
is preserved in every passage.

| # | Location | Change |
|---|----------|--------|
| S1 | §4 scope paragraph | Removed "retiring the existing un-tagged y2016 parquet, and updating references to the un-tagged path" from the scope description; added deferred language: "Post-construction cleanup, archival of the un-tagged y2016 file, and reference migration are separately gated after the construction report and validation report pass." |
| S2 | §8 y2014 terminal step | Removed "the post-construction steps (commit, retire un-tagged y2016, update references) proceed (§4, §19)"; replaced with "the commit step (§10 Step 8) proceeds"; added deferred-language sentence. |
| S3 | §10 Step 8 (sequence) | Replaced "commit… retire… via `git mv`; update references…" with "commit the three parquets and three sidecars to git"; added deferred-language sentence and explicit prohibitions (do NOT retire, do NOT `git mv`, do NOT update scripts). |
| S4 | §11 required output files | Replaced the paragraph authorizing `git mv` retirement of the un-tagged file with a paragraph stating the un-tagged file is not retired by this construction; added deferred-language sentence. |
| S5 | §15 A7 | Removed action item "(A7) **Retiring the existing un-tagged y2016 lookup**…"; renumbered old A9 (existing-output guard) as new A7. |
| S6 | §15 A8 | Removed action item "(A8) **Updating references to the un-tagged path**…". |
| S7 | §15 closing sentence | Replaced "its immediate post-construction housekeeping (commit, retire, update references)" with "the commit of the three lookups and sidecars (A6)"; added deferred-language sentence. |
| S8 | §19 R5 | Replaced "(R5) **The post-construction housekeeping.**…" with "(R5) **The commit record.**…"; deferred cleanup and reference migration explicitly. |

The §20 executor prompt was also updated at Step 8 and in the
`Save the construction report` paragraph to remove references to
housekeeping and replace them with the commit-only scope and
deferred language.

---

## 5. What remains authorized

The following are unchanged by this correction and remain fully
authorized under the memo.

- **Option B construction sequence**: run y2016 first; run y2015
  only if the y2016 value-identity gate passes; run y2014 only if
  both the y2016 gate and the y2015 validation pass (§6–§8, §10).
- **y2016 value-identity check** (§6, §10 Step 2): key-aligned
  comparison on `(year, drgn1, educ3, sex)` over 48 active cells,
  max absolute `gsur` difference ≤ 1e-12 (§13).
- **Per-year validation** (§7, §8, §10 Steps 3/5/7): row count 54,
  sidecar 14 fields, expected benchmark values, IDF parity ≈ 0.0.
- **Committing the three lookups and three sidecars to git**
  (§10 Step 8, §15 A6), conditional on all three years passing.
- **Existing-output guard** (§11, §10 Steps 1/4/6): archive any
  pre-existing year-tagged output before re-running; do not overwrite
  silently (now §15 A7 after renumbering).
- **Construction report** (§19, §20): save as
  `Results/JMP_GSURv2_multi_year_extension_construction_report_v1.md`
  recording the full sequence, value-identity result, per-year
  validations, sidecar contents, commit record, halt record (if
  applicable), and next-gate readiness.
- All halt conditions (§14), failure-handling rules (§18), and
  downstream prohibitions (§16) are unchanged.

---

## 6. What remains not authorized

The following remain explicitly not authorized, unchanged from the
original memo (§16).

- MNL parquet rebuild (N1).
- Pooled stacking re-run (N2).
- Pooled estimation (N3).
- Welfare implementation or computation (N4).
- Canonical promotion of any file (N5).
- Any downstream step beyond the commit of the six year-tagged
  output files.

Additionally, as a result of this correction, the following are now
explicitly outside the scope of this construction authorization (they
were erroneously included before):

- Retiring the existing un-tagged y2016 lookup
  (`FR_gsur_ruro_v2_stageA.parquet`) to any archive path.
- Running `git mv` of any un-tagged file.
- Updating canary scripts to point at year-tagged paths.
- Updating validation scripts to point at year-tagged paths.
- Any other reference migration from the un-tagged path to a
  year-tagged path.

These actions are separately gated and will be authorized — if
appropriate — after the construction report and validation report
pass.

---

## 7. Final verdict

After this correction,
`docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md`
has exactly 20 numbered section headings (§1–§20) consistent with the
memo's own introduction. The "Required final statements" block is
plain bold text under §20.

The construction scope is now limited to the Option B Stage A lookup
construction and the commit of the six year-tagged output files.
Post-construction cleanup, archival of the un-tagged y2016 file, and
reference migration are deferred to a separate gate that follows
after the construction report and validation report pass.

The core Option B construction authorization — the run sequence,
value-identity gate, per-year validations, commit, halt conditions,
and downstream prohibitions — is unchanged and remains in force.

The memo is ready to serve as the construction authorization for the
GSURv2 multi-year Stage A lookup construction under Option B.

---

## 8. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md` | Heading correction | `## Required final statements` demoted to `**Required final statements**` plain text under §20 |
| `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_authorization_v1.md` | Scope correction (S1–S8) | Post-construction cleanup actions (retire un-tagged file, `git mv`, update canary/validation scripts, reference migration) removed from §4, §8, §10 Step 8, §11, §15 A7–A8 and closing sentence, §19 R5, §20 executor prompt; replaced with deferred language |
| `docs/JMP_GSURv2_multi_year_extension_construction_authorization_correction_v1.md` | New file | This report |

No code was changed. No data was built.