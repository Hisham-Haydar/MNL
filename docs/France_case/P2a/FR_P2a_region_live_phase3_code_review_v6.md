# 1. Sixth-review verdict

**FINAL VERDICT: APPROVE**

# 2. Governing execution scope

This is the narrow final update requested after the attempt-ID fix. The governing
standard remains
`docs/France_case/P2a/FR_P2a_region_live_phase3_execution_scope_v1.md`.
The preserved pre-fix review,
`FR_P2a_region_live_phase3_code_review_v6_pre_fix.md`, returned
`APPROVE AFTER FIXES` solely because ordinary same-label/same-status attempts could
collide under the former clock-modulo identifier.

This update reviewed only closure of the four requirements in pre-fix review section
17:

1. collision-resistant attempt allocation;
2. deterministic collision and finalization tests;
3. reliable repeated no-optimizer validation; and
4. correction of the three stale comments.

The econometric, numerical, provenance, Git-identity, package-identity, and public-CLI
findings already accepted in the pre-fix review were not reopened except to verify that
the fix did not change them.

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_phase3_execution_scope_v1.md`;
- `FR_P2a_region_live_phase3_simplification_report_v1.md`;
- `FR_P2a_region_live_phase3_code_review_v6_pre_fix.md`;
- `FR_P2a_region_live_phase3_attempt_id_fix_report_v1.md`;
- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; and
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`.

The complete current tracked diff, untracked-file inventory, both repository states,
and canonical Phase-3 transaction directories were inspected.

Reviewed pre-report state:

- MNL HEAD:
  `8ba73c161af9cec87802e2d87dd42e9d777fe0e7`;
- nested dclaborsupply HEAD:
  `27756a06ea189339aa82915ed2124628afed20eb`;
- MNL gitlink:
  `27756a06ea189339aa82915ed2124628afed20eb`;
- nested worktree: clean;
- tracked implementation changes: runner and safety tests only; and
- config diff: empty.

Before replacing this review, the tracked fix diff contained 160 insertions and 13
deletions across the runner and tests. The runner changes were confined to UUID
allocation, lock-held attempt reservation, post-acquisition manifest stamping, and two
requested comments. The tests added the deterministic collision/exhaustion cases and
corrected the requested preamble.

# 4. Public execution boundary

The pre-fix conclusion is unchanged. The documented public CLI remains the sole
production boundary. A real Phase-3 run still requires `--execute-phase3`; without it,
Phase 3 forces the contract-only dry-run. Canonical config, canonical output root, exact
Phase-3 subdirectory, expected commits, and review-v6 approval inputs remain enforced.

The attempt-ID fix introduced no injectable production root, estimator, minimizer,
authorization bypass, or alternate execution route.

# 5. Git revision and cleanliness gates

The Git gates are unchanged. A real run requires exact expected MNL and nested commit
SHAs, a nested HEAD equal to the MNL gitlink, and fully clean MNL and nested worktrees
including untracked files.

The nested repository is clean and its HEAD equals the gitlink. The MNL tree is
intentionally dirty at review time because it contains the uncommitted fix, reports, this
updated review, and preserved validation attempts. The real execution gate must continue
to refuse this pre-commit state.

# 6. Review approval gate

The canonical approval path remains fixed exactly to
`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md`.
The implementation still requires the file's SHA-256 supplied on the CLI and accepts only
one ordinary Markdown approval line under the exact first heading. The attempt-ID fix did
not alter that parser or gate.

This updated file supplies the required approval form. Its final SHA-256 must be computed
from the exact committed bytes and passed to the one authorized execution.

# 7. Package source identity

Package-source controls are unchanged. All required dclaborsupply modules must resolve
beneath the reviewed nested source root, be tracked at the approved nested commit, and
match their Git-canonical blobs. The nested repository remained untouched and clean
throughout this review.

The requested stale package-inventory comment now accurately describes Git-canonical
content equality and the Windows `autocrlf` distinction. This was a comment-only change;
the verifier is unchanged.

