# JMP-M05C Increment-B Proportionality Decision v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation  
**Escalation:** Increment-B Review v2 returned `REJECT`  
**Decision-maker:** ChatGPT JMP Deputy Programme Director  
**Date:** 2026-08-03  
**Verdict:** NUMERICAL CORE ACCEPTED; ONE MECHANICAL THREE-FIX CLOSURE AUTHORIZED

## 1. Finding

Increment-B Review v2 establishes that:

- the numerical and econometric core is unchanged and sound;
- T-5 theta authentication passes;
- the authoritative gradient source passes;
- all six Review-v1 adversarial examples were substantially closed;
- all twelve reviewer proofs execute;
- Increment A remains green;
- accepted bundles and package state are unchanged;
- no persistence event occurred.

The remaining defects are:

1. the expected T-22 active-name set is caller-overridable;
2. serializers reject an empty `inference_grade` only after writing;
3. `write_score_aggregate_summary(extra=...)` can persist prohibited row-level
   content and overwrite protected fields.

Only defect 3 is independently sufficient to block progression because it
contradicts the no-row-level-persistence and disclosure contract. Defects 1 and
2 are localized mechanical defects and are closed in the same task because
their fixes are trivial and already precisely identified.

## 2. Proportionality ruling

No further broad Increment-B review or software-hardening cycle is authorized.

Authorize one finite, test-first mechanical closure whose complete target is:

- three frozen failing probes;
- three localized corrections;
- existing numerical regression suite;
- one focused binary verification.

The reviewer may not add new non-econometric or security-hardening requirements.

A newly observed issue may block only if it affects:

- econometric/statistical correctness;
- the actual production path;
- accepted-artifact integrity;
- reproducibility;
- row-level data persistence or disclosure.

Other observations must be recorded as nonblocking technical debt.

## 3. Frozen three probes

### Probe B-1 — T-22 authority

The public gate must not accept a caller-supplied expected active-name set.

The expected set must be derived internally from the authenticated parameter
map or the frozen authenticated constant checked against that map.

The probe must show that attempts to supply or forge another expected-name set
are impossible or rejected.

### Probe B-2 — Refusal leaves destination untouched

For every serializer, invalid or empty `inference_grade` must be rejected before
opening, creating, truncating, or replacing the destination.

The probe must start from a nonexistent destination and prove it remains
nonexistent after refusal.

Where an existing sentinel destination is used, refusal must leave its bytes
and hash unchanged.

### Probe B-3 — No arbitrary `extra=` persistence

Remove the unrestricted `extra=` channel from
`write_score_aggregate_summary`, or replace it with an explicit immutable
allowlist of scalar non-sensitive keys.

The serializer must:

- reject arrays, frames, mappings containing arrays, bytes/memoryviews, and
  row-level sequences;
- reject protected-field collisions;
- construct protected fields after any permitted extension so they cannot be
  overwritten;
- reject the reviewer's temporary `5×37` score-block example before writing;
- leave the destination untouched on refusal.

The preferred baseline is to remove `extra=` entirely unless Increment C has a
specific accepted need for named scalar extensions.

## 4. Acceptance criterion

Increment B is accepted when:

1. the exact three frozen probes pass;
2. the existing Increment-A and Increment-B regression suites pass;
3. numerical outputs, constants, schemas, and source authorities are unchanged;
4. no row-level score artifact is written;
5. accepted bundles and nested package remain unchanged;
6. the focused reviewer returns `PASS`.

No broad re-audit is required.

## 5. Review verdict

The focused closure review may return only:

- `PASS`; or
- `FAIL`.

A `PASS` authorizes the exact Increment-B commit and Increment C.

A `FAIL` returns to the Goal 1 Manager. The manager may correct only a direct
implementation error in one of the same three frozen probes. No new review
class or architectural redesign is authorized without deputy escalation.

## 6. Prospective rule for Increment C

Increment C must be managed under
`JMP_certification_proportionality_rule_v1.md`.

The review should focus on:

- actual production runner execution;
- fresh-process reproduction;
- aggregate-only transaction;
- STOPPED truthfulness;
- no `complete/`;
- no row-level persistence;
- accepted-artifact and revision binding.

It must not restart capability-security or import-surface certification.
