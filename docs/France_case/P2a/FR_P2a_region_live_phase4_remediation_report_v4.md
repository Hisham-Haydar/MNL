# FR P2a Region-Live — Phase-4 Remediation Report — v4

Date: 2026-07-29. Applies the required fixes of
`FR_P2a_region_live_phase4_code_review_v4.md` §17–§18 (verdict APPROVE AFTER
FIXES): shared artifact-staging state, a single exceptional-evidence merge
policy, the post-staging exception regression test, strengthened
authentication-test key contracts, and rebinding to Phase-4 review v5. No real
gradient or Hessian; no optimizer; theta untouched; no Phase 5+;
dclaborsupply-monorepo and the accepted Phase-3 bundle unmodified; nothing
committed.

## 1. Remediation-v4 verdict

**READY FOR PHASE-4 REVIEW V5.** Artifact-staging state now lives in the
orchestration-owned progress object and every exceptional finalization path —
inside the diagnostic body and in both outer handlers — consults it through
one shared merge policy. A post-staging exception finalizes with the staged
`phase4_diagnostics.json` as the sole authoritative record (no duplicate
manifest copy, non-partial label, explicit authority fields). Suite: **55
passed**; the new post-staging test passes 10/10 consecutive runs and tests
53/54 pass 5/5; `git diff --check` exit 0; canonical dry-run awaits
`PHASE4_REVIEW_V5` approval with all evaluation flags false; Phase-3 bundle
byte-identical.

## 2. Review-v4 defect addressed

§17 (Medium): `artifacts_staged` was local to `_phase4_run_diagnostics`, so a
post-staging unexpected exception reaching `_phase4_run` unconditionally
attached a duplicate `partial_diagnostics` labelled
`STOPPED_ATTEMPT_PARTIAL_EVIDENCE`. §17 (Low): no test forced an exception
after full artifact staging. Both fixed per §18.1–.5.

## 3. Files inspected

Read in full: code review v4, remediation report v3, code review v3, the
Phase-3 manager acceptance, the runner, the config, the safety tests, and the
complete current Git diff (HEAD `c7d558a36489520a0f8487abf939d5300deaffb1`;
nested HEAD = gitlink `27756a06ea189339aa82915ed2124628afed20eb`, clean).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (cumulative uncommitted
   +988/−17): shared staging state, `_merge_phase4_exception_evidence`,
   handler rewiring, review-v5 rebinding.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+43/−5): comment-only
   v4→v5 corrections; no threshold or anchor change.
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+787/−3): test 55 added,
   tests 53/54 strengthened, tests 42/52 rebound; all 54 prior tests retained.

Created: this report. All earlier reports and reviews preserved unchanged. The
real review-v5 file was NOT created.

## 5. Shared artifact-staging state

The `_phase4_run`-owned progress object now initializes exactly:
`gradient_evaluated: false`, `hessian_evaluated: false`,
`partial_diagnostics: null`, `artifacts_staged: false`,
`diagnostics_artifact_name: null`. Immediately after
`_phase4_write_artifacts` returns — i.e. only once every required numerical
artifact including `phase4_diagnostics.json` has been written —
`artifacts_staged` flips to true and `diagnostics_artifact_name` records
`"phase4_diagnostics.json"`. The object is visible to
`_phase4_run_diagnostics`, both outer `_phase4_run` handlers, and final
manifest construction.

## 6. Exceptional evidence merge policy

`_merge_phase4_exception_evidence(manifest, progress, stop_or_exc)` is the
single policy used by every Phase-4 exception handler. It merges the
derivative flags and the exception record (type/message, plus code/gate for
StopRun), then decides evidence retention ONLY on
`progress["artifacts_staged"]`: when false, the live record attaches as
`partial_diagnostics` with the pre-staging label
(`FAILED_AUTHENTICATION_ATTEMPT` for runtime-map/input-recheck,
`STOPPED_ATTEMPT_PARTIAL_EVIDENCE` otherwise); when true, any stale
`partial_diagnostics` key is removed and the manifest records
`diagnostic_evidence_status: FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT`,
`diagnostic_artifact_authority: phase4_diagnostics.json`, and
`diagnostic_artifact_staged: true`. The old unconditional
`include_partial=True` calls in the outer handlers are gone; no branch decides
retention without consulting the shared state.

## 7. Post-staging exception path

