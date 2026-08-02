# 1. Phase-5 review-v3 verdict

**FINAL VERDICT: REJECT**

The exact state is not safe to commit or authorize for a full dry run. Fifteen
of the 51 review gates fail. The statistical design and package boundary remain
preserved, but material authorization, post-evaluation authentication,
STOPPED-custody, transaction-endpoint, and lifecycle-test defects remain.

# 2. Scope and exact state

This is the independent final exact-state review commissioned under M05B-AC-9.
I reviewed the Phase-5 design v4 and all binding methods reviews, the JMP-M05B
charter, deputy E2 decision v1, implementation report v1, reviews v1 and v2,
remediation reports v1 and v2, the complete tracked diff and all untracked
Phase-5 sources, configuration and tests, `.gitignore`, the authenticated
parameter-map CSV, source inventory, accepted Phase-3 and Phase-4 manifests and
bundle verifiers, and the provisioned restricted-store evidence through its
redacted local read-only view. Remediation report v2 was treated as a set of
claims to test, not as evidence.

The reviewed MNL base HEAD is
`983a2ecf1d16592b9f90085f6a6b690b8a964110`. The nested package HEAD and MNL
gitlink are both `27756a06ea189339aa82915ed2124628afed20eb`; the nested
worktree is clean. The final MNL working set contains exactly the two expected
modified files, the four Phase-5 source/config/test files, reviews v1 and v2,
the five expected report documents, and this review v3. No status entry under
an `attempts/` path exists. The Phase-5 output root does not exist.

The following table gives an explicit result for every gate. A dagger marks the
sixteen gates that failed review v2 and therefore required explicit recheck.

