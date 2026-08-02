# FR P2a Region-Live — Phase-5 Architectural Closure Report — v1

**Mission:** JMP-M05B — Phase-5 Inference Implementation and Certification
**Cycle:** the one deputy-authorized **architectural closure** (`JMP_M05B_E2_deputy_decision_v2.md`) — not remediation cycle 3
**MNL base:** `983a2ecf1d16592b9f90085f6a6b690b8a964110`
**Date:** 2026-08-02
**Commit status:** **UNCOMMITTED**. Commit is prohibited until review v4 `APPROVE` (deputy §9).

---

## 1. Closure verdict

The single-entry architecture is implemented and the application-level full-score capability is reduced to **one** gated process entry, confirmed by a static call-site scan: exactly one `build_score_matrix(` call site exists in application code, inside the nested provider of the gated entry. The six narrow residual groups are implemented. Validation is complete and green.

**FINAL VERDICT: READY FOR CLOSED-FORM REVIEW V4**

---

## 2. Scope

Implemented: the single-entry architecture (§A), the T-12 child capability (§B), canonical configuration binding (§C), the closed-form surface inventory (§D), STOPPED rename safety (§E), post-evaluation reauthentication in every full-score process (§F), truthful complete inventory (§G), behavioural tests (§H), lifecycle-aware working-set tests (§I), and documentation cleanup (§J).

Not touched: the statistical design, likelihood, loader, θ̂, parameters, bounds, pins, covariance formulas, correction scalar, hypotheses, T/W constants, package source, and output interpretation. No full 1,555-household score was computed. No dry run. No commit.

---

## 3. Starting state

Verified before any code was written.

| Axis | Expected (addendum a) | Observed | Result |
| --- | --- | --- | --- |
| MNL base | `983a2ecf…` | identical | PASS |
| Modified | `.gitignore`, `tests/p2a/test_p2a_regionlive_phase3_safety.py` | exactly those two | PASS |
| Untracked code | Phase-5 sources/config/tests | 4 files | PASS |
| Untracked reviews | v1/v2/v3 | 3 files | PASS |
| Untracked reports | "five report docs" | **4** | see below |
| Nested | clean at `27756a06…` | clean, identical | PASS |

**One discrepancy, reported before writing code as the addendum requires.** The addendum (and review v3 §2) state *five* untracked report documents; the working set contains **four**: `FR_P2a_phase4_test42_housekeeping_report_v1.md`, `FR_P2a_region_live_phase5_implementation_report_v1.md`, `FR_P2a_region_live_phase5_remediation_report_v1.md`, `FR_P2a_region_live_phase5_remediation_report_v2.md`. **Nothing unexpected is present** — no extraneous or foreign artifact — so the "anything else: stop" condition did not fire. This is a propagated counting discrepancy, not a repository defect; the fifth report is this closure report, created by this cycle. The §I profiles encode the *observed* inventory, enumerated from the repository rather than from the prose count.

---

## 4. Threat-model compliance

The frozen model (deputy §2) is honoured exactly and not expanded. The boundary protects against accidental invocation, bypass through documented or import-callable application routes, stale or caller-supplied configuration, forged review/revision/custody inputs, output-path substitution, Git-worktree leakage, transaction/failure-record inconsistency, and mutation between evaluation and publication.

It does **not** claim security against an adversary who already has arbitrary code execution in the same interpreter. This is stated in the module header, in the inventory JSON (`threat_model`), and in `_ScoringAuthorization`'s docstring. Accordingly the primary boundary is **structural** — the full score is built only inside a nested closure with no module-level name — with the token and the opaque context as defence in depth, never as the sole boundary (§A.9).

---

## 5. Single gated process entry

`main()` in `scripts/p2a/run_p2a_phase5_inference.py` is the only application-level process entry capable of full scoring.

