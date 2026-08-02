# 1. Phase-5 review-v2 verdict

**FINAL VERDICT: APPROVE AFTER FIXES**

The remediated implementation preserves the accepted statistical design and
package boundary, and most of the twelve requested fixes are present. It is not
yet an executable or commit-ready exact state. Ten required corrections remain:
authorization can be forged at the internal scoring entry point; the required
review-v2 heading cannot be authenticated; transaction subdirectories can be
redirected through reparse points; the authenticated parameter map is not used
at every projection; T-13 does not reauthenticate every consumed input; stopped
restricted members are not inventoried truthfully; raw custody locator data is
not fully redacted; the numerical-tolerance ruling is misstated; one post-run
lifecycle test is invalid; and the working set contains an unexpected Phase-3
attempt. No full dry run is authorized by this verdict.

# 2. Scope and exact state

This is an independent review of the uncommitted JMP-M05B remediation at MNL
HEAD `983a2ecf1d16592b9f90085f6a6b690b8a964110`. I read the Phase-5 design v4
and binding methods reviews, charter, deputy E2 decision, implementation report
v1, code review v1, remediation report v1, complete current diff, runner,
helper, configuration, tests, `.gitignore`, authenticated parameter map, source
inventory, accepted Phase-3 and Phase-4 manifests and verifiers, and the local
provisioning evidence through a redacted read-only view.

The nested `dclaborsupply` revision is
`27756a06ea189339aa82915ed2124628afed20eb`, equal to the MNL gitlink and
clean. The separately discovered `Job_Market_paper` worktree was also included
in the ancestry review. No restricted-store locator expansion or ACL principal
is reproduced here.

The expected modified files were `.gitignore` and
`tests/p2a/test_p2a_regionlive_phase3_safety.py`. The expected untracked files
were the Phase-5 helper, runner, YAML, Phase-5 test module, and four named report
documents. Excluding this mandated review document, the observed set additionally
contains an untracked completed Phase-3 attempt under
`outputs/.../phase3_estimation_v1/attempts/20260801T155028Z_..._PHASE_3_DRY_RUN_COMPLETE/`,
with a console log and manifest. It existed before review execution and was not
created by this review, but it contradicts the addendum's expected exact state
and R-24. Gate 49 therefore fails.

The Phase-5 test module passed twice in the project virtual environment with
bytecode and pytest cache generation disabled: `81 passed` in 15.17 seconds and
`81 passed` in 15.07 seconds. After this review file was created, the same suite
passed in the review-bearing state: `81 passed` in 15.52 seconds. A separate
remediation-focused run passed twice with `28 passed, 53 deselected`. These are
no-full-score tests. The restricted store remained empty and no Phase-5 output
root, score member, or dry-run attempt was created. Review gate results are:

| Gates | Result |
|---|---|
| 1-5 | pass |
| 6 | fail |
| 7 | pass |
| 8 | fail |
| 9-10 | pass |
| 11-12 | fail |
| 13-17 | pass |
| 18 | fail |
| 19-23 | pass |
| 24-25 | fail |
| 26 | pass |
| 27 | fail |
| 28 | pass for the provisioned store as inspected |
| 29 | fail: attempt directories are unique, but member writes can overwrite |
| 30-31 | pass |
| 32 | fail |
| 33 | pass |
| 34 | fail |
| 35-40 | pass |
| 41 | fail |
| 42 | pass |
| 43-44 | fail |
| 45-46 | pass |
| 47 | pass |
| 48-49 | fail |
| 50-51 | pass |

# 3. Statistical-design preservation

Gates 1 and 4 pass. The accepted theta, bounds, pins, parameter identities,
covariance construction, finite-sample corrections, tolerances that are true
design constants, warning thresholds, and inference formulas were not changed.
The Phase-5 implementation continues to use the accepted 47/37/35 dimensions,
the accepted Hessian bread, household-cluster meat, and the design-v4 Wald and
diagnostic definitions.

R-23a is upheld. The revised expectation `0.0644` in
`test_p2a_regionlive_phase5_inference.py:505-521` is computed from
`(1555 / 1554 - 1) * 100 = 0.06435006435006052` and rounded to four decimal
places; the fixture independently checks the correction factor `1555 / 1554`.
No scientific constant moved.

