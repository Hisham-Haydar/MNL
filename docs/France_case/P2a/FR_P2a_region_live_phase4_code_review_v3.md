# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

# 2. Scope

This narrow third review checked closure of the remaining review-v2 defects:
exceptional derivative-progress accounting, partial diagnostic preservation,
Phase-4 review-v3 authorization, and stale metadata. It also confirmed that
the previously approved numerical and transaction logic remains unchanged.

The two named derivative failures are corrected. One adjacent
post-evaluation authentication-failure branch still drops available
diagnostics, so the exact state is not yet approved for a real Phase-4 run.

No real gradient or Hessian, optimizer, Phase 4 execution, Phase 5+, inference,
post-estimation, welfare, synthetic recovery, EUROMOD, or notebook path was
run.

# 3. Files reviewed

The review read the Phase-4 implementation report, reviews v1 and v2,
remediation reports v1 and v2, the Phase-3 manager acceptance, the complete
current runner and YAML configuration, the complete safety-test file and
current Git diff, and all five accepted Phase-3 `complete/` artifacts.

The current tracked diff remains confined to the runner, its configuration,
and its safety tests. MNL HEAD remains
`c7d558a36489520a0f8487abf939d5300deaffb1`; nested HEAD and MNL gitlink both
remain `27756a06ea189339aa82915ed2124628afed20eb`, with the nested worktree
clean.

# 4. Derivative-progress accounting

PASS for the requested derivative paths. `_phase4_run()` owns one mutable
progress record visible to every controlled finalization handler.
`_phase4_diagnose()`:

- sets `gradient_evaluated` to true immediately after the fake or real
  gradient result is successfully obtained and converted, before the
  consistency gate; and
- sets `hessian_evaluated` to true immediately after the fake or real Hessian
  result is successfully obtained and converted, before symmetry, spectral,
  regional, or Schur processing.

No later code assigns either progress value back to false.
`_phase4_merge_progress()` overwrites the manifest skeleton’s initial false
values with the live progress state on normal, controlled-STOPPED, and
unexpected-exception paths.

# 5. Gradient-consistency failure

PASS. A fake gradient of ones against the zero published projection triggers
the exact S-8 `phase4-gradient` stop before the Hessian callable is reached.
The finalized STOPPED manifest records:

- `gradient_evaluated: true`;
- `hessian_evaluated: false`;
- exception type `StopRun`;
- the exact stop code and gate; and
- the 37-element gradient and consistency deviation in
  `partial_diagnostics`.

No `complete/` directory is created. The attempt is preserved separately,
staging is empty, and the lock is released.

# 6. Singular-Schur failure

PASS. A deterministic fake 37-by-37 Hessian with an exactly singular nuisance
block reaches the production solve route and raises the exact S-5
`schur-solve` stop. The finalized STOPPED manifest records:

- `gradient_evaluated: true`;
- `hessian_evaluated: true`;
- exception type `StopRun`;
- the exact stop code and gate; and
- pre-solve symmetry, full spectrum, loading, and design-rank diagnostics.

The absent regional result proves that the informational pseudoinverse did not
replace the failed gating solve. No `complete/` is created; the attempt,
staging, and lock states finalize correctly.

# 7. Partial diagnostic preservation

PARTIAL. The live `diag` dictionary is correctly retained by reference and
attached to the two named exceptional STOPPED manifests reviewed in sections
5–6.

However, available diagnostics are still lost if the post-evaluation
runtime-map or input-hash recheck raises. `_phase4_run_diagnostics()` first
sets `manifest["gates4"]`, then performs the recheck, and only afterward writes
the diagnostic artifacts. Its exception handler requests a partial merge, but
`_phase4_merge_progress()` suppresses `partial_diagnostics` whenever `gates4`
already exists.

A safe fake-only reproduction of a failed post-evaluation input recheck
therefore produced S-8 `input-recheck`, true/true derivative flags, and a gate
summary, but no `partial_diagnostics` and no numerical artifact beyond the
console and manifest. The complete gradient, spectrum, symmetry, design,
regional block, and Schur evidence was available in memory and was discarded.

# 8. Exception finalization

PASS for safety and transaction state; PARTIAL for evidence completeness. All
controlled failures remain STOPPED, cannot publish `complete/`, are preserved
under distinct attempt directories, empty staging, and release the lock.
Exact stop codes and gates are retained.

The residual in section 7 cannot create a false successful result, but it
violates review-v2’s requirement to preserve whatever partial diagnostic
evidence is available.

# 9. Phase-4 review-v3 binding

PASS. The sole canonical Phase-4 approval path is exactly:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v3.md`.

The verifier requires that exact path and SHA-256, expected MNL and nested
HEADs, gitlink equality, fully clean worktrees, and the exact review verdict
before entering the real diagnostic body.

Phase-4 review-v1, Phase-4 review-v2, and Phase-3 review-v6 paths are rejected.
The parser accepts only one exact APPROVE verdict under the exact first heading
`# 1. Phase-4 review verdict`; APPROVE AFTER FIXES, REJECT, wrong headings,
duplicate verdicts, and wrong hashes are refused. Consequently this review
cannot authorize execution.

# 10. Stale metadata closure

PASS. The former live claims that Phase 4 used review-v6 have been replaced by
the Phase-4-specific review-v3 contract. Remaining review-v6 mentions in
Phase-4-facing text state rejection or nonauthorization. The runner header,
refusal message, `run_phase4()` docstring, manifest labels, CLI review help,
and YAML comments agree.

