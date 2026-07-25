# 1. Fifth-review verdict

**FINAL VERDICT: REJECT**

Not every required fix in review-v4 section 18 is closed. The authorization-location,
single-runtime-map, G-16-boundary, stale-metadata, dry-run, and regression fixes are
substantially closed. Three safety properties remain open:

1. the production orchestrator accepts a caller-created authorization record instead of
   verifying the external authorization internally;
2. the test-double boundary can be bypassed with wrappers and by calling the test body
   directly; and
3. package identity authenticates the path named by a module, not the executing module
   object, and it compares Git-filtered content rather than requiring raw working bytes to
   equal the committed blob.

The review-v5 verdict parser also does not enforce the required exact first-section line.
The present state must not be authorized or used for a real Phase-3 estimation.

# 2. Scope

This was an independent, read-only review of the Phase-3 implementation at:

- MNL HEAD `ee3cb4c5ecf5cb6d31e4f8e28ff25180867c315f`;
- nested `dclaborsupply-monorepo` HEAD and MNL gitlink
  `27756a06ea189339aa82915ed2124628afed20eb`; and
- review-v4 reference commit `6dda418f6f5b60992e73a521a25c3b5651410457`.

The MNL and nested worktrees were clean before this review file was created. The tracked and
staged current diff was empty. The complete change from review v4 to the reviewed HEAD was
also inspected.

No real Phase 3, optimizer, EUROMOD, inference, post-estimation, welfare, or notebook was
run. No execution-authorization file was created. No implementation, config, test, package,
or production-output file was edited. The only file created by this review is this report.

# 3. Files reviewed

The following Phase-3 records were read in full:

- `FR_P2a_region_live_phase3_implementation_report_v1.md`;
- `FR_P2a_region_live_phase3_remediation_report_v1.md` through
  `FR_P2a_region_live_phase3_remediation_report_v4.md`;
- `FR_P2a_region_live_phase3_code_review_v1.md` through
  `FR_P2a_region_live_phase3_code_review_v4.md`; and
- `FR_P2a_region_live_dry_run_report_v2.md`.

The current implementation surface was read in full:

- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; and
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`.

Every module named by `REQUIRED_PACKAGE_MODULES` was read:

- `dclaborsupply/__init__.py` and `dclaborsupply/models.py`;
- `dclaborsupply/data/__init__.py` and `dclaborsupply/data/loader.py`;
- `dclaborsupply/spec/__init__.py` and `dclaborsupply/spec/parser.py`; and
- `dclaborsupply/likelihood/__init__.py`, `index.py`, `engine_jax.py`, and
  `_numpy_primitives.py`.

Git status, both repository revisions, the MNL gitlink, current diffs, the review-v4-to-HEAD
diff, committed Phase-3 dry-run evidence, Git blobs, loaded-module paths, and path-containment
behavior were inspected.

# 4. Production orchestration closure

Question 1 passes narrowly; questions 2-4 do not.

The old `_phase3_orchestrate` name has been removed, and `run_phase3()` correctly performs
canonical config/output checks and calls `_verify_external_authorization()` for a non-dry
run. That wrapper is not the whole production boundary, however.

`_phase3_orchestrate_production(args, cfg, authorization_record)` remains a directly callable,
production-capable orchestrator. It:

- accepts `authorization_record` from its caller;
- checks only that `verified is True` and `execution_ready is True`;
- does not call `_verify_external_authorization()` itself;
- hard-selects `CANONICAL_PHASE3_ROOT`;
- calls the genuine package-identity verifier and contract; and
- reaches `_phase3_estimate(..., minimize_fn=None)`, which imports the real SciPy minimizer.

Consequently, a caller-created dictionary containing the two accepted booleans can cross the
orchestrator's authorization check. If the forged record omits
`approved_dclaborsupply_commit`, package verification falls back to the current nested HEAD.
This path was established by static control-flow review; it was deliberately not executed.

Test 45 checks `{}` and a record with `verified: true` but `execution_ready: false`. It does
not check the dangerous record in which both fields are true. The docstring's statement that
the orchestrator exposes no alternative authorization is therefore stronger than the
implementation.

Answers:

- Q1: Yes, narrowly. The generic orchestrator that injected root, contract, estimator,
  minimizer, and identity verifier has been eliminated. The replacement still has the
  distinct authorization-injection defect described above.
- Q2: Yes. A direct callable combines canonical production paths with the injected
  authorization record and then genuine production components.
- Q3: No. Root, contract, estimator, identity verifier, and minimizer are fixed, but
  authorization remains injectable.
- Q4: No. Verification is performed only by the wrapper, not internally by every non-dry
  production attempt.

# 5. Test-double isolation

The root-containment part is sound: `_run_phase3_test_attempt()` and
`_phase3_attempt_test_body()` resolve the requested root and reject the canonical Phase-3
root, the region-live root, `MNL/outputs`, the entire MNL worktree, and the nested worktree.
Thus Q5 passes.

The callable boundary is not sound:

- `_validate_test_double()` rejects only exact object identity for the genuine contract,
  estimator, and identity verifier.
- A marked `functools.partial` around each genuine callable was accepted by a permitted
  static probe.
- A marked `functools.partial` around a callable identifying as
  `scipy.optimize._minimize.minimize` was also accepted.
- `_phase3_attempt_test_body()` is itself directly callable and rechecks only the root. It
  does not validate the four injected callables. It can therefore accept the exact genuine
  contract, estimator, identity verifier, and minimizer on a root outside the worktrees.

No accepted callable was invoked by the probe. `scipy.optimize` remained unloaded.

Tests 45-46 cover bare-object identity and a bare SciPy-named stub, but do not cover partials,
wrapped callables, or direct test-body access with genuine components.

Answers:

- Q6-Q9: No as safety properties. Bare genuine objects are rejected by the outer helper,
  but wrappers and the direct test body bypass those checks.

# 6. Authorization location

Questions 10-11 pass.

`_verify_external_authorization()` requires an absolute existing file, resolves it, and
rejects it when it equals or descends from either the MNL or nested worktree. This check is
independent of Git status and ignore rules. Test 47 covers ordinary, ignored, nested, and,
when the host permits it, symlink-resolved in-worktree locations, plus a valid outside-tree
location.

No JSON matching the Phase-3 execution-authorization schema was present in the reviewed
worktree. No authorization file was created during this review.

# 7. Package-module authentication

Questions 12 and 14-16 are not fully closed; Q13 passes at the declared-name level.

The immutable inventory now names all ten requested modules: top-level package, `models`,
`data`, loader, `spec`, parser, `likelihood`, index, JAX engine, and
`_numpy_primitives`. The verifier also appends other currently loaded
`dclaborsupply.*` modules that expose `__file__`. For each claimed file it checks resolved
ancestry, tracked-blob existence at the selected commit, and a Git-filtered working blob id.
This correctly rejects a module whose declared path is outside the reviewed source root and
ordinary untracked or modified files.

It does not authenticate the executing module object. It trusts mutable `__name__` and
`__file__` attributes, then hashes the file at that claimed path. In a fresh-process,
no-optimizer probe:

- an in-memory fake `dclaborsupply.likelihood._numpy_primitives` claimed the genuine tracked
  `_numpy_primitives.py` path;
- `_verify_package_identity()` returned `package_identity_ok: true`,
  `module_failures: []`, and `blob_equal: true`; and
- `dclaborsupply.data.loader` actually imported and retained both fake
  `PrecomputedDataSingles` and fake `PrecomputedDataCouples`.

Thus a preloaded or custom-loader substitution can authenticate file A while executing module
B. The outside-path test does not cover a substituted module that claims the genuine path.

The literal raw-byte requirement also fails. The verifier uses
`git hash-object --path`, which applies Git attributes/EOL filters. Two examples from the
clean reviewed nested checkout were:

| Module file | Committed raw SHA-256 | Working raw SHA-256 | Filtered blob id equal |
|---|---|---|---|
| `spec/parser.py` | `8207260fb1c4e363f523df5d3eccbefed29eab35b989bfbdf1eb162a71893456` | `94d436749f7bffbbd92683c390c452d575212f2d8ade2d449aa26dab1a7dbf29` | yes |
| `likelihood/_numpy_primitives.py` | `99e47ea35e1da94ac96bc490a87ab917ceb27f6db07b41aefb8a7af04ae650f8` | `4d1a2ad6d781e0b834acc6ef20b51f8c96ad894f4a4dea962384acc69163cffe` | yes |

The difference is consistent with checkout EOL normalization, but Q15 and review-v4 section
18 explicitly require working source bytes to equal the committed blob. The current
implementation records unequal raw hashes and still passes.

Answers:

- Q12: No, because the records authenticate claimed paths rather than the executing objects.
- Q13: Yes, the requested ten module names are in the required inventory.
- Q14: Only for each claimed path, not for the code object actually supplying the module.
- Q15: No; Git-filtered equality is used and raw byte inequality currently passes.
- Q16: No; ordinary outside/untracked paths fail, but a substituted module that claims the
  tracked `_numpy_primitives.py` path passes.

# 8. Runtime-map lifecycle

Question 17 passes on the genuine production route. `_phase3_orchestrate_production()` creates
one runtime-path map, fingerprints it, and passes the same object to `_phase3_contract()`.
The contract uses it for authentication and consumption, retains it in the context, and
`_phase3_estimate()` uses that retained object for the post-call recheck. Tests 50 and 52
verify that a poisoned factory is not called later.

Question 18 passes only on a normal optimizer return. The pre-attempt fingerprint is persisted
in the manifest, and normal completion persists equal pre/post fingerprints in diagnostics.
If the minimizer raises, the exception path rehashes the retained paths but does not calculate,
compare, or persist a post-call runtime-map fingerprint. A runtime-map-fingerprint failure
also raises before a post fingerprint can be recorded in the normal diagnostics. Stable
identity is therefore enforced and evidenced on the normal path, but not persisted uniformly
for every optimizer outcome.

# 9. G-16 exact boundaries

Questions 19-21 pass.

The fixed epsilon is `1e-9`. Test 43 establishes:

- exactly `lo - epsilon`: pass;
- exactly `hi + epsilon`: pass;
- `nextafter(lo - epsilon, -infinity)`: fail; and
- `nextafter(hi + epsilon, +infinity)`: fail.

The aggregate assertion directly compares `g16_inbounds_ok` with the independently expected
boolean; it is no longer tautological. These checks passed in the full suite.

# 10. Review-v5 authorization binding

Question 22 passes: `CANONICAL_APPROVED_REVIEW_REL` is fixed to
`FR_P2a_region_live_phase3_code_review_v5.md`; the authorization must name that exact path,
bind its committed blob hash, and find it as a tracked blob in the approved MNL commit.

Question 23 fails. `_parse_review_verdict()` strips each candidate line and, for section
placement, only rejects a marker appearing after the second top-level heading. Static probes
showed that it accepts:

- an approval marker padded with leading and trailing spaces;
- an approval marker in a preamble before the first section; and
- an approval marker inside a fenced Markdown code block.

The positive test fixture is also stale: `GOOD_REVIEW` still begins with
`# 1. Fourth-review verdict` even though it is written to the canonical v5 path. The parser
accepts it because it does not require the exact first heading or require the marker to be
plain Markdown content strictly inside that section.

