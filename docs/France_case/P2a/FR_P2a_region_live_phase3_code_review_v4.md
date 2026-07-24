# 1. Fourth-review verdict

**FINAL VERDICT: REJECT**

The remediation closes the original YAML alias divergence, canonical-config
checks on the intended entrypoint, immutable target controls, exact review-blob
authorization, substring ancestry bug, target-mismatch publication, and most
test-coverage defects.

It does not close every required fix in review-v3 section 21:

1. `_phase3_orchestrate` remains a directly callable private function accepting
   an arbitrary transaction root, contract, estimator, minimizer, identity
   verifier, and authorization record. It has no canonical-root or verified-
   authorization invariant. The prior production bypass was moved down one
   layer rather than removed.
2. `_run_phase3_test_attempt` requires non-`None` components but does not require
   them to be fake. It accepts the real contract, estimator, identity verifier,
   and an explicitly supplied real minimizer.
3. the authorization verifier does not require the authorization JSON to reside
   outside either worktree. A valid authorization in a Git-ignored in-worktree
   path passes the implemented cleanliness check.
4. package identity checks only four modules. A safety-critical transitive
   module used by the loader can be preloaded from outside the reviewed nested
   repository while `package_identity_ok` remains true.
5. the G-16 remediation test does not exercise the exact epsilon boundary, and
   one aggregate-gate assertion is tautological for failing cases.

The first two findings and the package-source substitution are high-severity
execution-integrity defects. Real Phase 3 must remain blocked.

The 30 review questions are answered directly below.

| Q | Answer | Finding |
|---:|:---:|---|
| 1 | Qualified yes | The production contract opens its data inputs from `_phase3_runtime_paths()`, although authentication and recheck reconstruct fresh maps rather than receiving the same map object. |
| 2 | Yes | All four retained consumed-path aliases are required to resolve to their corresponding runtime-map paths. |
| 3 | No in the intended CLI; possible through private state manipulation | Reviewed YAML cannot select a different consumed file, but separate runtime-map construction leaves a stateful direct-call seam. |
| 4 | No implementation-wide | `main`, `run_phase3`, and authorization enforce the canonical config; `_phase3_orchestrate` does not. |
| 5 | Yes through the private bypass | The intended entrypoint refuses an identical copied config, but direct orchestration does not enforce config identity. |
| 6 | No | The old `_txn_root` bypass is now exposed as the unguarded `txn_root` argument of `_phase3_orchestrate`. |
| 7 | Yes, improperly | `_run_phase3_test_attempt` guards production roots, but `_phase3_orchestrate` can directly address them. |
| 8 | No | The named production `run_phase3` entrypoint exposes only `args` and `cfg`; its dependencies are hard-wired. |
| 9 | No | Component arguments must be non-`None`, but the real components are not rejected. |
| 10 | Yes | Both controls are code constants, YAML equality is checked, and operative code uses the constants. |
| 11 | No through the genuine post-gate route | A genuine target mismatch cannot return `PHASE_3_COMPLETE`; injected orchestration can bypass the genuine gate entirely. |
| 12 | Yes | The canonical approved review path is fixed exactly to review v4. |
| 13 | Yes | The review must resolve as a tracked blob at the approved MNL commit. |
| 14 | Yes | SHA-256 is calculated over the committed blob and compared with the authorization record. |
| 15 | Yes | Exactly one first-section line equal to `**FINAL VERDICT: APPROVE**` is required. |
| 16 | Yes | `APPROVE AFTER FIXES` is rejected and tested. |
| 17 | No under the literal wording | Tracked, staged, and ordinary untracked changes are refused, but ignored untracked files are allowed. |
| 18 | No | The authorization path has no resolved-ancestry exclusion for either worktree. |
| 19 | Yes for the modules examined | Checked module files use resolved `Path.is_relative_to` ancestry. |
| 20 | Yes | The sibling-substring attack fails for a checked module. |
| 21 | No | Directly loaded package dependencies such as `likelihood._numpy_primitives` and package initializers are omitted. |
| 22 | Partial | Bounds, inside-epsilon, and outside-epsilon cases are present, but exact `lo-epsilon`/`hi+epsilon` are absent and one aggregate assertion is ineffective. |
| 23 | Yes for the genuine estimator route | Both high and low target mismatches finish under `attempts/` with no `complete/`. |
| 24 | Yes | The full suite passes without importing or invoking the real optimizer. |
| 25 | Yes | `git diff --check` and committed-diff checks pass. |
| 26 | Yes | Phase 1-2 code and evidence are preserved; the permitted scratch regression passes. |
| 27 | Yes | The canonical dry-run remains unauthorized, non-optimizing, and unable to publish `complete/`. |
| 28 | Yes | Phases 4-8 remain refused. |
| 29 | No | The state is already committed, but it is not safe to designate as the authorization-ready reviewed implementation. |
| 30 | No | A valid authorization file cannot cure the orchestration and package-identity bypasses. |

