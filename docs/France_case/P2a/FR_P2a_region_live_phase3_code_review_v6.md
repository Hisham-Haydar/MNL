# 1. Sixth-review verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

The simplified implementation satisfies the new research-reproducibility scope on the
public CLI boundary, Git identity, package identity, input provenance, parameter mapping,
pins, numerical gates, successful-result immutability, and non-optimizing dry-run behavior.
The superseded adversarial-Python findings from reviews v1-v5 were not used as rejection
criteria.

One in-scope output-transaction defect remains. `Phase3Transaction.attempt_id` uses
`time.time_ns() % 1_000_000`, which is not unique on this Windows host. Repeated attempt IDs
can collide with an existing attempt destination. The orchestration may downgrade an initial
review/dry-run publication collision to `STOPPED`, while an existing same-ID `STOPPED`
destination can leave the new evidence in `.staging` and strand the lock. This directly
violates execution-scope section 9's requirements for unique attempt staging and preserved
non-success attempts.

The fix is small and does not affect the econometric implementation. Phase 3 must remain
unexecuted until the attempt identifier is made collision-resistant, a deterministic
regression test is added, the complete no-optimizer suite passes reliably, and this review
is updated to an exact approval.

# 2. Governing execution scope

The controlling standard is
`FR_P2a_region_live_phase3_execution_scope_v1.md`, SHA-256
`fa3e6a0a1273aa417af6f2d8c401f15d4d86389cdbdbed83bf11d9dd1ebe7d18`.
It supersedes the earlier adversarial-Python execution-security requirements while retaining
the numerical, provenance, Git, package-origin, and transaction requirements.

This review therefore did not treat any of the following as defects:

- intentional bypass of the public CLI;
- forged internal dictionaries or malicious direct private-helper calls;
- `functools.partial`, `__wrapped__`, or pre-mutated `sys.modules` attacks;
- removal of the external authorization JSON and test-double marker system; or
- Markdown-injection hardening beyond the specified review-file check.

The attempt-ID collision is not one of those excluded cases. It is an accidental filesystem
collision in the ordinary transaction implementation and falls directly within the in-scope
requirements for unique attempts and complete evidence preservation.

# 3. Files reviewed

The following were read in full:

- `FR_P2a_region_live_phase3_execution_scope_v1.md`;
- `FR_P2a_region_live_phase3_simplification_report_v1.md`;
- `FR_P2a_region_live_phase12_manager_acceptance_v1.md`;
- `FR_P2a_region_live_dry_run_report_v2.md`;
- the Phase-3 implementation report v1;
- remediation reports v1-v4;
- code reviews v1-v5;
- `scripts/p2a/run_p2a_regionlive_rebuild.py`;
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; and
- `tests/p2a/test_p2a_regionlive_phase3_safety.py`.

The ten safety-critical package modules were also reviewed: the top-level package,
`models`, `data` and its loader, `spec` and its parser, and `likelihood` with its index,
JAX engine, and `_numpy_primitives`.

The complete current source was read and the complete Git change was inspected. Reviewed
state before this report:

- MNL HEAD: `40a2c84e70d60cb97944feb081e8e7beb93d5bcc`;
- nested HEAD: `27756a06ea189339aa82915ed2124628afed20eb`;
- MNL gitlink: `27756a06ea189339aa82915ed2124628afed20eb`;
- nested worktree: clean;
- tracked changes: runner, config, and safety tests;
- untracked governing documents: execution scope and simplification report; and
- untracked validation dry-run attempts under the canonical Phase-3 `attempts/` history.

The tracked diff contains 566 insertions and 1,318 deletions across the three implementation
files. No historical review or remediation report was modified.

# 4. Public execution boundary

Questions 1-3 pass.

The runner module documentation and CLI help identify the public CLI as the production
boundary. `main()` dispatches Phase 3 only through `run_phase3()`. The CLI exposes the exact
scope-document controls:

- `--execute-phase3`;
- `--expected-mnl-head`;
- `--expected-dclaborsupply-head`;
- `--approved-review`; and
- `--approved-review-sha256`.

Without `--execute-phase3`, `run_phase3()` forces `args.dry_run = True` and enters the
contract-only path. With it, the Git/review gates run before the real branch is enabled.
The private `_phase3_run()` also refuses a non-dry call without a verified gate record, but
private-call hardening is not relied upon as the production boundary.

The canonical config is enforced by resolved path in both `main()` and `run_phase3()`.
The resolved `--out`, configured output root, and exact `phase3_estimation_v1` subdirectory
must all match their canonical constants. Test 10 rejects an alternate output root and an
identical copied config.

