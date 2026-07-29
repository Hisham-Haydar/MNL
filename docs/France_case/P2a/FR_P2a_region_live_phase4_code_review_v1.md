# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

The Phase-4 numerical construction, accepted-theta binding, regional-identification
logic, and output transaction are suitable in substance. Real execution is not
approved because the implementation still authenticates the already-approved
Phase-3 review-v6 document instead of an independently approved Phase-4 review.
The safety suite also lacks deterministic coverage of two failure paths.

# 2. Scope

This was an independent static and no-Hessian review of the uncommitted Phase-4
implementation on MNL commit
`c7d558a36489520a0f8487abf939d5300deaffb1`, with nested package HEAD and MNL
gitlink `27756a06ea189339aa82915ed2124628afed20eb`.

No real Hessian, optimizer, theta update, clustered inference, standard error,
post-estimation, welfare, synthetic-recovery, EUROMOD, or notebook path was run.
The permitted no-Hessian suite, a canonical Phase-4 dry-run, parse checks, Git
checks, and immutable-bundle hash checks were performed.

# 3. Files reviewed

The review covered in full:

- `FR_P2a_region_live_manager_decisions_v2.md`;
- `FR_P2a_region_live_production_rebuild_plan_v2.md`;
- `FR_P2a_region_live_phase3_manager_acceptance_v1.md`;
- `FR_P2a_region_live_phase3_estimation_report_v1.md`;
- `FR_P2a_region_live_phase4_implementation_report_v1.md`;
- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`;
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`;
- all five files in the accepted Phase-3 `complete/` bundle;
- the imported dclaborsupply specification, parser, loader, likelihood, JAX
  objective, gradient, and Hessian routes; and
- the complete current Git state and uncommitted diff.

The diff is confined to the runner, its YAML configuration, and its safety
tests (1,019 insertions and 8 deletions), plus the untracked Phase-4
implementation report and permitted validation-attempt outputs. The nested
package worktree is clean.

# 4. Phase-3 bundle binding

PASS. Phase 4 hard-requires the canonical
`phase3_estimation_v1/complete/` directory and its exact five-file set. It
recomputes the SHA-256 of each of the four non-manifest artifacts, requires the
hash dictionary to equal the Phase-3 manifest exactly, and recomputes the
sorted deterministic bundle digest. The result must equal both the manifest
and the immutable code/YAML value:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

Independent recomputation matched that value. The digest printed in the review
request is 94 hexadecimal characters and therefore is not a SHA-256; it
contains a duplicated substring. The 64-character value above is the
unambiguous value in the manager acceptance, Phase-3 manifest, implementation,
configuration, and independent recomputation.

The verifier also requires `PHASE_3_COMPLETE`, `optimizer_called: true`, and
the recorded Phase-3 acceptance gates. No fallback to a stale, provisional,
notebook, warm-start, or root-level theta exists.

# 5. Accepted-theta binding

PASS. `estimation_results.json` is the authoritative full-precision source for
the 47-vector. Its theta must be bitwise equal to
`optimizer_diagnostics.json::final_theta`, and its recomputed theta hash must
equal the diagnostic record. `theta_estimated.csv` must have specification-exact
name order and agree within the documented serialization tolerance.

Independent checks found 47 entries, exact JSON/diagnostics equality, correct
CSV order, and theta SHA-256
`c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`.
All ten accepted pins are checked byte-for-byte against the parameter map.

# 6. Derivative route

PASS. The derivative surface wraps the package-created JAX singles objective,
which returns negative log likelihood. Phase 4 does not reproduce likelihood
mathematics. JAX x64 is enabled by the package engine, and the accepted
objective is reproduced at `theta_hat` before derivative evaluation.

The canonical dry-run constructs `jax.grad` and `jax.hessian` transformations
but returns before either is evaluated. The dry-run completed with
`hessian_evaluated: false`, `optimizer_called: false`, and
`execution_ready: false`.

In a real run, the free gradient is compared with the persisted Phase-3
free-gradient projection using the fixed consistency tolerance. The existing
35-non-bound maximum is recorded but is not silently imposed as a new
Phase-3 gradient-acceptance gate.

# 7. Free-vector and pin handling

PASS. The accepted specification supplies the 47-name order. The existing
explicit parameter map supplies exactly 37 ordered free names and ten ordered
pins. Phase 4 projects the accepted 47-vector to those 37 coordinates, creates
a full base vector containing the exact pin values, and scatters only the
37-vector into the corresponding free indices.

Consequently the Hessian is exactly 37 by 37 over the ordered free vector, and
all ten pins are outside differentiation. Projection/expansion and pin
immutability remain covered by the preserved Phase-3 tests.

# 8. Hessian symmetry

PASS. Symmetry is measured on the raw Hessian before any symmetrization:

`max(abs(H - H.T)) <= 1e-8 * max(abs(H))`.

Only after that check is the spectral matrix formed as `(H + H.T) / 2`.
The raw Hessian itself is persisted in CSV and NPY form.

