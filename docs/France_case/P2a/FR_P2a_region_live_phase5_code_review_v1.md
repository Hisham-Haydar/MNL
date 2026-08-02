# 1. Phase-5 review verdict

**FINAL VERDICT: REJECT**

# 2. Scope and state reviewed

This was an independent read-only review of the uncommitted JMP-M05B Stage I-3 implementation. The implementation was assessed against the binding design v4, the JMP-M05B mission charter, deputy decisions D-1 through D-8, and the PI disclosure determination; claims in the implementation report were treated only as claims to verify.

The reviewed repository state was:

- MNL HEAD `983a2ecf1d16592b9f90085f6a6b690b8a964110`;
- nested dclaborsupply HEAD and MNL gitlink `27756a06ea189339aa82915ed2124628afed20eb`;
- a clean nested worktree;
- the stated Phase-5 working set only: the two new Python modules, the new YAML, the new Phase-5 tests and implementation report, and the `.gitignore` change;
- no modification to the accepted Phase-3/Phase-4 runner, its config, the package, theta, or either accepted bundle.

I read the implementation, configuration, tests, complete uncommitted state, accepted bundle contracts, and the safety-critical package loader/JAX route. I did not run a Phase-5 contract command, full dry run, reproduction mode, real run, optimizer, Hessian, EUROMOD, or notebook. The permitted isolated Phase-5 deterministic module was run with bytecode and pytest cache writes disabled: `53 passed in 10.43s`. MNL status, nested status, and accepted artifacts were unchanged afterward. `git diff --check` passed for MNL and the nested repository.

# 3. Design conformance

The central statistical construction is substantially correct:

- the score is the positive per-household log-likelihood Jacobian from `jax.jacfwd`;
- the identity uses `sum(S) = -gradient(negLL)` with the registered T-1/T-4 tolerances;
- the raw Phase-4 bread is hash-checked, symmetrised as `(H + H.T) / 2`, and reduced by name to the 35-coordinate interior block;
- the meat is `S_I.T @ S_I` on exactly 35 columns;
- `c = 1555/1520`, with CR0 recoverable as `V_robust / c`;
- T-7 uses the exact backward-error coefficient and the certified upward value `6.0424e-12`;
- the model and robust covariance algebra, E_R selector, H0-A/B/C/G restriction matrices, separate model/robust Wald results, active-upper-bound reporting, and literal `NA` rules agree with design v4.

Exact conformance nevertheless fails in several binding places:

1. `_phase5_evaluate()` summarizes the mandatory gate register before T-12, T-13, T-20, and T-23 exist. Those four gates are therefore reported missing and the evaluator returns `STOPPED`. `_run()` later adds the gates and recomputes the register but never clears the stale halt or restores `PHASE_5_DRY_RUN_COMPLETE`. An all-passing dry run cannot complete.
2. Production does not load and validate `phase5_parameter_map_v1.csv` as a binding map. It derives the scientific map from the specification/Phase-4 contract and reads the CSV only through an optional display-block helper that silently returns `{}` when the file is missing. This violates design sections 7 and 21, which require the implementation to key projections on both committed sources and assert name equality at every projection.
3. The pin-gradient falsification is tautological. The runner creates a 47-name zero dictionary and fills only the 37 free entries, so every pin necessarily appears as zero. It does not authenticate and test the published 47-coordinate `gradient_final`, despite that authoritative vector being present in the accepted Phase-3 diagnostics.
4. T-13 does not rehash either accepted bundle after evaluation. It copies the pre-evaluation Phase-3 and Phase-4 bundle hashes from the context and compares those cached strings with constants. The ordinary runtime-input recheck does not cover the accepted complete bundles. In-run mutation of Phase-3 artifacts or Phase-4 diagnostics/manifest would therefore pass this purported post-evaluation bundle check.

# 4. Likelihood reuse

The likelihood-reuse requirement passes. `_phase5_contract()` imports and invokes the committed Phase-3/4 contract, consumes its exact male and female loader objects, and calls the package `build_jax_singles_ll(..., per_group=True)`. The 37-vector is injected into the accepted 47-vector with the ten pins held fixed. No second loader implementation or copied likelihood mathematics appears in the Phase-5 modules.

The Phase-4 gradient and Hessian closures are discarded. Phase 5 loads the accepted Hessian artifact and does not expose an optimizer call in its current source. The nested package remains clean and unchanged.

The static no-optimizer conclusion passes, but the advertised T-20 runtime guard does not. In a fresh interpreter `scipy.optimize` is not resident when `NoOptimizerGuard.__enter__()` runs, so the guard patches nothing; a subsequent lazy import exposes the real `scipy.optimize.minimize`, while `record()` still reports `ok: true` and `guard_installed: false`. The prohibited-module check is likewise made only at the start of `_run()` and is absent from the public reproduction path.

# 5. Custody and disclosure

The PI-determination supremacy is correctly applied to the named primary artifacts:

- `phase5_scores_free.npy`, its row-level CSV rendering, and `phase5_score_row_index.csv` are classified as restricted;
- the `.gitignore` patterns cover all three globally;
- row and column fingerprints are computed;
- the three named restricted members are folded as sorted `name:sha256` entries into the same manifest-excluded hash-of-hashes as the non-disclosive members.

