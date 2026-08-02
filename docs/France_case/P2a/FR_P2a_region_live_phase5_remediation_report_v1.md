# 1. Remediation verdict

**FINAL VERDICT: READY FOR PHASE-5 REVIEW V2**

All twelve required fixes from `FR_P2a_region_live_phase5_code_review_v1.md` §10
are implemented. The corrected deterministic no-full-score suite is **81 passed**
and is green twice consecutively; the twenty-one critical authorization/custody
tests are green ten consecutive times. No commit was made, no dry run was run,
no full 1,555-household score was computed, no design decision was reopened, and
the nested package is byte-unchanged.

One residual warning is carried forward and is stated in §22: the provisioned
restricted store has **no institutional backup**. That is the deputy-anticipated
condition of decision §5, ruled sufficient for the review and one dry run; it is
recorded verbatim in the manifest custody block so it propagates into the dry-run
packet. It is not a remediation defect.

# 2. Scope

Remediation cycle **1 of 2** under JMP-M05B, authorized by
`JMP_M05B_E2_deputy_decision_v1.md` §1 and §4.

Implemented exactly the twelve review-v1 required fixes. Nothing else.

Not done, by instruction: no commit; no Phase-5 dry run; no full-score
calculation; no change to design v4, D-1…D-8, the likelihood, the model, the
specification, θ̂, parameter values, bounds, pins, covariance formulas, the
finite-sample correction, the regional hypotheses, or any T/W constant; no
modification of `dclaborsupply-monorepo`; no change to the review-v1 file; no
test-42 housekeeping (deputy §7, separate change).

Three points the manager addendum resolved were treated as in-scope and are
implemented as directed: re-pointing `restricted_custody.store_root` to the
provisioned store in redacted form (addendum a, inside fix 8); the Windows
durability semantics for the publication transaction (addendum b); and synthetic
review fixtures with isolated throwaway repositories for the authorization-gate
tests (addendum c).

# 3. Starting state

| Object | Value |
| --- | --- |
| MNL HEAD | `983a2ecf1d16592b9f90085f6a6b690b8a964110` (unchanged; no commit) |
| Nested `dclaborsupply` HEAD / MNL gitlink | `27756a06ea189339aa82915ed2124628afed20eb` |
| Nested worktree | clean before and after |
| `Job_Market_paper` HEAD | `7195fc50f6a73e20bdf62fc4baae48c18dedd345` |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`, rehash verified before and after |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`, rehash verified before and after |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061`, unchanged |
| Phase-5 implementation + review v1 | preserved uncommitted |
| `complete/` under the Phase-5 root | absent (the root itself does not exist) |
| Household-level score bytes | none created |

The restricted store provisioned for fix 8 is bound in redacted form only:
`%USERPROFILE%\MNL\restricted_artifacts\p2a_phase5`, provisioning record
SHA-256 `d3da8fefc0c695f337ca83f2b1548dc353c6121932fde4157bad35ed7cedad72`
(read-only evidence; never copied into the repository).

**Working-tree note.** Running the pre-existing suite executes
`test_29_subprocess_dry_run_never_optimizes`, which writes a Phase-3 dry-run
attempt bundle into the accepted output tree. One such directory
(`20260801T152012Z_…_dryrun_PHASE_3_DRY_RUN_COMPLETE`, untracked, two files) was
created by that invocation and was removed, restoring the exact starting state —
the same treatment the implementation report applied to test 42's side effect.
It was incidental to a test invocation and is not evidence of any authorized run.

# 4. Files inspected

Read in full: the deputy decision v1, the JMP-M05B implementation mission
charter v1, the mission ledger v1, the PI disclosure determination v1, the
Phase-5 code review v1, the Phase-5 implementation report v1, both Phase-5
modules, the Phase-5 config, the Phase-5 test module, `phase5_parameter_map_v1.csv`,
and the restricted-store provisioning record (read-only). Read in the sections
that bind this work: design v4 §7.2–§7.4, §8.1–§8.3, §12.3–§12.5, §13, §17.1–§17.3,
§18.1–§18.6, §21, §22; the source-verification v1 and source inventory v1;
`run_p2a_regionlive_rebuild.py` (transaction, contract, Git and package-identity
helpers, reused by import).

Read-only, never modified: both accepted `complete/` bundles, the certified spec
YAML, θ̂, the Phase-3/4 runner and its config, and the nested package.

# 5. Files modified

| Path | Status | SHA-256 | Lines |
| --- | --- | --- | --- |
| `scripts/p2a/phase5_inference.py` | modified (new) | `d28977e97d6be9693681b834a8aa08b62ad5555398131b80fe80462526acce94` | 2852 |
| `scripts/p2a/run_p2a_phase5_inference.py` | modified (new) | `63ea1d653eadbdfb123b21d445f4fd07ec6535b6a8419232e83496c4f87a8e20` | 1871 |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | modified (new) | `2c9b4f0593853e4378ab562c90938217639429d7029afab974dc3e6ddd33b27b` | 87 |
| `tests/p2a/test_p2a_regionlive_phase5_inference.py` | modified (new) | `6f70c507de3b730b0c9a95e51486048cbfe720108be3b2da4186682202ded2c2` | 2423 |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_remediation_report_v1.md` | new — this report | *(self)* | — |