R-23b is not upheld as worded. The observed authentication results are sound:
maximum deviations were approximately `2.22e-16` for estimates, `3.06e-17` for
the full gradient, `8.88e-16` for the free gradient, and zero for pins and
bounds; all ten pin-gradient coordinates are exactly `0.0`. However,
`_values_agree` uses `1e-15 * max(abs(a), abs(b), 1.0)`, which is a mixed
absolute/relative rule with an absolute `1e-15` floor below unity. It is not a
uniform `1e-15` relative, approximately 4.5-ULP rule. The fixed CSV byte hash
currently prevents this inaccurate description from creating a practical CSV
tamper path, but the ruling and manifest terminology must describe the policy
actually implemented, or the comparator must be changed to the policy that is
approved.

# 4. Package-boundary preservation

Gates 2 and 3 pass. No likelihood or loader was duplicated: the Phase-5 runner
reuses the accepted Phase-4 contract and calls the package likelihood route
through `build_jax_singles_ll(..., per_group=True)`. The nested package is clean
at its accepted gitlink revision. No `dclaborsupply` source, test, or metadata
was modified.

# 5. Fix 1 — authorization

Gate 5 passes: the public CLI exposes only `contract` and `dryrun`; it has no
full-score reproduction route, arbitrary output argument, or real-run switch.
The T-12 child route accepts no caller-selected score destination and rechecks
the bundle, parameter-map, store, review, revision, and cleanliness controls.
Gate 7 therefore also passes.

Gates 6 and 8 fail. `_run()` at
`scripts/p2a/run_p2a_phase5_inference.py:1366-1378` trusts only the two caller-
supplied booleans `verified` and `execution_ready` in `gates_record`; a Python
caller can construct those values and reach `_phase5_evaluate` without rerunning
the exact authorization verifier. The integration tests themselves invoke this
bypass with a synthetic record. An underscore-prefixed function is not a
security boundary. The scoring entry point must rederive all binding gates from
the actual files and repositories, or accept a complete, cryptographically
bound, non-forgeable authorization result.

There is a second fail-closed defect under gate 48. The mandated heading in this
review is `# 1. Phase-5 review-v2 verdict`, while
`PHASE5_REVIEW_HEADING` at runner line 100 requires
`# 1. Phase-5 review verdict`. The parser and tests accept the obsolete heading
and reject the required one. Consequently this prompt-compliant review cannot
authorize the current runner, regardless of its verdict.

# 6. Fix 2 — Git ancestry

Gates 9 and 10 pass. The helper dynamically discovers repositories and linked
worktrees, including MNL, the nested repository, `Job_Market_paper`, and any
additional discovered worktree. Direct containment is rejected, as are root-
level relative, `..`, case-fold, symlink, junction, `.git` directory, and `.git`
file escapes.

Gates 11 and 12 fail at the transaction endpoints. The provisioned root is
resolved and checked, but its `staging/` and `published/` children are checked
only with `is_dir()` and `stat()` at helper lines 2319-2339. A safe temporary
probe replaced those children with NTFS junctions to an outside directory; the
store contract still returned success. A post-provisioning reparse replacement
can therefore redirect staging or publication away from the bound root. The
root, fixed children, attempt path, stopped destination, and publish destination
must each be opened or resolved fail-closed, checked for reparse points, and
proved contained beneath the authenticated root immediately before use and
rename.

# 7. Fix 3 — orchestration

Gates 13-16 pass for orchestration control flow. T-20, T-13, T-23, and T-12 are
attached before the sole final gate summary. The synthetic all-pass integration
path produces exactly one `PHASE_5_DRY_RUN_COMPLETE` attempt; a failing gate
produces one STOPPED attempt; and Phase-5 production success plus any
`complete/` publication is refused.

The STOPPED status selection is truthful, but the restricted partial-member
evidence written with that status is not always truthful. That distinct defect
is recorded under gates 27 and 32 below.

# 8. Fix 4 — parameter-map binding

