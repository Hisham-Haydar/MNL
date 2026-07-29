# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

# 2. Scope

This was a narrow, independent review of the review-v3 remediation for Phase-4 diagnostic preservation. It checked the two post-evaluation authentication failures, the exceptional-finalization paths, review-v4 approval binding, and preservation of the previously reviewed numerical and transaction contracts.

The review did not evaluate the real gradient or Hessian, invoke an optimizer, execute real Phase 4, run Phase 5 or later, or run inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebooks.

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_phase4_implementation_report_v1.md`
- Phase-4 code reviews v1, v2, and v3
- Phase-4 remediation reports v1, v2, and v3
- `FR_P2a_region_live_phase3_manager_acceptance_v1.md`
- `scripts/p2a/run_p2a_regionlive_rebuild.py`
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`
- every file in the accepted Phase-3 `complete/` bundle
- the complete current Git diff and repository state

The MNL HEAD is `c7d558a36489520a0f8487abf939d5300deaffb1`. The nested HEAD and MNL gitlink are both `27756a06ea189339aa82915ed2124628afed20eb`.

# 4. Live diagnostic lifecycle

The review-v3 defect is closed for the two intended authentication paths. `_phase4_diagnose()` creates one mutable diagnostic dictionary and immediately stores the same object in `progress["partial_diagnostics"]`. Gradient, Hessian, symmetry, spectrum, design, regional-subblock, Schur, loading-share, and gate results are added to that live object.

The derivative flags are updated immediately after each successful fake derivative call. A later exception does not reset them. The live object remains available to `_phase4_merge_progress()` before `phase4_diagnostics.json` is staged.

Artifact persistence in `_phase4_run_diagnostics()` now uses an explicit local `artifacts_staged` state. The presence of `gates4` is no longer used as a proxy for persistence.

# 5. Runtime-map authentication failure

The post-evaluation runtime-map fingerprint path is correctly finalized as a controlled `STOPPED` attempt:

- stop code and gate are exactly `S-8` / `runtime-map`;
- `gradient_evaluated` and `hessian_evaluated` remain `true`;
- exception type and message are persisted;
- `diagnostic_evidence_status` is `FAILED_AUTHENTICATION_ATTEMPT`;
- the retained live record contains gradient diagnostics, Hessian symmetry and spectrum, regional-design rank, regional-subblock and Schur diagnostics, loading information, and the gate summary;
- `complete/` is not created;
- the stopped attempt is retained under `attempts/`;
- staging is empty and the lock is released after finalization.

Test 53 exercises `_phase4_run_diagnostics()` and transaction finalization with fake derivatives; it is not merely an isolated helper test.

# 6. Input-hash authentication failure

The post-evaluation input-recheck path is also correctly finalized:

- stop code and gate are exactly `S-8` / `input-recheck`;
- both derivative flags remain `true`;
- the evidence is labelled `FAILED_AUTHENTICATION_ATTEMPT`;
- the complete pre-evaluation, post-evaluation, and accepted hash values are retained for each checked input;
- the live scientific diagnostics remain attached to the stopped manifest;
- no result is published to `complete/`;
- the attempt is preserved, staging is emptied, and the lock is released.

Test 54 drives the full fake-derivative orchestration and controlled finalization after mutating an authenticated input. It verifies the mismatch and the retained hash evidence.

# 7. Failed-authentication evidence labelling

Both post-evaluation authentication failures use the exact, unambiguous label `FAILED_AUTHENTICATION_ATTEMPT`. They remain `STOPPED` attempts with an explicit S-8 stop record and cannot satisfy successful-bundle publication.

The retained diagnostics are therefore evidence about a failed authentication attempt, not an accepted Phase-4 curvature result. They cannot be mistaken for a successful result unless a reader disregards the manifest status, stop record, evidence label, directory location, and absence of `complete/`.

# 8. Exceptional finalization