# 2. Scope

This was an independent read-only review of the exact current repository state:

- MNL HEAD and `origin/main`:
  `7c1546c52b423f881c103d8662226f272ba5701d`;
- nested `dclaborsupply-monorepo` HEAD:
  `27756a06ea189339aa82915ed2124628afed20eb`; and
- MNL gitlink:
  `27756a06ea189339aa82915ed2124628afed20eb`.

At review start, both repositories were clean, with no staged, unstaged, or
ordinary untracked files. The complete current Git diff and cached diff were
empty. The Phase-3 implementation and remediation-v3 evidence had already been
committed and pushed before this review, notwithstanding the remediation
report's contemporaneous statement that nothing had yet been committed.

No execution-authorization file exists. No real Phase 3, real optimizer,
EUROMOD, inference, post-estimation, welfare, or notebook was run. The sole
repository write made by this review is this requested report.

# 3. Files reviewed

The following were read in full:

- `docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase12_manager_acceptance_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_implementation_report_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v3.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v3.md`
- `docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v2.md`
- `scripts/p2a/run_p2a_regionlive_rebuild.py`
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`
- `dclaborsupply/__init__.py`
- `dclaborsupply/models.py`
- `dclaborsupply/spec/parser.py` and its package initializer
- `dclaborsupply/data/loader.py` and its package initializer
- `dclaborsupply/likelihood/engine_jax.py`
- `dclaborsupply/likelihood/_numpy_primitives.py`
- `dclaborsupply/likelihood/index.py` and its package initializer

The current Git diff was inspected in full and was empty. The committed
remediation diff, current imported-module set, Git blobs, current dry-run
attempts, canonical transaction layout, and package path-containment behavior
were also inspected.

# 4. Consumed-path closure

The ordinary production-path defect is substantially closed.

`_phase3_contract` constructs `rt = _phase3_runtime_paths()` and uses it to open:

- the Phase 1-2 rebuild manifest;
- certified specification;
- Phase 1-2 dry-run report;
- frozen-stem metadata;
- certified warm-start theta;
- stored region-live start theta; and
- frozen-stem parquet.

No corresponding Phase-3 data read remains through
`MNL_ROOT / cfg[...]` or `out.path(...)`.

The retained aliases:

- `certified_spec.yaml`;
- `warm_start.theta_csv`;
- `phase3.start_theta.csv`; and
- `stored_region_live_theta.v1_csv`

must each resolve to the corresponding immutable runtime-map path before any
data read. Every authentication-table path is also compared with its
code-constructed runtime path and hash. Test 35 mutates each alias and confirms
an `alias-identity` stop.

One lower-level gap remains. The local `rt` map is not passed to
`_authenticate_inputs`; that function constructs another map. Post-call recheck
constructs another map again. The normal code-owned function is deterministic,
so the current CLI paths agree, but the remediation report's claim that one map
object governs consumption, authentication, and recheck is not literal. A
stateful monkeypatch or direct-call replacement can make those maps differ.

# 5. Canonical config enforcement

Resolved canonical-config equality is enforced in:

- `main`, before dispatch into `run_phase3`;
- `run_phase3`; and
- `_verify_external_authorization`.

An identical copied config, a path resolving elsewhere through traversal, and a
symlink resolving elsewhere are intended to be refused. The copy and traversal
checks ran successfully; the symlink case is the suite's one platform skip
because this Windows account cannot create the test symlink.

This is not enforced inside `_phase3_orchestrate`. A direct caller can provide
an arbitrary `args.config` and `cfg` while also choosing the canonical
transaction root. Therefore the exact path is required by the intended
production entrypoint but not by every callable Phase-3 orchestration route.

# 6. Production/test-seam separation

`run_phase3(args, cfg)` is correctly narrowed. It exposes no transaction-root,
contract, estimator, minimizer, or identity-verifier argument, requires the
canonical config and output roots, verifies authorization for a non-dry run,
and supplies the genuine dependencies itself.

The separation fails one layer below. `_phase3_orchestrate` directly exposes:

- `txn_root`;
- `contract_fn`;
- `estimate_fn`;
- `minimize_fn`;
- `identity_fn`; and
- `auth_record`.

It neither refuses a canonical production root nor requires a verified
authorization for a non-dry attempt. `execution_ready` is merely recorded in
the manifest; it is not an execution gate. Estimation proceeds whenever
`args.dry_run` is false.

Consequently, a direct call can provide:

- `txn_root=CANONICAL_PHASE3_ROOT`;
- the genuine contract and estimator;
- `minimize_fn=None`, which selects real SciPy;
- the genuine identity verifier; and
- `auth_record={}`.

That route reaches the canonical transaction and real estimator without
external authorization. Arbitrary injected functions can likewise fabricate
the exact three pre-finalization artifacts and publish a canonical
`complete/`. This call was not executed during review; the control flow is
direct and unconditional in the source.

The guarded `_run_phase3_test_attempt` wrapper correctly refuses its own
`test_root` when it equals or descends from the canonical Phase-3 root,
region-live root, or `MNL/outputs`. It also requires every component argument
to be non-`None`. It does not establish that those components are fake:
the real contract, estimator, identity verifier, and an explicit real
minimizer satisfy the check and can perform unauthorized real estimation at a
non-production root.

Test 37 checks only `run_phase3`'s public signature, guarded wrapper roots,
missing components, and the marker. It does not test direct
`_phase3_orchestrate` refusal or rejection of real component identities.

# 7. Immutable target controls

This review-v3 defect is closed in the genuine estimator route.

The runner defines:

- `PHASE3_PREOPT_OBJECTIVE_TOL = 1e-4`; and
- `PHASE3_TARGET_MISMATCH_STATUS =
  "REVIEW_REQUIRED_TARGET_MISMATCH"`.

YAML equality is independently validated. The pre-optimization check uses the
code constant, and `_phase3_post_gates` returns the code-owned mismatch status
rather than the YAML value. Changing the YAML status to
`PHASE_3_COMPLETE` cannot change the genuine gate result.

`Phase3Transaction.finish` sends every status other than the exact success
string to `attempts/`. A genuine objective mismatch therefore cannot publish
`complete/`.

# 8. Exact review authorization

The exact review-authorization design is correctly implemented:

- `CANONICAL_APPROVED_REVIEW_REL` is fixed to this review-v4 path;
- `approved_review_path` must equal the exact POSIX relative path;
- `git rev-parse <approved-commit>:<path>` must resolve a tracked blob;
- `git cat-file blob` supplies the committed bytes;
- SHA-256 of those committed bytes must equal
  `approved_review_sha256`;
- the working-tree file must byte-match the blob; and
- verdict parsing occurs on the committed blob.

The verdict parser requires exactly one line beginning with the final-verdict
marker, requires it in the first section, and accepts only the exact requested
approval line. `APPROVE AFTER FIXES`, `REJECT`, prose mentions, missing verdict,
and multiple verdicts are rejected. Tests 39 and 40 cover the principal cases.

Because this report's verdict is `REJECT`, it cannot satisfy that execution
authorization check and no authorization file may be created for this state.

# 9. Repository cleanliness

`_git_fully_clean` is an improvement over `-uno`. It calls:

`git status --porcelain --untracked-files=all`

for both MNL and the nested repository. Tests confirm refusal of tracked
modifications, staged changes, ordinary untracked files, and nested untracked
files.

The implementation does not provide the full guarantee claimed by its comments
and config header:

- Git status excludes ignored files unless explicitly asked to show them; and
- test 41 deliberately confirms that an ignored file passes.

The authorization verifier only requires the JSON path to be absolute and an
existing file. It does not resolve the path and reject ancestry beneath MNL or
the nested repository.

A permitted test in a temporary Git repository placed a valid authorization
JSON at an ignored path inside the repository. Git status was empty and
`_verify_external_authorization` returned `verified: true`. Thus the statement
that the authorization must reside outside both worktrees is documentation,
not enforcement.

The same ignored-file gap matters for package source: an ignored Python module
inside the expected source root is not made visible by `_git_fully_clean`.

# 10. Package source containment

For the four modules it examines, the new implementation correctly resolves
`__file__` and uses `Path.is_relative_to(PACKAGE_SOURCE_ROOT)`. A module with no
`__file__` fails. The sibling path
`dclaborsupply-monorepo_evil/...` is correctly rejected. Current ordinary
imports all resolve under the nested repository, and nested HEAD equals the
parent gitlink.

The checked inventory is incomplete. The verifier checks only:

- top-level `dclaborsupply`;
- `dclaborsupply.spec.parser`;
- `dclaborsupply.data.loader`; and
- `dclaborsupply.likelihood.engine_jax`.

Importing those modules also loads safety-relevant package modules including:

- `dclaborsupply.models`;
- `dclaborsupply.data`;
- `dclaborsupply.spec`;
- `dclaborsupply.likelihood`;
- `dclaborsupply.likelihood.index`; and
- `dclaborsupply.likelihood._numpy_primitives`.

The loader directly imports `EPS`, `PrecomputedDataSingles`, and
`PrecomputedDataCouples` from `_numpy_primitives` and constructs the data
objects passed to the JAX objective. It is therefore safety-critical.

A safe fresh-process probe preloaded a synthetic
`dclaborsupply.likelihood._numpy_primitives` whose `__file__` was
`C:\outside-reviewed-tree\_numpy_primitives.py`. The genuine loader used the
synthetic `PrecomputedDataSingles`, while `_verify_package_identity()` returned
`package_identity_ok: true` because the substituted dependency was not in its
inventory.

This is a concrete package-source substitution, not merely incomplete
reporting. Review-v3 section 21 explicitly required all safety-critical imported
modules.

# 11. G-16 boundary coverage

The G-16 implementation applies the code-validated epsilon `1e-9` to all 37
free parameters:

- values below `lo - epsilon` fail; and
- values above `hi + epsilon` fail.

Test 43 exercises exact parameter bounds, points `0.5e-9` beyond each bound
that remain within tolerance, and points `2e-9` beyond each bound that fail the
per-row check. Separate tests assert upper-side G-16 failure through both the
pure gate and fake-estimator route.

Coverage remains incomplete relative to review v3:

- exact `lo - 1e-9` and `hi + 1e-9` tolerance-boundary cases are absent; and
- `assert gates["g16_inbounds_ok"] is expect_ok or not expect_ok` is
  automatically true whenever `expect_ok` is false, so test 43 does not verify
  the aggregate gate for its two failing cases.

The code appears correct, but the required exact-boundary regression proof is
not fully closed.

# 12. Target-publication safety

Test 44 drives the genuine `_phase3_estimate` implementation through an
asserting fake minimizer with objective shifts of `+1e-3` and `-1e-3`.
Both cases:

- return exit code 4;
- persist the immutable
  `REVIEW_REQUIRED_TARGET_MISMATCH` status;
- publish only under `attempts/`; and
- leave `complete/` absent.

This closes the target-high and target-low publication requirement for the
genuine estimator.

The unguarded `_phase3_orchestrate` remains able to accept an injected estimator
that returns `PHASE_3_COMPLETE` without running the genuine gate. That is the
separate production/test-seam defect described in section 6.

# 13. Test adequacy

Permitted validation performed:

- Python AST parse of runner and tests: passed;
- YAML safe parse: passed;
- full safety suite in the project environment, with bytecode and pytest cache
  disabled: **43 passed, 1 skipped in 10.69 seconds**;
- skipped test: Windows symlink creation unavailable;
- source inspection and import trace found no real SciPy call in the suite;
- `git diff --check`: passed;
- `git show --check HEAD`: passed;
- current tracked and cached diffs: empty;
- current MNL and nested repository status: clean before this report;
- imported package-path inspection: current ordinary paths are under the nested
  source root;
- outside-tree transitive-module substitution probe: package verification
  incorrectly passed, exposing the defect;
- existing canonical dry-run bundle inspection: passed the dry-run invariants;
  and
- Phase 4 refusal: exit code 2 before Phase-3 work.

The suite materially improves confidence in mapping, pins, objective/gradient
signs, optimizer contract, G-16 behavior, target isolation, input mutation,
artifact completeness, atomic publication, locking, review blobs, and ordinary
Git dirtiness.

Missing tests correspond directly to residual defects:

- direct `_phase3_orchestrate` canonical-root and no-authorization refusal;
- rejection of real components by the private test route;
- ignored in-worktree authorization refusal;
- omitted/transitive package-module substitution;
- ignored package-source refusal;
- use of one runtime-map object across authentication, consumption, and recheck;
  and
- exact epsilon-boundary plus non-tautological aggregate G-16 assertions.

# 14. Phase 1–2 regression safety

The remediation diff does not alter the Phase 1-2 implementation bodies. Phase
3 remains a separate dispatch branch and consumes accepted Phase 1-2 evidence
read-only.

A permitted scratch-root `--phase 2 --dry-run` completed with:

- exit code 0;
- `DRY_RUN_PHASES_1_2_COMPLETE`; and
- regenerated stem SHA-256
  `8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