The custody implementation is not safe enough to approve:

1. Public `--mode reproduce --reproduce-out <path>` performs the complete 1,555-by-37 score construction without the Phase-5 review, expected-commit, cleanliness, package-identity, transaction-lock, or custody gates. It then writes the authoritative score array to the caller-selected location. This is an unauthorized full-score execution and disclosure bypass.
2. Path confinement enumerates only MNL and its nested repository. A destination inside the sibling `Job_Market_paper` Git worktree, or another Git worktree, passes the check. This does not implement “outside every Git tree.”
3. T-12 leaves a second full score array at `<restricted-attempt>/_t12/phase5_scores_free.npy`. That duplicate is outside `PHASE5_RESTRICTED_ARTIFACTS`, the custody record, and the closed bundle hash. Ruling A-2 is therefore not fully implemented in the actual retained store.
4. The configured Phase-5 custody leaf does not presently exist. Its nearest existing directory is an ordinary mutable Windows directory granting full control to user/admin principals. The writer creates directories with `exist_ok=True` and publishes files with `os.replace`; neither the code nor the environment establishes the required durable, access-controlled, immutable custody contract.
5. The three restricted members are written sequentially into their final external directory, not into an external staging directory followed by an atomic directory publication. A failure after one or two writes can leave orphaned household-level bytes without hashes or a locator in the STOPPED manifest.
6. The unconditional T-23 fields are absent from the manifest skeleton. Contract attempts and early failures can therefore omit `disclosure_class` and `retention_responsibility`, although design v4 requires them on every run.

The implementation records actual `.npy` on-disk size, which is correct. The design's `460,280` parenthetical is the raw float payload size and cannot be the literal byte size of a NumPy-format file with a header; I do not treat that accurate implementation behavior as a defect.

# 6. Transaction and authorization separation

The ordinary MNL-side transaction inherits the accepted lock/staging/UUID attempt mechanism. Normal dry-run and STOPPED finalization targets `attempts/`; successful attempts are distinct; `complete/` is absent; and `PHASE5_REAL_RUN_AUTHORIZED = False` plus the lack of a real/execute CLI mode prevents production publication. Flipping the constant fails closed.

The Phase-5 review parser itself is correct. It requires this exact first heading, exactly one ordinary verdict line in the first section, the canonical review-v1 path, its SHA-256, exact MNL/nested revisions, gitlink equality, and clean worktrees. The token `PHASE5_REVIEW_V1_APPROVED` is emitted by a successful verifier; it is not an additional textual token required in the review file. This rejection line therefore cannot authorize execution.

Authorization separation still fails because the verifier is called only for `mode == dryrun`. Public `contract` starts a Phase-5 attempt without review approval, and public `reproduce` evaluates and writes the full score without review approval. Design section 18.1 says execution must refuse before the review gate, not merely the final dry-run wrapper.

MNL-side failure preservation also does not cure the external-custody gaps: partially written restricted files and the T-12 duplicate are outside the transaction's staged exact-set checks. In addition, the stale gate status described in section 3 means the authorized dry run is guaranteed to publish a STOPPED attempt even if every final gate passes.

# 7. Tests

The isolated deterministic module passed all 53 collected tests and did not mutate accepted artifacts. The synthetic numerical tests cover most of the charter section 8 list well: mapping helpers, active-bound reporting, cluster order, score sign, a four-household production route, bread, PSD/covariance algebra, regional restrictions, literal `NA`, basic custody fields, basic transactions, and real-run refusal.

The green count is insufficient for acceptance because important integration and lifecycle cases are absent:

- no fake-score orchestration test reaches `_phase5_evaluate()` and proves that a complete all-gates-pass battery becomes `PHASE_5_DRY_RUN_COMPLETE`; hence the unconditional STOPPED defect is missed;
- no test detects post-evaluation mutation of copied Phase-3/Phase-4 bundles;
- no test covers partial restricted-store publication, the retained `_t12` duplicate, or the ungated public reproduction path;
- no fresh-process test proves that T-20 is installed before a lazy `scipy.optimize` import;
- the execution-gate tests do not exercise a successful verifier or the wrong-HEAD, wrong-gitlink, dirty-worktree, missing-review, and wrong-review-hash paths using isolated repositories;
- test 08 contains a tautological `... or True` assertion;
- test 16 contains a second tautological conditional whose false branch is never evaluated;
- test 14 asserts that the required review file is absent, so this mandated review makes the suite fail;
- test 14b asserts that live HEAD remains the pre-implementation documentation checkpoint, so the required implementation/review commit makes it fail;
- test 22 requires the Phase-5 root to remain empty, so the authorized preserved dry-run attempt makes it fail.

The last three are lifecycle-invalid tests, not harmless snapshots. The exact review/commit/dry-run sequence required by the charter cannot retain a green suite until they are corrected.

