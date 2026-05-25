> Archived on 2026-05-26 as a documentation-only correction whose substance is reabsorbed.
> Base files (kept active): `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` and `..._construction_report_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP GSURv2 Multi-Year Extension — Construction Verdict Correction v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Purpose

This document records three narrow documentation corrections applied
across three files. No data values, parquets, sidecars, validation
results, commands, or authorization status were changed.

| # | File | Issue | Action |
|---|------|-------|--------|
| C1 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | Extra `## Required final statements` heading (21st heading, beyond the 16 required sections) | Demoted to `**Required final statements**` plain bold text under §16 |
| C2 | `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | Post-construction cleanup described as a "conservative deviation" from the authorization | Replaced with: construction followed the authorization; cleanup was correctly not executed because it is separately gated |
| C3 | `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md` and `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md` | FRM0 labelled "Mayotte"; FRI2 labelled "Corsica" | Corrected to FRM0 = Corse; FRI2 = Limousin |

---

## 2. Files corrected

| File | Sections changed | Change type |
|------|-----------------|-------------|
| `docs/JMP_GSURv2_multi_year_extension_construction_verdict_v1.md` | §1, §2, §15, §16, closing block | Heading demotion (C1); authorization-scope wording (C2) |
| `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md` | §9 (Crosswalk logic) | NUTS label correction (C3) |
| `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md` | §11 (Denominator-source and fallback checks) | NUTS label correction (C3) |
| `docs/JMP_GSURv2_multi_year_extension_construction_verdict_correction_v1.md` | — | New file (this report) |

No code was changed. No data was built. No parquets or sidecars were
modified.

---

## 3. Heading correction

**Before:** The verdict document had 16 numbered sections (§1–§16)
followed by a 17th heading:

```
## Required final statements
```

This made `Required final statements` an unintended 17th `##`-level
section, inconsistent with the 16-section structure.

**After:** The `##` marker is removed; the block is now:

```
**Required final statements**
```

It is plain bold text under §16, consistent with the 16-section
structure. The statements themselves are unchanged.

---

## 4. Authorization-scope wording correction

**Problem.** Several passages in the verdict described the non-
execution of post-construction cleanup as a "conservative deviation"
from the authorization:

- §1: "the post-construction housekeeping … was deferred to a
  separate cleanup gate rather than executed in the construction;
  this is a conservative deviation that preserves the existing
  baseline intact"
- §2 heading: "The post-construction housekeeping (Step 8 of the
  authorization §10) was deferred to a separate cleanup gate, which
  is a conservative deviation that does not affect the construction
  PASS."
- §2 body: "The deferral is a conservative deviation from the
  authorization's Step 8, not a failure to follow the authorization.
  The authorization conditioned Step 8 on all three years passing;
  all three years did pass, so Step 8 was authorised. The
  construction chose to defer the irreversible housekeeping …"

This framing was incorrect. The construction authorization §4 states
explicitly that "post-construction cleanup, archival of the un-tagged
y2016 file, and reference migration are separately gated after the
construction report and validation report pass", and §10 Step 8
restricts the construction to committing the six output files only,
with the same deferred-cleanup language. The cleanup was not
authorized inside the construction; not performing it was not a
deviation of any kind.

**Fix applied.** All passages describing the cleanup non-execution as
a deviation have been replaced with language stating that the
construction followed the authorization correctly, and that post-
construction cleanup is separately gated per the authorization.

Specific changes:

| Location | Before | After |
|----------|--------|-------|
| §1 first outstanding item | "conservative deviation that preserves the existing baseline" | "correctly not executed: post-construction cleanup … are separately gated (per the construction authorization §4 and §10 Step 8), and the construction followed the authorization correctly by not performing them" |
| §2 heading | "deferred to a separate cleanup gate, which is a conservative deviation that does not affect the construction PASS" | "correctly not executed: they are separately gated per the construction authorization §4 and §10 Step 8, and the construction followed the authorization correctly by not performing them" |
| §2 body (deferral paragraph) | "The deferral is a conservative deviation … The construction chose to defer the irreversible housekeeping …" | Replaced with: the construction authorization §4 and §10 Step 8 explicitly defer cleanup to a separate gate; the construction followed the authorization; no deviation occurred |
| §15 housekeeping block header | "Post-construction housekeeping. Three housekeeping items are outstanding from the construction" | "Post-construction cleanup (separately gated). Three items are separately gated per the construction authorization and are not outstanding failures of the construction" |
| §15 H1 | "retirement … is deferred to a cleanup gate" | "retirement … is separately gated after the construction report and validation report pass, per the authorization" |
| §15 H2 | "The migration is deferred to the same cleanup gate" | "The migration is separately gated per the authorization" |
| §16 parallel task sentence | "post-construction cleanup … which may be authorised under a separate narrow cleanup authorization" | "post-construction cleanup authorization … which may be issued at any time after this verdict" |

