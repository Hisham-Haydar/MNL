# FR P2a Region-Live — Phase-5 Remediation Report — v2

**Mission:** JMP-M05B — Phase-5 Inference Implementation and Certification
**Cycle:** final remediation cycle **2 of 2** (card M05B-AC-8, manager ruling **R-25**)
**Fix source:** `FR_P2a_region_live_phase5_code_review_v2.md` §17–§18 (ten correction groups), read in full with each per-fix section §5–§15
**Date:** 2026-08-01
**Commit status:** **UNCOMMITTED**, as is every Phase-5 file at this stage.

---

## 1. Remediation verdict

All ten correction groups of review v2 §18 are implemented, with the three manager rulings applied as written. The no-full-score suite is green and stable: **96 tests, 96 passed**, twice in succession, and the critical authorization/custody/reparse subset passed **10 consecutive times**. No design constant, package file, θ̂, pin, bound or gate constant changed. No full dry run and no real run were performed. Reviews v1 and v2 are byte-identical to their pre-remediation digests.

**FINAL VERDICT: READY FOR FINAL EXACT-STATE REVIEW**

---

## 2. Scope and starting state

Scope was exactly the ten groups plus Step 0. Nothing else was touched.

Binding state at entry, re-verified:

| Object | Value | Result |
| --- | --- | --- |
| MNL HEAD | `983a2ecf1d16592b9f90085f6a6b690b8a964110` | unchanged |
| Nested `dclaborsupply` HEAD = gitlink | `27756a06ea189339aa82915ed2124628afed20eb` | unchanged, clean |
| `Job_Market_paper` HEAD | `7195fc50f6a73e20bdf62fc4baae48c18dedd345` | unchanged |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | rehashes exactly |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | rehashes exactly |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | rehashes exactly |
| Review v1 | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` | **unchanged** |
| Review v2 | `48eae5ebbfd5fbeeb8527a4e75cb82f925dbe272342b84dd6a8e951241a3465d` | **unchanged** |

---

## 3. Step-0 reconciliation (fix 10, executing ruling R-24)

**Before.** `git status --porcelain` carried one entry beyond the manager's expected inventory — the untracked completed Phase-3 attempt review v2 §2 recorded as the gate-49 defect:

```
 M .gitignore
 M tests/p2a/test_p2a_regionlive_phase3_safety.py
?? docs/France_case/P2a/FR_P2a_phase4_test42_housekeeping_report_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v2.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase5_remediation_report_v1.md
?? outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/attempts/
     20260801T155028Z_242820_7bd3042fec0d4ca193ee496c54789eb8_dryrun_PHASE_3_DRY_RUN_COMPLETE/
?? scripts/p2a/configs/p2a_phase5_inference_v1.yaml
?? scripts/p2a/phase5_inference.py
?? scripts/p2a/run_p2a_phase5_inference.py
?? tests/p2a/test_p2a_regionlive_phase5_inference.py
```

**Inspected before deletion.** Two files (`phase3_console.log`, `phase3_manifest.json`); `status = PHASE_3_DRY_RUN_COMPLETE`, `optimizer_called = false`; zero files tracked by Git. A non-optimizing Phase-3 dry-run attempt, not evidence of record.

**Action.** Exactly that directory was deleted, in one command. Nothing else was removed; the pre-existing empty `.staging` bases were left untouched.

**After.** The working set is now exactly the manager's inventory — 2 modified, the Phase-5 untracked set, the report docs, and reviews v1/v2. No `/attempts/` entry remains. `test_c2_fix10_working_set_is_exactly_the_manager_inventory` asserts this and will fail if any attempt directory reappears.

**Accepted bundles untouched:** both rehash to their frozen values, before and after (§16).

---

## 4. Fix 1 — authorization cannot be forged at the scoring entry point

*Review v2 gates 6 and 8; §5 and §17 item 1.*

`_run()` trusted two caller-supplied booleans, so a Python caller could reach `_phase5_evaluate` without passing the verifier — and the integration tests did exactly that.

- `_run` now **rederives the entire authorization from the actual files and repositories** via `_reauthorize(args, "run-entry")`, and rederives it **again immediately before the scoring call** as `_reauthorize(args, "before-scoring")`. The `gates_record` parameter is no longer trusted for anything.
- `_verify_phase5_execution_gates` now returns an `authorization_binding` — a SHA-256 over the *observed* facts (both HEADs, gitlink, review path, review digest). `_assert_authorization_binding` requires any supplied record to match the freshly derived binding **and** each bound field. A fabricated record cannot match unless the environment genuinely authorizes, in which case it is not a forgery.
- `main()` no longer threads a record at all; a failed gate returns exit 2 with a clean message and writes nothing.
- There is no bypass parameter and no injectable verifier result. The only seams are `_auth_repo_root()`/`_auth_nested_root()`, which select the **repository location** — the full verifier still runs against whatever they return, exactly as the accepted Phase-3/4 `_repo_root`/`_nested_root` convention does.
- The synthetic orchestration fixture no longer forges a record: it builds a **genuinely authorizing repository** with real HEADs, a real `160000` gitlink, a clean worktree and a real review file carrying the exact v3 heading and an exact APPROVE. `_check_gitlink=False` was removed from the authorization tests, so the gitlink axis is now genuinely exercised.

---

## 5. Fix 2 — authorization bound to the final review artifact

*Review v2 gate 48 and §17 item 2, under the manager's targeting clause.*

Review v2's "review-v2 heading" wording is superseded on this one point: v2 is `APPROVE AFTER FIXES` and can never authorize execution. The executable approval is v3.

| Item | Value |
| --- | --- |
| `CANONICAL_APPROVED_PHASE5_REVIEW_REL` | `docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v3.md` |
| `PHASE5_REVIEW_HEADING` | `# 1. Phase-5 review-v3 verdict` |
| `REJECTED_PHASE5_REVIEW_RELS` | **both** v1 and v2 |