Unchanged and verified unchanged:

| Path | SHA-256 |
| --- | --- |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md` | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` |
| `docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md` | `2dc01c8f230feceef2df50beb30121298566af8c43bc28966d99966bfd6a65e9` |
| `.gitignore` | `09e1945563b082d75f63f18f7c9164be4a4c84f407dc06bffc66634d3b5503d5` |
| `docs/France_case/P2a/phase5_parameter_map_v1.csv` | `ed48958d4f4994f80de6dc7f3acc1c1d8490cf31f0701b8d6ac9e01cf4e9a219` |

All five modified/new files remain **uncommitted**.

# 6. Fix 1 — authorization bypass

**Defect.** Public `--mode reproduce --reproduce-out <path>` performed the full
1,555×37 score construction with no review, expected-commit, cleanliness,
package-identity, transaction-lock or custody gate, and wrote the authoritative
array to a caller-selected location. Separately, public `contract` started a
Phase-5 attempt with no review approval at all.

**Fix.** Both halves.

1. **The public reproduction route is removed.** `--mode` is now
   `("contract", "dryrun")`; `reproduce` is not a mode and `--reproduce-out`
   does not exist. `_reproduce()` is deleted. No public argument selects an
   output path for household-level bytes.
2. **The only remaining full-score child is private and equally gated.** T-12
   spawns `--internal-t12-child`, which is `argparse.SUPPRESS`ed and useless
   without a single-use nonce the parent generates per run and passes through
   the environment together with the authorization payload. Before it is
   permitted to score, the child re-runs `_verify_phase5_execution_gates`
   (review path/hash/verdict, expected MNL HEAD, expected nested HEAD, gitlink,
   full cleanliness of both worktrees) and re-binds the restricted-store
   contract. It accepts no output path and writes no file (see fix 7).
3. **`contract` is gated identically.** `_verify_phase5_execution_gates` now
   runs for every public mode in `main()`, and `_run()` refuses both modes
   unless `verified` and `execution_ready` are both true — before the lock, the
   transaction, or any write.

The contract route therefore fails closed before full scoring if any
authorization gate is absent.

**Review binding.** Review v1 is `REJECT`; deputy §6/§8 bind execution to the
independent review v2. `CANONICAL_APPROVED_PHASE5_REVIEW_REL` now names
`FR_P2a_region_live_phase5_code_review_v2.md`, and review v1 is added to
`REJECTED_PHASE5_REVIEW_RELS` beside the Phase-3 review-v6 and Phase-4 review-v7,
so it is refused as an authorizer by path as well as by verdict. The design §18.1
manifest token `PHASE5_REVIEW_V1_APPROVED` is left unchanged — it is a
design-specified string denoting "the Phase-5 review gate is satisfied", and
which document satisfies it is the deputy's decision, not this implementation's.

**Tests.** `test_r01`–`test_r06`, `test_16`.

# 7. Fix 2 — Git ancestry

**Defect.** Path confinement enumerated only MNL and its nested repository, so a
destination inside the sibling `Job_Market_paper` worktree, or any other
worktree, passed.

**Fix.** `assert_restricted_path_outside_git` is rewritten and takes
`search_roots` — places to *look for* worktrees, not a list of roots to avoid.
It rejects, each with the exact reason recorded:

- a relative path, or any `..` segment;
- any symlink or NTFS junction on the ancestor chain, and any path whose
  `realpath` differs from its literal `abspath`;
- any path whose ancestor chain contains `.git` as a **directory** (ordinary
  clone / main worktree) **or a file** (linked worktree / submodule gitlink);
- any path under a **discovered** worktree.

`discover_git_worktrees` unions two independent routes: a bounded filesystem
walk for `.git` entries under the configured repository parent
(`GIT_SEARCH_ROOTS = (MNL_ROOT.parent, MNL_ROOT, MNL_ROOT/"dclaborsupply-monorepo")`),
and `git worktree list --porcelain` on each discovered repository — which
reports linked worktrees living anywhere else on the filesystem. Case-folding
escapes are closed by comparing `os.path.normcase`d paths.

Observed on this machine: the three worktrees discovered are MNL, the nested
`dclaborsupply-monorepo`, and the sibling `Job_Market_paper`. A restricted
destination under each is rejected.

The store target is bound to the provisioned root (fix 8), and the binding
assertion runs on the **expanded** path.

**Tests.** `test_r07`, `test_r08`, `test_r09`, `test_11b`.

