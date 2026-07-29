# FR P2a Region-Live — Phase-4 Remediation Report — v2

Date: 2026-07-29. Applies the required fixes of
`FR_P2a_region_live_phase4_code_review_v2.md` §21–§22 (verdict APPROVE AFTER
FIXES): exceptional-path derivative provenance, the two remaining stale
Phase-3-review strings, and rebinding of the approval gate to Phase-4 review
v3. No real gradient or Hessian; no optimizer; theta untouched; no Phase 5+;
dclaborsupply-monorepo and the accepted Phase-3 bundle unmodified; nothing
committed.

## 1. Remediation-v2 verdict

**READY FOR PHASE-4 REVIEW V3.** Derivative-progress flags now flip immediately
after each derivative evaluates and survive every exception path: a
gradient-consistency stop finalizes `gradient_evaluated: true /
hessian_evaluated: false`, a singular post-Hessian Schur stop finalizes
`true / true`, and partial diagnostics are preserved in the STOPPED manifest.
The real-execution gate is rebound to
`FR_P2a_region_live_phase4_code_review_v3.md` (v1, v2 and Phase-3 review-v6 all
rejected). Suite: **52 passed**; the two new STOPPED-finalization tests pass in
five consecutive repetitions; `git diff --check` exit 0; canonical dry-run exit
0 with all evaluation flags false; Phase-3 bundle byte-identical.

## 2. Review-v2 defects addressed

§21.1 (Medium, inaccurate STOPPED provenance) → fixed by live progress
accounting merged into the manifest on every finalization path (§5–§9).
§21.2 (Low, stale Phase-3 approval wording + dry-run help) → fixed (§11).
§22.4 (rebind to review v3) → fixed (§10).

## 3. Files inspected

Read in full: the Phase-4 implementation report, reviews v1 and v2, remediation
report v1, the Phase-3 manager acceptance, the runner, the config, the safety
tests, and the complete current Git diff (HEAD
`c7d558a36489520a0f8487abf939d5300deaffb1`; nested HEAD = gitlink
`27756a06ea189339aa82915ed2124628afed20eb`, clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (cumulative uncommitted
   +927/−17): progress accounting, `_phase4_merge_progress`,
   `_phase4_run_diagnostics`, exception records, review-v3 rebinding, string
   corrections.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+43/−5): comment-only
   v2→v3 corrections; no threshold or anchor change.
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+665/−3): tests 50–52
   added, test-42 review-gate label updated; all 49 prior tests retained.

Created: this report. All previous reports and reviews preserved unchanged.
The real review-v3 file was NOT created.

## 5. Derivative-progress design

One mutable `progress` dict is owned by `_phase4_run` (created before the
transaction try-block, so it is visible to every exception handler) and passed
into `_phase4_diagnose`. Inside the diagnostic route:
`gradient_evaluated` flips to true immediately after `grad_fn` returns and
BEFORE the gradient-consistency gate; `hessian_evaluated` flips immediately
after `hess_fn` returns and BEFORE symmetry/eigen gates. The live `diag` dict
is exposed as `progress["partial_diagnostics"]` (a reference, never a copy),
so everything computed up to a raise is available to finalization.
`_phase4_merge_progress` writes both flags into the manifest on every outcome
— success, gated STOPPED, StopRun mid-diagnostics, and unexpected exceptions —
and attaches `partial_diagnostics` only when the full gate record (`gates4`)
was never reached. No state waits for `_phase4_diagnose()` to return.

## 6. Gradient-consistency STOPPED path

Test 50 drives the production `_phase4_run_diagnostics` body (real
transaction, manifest skeleton, fake gradient returning ones against a zero
published projection): the gradient evaluates, the consistency gate raises,
finalization records status `STOPPED`, stop code `S-8` / gate
`phase4-gradient`, exception type `StopRun`, **`gradient_evaluated: true`,
`hessian_evaluated: false`**; the partial diagnostics preserve the 37-element
gradient and the deviation (1.0) while containing no Hessian battery; no
`complete/`, staging empty, lock absent, `_STOPPED` attempt preserved. No
successful-result artifacts are required for the STOPPED attempt.

## 7. Singular-Schur STOPPED path

Test 51 uses the deterministic 37×37 fake Hessian with the exactly singular
`[[1,1],[1,1]]` nuisance block: gradient and Hessian both evaluate, the
solve-based Schur route raises the registered `StopRun("S-5", "schur-solve")`,
and finalization records **`gradient_evaluated: true`,
`hessian_evaluated: true`**, the exact stop code/gate, and the pre-solve
diagnostics (symmetry ok, full 37-eigenvalue spectrum, design rank 10). The
manifest contains no `regional` record — the informational pseudoinverse is
computed only after a successful solve and cannot substitute for the gating
route. No `complete/`, staging empty, lock absent.

## 8. Partial diagnostic preservation

`partial_diagnostics` is the same dict `_phase4_diagnose` builds incrementally,
attached to the STOPPED manifest by `_phase4_merge_progress(include_partial=
True)` only when `gates4` is absent (successful and gate-stopped attempts carry
the full record instead, avoiding duplication). Both STOPPED tests assert its
content; the successful-bundle artifact-set requirement is unchanged.

## 9. Exception finalization

`_phase4_run_diagnostics` catches StopRun raised anywhere after contract
validation, merges progress + partial diagnostics, records
`exception: {type, message, code, gate}`, and finalizes under
`attempts/<attempt>_STOPPED/`. The outer `_phase4_run` handlers do the same
for contract-phase stops and unexpected exceptions (which additionally record
the concrete exception type and message). `complete/` is never published on
any exceptional path; the lock is released by controlled finalization; the
exact successful artifact-set requirement is untouched.

