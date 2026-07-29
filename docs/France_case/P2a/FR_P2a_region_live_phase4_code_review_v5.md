# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

# 2. Scope

This fifth review was limited to closure of review v4's staged-artifact evidence defect and regression confirmation for the previously approved Phase-4 numerical, provenance, and transaction logic.

No real gradient or Hessian was evaluated. No optimizer, real Phase-4 run, Phase 5 or later, inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebook route was run.

The code-level defect is closed. One explicit test requirement remains incomplete: the checked-in deterministic post-staging test reaches the inner `_phase4_run_diagnostics()` exception handler, not the `_phase4_run()` outer fallback identified in review v4. A separate temporary-root fake-only probe confirmed that the outer fallback works, but the repository suite does not enforce it.

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_phase4_code_review_v4.md`;
- `FR_P2a_region_live_phase4_remediation_report_v4.md`;
- the Phase-4 implementation report, reviews v1-v3, and remediation reports v1-v3;
- `FR_P2a_region_live_phase3_manager_acceptance_v1.md`;
- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`;
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`;
- the complete current Git diff; and
- all five files in the accepted Phase-3 `complete/` bundle.

MNL HEAD remains `c7d558a36489520a0f8487abf939d5300deaffb1`. The nested dclaborsupply HEAD and MNL gitlink both remain `27756a06ea189339aa82915ed2124628afed20eb`; the nested worktree is clean.

# 4. Shared artifact-staging state

PASS. `_phase4_run()` owns one mutable `progress` object containing derivative flags, the live diagnostic reference, `artifacts_staged`, and `diagnostics_artifact_name`. The same object is passed into `_phase4_run_diagnostics()` and remains visible to both its handlers and `_phase4_run()`'s outer handlers.

`artifacts_staged` starts false. It changes to true only after `_phase4_write_artifacts()` returns. That writer atomically writes all six required numerical artifacts:

- `hessian_free.csv`;
- `hessian_free.npy`;
- `hessian_eigenvalues.csv`;
- `regional_hessian_subblock.csv`;
- `regional_schur_complement.csv`; and
- `phase4_diagnostics.json`.

The authoritative artifact name is recorded only after those writes complete. A partial writer failure therefore remains a pre-staging exceptional path.

# 5. Exceptional evidence merge policy

PASS. All four Phase-4 post-acquisition exception handlers use `_merge_phase4_exception_evidence()`:

- the inner `StopRun` handler;
- the inner unexpected-exception handler;
- the outer `StopRun` handler; and
- the outer unexpected-exception handler.

No outer handler unconditionally attaches `partial_diagnostics`. The single policy always merges the live derivative flags and exact exception record, then branches only on `progress["artifacts_staged"]`.

When staging is false, the available live diagnostic record is retained as `partial_diagnostics`. When staging is true, any stale manifest copy is removed and the staged diagnostic artifact is named as the authority.

# 6. Post-staging exception path

PASS for implementation behavior; PARTIAL for checked-in regression coverage.

Test 55 deterministically raises on the first `_phase4_finalize()` call after all numerical artifacts are staged. It preserves a separate `STOPPED` attempt with:

- true/true derivative flags;
- exact `RuntimeError` type and message;
- S-0 / `unexpected`;
- the full staged numerical artifact set;
- no `complete/`;
- empty staging; and
- a released lock.

However, `_p4_stopped_run()` calls `_phase4_run_diagnostics()` directly. The forced exception is caught by that function's new inner unexpected-exception handler, and the second finalization succeeds. The test never invokes `_phase4_run()` and therefore does not force the original outer fallback. Its `calls["n"] == 2` assertion confirms the inner route rather than the outer route.

An independent temporary-root probe used only fake NumPy derivatives and forced two consecutive finalization exceptions so the second escaped the inner handler into `_phase4_run()`. The third finalization produced the expected safe result: exit 3, `STOPPED`, true/true flags, exact `RuntimeError` type/message, no manifest `partial_diagnostics`, the full-artifact authority label, retained `phase4_diagnostics.json`, no `complete/`, empty staging, and no lock. Thus the code works, but this fallback is not protected by a checked-in regression test.

# 7. Full diagnostic artifact authority

PASS. Once staging is complete, the manifest records:

- `diagnostic_evidence_status: FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT`;
- `diagnostic_artifact_authority: phase4_diagnostics.json`; and
- `diagnostic_artifact_staged: true`.

The label does not describe the evidence as partial. The retained `phase4_diagnostics.json` contains the full gradient, symmetry, 37-value spectrum, loading shares, design, regional subblock, Schur, gate, warning, and identification records. Derivative flags and exact exception evidence remain in the manifest.

# 8. Manifest deduplication

PASS. The staged branch explicitly removes any `partial_diagnostics` key. Test 55 proves that the stopped manifest contains no duplicate scientific record while the full `phase4_diagnostics.json` remains in the exact eight-file stopped bundle.

No retained staged diagnostic can be mistaken for a successful result: the manifest status is `STOPPED`, the stop is S-0 / `unexpected`, the evidence label names a stopped attempt, the bundle is under `attempts/`, and `complete/` is absent.

# 9. Authentication evidence

PASS. When artifacts have not been staged, tests 53 and 54 retain the live record and explicitly require these diagnostic families:

- `gradient_free`;
- `gradient_consistency_max_abs_dev`;
- `symmetry`;
- `eigen`;
- `loading_shares`;
- `design`;
- `regional`; and
- `gates`.

Runtime-map and input-recheck failures remain labelled `FAILED_AUTHENTICATION_ATTEMPT`, preserve true/true derivative flags, and retain exact S-8 gate evidence. The input-recheck test requires pre, accepted, and post hashes for every table entry and at least one explicit `ok: false` mismatch.

# 10. Phase-4 review-v5 binding

PASS. Real Phase-4 execution is bound exactly to:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v5.md`

