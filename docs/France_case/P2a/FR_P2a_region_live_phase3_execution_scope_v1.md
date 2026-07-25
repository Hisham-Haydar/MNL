# FR P2a Region-Live — Phase-3 Execution Scope — v1

Date: 2026-07-25. Manager decision resetting the Phase-3 execution-control threat model
from an adversarial-Python posture to a research-grade reproducibility contract.

## 1. Scope decision

The previous authorization design (external authorization JSON, test-double markers,
private-helper hardening, review-blob-in-authorization binding — remediations v1–v4,
reviews v1–v5) adopted an adversarial Python threat model that is disproportionate for an
economics research estimation pipeline. **This document supersedes only the Phase-3
execution-security requirements of those earlier remediation/review prompts.** All prior
implementation, remediation, and review reports remain valid — and immutable — engineering
audit history. The underlying econometric and numerical gates are unchanged. **Phase 3
remains prohibited until review v6 returns APPROVE.**

## 2. Research reproducibility objective

The goal is that the first real Phase-3 estimation be exactly reproducible and honestly
provenanced: run from a clean, reviewed, committed tree, on hash-verified inputs, through
the validated package objective, with a transactional, immutable result bundle — such that
any colleague can re-derive the identical result from the recorded commits and hashes.

## 3. Threats in scope

Accidental source-code drift; stale or substituted input artifacts; incorrect Git
revisions; incorrect nested-repository gitlink; dirty or untracked worktree changes; wrong
specification, theta, or output paths; incomplete or nontransactional result publication;
accidental overwrite of an accepted result; parameter-order, pin, bound, gradient, or
objective errors; package imported from the wrong source tree.

## 4. Threats out of scope

An attacker with arbitrary Python execution inside the estimation process; malicious
monkeypatching of `sys.modules`; forged internal Python dictionaries; `functools.partial`
or `__wrapped__` attacks; malicious direct calls to private Python helpers; a caller
intentionally bypassing the public CLI; Markdown injection beyond exact review-file
validation. A user able to execute arbitrary Python already has sufficient authority to
modify or replace the estimator; the production boundary is the documented CLI invocation
in a clean, reviewed repository — not every private Python callable.

## 5. Git identity policy

A real run requires: current MNL HEAD equal to `--expected-mnl-head`; current nested
dclaborsupply HEAD equal to `--expected-dclaborsupply-head`; the MNL gitlink for
`dclaborsupply-monorepo` equal to that nested HEAD; and
`git status --porcelain --untracked-files=all` empty for **both** repositories. These are
reproducibility checks, not cryptographic authorization.

## 6. Package identity policy

Imported `dclaborsupply` and its safety-critical modules (package, `spec.parser`,
`data.loader`, `likelihood.index`, `likelihood.engine_jax`,
`likelihood._numpy_primitives`, plus `models`/`data`/`spec`/`likelihood` initializers)
must resolve beneath `dclaborsupply-monorepo/packages/dclaborsupply/src`; each module path
must be tracked at the nested HEAD; and `git hash-object --path <rel> <file>` must
reproduce the tracked blob id. Git-canonical blob equality is used deliberately: under
Windows `autocrlf`, checked-out text files carry CRLF while blobs store LF, so raw
SHA-256 of working bytes may legitimately differ although the Git-canonical content — the
identity Git itself commits and reviews — is unchanged. Raw hashes are still recorded for
audit. The real run must start in a fresh Python process from the clean reviewed tree; no
defense against pre-mutated `sys.modules` is attempted (out of scope).

## 7. Review approval policy

The canonical approval document is
`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md`. A real run requires
its SHA-256 to equal `--approved-review-sha256` and the file to contain exactly one
ordinary Markdown line `**FINAL VERDICT: APPROVE**` under the exact first heading
`# 1. Sixth-review verdict`. `APPROVE AFTER FIXES` and `REJECT` are refused. Reviews
v1–v5 (all REJECT) cannot authorize execution.

## 8. Execution CLI policy

The single production execution boundary is the documented CLI:

```
python scripts/p2a/run_p2a_regionlive_rebuild.py
  --config scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
  --phase 3
  --out outputs/p2a_singles2016/region_live_v1
  --execute-phase3
  --expected-mnl-head <40-hex>
  --expected-dclaborsupply-head <40-hex>
  --approved-review docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md
  --approved-review-sha256 <64-hex>
```

`--execute-phase3` is mandatory for a real run; without it `--phase 3` performs only the
existing non-optimizing dry-run. The exact canonical config and output paths remain
mandatory; phases above 3 remain refused. Private helpers stay private and are not
supported execution interfaces; they carry no malicious-caller defenses.

## 9. Output transaction policy

Unchanged from the accepted design: canonical Phase-3 output root; exclusive lock; unique
attempt staging; immutable `complete/`; atomic directory-level publication; no overwrite
of a prior success; exact successful artifact set; manifest written last and excluded from
its own artifact-hash dictionary; failed/review/dry attempts land under `attempts/`.

## 10. Numerical gates retained

Unchanged: input hashes verified before and rechecked identically after optimization over
one threaded runtime map; the explicit 37-free ↔ 47-full parameter map; the exact ten
pins; the two expected bound parameters (`beta_l_age2_sm`, `beta_l_age2_sf`); the
35-parameter gradient gate (< 1e-2); G-16 with ε = 1e-9; the target objective
19053.46553160094 with tolerance 1e-4 and two-sided
`REVIEW_REQUIRED_TARGET_MISMATCH`; exact L-BFGS-B options
(maxiter 5000, maxcor 30, ftol 1e-15, gtol 1e-10); no Phase 4–8 operation.

## 11. Superseded controls

Removed as out-of-scope: the external authorization JSON (schema, record, location rules,
review-blob-in-JSON binding); `--authorization`; test-double markers and
genuine-component identity rejection; the private test-orchestration helper and its
production-tree refusal machinery; the scipy-module presence guard as an adversarial
control (dry-runs are proven non-optimizing structurally and by recorded state).

## 12. Relationship to prior reviews

Reviews v1–v5 remain the audit record of the hardening iterations; their
execution-security requirements are superseded by this scope, while every econometric,
numerical, provenance-hashing, and transactional requirement they validated is retained.
Review v6 evaluates the simplified contract.

## 13. Baseline and P2a status

The certified 47-parameter pooled baseline (`joint_pooled_v1_bll0_tlmpin`, negLL
238504.6360973987) remains the formal JMP baseline, untouched. P2a region-live remains
PROVISIONAL; no inference, manuscript, or welfare use; welfare remains non-reportable.

## 14. Immediate next action

Implement the simplified contract (runner/config/tests), validate without executing real
Phase 3, and request review v6. Only an exact APPROVE there unblocks the first real run
via the §8 CLI.
