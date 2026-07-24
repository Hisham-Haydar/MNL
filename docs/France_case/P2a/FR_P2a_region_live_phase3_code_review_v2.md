# 1. Second-review verdict

**REJECT**

The remediation closes the prior-success overwrite risk and correctly implements the
37-free-to-47-full parameter map, immutable pins, G-16, the 35-coordinate gradient gate,
canonical output confinement, directory-level publication, manifest hashing, and persisted final
status. The implementation must nevertheless not execute because the original high-severity input
provenance defect is only partially resolved, and the original required non-optimizing test
coverage remains materially incomplete.

The decisive provenance failure is structural, not a mismatch in the current files:
`_authenticate_inputs` neither requires the exact authentication-key set nor binds authenticated
paths to the independently constructed paths later consumed. It also treats the config's
`sha256: SELF` value as the just-measured hash, which records and rechecks the config but does not
authenticate it against an accepted pre-run digest. Consequently, a consumed input may be omitted
from the authentication table, or file A may be authenticated while file B is consumed. The
post-optimization recheck faithfully rechecks that same incomplete table and therefore does not
close the defect.

# 2. Scope

This was an independent static review of the complete current uncommitted Phase-3 remediation.
The only file written by the review is this requested report. No real Phase 3, estimation,
optimizer, EUROMOD, inference, post-estimation, welfare, or notebook was run, and no commit was
made.

Answers to the 26 required questions:

| Q | Answer | Static conclusion |
|---:|:---:|---|
| 1 | Yes | SciPy receives a 37-element free vector. |
| 2 | Yes | Expansion reconstructs the 47-name package-objective vector deterministically. |
| 3 | Yes | The ten pins are excluded from the optimizer and injected immutably. |
| 4 | Yes | Projection and expansion round-trip exactly. |
| 5 | Yes | The ten-name pin tuple is checked for identity, uniqueness, existence, and order. |
| 6 | Yes | G-16 is persisted and enforced at the configured `1e-9`. |
| 7 | Yes | The gradient gate uses exactly 35 non-bound free parameters. |
| 8 | **No** | Authentication has no exact required-key/runtime-path binding and config self-authentication is tautological. |
| 9 | Partial | Rehash timing and comparison are correct, but only the incomplete pre-run table is rechecked. |
| 10 | Yes | Phase 1-2 manifest status and accepted script/config anchors are checked. |
| 11 | Yes | The resolved canonical region-live root is hard-enforced in production. |
| 12 | Yes | The exact `phase3_estimation_v1` subdirectory is hard-enforced. |
| 13 | Yes | Dry-runs and controlled failures do not alter `complete/`. |
| 14 | Yes | A repeated real run cannot replace an existing `complete/`. |
| 15 | Yes | An exclusive `O_CREAT | O_EXCL` lock protects the active run. |
| 16 | Partial | Publication is a directory rename, but success does not assert that all four required non-manifest artifacts exist. |
| 17 | Yes | The manifest is excluded from its artifact-hash dictionary. |
| 18 | Yes | `FINAL STATUS:` is written before console hashing and publication. |
| 19 | Yes | Target mismatch and controlled failures are routed outside `complete/`. |
| 20 | Yes | Method, option keys, and option values are exact. |
| 21 | Yes | The safety tests avoid real estimation and the real optimizer. |
| 22 | **No** | Tests do not cover the actual fake-minimizer integration or several original failure modes. |
| 23 | Yes | Phase 1-2 control flow is preserved by static inspection. |
| 24 | Yes | Phases 4-8 are absent from the Phase-3 route and `--phase > 3` is refused. |
| 25 | Yes | Direct SciPy use is limited to the objective built by the package JAX API. |
| 26 | **No** | The unresolved high provenance defect prevents the first real estimation. |

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_manager_decisions_v2.md`
- `FR_P2a_region_live_production_rebuild_plan_v2.md`
- `FR_P2a_region_live_phase12_manager_acceptance_v1.md`
- `FR_P2a_region_live_phase3_implementation_report_v1.md`
- `FR_P2a_region_live_phase3_code_review_v1.md`
- `FR_P2a_region_live_phase3_remediation_report_v1.md`
- `FR_P2a_region_live_dry_run_report_v2.md`
- `scripts/p2a/run_p2a_regionlive_rebuild.py`
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`