The verifier requires the canonical path, supplied and recomputed SHA-256, expected MNL and nested HEADs, gitlink equality, fully clean worktrees, the exact first heading, and exactly one ordinary Markdown `**FINAL VERDICT: APPROVE**` line in the first section.

Tests prove that Phase-4 reviews v1-v4 and Phase-3 review-v6 are rejected, that the real review-v4 `APPROVE AFTER FIXES` body cannot authorize when copied to the v5 path, and that a synthetic exact review-v5 APPROVE document passes structurally.

This review is not exact APPROVE and therefore cannot authorize execution. The test-only remediation must bind the next candidate to Phase-4 review v6, or the later canonical Phase-4 review that ultimately returns exact APPROVE.

# 11. Numerical-logic preservation

PASS. The remediation leaves the accepted numerical contract unchanged:

- ordered 37-free / 47-full mapping with ten immutable pins;
- package-built negative-log-likelihood derivative route;
- raw symmetry tolerance `1e-8 * max_abs_H`;
- symmetrized spectral calculations;
- rank tolerance `1e-10 * max_abs_eigenvalue`;
- strict positive-definiteness requirements;
- condition tiers `<= 1e7`, `> 1e7 and <= 1e10`, and `> 1e10`;
- exact ten-name regional parameter block and design columns;
- design rank 10;
- raw regional-subblock positive definiteness;
- solve-based Schur complement and rank/positive-eigenvalue gates; and
- loading share at or above 0.5 as warning-only.

The immutable code constants still match YAML exactly. Fake-only numerical, mapping, boundary, regional, and transaction tests remain passing.

# 12. Transaction preservation

PASS. The Phase-4 transaction remains confined to `phase4_curvature_v1/`, with an exclusive lock, unique staging directory, separate attempts, immutable `complete/`, manifest-last hashing without self-hash, exact artifact-set validation, and atomic directory publication.

The post-staging test retains its stopped attempt separately, leaves `complete/` absent, empties staging, and releases the lock. The shared transaction still defaults to `PHASE_3_COMPLETE`; only Phase 4 supplies `PHASE_4_COMPLETE`. Existing Phase-3 transaction, collision, immutability, and publication tests pass.

# 13. Test adequacy

The permitted validation used the project virtual environment and no real derivative or optimizer:

- complete safety suite: `55 passed`;
- test 55: ten consecutive passing runs;
- tests 53 and 54: five consecutive passing grouped runs;
- independent grouped validation also passed tests 53-55 repeatedly;
- compile/import and YAML parsing: pass;
- `git diff --check`: pass.