# 8. Input provenance

Input authentication and the post-optimization recheck are unchanged. The complete diff
contains no change to the runtime-path map, authentication labels or paths, input hashes,
pre-call verification, post-call rehash, runtime-map fingerprint, or Phase 1–2 evidence
anchors.

# 9. Parameter and pin handling

The explicit ordered 37-free to 47-full mapping, inverse projection, exact ten-name pin
tuple, immutable pin values, and two expected bound names are unchanged. No parameter
name, ordering, index construction, expansion, projection, or pin assertion appears in
the fix diff.

# 10. Numerical gates

The fix leaves every numerical control unchanged:

- target negLL `19053.46553160094`;
- objective tolerance `1e-4`;
- pre-optimization objective tolerance `1e-4`;
- G-16 epsilon `1e-9`;
- 35-non-bound-free gradient threshold `1e-2`;
- bound-hit epsilon `1e-5`;
- method `L-BFGS-B`; and
- options `maxiter=5000`, `maxcor=30`, `ftol=1e-15`, `gtol=1e-10`.

The objective route, objective and Jacobian signs, two-sided target-mismatch status,
parameter counts, hashes, and transaction status strings are also unchanged. The config
file has no diff.

# 11. Output transaction safety

Review questions 1–9 pass.

The old `time.time_ns() % 1_000_000` allocation is completely absent from implementation
and tests. A transaction now receives its identifier only in `acquire()`, in the form:

```text
{UTC-second}_{pid}_{full-32-hex-uuid4}_{label}
```

`acquire()` first obtains the exclusive `O_CREAT | O_EXCL` lock. While that lock is held,
the allocator:

1. generates a full `uuid.uuid4().hex` token;
2. rejects an ID already represented in `.staging/`;
3. rejects an ID already represented under `attempts/` with any status suffix; and
4. atomically reserves `.staging/<attempt-id>` with
   `mkdir(exist_ok=False)`.

Both a detected destination and a `FileExistsError` from the reservation cause a fresh
UUID retry. The bounded 100-candidate exhaustion path raises
`S-0/attempt-allocation`, releases the lock, leaves no staging evidence, creates no
attempt publication, preserves prior evidence, and leaves the root reusable.

Same-label/same-status attempts therefore receive distinct destinations and cannot
overwrite one another through the normal transaction path. Scratch verification of
`PHASE_3_COMPLETE`, `PHASE_3_DRY_RUN_COMPLETE`,
`REVIEW_REQUIRED_TARGET_MISMATCH`, and `STOPPED` confirmed that each controlled
finalization moves its staging directory and releases the lock.

After all validation:

- `.phase3.lock` is absent;
- `.staging/` has zero entries; and
- `complete/` is absent.

# 12. Test adequacy

Review questions 10–12 pass.

The new deterministic tests freeze the timestamp and monkeypatch the UUID sequence:

- test 31 forces `a, a, a, b`, exercises the real `acquire()` retry route, verifies
  two same-label/same-status attempts with distinct full UUID tokens, and proves both
  payloads survive separately with empty staging and no lock;
- test 32 holds the UUID at one colliding value through all 100 retries, verifies the
  registered exhaustion stop, no misleading publication, intact prior evidence, empty
  staging, released lock, and subsequent root reuse.

Independent repeated validation using the project `.venv` produced:

- transaction tests 14, 15, 16, 31, and 32:
  **100/100 fresh-process iterations passed**, totaling 500 selected test executions;
- the formerly flaky transaction test 14:
  **100/100 passed** within those iterations;
- complete no-optimizer safety suite:
  **5/5 consecutive fresh-process runs passed, 32 tests each**; and
- one additional complete reviewer run:
  **32 passed**.

Estimator-route tests replace `scipy.optimize.minimize` before calling the estimator;
the subprocess dry-run omits `--execute-phase3`. No real optimizer or real Phase-3
estimation was invoked.