| Gate | Result | Exact-state basis |
|---:|:---:|---|
| 1 | PASS | No accepted statistical formula, estimand, threshold, dimension, or constant changed. |
| 2 | PASS | The production loader and `build_jax_singles_ll(..., per_group=True)` are reused; no likelihood/loader duplicate exists. |
| 3 | PASS | The nested package is clean at the accepted gitlink. |
| 4 | PASS | Accepted theta, bounds, pins, maps, bread, covariance formulas, and scientific constants remain unchanged. |
| 5 | **FAIL** | `_phase5_contract` plus `_phase5_evaluate` is an import-callable full 1,555-by-37 score route with no authorization or custody gate. |
| 6† | **FAIL** | Direct contract/evaluate calls bypass review path/hash/verdict, revisions, cleanliness, custody, T-20, and T-23. |
| 7 | **FAIL** | Direct `_run` accepts a caller-supplied `cfg5` object whose restricted root is not proved equal to the canonical YAML object recorded in the manifest. |
| 8† | **FAIL** | The implementation and tests guard `_run`, but not the direct scoring callable or in-memory configuration routes. |
| 9 | PASS | Filesystem discovery and `git worktree list --porcelain` dynamically union actual and linked worktrees. |
| 10 | PASS | MNL, the nested package, `Job_Market_paper`, and linked worktrees discovered from the configured search roots are rejected as restricted destinations. |
| 11† | **FAIL** | `RestrictedPublication.stop()` does not recheck the staging source immediately before rename or validate the renamed STOPPED endpoint afterward. |
| 12† | **FAIL** | A post-open junction can survive as a STOPPED endpoint, and caller-supplied `cfg5` is not invariably bound to the canonical provisioned root. |
| 13 | PASS | T-20, T-13, T-23, and T-12 attach before the sole final gate summary. |
| 14 | PASS | The synthetic all-pass orchestration produces one preserved `PHASE_5_DRY_RUN_COMPLETE` attempt. |
| 15 | PASS | Gate and exception failures map to STOPPED status; custody truthfulness separately fails gates 27 and 32. |
| 16 | PASS | Production `complete/` publication remains impossible in canonical orchestration. |
| 17 | PASS | The map byte hash, exact schema, 47 rows, names, statuses, indices, values, pins, bounds, and gradients are authenticated. |
| 18† | PASS | The score embedding, H-II, interior score selection, and reporting labels use the authenticated 47→37→35 map, with the Phase-4 projection only as a bitwise witness. |
| 19 | PASS | Name, order, status, index, and value tampering fails closed. |
| 20 | PASS | The full gradient is loaded from the reverified accepted Phase-3 bundle member. |
| 21 | PASS | Pin falsification selects the ten actual pin coordinates by authenticated name. |
| 22 | PASS | The full-gradient map consumes all 47 source values and assigns no pin zero by construction. |
| 23 | **FAIL** | Parent T-13 runs before the T-12 child performs the last full-score evaluation; the child never reruns either bundle verifier after its evaluation. |
| 24† | **FAIL** | The T-12 child has no post-evaluation theta/map/gradient/config/input recheck; parent T-13 also reuses cached Phase-4 map, bounds, and pin semantic objects. |
| 25† | **FAIL** | Tests mutate copies and call isolated verifiers, but never exercise real T-13 after an evaluation and prove STOPPED before publication. |
| 26 | PASS | T-12 hashes an in-memory `.npy` serialization and creates no duplicate score file or output-path argument. |
| 27† | **FAIL** | STOPPED inventory excludes directories/junctions from observed and undeclared member sets; STOPPED finalization also declares the canonical set while hashing only cached members. |
| 28 | PASS | The inspected store is persistent, access-restricted, local, outside discovered Git roots, and authenticated through the redacted provisioning record. |
| 29† | PASS | Attempt directories are unique and member files use exclusive creation, refusing duplicate or pre-existing members. |
| 30 | PASS | Successful publication is one same-volume directory rename. |
| 31 | PASS | An existing published attempt destination is refused. |
| 32† | **FAIL** | A post-write/pre-bookkeeping fault yields top-level `restricted_bytes_created=false` while nested disk inventory says true; partial hashes are omitted from the STOPPED bundle hash. |
| 33 | PASS | Unconditional custody fields exist in the manifest skeleton before contract and evaluation. |
| 34† | PASS | Recursive redaction and negative assertions remove raw restricted locators from commit-eligible diagnostics and manifests. |
| 35 | PASS | The optimizer guard proactively imports and patches optimizer entry points. |
| 36 | PASS | Lazy imports are covered, and the canonical T-12 child installs an independent guard. |
| 37 | PASS | T-20 cannot report success unless a guard is actively installed and no guarded call occurred. |
| 38 | PASS | Effective per-builder chunk widths/counts and comparison-route values are recorded. |
| 39 | PASS | Post-contract and post-evaluation runtime and JAX x64 snapshots are recorded. |
| 40 | PASS | Canonical orchestration places runtime, chunk, guard, and gate-register evidence in the manifest. |
| 41† | **FAIL** | Deterministic integration coverage is missing for real T-13 mutation timing, STOPPED junction replacement, and final manifest truthfulness. |
| 42 | PASS | The known tautological assertions were replaced with falsifiable calculations and refusal checks. |
| 43† | **FAIL** | The working-set test is lifecycle-invalid: it omits review v3, expects the pre-commit dirty state, rejects a legitimate attempt, and uses subset rather than equality. |
| 44† | **FAIL** | The complete suite is not valid with this v3 file, after commit, or after the authorized dry run. |
| 45 | **FAIL** | The suite passed twice before v3, but fails in the mandatory final review-bearing state. |
| 46 | PASS | This review created no household score bytes, full-score computation, Phase-5 root, or dry-run attempt. |
| 47 | PASS | Review v1 is explicitly rejected by canonical path and cannot authorize execution. |
| 48† | PASS | The executable parser exactly targets v3 and refuses v1, v2, conditional approval, rejection, wrong heading, duplicate verdict, wrong digest, or dirty/revision-mismatched state. |
| 49† | PASS | After adding only this mandated v3 file, the actual working set is exactly the manager-specified inventory. |
| 50 | PASS | `git diff --check` passes. |
| 51 | PASS | Accepted Phase-3/4 bundles and the nested state rehash and compare unchanged. |

# 3. Statistical-design preservation

Gates 1 and 4 pass. The implementation retains the accepted 47 total, 37 free,
35 interior, ten pinned, and two active-bound coordinates; the accepted theta;
the name-keyed conditional estimand; the symmetrised accepted Phase-4 bread;
the household score and unweighted meat; the model and robust covariance
formulas; `1555/1520`; the regional restrictions; and every T/W scientific
threshold. No optimizer or Hessian evaluation was run during this review.

Manager-closed items A-1 through A-4 are not reopened. The retention warning is
also treated exactly as ruled: it remains an operational limitation propagated
to the manifest and is sufficient for review plus one dry run, but it does not
cure the code defects found here.

R-23b-rev is correct as a policy. The implemented comparison is the mixed rule
`a == b or abs(a-b) <= 1e-15 * max(abs(a), abs(b), 1.0)`: relative at and above
unit magnitude, with an absolute `1e-15` floor below it. The constant did not
change. One emitted authentication note still calls it a “relative bar”; that
wording violates the ruling that all descriptions state the mixed policy
exactly, although it does not alter the authenticated numerical result.

# 4. Package-boundary preservation

