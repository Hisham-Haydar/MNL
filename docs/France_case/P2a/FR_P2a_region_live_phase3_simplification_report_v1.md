# FR P2a Region-Live — Phase-3 Simplification Report — v1

Date: 2026-07-25. Implements `FR_P2a_region_live_phase3_execution_scope_v1.md` (created
first). No real Phase 3; no optimizer invoked; nothing committed; history untouched.

## 1. Simplification verdict

**READY FOR FINAL INDEPENDENT REVIEW.** The adversarial authorization subsystem is fully
removed and replaced by the research-grade CLI execution contract; every numerical and
output-safety control is preserved; the rewritten suite passes 30/30 with a clean
`git diff --check`; a 3-lens adversarial verification workflow found zero functional
leftovers and zero preservation defects (its comment-residue and gitlink-coverage findings
were fixed and re-validated in this pass).

## 2. Reason for scope reset

Manager decision (scope doc §1/§4): the prior design defended against an attacker with
arbitrary Python execution — disproportionate for a research pipeline whose real risks are
drift, stale inputs, wrong revisions, dirty trees, and non-transactional publication. The
production boundary is now the documented CLI in a clean, reviewed repository.

## 3. Files inspected

All governing docs, every Phase-3 implementation/remediation/review report v1–v5, the
runner/config/tests, the Phase-3 dclaborsupply modules, and the full Git state (HEAD
`40a2c84` = review-v5 REJECT commit; clean tree at start).

## 4. Files modified

Runner (−452 net), tests (full rewrite, −1,402→~700 lines), config (comment refresh only);
created: the scope doc and this report. Prior reports untouched.

## 5. Removed authorization subsystem

Gone entirely (grep-verified by the leftover lens): `--authorization`, `AUTH_SCHEMA` /
required-field schema, authorization records and location rules, review-blob-in-JSON
binding, `_verify_external_authorization`, test-double markers +
`_validate_test_double`, `_run_phase3_test_attempt` / `_phase3_attempt_test_body` /
`_phase3_orchestrate_production`, the scipy-module presence guard, and all
`auth_record` naming (now `gates_record`). No authorization JSON is required or created.

## 6. Public execution boundary