# 5. Git revision and cleanliness gates

Questions 4-6 pass.

For a real run, `_verify_execution_gates()` requires lowercase 40-hex values for both
expected commits and compares them with the current MNL and nested HEADs. It reads the
`dclaborsupply-monorepo` gitlink from the MNL HEAD and requires it to equal the nested HEAD.

Both repositories are checked with:

```text
git status --porcelain --untracked-files=all
```

This covers tracked, staged, and untracked drift. Tests cover incorrect MNL and nested
revisions, dirt in both repositories, live gitlink equality, and a committed gitlink
mismatch. A dedicated staged-only case is absent, but the operative Git command necessarily
reports staged changes.

The current MNL tree is intentionally dirty and cannot pass a real-run gate yet. The nested
tree is clean and its HEAD equals the recorded gitlink.

# 6. Review approval gate

Questions 7-10 pass under the governing scope.

The approved path is fixed to
`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md`. The CLI argument must
equal that exact relative path. A 64-hex SHA-256 is mandatory and is compared with the
actual v6 review bytes.

The parser accepts the prescribed ordinary review form: the exact first heading
`# 1. Sixth-review verdict`, followed in its first section by exactly one approval-verdict
line. It refuses the two non-approval verdicts, a wrong first heading, prose-only approval,
and multiple verdict markers. Tests also reject the v5 review path and malformed review
hashes.

The parser normalizes surrounding whitespace and is not a general Markdown parser. Fenced
or otherwise adversarial Markdown constructions were deliberately not treated as blockers
because execution-scope section 4 excludes Markdown injection beyond this review-file
validation. The actual v6 report uses an unindented ordinary Markdown verdict line.

# 7. Package source identity

Questions 11-14 pass.

The immutable inventory contains all ten scope-required package modules and adds any other
loaded `dclaborsupply.*` source modules. For every module it requires:

- resolved ancestry beneath
  `dclaborsupply-monorepo/packages/dclaborsupply/src`;
- a tracked blob at the selected nested commit; and
- equality between the tracked blob id and
  `git hash-object --path <relative-path> <working-file>`.

The real route passes the expected nested commit from the verified CLI gates. The verifier
also requires nested cleanliness, nested HEAD equality with the expected commit, and live
gitlink equality.

Live validation returned `package_identity_ok: true` for all ten modules, with no failures;
every path was beneath the reviewed source root and every Git-canonical working blob id
equaled its tracked blob id. No optimizer module was loaded by this check.

The governing scope and simplification report correctly document Windows `autocrlf`: raw
working SHA-256 may differ from the LF blob while Git-canonical content remains identical.
Raw hashes are still recorded for audit. The runner's detailed verifier comment says this
correctly, although its earlier inventory comment still uses the imprecise phrase
“byte-identical blob”; that comment should be cleaned up but does not alter the implemented
gate.

# 8. Input provenance

Questions 15-16 pass for all Phase-3-consumed Phase 1-2 evidence.

The immutable runtime map has exactly ten labels covering geometry and metadata, the frozen
stem and metadata, certified spec, certified warm start, stored region-live start theta,
Phase 1-2 manifest, accepted dry-run report, and pre-estimation reload evidence.

`_authenticate_inputs()` requires exact label-set equality, exact equality between each
configured path and the independently constructed runtime path, file existence, and
SHA-256 equality. The contract additionally verifies the accepted Phase 1-2 manifest status
and its original runner/config anchors.

Live authentication passed all ten labels. The runtime-map fingerprint was:

`f9a5ba9f4d7db55c6b9913376974855f79e65ac0b9e696debb8958b7b4a5d0de`.

The same map object is threaded through consumption and the post-optimizer recheck. On a
normal optimizer return, its fingerprint is compared before any result artifact is written,
and every input is rehashed against both pre-run and accepted hashes. Optimizer exceptions
also perform the input recheck. Tests cover input mutation and prove the map factory is not
re-entered.

Original raw/pricing artifacts are not reopened by Phase 3; their hashes and reconstruction
lineage are carried by the accepted Phase 1-2 evidence. They are not Phase-3-consumed files.

# 9. Parameter and pin handling

Questions 17-19 pass.

`build_phase3_parameter_map()` requires:

- 47 unique names;
- the exact ordered ten-name pin tuple;
- 37 ordered free names;
- disjoint pin/free sets whose union is the full vector; and
- pin values indexed by the actual 47-name specification order.