Generic `--dry-run` help now explicitly describes Phase-4 bundle/contract
validation without gradient or Hessian evaluation.

# 11. Numerical-logic preservation

PASS. The remediation did not alter the objective, 37↔47 parameter mapping,
ten pins, accepted theta, regional parameter order, Hessian construction,
symmetry or rank formulas, strict positive-definiteness tests, condition
tiers, regional design rank, raw regional-subblock test, solve-based Schur
complement, or warning-only loading diagnostic.

The immutable Phase-4 constants and exact YAML equality remain:

- symmetry relative tolerance `1e-8`;
- rank relative tolerance `1e-10`;
- condition boundaries `1e7` and `1e10`;
- strict positive eigenvalue requirements;
- 37 free and ten regional parameters; and
- loading-warning share `0.5`.

# 12. Transaction preservation

PASS. Successful publication still requires the exact Phase-4 artifact set,
manifest-last hashing without self-hash, and atomic directory publication.
Existing `complete/` remains immutable. STOPPED and dry-run attempts remain
separate, and the shared transaction still defaults to
`PHASE_3_COMPLETE` while Phase 4 explicitly requests `PHASE_4_COMPLETE`.

The new progress state does not weaken successful-bundle completeness,
overwrite refusal, lock, staging, or publication rules.

# 13. Test adequacy

The complete no-real-Hessian suite passed: `52 passed in 26.21s`. Python AST
parsing, runner import, YAML parsing, and `git diff --check` passed.

Tests 50 and 51 use only fake derivative callables and drive the real
diagnostic/finalization body. They assert derivative flags, exact stops,
partial diagnostics, separate STOPPED publication, no `complete/`, empty
staging, and released locks. Review-v3 path/rejection and stale-string tests
also pass.

Coverage remains incomplete for Phase-4 runtime-map fingerprint and input-hash
recheck failures after successful fake diagnostics but before artifact
writing. The safe reproduction in section 7 demonstrates the untested loss.

# 14. Phase-3 regression safety

PASS. The accepted deterministic bundle SHA-256 remains:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`.

All four non-manifest hashes match the Phase-3 manifest, whose own hash remains
`60eb1412cc14211a866d795e6bac3a7bde07c1f5879f4b000e066c2020fa8884`.
The authoritative 47-vector remains bitwise equal to the optimizer diagnostic
theta with SHA-256
`c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`.

Phase-3 mapping, authorization, transaction, dry-run, and failure tests remain
passing. Package source, accepted output, theta, and notebook files are
unchanged.

# 15. Phase-4 dry-run safety

PASS. The canonical Phase-4 dry-run completed with:

- `gradient_evaluated: false`;
- `hessian_evaluated: false`;
- `optimizer_called: false`;
- `execution_ready: false`; and
- `AWAITING_PHASE4_REVIEW_V3_APPROVE`.

The derivative transformation was loaded but not evaluated. Phase-4
`complete/` is absent, staging is empty, and the lock is absent.

# 16. Prohibited-operation audit

PASS. No real gradient or Hessian, optimizer, Phase 4 execution, Phase 5+,
inference, score, standard error, post-estimation, welfare, synthetic
recovery, EUROMOD, or notebook path was run. Phase 5 remains explicitly
refused. No implementation or package file was edited by this review and
nothing was committed.

# 17. Residual defects

**Medium — post-evaluation authentication failure loses diagnostics.** A
runtime-map fingerprint or input-hash recheck stop occurs after complete
diagnostics but before numerical artifact writing. Because the manifest
already has `gates4`, exceptional partial merging suppresses the full live
diagnostic record. The attempt remains safely STOPPED with correct true/true
progress, but its available scientific evidence is not preserved.

# 18. Required fixes

1. Preserve the live full/partial diagnostic record on every exceptional path
   before `phase4_diagnostics.json` is successfully staged. Do not use the
   presence of the gate summary alone as evidence that the full record was
   persisted.
2. Add fake-derivative finalization tests for both runtime-map fingerprint
   mismatch and input-hash recheck failure. Assert S-8 with the exact gates,
   true/true progress, retained diagnostic evidence, no `complete/`, separate
   STOPPED attempts, empty staging, and released locks.
3. Keep successful-bundle requirements unchanged and clearly label this
   diagnostic evidence as belonging to a failed authentication attempt.
4. Since review v3 is not APPROVE, rebind the remediated execution gate and
   associated CLI, manifest labels, YAML comments, and tests to
   `FR_P2a_region_live_phase4_code_review_v4.md` or the later Phase-4 review
   that ultimately approves the exact state.

# 19. Whether exact state may be committed

Not as the final execution-ready Phase-4 checkpoint. It may be retained only
as a non-executable remediation record until the remaining evidence-preservation
branch is corrected and independently reviewed.

# 20. Whether real Phase 4 may execute

No. This conditional review is correctly rejected by the current approval
parser. After the residual fix, the exact remediated state must receive a
subsequent Phase-4 APPROVE review, be committed with that review, and pass all
clean-repository and revision gates before one real execution.

# 21. Immediate next action

Fix diagnostic preservation for post-evaluation runtime-map and input-recheck
stops, add the two fake-only finalization tests, bind authorization to
Phase-4 review v4, and request a narrow fourth review. Do not run
`--execute-phase4`.
