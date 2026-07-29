# FR P2a Region-Live — Phase-4 Remediation Report — v5

Date: 2026-07-29. Closes the single test-coverage requirement of
`FR_P2a_region_live_phase4_code_review_v5.md` §17–§18 (verdict APPROVE AFTER
FIXES): a checked-in deterministic regression of the OUTER `_phase4_run()`
post-staging unexpected-exception fallback, plus rebinding of the approval
gate to Phase-4 review v6. Test-only closure — no numerical, derivative,
provenance, input, transaction, or publication logic changed. No real
gradient or Hessian; no optimizer; theta untouched; nothing committed.

## 1. Remediation-v5 verdict

**READY FOR FINAL PHASE-4 REVIEW.** The outer fallback is now protected by a
deterministic fake-only regression (test 56) that invokes `_phase4_run()`
itself, forces a RuntimeError to escape the diagnostic-call boundary after the
full artifact set is staged, and verifies the identical staged-artifact
evidence contract via the single shared merge policy. Suite: **56 passed**
(twice); test 56 passes **20/20** consecutive runs, test 55 **10/10**, tests
53+54 **5/5**; `git diff --check` exit 0; canonical dry-run awaits
`PHASE4_REVIEW_V6` approval with all evaluation flags false; Phase-3 bundle
byte-identical.

## 2. Review-v5 requirement addressed

§17: the checked-in post-staging test (55) reached only the inner
`_phase4_run_diagnostics` handler; the outer `_phase4_run()` fallback —
correct in implementation and confirmed by the reviewer's probe — had no
repository regression protection. Closed per §18.1–.4 with a test-only change
plus the mandated review-v6 rebinding.

## 3. Files inspected

Read in full: code reviews v5 and v4, remediation report v4, the Phase-3
manager acceptance, the runner, the config, the safety tests, and the complete
current Git diff (HEAD `c7d558a36489520a0f8487abf939d5300deaffb1`; nested HEAD
= gitlink `27756a06ea189339aa82915ed2124628afed20eb`, clean).

## 4. Files modified

1. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+860/−3 cumulative):
   test 56 added; tests 42/52 rebound to the Phase-4 review-v6 contract; the
   Phase-3-review-v6 stale-string sweep narrowed to its actual intent now that
   the Phase-4 approval document is itself named v6.
2. `scripts/p2a/run_p2a_regionlive_rebuild.py` (+988/−17 cumulative;
   this round: review-binding strings and labels ONLY — no logic change).
3. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+43/−5; comment-only
   binding updates).

Created: this report. All earlier reports and reviews preserved unchanged.
The real Phase-4 review-v6 file was NOT created.

## 5. Outer-handler regression design

Test 56 monkeypatches only test seams around the production orchestration:
`CANONICAL_PHASE4_ROOT` → a temporary root (the fake-safe temporary-root
route); `_verify_package_identity` → a stub record; `_phase4_contract` → the
fake-derivative context; and the diagnostic-call boundary
(`_phase4_run_diagnostics`) → a fake that receives the GENUINE orchestration
transaction and progress objects, runs the production `_phase4_diagnose`
(fake derivatives), stages the complete artifact set with the production
`_phase4_write_artifacts`, sets `artifacts_staged = true` and
`diagnostics_artifact_name = phase4_diagnostics.json` on the shared progress
state, and raises `RuntimeError("forced outer post-staging failure")`.
`_phase4_finalize` is NOT monkeypatched — the outer handler's finalization is
the production route.

## 6. Outer-handler execution path

The test calls `runner._phase4_run(args(dry_run=False), cfg, {verified,
execution_ready})` directly; the raised RuntimeError escapes the boundary and
is caught by `_phase4_run()`'s outer unexpected-exception handler. Asserted:
return code 3 (controlled unexpected failure); manifest `mode: "phase4
curvature diagnostics"` (the call demonstrably went through `_phase4_run`);
status `STOPPED`; stop `S-0`/`unexpected`; exception type `RuntimeError` with
the exact message; `gradient_evaluated`/`hessian_evaluated` true/true.

## 7. Staged diagnostic authority

The finalized manifest records `diagnostic_artifact_staged: true`,
`diagnostic_artifact_authority: phase4_diagnostics.json`, and
`diagnostic_evidence_status: FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT`.
The preserved `phase4_diagnostics.json` is parsed from the STOPPED attempt and
contains the complete fake scientific record (gradient, symmetry, 37-value
spectrum, loading shares, design, regional, gates); the attempt directory
carries the exact staged artifact set plus `phase4_manifest.json`.

## 8. Manifest deduplication

`partial_diagnostics` is asserted absent from the outer-route STOPPED
manifest — the staged artifact is the sole authoritative record on this path,
exactly as on the inner route.

## 9. Inner-handler coverage preservation

Test 55 is retained unchanged (inner `_phase4_run_diagnostics` handler,
one-shot finalize failure) and still passes 10/10 consecutive runs; tests
53/54 (pre-staging authentication paths) still pass 5/5. Both exceptional
handlers therefore remain covered independently.

## 10. Shared merge-policy verification

Test 56 wraps the production `_merge_phase4_exception_evidence` in a
delegating spy: exactly one merge fires on the outer route, with the
`RuntimeError` instance, producing field-identical staged-branch output to the
inner route of test 55. No merge logic is duplicated in the test or the
runner — the outer handler routes through the same single policy.