The parser, the constants, the CLI help text and the tests all bind to v3. The refusal list carries per-document reasons (v1 REJECT; v2 conditional, never executable) alongside the Phase-3 review-v6 and Phase-4 review-v7. The parser test asserts that the obsolete `# 1. Phase-5 review verdict` and `# 1. Phase-5 review-v2 verdict` headings no longer authenticate, and that an `APPROVE AFTER FIXES` verdict is refused — which is precisely why v2 cannot be the authorizer. The full review/revision/cleanliness lifecycle (both HEADs, gitlink identity, full cleanliness of both worktrees, review path, digest, heading, verdict) is unchanged and still runs before any score.

The v3 file does not exist yet, which is correct: the dry run cannot start until the final review produces it.

---

## 6. Fix 3 — reparse points and containment escapes

*Review v2 gates 11 and 12; §6 and §17 item 3.*

The review replaced `staging/` and `published/` with NTFS junctions and the store contract still returned success, because the children were checked only with `is_dir()`/`stat()`.

Three new helpers in `phase5_inference.py`:

- `is_reparse_point()` — detects symlinks **and junctions**, via `st_reparse_tag` / `FILE_ATTRIBUTE_REPARSE_POINT` (`0x400`). `Path.is_symlink()` alone does not catch a junction, which was the gap.
- `assert_no_reparse_point()` — fail-closed refusal.
- `assert_contained_realpath()` / `assert_restricted_endpoint()` — containment proved on **fully resolved** paths, so a reparse point anywhere in the chain is caught, not only at the leaf.

Applied immediately before use or rename at every security-sensitive endpoint: the store **root**, the fixed **`staging/`** and **`published/`** children, each **member path**, the **staging attempt directory**, the **stopped destination**, and the **publication source and destination**.

The test reproduces the review's exact probe — provision a store, confirm it passes, junction-replace `staging/`, and confirm the contract now refuses — and asserts the failure message names the reparse point, so it cannot pass for the wrong reason. It uses the `outside_temp` fixture so the temporary-directory refusal cannot mask the reparse check.

---

## 7. Fix 4 — the authenticated map at every projection

*Review v2 gate 18; §8 and §17 item 4.*

The one projection that actually reached score construction was the one **not** keyed on the authenticated CSV: the embedding used `pmap34["free_idx"]` and a `base_full` from the reused Phase-4 contract.

- New `authenticated_embedding(pmap, csv_rec, theta_full)` derives the free full-indices, the pin positions, the pin payload (from the authenticated `pin_value` column), `base_full`, and the free vector — all **by name** from the authenticated map, and only after `assert_projection_authenticated`.
- New `assert_embedding_agrees()` keeps the Phase-4 embedding as a **cross-source witness** that must agree bitwise. On disagreement, score construction is refused.
- The runner now builds `free_idx` and `base_full` from the authenticated embedding, and `ctx["free_hat"]` is **re-derived after authentication** rather than inherited from the pre-authentication Phase-4 projection.
- Testing is behavioural, not source-token: an **unbound** map raises `T-17` from `authenticated_embedding`, and a **disagreeing** witness raises from `assert_embedding_agrees`. `test_21` additionally proves all of this on the **real accepted state**, including that the authenticated free positions equal the by-name positions and that `free_hat` matches the Phase-4 projection bitwise.