1. It parses the CLI and calls `_load_canonical_config()` itself.
2. The canonical YAML bytes are digested and bound **before** any score-capable object exists.
3. Review, revisions, cleanliness, gitlink, bundles, parameter map, gradient, config and restricted-store identity are authenticated.
4. Only then is `_ScoringAuthorization` constructed — it refuses any constructor call that does not present the module-private entry token, and the token is used at exactly one place.
5. Full scoring happens only inside `_open_scoring_session`'s nested `_NestedScoreProvider`, which captures the authorization lexically and re-checks it on every call.
6. `_phase5_contract` without an authorization is contract-only: it withholds `per_group_free_fns`, `loader_data`, `jax` and `jnp`, and sets `score_capable=False`.
7. No caller can pass `cfg5`, booleans, records, contexts, roots or output paths into a score-capable function: `main` loads the config, `_run` rederives authorization, and `_phase5_evaluate` requires both the active context and the nested provider.
8. The direct `_phase5_contract` + `_phase5_evaluate` route is structurally disabled and refuses before computing.
9. Tests use bounded synthetic fixtures — a synthetic contract plus a synthetic score provider — rather than bypassing authorization.

---

## 6. Parent and T-12 child roles

Both are roles of the same entry and reach a score through the same `_open_scoring_session`.

| | Parent | T-12 child |
| --- | --- | --- |
| Entered via | `main → _run` | `main → _t12_child` (private flag + nonce + single-use capability) |
| Score path | `_open_scoring_session` → nested provider | identical |
| Post-evaluation reauth | `_t13_reauthenticate` | `_t12_child_reauthenticate` |

The child previously performed the *last* full evaluation with no post-evaluation check (review v3 gates 23/24). It now reruns both closed-set bundle verifiers, rehashes every consumed input against its frozen pre-digest, re-asserts the canonical configuration, and re-verifies the restricted-store contract **before** returning its digest.

---

## 7. Authorization-context construction

`_ScoringAuthorization` has no public constructor, `__slots__` only, an opaque `__repr__` that leaks no field values, and a `summary()` that carries digests and identities but no store path. It is created only after every gate passes, registered in `_ACTIVE_AUTHORIZATION`, and torn down in a `finally` block so it never outlives its attempt. `_require_active_authorization` refuses anything that is not an instance **and** is not the context currently in force.

---

## 8. Canonical configuration binding

`_load_canonical_config()` reads the canonical YAML bytes, digests them, parses them, and checks `output_subdir`. `_assert_config_is_canonical()` re-reads the file, re-compares the digest, and requires the in-use object to be value-identical to the canonical content — refusing an in-memory substituted configuration, which is the review-v3 gate-7 route (a caller-supplied `cfg5` naming a different eligible restricted root). It runs before the scoring session opens and again in post-evaluation reauthentication, so the manifest and T-13 describe the same configuration object scoring and custody actually consumed.

---

## 9. Full-score surface inventory

`docs/France_case/P2a/phase5_full_score_surface_inventory_v1.json`

- `application_full_score_surface_count = 1`
- `expected_full_score_call_sites = ["scripts/p2a/run_p2a_phase5_inference.py:625"]`
- `inventory_sha256 = 734606947854ed1bfd3ee807df5000e3128cc93d2fa1b33fcfaedee7412cf330`

It records the canonical surface's source file, process-entry symbol, both roles, authorization prerequisites, the canonical config source and digest rule, the restricted-store binding, and the post-evaluation reauthentication for each role; the removed/disabled former surfaces; the excluded generic primitives with rationale; and the tests proving noncanonical routes refuse. `test_ac_single_gated_entry_is_the_only_full_score_surface` re-derives the call-site list statically and fails if it ever disagrees with the declared list, and independently recomputes the inventory's self-digest.

Per addendum (b), the JSON is created in this cycle but committed only at the deputy §9 step-2 gate after review v4 `APPROVE`.

---

## 10. Removed or disabled former surfaces