# 8. Fix 3 — gate ordering

**Defect.** `_phase5_evaluate()` summarised the mandatory gate register before
T-12, T-13, T-20 and T-23 existed. Those four were therefore reported missing,
the evaluator returned `STOPPED`, and `_run()` later added the gates and
recomputed the register but never cleared the stale halt or restored
`PHASE_5_DRY_RUN_COMPLETE`. An all-passing dry run could not complete.

**Fix.** `_phase5_evaluate` no longer decides a status and no longer summarises
the register; its signature changed from
`(status, halt, diag, arrays)` to `(gates, diag, arrays)`. `_run` attaches T-20,
then T-13, then T-23, then T-12, and only then calls `p5.summarise_gates` — once.
`summarise_gates` appears exactly once in the runner, and the source of
`_phase5_evaluate` is asserted not to contain it.

**Proof, without a dry run.** `test_r23` runs the **real** orchestration —
the real transaction, gate register, artifact writer, manifest, restricted
publication and finalizer — over a synthetic 6-household contract and evaluation
stand-in. All gates pass ⇒ exit 0, **exactly one** preserved attempt named
`dryrun_…_PHASE_5_DRY_RUN_COMPLETE`, `gate_register.ok == true` with
`gating_missing == []` and all four late gates present in the register, and
**no `complete/` anywhere**. `test_r24` flips T-7 to failing ⇒ exit 2, exactly
one `…_STOPPED` attempt, `stop.gate == "gate-register"`, `gating_failed == ["T-7"]`,
nothing published, and the partial restricted staging preserved with a STOPPED
suffix and truthful hash evidence. `test_r25` asserts the ordering property at
source level and that a register missing any one late gate is a failure.

The real full dry run was **not** run.

# 9. Fix 4 — parameter-map binding

**Defect.** Production derived the scientific map from the specification and the
Phase-4 contract, and read `phase5_parameter_map_v1.csv` only through an optional
display-block helper that silently returned `{}` when the file was missing.

**Fix.** `load_parameter_map_csv` authenticates before it parses: SHA-256 equal
to the accepted `ed48958d…`, the exact 20-column schema in order, exactly 47
rows, `full_index_0based` equal to the row position, the status vocabulary, the
derived 37/35/10/2 partition, dense free and interior ordinals, and the
structural rules (no free/interior index on a pinned row, no interior index on
an active-bound row, `active_bound_side == "upper"`).

`authenticate_parameter_map` then compares it against every other accepted
source in one place: the certified specification order carried by `pmap`, the
Phase-4 `contract.parameter_map`, accepted θ̂, the accepted 47-element gradient,
the pin values, and the spec bounds.

`bind_authenticated_parameter_map` stamps the authenticated map onto `pmap`, and
`assert_projection_authenticated` is called at **every** 47→37→35 projection
site — `contract/parameter-map`, `contract/H_II 37->35`,
`evaluate/S_interior 37->35`, `evaluate/parameter-table blocks`. Reporting-table
block labels now come from the authenticated record; the unauthenticated re-read
helper `_parameter_blocks()` is deleted. `_t13_reauthenticate` re-authenticates
the map after evaluation.

**One implementation-level finding, flagged not improvised.** The CSV is a
decimal *rendering* of float64 and does **not** round-trip bitwise — exactly the
property `hessian_free.csv` has [F-4], design §8.1 point 1. Measured against the
accepted sources:

| Column | max abs deviation | entries differing |
| --- | --- | --- |
| `accepted_value_full_precision` vs θ̂ | `2.220446e-16` | 15 of 47 |
| `grad_full_negll` vs `gradient_final` | `3.062871e-17` | 5 of 47 |
| `grad_free_negll` vs `gradient_final` | `8.881784e-16` | — |
| `pin_value`, `spec_bound_lb`, `spec_bound_ub` | `0.0` | 0 |

"Exact value equality" is therefore not literally attainable for the real-valued
columns, and claiming it would be false. The implemented rule instead makes the
distinction explicit and records the actual numbers:

- **names, order, status and every integer index column: EXACT equality**, which
  is what carries the scientific content;
- **real-valued columns:** agreement at `PARAMETER_MAP_VALUE_REL_TOL = 1e-15`
  (≈4.5 ULP), which admits decimal round-trip noise and nothing else, with the
  observed maximum deviation per column recorded in the manifest so the reviewer
  reads the number rather than a claim;
- **pin gradients: exactly `0.0`**, no tolerance;
- the authoritative values remain the accepted `.npy`/JSON sources; the CSV is
  never the source of a number.

If the reviewer prefers a different treatment, this is the one decision in the
remediation where a defensible alternative exists, and it is stated here rather
than buried.

**Tests.** `test_r10`, `test_r11`, `test_21`.

# 10. Fix 5 — full-gradient authentication

