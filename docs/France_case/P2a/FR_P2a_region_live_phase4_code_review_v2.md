# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

# 2. Scope

This was the second independent static and no-Hessian review of the remediated
Phase-4 implementation. It tested closure of every defect and required fix in
review v1 sections 21–22 against MNL HEAD
`c7d558a36489520a0f8487abf939d5300deaffb1`, nested HEAD and MNL gitlink
`27756a06ea189339aa82915ed2124628afed20eb`.

The Phase-4-specific approval gate and all requested numerical failure tests
are now implemented correctly. The exact state is not yet approved for real
execution because two inaccurate Phase-3 review references remain and
exceptional derivative paths publish incorrect evaluation-state flags.

No real gradient or Hessian, optimizer, theta update, Phase 5+, clustered
inference, post-estimation, welfare, synthetic recovery, EUROMOD, or notebook
path was run.

# 3. Files reviewed

The review read the Phase-4 implementation report, review v1, remediation
report v1, Phase-3 manager acceptance and estimation report, manager decisions
v2, production rebuild plan v2, the complete current runner and YAML
configuration, the complete safety test file and Git diff, and all five files
in the accepted Phase-3 `complete/` bundle.

The current tracked diff is confined to:

- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; and
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`.

The nested dclaborsupply worktree is clean and its HEAD equals the MNL gitlink.

# 4. Phase-4 approval binding

PASS. A real Phase-4 run is bound to the exact canonical path:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v2.md`.

The dedicated verifier requires the supplied path to equal that value, checks
the supplied value is a 64-hex SHA-256, recomputes the file hash, and parses the
review before `run_phase4()` can enter the real diagnostic body.

The parser requires the exact first heading `# 1. Phase-4 review verdict`,
exactly one final-verdict line in that first section, and accepts only the
ordinary Markdown APPROVE form. APPROVE AFTER FIXES, REJECT, a wrong heading,
multiple verdict lines, malformed hashes, and hash mismatches are refused.

Because this review is conditional rather than APPROVE, the present v2 path
cannot authorize a real run.

# 5. Phase-3 review rejection

PASS. Supplying the canonical Phase-3 review-v6 path triggers the dedicated
`phase4-review-gate` stop stating that Phase-3 review-v6 cannot authorize
Phase 4. The Phase-4 review-v1 path is also noncanonical and refused; even if
its content were copied to the v2 path, its APPROVE AFTER FIXES verdict would
be rejected.

The public `--execute-phase4` route calls only the Phase-4 verifier. It cannot
reach gradient or Hessian evaluation using the Phase-3 approval arguments.

# 6. Commit and cleanliness gates

PASS. Before the real diagnostic body, the Phase-4 verifier requires:

- 40-hex expected MNL and nested commit SHAs equal to the live HEADs;
- MNL gitlink equality with the nested HEAD;
- full MNL cleanliness, including tracked, staged, and all untracked files;
- full nested-worktree cleanliness; and
- the canonical Phase-4 review path, hash, and exact verdict.

Temporary-repository tests independently cover MNL-HEAD mismatch, nested-HEAD
mismatch, wrong gitlink, untracked files in either worktree, wrong review path,
wrong review hash, and wrong verdict. The private real body also refuses an
unverified gate record before acquiring a transaction or evaluating
derivatives.

# 7. Phase-3 bundle binding