Gates 2 and 3 pass. No file in `dclaborsupply-monorepo` changed. Phase 5 reuses
the accepted Phase-3/4 contract, package loader, and production per-group JAX
likelihood hook. The application code introduces no alternative loader,
likelihood, objective, or package-local patch.

# 5. Fix 1 — authorization

This fix fails gates 5 through 8.

The CLI is narrow and fail-closed: its public modes are `contract` and `dryrun`,
there is no reproduction output argument, and `_run` rederives authorization at
entry and before its own scoring call. The T-12 CLI child also rechecks the v3
review, revisions, cleanliness, accepted bundles, map, and store contract.

Those protections do not cover all Python-callable scoring paths. Calling
`_phase5_contract(cfg5, cfg34, log)` and then `_phase5_evaluate(ctx, cfg5, log,
progress)` directly constructs and returns the full score arrays without
`_reauthorize`, restricted-store binding, or an installed/verified optimizer
guard. Review v2 already established that an underscore is not a security
boundary. The remediation test asserting “no route” examines only `_run`.

There is also a caller-selected custody route. `_run` consumes its `cfg5`
argument directly, while the manifest and T-13 hash the canonical YAML file,
not proof that the in-memory object equals that file. The store verifier binds a
provisioning-record digest but does not bind the record's store identity to the
selected root. A Python caller can therefore supply another eligible root with
a copied valid record. This violates the no-arbitrary-output and exact-custody
requirements even when `_run`'s repository authorization passes.

The v3 executable parser itself is correct. It requires this exact path, the
exact first heading, exactly one first-section approval verdict, the supplied
file digest, both exact HEADs/gitlink, and clean MNL/nested worktrees. It rejects
reviews v1 and v2 and rejects conditional or negative verdicts. This review's
negative verdict is therefore intentionally non-authorizing. The CLI help text
nevertheless still names review v2 and the obsolete heading; it is misleading
but fail-closed.

# 6. Fix 2 — Git ancestry

Gates 9 and 10 pass; gates 11 and 12 fail.

The helper dynamically discovers ordinary, nested, sibling, and linked
worktrees. It normalizes case, resolves real paths, rejects relative and `..`
paths, checks `.git` directory/file ancestry, and rejects symlink/junction
redirection at the provisioned root and normal success endpoints. The actual
MNL, nested, and `Job_Market_paper` worktrees are in the discovered set.

The STOPPED endpoint remains open. `RestrictedPublication.stop()` checks the
prospective destination and its parent, but it does not recheck
`self.staging`/the rename source immediately before `os.rename`, and it does not
validate the renamed STOPPED endpoint afterward. Replacing an opened attempt
directory with a junction can therefore leave a renamed STOPPED junction whose
target lies outside the authenticated root. The endpoint test checks source
tokens rather than reproducing this transaction-child replacement. The
caller-supplied `cfg5` issue in section 5 independently prevents invariant
binding to the canonical provisioned root.

# 7. Fix 3 — orchestration

Gates 13 through 16 pass. T-20, parent T-13, T-23, and T-12 are attached before
the one gate-register summary. A synthetic all-pass attempt reaches exactly one
`PHASE_5_DRY_RUN_COMPLETE` destination; a synthetic gate failure reaches one
STOPPED destination. The canonical transaction refuses production
`PHASE_5_COMPLETE` and never publishes `complete/`.

These orchestration results do not cure the later T-12 reauthentication gap or
the inaccurate STOPPED custody record described below.

# 8. Fix 4 — parameter-map binding

Gates 17 through 19 pass, including prior-failed gate 18. The CSV is hashed
before parsing, has an exact 20-column schema and 47 rows, and is cross-checked
against the certified specification order, Phase-4 parameter map, accepted
theta, full gradient, pins, and bounds. The score embedding is derived by name
from the authenticated CSV; the reused Phase-4 embedding is only a required
bitwise witness. H-II, the interior score matrix, and table block labels all
require the bound authenticated map.

Byte, name, order, status, index, and value tampering fails. The remaining
“relative bar” description is a documentation/manifest-language defect under
R-23b-rev, not an unauthenticated projection.

# 9. Fix 5 — full-gradient authentication

Gates 20 through 22 pass. The 47-element `gradient_final` is loaded from the
accepted Phase-3 `optimizer_diagnostics.json` member using the digest produced
by the closed-set bundle verifier. Shape and finiteness are enforced. Pin
components are selected at the actual name-keyed coordinates and must equal
zero. `full_gradient_map` maps all 47 supplied components and does not create
zeros for pins.

# 10. Fix 6 — post-evaluation reauthentication