One production entrypoint: the scope-doc §8 CLI. `--execute-phase3` is mandatory for a
real run; without it `--phase 3` **forces** the non-optimizing dry-run (verified live and
by test 29's subprocess run). Canonical config/out/subdir remain mandatory; phases > 3
refused. `_phase3_run` is private, undocumented as an interface, and independently refuses
an unverified real run before any transaction (test 28: no lock ever appears).

## 7. Git revision gates

`_verify_execution_gates`: MNL HEAD == `--expected-mnl-head`; nested HEAD ==
`--expected-dclaborsupply-head`; MNL gitlink == nested HEAD (negative-path proven via a
temp-repo `update-index --cacheinfo 160000` gitlink in test 30; live equality in test 27);
`git status --porcelain --untracked-files=all` empty for both repos (tracked/untracked
dirty variants tested, both repos).

## 8. Review approval gate

Canonical path pinned to `…code_review_v6.md`; SHA-256 must equal
`--approved-review-sha256`; exactly one `**FINAL VERDICT: APPROVE**` line under the exact
first heading `# 1. Sixth-review verdict`; AFTER FIXES, REJECT, wrong heading, prose
APPROVE, multi-verdict, wrong path (v5), and malformed SHA all refused (tests 25–26).

## 9. Package identity gate

Unchanged in substance: ancestry under `packages/dclaborsupply/src` via
`is_relative_to` for the ten-module inventory (+ any loaded `dclaborsupply.*`), tracked at
nested HEAD (or the expected head on real runs), with **Git-canonical blob equality**
(`git hash-object --path`) — documented rationale: under Windows autocrlf, worktree text
files carry CRLF while blobs store LF, so raw SHA-256 may differ although the committed
content is identical; raw hashes stay persisted for audit. Substitution / untracked /
modified refusals tested (tests 23–24).

## 10. Numerical gates preserved

Zero-finding preservation audit (workflow lens, line-by-line): 37↔47 map + ordered pin
tuple; expected bound pair; 35-parameter gradient gate 1e-2; G-16 ε=1e-9 (exact ± ε and
nextafter boundaries tested); target 19053.46553160094 ± 1e-4 two-sided with immutable
`REVIEW_REQUIRED_TARGET_MISMATCH`; exact L-BFGS-B options; pre-opt objective tolerance;
input authentication + identical post-optimization recheck over one fingerprinted runtime
map; safety-constant YAML equality.

## 11. Transactional publication preserved

Lock (O_EXCL, never auto-deleted), unique attempts, immutable `complete/`, atomic
directory rename, exact 4-artifact + manifest-last bundle, no manifest self-hash,
mismatch/failure → `attempts/` only (tests 14–16).

## 12. Test-suite simplification

Rewritten to 30 tests around the new scope: pure gates, transaction, estimator route via
`scipy.optimize.minimize` monkeypatching (FakeMin asserts 37-vector, 37 bounds, jac=True,
exact options, objective/gradient signs on the real interleaved ordering), execution-gate
batteries on temporary Git repositories, package identity, subprocess canonical dry-run.
Removed: marker/genuine-double/seam-separation/authorization-JSON/raw-EOL-equality tests
(out-of-scope threats).

## 13. Safety-test result

`pytest -q` → **30 passed**, exit 0 (~15 s); `git diff --check` exit 0. No real optimizer
call anywhere (FakeMin patched before every `_phase3_estimate` invocation; subprocess
dry-run never reaches estimation).

## 14. Phase 1–2 regression

Scratch-root `--phase 2 --dry-run`: exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`, stem
regenerated **byte-identical** (`8bf083ce…`).

## 15. Phase-3 dry-run

Canonical CLI without `--execute-phase3`: exit 0, `PHASE_3_DRY_RUN_COMPLETE`;
`optimizer_called: false`, `execution_ready: false`,
`review_gate: AWAITING_REVIEW_V6_APPROVE`; `complete/` absent; lock released; contract
dev 0.00e+00 (run live and again inside test 29).

## 16. Prohibited-operation audit

No EUROMOD/draws/Hessian/inference/post-estimation/welfare/synthetic recovery/notebooks;
`--phase 4` refused (exit 2); sweep: **0 changed pre-existing files** under
`region_live_v1/`; nested monorepo clean; baseline/thetas/Phase 1–2 evidence untouched.
Adversarial workflow: leftover lens — no functional residue (3 comment findings, fixed);
preserve lens — zero findings; coverage lens — gitlink gap fixed (test 30), remaining
low items recorded in §18.

## 17. Git diff summary

```
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |   18 ±
 M scripts/p2a/run_p2a_regionlive_rebuild.py          |  452 ±  (net removal)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | 1402 ±  (rewrite, net -848)
 ?? docs/France_case/P2a/FR_P2a_region_live_phase3_execution_scope_v1.md
 ?? docs/France_case/P2a/FR_P2a_region_live_phase3_simplification_report_v1.md
 ?? outputs/.../phase3_estimation_v1/attempts/… (validation dry-run bundles)
```

HEAD `40a2c84`; nothing committed; history intact.

## 18. Residual warnings

Low-severity test-coverage niceties flagged by the coverage lens and left for review v6's
judgment (all corresponding runner branches exist and are exercised indirectly):
tracked-dirty variant in the gate battery covers untracked/tracked but not a staged-only
case per repo; review-hash equality is refused via the earlier format/hash path; the
missing-expected-bound G-15 direction, the pins-violated STOP branch, the
`complete/`-pre-exists real-run refusal, and the package `expected_commit`-mismatch branch
lack dedicated unit tests; test 29 (subprocess dry-run) necessarily writes an attempt
bundle into the canonical `attempts/` history, consistent with the never-delete
discipline.

## 19. Whether final independent review may begin

**YES** — the simplified contract is implemented, validated, and adversarially audited.

## 20. Immediate next action

Review v6. On one exact `**FINAL VERDICT: APPROVE**` under `# 1. Sixth-review verdict`:
commit, record the approved HEADs and review hash, and execute the first real Phase 3 via
the scope-doc §8 CLI. Phases 4–8 remain manager-gated.

**FINAL VERDICT: READY FOR FINAL INDEPENDENT REVIEW** (no real Phase 3; no authorization
file; nothing committed).