| Former surface | Status | Mechanism |
| --- | --- | --- |
| `_phase5_contract` + `_phase5_evaluate` | structurally incapable | contract-only result withholds every score-capable handle; the evaluator requires the active context **and** the nested provider |
| `_run(args, cfg5, …, gates_record)` | structurally incapable | authorization rederived at entry and before scoring; configuration bound to the canonical digest |
| `_t12_child(cfg5, cfg34)` | role of the canonical surface | single-use parent-issued capability + complete post-evaluation reauthentication |

Excluded as generic primitives, with rationale recorded in the inventory: `build_score_matrix`, `jacrev_subset_scores`, and the nested package's `build_jax_singles_ll`. None can independently construct the accepted Phase-5 artifact, which additionally requires the production loader data, the authenticated 47→37→35 embedding, the accepted θ̂ and the canonical row order.

---

## 11. STOPPED rename safety

Immediately **before** the rename, `stop()` re-resolves and revalidates the staging source and its ancestors, rejects reparse points, and proves containment beneath the authenticated root. Immediately **after**, it resolves and validates the STOPPED endpoint and its ancestors, and verifies same-volume authenticated-root containment, failing closed while preserving truthful evidence if the endpoint is invalid. This closes review-v3 gates 11/12, in which a post-open junction could survive as a STOPPED endpoint pointing outside the root.

---

## 12. Post-evaluation reauthentication

After **every** full-score evaluation — parent and child — the process reruns closed-set Phase-3 and Phase-4 bundle verification, reloads and rehashes every consumed input against its frozen pre-evaluation digest, rederives θ̂, gradient, map, bounds, pins and the canonical configuration from source, verifies restricted-store identity and the provisioning record, compares against the exact objects used during evaluation, and refuses publication on any mutation. No cached semantic object substitutes for a required reload.

---

## 13. Truthful retained-member inventory

`inventory()` enumerates every retained filesystem object — regular files, directories, junctions, symlinks, unreadable members, and partial/unbookkept members — and requires agreement among the top-level custody state, the observed inventory, declared membership, member hashes, and the STOPPED bundle membership and hash. A byte written before bookkeeping is still discovered and reported truthfully, which is the review-v3 gate-32 contradiction.

---

## 14. Behavioral integration tests

Deterministic, bounded-synthetic tests cover: direct contract/evaluate refusal; in-memory config substitution refusal; copied provisioning record with a different root; replayed child capability; T-12-window mutation; STOPPED junction replacement; partial-write truthfulness; no-publication on failure; surface count exactly one; noncanonical-route refusal; and no household score bytes created by the suite.

---

## 15. Lifecycle-aware tests

The hard-coded guard is replaced by three **exact** state profiles — reviewed-uncommitted, clean post-commit, and post-dry-run with exactly one preserved attempt — asserted with set **equality** on both the modified and untracked sets, never `<=`. The simulated-repository test materialises each profile in a throwaway repo and proves the contract holds in all three, including that `complete/` never exists in any state.

---

## 16. Documentation corrections

Stale review-v2 CLI help and obsolete heading/path references are corrected. Because review v3 returned `REJECT`, the executable authorization target advances to **review v4**, exactly as v2 -> v3 was handled last cycle and as deputy s9 requires (the dry run binds to the "review-v4 path/hash"). `CANONICAL_APPROVED_PHASE5_REVIEW_REL`, `PHASE5_REVIEW_HEADING` (`# 1. Phase-5 review-v4 verdict`), the CLI help and the tests all move together; reviews **v1, v2 and v3** are now all named in `REJECTED_PHASE5_REVIEW_RELS` and none can authorize execution.

The residual "relative bar" wording that review v3 s3 flagged in the emitted authentication note is replaced. Every remaining comparator description uses the sole authoritative R-23b-rev string verbatim, per addendum (c):

`a == b or abs(a-b) <= 1e-15 * max(abs(a), abs(b), 1.0)`