## 10. Phase-4 review-v3 binding

`CANONICAL_APPROVED_PHASE4_REVIEW_REL` now points to
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v3.md`; the
heading contract (`# 1. Phase-4 review verdict`, exactly one
`**FINAL VERDICT: APPROVE**` line) is unchanged. CLI help, the manifest
review-gate labels (`AWAITING_PHASE4_REVIEW_V3_APPROVE` /
`PHASE4_REVIEW_V3_APPROVED`), configuration comments, and tests are updated
consistently. Test 52 proves: the synthetic exact review-v3 APPROVE passes
structurally; the v1 and v2 paths are rejected; the Phase-3 review-v6 path is
rejected with the dedicated message; and the REAL review-v2 body (APPROVE
AFTER FIXES) copied to the v3 path is rejected by the verdict parser. The
real review-v3 file was not created.

## 11. Stale string corrections

The `_phase4_run` refusal now reads "verified Git + Phase-4 review-v3 approval
gates"; the `run_phase4` docstring names the Phase-4-specific review-v3 gate
with v1/v2/v6 rejection; the module header and YAML comments are aligned; the
generic `--dry-run` help now describes Phases 1, 2, 3 AND 4 explicitly. Test
52 greps the live source: every remaining `review-v6` mention inside the
Phase-4 code is a rejection/never statement, and none claims authorization.

## 12. Test additions

Tests 50–52 (suite 49 → **52**): both exceptional STOPPED paths driven through
production finalization with true/false and true/true flags, exact stop
code/gate, partial-diagnostics preservation, no `complete/`, preserved
attempt, empty staging, released lock (G.1–G.8); review-v1/v2/v6 rejection,
synthetic v3 APPROVE pass, real-v2-body rejection (G.9–G.12); dry-run-help and
stale-string source assertions (G.13). No test calls the real gradient or
Hessian; all 49 prior tests are retained and passing.

## 13. Full no-Hessian suite

`pytest -q` → **52 passed** (~26–30 s), twice. `py_compile` clean for runner
and tests; YAML parses; `git diff --check` exit 0 (after trimming one EOF
blank line the checker caught).

## 14. Repeated exceptional-path tests

Tests 50+51 executed in five consecutive fresh pytest runs:
exit codes `0,0,0,0,0` (2 passed each run).

## 15. Phase-4 dry-run

Canonical `--phase 4` without `--execute-phase4`: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`; manifest `gradient_evaluated: false`,
`hessian_evaluated: false`, `optimizer_called: false`,
`execution_ready: false`, `review_gate: AWAITING_PHASE4_REVIEW_V3_APPROVE`;
`complete/` absent, lock absent, staging empty. Phase 5 refused (exit 2).

## 16. Phase-3 bundle regression

All accepted `complete/` artifact hashes equal the Phase-3 manifest record;
the deterministic bundle digest recomputes to
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`; the
manifest file hash is unchanged (`60eb1412…`). Nested repository clean at
`27756a0…`.

## 17. Prohibited-operation audit

No real gradient/Hessian (fake matrices only; dry-run flags false; structural
branch), no optimizer, no theta change, no Phase 5+ (refused), no
SE/post-estimation/welfare/synthetic recovery/EUROMOD/notebooks, no
dclaborsupply-monorepo edit, no accepted-evidence change, nothing committed.
Writes: preserved dry-run/test attempt evidence and this report.

## 18. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +43/−5
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +927/−17  (cumulative)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +665/−3   (cumulative)
 ?? docs/…/phase4_code_review_{v1,v2}.md (reviewer records)
 ?? docs/…/phase4_implementation_report_v1.md, phase4_remediation_report_{v1,v2}.md
 ?? outputs/…/attempts/… (preserved dry-run/test evidence)
```

`git diff --check` exit 0; index clean; HEAD `c7d558a` untouched.

## 19. Residual warnings

- `partial_diagnostics` can enlarge a STOPPED manifest by a few KB (gradient +
  spectrum lists); accepted as the cost of accurate exceptional evidence.
- The exceptional-path tests drive `_phase4_run_diagnostics` (the shared
  production body) rather than the full CLI, because the real contract requires
  the production inputs; the dry-run subprocess test continues to cover the
  CLI end-to-end.
- The `_phase4_run_diagnostics` input recheck is conditioned on the ctx
  carrying the production runtime map; production contexts always do, and
  fake-derivative test contexts intentionally omit it (documented seam,
  research-grade threat model).

## 20. Whether review v3 may begin

**YES.** Both review-v2 defects are closed with deterministic finalization
evidence, the approval gate is bound to the not-yet-existing review v3, and
the exact uncommitted state is ready for the narrow third independent
no-Hessian review.

## 21. Immediate next action

Independent Phase-4 review v3 of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict` at the
canonical v3 path: commit the reviewed state cleanly, then execute the single
real Phase-4 run via `--phase 4 --execute-phase4 --expected-mnl-head
<post-commit SHA> --expected-dclaborsupply-head 27756a0…
--approved-phase4-review …phase4_code_review_v3.md
--approved-phase4-review-sha256 <committed hash>`. Do not run
`--execute-phase4` before then.

**FINAL VERDICT: READY FOR PHASE-4 REVIEW V3** (no real derivatives; nothing
committed).