**Defect.** The pin-gradient falsification was tautological: the runner built a
47-name zero dictionary and filled only the 37 free entries, so every pin
necessarily appeared as zero and the design §12.5 criterion could never fire.

**Fix.** The accepted 47-element `gradient_final` lives in the accepted Phase-3
bundle member `optimizer_diagnostics.json`, so its digest is already inside that
closed hash-of-hashes. `load_full_gradient` rehashes the file against the digest
the Phase-3 bundle verifier just recomputed, checks the vector's length and
finiteness, and marks the record `authenticated`. `full_gradient_map` refuses an
unauthenticated record and produces the name-keyed 47-vector with no zero-filling.

`check_pin_gradients` now **refuses** a gradient map in which any pin name is
absent — a map that merely omits the pins would have let `.get` manufacture the
zeros again — and refuses an unauthenticated source. It records the source path,
digest, key and `assigned_zeros_by_construction: false`.

Verified pin components: all ten of
`beta_l0_m, beta_l_age_m, beta_l_age2_m, beta_l0_f, beta_l_age_f, beta_l_age2_f,
beta_l_nkids_f, theta_l_f, beta_E_y2015, beta_E_y2017` carry exactly `0.0` in the
accepted 47-vector, satisfying the accepted exact-zero contract.

**T-1 is untouched.** Design §21 step 5 binds T-1 to the Phase-4 recorded
`gradient_free`, and it still does. `crosscheck_free_gradient` records that the
47-vector's free projection agrees with that reference to `8.881784e-16` in 2 of
37 entries — one ULP of accumulated JSON round-trip, well inside the declared
`1e-14` bar — as evidence rather than assumption. Changing the T-1 reference
would have been a design change and was not made.

**Tests.** `test_02b` (rewritten), `test_r12`, `test_21`.

# 11. Fix 6 — post-evaluation reauthentication

**Defect.** T-13 copied the pre-evaluation Phase-3 and Phase-4 bundle hashes out
of the context and compared those cached strings with the frozen constants. In-run
mutation of Phase-3 artifacts or Phase-4 diagnostics/manifest would have passed
this purported post-evaluation bundle check.

**Fix.** `_t13_reauthenticate` replaces it. Nothing is cached:

1. **both closed-set verifiers re-run against the filesystem** —
   `p34._phase4_verify_phase3_bundle(...)` and `verify_phase4_bundle(...)` —
   with the recomputed roll-ups compared to the accepted constants *and* to the
   pre-run values, and the per-artifact digests recorded, not just the roll-ups;
2. **every consumed artifact reloaded and rehashed from disk**: the authoritative
   bread, the certified spec YAML, the parameter-map CSV, the Phase-3 optimizer
   diagnostics, the Phase-4 diagnostics and manifest, both config YAMLs, and the
   runner and helper modules themselves;
3. **θ̂ re-derived and rehashed**, the **full gradient re-authenticated** and
   compared bitwise with the pre-run vector, and the **parameter map re-loaded**
   and re-compared by digest and name order;
4. the Phase-3/4 runtime-input recheck, both runtime-map fingerprints, and
   bitwise pin identity.

It runs after evaluation and before any result write or publication, and raises
`HP-MUT / T-13` naming the failing labels.

**Tests.** `test_r26` (structural: both verifiers invoked, every artifact
reloaded, no cached comparison remains), `test_r27` (a one-byte mutation of the
authoritative bread in a **copy** fails T-5; a mutated gradient source fails its
rehash; the accepted bundles are proven unchanged before and after).

# 12. Fix 7 — T-12 member closure

**Defect.** T-12 left a second full score array at
`<restricted-attempt>/_t12/phase5_scores_free.npy`, outside
`PHASE5_RESTRICTED_ARTIFACTS`, the custody record and the closed bundle hash, so
ruling A-2 was not implemented in the retained store.

**Fix.** The child now streams a digest, not a file. `p5.npy_bytes` serialises
the score matrix into an in-memory buffer with `np.save`, `p5.npy_sha256` hashes
those bytes, and the child prints only the digest on stdout. It receives no
output path and creates no file — on success or on failure. The parent compares
the digest with the staged member's, and additionally asserts that the staged
`.npy` digest equals the in-memory serialisation of the same array.

The equality of the two serialisations is a verified property, not an assumption:
`test_r13` asserts `npy_bytes(S) == open(f,'wb'); np.save(f,S)` byte-for-byte.

The restricted member set is closed and enforced three ways:
`RestrictedPublication._member_path` refuses any name outside
`RESTRICTED_ATTEMPT_MEMBERS`; `seal()` refuses to proceed while any declared
member is missing; `validate_closed_member_set()` requires the staging directory
listing to equal the expected set exactly before publication. No unregistered
`_t12` file can exist, and the runner source contains no `_t12` path at all.

**Tests.** `test_r13`, `test_r16`, `test_r23` (published listing equals the
closed set exactly).

# 13. Fix 8 — restricted transaction