Gates 17 and 19 pass. Before parsing, the implementation enforces the fixed CSV
SHA-256, the exact 20-column schema and 47-row shape, then authenticates identity
columns, names, order, status, indices, pins, bounds, accepted estimates, and
gradient values. Byte-level name, order, status, or value tampering fails the
fixed hash. Pin gradients are checked at their actual coordinates and exactly
equal zero.

Gate 18 fails. The accepted `free_hat` is projected inside the reused Phase-4
contract before the CSV is authenticated, and score embedding at runner lines
629-637 uses `pmap34["free_idx"]` rather than the authenticated Phase-5 map.
Bread and meat later use the authenticated map, but design v4 requires every
47-to-37-to-35 projection to key on the authenticated CSV with a name-equality
check. The current source-token test enumerates selected downstream sites but
does not exercise the score embedding projection. All projections must use the
authenticated map directly, with an integration test proving that an unbound or
disagreeing map cannot reach score construction.

# 9. Fix 5 — full-gradient authentication

Gates 20-22 pass. The full 47-element `gradient_final` is loaded from the
reverified Phase-3 `optimizer_diagnostics.json` member, with its digest derived
from the accepted bundle. Shape and finiteness are checked. Pin falsification
locates the ten real pin coordinates by authenticated name and requires their
accepted components to be exactly zero. `full_gradient_map` maps every source
component; it does not assign pin zeros by construction.

# 10. Fix 6 — post-evaluation reauthentication

Gate 23 passes narrowly: T-13 reloads both accepted bundle directories and reruns
the Phase-3 and Phase-4 closed-set verifiers after evaluation.

Gates 24 and 25 fail. For several consumed inputs with no frozen digest,
`_t13_reauthenticate` searches the Phase-4 artifact hash map by basename and,
when no entry exists, sets the result to success. This leaves the Phase-4
manifest, Phase-3 and Phase-4 configurations, Phase-5 configuration, runner, and
helper without a pre/post content comparison. Runtime-map fingerprints bind
resolved paths, not file contents. Theta is hashed from cached
`ctx["theta_hat"]` instead of being rederived from reloaded accepted sources;
the CSV is reloaded only for digest/name comparison rather than rerunning the
complete cross-source parameter-map authentication.

A safe copied-bundle mutation confirmed the gap: changing parameter-map content
inside the copied Phase-4 manifest did not change the accepted bundle digest,
because that manifest is outside the bundle-hash member set. Existing r26 is a
source-string assertion and r27 tests isolated loaders; neither mutates a
consumed input during evaluation and then exercises T-13 before publication.
The runner must capture raw pre-evaluation digests for every consumed file,
compare them after evaluation, rederive theta and the accepted gradient, and
rerun full parameter-map authentication. Deterministic integration tests must
mutate each input class during the evaluation callback and prove STOPPED before
any restricted or ordinary publication.

# 11. Fix 7 — T-12 member closure

Gate 26 passes. T-12 serializes the score array in memory and reproduces the hash
without creating a duplicate registered or unregistered score file. Successful
publication enforces the exact declared restricted member set.

Gate 27 fails on failure paths. `stop()` preserves the directory, but
`evidence()` reports only the cached `member_hashes`; it never inventories,
validates, and hashes the actual stopped directory. Extra files or bytes written
before a bookkeeping failure can therefore remain outside the reported set.
Failure finalization must scan the real directory without deleting it, reject or
flag every undeclared member, hash every retained declared member, and report the
exact observed set.

# 12. Fix 8/9 — custody and transaction

Gate 28 passes for the store as inspected. The redacted provisioning record and
live checks show a persistent, access-restricted local store outside all three
discovered Git roots, outside temporary/cloud/UNC locations, with protected
access control, fixed child directories on the same volume, and no current
reparse points. Staging and published directories were empty. This finding does
not disclose the expanded locator or any ACL identity.

R-23c is upheld. With `record_sha256` omitted, canonical JSON recomputation
matched the record's self-declared digest, and that digest then matched the
configured digest. The raw file digest is intentionally a different quantity.
This is the required two-stage self-consistency and configuration-binding check.