The scratch result was removed after validation. No accepted production
Phase 1-2 file was changed.

# 15. Phase-3 dry-run safety

The latest existing canonical dry-run attempt is:

`20260724T154825Z_456964_368500_dryrun_PHASE_3_DRY_RUN_COMPLETE`.

Its persisted evidence records:

- `status: PHASE_3_DRY_RUN_COMPLETE`;
- `authorization_status: AWAITING_POST_REVIEW_AUTHORIZATION`;
- `execution_ready: false`;
- `optimizer_called: false`;
- null execution authorization;
- successful package and input contract;
- start negLL exactly `19053.46553160094`; and
- no manifest self-hash.

The canonical Phase-3 root has no `complete/` and no retained lock. No new
canonical dry-run was launched by this review because existing committed
evidence was sufficient and the review role is read-only.

# 16. Prohibited-operation audit

The genuine Phase-3 estimator continues to use the package-built JAX singles
objectives and `jax.value_and_grad`; it does not duplicate likelihood
mathematics. SciPy is imported only inside `_phase3_estimate` when no minimizer
is supplied.

The safety suite supplies a fake minimizer for every `_phase3_estimate` call.
No real optimizer module or call was used. No Phase-3 route implements EUROMOD,
draw regeneration, Hessian, inference, scores, sandwich covariance,
post-estimation, welfare, synthetic recovery, or notebook execution.