Projection and expansion enforce shapes `(47,)` and `(37,)`. Expansion inserts immutable pin
values on every objective call and final reconstruction. The contract verifies both
directions of the round trip and bitwise equality of all ten pins.

The actual specification has pin indices
`[10, 11, 12, 13, 14, 15, 16, 17, 31, 32]`. The expected free-bound pair is derived from the
accepted theta and bounds, then cross-checked against the immutable names
`beta_l_age2_sm` and `beta_l_age2_sf`. Removing those two from the 37 free names yields
exactly 35 parameters for the gradient gate.

# 10. Numerical gates

Questions 20-22 pass.

G-16 applies epsilon `1e-9` to every run-level free parameter and stops on any violation.
Tests cover exactly `lo-epsilon` and `hi+epsilon` as passing and the next representable
values outside both boundaries as failing.

The optimizer contract requires exactly:

```text
method: L-BFGS-B
maxiter: 5000
maxcor: 30
ftol: 1e-15
gtol: 1e-10
```

The estimator calls the package-built JAX objective with `jac=True`, the ordered 37-vector,
37 free bounds, and those exact options. Fake-minimizer integration checks vector length,
bounds, objective sign, gradient sign, and pin preservation without invoking the real
optimizer.

The target gate uses the two-sided absolute deviation from
`19053.46553160094` with tolerance `1e-4`. Both materially higher and lower objectives
produce `REVIEW_REQUIRED_TARGET_MISMATCH`, never successful publication. Optimizer failure,
exception, unexpected bounds, gradient failure, pin structure, and G-16 each stop separately.

# 11. Output transaction safety

Questions 23-24 pass; question 25 fails.

The successful path validates the exact pre-manifest artifact set, writes the console status,
hashes the four artifacts without self-hashing the manifest, writes the manifest last, checks
the final five-file set, and publishes by same-root directory `os.replace()` into
`complete/`. This is directory-level atomic publication.

A prior or newly appeared `complete/` is checked before optimization, before finalization,
and again in `Phase3Transaction.finish()`. A prior successful result therefore cannot be
overwritten.

Normal dry-run, stopped, and review-required statuses are moved under `attempts/`. That
guarantee is undermined by the attempt identifier:

```python
time.time_ns() % 1_000_000
```

On this Windows host, a 10,000-construction probe produced only 123 distinct IDs, with 9,877
duplicates and maximum multiplicity 230. In a forced same-ID `STOPPED` collision at the
transaction layer:

- the first attempt remained preserved;
- the second directory-level move raised `PermissionError` because its destination already
  existed;
- the second evidence remained in `.staging`; and
- the lock remained present until explicit cleanup by the probe.

In the full orchestration, a review-required or dry-run destination collision first reaches
the outer exception handler, which retries publication as `STOPPED`. That may preserve the
evidence under a different status when the corresponding STOPPED destination is free, but it
still corrupts attempt identity/status. A STOPPED collision, or a retry whose STOPPED
destination already exists, has the stranded-staging/lock failure demonstrated above.

An independent run of tests 1-22 failed at
`test_14_success_bundle_immutable` for the same collision. Repeating that isolated test in
fresh processes produced 11 passes and 1 failure. This is an accidental transaction failure,
not an adversarial private-helper scenario.

# 12. Test adequacy

Question 26 passes for the requested accidental-drift and numerical failure modes, but the
suite is not yet stable enough for final approval.

One complete run produced:

```text
30 passed in 16.38s
```

An independent complete run also passed. All estimator-route tests monkeypatch
`scipy.optimize.minimize` with `FakeMin` before `_phase3_estimate()` is called, and the
subprocess dry-run omits `--execute-phase3`. No real optimizer or real estimation ran.

The suite covers parameter mapping, pins, bounds, G-16, gradients, two-sided target
mismatch, optimizer failure and exception, input mutation, canonical paths, package origin,
Git commits, cleanliness, gitlink mismatch, locks, bundle completeness, and dry-run state.

However, the transaction test is nondeterministic because of the production attempt-ID
defect, and it does not deterministically assert uniqueness under a fixed/coarse clock. The
suite cannot be considered reliably green until that defect and coverage gap are fixed.

Additional static validation passed:

- runner and test AST parsing;
- YAML parsing;
- `git diff --check`;
- cached diff check; and
- nested-repository diff check.

# 13. Phase 1–2 regression safety

Question 28 passes.

An external scratch-root Phase 1-2 dry-run returned exit code 0 with
`DRY_RUN_PHASES_1_2_COMPLETE`; Phase 1 and Phase 2 both passed. The regenerated frozen stem
was byte-identical to the accepted artifact:

