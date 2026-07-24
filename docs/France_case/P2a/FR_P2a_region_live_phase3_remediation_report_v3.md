# FR P2a Region-Live — Phase-3 Remediation Report — v3

Date: 2026-07-24. Narrowly targeted remediation of the review-v3 **REJECT**
(`FR_P2a_region_live_phase3_code_review_v3.md` §20 residuals / §21 required fixes; task
decisions A–H). No architecture redesign; no real Phase 3; no optimizer; no authorization
file created; no notebook/package/baseline/evidence change; nothing committed. Prior
reports and reviews preserved unchanged.

## 1. Remediation-v3 verdict

**READY FOR FOURTH INDEPENDENT REVIEW.** All §20/§21 items are closed: the immutable
runtime map is now the sole source of every Phase-3 file open with alias-identity
enforcement; the canonical config path is required at three layers; the `_txn_root`
production bypass is eliminated by a seam-free production entrypoint plus a
production-tree-refusing private test helper; the two remaining gate controls are pinned
in code; authorization binds to the exact tracked review-v4 blob with an exactly parsed
APPROVE and full `-uall` cleanliness on both repos; package containment uses resolved
`Path.is_relative_to` ancestry. 43/43 runnable safety tests pass (1 platform skip);
`git diff --check` exits 0; Phase 1–2 regression and the canonical Phase-3 dry-run pass.

## 2. Review-v3 defects addressed

§20.1 → decision A+B (§5–6). §20.2 → decision C (§7). §20.3 → decision D (§8).
§20.4 → decision E+F (§9–10). §20.5 → decision G (§11). §20.6 → decision H (§12–15).
Every §21 fix (1–7) implemented; fix 8 (fourth review) is §22–23.

## 3. Files inspected

All ten binding documents including review v3 (§20–21 in full, verdict/§1 head); the
runner, config, and test suite; the current git diff; the dclaborsupply modules imported
by the runner (`dclaborsupply`, `spec.parser`, `data.loader`, `likelihood.engine_jax`).

## 4. Files modified

Only the three authorized files (`git diff --stat`: runner +351 lines changed, tests
+345, config +6). Created: this report. Untouched: verify script, notebooks,
`dclaborsupply-monorepo` (clean), certified baseline, thetas, Phase 1–2 evidence, and all
prior Phase-3 reports/reviews.

## 5. Consumed-path closure

`_phase3_contract` now takes ONE `_phase3_runtime_paths()` map and opens **every**
consumed file through it: certified spec (`EstimationSpec.from_yaml(rtmap[…])`),
warm-start theta (`load_custom_initial_values(rtmap[…])`), stored start theta
(`pd.read_csv(rtmap[…])`), stem parquet + mnlmeta, Phase 1–2 manifest and dry-run report —
no `out.path(...)`/`MNL_ROOT/cfg[...]` opens remain in the Phase-3 route. The four
retained legacy aliases (`certified_spec.yaml`, `warm_start.theta_csv`,
`phase3.start_theta.csv`, `stored_region_live_theta.v1_csv`) must each resolve exactly to
their runtime-map path before any read (`alias-identity` STOP otherwise); the resolution
evidence is persisted. Test 35 mutates each alias independently and proves refusal.
(A variable-name collision between the runtime map and the round-trip dict — both `rt` —
was caught by the live dry-run and fixed by renaming the round-trip dict `rtrip`.)

## 6. Canonical config enforcement

`CANONICAL_PHASE3_CONFIG` is enforced by resolved-path equality in `main` (before
dispatch), in `run_phase3`, and in `_verify_external_authorization` (which also keeps the
hash check). Test 36: canonical passes (the live dry-run), an identical copy elsewhere
fails, traversal resolving elsewhere fails, symlink-resolving-elsewhere fails (skipped on
this host — symlink privilege unavailable; guarded with `pytest.skip`).

## 7. Production and test-seam separation

