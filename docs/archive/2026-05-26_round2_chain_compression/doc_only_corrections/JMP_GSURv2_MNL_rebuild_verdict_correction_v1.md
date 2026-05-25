> Archived on 2026-05-26 as a documentation-only correction whose substance is reabsorbed.
> Base file (kept active): `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP GSURv2 MNL-Parquet Rebuild Verdict — Correction v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Purpose

This document records a narrow wording correction applied to
`docs/JMP_GSURv2_MNL_rebuild_verdict_v1.md`. No data values,
parquet files, validation results, or downstream authorizations were
changed. The correction is documentation-only.

| # | Issue | Action |
|---|-------|--------|
| C1 | §19 and §23 (and the §1 summary, §20 cross-reference, §22 table, and Required final statements) contained wording suggesting this verdict directly authorizes Claude Code execution of the Stage M1 P3a GSURv2 stacking re-run | Replaced with the required wording: the immediate next authorized task is to write the stacking re-run authorization memo; the stacking execution itself remains separately gated and is not authorized until that memo exists |

---

## 2. Issue corrected

The verdict document stated, in several places, that "the Stage M1
P3a GSURv2 pooled stacking re-run is authorised as the next gate"
and that "the stacking re-run is authorised as the next gate (§19)."
This wording was ambiguous: it could be read as authorizing Claude
Code to execute the stacking re-run on the basis of this verdict
alone, with the authorization memo being optional or concurrent
rather than a prerequisite.

The correct sequencing is:

1. This verdict completes the post-rebuild assessment.
2. The immediate next authorized task is to write the Stage M1 P3a
   GSURv2 stacking re-run authorization memo.
3. The stacking execution itself is not authorized until that memo
   exists and authorizes it.

The ambiguous passages were in the following locations:

| Location | Ambiguous wording |
|----------|-------------------|
| §1 (verdict summary, closing paragraph) | "authorises one downstream step and no more: the Stage M1 P3a GSURv2 pooled stacking re-run (§19), which is the next gate" |
| §19 (section heading and bold statement) | "The Stage M1 P3a GSURv2 pooled stacking re-run is authorised as the next gate, conditional on a separate stacking authorization memo specifying its scope" |
| §19 (body, second paragraph) | "This verdict authorises the Stage M1 P3a GSURv2 pooled stacking re-run as the next gate, and only that. The authorisation is bounded: it authorises the stacking re-run to proceed to its own authorization memo" |
| §20 (cross-reference to §19) | "the Stage M1 P3a GSURv2 stacking re-run is authorised as the next gate but has not been executed" |
| §22 (downstream gates table) | Single row: "Stage M1 P3a GSURv2 stacking re-run — Authorised as the next gate (§19); requires its own stacking authorization memo specifying scope" |
| §22 (closing paragraph) | "The immediate downstream gate is the Stage M1 P3a GSURv2 stacking re-run (§19, §23), which is authorised as the next gate" |
| §23 (section heading and bold statement) | "The immediate next task is the Stage M1 P3a GSURv2 pooled stacking re-run authorization memo" / "The stacking re-run is authorised as the next gate (§19)" |
| Required final statements | "The Stage M1 P3a GSURv2 pooled stacking re-run is authorised as the next gate, conditional on its own stacking authorization memo specifying scope" |

---

## 3. Wording correction

All ambiguous passages are replaced with the required wording or
its contextual equivalent.

**Required wording (applied to all affected passages):**

> "The immediate next authorized task is to write the Stage M1 P3a
> GSURv2 stacking re-run authorization memo. The stacking execution
> itself remains separately gated and is not authorized until that
> memo exists."

**Specific substitutions applied:**

| Location | Before | After |
|----------|--------|-------|
| §1 closing paragraph | "authorises one downstream step and no more: the Stage M1 P3a GSURv2 pooled stacking re-run (§19), which is the next gate" | "advances the pipeline to one immediate next authorized task and no more: writing the Stage M1 P3a GSURv2 stacking re-run authorization memo (§19, §23). The stacking execution itself remains separately gated and is not authorized until that memo exists" |
| §19 bold statement | "The Stage M1 P3a GSURv2 pooled stacking re-run is authorised as the next gate, conditional on a separate stacking authorization memo specifying its scope" | "The immediate next authorized task is to write the Stage M1 P3a GSURv2 stacking re-run authorization memo. The stacking execution itself remains separately gated and is not authorized until that memo exists" |
| §19 body, second paragraph opening | "This verdict authorises the Stage M1 P3a GSURv2 pooled stacking re-run as the next gate, and only that. The authorisation is bounded: it authorises the stacking re-run to proceed to its own authorization memo" | "This verdict advances the pipeline to the stacking authorization memo as the immediate next task, and only that. The stacking re-run does not execute on the basis of this verdict alone: a separate stacking authorization memo must first be written" |
| §19 body, Step 2 sequence item | "conditional on the authorization" | "conditional on the authorization memo existing and authorizing execution" |
| §19 last paragraph of body | "No step beyond the stacking re-run is authorised by this verdict" | "No step beyond the stacking authorization memo is authorised by this verdict" (with addition: "But the execution of the stacking re-run is gated on its own authorization memo; this verdict does not authorize that execution") |
| §20 cross-reference | "the Stage M1 P3a GSURv2 stacking re-run is authorised as the next gate but has not been executed, §19" | "the Stage M1 P3a GSURv2 stacking re-run authorization memo has not yet been written (§19)" |
| §22 table | Single row "Stage M1 P3a GSURv2 stacking re-run — Authorised as the next gate (§19)…" | Split into two rows: (1) "Stage M1 P3a GSURv2 stacking re-run authorization memo — Immediate next authorized task (§19, §23)"; (2) "Stage M1 P3a GSURv2 stacking re-run execution — Not authorized until the stacking authorization memo exists" |
| §22 closing paragraph | "The immediate downstream gate is the Stage M1 P3a GSURv2 stacking re-run (§19, §23), which is authorised as the next gate" | "The immediate next authorized task is writing the Stage M1 P3a GSURv2 stacking re-run authorization memo (§19, §23). The stacking execution itself is not authorized until that memo exists" |
| §23 bold statement | "The immediate next task is the Stage M1 P3a GSURv2 pooled stacking re-run authorization memo" + "The stacking re-run is authorised as the next gate (§19)" | "The immediate next authorized task is to write the Stage M1 P3a GSURv2 stacking re-run authorization memo. The stacking execution itself remains separately gated and is not authorized until that memo exists" |
| §23 Step 1 label | "This is the immediate next task" | "This is the immediate next authorized task" |
| Required final statements | "The Stage M1 P3a GSURv2 pooled stacking re-run is authorised as the next gate, conditional on its own stacking authorization memo specifying scope" | "The immediate next authorized task is to write the Stage M1 P3a GSURv2 stacking re-run authorization memo. The stacking execution itself remains separately gated and is not authorized until that memo exists" |

---

## 4. What was not changed

The following are confirmed unchanged:

- The **PASS WITH MINOR DOCUMENTATION CAVEAT** classification.
- All V1–V12 findings and results for all three survey years.
- The FR_2017 `y2017` documentation-typo finding (§16, §17 D1):
  the actual files and sidecars carry `GSURv2_y2016`; the typo is
  isolated to report v2 §5. This finding is unchanged.
- The GSURv2-final input status of the rebuilt MNL parquets (§18).
- The statement that pooled estimation is NOT authorized (§20).
- The statement that welfare computation is NOT authorized (§21).
- The statement that M1-clean 2016 remains the active JMP baseline.
- All SHA-256 hashes, row counts, household counts, and validation
  results recorded in the verdict.
- The description of the stacking re-run scope (what the
  authorization memo must specify).
- The downstream sequencing (authorization memo → stacking re-run
  → stacking verdict → pooled estimation gates).
- The statement that the stacking re-run produces the final (non-
  provisional) pooled dataset, not an estimation result.
- All other sections (§1–§18, §20–§22) except where the specific
  passages listed in §3 were corrected.

No parquet data was changed. No sidecar was changed. No validation
was rerun.

---

## 5. Final verdict

**The GSURv2 MNL-parquet rebuild verdict remains PASS WITH MINOR
DOCUMENTATION CAVEAT.**

The wording correction does not affect the verdict classification,
the data findings, or the downstream authorization status. After
correction, the verdict accurately states:

- The immediate next authorized task is to write the Stage M1 P3a
  GSURv2 stacking re-run authorization memo.
- The stacking execution itself remains separately gated and is not
  authorized until that memo exists.

**Pooled stacking re-run execution is NOT authorized.** Writing the
stacking re-run authorization memo is the only task authorized by
this verdict as the immediate next step.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced only
by a future SA2 verdict explicitly promoting a final pooled
specification.