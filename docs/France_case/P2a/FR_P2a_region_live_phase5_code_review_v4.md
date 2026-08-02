# 1. Phase-5 review-v4 verdict

**FINAL VERDICT: REJECT**

The closed-form rule fails. The declared inventory says one application-level
full-score surface, but static source inspection establishes a second
import-callable application route: `_phase5_contract_impl()` exposes the
production per-household likelihood closures and every input needed by
`phase5_inference.build_score_matrix()` without the canonical entry or an
authorization context. That is an application helper plus a generic derivative
primitive constructing the accepted Phase-5 score, not an excluded generic
primitive standing alone. Under deputy decision v2 section 3, a second surface
is automatic rejection.

Independent binding failures also remain in the T-12 capability, STOPPED rename,
post-evaluation reload, retained-member inventory, behavioral coverage, and
lifecycle profiles. These findings are all inside the frozen threat model.

# 2. Scope and exact state

This is the final independent closed-form review of JMP-M05B. I read deputy
decision v2; design v4 and the binding methods review, recheck, and micro-recheck;
the implementation charter and mission ledger; reviews v1-v3; remediation
reports v1-v2; the implementation, test-42, and architectural-closure reports;
the complete tracked diff and untracked Phase-5 working set; the source, YAML,
tests, surface inventory, parameter map, and source inventory; the accepted
Phase-3/4 bundles and verifiers; and the restricted-store provisioning evidence
through a redacted read-only inspection.

The MNL base is `983a2ecf1d16592b9f90085f6a6b690b8a964110`. The nested
HEAD and MNL gitlink are both
`27756a06ea189339aa82915ed2124628afed20eb`, and the nested worktree is
clean. After adding only this mandated review, the working set has exactly the
manager-specified two modified files and expected untracked sources, reviews,
five reports, surface inventory, and review v4. No unrelated status entry is
present. `git diff --check` passes.

No Phase-5 output root, `complete/`, attempt, restricted score member, or full
score was created. The restricted `staging/` and `published/` directories were
empty before and after review validation.

# 3. Frozen threat model

The review applies only the deputy-v2 boundary: unsupported, documented, or
import-callable application bypasses; caller-supplied configuration or custody;
stale authorization; mutation; Git leakage; and transaction inconsistency. It
does not demand resistance to arbitrary malicious code execution, source
rewriting, monkeypatching, or interpreter introspection by an actor already
controlling the process.

The decisive `_phase5_contract_impl()` route is an ordinary module-level
application helper that returns the production scoring ingredients by normal
call semantics. Finding it requires neither source modification nor
monkeypatching, so rejecting it does not expand the frozen threat model.

# 4. Statistical-design preservation

Preservation gates 1 and 3 pass. The implementation retains the accepted
47/37/35 parameter partition, ten pins, two active upper bounds, accepted theta,
positive-household-score sign convention, canonical `idhh` order, symmetrised
Phase-4 bread, unweighted household meat, conditional covariance, correction
`1555/1520`, regional restrictions, T/W constants, and mixed
absolute/relative parameter-map comparator. No statistical design artifact or
accepted input changed, and no optimizer or Hessian evaluation was run.

# 5. Package-boundary preservation

Preservation gate 2 passes. The nested package is clean at the accepted gitlink.
The application continues to use the package loader and
`build_jax_singles_ll(..., per_group=True)`; no package source, duplicate loader,
or duplicate likelihood implementation was added.

# 6. Closed-form surface inventory

`phase5_full_score_surface_inventory_v1.json` parses, and its self-digest
recomputes to
`734606947854ed1bfd3ee807df5000e3128cc93d2fa1b33fcfaedee7412cf330`.
Its declared count is one and its shallow call-site list matches the single
literal application call to `build_score_matrix()` at runner line 625.

The inventory is not truthful as a closed-form surface inventory. Its static
test scans only literal `build_score_matrix(` call sites
(`test_p2a_regionlive_phase5_inference.py:3115-3126`) and never audits helpers
that export the complete scoring ingredients. It therefore misses the direct
`_phase5_contract_impl()` route. The actual application-level count is at least
two, so review gates 5 and 6 fail and the closed-form decision is rejection.