Only the exact unpadded approval line as ordinary content inside the exact v5 first section
should be accepted.

# 11. Test adequacy

The full safety suite completed:

```text
51 passed, 1 skipped in 15.94s
```

The skip was the Windows symlink test because this host lacks symlink privilege. The resolved
ancestry implementation and the remaining authorization-location cases passed. Python AST
parsing succeeded for the runner and tests, and the YAML parsed successfully.

The suite uses fake minimizers and did not invoke the real optimizer or real estimation.
Independent probes also ended with no `scipy.optimize` module loaded. Therefore Q24 passes.

The suite is not adequate to approve the implementation because it omits the exact failure
modes demonstrated in sections 4, 5, 7, and 10:

- both authorization booleans forged on direct production-orchestrator access;
- partial/wrapped genuine callables;
- direct test-body access with genuine callables;
- an in-memory module with a spoofed genuine `__file__`;
- raw committed-blob versus working-byte inequality; and
- padded, preamble, fenced, or wrong-first-heading verdict markers.

`git diff --check`, the review-v4-to-HEAD diff check, and `git show --check HEAD` all passed.
Thus Q25 passes.

# 12. Phase 1-2 regression safety

Question 26 passes on the evidence reviewed.

A permitted scratch Phase 1-2 dry-run completed with exit code 0 and status
`DRY_RUN_PHASES_1_2_COMPLETE`; both phases passed and the reconstructed frozen-stem SHA-256
remained:

`8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

The scratch output was removed. The committed Phase 1-2 acceptance and dry-run evidence remain
unchanged, and no optimizer or prohibited later phase was invoked.

# 13. Phase-3 dry-run safety

Question 27 passes.

The latest committed dry-run attempt,
`20260725T151424Z_116824_672700_dryrun_PHASE_3_DRY_RUN_COMPLETE`, records:

- `authorization_status: AWAITING_POST_REVIEW_AUTHORIZATION`;
- `execution_authorization: null`;
- `execution_ready: false`;
- `optimizer_called: false`;
- start negLL `19053.46553160094` with deviation `0.0`; and
- no `complete/` directory and no remaining lock.

The dry-run follows the genuine contract path but stops before `_phase3_estimate()`.

# 14. Prohibited-operation audit

Question 28 passes. The production runner accepts only Phases 1-3 and refuses Phases 4-8
before execution. The current implementation contains no Phase 4-8 orchestration.

During this review:

- real Phase 3 and the real optimizer were not called;
- no execution authorization was created;
- EUROMOD, inference, post-estimation, welfare, and notebooks were not run;
- no production output was written or changed;
- no implementation file was modified; and
- no commit was made.

# 15. Residual defects

1. **Critical — caller-forgeable production authorization.**
   `_phase3_orchestrate_production()` trusts two booleans in its caller-supplied record and
   can then reach the canonical root and real optimizer route.
2. **High — production components can cross the test seam.**
   Partial/wrapped genuine callables pass `_validate_test_double()`, and the direct test body
   performs no callable validation.
3. **High — executing package module is not authenticated.**
   A substituted in-memory module can claim a genuine path, pass blob verification, and be
   consumed by the loader.
4. **Medium — raw working bytes are not required to equal the committed blob.**
   Git-filtered equality is intentionally used, contrary to the explicit review requirement.
5. **Medium — review verdict parsing is not exact.**
   Padded, preamble, fenced, and wrong-first-heading approval documents are accepted.
6. **Low — runtime-map post fingerprint is incomplete on failure paths.**
   The normal return is fully evidenced, but optimizer-exception and fingerprint-failure
   paths do not persist a post fingerprint.
7. **Low — remediation-state description is stale.**
   The remediation-v4 report says the implementation was uncommitted, whereas the reviewed
   implementation and subsequent dry-run evidence are already committed at the reviewed
   HEAD.

# 16. Required fixes

1. Remove `authorization_record` from the production-orchestrator interface. Every direct
   non-dry production callable must resolve and call `_verify_external_authorization()`
   internally, then pass only a verifier-produced, non-caller-constructible result into the
   attempt body. Add a safe test proving a forged two-boolean dictionary cannot cross this
   boundary without touching the canonical transaction root.
2. Put test-only orchestration in a structurally separate test module or enforce callable
   validation inside the deepest callable body. Recursively unwrap `functools.partial`,
   `__wrapped__`, bound methods, and callable objects, and reject every genuine production
   component and real SciPy minimizer. Add direct-body and wrapper-bypass tests.
3. Authenticate the code actually executing, not mutable module metadata. Perform controlled
   imports from the approved source root in an isolated fresh process, reject preloaded
   substitutions, and validate import specs/loaders/origins and relevant code origins. Add
   the demonstrated spoofed-`__file__` regression test.
4. Implement the review-v4 raw-byte contract, or formally amend the governing requirement.
   If raw equality remains required, compare `Path.read_bytes()` directly with `git cat-file
   blob` bytes and establish checkout attributes that make legitimate reviewed files equal.
5. Parse the review document structurally: require the exact v5 first heading, exactly one
   unpadded verdict line as ordinary content between the first and second headings, and no
   fenced/code-block match. Correct the positive fixture to the v5 heading and add adversarial
   tests.
6. Compute, compare, and persist the post-call runtime-map fingerprint on optimizer success,
   optimizer failure, optimizer exception, and map-drift failure paths.
7. Rerun the no-optimizer suite and request a sixth independent review. Do not create an
   execution authorization before an exact approval.

# 17. Whether exact reviewed state may be committed

No. Question 29 fails.

The reviewed implementation is already present in committed history, but it must not be
designated as the approved execution state or combined with this review as an
authorization-ready checkpoint. The defects above require implementation and test changes,
followed by another independent review.

# 18. Whether Phase 3 may execute after authorization

No. Question 30 fails.

An external authorization file cannot repair callable authorization bypasses, test-seam
bypasses, package-object authentication, or permissive review parsing. Creating an
authorization for this state would falsely certify the safety boundary. The first real
Phase-3 estimation must remain blocked.

# 19. Immediate next action

Remediate all items in section 16, extend the safety tests with the demonstrated adversarial
cases, run only the permitted no-optimizer validation, and submit the exact clean committed
state for a sixth independent read-only review. Do not create an execution-authorization file
and do not execute real Phase 3.
