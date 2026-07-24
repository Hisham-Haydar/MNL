# 1. Third-review verdict

**FINAL VERDICT: REJECT**

The remediation closes most of the numerical, parameter-mapping, failure-evidence,
locking, and transactional-publication defects identified in review v2. The
non-optimizing safety suite passes 34/34 tests.

It does not close all review-v2 defects. In particular:

1. the authenticated path map is still not the map used to open the certified
   specification, warm-start theta, and stored region-live theta;
2. the canonical reviewed config path is not required;
3. a direct `run_phase3` call can set `_txn_root` to the canonical Phase-3 root,
   be classified as non-production, bypass external authorization, and retain
   the default real contract, estimator, and minimizer;
4. `target_mismatch_status` and `pre_opt_objective_tol` remain controlled only
   by YAML, with the former able to convert a failed target gate into
   `PHASE_3_COMPLETE`;
5. imported-module containment is checked by substring rather than path
   ancestry; and
6. the authorization review-path/verdict and clean-tree checks are not exact.

These are executable control failures, not documentation-only observations.
The first real Phase-3 estimation remains prohibited.

The 32 review questions are answered directly below.

| Q | Answer | Finding |
|---:|:---:|---|
| 1 | Yes | The code owns an exact ten-label authentication set and rejects missing or extra labels. |
| 2 | No | Three actual reads still use separate YAML paths rather than the authenticated runtime paths. |
| 3 | Yes | An authentication-table label cannot be omitted, but a different actually consumed spec/warm/start file can be selected without appearing in that table. |
| 4 | Yes | File A can be authenticated while file B is selected and consumed. |
| 5 | Yes | `SELF` authentication has been removed. |
| 6 | No | The production CLI requires authorization, but the `_txn_root` API seam can bypass it, including at the canonical root. |
| 7 | Partial | The gated CLI verifies all listed hashes/commits, but arbitrary config/review paths and a loose review-verdict test prevent an exact trusted binding. |
| 8 | No | Only tracked dirtiness is checked; `git status --porcelain -uno` ignores untracked files. |
| 9 | Yes | Nested HEAD is checked against both the parent gitlink and, on an authorized CLI run, the approved nested commit. |
| 10 | No | Current imports are correct, but enforcement is a substring test and does not prove true containment. |
| 11 | No | Most constants are independently pinned, but `pre_opt_objective_tol` and `target_mismatch_status` are not. |
| 12 | Yes | The fake minimizer exercises `_phase3_estimate` itself. |
| 13 | Yes | The test loads the certified specification's actual 47-name order. |
| 14 | Yes | The minimizer receives 37 coordinates and bounds in production free-name order. |
| 15 | Yes | The fake route verifies positive negLL and positive gradient signs. |
| 16 | Yes | All ten pins remain excluded and bitwise unchanged through the fake route. |
| 17 | Yes | Both materially high and materially low target outcomes are tested. |
| 18 | Yes | Optimizer failure/exception, G-16, gradient, and unexpected-bound failures are tested. |
| 19 | Partial | Mutation of a mapped authenticated file is caught before writes, but the three path aliases mean a differently consumed file is outside that recheck. |
| 20 | Yes | `optimizer_called` is marked before invocation and remains true when the minimizer raises. |
| 21 | Yes | Success requires the exact five-file final bundle. |
| 22 | Yes | Missing and unexpected artifacts are refused. |
| 23 | Yes | A valid success bundle is published by one directory-level `os.replace`. |
| 24 | Yes | The manifest is excluded from its own artifact-hash dictionary. |
| 25 | Yes | Legacy migration now occurs after exclusive-lock acquisition. |
| 26 | Yes | Lock contention is tested without migration or optimizer access. |
| 27 | Partial | Operative phase fields are corrected, but the runner and config headers still say “Phases 1-2.” |
| 28 | Yes | The Phase-3 dry-run remains non-optimizing, needs no execution authorization, and records that it is not execution-ready. |
| 29 | Yes | The Phase 1-2 route and accepted evidence are preserved by the reviewed diff. |
| 30 | Yes | Phases 4-8 are absent from the route and `--phase 4` is refused. |
| 31 | No | The implementation is not safe to commit as an authorization-ready implementation. |
| 32 | No | The exact current commit plus an authorization file would not cure the structural bypasses. |

# 2. Scope

This was an independent, read-only review of the current uncommitted Phase-3
implementation at:

- MNL HEAD `d195cf63339973e00eabd246447de530265aa267`;
- nested `dclaborsupply-monorepo` HEAD
  `27756a06ea189339aa82915ed2124628afed20eb`; and