The inventory is also stale: its authorization prerequisites still name a
Phase-5 review-v3 approval, although v3 is rejected and the executable target is
v4.

# 7. Single gated process entry

The canonical `main()` path is gated, but it is not the sole full-score surface.
The second route is structurally complete:

- `_phase5_contract_impl()` is module-level and callable directly
  (`run_p2a_phase5_inference.py:842-844`).
- Authorization is checked only conditionally when `_authorization` is not
  `None` (`1016-1018`).
- With no authorization it still constructs both production
  `per_group=True` likelihoods (`1019-1023`), the authenticated embedding and
  accepted free vector (`1029-1046`), and the two free-coordinate closures
  (`1048-1052`).
- It unconditionally returns `free_hat`, `per_group_free_fns`, `group_counts`,
  `row_order`, `jax`, and `jnp` (`1102-1115`). Those values can be passed
  directly to the generic `phase5_inference.build_score_matrix()` without
  `main()`, review/revision gates, canonical custody, or an authorization
  context.

The public wrapper strips these values only after the implementation helper has
returned (`825-830`). Testing only `_phase5_contract()` therefore does not make
the underlying import route structurally incapable.

The nominal canonical parent route is also not executable as written.
`_open_scoring_session()` returns a `_NestedScoreProvider` that defines
`forward()` and `reverse_subset()` but no `__call__` (`614-638`), while
`_phase5_evaluate()` refuses every provider for which `callable(provider)` is
false (`1143-1148`) before it calls `provider.forward()` at line 1177. The
synthetic orchestration tests replace `_phase5_evaluate()` itself and therefore
mask this production mismatch. Gate 7 passes narrowly for the exact former
`_phase5_contract()` plus `_phase5_evaluate()` pair; gates 8-10 fail because the
implementation helper is a distinct bypass, caller custody/configuration is not
closed across that bypass, the two canonical roles are not both executable, and
the behavioral tests miss these facts.

# 8. Authorization capability and canonical config

The canonical parent path correctly reads and digests the canonical YAML inside
`main()`, reasserts value identity before opening its scoring session, and
creates `_ScoringAuthorization` only after its contract and canonical gates.
The parser correctly targets this review's exact path and first heading,
rejects reviews v1-v3, rejects `APPROVE AFTER FIXES`, and accepts only one exact
approval line in the first section. That establishes the parent half of gate
11, the supported-constructor condition in gate 12, and ruling R-29.

Gate 11 nevertheless fails across the two authorized roles. The child creates
its authorization context at lines 2531-2545 before
`_open_scoring_session()` reruns the accepted-bundle, map, gradient, bound, and
pin contract gates at line 2546. Gate 13 holds for the nominal `main()` path,
but not as an architecture-wide configuration guarantee: the second
`_phase5_contract_impl()` surface does not bind or consume the canonical
Phase-5 YAML at all, consumes caller-supplied `cfg34`, and exports full-score
ingredients. That is also the direct gate-8 failure.

Capability/store binding fails gates 14 and 15. The restricted-store verifier
does not return a `store_identity`, so the parent context and child capability
bind `None`. `_consume_t12_capability()` accepts an environment-selected path
based only on file existence and basename (`2368-2385`), without proving that it
lies in the authenticated parent attempt. Its comparison set (`2399-2411`)
omits `attempt_id`, `parent_pid`, `store_identity`, and
`authorization_binding`. A caller can therefore create a same-named capability
record and reach the child role after the repository gates without a live
parent attempt; atomic rename makes that file single-use, but does not prove
parent issuance or bind it to the exact attempt and store.

Accordingly, gate 12 passes narrowly; gates 11 and 13-15 fail.

The source and inventory correctly disclaim arbitrary same-process adversarial
security, so gate 16 passes.

# 9. Parent and T-12 child roles

Gate 9 fails. Parent and child nominally enter through `main()` and both call
`_open_scoring_session()`, but only the child can use the returned provider: it
calls `provider.forward()` directly (`2546-2550`). The parent first passes that
same non-callable object to `_phase5_evaluate()` and is deterministically
refused by the `callable()` check (`1994-2002,1143-1148`). The test fixture
replaces both the scoring session and evaluator
(`test_p2a_regionlive_phase5_inference.py:2194-2212`), so it does not exercise
this production path.