The relevant package specification/parser, initial-value binding, singles loader, JAX likelihood,
and optimizer-wrapper APIs under
`dclaborsupply-monorepo/packages/dclaborsupply/src/dclaborsupply/` were also reviewed. The complete
tracked diff, all relevant untracked files, repository status, Phase-3 attempt layout, and nested
repository state were inspected. The nested repository was clean at
`27756a06ea189339aa82915ed2124628afed20eb`, and the imported package currently resolved to that
working tree.

# 4. Resolution of critical defects

The prior critical overwrite defect is resolved. A run uses a unique staging directory, an
exclusive lock, and an immutable `complete/` destination. Real reruns refuse when `complete/`
exists, and finalization checks again immediately before a successful publish. Dry-runs, target
mismatches, optimizer/gate failures, and caught exceptions are moved to `attempts/`, not
`complete/`.

The current production directory contains no `complete/` and no `.phase3.lock`; the two existing
records are dry-run/rejected-review attempts. This review did not change them.

# 5. Resolution of high defects

- **G-16:** resolved for the reviewed config and post-fit code.
- **Canonical confinement:** resolved for the production CLI.
- **Explicit 37-free/47-full mapping:** resolved.
- **Complete input authentication:** **not resolved**. All current non-self configured hashes match
  the present files, but the implementation does not guarantee that the configured rows are the
  complete set of runtime inputs or that their paths equal the paths actually read. The config
  itself has no accepted pre-run hash.
- **Post-optimization authentication:** implemented with correct timing, but only over the
  incomplete/self-trusting pre-run table; therefore the high provenance defect remains open as a
  whole.

Because at least one original high defect remains, this review cannot use `APPROVE AFTER FIXES`.

# 6. Resolution of medium defects

Exact pin-set validation is resolved. Directory-level publication and manifest self-hashing are
resolved on the normal production path. The console-status defect is also resolved.

The required safe-test remediation is incomplete. Eighteen tests pass, but none calls
`_phase3_estimate`, supplies `_minimize_fn`, or uses a fake optimizer result. The remediation
report's statement that the suite uses fake objectives/optimizers is therefore inaccurate. There
is also no success-bundle completeness assertion before publication and no test for that failure
mode.

# 7. Parameter-vector mapping

`build_phase3_parameter_map` requires 47 unique full names, the exact ordered ten-name accepted pin
tuple, pin existence, disjoint free/pin sets, and exactly 37 free names. Projection requires shape
`(47,)`; expansion requires shape `(37,)`; both use indices derived from the package's
`spec.all_param_names`.

A safe structural check against the actual spec produced 47 full names, 37 free names, ten pins,
and pin indices `[10, 11, 12, 13, 14, 15, 16, 17, 31, 32]`. Full-to-free-to-full reconstruction and
the reverse free-vector round-trip were bitwise exact after substituting the defined pin values.

# 8. Pin handling

The config pin list must equal the immutable `ACCEPTED_PIN_NAMES` tuple exactly, including order.
Duplicates, missing members, extras, unknown names, or reordering stop the contract. Pin values are
read from the accepted warm start, omitted from both the optimizer vector and optimizer bounds,
injected during every 37-to-47 expansion, and checked bitwise after optimization. This resolves the
original pin-identity and optimizer-exclusion defects.

# 9. G-16 and bounds

The reviewed config sets `g16_inbounds_epsilon: 1.0e-9`. Every one of the 37 free estimates is
checked against `lo - epsilon` and `hi + epsilon`; parameter-level evidence and
`g16_inbounds_ok` are persisted, and violation yields S-3.

The expected bound set is derived from the accepted start vector and spec bounds, then compared
with both the configured names and the runner's named constant. It resolves to
`beta_l_age2_sm` and `beta_l_age2_sf`. The remaining non-bound free set is asserted to contain
exactly 35 names, and only those names enter G-3. A residual fail-closed gap is that the runner does
not independently assert `epsilon == 1e-9`; it trusts the unauthenticated config value.

# 10. Input provenance

The reviewed YAML contains 12 authentication rows. The eleven rows with fixed digests currently
exist and match their configured SHA-256 values. The contract also checks the accepted Phase 1-2
manifest status and its recorded runner/config hashes against the registered anchors.

Three implementation defects remain:

1. `_authenticate_inputs` iterates whichever keys the config supplies and never asserts the exact
   required label set.
2. Authenticated paths are not mapped to and compared with the exact resolved runtime paths used
   for the spec, warm start, stored start theta, Phase 1-2 JSON evidence, stem, and companion
   metadata. The stem check is only a filename-suffix check.