Gates 23 through 25 fail.

For the parent's first score evaluation, T-13 reruns both closed-set bundle
verifiers, compares raw pre/post hashes for the closed consumed-input list,
reloads theta and gradient, and reruns map authentication. That is a material
improvement over review v2.

It is not the final post-evaluation check. The actual sequence is parent score,
parent T-13, restricted staging, then the T-12 child starts a fresh process and
performs another complete 1,555-household score evaluation, followed by
publication. The child verifies inputs before scoring but never reruns T-13 or
either closed-set bundle verifier afterward. A mutation during the child window
is therefore outside the required post-evaluation check. Equality of the score
digest is not a substitute: mutations to inputs that do not change those bytes
can still pass.

Parent T-13 also rebuilds part of its semantic check from cached `man4`, bounds,
and pin objects rather than from wholly reloaded sources. Raw hashes catch a
persistent mutation in the parent window, but this does not satisfy the stated
full-reload contract or the child timing gap.

The test gap is the same one review v2 identified. The synthetic orchestrator
monkeypatches T-13 to success; one test searches source text; another mutates a
copied bread/gradient source and calls isolated verifiers; and the new digest
test checks only pre-digest enumeration. No deterministic test mutates a
consumed class during evaluation, invokes real T-13, and proves STOPPED before
ordinary or restricted publication.

# 11. Fix 7 — T-12 member closure

Gate 26 passes and gate 27 fails. The T-12 child accepts no score-output path,
serializes `.npy` bytes in memory, and emits only a digest, so it leaves no
second registered or unregistered score file.

Successful restricted publication enforces the declared member set. Failure
inventory is not exact: directories and junctions are added internally as
names ending in `/` and then excluded from `observed_members`,
`undeclared_members`, and `restricted_bytes_created`. An undeclared retained
directory can therefore be invisible and even leave `inventory.ok=true`.
Moreover, STOPPED finalization skips restricted membership checking, folds only
cached successful member hashes into the bundle digest, yet declares the full
canonical restricted set in `bundle_membership`.

# 12. Fix 8/9 — custody and transaction

Gates 28 through 31, 33, and 34 pass; gate 32 fails.

The redacted live inspection confirms the provisioned store is persistent,
locally access-restricted, outside the discovered Git roots and temporary/cloud
locations, and currently has empty staging and publication children. The
record's canonical self-digest and configured digest agree. No restricted
locator or ACL-sensitive identity is reproduced here.

Normal-path staging is unique, member writes use exclusive creation, successful
publication is an atomic same-volume directory rename, an existing destination
is refused, and commit-eligible records recursively remove raw locator keys.
Custody fields are initialized before contract and evaluation.

Failure truthfulness remains defective. If bytes reach disk and a fault occurs
before `member_hashes` bookkeeping, `pub.evidence()` correctly finds those
bytes, but `_preserve_restricted_on_failure()` sets the manifest's top-level
`restricted_bytes_created` from `bool(pub.member_hashes)`. The same manifest can
therefore say `false` at the authoritative top level and `true` in nested
observed inventory. Actual partial hashes are also absent from the STOPPED
bundle hash while the manifest declares the canonical member set. Combined with
the STOPPED-junction and directory-inventory defects, failed partial writes do
not preserve one truthful, closed, authoritative transaction record.

# 13. Fix 10 — optimizer guard

Gates 35 through 37 pass for canonical orchestration. The guard proactively
loads and patches optimizer entry points before the contract, checks around
lazy imports and score callables, and is independently installed in the T-12
child. `record()` raises unless the guard is currently active. The direct
scoring callable bypass in section 5 remains outside that guarded
orchestration, which is why authorization gates fail even though the T-20
implementation itself passes.

# 14. Fix 11 — runtime metadata

Gates 38 through 40 pass. The runner records effective builder chunk widths,
group and chunk counts, the comparison route, a pre-contract environment, a
post-contract environment after x64 activation, and a post-evaluation snapshot.
Canonical finalization places these fields, guard checks, and the final gate
register in the manifest.

# 15. Fix 12 — tests and lifecycle

Gates 41, 43, 44, and 45 fail; gates 42 and 46 pass.

Before this review file existed, the no-full-score Phase-5 suite passed twice:
`96 passed in 19.00s` and `96 passed in 18.27s`. Those runs left the exact Git
status unchanged, created no Phase-5 root or attempt, and created no restricted
score member. In the mandatory final review-bearing state, the suite fails the
working-set test because that test omits review v3 from its allowed inventory:
`1 failed, 95 passed in 18.72s`, with that test as the sole failure.