The shared names also do not cure the second helper surface or the forgeable
child capability. The child consumes the capability before it reruns the
review/revision and store gates (`2500-2521`), and never authenticates the
omitted attempt/store fields afterward.

# 10. STOPPED rename safety

Gates 17-19 fail. `RestrictedPublication.stop()` checks the prospective STOPPED
destination name and its parent, but immediately before `os.rename` it does not
revalidate the staging source or reject a source reparse point
(`phase5_inference.py:2797-2812`). After the rename it assigns the endpoint to
`self.stopped` without validating the resulting endpoint or its resolved
containment (`2813-2818`). A post-open junction replacement is therefore the
same unresolved path described by review v3.

The purported endpoint test is a source-token test
(`test_p2a_regionlive_phase5_inference.py:2673-2683`); it does not replace the
opened attempt directory with a junction, invoke `stop()`, and prove refusal.

# 11. Post-evaluation reauthentication

The parent invokes T-13 after its own final evaluation, and the T-12 child now
invokes `_t12_child_reauthenticate()` after its score evaluation. Gates 20 and
21 therefore pass as ordering facts.

Gates 22 and 23 fail. Parent reauthentication still builds semantic map checks
from cached `ctx["man4"]`, `ctx["bounds_full"]`, and pin objects
(`run_p2a_phase5_inference.py:1793-1801,1835-1838`). Child reauthentication
reruns bundle verifiers and raw hashes, but does not reload and semantically
reauthenticate theta, the full gradient, the parameter map, bounds, and pins
(`2587-2624`). The suite contains no behavioral T-12-window mutation test and no
real evaluation-to-publication mutation test; the existing mutation test alters
copies and invokes isolated verifiers.

# 12. Retained-member and custody truthfulness

Gates 24-27 fail. `RestrictedPublication.inventory()` initially records a
directory as `name/`, then excludes every such member from `names`,
`observed_members`, `undeclared_members`, bookkeeping checks, and
`restricted_bytes_created` (`phase5_inference.py:2726-2754`). Junctions or
symlinks to directories follow the same path. Thus retained directories and
junctions can be visible only as an inert marker while the authoritative
inventory still reports success.

Failure finalization independently sets top-level
`restricted_bytes_created` from cached `bool(pub.member_hashes)` rather than the
real directory inventory (`run_p2a_phase5_inference.py:2183-2189`). For a
STOPPED attempt, `_finalize()` folds only cached `restricted_hashes` into the
bundle hash, skips closed-membership checking, yet declares the canonical
restricted member set (`1609-1647`). Top-level custody, nested evidence, actual
retained members, and the STOPPED bundle hash can therefore disagree after a
partial or unbooked write.

# 13. Behavioral test coverage

The pre-review-v4 no-full-score Phase-5 suite passed: `103 passed in 21.83s`.
The applicable Phase-3/4 safety suite, with only the two production-attempt
writers deselected, passed: `55 passed, 2 deselected in 19.79s`. These runs
created no Phase-5 root or restricted member.

Green tests do not prove the closure claims. The surface scan misses exported
score ingredients; the STOPPED endpoint check is textual rather than
behavioral; no test proves parent issuance and complete binding of the child
capability; the partial-write test examines `pub.evidence()` but not top-level
finalization and STOPPED bundle identity; and no real post-evaluation mutation
window is exercised. The synthetic orchestration test also replaces
`_phase5_evaluate()`, so it misses the production provider's failed
`callable()` contract. Applicable original gates 5-6, 8, 11-12, 24-25, 27, 32,
41, and 43-45 therefore fail notwithstanding the pre-v4 green count.

# 14. Lifecycle-aware test coverage

Gates 28 and 29 fail. `PHASE5_REVIEW_DOCS` contains only v1-v3
(`test_p2a_regionlive_phase5_inference.py:2956-2960`). The exact
reviewed-uncommitted profile and live equality assertion (`2974-3018`) therefore
treat this mandated review-v4 file as unexpected. In the final review-bearing
state the complete Phase-5 suite fails deterministically: **1 failed, 102 passed
in 21.86s**, at
`test_ac_lifecycle_reviewed_uncommitted_state_is_exact`, solely because review
v4 is an unexpected untracked file under the hard-coded profile.