- parent MNL gitlink
  `27756a06ea189339aa82915ed2124628afed20eb`.

The tracked implementation diff contains 648 insertions and 45 deletions across
the runner, config, and safety test. The untracked remediation-v2 report and
current Phase-3 dry-run attempt were also inspected.

No real Phase 3, real optimizer, EUROMOD, inference, post-estimation, welfare,
notebook, or commit operation was run. The only file created by this review is
this requested report.

# 3. Files reviewed

The following files were read in full:

- `docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase12_manager_acceptance_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_implementation_report_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v2.md`
- `scripts/p2a/run_p2a_regionlive_rebuild.py`
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`
- `dclaborsupply/__init__.py`
- `dclaborsupply/spec/parser.py`
- `dclaborsupply/data/loader.py`
- `dclaborsupply/likelihood/engine_jax.py`

The complete current tracked Git diff was read. The current imported module
locations, nested HEAD, parent gitlink, tracked working-tree state, dry-run
attempt bundle, and canonical Phase-3 transaction layout were inspected
read-only.

# 4. Input authentication closure

The literal label-set defect is closed. `_phase3_runtime_paths` defines ten
code-owned labels at runner lines 1194-1215, and `_authenticate_inputs` requires
exact set equality at lines 1224-1230. The current YAML has exactly those ten
labels. Missing and extra labels are refused. The current ten configured paths
also resolve to the ten code-owned paths, and all current hashes pass.

The consumed-path defect is not closed. After authentication, the contract
opens:

- the specification from `cfg["certified_spec"]["yaml"]` at line 1631;
- the warm-start theta from `cfg["warm_start"]["theta_csv"]` at line 1661; and
- the stored start theta from `phase3.start_theta.csv` at line 1670.

Those three pointers are independent of the paths authenticated under
`certified_spec_yaml`, `certified_warm_start_theta`, and
`stored_region_live_start_theta`.

A safe in-memory mutation changed all three consumed pointers while leaving the
authentication block unchanged. `_authenticate_inputs` still passed all ten
labels. It authenticated the certified specification at
`scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` while the
mutated contract pointer selected `scripts/p2a/run_p2a_regionlive_rebuild.py`.
No Phase-3 contract or objective was executed for this check.

The canonical config-path requirement from review-v2 section 21 is also not
implemented. The CLI accepts any `--config`; authorization hashes the path
supplied in `args.config` but never requires its resolved identity to equal
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`.

Consequently, authentication labels are exact, but authentication is not yet an
exact contract over every file actually consumed. `SELF` has been correctly
removed.

# 5. External authorization design

For the ordinary production CLI path, `_verify_external_authorization` is called
before lock acquisition and verifies:

- MNL HEAD;
- nested package commit, through the subsequent package-identity check;
- runner SHA-256;
- the SHA-256 of the supplied config;
- safety-test SHA-256; and
- approved-review SHA-256.

Missing, relative, absent, wrong-schema, malformed-hash, dirty-tracked-tree, and
hash-mismatch cases are refused in the implemented verifier.

External authorization is nevertheless not mandatory for every real execution
route. `run_phase3` defines production solely as `_txn_root is None` at line
1909. Passing `_txn_root=CANONICAL_PHASE3_ROOT` makes `production` false, skips
the authorization branch at lines 1940-1943, and sets the transaction root to
the canonical production directory. If `_contract_fn`, `_estimate_fn`, and
`_minimize_fn` are omitted, the defaults remain the real contract, estimator,
and SciPy minimizer. Injected functions could likewise publish a fabricated
exact-size `complete/` bundle at the canonical root. The comment that test seams
are confined to non-production roots is not enforced.

Authorization review identity is also loose:

- `approved_review_path` can identify an arbitrary or traversing path rather
  than the canonical reviewed report;
- the report need not be a tracked blob in the approved MNL commit; and
- the first-1000-character substring test accepts `APPROVE AFTER FIXES` as
  `APPROVE` when `REJECT` is absent.

The external record therefore contains the requested fields, but it does not
yet establish the exact reviewed config and exact approved review as a trusted
execution boundary.

# 6. Repository and package identity

The current repository state is internally consistent:

- nested HEAD equals the MNL gitlink at
  `27756a06ea189339aa82915ed2124628afed20eb`;
- parser, loader, JAX engine, and top-level `dclaborsupply` currently import from
  `dclaborsupply-monorepo/packages/dclaborsupply/src/dclaborsupply/`; and
- the nested tracked tree is clean.

The runtime enforcement is not exact. Runner line 1393 uses:

`all(str(nested) in module_path for module_path in imported_modules)`

This is substring matching. A sibling such as
`dclaborsupply-monorepo_evil/pkg.py` passes that expression while failing a true
`Path.is_relative_to(nested)` check. The verifier also checks only three named
modules even though the contract imports `EstimationSpec` from the top-level
package and those modules import additional package code.

Both MNL and nested cleanliness use `git status --porcelain -uno`, which ignores
untracked files. Thus the code proves the approved HEAD and absence of tracked
modifications, but not a fully clean reviewed source tree.

# 7. Safety-critical constants

The new immutable constants correctly hard-validate:

- full-precision target `19053.46553160094`;
- final objective tolerance `1e-4`;
- G-16 epsilon `1e-9`;
- 35-coordinate gradient threshold `1e-2`;
- bound-hit epsilon `1e-5`;
- 47/37/10 and household/alternative counts;
- exact ordered pins;
- expected two bound names; and
- exact L-BFGS-B method and option keys/values.

Two operative gate controls are omitted:

- `phase3.gates.pre_opt_objective_tol`, used at runner line 1757; and
- `phase3.gates.target_mismatch_status`, returned verbatim at line 1570.

A safe in-memory check changed the former to `1e99` and the latter to
`PHASE_3_COMPLETE`; `_validate_safety_constants` still passed. The latter change
would cause a failed G-1 target gate to return the success status consumed by
the publication path. This is a safety-critical closure failure.

# 8. Parameter-vector mapping

The 37-free-to-47-full implementation is correct.

`build_phase3_parameter_map` requires 47 unique names, the exact unique ordered
ten-name pin tuple, a disjoint and complete 37/10 partition, and deterministic
indices. `project_full_to_free` requires shape `(47,)`.
`expand_free_to_full` requires shape `(37,)`, places free coordinates in
production order, and injects immutable pin values.

The contract performs both projection/expansion round trips and a bitwise pin
check. The fake-minimizer route confirms that the optimizer receives 37 free
coordinates and 37 matching bounds. Final full gradients are projected with
the same `free_idx`. The 35-coordinate gate excludes exactly the two derived
expected-bound free parameters.

# 9. Fake-minimizer integration

The new integration fixture calls `_phase3_estimate` itself and does not call
the real optimizer. It loads the certified specification to obtain the actual
47-name order. The ten pin indices are asserted to be:

`[10, 11, 12, 13, 14, 15, 16, 17, 31, 32]`.

The fake minimizer asserts:

- 37 start coordinates and 37 bounds;
- `jac=True`;
- method `L-BFGS-B`;
- exact options `maxiter=5000`, `maxcor=30`, `ftol=1e-15`, and `gtol=1e-10`;
- positive negLL sign;
- positive gradient sign and correct free-coordinate ordering; and
- correct 37-to-47 expansion.

The route also verifies bitwise preservation of every pin.

# 10. Failure-gate coverage

The suite covers:

- optimizer `success=False`;
- an exception after minimizer invocation;
- target deviations on both sides of the target;
- the 35-free gradient gate;
- G-16 upper-bound violation;
- unexpected bound hit;
- exact expected-bound-set success;
- pin preservation;
- post-call input mutation;
- incomplete and unexpected artifact sets; and
- lock contention.

The executable gate order is correct: optimizer failure, pin/free structure,
G-16, expected-bound set, 35-free gradient, and then the two-sided target gate.

Residual low-level test gaps remain. There is no G-16 lower-bound case or exact
epsilon-boundary case, target mismatch is tested directly through
`_phase3_estimate` rather than through transaction/publication orchestration,
and the remediation-v2 report incorrectly states that test 28 routes input
mutation through `run_phase3`; test 28 routes an optimizer exception, while
mutation is covered directly by test 27.

# 11. Post-optimization input recheck

For the immutable authentication map, `_recheck_inputs` recomputes all ten
runtime paths and hashes and compares them to both the pre-call and accepted
values. `_phase3_estimate` performs that recheck at lines 1821-1829 before any
result artifact is written at lines 1864-1898. The fake mutation test confirms
S-8 and an empty staging directory.

This guarantee inherits the unresolved path-alias defect. If a different spec,
warm start, or stored theta is selected through its separate YAML pointer, the
post-call recheck hashes the hard-coded authenticated file rather than the
differently consumed file. Post-call rechecking is therefore correctly ordered
but incomplete over the actual possible input set.

# 12. Optimizer invocation state