`_phase4_run_diagnostics` additionally catches unexpected non-StopRun
exceptions (review-v4 §18.1's sanctioned alternative), so post-staging
failures finalize where the shared state is guaranteed live; the outer
handlers apply the identical policy as a fallback. Test 55 forces the failure
deterministically by monkeypatching the first finalization call after staging
(one-shot raiser, then the real function): the attempt finalizes STOPPED
(exit 3), `RuntimeError` + exact message persisted, `S-0`/`unexpected` stop,
true/true flags, and the preserved attempt directory contains the exact
eight-file set including the full `phase4_diagnostics.json`.

## 8. Full diagnostic artifact authority

In the staged branch the staged `phase4_diagnostics.json` is the sole
authoritative scientific record: test 55 parses it from the preserved STOPPED
attempt and asserts the full key set (gradient, symmetry, 37-eigenvalue
spectrum, loading shares, design, regional, gates) while the manifest names it
as `diagnostic_artifact_authority` with `diagnostic_artifact_staged: true`.

## 9. Manifest deduplication

Test 55 asserts `partial_diagnostics` is absent from the post-staging STOPPED
manifest, and the merge policy actively pops any stale key. The evidence label
in this branch never says "partial". Pre-staging paths (tests 50/51/53/54) are
unchanged and still attach the labelled live record.

## 10. Authentication-test strengthening

Tests 53 and 54 now assert the explicit minimum retained-key contract —
`gradient_free`, `gradient_consistency_max_abs_dev`, `symmetry`, `eigen`,
`loading_shares`, `design`, `regional`, `gates` — on top of the existing value
assertions. Test 54 additionally asserts the complete pre/accepted/post hash
evidence for every checked input and at least one `ok: false` entry. All
existing transaction and evidence-label assertions are retained.

## 11. Phase-4 review-v5 binding

`CANONICAL_APPROVED_PHASE4_REVIEW_REL` now points to
`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v5.md`; CLI help,
YAML comments, module header, and the manifest labels
(`AWAITING_PHASE4_REVIEW_V5_APPROVE` / `PHASE4_REVIEW_V5_APPROVED`) are
updated consistently, and the dry-run reports
`AWAITING_PHASE4_REVIEW_V5_APPROVE` (verified live). Test 52 proves: the
synthetic exact review-v5 APPROVE passes structurally; the v1, v2, v3 AND v4
paths are rejected; the Phase-3 review-v6 is rejected with its dedicated
message; and the REAL review-v4 body (APPROVE AFTER FIXES) copied to the v5
path is rejected by the parser. The real review-v5 file does not exist and
was not created.

## 12. Numerical-logic preservation

Unchanged: accepted bundle hash `2cf23764…`; accepted theta; 37-free/10-pin
map; the ten regional names; derivative construction; symmetry 1e-8; rank
1e-10; strict PD gates; condition 1e7/1e10 tiers; the solve-based Schur
formula; the warning-only loading-share interpretation. Only exceptional
evidence bookkeeping changed.

## 13. Transaction preservation

Untouched: the Phase-4 artifact set, successful publication rules,
manifest-last + no-self-hash, lock/staging/attempts/immutable `complete/`
layout, overwrite refusal, and the shared transaction's Phase-3 default.
Phase-3/Phase-4 transaction batteries pass unchanged; test 55 additionally
confirms the STOPPED bundle carries the exact eight-file set.

## 14. Test additions

Test 55 (suite 54 → **55**): the deterministic post-staging exception
regression per review-v4 §18.3, driving production finalization with fake
derivatives only. Tests 53/54 strengthened per §18.4; tests 42/52 rebound per
§18.5. No test calls the real gradient or Hessian; all 54 prior tests are
retained and passing.

## 15. Full no-Hessian suite

`pytest -q` → **55 passed** (~27 s), twice. `py_compile` clean; YAML parses;
`git diff --check` exit 0 (after trimming one EOF blank line the checker
caught).

## 16. Repeated exceptional-path tests

Test 55: **10/10** consecutive fresh runs (exit codes all 0). Tests 53+54:
**5/5** consecutive fresh runs (exit codes all 0).

## 17. Phase-4 dry-run

Canonical `--phase 4` without `--execute-phase4`: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`; `gradient_evaluated: false`,
`hessian_evaluated: false`, `optimizer_called: false`,
`execution_ready: false`, `review_gate: AWAITING_PHASE4_REVIEW_V5_APPROVE`;
`complete/` absent, lock absent, staging empty. Phase 5 refused (exit 2).

## 18. Phase-3 bundle regression

All accepted `complete/` artifact hashes equal the Phase-3 manifest record;
the deterministic bundle digest recomputes to
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`; the
manifest hash is unchanged (`60eb1412…`). Nested repository clean at
`27756a0…`; no notebook, package, theta, estimate, or accepted evidence
changed.

## 19. Prohibited-operation audit

No real gradient/Hessian (fake matrices only; dry-run flags false), no
optimizer, no theta change, no Phase 5+ (refused), no
inference/post-estimation/welfare/synthetic recovery/EUROMOD/notebooks, no
dclaborsupply-monorepo edit, no prior report altered, nothing committed.
Writes: preserved attempt evidence and this report.

## 20. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +43/−5
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +988/−17  (cumulative)
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +787/−3   (cumulative)
 ?? docs/…/phase4_code_review_{v1..v4}.md (reviewer records)
 ?? docs/…/phase4_{implementation,remediation_v1..v4} reports
 ?? outputs/…/attempts/… (preserved dry-run/test evidence)
```

`git diff --check` exit 0; index clean; HEAD `c7d558a` untouched.

## 21. Residual warnings

- If `_phase4_finalize` itself fails twice (forced only via the one-shot test
  monkeypatch; a real double failure would be an I/O-level fault), the second
  exception escapes to `_phase4_run`'s outer handler, which applies the same
  policy and finalizes a third time; a triple failure would leave the lock as
  the intentional crash fail-safe.
- The gates4 summary remains in the manifest alongside the staged-artifact
  authority fields (it is a summary, not the scientific record; the authority
  field disambiguates).
- The cumulative uncommitted diff now spans four remediation rounds; review v5
  evaluates the aggregate state.

## 22. Whether review v5 may begin

**YES.** Both review-v4 defects are closed with deterministic finalization
evidence, the gate is bound to the not-yet-existing review v5, and the exact
uncommitted state is ready for the narrow fifth independent no-Hessian review.

## 23. Immediate next action

Independent Phase-4 review v5 of this exact diff. On one exact
`**FINAL VERDICT: APPROVE**` under `# 1. Phase-4 review verdict` at the
canonical v5 path: commit the reviewed state cleanly, then execute the single
real Phase-4 run via `--phase 4 --execute-phase4 --expected-mnl-head
<post-commit SHA> --expected-dclaborsupply-head 27756a0…
--approved-phase4-review …phase4_code_review_v5.md
--approved-phase4-review-sha256 <committed hash>`. Do not run
`--execute-phase4` before then.

**FINAL VERDICT: READY FOR PHASE-4 REVIEW V5** (no real derivatives; nothing
committed).
