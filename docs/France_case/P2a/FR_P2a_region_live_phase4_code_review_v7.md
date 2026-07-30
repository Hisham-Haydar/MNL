# 1. Phase-4 review verdict

**FINAL VERDICT: APPROVE**

# 2. Scope

This independent review assessed only the corrected Phase-4 R-1 regional-design
source and preservation of the Phase-4 implementation approved in review v6.
The reviewed base revision was MNL HEAD
`09531651313367954b5a016200ff563d26fde383`; the nested dclaborsupply HEAD and
MNL gitlink were both
`27756a06ea189339aa82915ed2124628afed20eb`.

No real gradient or Hessian was evaluated. No optimizer, real Phase-4 run,
Phase 5 or later, inference, post-estimation, welfare, synthetic recovery,
EUROMOD, or notebook route was run. No implementation file was edited and no
commit was made by this review.

# 3. Files reviewed

The review read the R-1 design audit and correction report, Phase-4 code review
v6, Phase-4 remediation report v5, Phase-3 manager acceptance, the complete
current runner/config/test diff, the current runner and configuration, the
safety test file, and the production dclaborsupply singles loader. It also
inspected the accepted Phase-3 complete bundle, the preserved first real
Phase-4 STOPPED attempt, and all four files in
`phase4_R1_design_audit_v1/`.

The accepted specification and the JAX singles-likelihood construction were
checked where needed to verify the ten design attributes and their coefficient
mapping.

# 4. Accepted false-failure finding

The finding `CURRENT_R1_FALSE_FAILURE` is confirmed conclusively.

The old R-1 input was a 1,555-by-10 household matrix read from stored stem
columns. Its `reg2` through `reg8` columns are all identically zero, and its
rank is 3 at tolerance `2.8972812327725502e-9`. Its singular spectrum exactly
matches the R-1 record in the preserved STOPPED attempt.

The stem has no `reg_nuts1_2` through `reg_nuts1_8` columns. The production
loader therefore derives `reg2` through `reg8` from `drgn1`. The resulting
loader matrix is 1,555-by-10, has rank 10 at tolerance
`3.0399849582996693e-9`, and is exactly array-equal to the independently
constructed `drgn1` matrix. All eight regions have support.

The stopped run's other evidence is mutually consistent with a false R-1
failure: full-Hessian rank 37 and positive definiteness, clean condition
number, positive-definite raw regional subblock, and rank-10 positive-definite
Schur complement.

# 5. Production loader provenance

PASS. `_phase3_contract` constructs `dm` and `df_` once from the authenticated
frozen male and female frames. Those exact two objects are passed to
`build_jax_singles_ll` to build the two components of the accepted JAX
objective. The contract now returns the same object identities as
`loader_data = (dm, df_)`.

`_phase4_contract` unpacks that tuple and passes it directly to
`_phase4_regional_design`. It performs no second parquet read, frame split,
specification load, loader call, parameter-map construction, or alternative
ordering for R-1. Returning the already-existing objects is non-mutating; the
Phase-3 estimation and transaction bodies are unchanged and all Phase-3
regression tests pass.

# 6. Corrected R-1 design source

PASS. `_phase4_regional_design(dm, dfem)` reads exactly these attributes from
the production loader objects, in this fixed order:

`gsur, reg2, reg3, reg4, reg5, reg6, reg7, reg8, drgur, drgmd`.

The helper contains no stem read and no copy of the loader's regional fallback
logic. The old `_phase4_contract` read of stored stem `reg2` through `reg8` has
been removed. The immutable runner/config contract now requires and persists
`production_likelihood_loader_arrays` as the design source.

# 7. Household reduction

PASS. The helper uses each loader object's own `group_starts`, `group_ends`,
and `group_ids`. It checks every one of the ten arrays for finite values and
for exact constancy within every loader choice block before selecting the row
at each group start.

The male and female blocks are concatenated and stable-sorted by loader
household ID. The production-data validation found 714 male plus 841 female
groups, 101 alternatives in each group, no cross-sex ID overlap, 1,555 unique
strictly ordered IDs, and exact agreement with the globally sorted stem
household IDs. `_phase4_contract` requires shape `[1555, 10]`, 1,555 loader
groups, 1,555 unique household IDs, within-block constancy, and finiteness
before R-1 can run.

# 8. Parameter-to-column mapping

PASS. The positional mapping is exact and is persisted in contract
diagnostics:

- `gsur` to `beta_E_gsur`;
- `reg2` through `reg8` to `beta_E_drgn2` through `beta_E_drgn8`;
- `drgur` to `beta_E_drgur`; and
- `drgmd` to `beta_E_drgmd`.

The parameter names remain derived from the accepted specification and must
agree exactly, in order, with both the immutable code tuple and the YAML list.

# 9. Exact likelihood-design binding

PASS. The corrected helper output is exactly array-equal to an independent
reduction of the production loader arrays at their group starts. It is also
exactly array-equal, column by column, to the loader-equivalent construction
using `1{drgn1 == k}` for regions 2 through 8.

The JAX singles builder resolves the same named attributes from the same loader
objects when it constructs the market-opportunity terms. Phase 4 cannot
substitute a provisional, notebook, stale-frame, or stored-placeholder design
on this route.

The behavioral regression fails if the old matrix is substituted: that matrix
still has rank 3. Its source guard also requires
`_phase4_regional_design` plus `loader_data` in `_phase4_contract` and forbids
the frozen-stem path there. Thus a return to the dead stored columns is covered
both structurally and by exact-array/rank behavior.

# 10. R-1 rank gate

PASS. The implementation changed the design source, not the acceptance rule.
`_phase4_design_rank` still computes the tolerance as
`1e-10 * largest_singular_value`, and the Phase-4 gate still requires rank
exactly 10.

The corrected production-loader matrix passes with rank 10. The old
stored-column matrix continues to fail with rank 3. No tolerance, required
rank, singular-value calculation, or stop behavior was weakened.

# 11. False-failure regression test

PASS. Test 57 uses the canonical accepted frozen stem, certified
specification, stem metadata, and production `load_singles` function. It
proves that:

- stored `reg2` through `reg8` are all zero;
- the old matrix has rank 3 and fails R-1;
- the helper equals an independent reduction of all ten loader arrays;
- the helper IDs equal the independently reduced and sorted loader IDs;
- the corrected matrix has rank 10 and passes R-1;
- every loader regional dummy equals its `drgn1` derivation;
- substituting the old matrix fails; and
- `_phase4_contract` uses `loader_data` and does not read the frozen stem for
  R-1.

The test invokes no gradient, Hessian, or optimizer path. It passed ten
consecutive standalone pytest processes.

# 12. Dry-run behavior

PASS. The canonical Phase-4 dry-run exited 0 with
`PHASE_4_DRY_RUN_COMPLETE`. Its manifest reported:

- source `production_likelihood_loader_arrays`;
- shape `[1555, 10]`;
- all ten canonical column names and the complete parameter mapping;
- finite and within-block-constant loader arrays;
- 1,555 groups and 1,555 unique households;
- `gradient_evaluated: false`;
- `hessian_evaluated: false`;
- `optimizer_called: false`; and
- derivative route loaded but not evaluated.

The dry-run made no rank or real-Hessian claim. It left `complete/` absent,
staging empty, and the lock released.

# 13. Review-v7 authorization binding

PASS. Real Phase-4 execution is bound exactly to:

`docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v7.md`

The gate requires the canonical path, the supplied and recomputed review
SHA-256, expected MNL and nested HEADs, gitlink equality, fully clean
worktrees, the exact first heading, and one exact
`**FINAL VERDICT: APPROVE**` line in that first section before derivative
evaluation.

Tests reject the Phase-4 review-v1 through review-v6 paths and the separate
Phase-3 review-v6 path. A synthetic exact review-v7 APPROVE document passes
the structural gate. The canonical dry-run correctly reports
`AWAITING_PHASE4_REVIEW_V7_APPROVE`.

# 14. Numerical-logic preservation

PASS. Comparison with committed review-v6 code found no change to:

- the accepted theta, 37-free/10-pin map, or ten regional parameters;
- the package JAX objective, gradient, or Hessian construction;
- raw-Hessian symmetry checking or symmetrization;
- full-Hessian rank, positive-definiteness, and condition gates;
- raw regional-subblock extraction or positive-definiteness gate;
- solve-based Schur complement, rank, and minimum-eigenvalue gates; or
- the warning-only regional loading-share interpretation.

The numerical helper bodies are unchanged from HEAD. The only diagnostic-path
addition is the persisted R-1 design-source label. YAML gate values are
unchanged: symmetry `1e-8`, rank `1e-10`, condition tiers `1e7` and `1e10`,
37 free parameters, 10 regional parameters, and loading warning threshold
`0.5`.

# 15. Transaction preservation