`optimizer_called` is initialized false and marked true immediately before the
minimizer call. An exception from the minimizer is caught after that marker, and
the stopped attempt persists `optimizer_called: true`. The direct fake test and
the orchestration-level exception test both pass.

Dry-run manifests retain `optimizer_called: false`. The latest inspected
canonical dry-run attempt records
`authorization_status: AWAITING_POST_REVIEW_AUTHORIZATION`,
`execution_ready: false`, and `optimizer_called: false`.

# 13. Canonical output confinement

The ordinary production CLI correctly requires:

- `outputs/p2a_singles2016/region_live_v1` as the output root; and
- exactly `phase3_estimation_v1` as the Phase-3 subdirectory.

It refuses an existing successful `complete/` for a repeated real run. Dry runs
and failures finish under `attempts/`, and no reviewed path overwrites Phase 1-2
evidence.

The `_txn_root` authorization bypass weakens this guarantee at the API level:
the seam accepts the canonical root itself and can run default production code
or injected publishers there without authorization. It also accepts arbitrary
write roots. A test seam must be structurally unable to target the canonical
production tree.

# 14. Locking and legacy migration

The exclusive lock uses `O_CREAT | O_EXCL`. Lock acquisition occurs before
attempt-directory creation, legacy migration, and staging creation. The legacy
loose manifest/console migration now executes only while the lock is held.

The lock-contention test confirms that a held lock prevents contract execution,
does not migrate the legacy file, and does not create `attempts/`. This
review-v2 defect is closed.

# 15. Complete-bundle publication

Before success finalization, staging must contain exactly:

- `theta_estimated.csv`;
- `optimizer_diagnostics.json`; and
- `estimation_results.json`.

Finalization then writes `phase3_console.log`, calculates hashes over the four
non-manifest artifacts, writes `phase3_manifest.json` last, requires the exact
five-file final set, and atomically renames the staging directory to
`complete/`. Missing and unexpected files are refused. The manifest is not in
its own hash dictionary. Failed and review-required outcomes remain under
`attempts/`.

The transaction mechanism itself is sound. The separate authorization-seam
defect can still admit an unauthorized producer to that mechanism.

# 16. Phase metadata

Operative config metadata is corrected to:

- `phases_implemented: [1, 2, 3]`;
- `phase3_supported: true`;
- `phase3_execution_authorized: false`; and
- `phases_4_to_8_supported: false`.

Phase-3 manifests also carry authorization state and execution readiness.

The low review-v2 metadata defect is not completely closed: runner line 2 and
config line 2 still describe the files as “Phases 1-2.” The remediation-v2
report's claim of complete stale-metadata correction is therefore too broad.

# 17. Test adequacy

The following permitted validation was performed without real optimization:

- Python AST parse: runner and safety tests passed;
- YAML safe parse: config passed;
- package import-path inspection: current imports resolve beneath the nested
  repository;
- non-optimizing safety suite in the project virtual environment:
  **34 passed in 5.12 seconds**;
- current ten-input authentication: passed;
- safe in-memory consumed-path-alias mutation: authentication still passed,
  exposing the defect;
- safe in-memory gate-control mutation: safety validation still passed,
  exposing the defect;
- nested HEAD/gitlink comparison: equal;
- canonical dry-run evidence inspection: no `complete/`, no lock, no manifest
  self-hash; and
- `--phase 4 --dry-run`: refused with exit code 2 before any Phase-3 work.

Inspection proves that every `_phase3_estimate` test supplies `FakeMin`; the
real SciPy minimizer is not invoked.

Important missing tests correspond to the residual defects:

- canonical `_txn_root` seam refusal and default-real-estimator refusal;
- canonical config-path enforcement;
- consumed-path alias identity for spec/warm/start;
- exact valid authorization plus each bound-field failure;
- exact canonical review path and exact verdict parsing;
- true module ancestry and untracked-source refusal;
- `pre_opt_objective_tol` and `target_mismatch_status` mutation;
- G-16 lower and exact-boundary cases; and
- full orchestration isolation for target-high/target-low outcomes.

Test 34 defines a `good` authentication fixture but never exercises it.
`git diff --check` also fails at
`tests/p2a/test_p2a_regionlive_phase3_safety.py:702` because of a new blank line
at end of file.

# 18. Phase 1-2 regression safety

The Phase-3 CLI branch returns into `run_phase3` without re-running Phase 1 or
Phase 2. The reviewed diff does not alter the Phase 1-2 implementation bodies.
The Phase-3 contract consumes the accepted Phase 1-2 files read-only and checks
the accepted manifest script/config anchors.

The current accepted manifest, dry-run report, reload verification, frozen
stem, and metadata remain hash-authenticated. No Phase 1-2 production operation
was executed during this review.

