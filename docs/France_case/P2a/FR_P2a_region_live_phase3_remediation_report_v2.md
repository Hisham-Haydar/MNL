# FR P2a Region-Live — Phase-3 Remediation Report — v2

Date: 2026-07-24. Remediates the review-v2 **REJECT**
(`FR_P2a_region_live_phase3_code_review_v2.md`, §20 residuals + §21 required fixes; task
decisions A–J). No real Phase 3, no optimizer, no EUROMOD, no notebook execution; nothing
committed; historical reports/reviews preserved unchanged.

## 1. Remediation-v2 verdict

**READY FOR THIRD INDEPENDENT REVIEW.** Both open review-v2 defects (structural input
provenance, Q8/Q9; incomplete fake-optimizer coverage, Q22; bundle completeness, Q16) are
closed. 34/34 safety tests pass; Phase 1–2 regression and canonical Phase-3 dry-run pass;
zero pre-existing evidence files changed.

## 2. Review-v2 defects addressed

Q8 → decision A (exact label↔runtime-path contract, §5). Q9 → immutable-mapping recheck
(§5/§11 of this report). `SELF` tautology → decision B external authorization (§6).
Q16 → decision F bundle assertion (§12). Q22 → decision E integration suite (§9–§11, §16).
Plus C (constants, §7), D (package identity, §8), G (optimizer_called timing, §13),
H (lock-before-migration, §14), I (phase metadata, §15). Nothing narrowed or bypassed.

## 3. Files inspected

All ten binding docs including review v2; runner; config; tests; the imported
dclaborsupply modules (`spec.parser`, `data.loader`, `likelihood.engine_jax`); the full
git diff and the Phase-3 attempt layout.

## 4. Files modified

Only the three authorized files: runner (`run_p2a_regionlive_rebuild.py`), config
(`p2a_regionlive_rebuild_v1.yaml`), tests (`test_p2a_regionlive_phase3_safety.py`).
Created: this report. Unchanged: verify script, notebooks, monorepo (clean), certified
baseline, thetas, Phase 1–2 evidence, all four historical Phase-3 documents.

## 5. Exact runtime-path authentication

`_phase3_runtime_paths()` is the immutable code-level label→path map for exactly the ten
required labels, built only from `MNL_ROOT`/`CANONICAL_REGIONLIVE_ROOT`/`CANONICAL_STEM` —
never from YAML. `_authenticate_inputs` requires: YAML key set == the ten labels exactly
(no missing/extra); every configured path resolves to the independently constructed
runtime path (`path_identity_ok`); file existence; hash equality against the accepted
digest. Per-input records persist label, runtime path, configured path, path_identity_ok,
expected, actual, hash_ok. `phase3_runner_script` and `phase3_config_self` are **removed**
from the table (config note documents why); script/config/test identity moved to the
external authorization (§6). The post-optimization recheck recomputes the **same immutable
mapping** (not the YAML) and compares post ↔ pre ↔ accepted. Tests 17 and 34.

## 6. External execution authorization

`sha256: SELF` is gone. Real Phase 3 requires `--authorization <absolute-json-path>`
validating the `p2a_phase3_execution_authorization_v1` schema: status APPROVED; all ten
fields; 40/64-hex formats; current MNL HEAD == `approved_mnl_commit`; MNL tracked tree
clean; runner/config/safety-test hashes == approved values; the approved review-v3 file
exists, hash-matches, and its verdict head contains APPROVE (and not REJECT). All verified
**before** the production lock. The authorization file was **not** created here (it exists
only after third-review APPROVE + commit) and is never part of the result bundle. Dry-runs
run without it and report `authorization_status: AWAITING_POST_REVIEW_AUTHORIZATION`,
`execution_ready: false` (verified live, §18). Test 31 covers missing/relative/
wrong-schema refusals; test seams may simulate post-auth flows only on non-production
roots — the production CLI cannot bypass the check.

## 7. Safety-critical constant validation

`PHASE3_SAFETY_CONSTANTS` (target 19053.46553160094; tolerances 1e-4/1e-9/1e-2/1e-5;
47/37/35/10; 1555 households; 101 alternatives; the at-bound tuple; L-BFGS-B with exactly
maxiter 5000 / maxcor 30 / ftol 1e-15 / gtol 1e-10) is validated against the YAML by
`_validate_safety_constants` at the top of the contract; any deviation is a
pre-optimization STOP (test 33; optimizer block exactness re-checked via
`_validate_optimizer_contract`, test 10).

## 8. Package source identity

`_verify_package_identity` asserts: nested repo is exactly `MNL_ROOT/dclaborsupply-monorepo`;
nested tracked tree clean; MNL gitlink at HEAD equals the nested HEAD; the imported
`spec.parser`, `data.loader`, `likelihood.engine_jax` `__file__` paths resolve beneath the
nested tree; with an authorization present, nested HEAD must equal
`approved_dclaborsupply_commit`. Records nested HEAD, gitlink, dirty status, module paths,
`module_path_ok`, `package_identity_ok`; any mismatch is a pre-optimization STOP. The
production dry-run ran the real verifier (`package_identity_ok: true` in the live
manifest); tests inject a synthetic verifier only through the private seam.

## 9. Fake-minimizer integration