The test named `test_c2_fix10_working_set_is_exactly_the_manager_inventory` is
not exact: it uses `set(untracked) <= expected_untracked`, so missing required
files pass. It hard-codes the current two modified files, so it fails after
commit when the worktree becomes clean. It rejects any untracked `attempts/`
entry, while the authorized dry run intentionally preserves one attempt and its
ordinary manifest/diagnostic files are not all ignored. The separate
three-state test exercises a temporary transaction invariant; it does not run
or prove the complete suite in committed and post-dry-run Git states.

Coverage also misses real T-13 mutation-before-publication and the exact
STOPPED-junction/partial-write outcomes described above. The remaining
tautological finite-sample and real-mode assertions were genuinely replaced,
so gate 42 passes.

TEST-42 remains a logically separate change. Its diff is confined to
`test_p2a_regionlive_phase3_safety.py`, touches no Phase-5 code, inventories all
eight accepted Phase-4 members, moves the one generated attempt into a
test-owned temporary root before inspecting it, deletes that isolated copy in a
`finally` block, and compares accepted-bundle bytes before and after. I did not
run TEST-42 or any Phase-4 dry run in this review.

# 16. Accepted-artifact integrity

Gate 51 passes. Independent closed-set verification reproduced:

| Object | SHA-256 |
|---|---|
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` |
| accepted `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` |
| parameter-map CSV | `ed48958d4f4994f80de6dc7f3acc1c1d8490cf31f0701b8d6ac9e01cf4e9a219` |
| review v1 | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` |
| review v2 | `48eae5ebbfd5fbeeb8527a4e75cb82f925dbe272342b84dd6a8e951241a3465d` |

The accepted bundle member sets are exact, the nested worktree is clean at its
gitlink, and no accepted source or artifact changed during review.

# 17. Residual defects

1. A direct Python contract/evaluate route computes the full score without the
   exact authorization and custody gates.
2. `_run` trusts a caller-supplied in-memory configuration for restricted
   custody while recording/rechecking the canonical file instead.
3. STOPPED rename does not revalidate its source and resulting endpoint against
   junction/reparse escape.
4. The last full-score process, T-12, has no post-evaluation reauthentication.
5. STOPPED inventory omits directories/junctions and finalization can contradict
   actual partial bytes and omit them from the bundle hash.
6. Mutation tests do not exercise real T-13 and publication ordering.
7. The working-set test is invalid with review v3, after commit, and after the
   one preserved dry-run attempt; it is also a subset test, not equality.
8. CLI help still names review v2/the obsolete heading, and one authentication
   record still describes the approved mixed comparator as a relative bar.

# 18. Required fixes

1. Put an unforgeable authorization/custody token at the actual score-building
   callable boundary, or make full scoring reachable only inside one gated
   process entry; bind every consumed configuration object to the canonical
   file digest and the provisioned store identity.
2. Recheck the STOPPED rename source immediately before rename, reject reparse
   points along its chain, and validate the resulting STOPPED endpoint after
   rename.
3. Run complete post-evaluation bundle/input/theta/map/gradient
   reauthentication after every full score evaluation, including the T-12 child,
   before publication; rebuild semantic checks from reloaded sources.
4. Inventory every retained filesystem member, including directories,
   junctions, unreadable members, and partial files; make the top-level custody
   state, observed inventory, declared membership, and STOPPED bundle hash agree.
5. Add behavioral integration tests for direct-route refusal, in-memory config
   refusal, T-12-window mutation, STOPPED junction replacement, partial-write
   truthfulness, and no-publication outcomes.
6. Replace the working-set guard with lifecycle-aware exact assertions that pass
   with review v3, after clean commits, and after one preserved dry-run attempt;
   run the complete no-full-score suite in each simulated state.
7. Correct the stale v2 CLI help and every residual comparator description to
   the exact mixed absolute/relative R-23b-rev policy.

# 19. Whether exact state may be committed

No. The exact state fails 15 binding gates, including authorization, Git-path
escape, post-evaluation authentication, custody truthfulness, and lifecycle
validity. Test-42 may remain a logically separate prospective commit, but its
presence does not authorize the Phase-5 state.

# 20. Whether one full dry run may follow after commit

No. This review is deliberately non-executable. The v3 parser correctly refuses
its negative verdict, and a full dry run must not be attempted or enabled from
this state.

# 21. Immediate next action

Return this review and the 15-gate failure count to the Goal 1 Manager. Do not
commit the Phase-5 working set and do not run Phase 5. The manager should route
the findings under the governing remediation-budget/E2 process before any
further code change, commit, or execution authorization.