Phases 4-8 are refused before dispatch. No real Phase 3, execution-
authorization file, EUROMOD, inference, post-estimation, welfare, notebook, or
commit operation was performed by this review.

# 17. Residual defects

1. **High — canonical production orchestration remains injectable.**
   `_phase3_orchestrate` can directly select the canonical root and genuine
   estimator without verified authorization.
2. **High — package identity omits a data-container dependency.** A substituted
   outside-tree `_numpy_primitives` module is consumed by the loader while
   package identity passes.
3. **Medium — the private test helper does not require fake components.** It
   accepts the genuine estimator and a real minimizer at a non-production root.
4. **Medium — external authorization location is not enforced.** An ignored
   in-worktree authorization file passes.
5. **Medium — repository cleanliness does not cover ignored source.** Ignored
   package files are invisible to the cleanliness check.
6. **Low — runtime-map identity is reconstructed rather than threaded.**
   Authentication, consumption, and post-call recheck do not share one map
   object.
7. **Low — G-16 boundary proof is incomplete.** Exact epsilon boundaries are
   absent and one aggregate assertion is tautological.
8. **Low — stale review metadata remains.** The runner's authorization comment
   and CLI help still say authorization follows “third-review APPROVE,” although
   review v3 was `REJECT` and the implementation requires review v4.