It is described as the approved **mixed absolute/relative** policy and never as a purely relative bar.

---

## 17. Statistical-design preservation

Unchanged: the 47/37/35 dimensions, θ̂, bounds, pins, the name-keyed conditional estimand, the symmetrised accepted Phase-4 bread, the household score and unweighted meat, the model and robust covariance formulas, `1555/1520`, the regional restrictions, the certified `κ_BE = 6.0424e-12`, and every T/W threshold. No optimizer or Hessian evaluation ran.

---

## 18. Package-boundary preservation

`dclaborsupply-monorepo` is clean at `27756a06ea189339aa82915ed2124628afed20eb`, equal to the MNL gitlink. No package file changed. Phase 5 still reaches the likelihood only through `build_jax_singles_ll(..., per_group=True)`.

---

## 19. Test results

| Check | Result |
| --- | --- |
| K1 parse/compile Python + YAML + JSON | OK |
| K2 complete no-full-score suite, twice | **103 passed**, 103 passed |
| K2b whole repository, attempt-writers deselected | **163 passed, 2 deselected** |
| K3 critical single-entry / replay / config-binding / mutation / STOPPED-inventory / lifecycle x10 | 17 passed on all ten runs |
| K4 `application_full_score_surface_count` | **1** |
| K5 `git diff --check` | clean |
| K6 accepted Phase-3 / Phase-4 bundles | rehash exactly |
| K7 nested repository | clean at `27756a06...`, unchanged |
| K8 restricted store | `staging/` and `published/` both empty |
| K9 Phase-5 output root / `complete/` | neither exists |
| K10 reviews v1/v2/v3 | byte-immutable and non-authorizing |

The two deselected tests write production attempt bundles into the accepted output tree; `test_42` additionally fails at HEAD for a pre-existing reason unrelated to Phase 5 and remains in the separate TEST-42 commit scope.

---

## 20. Artifact and custody integrity

| Object | SHA-256 | State |
| --- | --- | --- |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | rehashes exactly |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | rehashes exactly |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | rehashes exactly |
| Review v1 | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` | byte-immutable |
| Review v2 | `48eae5ebbfd5fbeeb8527a4e75cb82f925dbe272342b84dd6a8e951241a3465d` | byte-immutable |
| Review v3 | `529fcb59a9ae879287b5dc671b80910bc7975c9d8ae375a7f8ab2bb1f13e6752` | byte-immutable |

The restricted store's `staging/` and `published/` are empty; no household-level score artifact exists. No Phase-5 output root and no `complete/` exist anywhere.

---

## 21. Residual warnings

1. **No institutional backup for the restricted store** — carried forward; operational limitation ruled sufficient for review plus one dry run.
2. **`test_42` fails at HEAD for a pre-existing, unrelated reason** and remains in the separate TEST-42 commit scope.
3. **Review v4 does not exist**, so the dry run cannot start — the intended fail-closed state.
4. **The report-count discrepancy of §3** is unresolved in the governing prose; the repository state is self-consistent.
5. **`_phase5_evaluate` end-to-end remains unexercised on real data** — that is the full dry run, forbidden here.

---

## 22. Whether review v4 may begin

**Yes.** Exactly one application-level full-score surface exists and is declared in the closed-form inventory; every formerly exposed route is structurally incapable; the six narrow groups are implemented; the statistical design and package boundary are untouched; and no full dry run or household score artifact was created.

---

## 23. Immediate next action

Return this report, the surface inventory and both worktree statuses to the Goal 1 Manager, and commission independent review v4 (Codex, fresh session, read-only, maximum reasoning) under the 51-gate framework plus the closed-form inventory. On `APPROVE`: the deputy §9 commit sequence, then exactly one full dry run. On `REJECT`: JMP-M05B pauses and returns to the deputy — no further code change is authorized.

**FINAL VERDICT: READY FOR CLOSED-FORM REVIEW V4**