`run_phase3(args, cfg)` now has **no** injectable arguments (verified by
`inspect.signature` in test 37) and always uses the real contract, estimator, minimizer
route, package-identity verifier, and the canonical transaction root, requiring external
authorization for real runs. The private `_run_phase3_test_attempt` requires an explicit
test root + fake contract + fake estimator + fake minimizer + fake identity verifier + the
`i_am_a_private_test=True` marker, and refuses (resolved `is_relative_to`) any root equal
to or beneath `CANONICAL_PHASE3_ROOT`, `CANONICAL_REGIONLIVE_ROOT`, or `MNL_ROOT/outputs`.
Test 37 proves each refusal, each missing-component refusal, and the marker refusal.

## 8. Immutable target controls

`PHASE3_PREOPT_OBJECTIVE_TOL = 1e-4` and
`PHASE3_TARGET_MISMATCH_STATUS = "REVIEW_REQUIRED_TARGET_MISMATCH"` are code constants;
`_validate_safety_constants` requires YAML equality for both; `_phase3_post_gates` and
`_phase3_estimate` return only the constant (never a YAML value); the contract compares
the pre-optimization objective against the constant. Test 38: changing either YAML key is
refused; with a YAML status hacked to `PHASE_3_COMPLETE`, the returned status is still the
constant and `Phase3Transaction.finish` routes it to `attempts/` — `complete/` is never
created; both high and materially lower objectives covered (also end-to-end in §14).

## 9. Exact review authorization

`CANONICAL_APPROVED_REVIEW_REL` pins review v4. The verifier requires:
`approved_review_path` equal to that exact POSIX string; the resolved current path equal
to `MNL_ROOT/rel`; file existence; `git rev-parse <commit>:<path>` proving the blob is
tracked at the approved commit; SHA-256 of the **committed blob** equal to
`approved_review_sha256`; and the working-tree file byte-equal to that blob. The verdict
is parsed exactly: exactly one `**FINAL VERDICT: …**` line in the document, located in the
first section, equal to `**FINAL VERDICT: APPROVE**`; APPROVE AFTER FIXES, REJECT, prose
"APPROVE", and multiple/contradictory verdict lines are all refused. Tests 39–40 cover
every case on temporary git repositories via the private `_repo_root`/`_nested_root`
seams (the real review-v4 file does not exist and is not used).

## 10. Git cleanliness enforcement

`_git_fully_clean` uses `git status --porcelain --untracked-files=all` (never `-uno`) and
is required for **both** MNL and the nested repo in the authorization check (and the
nested repo in package identity). The config header and the verifier message document
that the authorization JSON must reside **outside** both worktrees. Test 41: tracked
modification fails, staged fails, untracked fails, nested-untracked fails, ignored files
pass, fully clean passes.

## 11. Package-path ancestry

`PACKAGE_SOURCE_ROOT = …/dclaborsupply-monorepo/packages/dclaborsupply/src`;
`_module_ancestry_ok` uses resolved `Path.is_relative_to` (no substring anywhere) over the
top-level `dclaborsupply` package plus `spec.parser`, `data.loader`,
`likelihood.engine_jax` — the complete set of dclaborsupply modules directly imported by
the Phase-3 contract/objective route. Missing `__file__` fails. Resolved paths and
per-module ancestry results are persisted. Test 42: genuine ancestry passes (live
verification), the `dclaborsupply-monorepo_evil` sibling-substring attack is refused, and
missing-`__file__` is refused.

## 12. Remaining test closure

All 25 mandated items are covered: aliases (35), canonical config (36), seam separation +
root/descendant/outputs refusals + missing fakes + production signature (37), immutable
tolerance/status + no-success-publication (38), exact review path/verdict/AFTER-FIXES/
tracked-blob/committed-hash (39–40), MNL tracked/staged/untracked + nested untracked +
ignored-pass (41), ancestry pass + sibling attack (42), G-16 boundaries (43),
high/low target publication (44). All previously passing tests retained (migrated to the
private helper via a thin adapter); unused setup removed (test 9's `bad`, test 34's
`good`).

## 13. G-16 boundary tests

Test 43 checks a free parameter at the exact lower bound, exact upper bound, 0.5e-9
inside each bound (in-bounds true), and 2e-9 outside each bound (in-bounds false),
asserting the per-row `in_bounds` and `g16_inbounds_ok` at the pinned ε = 1e-9.