For failures before artifact staging, `_phase4_run_diagnostics()` preserves the live diagnostic record through `partial_diagnostics`. Controlled finalization preserves the exact stop code, gate, exception type, exception message, derivative-progress flags, and available diagnostics. The two reviewed authentication paths finalize cleanly and independently under `attempts/`.

Successful-result artifact requirements remain unchanged. The authentication remediation does not relax the exact artifact set, manifest-last rule, directory-level publication, or successful-status checks.

# 9. Staged-artifact exceptional path

One residual defect remains after the narrow authentication fix. The explicit `artifacts_staged` state is local to `_phase4_run_diagnostics()`. If all Phase-4 artifacts have been staged and a later unexpected exception escapes to `_phase4_run()`, the outer exception handler unconditionally calls `_phase4_merge_progress(..., include_partial=True)`.

A fake-derivative, temporary-root reproduction forced an exception at the first finalization call after confirming that `phase4_diagnostics.json` already existed. The resulting stopped attempt was transactionally safe: `complete/` was absent, the staged diagnostic file was retained, staging was empty, and the lock was released. However, the manifest also contained a duplicate `partial_diagnostics` record and labelled it `STOPPED_ATTEMPT_PARTIAL_EVIDENCE`.

Consequently, question 13 is not fully satisfied. When the full diagnostic artifact already exists, omission of duplicate partial diagnostics is not reliably enforced, and the evidence label incorrectly describes the duplicated full record as partial. This does not create a false success or lose scientific diagnostics, but it leaves the exceptional evidence contract internally inconsistent and contradicts the review-v3 remediation report.

# 10. Phase-4 review-v4 binding