PASS. The valid accepted deterministic bundle SHA-256 remains:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`.

It is unchanged in code and YAML. Independent validation found the exact
five-file set, recomputed all four non-manifest hashes, matched the manifest
hash dictionary, and reproduced that bundle digest. The malformed
94-character value from the earlier request was not used.

# 8. Accepted-theta binding

PASS. The accepted authoritative JSON theta remains a 47-vector and is
bitwise identical to `optimizer_diagnostics.json::final_theta`. Its recomputed
SHA-256 remains:

`c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`.

The accepted bundle and the root v1/v2 theta files retain their prior hashes.
The 37-free/10-pin mapping, exact pin preservation, and specification order
are unchanged.

# 9. Derivative route

PASS for the mathematical route. Phase 4 still wraps the package-built JAX
negative-log-likelihood objective over the ordered 37-free vector with all ten
pins fixed in the expanded 47-vector. It constructs `jax.grad` and
`jax.hessian` in the contract, but the dry-run returns before either callable
is evaluated.

The latest canonical dry-run recorded:

- `gradient_evaluated: false`;
- `hessian_evaluated: false`;
- `optimizer_called: false`;
- derivative route loaded but not evaluated; and
- `execution_ready: false`.

# 10. Full-Hessian gates

PASS. Fake-derivative orchestration now verifies every full-Hessian stop:

- raw symmetry failure → S-4;
- non-positive-definite full Hessian → S-4;
- rank below 37 → S-4; and
- condition tier above `1e10` → S-4.

The ratified values are unchanged: raw symmetry relative tolerance `1e-8`,
rank relative tolerance `1e-10`, strict positive definiteness, condition
thresholds `1e7` and `1e10`, 37 free parameters, and ten regional parameters.
YAML values must still equal the immutable code constants exactly.

# 11. Regional-subblock PD failure

PASS. The ineffective disjunctive test identified in review v1 was replaced.
A deterministic regional diagonal entry of `-0.5` produces
`raw_subblock_pd_ok == false` and a non-positive minimum eigenvalue.

A separate 37-by-37 fake-Hessian orchestration test reaches the production
R-2 gate and asserts `STOPPED`, code S-5, gate G-9, the false R-2 flag, a
preserved `_STOPPED` attempt, and absence of `complete/`.

# 12. Singular Schur failure

PASS for the numerical stop. The test creates an exactly singular nuisance
block containing `[[1, 1], [1, 1]]`. The production `np.linalg.solve` route
raises and is translated to code S-5 with gate `schur-solve`.

The pseudoinverse calculation remains after the successful solve and is used
only to record `solve_vs_pinv_max_abs_diff`; it cannot substitute for the
gating solve or change a verdict.

# 13. Fake-derivative orchestration

PASS. The test context injects only array-returning fake gradient/Hessian
callables and drives the production `_phase4_diagnose()` orchestration. It
covers:

- G-5, G-6, G-7, and G-8 failures;
- R-1 design-rank failure;
- R-2 raw-subblock failure;
- singular nuisance solve;
- R-4 rank and minimum-eigenvalue failures;
- warning-only regional loading;
- and the clean complete route.

No package-built or real-data Hessian is constructed or evaluated by these
tests.

# 14. Exact numerical boundaries

PASS. Deterministic tests establish:

- symmetry exactly at `1e-8 * max_abs_H` passes and the next representable
  value above it fails;
- an eigenvalue exactly at `1e-10 * max_abs_eigenvalue` is excluded from rank,
  while the next representable value above it is counted;
- condition exactly `1e7` is clean, immediately above is warning, exactly
  `1e10` is warning, and immediately above is failure; and
- strictly positive minimum eigenvalues pass PD, while zero and negative
  values fail.

The condition classification and rank gate remain separate ratified checks;
their conjunction can fail at a condition boundary even when the condition
tier alone is a warning.

# 15. Regional loading diagnostic

PASS. A loading share at or above 0.5 remains warning-only. The fake
orchestration proves that a clean curvature/regional result with this warning
returns `PHASE_4_COMPLETE`; the loading flag is absent from both hard gate
conjunctions.

# 16. Output transaction

PASS for the previously reviewed publication rules. The isolated
`phase4_curvature_v1/` transaction retains its exclusive lock, unique staging
attempt, immutable `complete/`, exact successful artifact set, manifest-last
publication, no manifest self-hash, directory-level atomic rename, overwrite
refusal, and separate STOPPED/dry-run attempt preservation.

The shared transaction default remains `PHASE_3_COMPLETE`, while Phase 4
explicitly supplies `PHASE_4_COMPLETE`. Validation left Phase-4 `complete/`
absent, staging empty, and the lock absent.

One exceptional-path provenance defect remains and is recorded in sections
21–22; it does not permit false successful publication.

# 17. Phase metadata

PARTIAL. The module header, hard-refusal overview, primary CLI phase help,
Phase-4 review arguments, manifest review-gate labels, YAML header, and YAML
run block now correctly describe Phases 1–4 and refusal of Phases 5–8.

Two live Phase-4 strings remain incorrect:

- `_phase4_run()` says an unverified real call requires “review-v6 gates”; and
- `run_phase4()` says in its docstring that Phase 4 uses the same Phase-3
  review-v6 gates.

The generic `--dry-run` help also describes only Phases 1–3, although the
separate `--execute-phase4` help correctly documents Phase-4 dry-run behavior.
Thus review-v1’s stale-metadata fix is not fully closed.

# 18. Phase-3 regression safety

PASS. The accepted Phase-3 bundle is byte-identical, the nested package is
clean, and existing Phase-3 mapping, authorization, input authentication,
transaction, dry-run, and failure tests remain passing. No accepted output,
theta, notebook, package source, or certified baseline file has a Git change.

# 19. Test adequacy

The complete no-Hessian suite passed: `49 passed in 24.82s`. The remediation
tests 47–49 also passed in five consecutive targeted repetitions. Python AST
parsing, runner import, YAML parsing, and `git diff --check` passed.

The canonical Phase-4 dry-run completed without gradient, Hessian, or optimizer
evaluation; Phase 5 was refused with exit code 2. Accepted Phase-3 hashes were
identical before and after validation.

Coverage is now adequate for the review-v1 authorization, numerical gate, and
boundary defects. It does not cover accurate finalized manifest flags when
`_phase4_diagnose()` raises after a derivative has already been evaluated.

# 20. Prohibited-operation audit

PASS. No real Phase-4 gradient or Hessian, optimizer, theta mutation, Phase 5+,
clustered standard error, score, sandwich, post-estimation, welfare, synthetic
recovery, EUROMOD, or notebook route was run. Validation created only permitted
dry-run attempt evidence; no Phase-4 `complete/` bundle was created. No
implementation file was edited by this review and nothing was committed.

# 21. Residual defects

1. **Medium — inaccurate STOPPED provenance.** The Phase-4 manifest initializes
   `gradient_evaluated` and `hessian_evaluated` to false, but `_phase4_run()`
   updates them only after `_phase4_diagnose()` returns. A gradient-consistency
   stop occurs after the gradient was evaluated and therefore finalizes
   false/false instead of true/false. A singular Schur solve occurs after both
   gradient and Hessian evaluation and therefore finalizes false/false instead
   of true/true. The singular path also loses the in-memory partial numerical
   diagnostics. The result remains STOPPED, but its execution evidence is
   inaccurate.
2. **Low — stale Phase-3 approval wording.** The two runner strings identified
   in section 17 still claim review-v6 authorization for Phase 4, and generic
   dry-run help omits Phase 4.

# 22. Required fixes

1. Propagate derivative progress into the manifest at the point each fake or
   real derivative successfully evaluates, including exception paths. A
   gradient-consistency STOPPED attempt must record true/false; a singular
   post-Hessian Schur STOPPED attempt must record true/true. Preserve whatever
   partial diagnostic evidence is available without relaxing successful-bundle
   requirements.
2. Add no-real-Hessian tests that drive both exceptional cases through
   finalization and assert the final STOPPED manifest’s status, stop code/gate,
   derivative flags, absence of `complete/`, and released lock/empty staging.
3. Replace the two remaining Phase-4 “review-v6” strings with the
   Phase-4-specific approval description and make generic dry-run help include
   Phase 4.
4. Since this review v2 is not APPROVE, bind the remediated execution gate,
   CLI, manifest labels, and tests to
   `FR_P2a_region_live_phase4_code_review_v3.md` (or a later Phase-4 review
   that ultimately approves the exact state).

# 23. Whether exact state may be committed

Not as the final execution-ready Phase-4 checkpoint. It may be preserved only
as a non-executable work-in-progress record. Correct the provenance and
metadata defects and review the exact remediated state again before treating
the implementation as accepted.

# 24. Whether real Phase 4 may execute

No. The current verifier will correctly reject this review’s conditional
verdict. After the fixes, a subsequent Phase-4 review must approve the exact
clean committed state before one real execution is permitted.

# 25. Immediate next action

Correct exceptional-path derivative accounting and the remaining stale
strings, add finalized-STOPPED-manifest tests, rebind approval to Phase-4
review v3, and request a narrow third independent no-Hessian review. Do not
run `--execute-phase4`.