## 14. Target-publication tests

Test 44 runs the real `_phase3_estimate` through the fake-minimizer route with the
objective shifted +1e-3 and −1e-3: both return exit code 4 with the immutable
`REVIEW_REQUIRED_TARGET_MISMATCH`, publish only to `attempts/…_REVIEW_REQUIRED_TARGET_
MISMATCH/`, and `complete/` never exists.

## 15. Header and whitespace repairs

Runner docstring now states: Phases 1–3 implemented; Phase-3 execution requires the
post-review external authorization; Phases 4–8 unsupported/refused. Config header
likewise (plus the authorization-file-location note). The test file is normalized
(trailing whitespace stripped, single EOF newline): **`git diff --check` exits 0**.

**Errata to remediation report v2 (recorded here; v2 preserved unchanged):** (a) v2 §17's
claim that the suite already exercised fake objectives/optimizers through the estimate
route was inaccurate — that coverage exists only as of this remediation (review v3 §6);
(b) v2's description of test 28 overstated it as a full fake-optimizer estimate test.

## 16. Full safety-suite result

`python -m pytest tests/p2a/test_p2a_regionlive_phase3_safety.py -q` →
**43 passed, 1 skipped** (symlink privilege unavailable on this host), exit 0, ~11 s.
No real optimizer, estimation data path, or production write in any test.

## 17. Phase 1–2 regression

Scratch-root `--phase 2 --dry-run`: exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`, regenerated
stem hash `8bf083ce…` — byte-identical again.

## 18. Phase-3 dry-run

Canonical command: exit 0, `PHASE_3_DRY_RUN_COMPLETE`; contract `negLL(start)` dev
0.00e+00; manifest: `authorization_status: AWAITING_POST_REVIEW_AUTHORIZATION`,
`execution_ready: false`, `optimizer_called: false`, `package_identity_ok: true`;
`complete/` absent; lock released. Two intermediate STOPPED dry-run attempts from the
`rt`-collision debugging remain under `attempts/` as honest audit records (they altered
nothing outside the attempt directories).

## 19. Prohibited-operation audit

No real optimizer call anywhere (guards + tests); no EUROMOD/draws/Hessian/inference/
post-estimation/welfare/synthetic recovery; `--phase 4` refused (exit 2); sweep across
`region_live_v1/`: **0 changed pre-existing files** (only new attempt directories);
notebooks and `dclaborsupply-monorepo` untouched (nested `git status` clean); certified
baseline, thetas, and accepted evidence unchanged.

## 20. Git diff summary

```
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |   6 ±
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | 351 ±
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | 345 ±
?? outputs/.../phase3_estimation_v1/attempts/…dryrun_STOPPED/ (×2, debug audit)
?? outputs/.../phase3_estimation_v1/attempts/…dryrun_PHASE_3_DRY_RUN_COMPLETE/
?? docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v3.md
```

`git diff --check`: exit 0. Nothing committed.

## 21. Residual warnings

(a) The symlink-config refusal test skips where symlink creation is unprivileged
(Windows default) — the enforcement itself is resolve-based and covered by the traversal
case. (b) `_git_tracked_dirty` remains defined but unused after the `-uall` upgrade —
retained to avoid churn; a reviewer may delete it. (c) The two STOPPED debug attempts are
retained as audit records per the never-delete-attempts discipline.

## 22. Whether fourth independent review may begin

**YES** — all §20/§21 items closed with live and test evidence, on a clean
`git diff --check`.

## 23. Immediate next action

Fourth independent static review. On an exact `**FINAL VERDICT: APPROVE**` (as review
v4 at the canonical path): commit the reviewed state, create the external authorization
file **outside both worktrees** from the approved commit/blob hashes, then execute the
first real Phase 3 with `--authorization`. Phases 4–8 remain manager-gated.

**FINAL VERDICT: READY FOR FOURTH INDEPENDENT REVIEW** (no real Phase 3; no
authorization file; nothing committed).