The real Phase-4 execution gate is bound to the exact canonical path:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v4.md`

The verifier requires the canonical path, supplied SHA-256, exact first heading, and exactly one ordinary Markdown `**FINAL VERDICT: APPROVE**` line in that first section. Phase-4 reviews v1, v2, and v3 and Phase-3 review-v6 cannot authorize Phase 4. A synthetic exact review-v4 APPROVE document passes the structural parser.

Because this review is `APPROVE AFTER FIXES`, it must not authorize real execution. The remediation should bind the next execution candidate to Phase-4 review v5, or to the later canonical review version that ultimately returns `APPROVE`.

# 11. Numerical-logic preservation

The current diff preserves the previously reviewed numerical contract:

- the explicit ordered vector remains 37 free parameters with 10 immutable pins in the 47-name full vector;
- the Hessian remains the Hessian of package-built negative log likelihood;
- raw-Hessian symmetry tolerance remains `1e-8 * max_abs_H`;
- spectral rank tolerance remains `1e-10 * max_abs_eigenvalue`;
- full, raw regional-subblock, and Schur positive-definiteness requirements are unchanged;
- condition classifications remain clean through `1e7`, warning above `1e7` through `1e10`, and failure above `1e10`;
- the canonical ten regional names and design-rank requirement remain unchanged;
- the Schur complement still uses the solve-based formula without an explicit inverse;
- regional loading share at or above 0.5 remains warning-only.

The no-Hessian mapping and numerical-gate tests passed. No accepted threshold, parameter order, pin, or status was weakened for the remediation.

# 12. Transaction preservation

The normal success and the two authentication-failure paths retain directory-level transaction isolation. A successful Phase-3 or Phase-4 `complete/` result cannot be overwritten. Stopped attempts are preserved separately, the manifest is written last and excluded from its own artifact hash map, and controlled finalization empties staging and releases the lock.

The shared Phase-3 transaction tests continue to pass. The residual staged-artifact issue is evidence duplication and labelling in an unexpected Phase-4 exception path; it does not publish a failed attempt or mutate Phase 3.

# 13. Test adequacy

Validation used the project virtual environment and did not call the real gradient, Hessian, or optimizer:

- the complete safety suite passed: `54 passed`;
- tests 53 and 54 passed in five repeated runs;
- the mapping and numerical subset passed: `19 passed`;
- Python compile/import, YAML parsing, and constant checks passed;
- `git diff --check` passed.

Tests 53 and 54 exercise transaction finalization and retain representative fields from the full scientific record. They do not cover the post-staging unexpected-exception branch identified in section 9. They should also assert a more explicit required key set for the retained regional-subblock, Schur, loading-share, and gate records rather than only representative fields.

# 14. Phase-3 regression safety

The accepted Phase-3 bundle still has exactly the required five files and remains byte-identical. Its deterministic bundle SHA-256 is:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

The authoritative theta JSON is unchanged, and its 47 values remain bitwise consistent with the optimizer diagnostics. The Phase-3 complete directory has no Git diff. Phase-3 mapping, bundle, execution, and transaction tests remain passing.

# 15. Phase-4 dry-run safety

The canonical Phase-4 dry-run completed without derivative or optimizer evaluation. It reported:

`AWAITING_PHASE4_REVIEW_V4_APPROVE`

The gradient, Hessian, and optimizer flags were all false. It did not create `complete/`; the stopped/dry-run attempt finalized with empty staging and no retained lock. Phase 5 remains refused.

# 16. Prohibited-operation audit

No real gradient or Hessian was evaluated. No optimizer was invoked. Phase 4 was not executed for real. Phase 5 or later, clustered inference, post-estimation, welfare, synthetic recovery, EUROMOD, and notebooks were not run.

Package source, notebooks, accepted theta, and the accepted Phase-3 complete bundle were not modified. No commit was made.

# 17. Residual defects

One review-blocking defect remains:

- **Medium — staged-artifact state is not propagated to outer exceptional finalization.** After full artifacts are staged, an unexpected exception handled by `_phase4_run()` can duplicate the complete diagnostic record in the manifest as `partial_diagnostics` and label it `STOPPED_ATTEMPT_PARTIAL_EVIDENCE`. The attempt remains safely stopped and all evidence is preserved, but the manifest is redundant and semantically inaccurate.

One associated test gap remains:

- **Low — no test forces an exception after full Phase-4 artifact staging.** The current tests therefore cannot enforce the intended “staged file is authoritative; no duplicate partial record” contract.

# 18. Required fixes

1. Propagate `artifacts_staged` through shared Phase-4 progress state, or catch later exceptions where that state remains available. Outer exceptional finalization must include `partial_diagnostics` only when `phase4_diagnostics.json` was not successfully staged.
2. When the full diagnostic artifact has been staged, preserve that file as the authoritative complete record and use an evidence label that does not call the record partial.
3. Add a fake-derivative test that forces an exception after artifact staging and verifies: `STOPPED`; exact exception evidence; full `phase4_diagnostics.json`; no duplicate manifest `partial_diagnostics`; no `complete/`; a separate attempt; empty staging; and released lock.
4. Strengthen tests 53 and 54 with an explicit retained-diagnostic key contract covering the regional subblock, Schur diagnostics, loading shares, and gate summary.
5. Rebind real execution to Phase-4 review v5, or the subsequent canonical Phase-4 review that evaluates the fix and returns exact `APPROVE`.

# 19. Whether exact state may be committed

No, not as the accepted Phase-4 execution state. The current implementation safely stops the reviewed failures, but the exact state still violates the staged-artifact evidence contract and lacks its regression test. The narrow fix and next approving review should be included before the Phase-4 execution checkpoint is committed.

# 20. Whether real Phase 4 may execute

No. This review is not an exact `APPROVE`, and the current approval verifier must therefore refuse it. Real Phase 4 may execute once only after the required fix, passing no-Hessian tests, an exact approving subsequent Phase-4 review, the reviewed commits and hashes, matching gitlink, and clean-worktree gates are all in place.

# 21. Immediate next action

Implement the narrow staged-artifact state propagation and regression test, rebind authorization to Phase-4 review v5, rerun the no-Hessian suite and dry-run, and request the next narrow independent review. Do not execute the real gradient or Hessian before that review returns exact `APPROVE`.