**Defect.** The configured custody leaf did not exist; its nearest existing
directory was an ordinary mutable Windows directory; the writer created
directories with `exist_ok=True` and published with `os.replace` per file; and
the three restricted members were written sequentially into their **final**
external directory, so a failure after one or two writes left orphaned
household-level bytes with no hashes and no locator in the STOPPED manifest.

**Fix, store binding (addendum a).** `restricted_custody.store_root` is
re-pointed to the provisioned store in **redacted** form,
`%USERPROFILE%\MNL\restricted_artifacts\p2a_phase5`, expanded at run time.
`provisioning_record_sha256` is added. At startup — before the lock is taken, so
a mis-provisioned store refuses without starting an attempt —
`verify_restricted_store_contract` asserts on the **expanded** path:

- full Git-ancestry rejection per fix 2, against every discovered worktree;
- not under any temporary directory;
- not under any cloud-synchronised root (env vars and path components) and not a
  UNC/network location — a redirected or roaming share replicates outside the
  ACL boundary;
- `staging/` and `published/` both exist;
- both on the **same volume** (`st_dev`), which is what makes the publication
  rename atomic rather than a copy;
- the provisioning record is present, **self-consistent** (recomputing its own
  published convention over its own content reproduces the digest it carries),
  and equal to the configured digest.

Binding to the record's self-declared canonical digest rather than the raw file
hash is deliberate: the raw hash is brittle under any re-serialisation and would
not verify the record's own integrity claim. Both are checked; the file digest is
recorded as evidence.

**Fix, transaction (addendum b).** `RestrictedPublication` implements:
`open()` — a unique staging directory that refuses a collision, never reused;
`write_npy`/`write_text`/`write_bytes` — each member fsync+closed, hashed from
the exact buffer written; `seal()` — `SHA256SUMS` and the custody manifest
written **before** publication, so a published directory can never hold unhashed
household-level bytes; `publish()` — closed-member validation then **one atomic
same-volume `os.rename` of the whole staging directory** into `published/`,
refusing if the destination exists; `stop(reason)` — a partial staging directory
preserved with a `.STOPPED` suffix, never deleted, with locator and per-member
hash evidence; `evidence()` — the locator reduced to its leaf name plus SHA-256.

The Windows durability semantics are implemented and documented in the module as
directed: **NTFS has no directory fsync**, so no POSIX directory-fsync barrier is
coded; the same-volume rename is the atomicity primitive.

**Redaction.** Commit-eligible artifacts carry only
`%USERPROFILE%\MNL\restricted_artifacts\p2a_phase5`, the locator's SHA-256, and
the attempt leaf name. `_redact()` strips the resolved store, and the manifest
records `expanded_root_recorded: false`. This report follows the same rule.

**Tests.** `test_r14`, `test_r15`, `test_r16`, `test_r17`, `test_r28`,
`test_r23`/`test_r24` (publication and STOPPED preservation through the real
orchestration).

# 14. Fix 9 — unconditional custody

**Defect.** The unconditional T-23 fields were absent from the manifest
skeleton, so contract attempts and early failures could omit `disclosure_class`
and `retention_responsibility`, although design §18.5 requires them on every run.

**Fix.** `p5.custody_state_skeleton` initialises all eight fields —
`disclosure_class`, `custody_state`, `custodian`, `retention_status`,
`publication_state`, `restricted_members`, `restricted_bytes_created`,
`locator_redaction` — inside `_manifest_skeleton`, i.e. **before** the store is
bound, before the lock, before the contract and before any evaluation. They are
written truthfully at that point (`NO_RESTRICTED_BYTES_CREATED`,
`restricted_bytes_created: false`) and are only ever enriched afterwards, never
introduced. `p5.custody_state_gate` validates completeness at skeleton time, at
T-23, and again in `_finalize` for **every** outcome.

`_preserve_restricted_on_failure` is called from both exception finalizers. If no
staging directory was ever opened it records exactly that; otherwise it preserves
the partial staging as `.STOPPED` and records the state, the member digests and
the redacted locator. The artifact-level custody block is merged **before** the
state fields are written, so the final state always describes the outcome and is
never overwritten by the snapshot taken at staging time.

**Tests.** `test_r18`, `test_r19`, `test_r24`.

# 15. Fix 10 — optimizer guard

**Defect.** In a fresh interpreter `scipy.optimize` is not resident when
`NoOptimizerGuard.__enter__()` runs, so the guard patched nothing; a subsequent
lazy import exposed the real `scipy.optimize.minimize`, while `record()` still
reported `ok: true` with `guard_installed: false`. The prohibited-module check
ran only at the start of `_run()`.