The suite now drives the **real `_phase3_estimate`** through the `minimize_fn` seam with an
asserting `FakeMin`: 37-element x0; 37 bounds; `jac=True`; method L-BFGS-B; exact options;
objective sign (+negLL); gradient sign and free-order identity (unit perturbation of a free
coordinate moves value by +0.5 and gradient[k] to +1); expansion identity through the value
function. scipy.optimize is never imported (module guard still enforced).

## 10. Actual parameter ordering tests

The integration fixture loads the **certified spec's real 47-name order**; test 20 asserts
the true interleaved pin positions `[10..17, 31, 32]`, free-name order equals the
pins-removed certified order, and all ten pins bitwise-preserved in the final theta. No
synthetic pins-first ordering is used for integration.

## 11. Post-call mutation tests

Test 27 mutates an authenticated input **during** the fake optimizer call: the recheck
(immutable mapping) detects it, returns S-8 STOPPED, and **nothing** is written to staging;
test 28 routes the same through `run_phase3` and verifies no publication. Test 17 covers
pre/post hash-change detection including the missing-label case.

## 12. Complete-bundle assertion

Before a successful publication, staging must contain exactly the three result artifacts
(console is then written by finalize); after the manifest is written, the staging set must
be exactly the four artifacts + manifest or publication raises. Missing-artifact,
unexpected-artifact, and complete-set cases are tested (test 29: incomplete → refused,
extra file → refused, exact set → published with the exact five files); manifest remains
excluded from its own hash dictionary (test 15).

## 13. Optimizer invocation state

`optimizer_called` is set **immediately before** the minimizer call via the
`mark_optimizer_called` callback; a raising minimizer yields a STOPPED attempt whose
manifest and console persist `optimizer_called: true` plus the exception type/message,
with `complete/` untouched (tests 22 and 28).

## 14. Lock and migration ordering

`Phase3Transaction.acquire` now: creates the lock (O_CREAT|O_EXCL) **first**, then creates
`attempts/`, performs the one-time legacy migration **under the lock**, then creates
staging. Real-run order overall: canonical CLI validation → external authorization →
lock → staging → migration → attempt. Test 30: with a held lock, the run refuses, no
legacy file moves, no attempts/ is created.

## 15. Phase metadata

Config now states `run.phases_implemented: [1, 2, 3]`, `phase3_supported: true`,
`phase3_execution_authorized: false`, `phases_4_to_8_supported: false`. The live dry-run
manifest reports `optimizer_called: false`, `authorization_status:
AWAITING_POST_REVIEW_AUTHORIZATION`, `execution_ready: false` (test 32 + §18).

## 16. Unit and integration tests

**34/34 PASS** (pytest 8.4.2, ~5 s): the original 18 (test 17 rewritten for the immutable
mapping) plus 16 new integration/authorization/bundle/lock tests covering every decision-E
item (success route; exact optimizer inputs; expansion; gradient projection; pins bitwise;
interleaved ordering; success=False; raise-after-invocation; target high **and** low;
gradient gate; G-16; unexpected bound hit; expected-set pass; mutation during call; S-8
recheck; no-publication-after-failure; optimizer_called-on-raise) and decisions F/H
(bundle refusals/pass; lock contention without migration). Iterations during hardening
fixed two real issues the tests exposed: float32 default in the test process (x64 now
forced) and the finalize completeness/console ordering.

## 17. Phase 1–2 regression

Scratch-root `--phase 2 --dry-run`: exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`, stem regenerated
**byte-identical** (`8bf083ce…`). Accepted evidence untouched.

## 18. Phase-3 dry-run

Canonical command: exit 0, `PHASE_3_DRY_RUN_COMPLETE`; contract dev 0.00e+00; new attempt
bundle under `attempts/`; manifest: `authorization_status: AWAITING_POST_REVIEW_
AUTHORIZATION`, `execution_ready: false`, `optimizer_called: false`,
`package_identity_ok: true`; `complete/` absent; lock released.

## 19. Prohibited-operation audit

No real optimizer (guarded + tested), no EUROMOD, no draws, no Phase 4+ computation, no
notebook/package/baseline/theta change; `--phase 4` refused (exit 2); sweep: **0 changed
pre-existing files** under `region_live_v1/`; monorepo clean at `27756a0`.

## 20. Git diff summary

```
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
 M scripts/p2a/run_p2a_regionlive_rebuild.py
 M tests/p2a/test_p2a_regionlive_phase3_safety.py
?? outputs/.../phase3_estimation_v1/attempts/2026…_dryrun_PHASE_3_DRY_RUN_COMPLETE/
?? docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v2.md
```

Nothing committed.

## 21. Residual warnings

(a) The config file itself still has no pre-registered digest — by design: its identity is
now controlled by `approved_config_sha256` in the external authorization + the clean-HEAD
requirement, which is the review-v2-prescribed replacement for the SELF tautology. (b) The
module-presence guard remains defense-in-depth, as both prior reviews noted. (c) The
production dry-run exercises the real package-identity verifier, which requires the gitlink
to match the nested HEAD — a deliberately strict condition operators must maintain.

## 22. Whether third independent review may begin

**YES** — all §20/§21 items are implemented with live and test evidence.

## 23. Immediate next action

Third independent static review. On APPROVE: commit the reviewed implementation, create the
external `p2a_phase3_execution_authorization_v1` file from the approved commit/hashes
(outside this task), then run the first real Phase 3 with `--authorization`. Phases 4–8
remain manager-gated.

**FINAL VERDICT: READY FOR THIRD INDEPENDENT REVIEW** (no real Phase 3; no authorization
file created; nothing committed).