The committed and one-attempt simulations do not prove the complete suite in
those states. They hard-code a tracked set that omits review v4
(`3028-3030`), while the always-collected live-state test continues to require
the uncommitted profile after commit. The post-dry-run simulation also replaces
`.gitignore` with a whole-Phase-5-root ignore rule (`3052-3059`) that the actual
`.gitignore` does not contain. It therefore hides ordinary attempt members that
would be untracked in the real one-attempt state.

# 15. Documentation consistency

Gate 31 passes: the implemented comparator and emitted authentication language
state the exact mixed absolute/relative rule
`a == b or abs(a-b) <= 1e-15 * max(abs(a), abs(b), 1.0)`.

Gate 30 fails. CLI help and executable constants correctly name v4, but the
surface inventory still names v3 as its approval prerequisite. Runner comments
at lines 92-114 and several test comments still describe v3 as the final
authorizer. The architectural-closure report claims all obsolete review
references were corrected and that its STOPPED, retained-member, behavioral,
and lifecycle groups are closed; the source and tests above contradict those
claims.

# 16. Accepted-artifact integrity

Gates 33-36 pass:

| Object | Recomputed SHA-256 / state |
| --- | --- |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` |
| parameter-map CSV | `ed48958d4f4994f80de6dc7f3acc1c1d8490cf31f0701b8d6ac9e01cf4e9a219` |
| nested package | clean at accepted HEAD/gitlink |
| restricted provisioning record | canonical self-digest matches configured `d3da8fef...`; store contract passes read-only verification |
| Phase-5 outputs | no root, attempt, `complete/`, or score artifact |
| whitespace | `git diff --check` passes |

Reviews v1-v3 rehash to the immutable digests recorded in the closure report.
The retention warning remains exactly the deputy-accepted operational warning
for review plus one dry run and is not reopened.

# 17. Residual defects

The decisive and independent residuals are:

1. `_phase5_contract_impl()` is a second import-callable application-level
   full-score route. This alone triggers automatic rejection.
2. The canonical parent cannot score because its provider fails the evaluator's
   `callable()` precondition; the integration fixture replaces the evaluator.
3. The surface inventory and its test miss the second route and retain a stale v3
   approval prerequisite.
4. The T-12 capability is not authenticated as parent-issued or bound on
   consumption to the exact attempt, parent, authorization, and store identity.
5. STOPPED rename neither revalidates its source immediately before rename nor
   validates the resulting endpoint afterward.
6. Parent/child post-evaluation checks do not perform the claimed complete
   semantic reload, and the mutation window is not tested behaviorally.
7. Directories/junctions are excluded from authoritative retained-member
   classification; top-level custody and STOPPED bundle identity can contradict
   actual partial members.
8. The mandatory review-v4 final state and the actual committed/one-attempt
   states are not valid complete-suite lifecycle profiles.
9. Documentation claims closure that the source and tests do not implement.

The applicable original 51-gate framework is therefore not green (review gate
32 fails), even though statistical preservation, package preservation, artifact
rehashing, nested cleanliness, no-output review discipline, and whitespace
checks pass.

# 18. Whether exact state may be committed

No. Gate 37 fails. The working-set inventory is exact, but exact inventory is
not architectural correctness. The second full-score surface and the remaining
authorization, transaction, custody, and lifecycle defects make this state
non-commit-ready under the binding binary rule. Test-42 remains a logically
separate prospective commit as already ruled; this review does not reopen it.

# 19. Whether one full dry run may follow after commit

No. This negative review is deliberately non-authorizing, and the parser must
refuse it. No Phase-5 commit or full dry run may follow under JMP-M05B. The
retention warning's deputy acceptance does not override failed architecture.

# 20. Immediate next action

Return this review and its rejection basis to the Goal 1 Manager. Under deputy
decision v2 sections 8-9, pause JMP-M05B and return the execution architecture
to the deputy programme director; no further remediation cycle, commit, or
Phase-5 run is authorized under this mission.