## 11. Phase-4 review-v6 binding

`CANONICAL_APPROVED_PHASE4_REVIEW_REL` now points to
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v6.md`; CLI help,
YAML comments, module header, and the manifest labels
(`AWAITING_PHASE4_REVIEW_V6_APPROVE` / `PHASE4_REVIEW_V6_APPROVED`) are
updated; the dry-run reports `AWAITING_PHASE4_REVIEW_V6_APPROVE` (verified
live). Test 52 proves: a synthetic exact Phase-4 review-v6 APPROVE passes
structurally; the Phase-4 v1–v5 paths are all rejected; the PHASE-3 review-v6
is rejected with its dedicated message (the two same-named documents remain
distinct canonical paths); and the REAL review-v5 body (APPROVE AFTER FIXES)
copied to the v6 path is rejected by the parser. The real Phase-4 review-v6
file does not exist and was not created.

## 12. Numerical-logic preservation

No numerical, derivative, provenance, input, transaction, or publication code
changed this round — the runner diff is binding strings/labels only. All
accepted values (bundle hash `2cf23764…`, theta, 37/10 map, regional names,
symmetry/rank/PD/condition gates, Schur formula, loading-share
interpretation) are untouched.

## 13. Transaction preservation

Untouched. Test 56 additionally re-proves on the outer route: STOPPED attempt
preserved separately under `attempts/`, exact staged set + manifest, no
`complete/`, empty staging, released lock.

## 14. Test additions

Test 56 (suite 55 → **56**); tests 42/52 rebound; the stale-string sweep
narrowed (documented in-test) because the Phase-4 approval document is now
itself named review v6 — the sweep still forbids any un-rejected "Phase-3
review-v6" claim in Phase-4 code and asserts the two historically stale
strings remain absent. No test calls the real gradient or Hessian.

## 15. Repeated outer-handler test

Test 56: **20/20** consecutive fresh pytest runs, exit codes all 0.
Test 55: **10/10**. Tests 53+54: **5/5**.

## 16. Full no-Hessian suite

`pytest -q` → **56 passed** (~27 s), twice. `py_compile` clean for runner and
tests; YAML parses; `git diff --check` exit 0 (after trimming one EOF blank
line the checker caught).

## 17. Phase-4 dry-run

Canonical `--phase 4` without `--execute-phase4`: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`; `gradient_evaluated: false`,
`hessian_evaluated: false`, `optimizer_called: false`,
`execution_ready: false`, `review_gate: AWAITING_PHASE4_REVIEW_V6_APPROVE`;
`complete/` absent, lock absent, staging empty. Phase 5 refused (exit 2).

## 18. Phase-3 bundle regression

All accepted `complete/` artifact hashes equal the Phase-3 manifest record;
the deterministic bundle digest recomputes to
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`; the
manifest hash is unchanged (`60eb1412…`). Nested repository clean at
`27756a0…`; no notebook, theta, package, accepted estimate, or Phase-3
evidence changed.

## 19. Prohibited-operation audit

No real gradient/Hessian (fake matrices in temporary roots only; dry-run flags
false), no optimizer, no theta change, no Phase 5+ (refused), no
inference/post-estimation/welfare/synthetic recovery/EUROMOD/notebooks, no
dclaborsupply-monorepo edit, no prior report altered, nothing committed.
Writes: preserved attempt evidence and this report.

## 20. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +43/−5
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +988/−17  (cumulative)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +860/−3   (cumulative)
 ?? docs/…/phase4_code_review_{v1..v5}.md (reviewer records)
 ?? docs/…/phase4_{implementation,remediation_v1..v5} reports
 ?? outputs/…/attempts/… (preserved dry-run/test evidence)
```

`git diff --check` exit 0; index clean; HEAD `c7d558a` untouched.

## 21. Residual warnings

- The Phase-4 approval document and the Phase-3 approval document now share
  the "review v6" ordinal; they remain distinct canonical paths and the gate
  rejects the Phase-3 file explicitly, but reviewers and operators should use
  the full filenames to avoid confusion.
- Test 56 passes a crafted verified gates-record to the private `_phase4_run`
  body (the documented research-grade test seam); the public CLI boundary
  remains covered by the subprocess dry-run and execution-gate batteries.
- The cumulative uncommitted diff spans five remediation rounds; the final
  review evaluates the aggregate state.

## 22. Whether final Phase-4 review may begin

**YES.** The last review-blocking requirement is closed with a deterministic,
repeatedly-passing outer-fallback regression; the production implementation is
substantively accepted per review v5; the exact uncommitted state is ready for
the final narrow Phase-4 review.

## 23. Immediate next action

Final independent Phase-4 review (v6) of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict` at the
canonical Phase-4 v6 path: commit the reviewed state cleanly, then execute the
single real Phase-4 run via `--phase 4 --execute-phase4 --expected-mnl-head
<post-commit SHA> --expected-dclaborsupply-head 27756a0…
--approved-phase4-review …phase4_code_review_v6.md
--approved-phase4-review-sha256 <committed hash>`. Do not run
`--execute-phase4` before then.

**FINAL VERDICT: READY FOR FINAL PHASE-4 REVIEW** (no real derivatives;
nothing committed).