Gate 29 fails in part. Attempt staging directories are unique and created with
`exist_ok=False`, but `RestrictedPublication.write_bytes()` opens members with
`"wb"`; a second write to the same declared name silently overwrites the first.
Member creation must be exclusive and a duplicate name must fail. Gate 30 passes
for the current same-volume, one-directory `os.rename` publication mechanism,
subject to closing the reparse-point escape in section 6. Gate 31 passes because
an existing published attempt destination is refused.

Gate 32 fails. A fault after bytes are written but before the hash is inserted
into `member_hashes` leaves a real partial file while STOPPED evidence reports
`restricted_bytes_created=false` and no digest. A controlled fsync-failure probe
reproduced exactly that contradiction. Failure evidence must be derived from an
inventory and hash of actual retained files, including uncertain or partial
writes, rather than only from successful in-memory bookkeeping.

Gate 33 passes. The custody skeleton and unconditional disclosure/retention
fields exist before store binding and before evaluation. Gate 34 fails because
the commit-record redaction function adds a locator hash and removes the resolved
path, but leaves the raw `custody_locator` field in the structure merged into
diagnostics and the manifest. Remove every raw locator representation from
commit-eligible records and assert its absence, while retaining only approved
redacted evidence.

# 13. Fix 10 — optimizer guard

Gates 35-37 pass. The guard is installed proactively, imports and patches the
prohibited optimizer entry points, checks before and after callable routes,
covers lazy imports, and is independently installed in the T-12 child process.
T-20 cannot record success unless the guard is active and no prohibited call was
observed.

# 14. Fix 11 — runtime metadata

Gates 38-40 pass. The runner records effective chunk bounds and sizes, group and
chunk counts, and comparison size. It records the JAX/x64 and runtime state after
the contract and again after evaluation. The attempt manifest receives the
authoritative gate register, runtime snapshots, chunking evidence, custody
evidence, member hashes, and bundle identity.

# 15. Fix 12 — tests and lifecycle

Gate 42 passes: the former tautological finite-sample assertion was replaced by
the computed fixture described under R-23a, and no executable unconditional
assertion was found. The review-v1 lifecycle assumptions about an absent review,
a permanently fixed live HEAD, and an always-empty Phase-5 root were replaced.

Gates 41, 43, and 44 nevertheless fail. Deterministic coverage is missing for
the unbound score projection, actual T-13 orchestration-time mutations,
transaction-child junction replacement, duplicate member writes, failure after
bytes precede hash bookkeeping, stopped-member closure, and full locator
redaction. The required review-v2 heading is also encoded incorrectly. Finally,
the inherited transaction leaves an empty `.staging` directory after a dry run,
whereas post-run `test_22` allows `staging` without the dot. The suite therefore
cannot remain valid after the authorized dry run even though it is green before
that run. Replace that expectation with the real lifecycle contract or remove
the empty internal directory during finalization, then exercise the test on a
synthetic completed attempt.

Gate 45 passes: the no-full-score suite passed repeatedly, including once after
this review file was present. Gate 46 passes for
this review: the test commands created no household score bytes and no Phase-5
attempt. The unexpected Phase-3 attempt described in section 2 predates this
review and is a gate-49 exact-state defect, not evidence that this reviewer ran a
Phase-5 dry run.

TEST-42 is logically separate. The change to
`test_p2a_regionlive_phase3_safety.py` inventories all eight accepted Phase-4
members, identifies the one attempt produced by the Phase-4 invocation, moves it
immediately into isolated temporary custody, and verifies accepted-bundle
identity before and after cleanup. It touches no Phase-5 implementation. The
accepted Phase-4 bundle remained byte-identical. This change and its housekeeping
report should be committed separately from JMP-M05B after the unexplained
Phase-3 attempt in the current worktree is reconciled.

# 16. Accepted-artifact integrity

Gate 51 passes. Independent closed-set verification reproduced:

- Phase-3 bundle SHA-256
  `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`;
- Phase-4 bundle SHA-256
  `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`;
- accepted `hessian_free.npy` SHA-256
  `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061`;
