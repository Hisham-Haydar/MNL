# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE**

# 2. Scope

This final narrow review assessed closure of the sole review-v5 blocker: checked-in deterministic coverage of `_phase4_run()`'s outer post-staging unexpected-exception fallback. It also confirmed preservation of the previously approved Phase-4 implementation, numerical gates, provenance binding, and transaction behavior.

No real gradient or Hessian was evaluated. No optimizer, real Phase-4 run, Phase 5 or later, inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebook route was run.

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_phase4_code_review_v5.md`;
- `FR_P2a_region_live_phase4_remediation_report_v5.md`;
- all prior Phase-4 implementation, remediation, and review reports;
- `FR_P2a_region_live_phase3_manager_acceptance_v1.md`;
- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`;
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`;
- the complete current Git diff; and
- all five files in the accepted Phase-3 `complete/` bundle.

The reviewed MNL base HEAD is `c7d558a36489520a0f8487abf939d5300deaffb1`. The nested dclaborsupply HEAD and MNL gitlink both remain `27756a06ea189339aa82915ed2124628afed20eb`; the nested worktree is clean.

# 4. Outer-handler regression path

PASS. New test 56, `test_56_outer_phase4_run_post_staging_fallback`, invokes `runner._phase4_run()` itself with a verified, execution-ready test record and a temporary Phase-4 transaction root.

The test replaces `_phase4_run_diagnostics()` with a deterministic diagnostic-call boundary. That boundary:

1. calls the production `_phase4_diagnose()` with fake NumPy gradient and Hessian callables;
2. stages every numerical artifact through the production `_phase4_write_artifacts()`;
3. updates the genuine orchestration-owned progress object;
4. raises `RuntimeError("forced outer post-staging failure")`.

Because the complete inner function is replaced, its exception handlers cannot intercept the injected error. The error escapes the diagnostic-call boundary and necessarily reaches `_phase4_run()`'s outer `except Exception` fallback.

The manifest's production mode and the merge-policy spy independently demonstrate that `_phase4_run()` and its outer fallback were reached. The spy records exactly one merge with the `RuntimeError`.

# 5. Shared progress state

PASS. `_phase4_run()` creates the progress dictionary and passes that same object into the test boundary. `_phase4_diagnose()` updates it immediately after the fake gradient and Hessian calls, producing:

- `gradient_evaluated: true`;
- `hessian_evaluated: true`; and
- a live full diagnostic dictionary.

After the production artifact writer returns, the boundary sets:

- `artifacts_staged: true`; and
- `diagnostics_artifact_name: phase4_diagnostics.json`.

Those values are visible unchanged to the outer handler before it merges exceptional evidence.

# 6. Staged diagnostic authority

PASS. Before the exception, the production writer creates all six numerical artifacts:

- `hessian_free.csv`;
- `hessian_free.npy`;
- `hessian_eigenvalues.csv`;
- `regional_hessian_subblock.csv`;
- `regional_schur_complement.csv`; and
- `phase4_diagnostics.json`.

The retained `phase4_diagnostics.json` is parsed from the stopped attempt and contains the complete fake scientific record: gradient, symmetry, 37-value spectrum, loading shares, design diagnostics, regional-subblock diagnostics, Schur diagnostics, and gate summary.

The manifest identifies that file as the sole authoritative scientific record through:

- `diagnostic_artifact_staged: true`;
- `diagnostic_artifact_authority: phase4_diagnostics.json`; and
- `diagnostic_evidence_status: FULL_DIAGNOSTIC_ARTIFACT_STAGED_STOPPED_ATTEMPT`.

# 7. Exceptional manifest correctness

PASS. The outer-handler STOPPED manifest records:

- `gradient_evaluated: true`;
- `hessian_evaluated: true`;
- stop code `S-0`;
- stop gate `unexpected`;
- exception type `RuntimeError`; and
- the exact message `forced outer post-staging failure`.

`partial_diagnostics` is absent. The evidence label does not describe the staged full record as partial, and no duplicate scientific record appears in the manifest.

# 8. Transaction finalization

PASS. The production `_phase4_finalize()` is not monkeypatched in test 56. It preserves the outer-handler result as a distinct `_STOPPED` attempt under `attempts/`.

The preserved directory has exactly the seven `PHASE4_ARTIFACTS` plus `phase4_manifest.json`. `complete/` is absent, `.staging/` is empty, and the lock is released. The stopped result cannot be mistaken for or overwrite a successful publication.

# 9. Inner-handler coverage

PASS. Existing test 55 is retained unchanged. It still forces a one-shot post-staging finalization exception inside `_phase4_run_diagnostics()` and verifies the same authority, deduplication, derivative-progress, artifact-set, and transaction contract.

Tests 53 and 54 also remain in place for the pre-staging runtime-map and input-recheck authentication failures.

# 10. Shared merge-policy preservation

PASS. All four Phase-4 exception handlers continue to call the single `_merge_phase4_exception_evidence()` implementation:

- inner `StopRun`;
- inner unexpected exception;
- outer `StopRun`; and
- outer unexpected exception.

Test 56 wraps that production helper with a delegating spy and proves one invocation with the exact outer `RuntimeError`. It does not duplicate merge logic. No handler unconditionally attaches `partial_diagnostics`, and artifact authority continues to depend only on the shared `artifacts_staged` state.

# 11. Phase-4 review-v6 binding

PASS. Real Phase-4 execution is bound exactly to:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v6.md`