PASS. Phase-4 artifact requirements, exclusive lock, UUID attempt allocation,
staging, separate STOPPED attempts, immutable `complete/`, manifest-last
publication, manifest self-hash exclusion, and directory-level atomic
publication are unchanged.

The complete transaction, artifact writer/finalizer, exceptional-evidence
merge policy, and exceptional finalization bodies are byte-text identical to
the committed v6 implementation. The transaction regression battery passed.
After validation, Phase-4 `complete/` remained absent, `.staging/` was empty,
and the lock was absent.

# 16. Phase-3 regression safety

PASS. The only Phase-3-contract change is returning the already-created
loader objects as an additional context key. Phase-3 estimation, manifest,
finalization, execution, and shared transaction behavior are unchanged.

The accepted five-file Phase-3 bundle remains exact. All four non-manifest
artifact hashes match its manifest, and its deterministic bundle SHA-256
recomputes to:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

The accepted theta is therefore unchanged. The nested repository is clean at
the accepted gitlink revision.

# 17. Preserved STOPPED-attempt safety

PASS. Every file in the first real attempt
`20260729T121430Z_322592_6a8a24821914433f9f4303f2a6459025_curvature_STOPPED`
was hashed before and after validation and remained byte-identical. Its seven
non-manifest artifact hashes also match its manifest, and its deterministic
bundle digest is
`52f34b54bfa678d588f0f40d47f18ff056a7abee2de06694a6daa6993edc8808`.

The preserved record still contains the successful 37-by-37 Hessian
evaluation and all regional curvature diagnostics, the rank-3 old R-1 result,
and the exact `S-5`/`G-9` stop. It was neither overwritten nor republished as
complete.

The frozen engine-ready stem is unchanged at SHA-256
`8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

# 18. Test adequacy

PASS. Static validation produced:

- complete no-Hessian suite: 57 passed in 28.31 seconds;
- repeated complete no-Hessian suite: 57 passed in 27.63 seconds;
- test 57: 10/10 consecutive standalone passes;
- canonical Phase-4 dry-run: exit 0 and derivative-free;
- Phase 5 refusal: exit 2;
- in-memory Python compilation and YAML parsing: pass;
- `git diff --check`: pass; and
- nested worktree cleanliness and HEAD/gitlink equality: pass.

The full suite retained all prior Phase-3 mapping, authorization, transaction,
bundle, Phase-4 numerical-boundary, failure-path, and publication tests. No
test was weakened to obtain the corrected R-1 result.

# 19. Prohibited-operation audit

No real gradient or Hessian was evaluated. No optimizer was invoked, theta was
not altered, and Phase 4 was not run for real. Phase 5 was tested only for its
required refusal; no Phase 5-or-later computation occurred.

No inference, post-estimation, welfare, synthetic recovery, EUROMOD, or
notebook route was run. Package source, accepted Phase-3 outputs, the frozen
stem, and the preserved first STOPPED attempt were not modified. No commit was
made.

# 20. Residual defects

None found within the review scope.

The audit/correction documents, R-1 audit artifacts, preserved STOPPED
attempt, and dry-run evidence are presently untracked. This is an operational
checkpoint condition, not a code defect: the intended evidence must be
committed or otherwise intentionally handled before the real-run cleanliness
gate can pass.

# 21. Required fixes

None.

# 22. Whether exact corrected state may be committed

Yes. The exact reviewed runner, configuration, tests, audit and correction
records, R-1 evidence, preserved first STOPPED attempt, and this approving
review may be committed as the corrected Phase-4 checkpoint.

No implementation change is required. The commit must preserve nested
gitlink `27756a06ea189339aa82915ed2124628afed20eb` and must not alter the
accepted theta, Phase-3 bundle, frozen stem, or preserved STOPPED files.

# 23. Whether Phase 4 may be rerun once

Yes, once and only once, after the exact reviewed state and this review are
committed and every execution gate passes.

The rerun must use the resulting expected MNL HEAD, nested HEAD
`27756a06ea189339aa82915ed2124628afed20eb`, matching gitlink, fully clean
worktrees, canonical config/output paths, this committed review-v7 path and
SHA-256, and `--execute-phase4`. Any mismatch must stop the attempt. Phase 5
or later remains unauthorized.

# 24. Immediate next action

Commit the exact corrected checkpoint and this review, intentionally include
or otherwise resolve every untracked evidence item, and verify both worktrees
are fully clean. Record the new MNL commit SHA and this committed review's
SHA-256. Then perform the single canonical Phase-4 rerun through the
documented CLI. Preserve the first STOPPED attempt and do not run Phase 5.