# 19. Prohibited-operation audit

The runner's Phase-3 objective is the package-built JAX singles objective:
`build_jax_singles_ll` for male and female singles, summed into `tot`. The
package function returns negative log-likelihood, and the runner passes that
positive negLL plus its positive gradient to SciPy. No likelihood mathematics
is duplicated in the runner.

The direct SciPy route is confined to `_phase3_estimate`, where
`scipy.optimize.minimize` is imported only if no fake minimizer is supplied.
No inference, Hessian, scores, sandwich, post-estimation, welfare, synthetic
recovery, EUROMOD, draw generation, or notebook route exists in Phase 3.
Phases 4-8 are refused.

The accepted certified warm start and stored region-live theta are intentional
contract inputs. No stale P2a result, standard-error, inference, or
post-estimation artifact is used as an estimation result.

This review ran no real Phase 3, real optimizer, EUROMOD, inference,
post-estimation, welfare, or notebook.

# 20. Residual defects

1. **High — authenticated and consumed paths can diverge.** The spec, warm
   theta, and stored theta can be consumed through pointers outside the exact
   authentication map. The canonical reviewed config path is also not required.
2. **High — external authorization is bypassable.** `_txn_root` alone selects
   non-production mode, accepts the canonical root, and leaves real default
   functions available.
3. **High — a YAML status can turn a failed target gate into success.**
   `target_mismatch_status` is returned verbatim and is not independently
   validated. `pre_opt_objective_tol` is also unpinned.
4. **Medium — authorization does not identify the exact approved review.**
   Review/config paths are not canonical, verdict matching is a substring test,
   and clean-tree enforcement ignores untracked files.
5. **Medium — package source containment is not proven.** Module location uses
   substring matching, omits the top-level package and transitive modules, and
   ignores untracked files.
6. **Low — tests and metadata are not fully closed.** Two headers remain stale;
   several tests named above are missing; remediation-v2 misdescribes test 28;
   test 34 contains unused setup; and `git diff --check` fails.

# 21. Required fixes

1. Use `_phase3_runtime_paths()` as the sole source for every Phase-3 file open,
   or require every legacy config alias to resolve exactly to its corresponding
   runtime-map path before any read. Add tests that mutate each alias.
2. Require `Path(args.config).resolve()` to equal the canonical config path in
   both the CLI and authorization verifier.
3. Seal all test seams from the production tree. At minimum, reject any injected
   transaction root equal to or beneath the canonical Phase-3/output tree and
   require explicitly injected fake contract, estimator, identity verifier, and
   minimizer for non-production runs. Prefer moving test orchestration into a
   helper that cannot select production paths.
4. Hard-code or independently validate
   `pre_opt_objective_tol == 1e-4` and
   `target_mismatch_status == "REVIEW_REQUIRED_TARGET_MISMATCH"`. Do not return a
   YAML-defined success status for G-1 failure.
5. Require the exact canonical review file, require an exact parsed final verdict
   of `APPROVE`, bind it to a tracked blob in the approved MNL commit, and test
   every authorization field. Do not accept `APPROVE AFTER FIXES`.
6. Replace module-path substring matching with resolved ancestry checks such as
   `Path.is_relative_to`. Include the top-level package and all safety-critical
   imported modules, and address untracked source in both repository-cleanliness
   checks.
7. Add the missing seam, path-alias, authorization, constant, G-16 boundary, and
   target-publication tests. Correct the remediation report's test description,
   stale headers, unused test setup, and `git diff --check` failure.
8. Request another independent read-only review. Do not create an execution
   authorization file before that review returns `APPROVE`.

# 22. Whether implementation may be committed

**No, not as an authorization-ready Phase-3 implementation.**

The high-severity provenance and authorization defects remain, and
`git diff --check` is not clean. Committing this state for post-review
authorization would bind known bypasses into the supposedly approved revision.
No commit was made by this review.

# 23. Whether Phase 3 may execute after authorization

**No.**

An authorization file for the exact current implementation would not repair
the consumed-path divergence, canonical-config omission, `_txn_root` bypass,
unvalidated target status, or package-path check. Because this review's final
verdict is `REJECT`, no valid post-review authorization should be created and
the first real Phase-3 estimation must not run.

# 24. Immediate next action

Implement only the required fixes in section 21, extend the non-optimizing
safety suite, obtain a clean `git diff --check`, and request a fourth
independent static review. Keep real Phase 3 blocked and do not create the
external authorization file unless that later review returns an exact
`APPROVE`.