The verifier requires the canonical path, supplied and recomputed SHA-256, expected MNL and nested HEADs, gitlink equality, fully clean worktrees, the exact first heading, and exactly one ordinary Markdown `**FINAL VERDICT: APPROVE**` line in the first section.

Tests prove that Phase-4 reviews v1-v5 and Phase-3 review-v6 are rejected. The similarly numbered Phase-3 and Phase-4 review files remain unambiguous because their exact canonical paths differ. A synthetic exact Phase-4 review-v6 APPROVE file passes, while the real review-v5 `APPROVE AFTER FIXES` body copied to the v6 path fails.

# 12. Numerical-logic preservation

PASS. No numerical, derivative, provenance, input, transaction, or publication logic changed in the review-v5 remediation. The runner changes for this round are review-v6 binding strings and labels only.

The accepted Phase-4 contract remains:

- explicit ordered 37-free / 47-full mapping with ten immutable pins;
- package-built negative-log-likelihood derivative route;
- raw symmetry tolerance `1e-8 * max_abs_H`;
- symmetrized spectral calculations;
- rank tolerance `1e-10 * max_abs_eigenvalue`;
- strict positive-definiteness requirements;
- condition tiers `<= 1e7`, `> 1e7 and <= 1e10`, and `> 1e10`;
- exact ten-name regional parameter and design blocks;
- regional design rank 10;
- raw regional-subblock positive definiteness;
- solve-based Schur complement with rank 10 and strictly positive minimum eigenvalue; and
- regional loading share at or above 0.5 as warning-only.

The immutable code constants match YAML. Mapping, numerical-boundary, regional, Schur, and authorization tests remain passing.

# 13. Phase-3 regression safety

PASS. The accepted Phase-3 directory still contains exactly:

- `estimation_results.json`;
- `optimizer_diagnostics.json`;
- `phase3_console.log`;
- `phase3_manifest.json`; and
- `theta_estimated.csv`.

All four non-manifest hashes match the Phase-3 manifest. The deterministic bundle SHA-256 independently recomputes to:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

The manifest file SHA-256 remains:

`60eb1412cc14211a866d795e6bac3a7bde07c1f5879f4b000e066c2020fa8884`

The accepted complete directory has no Git diff. The shared transaction still defaults to `PHASE_3_COMPLETE`, and its immutability, locking, collision-retry, completeness, and finalization tests pass unchanged.

# 14. Test adequacy

PASS. Validation used the project virtual environment and no real derivative or optimizer:

- complete no-Hessian suite: `56 passed`;
- tests 55 and 56 together: ten consecutive passing runs, 20/20 test executions;
- mapping, numerical, authorization, and transaction subsets: pass;
- Python parse/in-memory compile and runner import: pass;
- YAML parse and immutable-constant checks: pass; and
- `git diff --check`: pass.

The new test closes the sole review-v5 coverage gap without weakening or removing any earlier test.

# 15. Phase-4 dry-run safety

PASS. The canonical Phase-4 dry-run returned `PHASE_4_DRY_RUN_COMPLETE` and recorded:

- `review_gate: AWAITING_PHASE4_REVIEW_V6_APPROVE`;
- `gradient_evaluated: false`;
- `hessian_evaluated: false`;
- `optimizer_called: false`;
- `execution_ready: false`; and
- derivative route loaded but not evaluated.

It created no `complete/`, left staging empty, and released the lock. Phase 5 was refused with exit code 2.

# 16. Prohibited-operation audit

No real gradient or Hessian was evaluated. Tests 55 and 56 used fake NumPy derivatives in temporary transaction roots. No optimizer, real Phase-4 execution, Phase 5 or later, inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebook route was run.

The nested package, accepted theta, accepted Phase-3 bundle, notebooks, and implementation files were not modified by this review. No commit was made.

# 17. Residual defects

None found within the final review scope.

The sole review-v5 blocker is closed by a checked-in, deterministic, repeatedly passing outer-handler regression test. No production-code, numerical, provenance, authentication, or transaction defect remains open from Phase-4 reviews v1-v5.

# 18. Required fixes

None.

# 19. Whether exact state may be committed

Yes. The exact reviewed runner, configuration, safety tests, implementation/remediation records, and this approving review may be committed as the Phase-4 execution checkpoint.

Before execution, all intended evidence files must be handled so both MNL and nested worktrees are fully clean, including untracked files. The commit must preserve the reviewed nested gitlink.

# 20. Whether real Phase 4 may execute

Yes, once, after the exact reviewed state and this review are committed and all execution gates pass.

The invocation must use the resulting MNL commit SHA, nested commit `27756a06ea189339aa82915ed2124628afed20eb`, the matching MNL gitlink, the committed review-v6 path and SHA-256, fully clean worktrees, the canonical configuration, the canonical output root, and `--execute-phase4`. Any gate failure must stop execution.

# 21. Immediate next action

Commit the exact reviewed Phase-4 state together with this review, intentionally handle all preserved attempt evidence, and verify both worktrees are fully clean. Record the new MNL commit SHA and committed review-v6 SHA-256, then execute the single real Phase-4 run through the documented canonical CLI. Do not run Phase 5 or later.