# 9. Rank and positive-definiteness gates

PASS in implementation. Eigenanalysis uses the symmetrized 37 by 37 matrix.
The numerical tolerance is `1e-10 * max(abs(eigenvalues))`; consistent with the
production plan, rank counts eigenvalues strictly above that tolerance and
must equal 37. Positive definiteness separately requires
`minimum_eigenvalue > 0`. Zero, negative, and near-zero eigenvalues therefore
cannot produce an accepted curvature result. The `eig <= 1e-8` count is
persisted as the specified diagnostic.

# 10. Condition-number gate

PASS. For a positive-definite spectrum, the reported condition number is
`max_eigenvalue / min_eigenvalue`. A zero or negative minimum yields infinity
and failure. Classification is exactly:

- at most `1e7`: clean;
- greater than `1e7` and at most `1e10`: warning without halt;
- greater than `1e10`: failure.

The pooled comparison value `1.295e6` is retained in diagnostics.

# 11. Regional-parameter binding

PASS. Regional names are derived from the accepted specification/free-name
order, then required to equal both the immutable code tuple and the YAML tuple.
Static comparison with the canonical plan confirmed this exact order:

`beta_E_gsur`, `beta_E_drgn2`, `beta_E_drgn3`, `beta_E_drgn4`,
`beta_E_drgn5`, `beta_E_drgn6`, `beta_E_drgn7`, `beta_E_drgn8`,
`beta_E_drgur`, `beta_E_drgmd`.

The resulting free-vector positions are 15 through 24.

# 12. Regional design rank

PASS. The design is read from the authenticated frozen stem using `idhh` and
the exact ten design columns. Within-household constancy is checked before a
sorted one-row-per-`idhh` reduction. The resulting shape must be 1,555 by 10,
and its SVD rank under the ratified relative tolerance must equal 10.

Read-only inspection found 1,555 households, no missing regional-design cells,
and exact within-household constancy. Singular values and high-correlation
pairs are retained.

# 13. Regional Hessian subblock

PASS in implementation. The 10 by 10 block is selected from the symmetrized
free Hessian by the specification-derived free positions. Its eigenvalues are
computed after a defensive subblock symmetrization, and R-2 requires its
minimum eigenvalue to be strictly positive.

# 14. Conditional Schur complement

PASS in implementation. The nuisance block is the exact 27-coordinate
complement of the ten regional coordinates. The gating matrix is computed as:

`H_RR - H_RN @ solve(H_NN, H_NR)`.

No explicit inverse is used. A singular nuisance solve raises an S-5 stop.
The symmetrized Schur complement must have rank 10 under the ratified tolerance
and a strictly positive minimum eigenvalue. The `pinv(rcond=1e-10)` construction
is informational only; its maximum absolute difference from the solve-based
matrix is recorded and does not replace the gating calculation.

# 15. Regional loading diagnostic

PASS. A regional squared-loading share is calculated and persisted for every
one of the 37 eigenvectors. A share at or above 0.5 on any of the three
smallest eigenvectors creates a warning only. It is excluded from both the
curvature conjunction and the R-1/R-2/R-4 regional-identification conjunction,
so it cannot turn an otherwise passing result into failure.

# 16. Output transaction

PASS. The canonical root is exactly
`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/`, separate from
Phase 3. Writes are confined to an attempt staging directory under the
exclusive transaction lock.

Successful publication requires the exact seven non-manifest artifacts, writes
the manifest last, excludes the manifest from its own hash dictionary, checks
the exact final eight-file set, and performs a directory-level `os.replace`
into `complete/`. An existing or newly appeared `complete/` refuses
publication. STOPPED and dry-run attempts are moved separately under
`attempts/`; warning-only successful results retain their warnings in the
complete diagnostics and manifest. Validation left `complete/` absent,
staging empty, and the lock absent.

# 17. Phase-3 regression safety

PASS. The shared transaction change adds a `success_status` argument whose
default remains `PHASE_3_COMPLETE`; Phase 4 alone supplies
`PHASE_4_COMPLETE`. The preserved Phase-3 mapping, bundle, transaction,
authorization, dry-run, and failure tests pass.

All five accepted Phase-3 bundle files remained byte-identical after the test
suite and Phase-4 dry-run. The nested package HEAD still equals the MNL
gitlink, and package source, notebooks, theta files, and accepted Phase-3
outputs have no Git changes.

# 18. Execution-approval binding

FAIL — HIGH, execution-blocking. `run_phase4()` does require
`--execute-phase4` for a real run and then checks expected MNL/nested commits,
gitlink equality, fully clean worktrees, review path, review hash, and an exact
APPROVE verdict. However, it calls the unchanged Phase-3 verifier. That
verifier is hard-wired to:

`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md`