The committed Phase-4 `test_42_phase4_subprocess_dry_run_never_evaluates_hessian` is separately stale because it asserts that the accepted Phase-4 `complete/` bundle is absent. That defect predates Phase 5 and should be handled as separate housekeeping: replace the absence assertion with pre/post byte-identity checks and isolate any dry-run output. It is not charged as a Phase-5 implementation defect.

# 8. Goal-1 rulings A-1..A-4

1. **A-1 — substantively correct, metadata incomplete.** Canonical `chunk_size: 0` gives one chunk per male/female builder and T-11 compares it with 128. Chunking is used only as a memory knob. However, the manifest does not record the actual chunk size C as design section 18.5 requires.
2. **A-2 — not fully satisfied.** The hash algorithm correctly merges the three declared restricted `name:sha256` members with the non-disclosive members and excludes the manifest. The retained unregistered `_t12` score duplicate means the actual restricted artifact set is not closed.
3. **A-3 — correct.** `phase5_score_row_index.csv` is restricted, ignored, stored outside the declared MNL-side bundle, and represented by a row fingerprint in custody metadata. This correctly follows the PI determination over the superseded design-v4 “committed” row.
4. **A-4 — correct on the merits and in code.** For a covariance matrix, the least-supported direction is the eigenvector of the largest eigenvalue. The implementation selects that direction and treats W-2 as warning-only. The design's smallest-eigenvalue wording was information-matrix framing and should not override the covariance convention.

# 9. Residual defects

1. **Critical:** ungated public reproduction can compute and export the full restricted score matrix before review/commit authorization.
2. **Critical:** the restricted destination is not confined against every Git worktree and is not established as durable, access-controlled, and immutable.
3. **High:** an all-passing dry run is forced to STOPPED by premature gate-register evaluation.
4. **High:** the binding parameter-map CSV is not authenticated or used by production projections.
5. **High:** T-13 compares cached bundle hashes instead of rehashing both accepted bundles after evaluation.
6. **High:** external restricted artifacts are not transactionally published, and T-12 retains an unregistered duplicate score array.
7. **Medium:** the 47-coordinate pin-gradient falsification is manufactured from zeros instead of verified from the accepted full gradient.
8. **Medium:** unconditional custody fields and partial-write evidence are missing from early STOPPED/contract attempts.
9. **Medium:** T-20 can report success with no installed optimizer guard; prohibited-module checking does not cover every execution path.
10. **Medium:** manifest runtime metadata omits chunk size and captures JAX x64 state before the production contract enables x64, producing a stale environment record.
11. **Medium:** authorization, transaction, mutation, and all-pass orchestration integration coverage is incomplete.
12. **Low but mandatory for a reproducible handoff:** current Phase-5 tests contain lifecycle-invalid and tautological assertions, so the reviewed/committed/post-dry-run states cannot all remain green.

# 10. Required fixes

1. Remove public ungated score reproduction, or require the same verified Phase-5 review/revision/cleanliness gates internally for every full-score child process; public contract execution must also refuse until section 18.1 is satisfied.
2. Resolve restricted destinations by actual Git ancestry, including the sibling JMP repository and any other discovered worktree, rather than a two-root list.
3. Move the final gate-register decision after T-12, T-13, T-20, and T-23 are attached; prove all pass maps to one preserved `PHASE_5_DRY_RUN_COMPLETE` attempt and never to `complete/`.
4. Load, schema-check, hash/authenticate, and use `phase5_parameter_map_v1.csv` alongside the specification and Phase-4 contract, with exact name/order/status/value equality at every 47-to-37-to-35 projection.
5. Authenticate the accepted 47-element `gradient_final` and use its pin components for the section 12.5 falsification instead of assigning zeros by construction.
6. Re-run both closed-set Phase-3 and Phase-4 bundle verifiers after evaluation and before any result write; reload/recheck every consumed bundle artifact and accepted theta source rather than comparing cached pre-run strings.
7. Make T-12 reproduce the `.npy` hash without retaining a second unregistered household-score file, and enforce an exact restricted-store member set.
8. Provision and bind a durable, access-controlled, immutable restricted store; use unique non-overwriting external staging plus atomic directory-level publication, and preserve locator/hash evidence for every partial-write failure.
9. Initialize the unconditional T-23 disclosure and retention fields in every manifest, then enrich them atomically with artifact metadata; ensure every exception finalizer preserves accurate custody state.
10. Install the optimizer guard proactively in a fresh process, fail T-20 if the guard is not installed, and check prohibited modules before and after every callable execution path, including any T-12 child.
11. Record the actual chunk size and post-contract/evaluation JAX/x64 environment in the manifest rather than only in diagnostics or a pre-contract snapshot.
12. Add deterministic no-full-score integration tests for fixes 1 through 11, including successful and failing review/Git gates, post-call bundle mutation, restricted partial writes, lazy optimizer import, and all-pass status; remove the three lifecycle-state assertions and both tautological assertions.

# 11. Immediate next action

Do not commit and do not authorize the full Phase-5 dry run. Implement the twelve fixes in one bounded remediation, run the corrected deterministic no-full-score suite from the exact review-bearing state, and request an independent Phase-5 review v2 bound to that remediated state. Handle the stale committed Phase-4 test 42 in a separate housekeeping change.