3. For `phase3_config_self`, `expected` is replaced with the just-computed `actual` digest. This
   detects a mid-run change but accepts any pre-run config content.

A read-only helper check demonstrated both failures: deleting the consumed
`certified_spec_yaml` row still returned a successful 11-row authentication table, and changing
the runtime `certified_spec.yaml` path while leaving the authentication row unchanged still made
every authentication row pass. No optimizer or Phase-3 route was invoked for this check.

The package source is recorded as Git state but not enforced as the reviewed clean commit or as
the module paths under the nested repository. That weakens the fresh-process guarantee.

# 11. Post-optimization recheck

`_recheck_inputs` runs after the optimizer and final objective/gradient evaluation but before the
first result artifact write. It recomputes each listed hash and requires
`post == pre == expected`; a mismatch returns S-8 evidence without writing estimation result
artifacts. That ordering is correct.

The answer remains partial because omitted authentication rows and authenticated-path/runtime-path
divergence flow unchanged into the recheck. There is also no final rehash immediately before the
directory rename, although the registered requirement only demanded a post-optimizer,
pre-publication check.

# 12. Canonical output confinement

Production hard-codes and resolves
`MNL/outputs/p2a_singles2016/region_live_v1`, requires the config root to resolve to the same
location, and requires the exact `phase3_estimation_v1` subdirectory before creating a transaction.
All production Phase-3 artifacts are staged beneath that canonical Phase-3 root. Temporary roots
exist only through underscore-prefixed dependency-injection seams used by tests and are not
available from the CLI.

# 13. Locking and attempt isolation

The `.phase3.lock` file is created exclusively with `O_CREAT | O_EXCL`; an existing lock refuses
the run and requires manual inspection. Staging is attempt-specific, non-success results go to
attempt-specific directories, and `complete/` is separate and immutable.

Directory creation and one-time legacy-evidence migration occur before lock acquisition. This does
not expose `complete/`, but those ancillary mutations are not covered by the exclusive lock and
should be moved behind it for a fully serialized transaction.

# 14. Transactional publication

Successful publication uses `os.replace(staging, complete)` on the same filesystem, so the normal
four-artifact result set plus manifest becomes visible at directory level rather than through
per-file replacement. The console is completed first, the non-manifest artifacts are hashed, and
the manifest is written last. The manifest correctly does not hash itself.

`_bundle_hashes` silently hashes only required artifacts that are present. Before accepting
`PHASE_3_COMPLETE`, the runner should require the exact four-file non-manifest set and the manifest
write, then refuse publication if any required member is absent.

# 15. Failure preservation

Controlled contract, optimizer, G-16, gradient, bound, and unexpected failures after transaction
acquisition finalize a `STOPPED` attempt bundle. A target mismatch receives its review-required
status under `attempts/`. A prior successful `complete/` is never replaced. Lock-acquisition and
pre-transaction canonical-path refusals intentionally cannot write an attempt bundle.

A residual evidence defect exists if `_phase3_estimate` raises after the real optimizer has been
invoked: `manifest["optimizer_called"]` is set only after `_phase3_estimate` returns, so such a
STOPPED manifest can incorrectly record `optimizer_called: false`.

# 16. Optimizer contract

The validator requires exactly `method` and `options`, method `L-BFGS-B`, option keys exactly
`maxiter`, `maxcor`, `ftol`, and `gtol`, and values exactly `5000`, `30`, `1e-15`, and `1e-10`.
The call passes a 37-element start vector, 37 bounds, `jac=True`, and the validated settings.

The objective is the sum of the male and female negative log-likelihood functions returned by the
package's `build_jax_singles_ll`. The runner adds no likelihood mathematics. Its callback expands
37 free coordinates to the package's ordered 47-vector and returns the package negative objective
and its projected analytic gradient with no sign reversal. Direct SciPy use is justified because
the reviewed package wrapper cannot express the registered `maxcor=30`.

The objective gate is two-sided: either a worse fit or a materially better fit outside the two
registered tolerances becomes `REVIEW_REQUIRED_TARGET_MISMATCH`, never automatic success.

# 17. Test adequacy

Command run safely with bytecode and pytest caches disabled:

`python -m pytest -q tests/p2a/test_p2a_regionlive_phase3_safety.py -p no:cacheprovider`