# 18. Required fixes

1. Enforce production and test invariants inside `_phase3_orchestrate`, not only
   in its wrappers. A canonical-root non-dry call must require:
   - the canonical config;
   - a verified authorization record;
   - the exact genuine contract, estimator, and identity verifier; and
   - the production minimizer route.
   Any non-production call must be structurally unable to select any MNL output
   path.
2. Prevent `_run_phase3_test_attempt` from accepting the genuine contract,
   estimator, identity verifier, or a real SciPy minimizer. Add tests for each
   rejection and for direct `_phase3_orchestrate` access.
3. Resolve the authorization JSON path and reject it whenever it equals or
   descends from either the MNL or nested repository, independently of Git
   ignore rules. Add an ignored-in-worktree regression test.
4. Build and verify the complete loaded `dclaborsupply` module inventory for the
   Phase-3 route. At minimum include package initializers, `models`,
   `likelihood.index`, and `likelihood._numpy_primitives`. Require every module
   file to be a tracked blob at the approved nested commit and byte-match that
   blob, so ignored/untracked substitutions also fail.
5. Construct the runtime path map once, pass that same map into
   `_authenticate_inputs`, persist it in the contract context, and pass it to
   every post-call recheck.
6. Add exact `lo-epsilon` and `hi+epsilon` tests and replace the tautological
   G-16 aggregate assertion with direct equality.
7. Correct the stale “third-review APPROVE” comment and CLI help.
8. Run the safe suite and cleanliness checks again, then request a fifth
   independent read-only review. Do not create an execution authorization
   unless that review returns exact approval.

# 19. Whether implementation may be committed

**No, not as an authorization-ready reviewed implementation.**

The implementation is already committed and present at `origin/main` as
`7c1546c52b423f881c103d8662226f272ba5701d`; there is therefore no pending
implementation diff to commit. That commit must not be treated as approved for
Phase-3 authorization. The residual fixes require a new remediation commit and
another independent review.

No commit was made by this review.

# 20. Whether Phase 3 may execute after authorization

**No.**

A nominally valid authorization file cannot cure the unguarded canonical
orchestrator or the outside-tree package dependency accepted by the current
identity verifier. This report is a rejection, so the canonical review-blob
verdict check also prevents a valid execution authorization for this state.

Do not run the first real Phase-3 estimation.

# 21. Immediate next action

Implement only the fixes in section 18, add the missing non-optimizing
regressions, and request a fifth independent review. Preserve the current
Phase 1-2 evidence and Phase-3 attempt history. Do not create an execution-
authorization file and do not execute real Phase 3 unless the later review
returns an exact approval.