**Fix.** The guard **imports `scipy.optimize` proactively** and then neuters
fifteen entry points (`minimize`, `minimize_scalar`, `least_squares`, `root`,
`root_scalar`, `curve_fit`, `basinhopping`, `differential_evolution`, `linprog`,
`fmin`, `fmin_bfgs`, `fmin_l_bfgs_b`, `brute`, `shgo`, `dual_annealing`),
restoring them on exit. `record()` now **fails T-20 unless the guard is confirmed
installed** — `ok = installed and not optimizer_called` — so a guard that patched
nothing can no longer report success. It records `proactive_install`,
`import_error` and the list of patched entry points.

Prohibited-module checking is now performed at ten named points, each recorded
in the manifest with its timestamp: `phase5-start-before-imports`,
`after-optimizer-guard-install`, `after-contract-lazy-imports`,
`before-score-callable`, `after-score-callable`,
`after-t11-comparison-callable`, `before-restricted-publication`,
`t12-child-start`, `t12-child-before-score`, `t12-child-after-score`.

This deliberately changes a property test 12c asserted: `scipy.optimize` **is**
now imported, exactly once, inside the guard, solely to neuter it. Test 12c is
rewritten to assert the property that matters — one import, inside the guard,
every entry point replaced by a raiser, no entry point ever bound for use, no
optimizer called.

**Tests.** `test_r20` (a genuinely fresh subprocess: `scipy.optimize` absent at
start, guard installed, a lazily imported `minimize` is trapped), `test_r21`,
`test_r22`, `test_12`, `test_12c`.

# 16. Fix 11 — runtime metadata

**Defect.** The manifest omitted the actual chunk size and captured JAX x64
state before the production contract enabled x64, producing a stale environment
record.

**Fix.** `diag["chunking"]` and `manifest["chunking"]` record the configured
chunk size, the **realised** canonical chunk size (for `chunk_size: 0` this is
the per-builder group counts, one chunk each, which is the number ruling A-1
turns on), the per-builder chunk counts, the comparison chunk size (128) and its
chunk counts.

Three environment snapshots are recorded and labelled:
`environment` (`snapshot: pre-contract`), `environment_post_contract`
(taken after `_phase5_contract` enabled JAX x64) and
`environment_post_evaluation` (taken in `_finalize`). Each carries Python,
NumPy, pandas, SciPy, JAX, jaxlib, platform, machine, processor, cpu_count,
thread settings, XLA flags, JAX backend/devices and `jax_enable_x64`. Peak
memory continues to be recorded.

**Tests.** `test_r23` (all three snapshots present and labelled, all required
keys present, chunk metadata recorded).

# 17. Fix 12 — lifecycle-valid tests

**Removed — two tautological assertions** (review v1 §7):

| Test | Was | Now |
| --- | --- | --- |
| `test_08` | `assert round(...) == 0.0643 / 2 or True` — `or True` made it unfalsifiable | `assert round((c["c_cluster_only"] - 1) * 100, 4) == 0.0644`, the real cluster-only inflation. The tautology had been hiding a wrong constant. |
| `test_16` | `assert runner.main([...]) != 0 if False else True` — the false branch was never evaluated | `pytest.raises(SystemExit)` on `--mode real`, plus the same on `--mode reproduce`, which is the property that was meant to be tested |

**Replaced — three lifecycle-invalid assertions** (review v1 §7):

| Test | Was | Now |
| --- | --- | --- |
| `test_14` | asserted the mandated review file is **absent**, so producing the review failed the suite | asserts review v1 is in `REJECTED_PHASE5_REVIEW_RELS` and, when present, carries `**FINAL VERDICT: REJECT**` and is refused by the parser — true before and after the review exists |
| `test_14b` | pinned live HEAD to the pre-implementation documentation checkpoint, so the mandated commit failed the suite | asserts the recorded checkpoint and the numerical anchor are **ancestors** of live HEAD — true before the commit (equal) and after it |
| `test_22` | required the Phase-5 root to be **empty**, so the authorized preserved dry-run attempt failed the suite | asserts `complete/` never exists and that anything present is a `dryrun_…` attempt under `attempts/`, never a promoted bundle |

The suite is therefore valid in all three states: (1) the uncommitted reviewed
state, (2) the post-commit state, (3) the post-dry-run state.

Two further tests were corrected because the fixes deliberately changed the code
shape: `test_12c` (see §15) and `test_12d`, whose "no accepted artifact is
written" property is now stated on the **write call sites** via an AST walk
rather than on the presence of a path constant — fixes 5 and 6 made the runner
legitimately *read* from the accepted Phase-3 bundle.

**Added — deterministic no-full-score integration coverage, `test_r01`–`test_r28`.**
Authorization/review/Git gates with a well-formed synthetic APPROVE and failures
on missing review, wrong hash, REJECT verdict, wrong HEAD, wrong nested HEAD,
non-canonical path and dirty tree; dynamic worktree rejection and relative/`..`/
case-fold/symlink-junction escapes; parameter-map hash, schema and content
tampering; full-gradient tampering and the manufactured-zeros refusal;
post-evaluation bundle and input mutation; T-12 in-memory hashing and exact
member closure; restricted partial writes, atomic publication and overwrite
refusal; early-STOPPED custody truthfulness; lazy optimizer import in a fresh
process; all-pass gate ordering yielding `PHASE_5_DRY_RUN_COMPLETE`; and the
absence of `complete/`.