and to the heading `# 1. Sixth-review verdict`. That review already says
APPROVE and predates all Phase-4 code. After the current implementation is
committed into a clean worktree, those Phase-3 gates can authorize entry to
`_phase4_diagnose()` and the real Hessian. Current worktree dirtiness is only a
temporary stop and is not a valid Phase-4 approval control.

Therefore Phase-3 review-v6 alone currently can authorize new Phase-4 code,
contrary to the binding manager requirement. A Phase-4-specific approved review
is mandatory before derivative evaluation.

# 19. Test adequacy

The no-Hessian suite passed: `44 passed in 20.26s`. Python AST parsing, YAML
parsing, and `git diff --check` also passed. The canonical Phase-4 dry-run
returned `PHASE_4_DRY_RUN_COMPLETE` without gradient/Hessian evaluation or an
optimizer call. Phase 5 returned the explicit Phases 5–8 refusal.

Coverage is strong for bundle tampering, regional-name conflicts, symmetry,
rank, positive definiteness, condition tiers, design rank, analytic Schur
construction, Schur rank/minimum-eigenvalue failures, loading warnings,
transaction publication, overwrite refusal, and dry-run behavior.

Three gaps remain:

- no test proves that a Phase-3 review is rejected by the Phase-4 execution
  boundary or that the exact approved Phase-4 review contract is required;
- the claimed raw regional-subblock PD failure test is ineffective: its
  deterministic matrix returns `raw_subblock_pd_ok: true` with minimum
  eigenvalue approximately `8.88e-16`, and the disjunctive assertion still
  passes; and
- no deterministic singular-`H_NN` test asserts the `schur-solve` S-5 stop.

A fake-derivative `_phase4_diagnose()` integration test would additionally
verify that each full-Hessian and regional failure is wired to S-4/S-5 without
evaluating the real Hessian. Exact threshold-boundary cases should be added for
the symmetry, rank, and condition tiers.

# 20. Prohibited-operation audit

PASS. No optimizer call, theta mutation, real Hessian, clustered score,
standard error, post-estimation, welfare, synthetic recovery, EUROMOD,
notebook, or Phase-5+ computational route was found or run. The Phase-4 code
uses only the accepted estimate and local curvature/identification diagnostics.
Phases 5–8 are explicitly refused.

# 21. Residual defects

1. **High:** the real Phase-4 path authenticates Phase-3 review-v6 rather than
   a Phase-4-specific approved review.
2. **Medium:** deterministic tests do not actually exercise a failing raw
   regional-subblock PD gate or a singular nuisance-block Schur solve, and do
   not integrate the fake derivative route through the S-4/S-5 orchestration.
3. **Low:** the runner module description, CLI help, YAML header, and run
   metadata still state that only Phases 1–3 are implemented or that Phases
   4–8 are all unsupported, even though Phase 4 now exists and only Phases 5–8
   are refused.
4. **External record discrepancy:** the bundle string in the review request is
   malformed at 94 hex characters; the repository evidence consistently
   establishes the valid 64-character digest recorded in section 4.

# 22. Required fixes

1. Add a Phase-4-specific execution verifier. Because this review is not
   APPROVE, bind the remediated implementation to the subsequent
   `FR_P2a_region_live_phase4_code_review_v2.md` (or later Phase-4 review that
   ultimately returns APPROVE), its exact canonical path and SHA-256, its exact
   first heading, and exactly one `**FINAL VERDICT: APPROVE**` line. Retain the
   expected MNL commit, expected nested commit, gitlink, package identity, and
   fully clean worktree gates, all before gradient or Hessian evaluation.
2. Add tests proving that Phase-3 review-v6, a wrong Phase-4 path/hash/verdict,
   dirty worktrees, and commit/gitlink mismatches cannot reach Phase-4
   diagnostics, while the exact Phase-4 approval contract can.
3. Replace the ineffective raw-subblock test with a deterministic
   non-positive-definite block and assert R-2 failure. Add a singular
   nuisance-block test that asserts `StopRun("S-5", "schur-solve", ...)`.
   Add fake-derivative orchestration coverage for S-4/S-5 and exact gate
   boundaries without invoking the real Hessian.
4. Correct the stale Phase-4 support comments, CLI help, YAML header, and run
   metadata.

# 23. Whether implementation may be committed

Not as the final execution-ready Phase-4 implementation. Apply the required
authorization and test fixes, rerun the no-Hessian suite, and subject the exact
remediated diff to a Phase-4 review v2. A historical work-in-progress
checkpoint would not constitute approval to execute.

# 24. Whether real Phase 4 may execute

No. Real Phase 4 must remain blocked. The accepted Phase-3 bundle and
Phase-3 review-v6 do not authorize evaluation of the new Phase-4 Hessian.

# 25. Immediate next action

Implement the Phase-4-specific review gate and the missing deterministic
failure tests, correct the stale metadata, then request an independent
Phase-4 review v2 of the exact uncommitted state. Do not run
`--execute-phase4` before that review returns APPROVE and the reviewed state is
committed cleanly.
