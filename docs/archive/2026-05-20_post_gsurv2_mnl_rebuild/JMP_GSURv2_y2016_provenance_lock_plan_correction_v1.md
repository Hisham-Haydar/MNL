# JMP GSURv2 y2016 Provenance Lock Plan — Correction v1

*France 2016 | v1 | 2026-05-20*

---

## 1. Correction verdict

Two targeted wording and sequencing corrections applied to
`docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`.
No code was changed. No script was run. No parquet was written.
The lock procedure itself (§8, Steps 1–9) is unchanged.

| # | Location | Issue | Action |
|---|----------|-------|--------|
| F1 | §6 verdict line and "Why preferred" bullet | The y2016 rebuild was described as already "authorized" — implying the construction authorization had been issued | Replaced with "preferred lock procedure, to be authorized by the GSURv2 construction authorization" in the verdict, and clarified in the bullet that the rebuild "will be authorized by the GSURv2 construction authorization, which is a separate document not yet produced" |
| F2 | §10 opening sentence and item list | "The construction authorization memo is the next task" — skipped the readiness re-audit step that sits between the current remediation state and the construction authorization | Replaced with "The GSURv2 readiness re-audit is the next task"; added that the construction authorization is conditional on the re-audit returning READY or READY WITH MINOR FIXES; updated item 1 of the construction authorization requirements to reference that the re-audit verdict must be READY or READY WITH MINOR FIXES |

---

## 2. Files inspected

| File | Purpose |
|------|---------|
| `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` | Subject to both corrections; §6 and §10 read in full |
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_v1.md` | Confirmed that the construction authorization is a separate document deferred to after the remediation (§3, §11 A5, §12 N1, §14) |
| `docs/JMP_GSURv2_multi_year_extension_remediation_authorization_correction_v1.md` | Confirmed the conservative y2016 approach: "all reproduction deferred to construction authorization" (C4); "lock-plan document prepared; actual y2016 reproduction deferred to construction authorization" (C6) |

No code files were read. No data files were read. No scripts were run.

---

## 3. Authorization wording correction

**Problem.** §6 in the original lock plan contained two passages that
described the y2016 rebuild as already authorized:

> "**Verdict: YES. The y2016 rebuild under the parameterised script is
> the preferred and authorized lock procedure.**"

> "The rebuild is authorised under the construction authorization. It
> does not require a separate or special authorization; it is the first
> step of the standard construction workflow…"

The first sentence conflated "preferred" with "authorized": calling
the rebuild "the preferred and authorized lock procedure" implies that
authorization has been granted, when in fact the construction
authorization is a separate document not yet produced. The second
sentence compounded this by saying the rebuild "does not require a
separate or special authorization", which is technically true in the
sense that no new authorization *type* is needed — but is misleading
because the construction authorization document itself has not been
issued.

**Fix applied.**

Verdict line before:
> "the preferred and **authorized** lock procedure"

Verdict line after:
> "the preferred lock procedure, **to be authorized by the GSURv2
> construction authorization**"

Bullet before:
> "The rebuild is authorised under the construction authorization. It
> does not require a separate or special authorization; it is the first
> step of the standard construction workflow (run `--opportunity-year
> 2016`, verify value-identity, accept and retire un-tagged file, then
> proceed to y2015 and y2014)."

Bullet after:
> "The rebuild is the first step of the standard construction workflow
> (run `--opportunity-year 2016`, verify value-identity, accept and
> retire un-tagged file, then proceed to y2015 and y2014). It will be
> authorized by the GSURv2 construction authorization, which is a
> **separate document not yet produced**."

The lock procedure itself (§8 Steps 1–9, the recommended sequence,
the pass criteria) is unchanged.

---

## 4. Next-task sequencing correction

**Problem.** §10 opened with:

> "The construction authorization memo is the next task."

This skipped the readiness re-audit step. The remediation
authorization §14 specifies seven post-remediation validation checks
(V1–V7) and states: "If all seven pass, the construction
preconditions are met and the construction authorization may be
issued." That structure — validate first, then authorize — implies a
re-audit or validation pass before the construction authorization.
The original §10 collapsed this two-step sequence into one, giving
the impression that the construction authorization follows directly
from the provenance lock plan.

Additionally, the original §10 made no mention of what happens if
the re-audit returns NOT READY: the construction authorization is
unconditionally "the next task" regardless of any validation result,
which is inconsistent with the gating discipline established in the
remediation authorization.

**Fix applied.**

§10 now opens with:
> "The GSURv2 readiness re-audit is the next task. It must confirm
> that all remediation outputs (O1–O5, and O6–O7 if complete) are in
> place before the construction authorization is issued. The
> construction authorization is conditional on the re-audit returning
> READY or READY WITH MINOR FIXES; it must not be issued if the
> re-audit returns NOT READY."

The six-item construction authorization requirements list is retained
unchanged in content, but is now introduced as describing what the
construction authorization memo must contain *once issued after a
passing re-audit*, not as an immediate next-step recipe. Item 1 is
updated to add the re-audit conditionality:

Item 1 before:
> "Confirms all remediation preconditions are met (referencing the
> script remediation report … and validation report …)."

Item 1 after:
> "Confirms all remediation preconditions are met (referencing the
> script remediation report … and validation report …) **and that
> the re-audit returned READY or READY WITH MINOR FIXES**."

Items 2–6 are unchanged.

---

## 5. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` | Wording correction (F1) | §6 verdict line and "Why preferred" bullet: "preferred and authorized" → "preferred … to be authorized by the GSURv2 construction authorization"; "does not require a separate or special authorization" → "will be authorized by the GSURv2 construction authorization, which is a separate document not yet produced" |
| `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_y2016_provenance_lock_plan_v1.md` | Sequencing correction (F2) | §10: opening sentence changed from "construction authorization memo is the next task" to "GSURv2 readiness re-audit is the next task"; re-audit conditionality paragraph added; item 1 updated to require re-audit verdict of READY or READY WITH MINOR FIXES |
| `docs/JMP_GSURv2_y2016_provenance_lock_plan_correction_v1.md` | New file | This report |

The lock procedure (§8 Steps 1–9), the sidecar field specification
(§4), the post-hoc sidecar analysis (§5), the O7 sign-off section
(§7), the not-authorized list (§9), and all other sections are
unchanged.

No code was changed. No data was built.

---

## 6. Final status

After both corrections, `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_y2016_provenance_lock_plan_v1.md`
accurately represents the authorization state:

- §6 no longer implies the construction authorization has been issued.
  The y2016 rebuild is described as the preferred approach that *will
  be authorized*, not as an approach that *is already authorized*.
- §10 now places the readiness re-audit between the current
  remediation state and the construction authorization, consistent
  with the gating discipline in the remediation authorization §14.
  The construction authorization is explicitly conditional on a READY
  or READY WITH MINOR FIXES re-audit verdict.

The lock procedure (§8), the sidecar field specification (§4), and
all other substantive content are unchanged. The document is ready to
serve as the O5 remediation output for the construction authorization
to act on, subject to a passing re-audit.