`8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d`.

The Phase 1-2 implementation remains unchanged apart from shared removal of the superseded
SciPy-module-presence guard. Accepted Phase 1-2 evidence and the certified pooled baseline
were not modified.

# 14. Phase-3 dry-run safety

Question 27 passes.

The canonical subprocess invocation without `--execute-phase3` completed the contract-only
route. The latest reviewed attempt records:

- status `PHASE_3_DRY_RUN_COMPLETE`;
- `optimizer_called: false`;
- `execution_ready: false`;
- review gate `AWAITING_REVIEW_V6_APPROVE`;
- start negLL `19053.46553160094`;
- objective deviation `0.0`;
- no `complete/`; and
- no remaining production lock.

The full suite's subprocess test necessarily creates a preserved dry-run bundle under the
canonical `attempts/` directory. These bundles are currently untracked and must be handled
consistently with the audit-history and clean-tree policies before a real run.

# 15. Prohibited-operation audit

Question 29 passes.

The CLI refuses every phase above 3 before phase execution. Direct checks for Phases 4, 5,
6, 7, and 8 each returned exit code 2. No Phase 4-8 computation exists in the Phase-3 route.

During this review:

- real Phase 3 and the real optimizer were not invoked;
- EUROMOD, inference, post-estimation, welfare, synthetic recovery, and notebooks were not
  run;
- no implementation, config, package, baseline, theta, or accepted Phase 1-2 file was edited;
- no commit was made; and
- validation wrote only permitted dry-run evidence plus an external scratch regression
  directory.

# 16. Residual defects

1. **Blocking — attempt identifiers are not unique.** The clock-modulo suffix repeats
   heavily on Windows, making the test suite flaky and preventing guaranteed preservation of
   every failed/review/dry attempt under `attempts/`.
2. **Low — stale comments.** The package inventory comment says “byte-identical blob” even
   though the intentional policy is Git-canonical equality. The estimator docstring still
   mentions a removed `minimize_fn` injection, and the test-module preamble says tests never
   write a production output path even though the canonical dry-run test intentionally
   writes an attempt bundle.
3. **Operational — current tree is not execution-ready.** The implementation, scope,
   simplification report, this review, and validation attempts are not yet in one committed,
   fully clean state. This is expected before review completion and is correctly refused by
   the execution gates.

No econometric, objective, parameter-order, pin, gradient, bound, target, input-hash, package,
or successful-result overwrite defect was found.

# 17. Required fixes

1. Replace the modulo-clock attempt suffix with a collision-resistant identifier, preferably
   `uuid.uuid4().hex`, or atomically allocate and retry a unique staging/destination name
   while the exclusive lock is held.
2. Add a deterministic regression test that freezes or repeats the clock source, creates
   multiple same-label/same-status attempts, and proves:
   - distinct attempt IDs and destinations;
   - every attempt is preserved under `attempts/`;
   - `.staging` contains no stranded evidence; and
   - the lock is released after normal finalization.
3. Rerun the full no-optimizer suite repeatedly enough to demonstrate the former flaky
   transaction test is stable. Keep the public CLI dry-run and Phase 1-2 regression checks.
4. Correct the three stale comments identified in section 16 while touching the relevant
   files.

Do not alter any numerical threshold, parameter order, pin, objective route, input hash, or
transaction publication rule beyond making attempt allocation unique.

# 18. Whether exact reviewed state may be committed

No, not as the final execution-approved state.

Question 30 therefore fails for the exact current implementation. The scoped defect is
localized, but committing this state as the approved Phase-3 checkpoint would leave the
explicit unique-attempt requirement unsatisfied and preserve a nondeterministic safety suite.

A historical checkpoint could of course be committed if the manager wants it, but it must
not carry an approval verdict or be used for real estimation.

# 19. Whether Phase 3 may execute once

No, not from the exact state reviewed here.

After the section 17 fixes, a renewed independent check must update the canonical v6 review
to an exact approval. The fixed implementation, tests, scope, simplification report, review,
and intended dry-run evidence must then be committed in a fully clean MNL tree; the nested
tree must remain clean at the matching gitlink. Only then may the first real Phase-3
estimation execute once through the documented CLI using the post-commit MNL SHA, nested SHA,
and approved-review SHA-256.

# 20. Immediate next action

Make only the attempt-ID, deterministic transaction-test, and comment corrections listed in
section 17. Rerun the no-optimizer suite and the two dry-run regression checks, verify both
worktrees and the gitlink, and return the exact diff for a narrow final approval update.
Do not execute real Phase 3 meanwhile.