---

## 8. Fix 5 — T-13 anchors and full re-authentication

*Review v2 gates 24 and 25; §10 and §17 item 5.*

T-13 searched the Phase-4 artifact hash map by basename and **set the result to success when no entry existed**, leaving both configurations, the Phase-4 manifest, the Phase-5 config, the runner and the helper unchecked.

- New `_consumed_input_paths()` defines the **closed** consumed-input set, deliberately including every object that carries no frozen constant, plus the whole Phase-3/4 runtime map.
- New `_consumed_input_digests()` freezes a **raw pre-evaluation SHA-256 for every one of them** in the contract.
- T-13 iterates exactly that set and compares post-evaluation digests to the frozen pre-digests. **A missing pre-digest is itself a failure** — the default-to-success branch is gone, and `test_r26` asserts the removed line is absent and the new failure reason present.
- **Theta is re-derived** from the reloaded `estimation_results.json`, not hashed from `ctx["theta_hat"]`, and is compared both to the accepted digest and bitwise to the vector actually used.
- The **complete cross-source parameter-map authentication** is re-run (`authenticate_parameter_map`), not merely a digest/name comparison, and the authenticated embedding is re-derived and required to be bitwise stable.

---

## 9. Fix 6 — exclusive members and truthful stopped inventory

*Review v2 gates 29 and 32; §12 and §17 item 6.*

- `write_bytes` now opens members with **`"xb"`** (exclusive). A duplicate declared name fails; an on-disk squatter fails; the first bytes are never silently overwritten. The hash is recorded only after a durable fsynced write.
- New `inventory()` **scans, hashes and classifies the actual retained files** without deleting anything: observed members and digests, sizes, undeclared members, declared-missing members, and `partial_or_unbookkept` — files that exist but were never bookkept, or whose bookkept hash disagrees with the bytes on disk.
- `evidence()` is now derived from that inventory. The review's exact contradiction — bytes on disk while STOPPED evidence reported `restricted_bytes_created=false` — is reproduced in a test and now reports `true`, names the file, and carries its real digest with `inventory_matches_bookkeeping=false`.
- `publish()` refuses while the directory disagrees with the recorded hashes or contains anything undeclared.

---

## 10. Fix 7 — no raw locator in commit-eligible records

*Review v2 gate 34; §12 and §17 item 7.*

`_redact` added a locator hash but left the raw `custody_locator` in the structure merged into diagnostics and the manifest.

- `_redact` now strips **recursively** every key in `_RAW_LOCATOR_KEYS` (`custody_locator`, `restricted_store_resolved`, `expanded_root`, `store_root_expanded`, `restricted_locator`, `locator`) from dicts and lists, retaining only the SHA-256 and an explicit `locator_redaction` note.
- New `assert_no_raw_locator()` is a **negative assertion** applied to both commit-eligible artifacts — `phase5_manifest.json` in `_finalize` and `phase5_diagnostics.json` in `_write_committed_artifacts` — and it additionally fails if the **expanded store path** appears anywhere in the serialised record, even without a locator key.
- The expanded path is held only in the process-local `_EXPANDED_STORE_ROOT`, which is never serialised.

---

## 11. Fix 8 — the tolerance ruling now describes what is implemented

*Review v2 §3 (R-23b), §17 item 8, under manager ruling **R-23b-rev**.*

Per the ruling, the **implemented comparator is kept as the approved policy** and the language is corrected. **No design constant was altered**: `PARAMETER_MAP_VALUE_REL_TOL` remains `1e-15`.

The policy, stated exactly as implemented:

```
agree(a, b)  <=>  a == b  or  |a - b| <= 1e-15 * max(|a|, |b|, 1.0)
```

This is a **mixed absolute/relative** rule, not a uniform relative one:

- **|value| ≥ 1** — the `max(…, 1.0)` term is inert, so the bar is a **relative** `1e-15`, ≈ 4.5 ULP of a float64 of that magnitude;
- **|value| < 1** — the `1.0` term dominates, so the bar is an **absolute floor of 1e-15**, which is looser in relative terms (≈ `1e-12` relative at a value of order `1e-3`).