Result: **18 passed**. Inspection proves these tests do not import/call the real optimizer or run
real estimation.

Coverage is nevertheless insufficient for the first review's required fix. No test exercises the
actual `_phase3_estimate` wrapper with a fake minimizer and fake result. Therefore the suite does
not directly verify the real call's 37-element `x0`, 37 bounds, `jac=True`, objective/Jacobian
signs, 47-vector expansion, gradient projection, return handling, or post-optimizer recheck
ordering. It also lacks integrated tests for omitted/wrong authentication paths, input mutation
inside a fake optimizer, G-16 boundary/lower-bound behavior, gradient failure, pin mutation,
target-mismatch isolation, optimizer failure, exclusive-lock contention, and incomplete successful
bundles. The current mapping fixture places pins contiguously rather than exercising the actual
interleaved spec order.

# 18. Phase 1-2 regression safety

The Phase-3 route remains a separate branch and does not call Phase 1 or Phase 2. The reviewed
Phase 1-2 code has no remediation hunk, and the accepted Phase 1-2 evidence and frozen stem remain
unchanged. Static Python/YAML parsing and the Phase-3 safety suite passed. This review did not rerun
the Phase 1-2 dry-run.

The config's `run.phases_implemented: [1, 2]` and adjacent comment remain stale now that Phase 3 is
implemented and authorized; this is a documentation/config metadata defect, not an operative
control-flow regression.

# 19. Prohibited-operation audit

The Phase-3 contract imports the package spec, loader, and JAX likelihood only. SciPy is imported
inside the real estimation function only when no fake minimizer is supplied. Dry-run returns
before estimation and asserts that `scipy.optimize` is not loaded. No Hessian, rank, inference,
post-estimation, welfare, EUROMOD, proposal-draw generation, or notebook execution exists in the
Phase-3 path. `--phase > 3` is refused.

During this review, Python AST and YAML parsing passed, current configured hashes were checked
read-only, the mapping helpers were checked against the actual spec, `git diff --check` passed,
and all 18 safety tests passed. No prohibited computation was executed.

# 20. Residual defects

1. **High — input authentication remains incomplete.** Required labels and exact runtime paths are
   not enforced, and the config is not authenticated against an accepted pre-run digest.
2. **Medium — fresh-process package identity is not enforced.** The imported package path/commit
   is recorded but not required to equal the reviewed nested source.
3. **Medium — mandated non-optimizing integration tests remain incomplete.** The fake-minimizer
   seam and several original gate/failure modes are untested.
4. **Medium — successful-bundle completeness is not asserted.** Directory publication is atomic,
   but `_bundle_hashes` accepts a subset of the required artifacts.
5. **Medium — optimizer invocation can be misreported on an exception.** A post-invocation
   exception can persist `optimizer_called: false`.
6. **Low — lock scope and metadata need cleanup.** Legacy migration precedes lock acquisition,
   and `phases_implemented` still says `[1, 2]`.

# 21. Required fixes

1. Define an immutable exact authentication-label-to-runtime-path contract; require the exact key
   set and compare every configured authentication path with the resolved path actually consumed.
2. Supply a trusted pre-run anchor for the canonical config, such as an externally supplied
   accepted digest or approved immutable revision, rather than replacing `SELF` with the measured
   value. Require the canonical config path.
3. Hard-validate the manager-ratified G-16 epsilon and other safety-critical config constants that
   currently depend on the unanchored config.
4. Enforce the reviewed package source identity/module locations or an approved clean nested-repo
   revision before building the objective.
5. Add a fake-minimizer integration suite around `_phase3_estimate`, including optimizer-call
   shape/sign/options, post-call input mutation, all failure gates, target isolation, pin
   preservation, and actual interleaved parameter order.
6. Refuse `PHASE_3_COMPLETE` unless the exact required artifact set exists; test incomplete-bundle
   refusal and lock contention.
7. Persist optimizer-invocation state accurately even when estimation raises, move legacy
   migration behind the lock, and correct stale Phase-3 metadata.

# 22. Whether Phase 3 may execute

**No.** The final verdict is **REJECT**. The first real Phase-3 estimation must remain blocked
because the original high-severity provenance defect is still statically exploitable and the
required safety-test remediation is incomplete.

# 23. Immediate next action

Implement the required provenance/path-binding and test fixes without running real estimation,
then request a third independent static review. Do not execute Phase 3 until that review returns
`APPROVE`.