Per manager addendum (c), all authorization-gate tests use synthetic review
fixtures in isolated throwaway Git repositories under pytest's temp root; the
production binding constant stays pointed at the canonical review-v2 path for
the real runner, which `test_14` asserts.

No added test computes the full score matrix, runs a dry run, calls an
optimizer, or writes to any accepted artifact.

# 18. Statistical-design preservation

Nothing statistical changed. Specifically unchanged: the likelihood and its
production hook `build_jax_singles_ll(..., per_group=True)`; the model; the
specification; θ̂ (`c024b893…`); all 47 parameter values, the ten pins, the two
active upper bounds and every bound; the score construction, canonical row order
(D-7), meat, bread, `H_II`, and the covariance algebra; the finite-sample
correction `c = 1555/1520`; the regional selector `E_R`, the restriction rows,
and H0-A/B/C/G; every T- and W- gate formula; and every frozen constant —
`atol = rtol = 1e-8`, T-4 `1e-12`, asymmetry `2.3588019878151842e-4`, rank
convention `1e-10`, `κ_BE_certified = 6.0424e-12`, `z₀.₉₇₅`, and the χ² criticals.

T-1 still binds to the Phase-4 recorded `gradient_free` exactly as design §21
step 5 requires. `summarise_gates`, `GATING_TIERS`, `HALT_REGISTER` and the
warning tier are unchanged; warnings still never gate. Design v4 and D-1…D-8
were not reopened. No gate was weakened: every change either adds a gate
condition or moves an existing one later so it can actually be evaluated.

One new tolerance constant is introduced, and only for the parameter-map CSV
cross-check: `PARAMETER_MAP_VALUE_REL_TOL = 1e-15` (§9). It governs no scientific
quantity — the authoritative values remain the accepted `.npy`/JSON sources.

# 19. Package-boundary preservation

`dclaborsupply-monorepo` is **not modified in any way**. Its worktree is clean
(`git status --porcelain --untracked-files=all` returns zero lines) and its HEAD
is `27756a06ea189339aa82915ed2124628afed20eb`, matching the MNL gitlink.
`git diff --check` passes in the nested repository. No `PKG-M02` deficiency was
identified and no E2 package-modification need arose. The nested package was
inspected read-only.

# 20. Test results

| # | Validation step | Result |
| --- | --- | --- |
| 1 | Parse/compile Python and YAML | **PASS** — both modules and the test module compile; both configs parse |
| 2 | Corrected Phase-5 no-full-score suite, twice | **PASS** — `81 passed in 15.22s`; `81 passed in 15.31s` |
| 3 | New critical authorization/custody tests, ≥10 consecutive | **PASS** — 10/10 runs `21 passed`, 0 failing runs |
| 4 | Applicable pre-existing suites | **PASS** — `141 passed, 2 deselected in 32.55s` |
| 5 | `git diff --check` | **PASS** — MNL exit 0; nested exit 0 |
| 6 | Both accepted bundles verified | **PASS** — Phase-3 `2cf23764…`, Phase-4 `54848869…`, `hessian_free.npy` `e9ca080e…`, parameter map `ed48958d…`, all equal to accepted |
| 7 | Nested repository clean | **PASS** — zero status lines |
| 8 | No restricted score bytes exist | **PASS** — no `phase5_scores_free.npy/.csv` or `phase5_score_row_index.csv` anywhere under MNL or the restricted store; store `staging/` and `published/` both empty |
| 9 | No `complete/` | **PASS** — the Phase-5 root does not exist |
| 10 | Review v1 remains REJECT and cannot authorize | **PASS** — verdict line `**FINAL VERDICT: REJECT**`; the parser refuses it; the execution gate refuses it by path; the binding constant names review v2 |

The two deselections in step 4 are the pre-existing `test_29` and `test_42`,
both of which write production attempt bundles into the accepted output tree —
the same deselections the implementation report used. `test_42` additionally
fails at HEAD independently of this work; deputy §7 assigns it to separate
housekeeping and it is not touched here.

**Total Phase-5 test count: 53 → 81** (28 added; 2 tautological and 3
lifecycle-invalid assertions corrected; 2 further tests restated to match the
deliberately changed code shape).

# 21. Artifact-integrity results