- parameter-map CSV SHA-256
  `ed48958d4f4994f80de6dc7f3acc1c1d8490cf31f0701b8d6ac9e01cf4e9a219`.

All eight accepted Phase-4 member hashes match the TEST-42 housekeeping report.
The Phase-3 and Phase-4 manifests, accepted theta and Hessian sources, and nested
gitlink state were not changed by review activity.

# 17. Residual defects

The residual defects are implementation and certification defects, not a change
to the accepted statistical design:

1. `_run()` accepts a forgeable two-boolean authorization record.
2. The authorization parser requires the wrong review section heading.
3. Restricted transaction children and attempt destinations are not protected
   against post-provisioning reparse-point replacement.
4. The authenticated CSV map is bypassed at the accepted-theta and score
   projection sites.
5. T-13 lacks immutable pre/post anchors and full reload/re-authentication for
   every consumed input.
6. Restricted member writes are overwritable, and stopped contents are neither
   exactly inventoried nor truthfully hashed after partial-write faults.
7. Commit-eligible custody records retain a raw locator field.
8. R-23b describes a relative/ULP tolerance that the comparator does not
   implement.
9. The post-dry-run suite expects `staging` while the transaction leaves
   `.staging`.
10. The worktree contains an unexpected completed Phase-3 attempt despite R-24.

There is no institutional backup for the restricted store. The deputy decision
allows the present local provision for review and one dry run, so this is a
recorded operational limitation rather than an additional code-review blocker.

# 18. Required fixes

Exactly ten correction groups are required before a new exact-state approval:

1. Reverify all authorization inputs inside the full-scoring entry point, or
   replace the forgeable record with a complete cryptographically bound result.
2. Bind the parser, constants, help text, and tests to the exact mandated
   review-v2 heading and exact review/revision/cleanliness lifecycle.
3. Resolve and reject reparse points and containment escapes for the restricted
   root, fixed children, staging attempt, stopped destination, and publication
   destination at each security-sensitive operation.
4. Use the authenticated CSV-bound map directly at every 47-to-37-to-35
   projection and test the score-construction route, not source strings.
5. Freeze raw digests for all consumed inputs; after evaluation reload and
   rehash them, rederive theta and gradient, and rerun the complete parameter-map
   authentication, with real mutation-before-publication integration tests.
6. Use exclusive member creation; on every failure inventory and hash actual
   retained files, enforce/record the exact stopped-member set, and report
   partial bytes truthfully.
7. Remove every raw custody locator from commit-eligible structures and add a
   negative assertion for each published record.
8. Correct R-23b and manifest language to the implemented mixed
   absolute/relative policy, or implement and approve the stated comparator.
9. Correct the `.staging` post-run lifecycle contract and prove the complete
   suite remains valid before commit, after commit, and after a synthetic dry
   run.
10. Reconcile the unexpected Phase-3 attempt and restore the manager's exact
    working-set inventory without altering accepted bundles.

# 19. Whether exact state may be committed

No. Gates 6, 8, 11, 12, 18, 24, 25, 27, 29, 32, 34, 41, 43, 44, 48, and 49
fail. Gate 50 passes (`git diff --check` returned no error), but that does not
override the authorization, transaction, test-lifecycle, and exact-inventory
defects. TEST-42 must remain logically separate and be committed independently
from JMP-M05B when its own exact state is clean.

# 20. Whether one full dry run may follow after commit

No. This exact state must neither be committed nor used for a full dry run. The
current runner rejects this document's required heading, and this conditional
verdict is not execution authorization. A dry run may follow only after all ten
correction groups are implemented, no-full-score tests pass in the uncommitted
and committed states, the worktree and accepted artifacts are reverified, and a
new independent exact-state review gives an executable approval bound to the
actual revisions and review digest.

# 21. Immediate next action

Return the implementation to remediation. Preserve this review as evidence;
make no Phase-5 commit and run no full score. Reconcile the pre-existing Phase-3
attempt under Goal-1 management, keep TEST-42 in its own commit scope, implement
the ten correction groups, rerun only no-full-score validation, and submit the
resulting exact state for a new independent review before any one-run dry-run
authorization.