**Why the absolute floor is required, at ULP scale.** Several authenticated columns are **exactly `0.0`** — most importantly the ten pin coordinates of `gradient_final`, whose exact zero *is* the design §12.5 falsification criterion. A purely relative rule degenerates at zero (`rel_tol · 0 = 0`), so it would admit no deviation at all and would collapse to bitwise equality precisely where a decimal rendering is least able to guarantee it. The floor is what makes a decimal CSV round-trip comparable near zero, and at `1e-15` it sits far below every accepted magnitude in the map.

**Scope.** The comparator governs only agreement of the committed CSV *rendering* with the authoritative sources. It is not a design constant, not an inference tolerance, and it relaxes no T-/W- gate. The CSV additionally carries a fixed byte digest, so this is a redundant second control.

Recorded in code as `PARAMETER_MAP_VALUE_COMPARATOR`, written into the manifest under `parameter_map.value_comparator`, and asserted by a test that exercises the rule on both sides of unity and at exact zero. The test also asserts no source still claims a "uniform 1e-15 relative" or "4.5-ULP rule".

---

## 12. Fix 9 — the `.staging` lifecycle contract, proved in three states

*Review v2 gate 44; §15 and §17 item 9.*

The transaction (`Phase3Transaction`, inherited by `Phase5Transaction`) uses **`.staging`** and `.phase3.lock` — with the leading dot — and leaves the empty `.staging` base behind after publication to `attempts/`. The post-run assertion named a dotless `staging`, so the suite would have failed the moment the authorized dry run ran.

The contract now names `.staging`, and asserts the transaction's own `staging_base.name` so the expectation cannot drift from the implementation again.

Validity is proved in the three required states, **without any real dry run**:

1. **Uncommitted** — the Phase-5 root does not exist; the contract holds.
2. **Simulated committed** — the four Phase-5 sources present and unmodified, which is what a commit makes true of the working tree; the contract holds.
3. **After a SYNTHETIC completed dry-run attempt** — a real `Phase5Transaction` stages the full committed artifact set plus a manifest and publishes to `attempts/…_PHASE_5_DRY_RUN_COMPLETE`; the contract still holds, the empty `.staging` base is present and allowed, and a subsequent `finish("PHASE_5_COMPLETE")` is still refused.

---

## 13. Fix 10 — working-set reconciliation

Executed as Step 0 (§3). The manager's exact inventory is restored, accepted bundles are untouched, and a test now guards the inventory permanently.

---

## 14. Statistical and package preservation

**No statistical change.** θ̂, bounds, pins, parameter identities, the 47/37/35 dimensions, the accepted Hessian bread, the household-cluster meat, the covariance construction, the finite-sample correction `1555/1520`, the certified `κ_BE = 6.0424e-12`, every T-/W- gate formula and every warning threshold are untouched. The only tolerance *discussed* in this cycle is the CSV-rendering comparator of fix 8, whose value did not move and which gates nothing.

**No package change.** `dclaborsupply-monorepo` is clean at `27756a06ea189339aa82915ed2124628afed20eb`, equal to the MNL gitlink. No package source, test or metadata was read-write touched; the likelihood is still reached only through `build_jax_singles_ll(..., per_group=True)` and no loader or likelihood logic is duplicated.

**No forbidden route.** No optimizer, no Hessian recomputation, no welfare, decomposition, synthetic recovery, EUROMOD or notebook path. No commit. No full 1,555-household scoring and no real dry run were performed at any point in this cycle.

---

## 15. Test results

All runs with bytecode and pytest-cache generation disabled.

| Run | Result |
| --- | --- |
| Phase-5 suite, run 1 | **96 passed** in 16.83 s |
| Phase-5 suite, run 2 | **96 passed** in 16.30 s |
| Critical authorization/custody/reparse subset × 10 | **21 passed, 75 deselected** on every one of the ten runs (3.85–3.98 s) |
| Whole repository, attempt-writing tests deselected | **156 passed, 2 deselected** in 29.73 s |

Fifteen new `test_c2_*` tests cover the ten groups behaviourally, not by source string where behaviour is testable: forged-record refusal and binding mismatch; no route skipping reauthorization; junction rejection at the store contract and at every publication endpoint; unbound and disagreeing embeddings refused; frozen pre-digests for every consumed input; exclusive member writes; truthful stopped inventory after a simulated post-write fault; recursive locator redaction with a firing negative assertion; the comparator policy on both sides of unity and at zero; the `.staging` contract; the three-state lifecycle; and the working-set inventory.