The construction PASS verdict is unchanged. The lookup data products,
validation results, and authorization status are unchanged.

---

## 5. NUTS label correction

**Problem.** Two construction documents carried incorrect region-name
labels for two NUTS-2 codes:

| Code | Incorrect label used | Correct label |
|------|---------------------|---------------|
| FRM0 | Mayotte | Corse |
| FRI2 | Corsica | Limousin |

Mayotte (INSEE code 06, NUTS FRY5) is a distinct overseas collectivity
that was outside EU-LFS and EU-SILC France for the reference years
used in this project. FRM0 is Corse (Corsica in English; the NUTS code
for the Corse region in the 22-region NUTS-2016 metropolitan France
classification). FRI2 is Limousin (one of the three NUTS-2 units of
the former Limousin région, reclassified under NUTS-2016). The
suppression handling in the construction script operates on NUTS codes,
not on labels; the construction results are unaffected by the label
slip. The corrections are documentation-only.

**Occurrences corrected:**

| File | Section | Before | After |
|------|---------|--------|-------|
| `docs/JMP_GSURv2_multi_year_extension_construction_report_v1.md` | §9 Crosswalk logic | "FRM0 (Mayotte) and FRI2 (Corsica) suppression is year-invariant" | "FRM0 (Corse) and FRI2 (Limousin) suppression is year-invariant" |
| `Results/JMP_GSURv2_multi_year_extension_validation_report_v1.md` | §11 Denominator-source and fallback checks | "suppressed denominator cells (e.g., FRM0 Mayotte, FRI2 Corsica)" | "suppressed denominator cells (e.g., FRM0 Corse, FRI2 Limousin)" |

The external file remediation report
(`Results/JMP_GSURv2_external_file_remediation_report_v1.md`) already
carried the correct label "FRM0 (Corse)" and required no correction.

---

## 6. What was not changed

The following were inspected and left unchanged:

- All data values, `gsur` rates, and parquet contents.
- All sidecar JSON files and their field values.
- All validation results and PASS/FAIL verdicts.
- The y2016 value-identity gate result (max diff = 0.0).
- All IDF parity results (0.0 for all three years).
- All benchmark values and differences.
- The construction PASS verdict.
- The authorization status of all downstream steps (MNL rebuild,
  pooled stacking, pooled estimation, welfare — all remain NOT
  authorized).
- The construction sequence (Option B), commands run, script
  version (`178ca72`), and interpreter (`.venv\Scripts\python.exe`).
- The six output file SHA-256 hashes and sizes.
- All other sections of the verdict, construction report, and
  validation report not listed in §§3–5 above.

---

## 7. Final verdict

**GSURv2 multi-year lookup construction remains PASS.**

The three narrow documentation corrections (heading demotion,
authorization-scope wording, NUTS region labels) do not affect any
construction result, validation result, or authorization status. The
construction PASS is unchanged.

**GSURv2 coverage for P3a opportunity years 2014, 2015, and 2016
remains complete at the lookup level.** A validated, provenance-
documented GSURv2 lookup exists for each of the three opportunity
years. The MNL-parquet integration of these lookups is the next stage
and has not been performed.

**O7 crosswalk sign-off remains the next gate.** The O7 sign-off is
the prerequisite for the MNL-parquet rebuild. It is a pending user
decision.

**MNL parquet rebuild remains NOT authorized.** The O7 crosswalk
sign-off has not been explicitly signed off; the MNL-parquet rebuild
additionally requires its own authorization memo.

**Pooled stacking, pooled estimation, and welfare remain NOT
authorized.** These steps are downstream of the MNL-parquet rebuild
and are separately gated.