Coverage is adequate for the code-level staged-artifact policy, authentication evidence, numerical gates, bundle provenance, review binding, and transaction behavior.

It is not complete for review question 12. The checked-in suite contains no deterministic test that reaches `_phase4_run()`'s outer post-staging exception fallback. Static inspection and the independent fake-only probe establish that the branch currently works, but future changes could regress it without failing test 55.

# 14. Phase-3 regression safety

PASS. The accepted Phase-3 directory still has exactly:

- `estimation_results.json`;
- `optimizer_diagnostics.json`;
- `phase3_console.log`;
- `phase3_manifest.json`; and
- `theta_estimated.csv`.

All four non-manifest hashes match the Phase-3 manifest. The deterministic bundle SHA-256 independently recomputes to:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

The manifest file SHA-256 remains `60eb1412cc14211a866d795e6bac3a7bde07c1f5879f4b000e066c2020fa8884`. The accepted complete directory has no Git diff. The authoritative 47-vector, pin handling, package revision, and Phase-3 transaction behavior remain unchanged.

# 15. Phase-4 dry-run safety

PASS. The canonical Phase-4 dry-run returned `PHASE_4_DRY_RUN_COMPLETE` and:

- `review_gate: AWAITING_PHASE4_REVIEW_V5_APPROVE`;
- `gradient_evaluated: false`;
- `hessian_evaluated: false`;
- `optimizer_called: false`;
- `execution_ready: false`;
- derivative route loaded but not evaluated;
- no `complete/`;
- empty staging; and
- no lock.

Phase 5 was refused with exit code 2.

# 16. Prohibited-operation audit

No real gradient or Hessian was evaluated. The post-staging and outer-fallback probes used fake NumPy derivative callables in temporary transaction roots. No optimizer, real Phase-4 execution, Phase 5 or later, inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebook route was run.

The nested package, accepted theta, accepted Phase-3 bundle, notebooks, and implementation files were not modified by this review. No commit was made.

# 17. Residual defects

One low-severity but review-blocking test defect remains:

- **The deterministic post-staging test does not reach the original outer `_phase4_run()` exception handler.** It tests the newly added inner handler only. The outer handler is correctly implemented and passed an independent fake-only probe, so this is not a current false-success or evidence-loss defect. It is nevertheless an explicit negative answer to review question 12 and leaves the corrected outer fallback without repository regression protection.

No residual numerical, provenance, publication, authentication-evidence, or code-level staged-artifact defect was found.

# 18. Required fixes

1. Modify test 55 or add a new fake-only test that invokes `_phase4_run()` and deterministically forces a post-staging exception to reach its outer unexpected-exception handler.
2. Assert on that outer route: true/true derivative flags; exact exception type/message; S-0 / `unexpected`; retained full `phase4_diagnostics.json`; its authority fields and non-partial label; absent manifest `partial_diagnostics`; exact stopped artifact set; no `complete/`; separate attempt; empty staging; and released lock.
3. Keep the existing inner-handler test or otherwise preserve its coverage; the two handlers should remain governed by the same merge policy.
4. Because this review is `APPROVE AFTER FIXES`, rebind real execution, CLI/YAML labels, and authorization tests to Phase-4 review v6, or the later canonical Phase-4 review that approves the exact corrected state.

# 19. Whether exact state may be committed

No, not as the final accepted Phase-4 execution checkpoint. The implementation behavior is substantively correct, but the exact state does not satisfy the explicit outer-path deterministic-test requirement. Add that narrow test, rebind the review gate, and review the exact resulting state before treating it as execution-ready.

# 20. Whether real Phase 4 may execute

No. The current exact review-v5 verifier must reject this `APPROVE AFTER FIXES` verdict. After the test-only closure, the exact corrected state must receive a subsequent Phase-4 `APPROVE`, be committed with that review, and satisfy the expected revision, gitlink, review-hash, package-identity, and clean-worktree gates before one real Phase-4 execution.

# 21. Immediate next action

Add the narrow fake-only `_phase4_run()` outer-fallback regression test, rebind approval to Phase-4 review v6, rerun the no-Hessian suite and canonical dry-run, and request one final narrow review. Do not execute the real gradient or Hessian before that review returns exact `APPROVE`.