An initial invocation through the machine-wide Python 3.14 interpreter lacked JAX and
SciPy and therefore could not run the dependency-bearing tests. Its canonical dry-run
stopped before optimization and was correctly preserved as a separate `STOPPED` attempt,
with `optimizer_called=false`, empty staging, no lock, and no `complete/`. All pass counts
above use the project `.venv`.

AST parsing, YAML parsing, `git diff --check`, and the nested-repository cleanliness check
also pass.

# 13. Phase 1–2 regression safety

Review question 14 passes.

An external scratch-root `--phase 2 --dry-run` under the project environment returned
exit code 0 and `DRY_RUN_PHASES_1_2_COMPLETE`. Both phases passed; the JAX and NumPy
objectives reproduced `19053.4655316009`; and the regenerated stem was byte-identical to
the accepted artifact:

`8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

The tracked fix diff does not touch Phase 1–2 logic or accepted evidence.

# 14. Phase-3 dry-run safety

Review questions 15–16 pass.

The canonical CLI without `--execute-phase3`, run under the project environment, returned
exit code 0 and published a uniquely identified
`PHASE_3_DRY_RUN_COMPLETE` attempt. Its manifest records:

- `optimizer_called: false`;
- `execution_ready: false`; and
- `review_gate: AWAITING_REVIEW_V6_APPROVE`.

The full 32-hex UUID token is present in the attempt ID. After the dry-run,
`complete/` remains absent, `.staging/` is empty, and the lock is absent.

# 15. Prohibited-operation audit

Review question 17 passes.

Phase 4 was invoked only as a refusal check and returned exit code 2 without creating an
attempt. The runner continues to refuse every phase above 3.

During this update:

- real Phase 3 and the real optimizer were not invoked;
- EUROMOD, inference, post-estimation, welfare, synthetic recovery, and notebooks were
  not run;
- no implementation, config, package, parameter, baseline, or accepted Phase 1–2 file
  was edited by the reviewer;
- no execution-authorization file was created; and
- no commit was made.

Permitted validation created only preserved Phase-3 dry-run/STOPPED attempt evidence and
an external scratch regression that was removed after comparison.

# 16. Residual defects

No in-scope implementation or test defect remains.

The MNL tree is not execution-ready yet because the exact reviewed fix, reports, updated
review, and preserved validation attempts remain uncommitted/untracked. This is the
expected pre-commit state and is correctly rejected by the real-run cleanliness gate.

# 17. Required fixes

None.

All four required actions from the pre-fix review are closed:

1. full-UUID, lock-held, atomically reserved attempt IDs with bounded retry;
2. deterministic collision and exhaustion tests that prove preservation and cleanup;
3. stable repeated transaction and complete no-optimizer suite runs; and
4. correction of the three identified stale comments.

No further implementation change is required before committing the exact reviewed state.

# 18. Whether exact reviewed state may be committed

Yes.

Review question 19 passes. The implementation is safe to commit together with the exact
tests, governing/review reports, and intended preserved validation evidence. The commit
scope should be inspected carefully, and both repositories must be fully clean after the
commit before any execution attempt.

# 19. Whether Phase 3 may execute once

Yes, but only after the exact reviewed state is committed and every existing execution
gate passes.

Review question 20 passes conditionally on the documented prerequisites: activate the
project environment; commit the exact reviewed state and preserved evidence; verify the
MNL and nested trees are fully clean; verify nested HEAD equals the MNL gitlink; compute
the SHA-256 of this exact committed review; and supply the post-commit MNL SHA, nested SHA,
canonical review path, and review SHA to the documented public CLI with
`--execute-phase3`.

The current uncommitted tree must not execute real Phase 3.

# 20. Immediate next action

Inspect the final diff and repository inventory, stage only the exact reviewed
implementation, tests, reports, review, and intended preserved validation evidence, then
commit them as one reproducible checkpoint. Verify both worktrees are fully clean and the
gitlink matches nested HEAD. Record the committed MNL SHA, nested SHA, and this review's
SHA-256, then execute Phase 3 once through the documented CLI. Do not run Phases 4–8.