**Deselections.** `test_29` and `test_42` of the Phase-3 suite both write production attempt bundles into the accepted output tree, which would dirty the worktree — a charter §15 halt and the very defect Step 0 reconciled. `test_42` additionally fails at HEAD for a pre-existing reason unrelated to Phase 5: it asserts `phase4_curvature_v1/complete` does not exist, but that directory is the accepted Phase-4 bundle committed at the numerical anchor `982c522`. This is recorded, not fixed; TEST-42 remains logically separate per review v2 §15.

---

## 16. Artifact integrity

| Object | SHA-256 | State |
| --- | --- | --- |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | rehashes exactly |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | rehashes exactly |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | rehashes exactly |
| Review v1 | `b71a0b5b0ad74aecdf7f16133339d3ce642be8c84f9b892829a8f38fea37a4b5` | **byte-identical** |
| Review v2 | `48eae5ebbfd5fbeeb8527a4e75cb82f925dbe272342b84dd6a8e951241a3465d` | **byte-identical** |

Remediated files, all uncommitted:

| Path | SHA-256 | Lines |
| --- | --- | --- |
| `scripts/p2a/phase5_inference.py` | `5875feed03dea9f8dd8ac73a2bcd7dd7155ea8fc92b8bf81cc6ec39898e68482` | 3179 |
| `scripts/p2a/run_p2a_phase5_inference.py` | `baa95d7f6dff9aaf74e2a898d932936835ddf84ecb1870b2647a9317104b4bb5` | 2187 |
| `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | `2c9b4f0593853e4378ab562c90938217639429d7029afab974dc3e6ddd33b27b` | 87 |
| `tests/p2a/test_p2a_regionlive_phase5_inference.py` | `ae6f37c1c398c8a38dcde9c4ade6442842b3324d1c7d5ddc86f2c4fd99e0970e` | 2929 |
| `.gitignore` (modified) | `09e1945563b082d75f63f18f7c9164be4a4c84f407dc06bffc66634d3b5503d5` | 59 |
| `tests/p2a/test_p2a_regionlive_phase3_safety.py` (modified, TEST-42 scope) | `304ca86a185e2264278976c93c2a060654fb246fbac427074e5cb53160ebc30e` | 1773 |

Other checks: `git diff --check` returned no error. No `phase5_inference_v1/` root exists, so no `complete/` exists anywhere. The restricted store's `staging/` and `published/` are both **empty**; no household-level score bytes exist. No raw locator appears in any commit-eligible file.

---

## 17. Residual warnings

1. **No institutional backup for the restricted store.** Carried forward from review v2 §17: the store is PI-retained on a local access-controlled volume with no institutional backup. The deputy ruled this sufficient for the implementation review and one dry run; confirmation may be required before a production real run. Recorded verbatim in the config and propagated into the manifest custody block. Operational limitation, not a code defect.
2. **`test_42` fails at HEAD for a pre-existing, unrelated reason** (§15). Belongs to the separate TEST-42 commit scope.
3. **Review v3 does not exist yet**, so the dry run cannot start. This is the intended fail-closed state, not a defect.
4. **`_phase5_evaluate` end-to-end remains unexercised** — that is the full dry run, forbidden at this stage. Its constituent helpers are unit-tested, its contract is integration-tested against the real accepted state, and the orchestration around it is covered by the synthetic fixture.
5. **Manager confirmation still outstanding** on the three interpretations carried from implementation report v1 §7 (A-2 bundle membership under restricted custody, A-3 `phase5_score_row_index.csv` classified restricted, A-4 the W-2 weakest-direction reading). None was altered in this cycle.

---

## 18. Whether the final exact-state review may begin

**Yes.** All ten correction groups are implemented; the working set is exactly the manager's inventory; the no-full-score suite is green and repeatable; accepted artifacts, both worktrees and the package boundary are intact; reviews v1 and v2 are preserved byte-identical; and no commit, dry run or real run occurred.

The reviewer should note that the runner now binds to `FR_P2a_region_live_phase5_code_review_v3.md` with first heading `# 1. Phase-5 review-v3 verdict` and exactly one `**FINAL VERDICT: APPROVE**` line in the first section. Only that document, at that path, with that heading and that verdict, can authorize the single dry run.

---

## 19. Immediate next action

Return this report and both worktree statuses to the **Goal 1 Manager**. Commission the final independent exact-state review (Codex, read-only), producing `docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v3.md` in the form above. On APPROVE: the exact-state commit (I-5), then the single authorized full dry run (I-6). TEST-42 and its housekeeping report remain a separate commit scope. The production real run remains refused by construction and is the deputy programme director's decision alone.

**FINAL VERDICT: READY FOR FINAL EXACT-STATE REVIEW**