| Object | Before | After | Result |
| --- | --- | --- | --- |
| MNL HEAD | `983a2ecf…` | `983a2ecf…` | unchanged — no commit |
| Nested HEAD / gitlink | `27756a06…` | `27756a06…` | unchanged |
| Phase-3 bundle | `2cf23764…` | `2cf23764…` | rehash identical |
| Phase-4 bundle | `54848869…` | `54848869…` | rehash identical |
| `hessian_free.npy` | `e9ca080e…` | `e9ca080e…` | identical |
| `phase5_parameter_map_v1.csv` | `ed48958d…` | `ed48958d…` | identical, now hash-bound in code |
| Review v1 | `b71a0b5b…` | `b71a0b5b…` | unchanged |
| Implementation report v1 | `2dc01c8f…` | `2dc01c8f…` | unchanged |
| `.gitignore` | `09e19455…` | `09e19455…` | unchanged |
| Phase-3/4 runner and config, certified spec YAML, θ̂ CSV | — | — | untouched (`git status` clean for each) |
| Household-level score bytes | none | none | none created |
| Restricted store | empty | empty | `staging/` and `published/` both empty |

Working tree at return — identical to the starting state apart from the one new
report:

```
MNL (C:\Users\hisham\Repo\MNL)   HEAD 983a2ecf1d16592b9f90085f6a6b690b8a964110
 M .gitignore
?? docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_remediation_report_v1.md   (new)
?? scripts/p2a/configs/p2a_phase5_inference_v1.yaml
?? scripts/p2a/phase5_inference.py
?? scripts/p2a/run_p2a_phase5_inference.py
?? tests/p2a/test_p2a_regionlive_phase5_inference.py

dclaborsupply-monorepo           HEAD 27756a06ea189339aa82915ed2124628afed20eb
   clean — no modification of any kind
```

# 22. Residual warnings

1. **Restricted store has no institutional backup — carried forward, not a
   remediation defect.** The store is on the local `C:` volume only, outside the
   institutional UNC-redirected folder set and outside the EUROMOD-STORAGE backup
   convention. Loss of that volume is total loss of the custody artifacts. Deputy
   decision §5 anticipated this and ruled it sufficient for the implementation
   review and one dry run; the warning is recorded verbatim in
   `restricted_custody.retention_status` and propagates into the manifest custody
   block, hence into the dry-run packet. Confirmation of institutional
   backup/retention may be required before a production real run.

2. **The parameter-map CSV does not round-trip float64 bitwise** (§9). Names,
   order, status and all index columns are compared exactly; real-valued columns
   at `1e-15` relative with the observed deviations recorded. This is the one
   place where "exact value equality" as written in fix 4 is not literally
   attainable, and the reviewer should rule on the treatment.

3. **`environment_post_contract` is absent from a refused run**, by construction:
   a run refused at the authorization gate never reaches the contract. The
   pre-contract snapshot and the full custody state are still recorded.

4. **The T-12 child re-runs the full contract**, so an authorized dry run pays
   the contract cost twice. This is the price of gating the child identically to
   the parent (fix 1) and is deliberate.

5. **Pre-existing, unchanged, out of scope:** `test_42` remains stale at HEAD
   (deputy §7 housekeeping), and `test_29` and `test_42` both write production
   attempt bundles into the accepted output tree when run, so both remain
   deselected. Neither is a Phase-5 defect.

6. **A-2/A-3/A-4 interpretations stand as ruled by review v1 §8** and were not
   revisited. A-1's metadata gap is closed by fix 11.

# 23. Whether review v2 may begin

**Yes.** All twelve fixes are implemented and individually evidenced above; the
corrected deterministic no-full-score suite is green and stable; the accepted
artifacts, the nested package and review v1 are provably unchanged; nothing was
committed and no dry run was run. The state is bound to MNL HEAD
`983a2ecf1d16592b9f90085f6a6b690b8a964110` with the four uncommitted Phase-5
files at the digests listed in §5.

Review v2 should rule explicitly on:

- the parameter-map value-comparison treatment (§9, residual warning 2);
- the review-binding decision to point `CANONICAL_APPROVED_PHASE5_REVIEW_REL` at
  review v2 while leaving the design §18.1 token `PHASE5_REVIEW_V1_APPROVED`
  unchanged (§6);
- the T-12 in-memory-digest design as the implementation of ruling A-2 (§12);
- the restricted-store contract and the retention warning (§13, §22.1).

No E2 halt condition fired. No fix required touching design v4, D-1…D-8, the
package, or a gate constant, so no fix was stopped and reported under addendum
(e).

# 24. Immediate next action

Commission the independent Phase-5 **code review v2** (Codex, read-only,
maximum reasoning) bound to this exact remediated state, producing
`docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v2.md` with first
heading `# 1. Phase-5 review verdict` and one exact `**FINAL VERDICT: …**` line —
the form the implemented gate parser requires. Review v1 remains immutable
history.

Do not commit and do not authorize the full Phase-5 dry run before review v2
`APPROVE`. The separate test-42 housekeeping change (deputy §7) remains
outstanding and must stay logically separate from the Phase-5 implementation
commit.
