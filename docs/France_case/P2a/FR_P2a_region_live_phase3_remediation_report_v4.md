# FR P2a Region-Live — Phase-3 Remediation Report — v4

Date: 2026-07-25. Closes exactly the review-v4 **REJECT** residuals
(`FR_P2a_region_live_phase3_code_review_v4.md` §17–18; task decisions A–H). No estimator
redesign; no real Phase 3; no optimizer; no authorization file; no notebook/package/
baseline/evidence change; nothing committed; all prior reports/reviews immutable.

## 1. Remediation-v4 verdict

**READY FOR FIFTH INDEPENDENT REVIEW.** Every §17 defect and §18 fix is closed, the full
safety suite passes (51 passed, 1 platform skip), `git diff --check` exits 0, the Phase 1–2
regression and canonical Phase-3 dry-run pass, and an independent three-lens adversarial
verification workflow over the diff returned **zero bypass findings**, with its three low
(cosmetic/coverage) findings also fixed and re-validated in this same remediation.

## 2. Review-v4 defects addressed

§17.1 high (injectable canonical orchestrator) → decision A (§5). §17.2 high
(`_numpy_primitives` gap) + §17.5 (ignored source invisible) → decision D (§8).
§17.3 (helper accepts genuine components) → decision B (§6). §17.4 (authorization
location) → decision C (§7). §17.6 (map reconstruction) → decision E (§9). §17.7 (G-16
boundaries/tautology) → decision F (§10). §17.8 (stale review metadata) → decision G
(§11). §18.8 → §20–21.

## 3. Files inspected

All eleven binding docs including review v4 §17–18; runner/config/tests; the complete git
state and diff; every dclaborsupply module on the Phase-3 route (the ten-module inventory
plus loaded transitive `dclaborsupply.*`).

## 4. Files modified

`scripts/p2a/run_p2a_regionlive_rebuild.py` and
`tests/p2a/test_p2a_regionlive_phase3_safety.py` (+670/−196 combined). The config needed
no v4 change (verified by the stale-metadata lens: its authorization comments are
version-generic and `phases_implemented: [1,2,3]` / `phase3_execution_authorized: false`
already hold). Created: this report.

## 5. Production orchestration closure

The generic `_phase3_orchestrate` is **deleted** (`hasattr` false, grep-verified). The new
`_phase3_orchestrate_production(args, cfg, authorization_record)` exposes no injectable
root/contract/estimator/minimizer/verifier: it hard-uses `CANONICAL_PHASE3_ROOT`,
re-checks `CANONICAL_PHASE3_CONFIG`, and calls the genuine `_phase3_contract`,
`_phase3_estimate` (with the real minimizer route) and `_verify_package_identity` inline.
A non-dry call refuses — **before any lock or transaction is constructed** — unless the
supplied record has `verified is True` **and** `execution_ready is True`. Dry-runs remain
non-optimizing and unauthorized. The test path is structurally separate
(`_run_phase3_test_attempt` → `_phase3_attempt_test_body`), never calls the production
orchestrator, and both layers refuse (resolved `is_relative_to`) roots at/under the
canonical Phase-3 root, the region-live root, `MNL/outputs`, **the entire MNL worktree,
and the nested monorepo worktree**. Shared finalize/manifest helpers take only the
already-validated transaction — no function-injection surface. Verified by introspection
+ execution tests (test 45) and the adversarial bypass lens (zero findings).

## 6. Test-double isolation

`_validate_test_double` requires `__phase3_test_double__ is True` on every injected
contract/estimator/minimizer/identity component and — checked **before** the marker —
rejects identity with `_phase3_contract`, `_phase3_estimate`, `_verify_package_identity`,
`_phase3_orchestrate_production`, `run_phase3`, and any callable whose module/qualname
identifies the real SciPy minimizer. Test 46 proves each genuine component is refused even
with the marker attached, the scipy-identifying stub is refused, and unmarked callables
are refused (no scipy import occurs in tests).

## 7. Authorization-location enforcement

The verifier resolves the authorization path and rejects it when equal to or beneath the
MNL or nested worktree — by pure resolved ancestry, before and independent of any Git
status/ignore logic. Test 47: ordinary in-worktree, **ignored** in-worktree,
nested-worktree, and inside-resolving symlink (where supported) all refused with the
location message; a valid absolute outside path is structurally accepted
(`verified/execution_ready` true).

## 8. Complete package-module authentication

`REQUIRED_PACKAGE_MODULES` pins the exact ten modules (package initializers, `models`,
`data.loader`, `spec.parser`, `likelihood.index`, `likelihood.engine_jax`,
`likelihood._numpy_primitives`), imported explicitly and unioned with every other loaded
`dclaborsupply.*` module. Per module: `__file__` required; resolved ancestry under
`packages/dclaborsupply/src`; nested-repo-relative path derived; **tracked blob required
at the reference commit** (the approved nested commit when authorized, nested HEAD for
dry-runs, with gitlink==HEAD enforced); committed blob read via Git; equality gated on
`git hash-object --path` reproducing the tracked blob id (Git's own canonical identity —
raw-byte comparison false-fails on autocrlf checkouts, a real effect found live on two
CRLF-checked-out modules; raw SHA-256s of blob and worktree are still persisted per
module together with path, relative path, blob id and equality). This rejects sibling
paths, outside-tree symlinks, ignored/untracked substitutes (no blob), modified sources
(blob mismatch), and missing files. Test 48 verifies the full inventory live and
reproduces the review-v4 outside-tree `_numpy_primitives` substitution (refused); test 49
proves untracked-substitute and modified-vs-blob refusals on a temporary repository.

## 9. Single runtime-map lifecycle

The production orchestrator builds `_phase3_runtime_paths()` **once per attempt**,
fingerprints it (`_runtime_map_fingerprint`, persisted in the manifest), and threads the
same object through alias validation, `_authenticate_inputs`, every contract read, the
returned context (`ctx["rtmap"]` + fingerprint), `_phase3_estimate`, and both
`_recheck_inputs` call sites; the estimate re-fingerprints before the recheck and stops
S-8 on drift, persisting pre/post fingerprints. Test 50 (changing-factory: zero factory
calls during estimate; fingerprints equal) and new test 52 (poisoned factory: the full
real contract passes end-to-end using only the injected map, `ctx["rtmap"] is rtmap`)
prove both legs.

## 10. G-16 exact-boundary closure

Test 43 rewritten: exactly `lo − ε` and `hi + ε` pass; `np.nextafter` one ULP below/above
fails; every case asserts the per-row `in_bounds` **and** the aggregate
`gates["g16_inbounds_ok"] == expect_ok` directly — the tautological aggregate assertion is
gone (grep-verified by the stale lens).

## 11. Review-v5 metadata

`CANONICAL_APPROVED_REVIEW_REL` now binds
`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v5.md`; CLI help, error
messages, and the schema comment state that only the canonical review-v5 tracked blob
with one exact `**FINAL VERDICT: APPROVE**` line in its first verdict section authorizes
execution; every "third-review"/review-v4-authorizes implication is removed (the one
straggler comment found by the verification workflow was fixed). Test 51 asserts the v5
constant and refuses a v4 `approved_review_path`.

## 12. Safety-test additions

New/rewritten: tests 43 (boundaries), 45 (orchestrator surface + pre-lock production
refusals + test-body root refusal), 46 (genuine-double rejections), 47 (authorization
location battery), 48–49 (module inventory + blob identity + substitutions), 50/52
(single-map threading, both legs), 51 (review-v5 binding); marker migration across every
double; helper-root refusals extended to repository paths. All previously passing tests
retained.

## 13. Full safety-suite result

`pytest -q` → **51 passed, 1 skipped** (symlink privilege; the enforcement is
resolve-based and covered by traversal cases), exit 0. No test touches the real
optimizer, estimation data mutation, or any production output path.

## 14. Phase 1–2 regression

Scratch-root `--phase 2 --dry-run`: exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`, regenerated
stem **byte-identical** (`8bf083ce…`) once more.

## 15. Phase-3 dry-run

Canonical command (run three times across the iteration, final run on the final code):
exit 0, `PHASE_3_DRY_RUN_COMPLETE`; manifest: `authorization_status:
AWAITING_POST_REVIEW_AUTHORIZATION`, `execution_ready: false`, `optimizer_called: false`,
`package_identity_ok: true`, `rtmap_fingerprint` persisted; `complete/` absent; lock
released; contract dev 0.00e+00.

## 16. Prohibited-operation audit

No real optimizer/EUROMOD/draws/Hessian/inference/post-estimation/welfare/synthetic
recovery/notebook execution. `--phase 4` refused (exit 2). Sweep: **0 changed
pre-existing files** under `region_live_v1/` (only new dry-run attempt bundles). Nested
monorepo clean; certified baseline, thetas, and Phase 1–2 evidence untouched. An
independent 3-agent adversarial workflow (bypass / coverage / stale lenses) audited the
diff: zero bypass findings; all 25 mandated closure items mapped to concrete tests; the
three low findings it raised (stale comment, dead `-uno` helper, untested contract-side
map leg) were fixed and re-validated in this remediation.

## 17. Git-state and predecessor commit

HEAD at validation: **`6dda418`** (the review-v4 commit). Commit
**`7c1546c52b423f881c103d8662226f272ba5701d` is retained, un-reset and un-amended, as the
rejected predecessor state**; this remediation exists solely as an uncommitted diff on
top, awaiting the fifth review.

## 18. Git diff summary

```
 M scripts/p2a/run_p2a_regionlive_rebuild.py      | 575 ++++++++++++++-------
 M tests/p2a/test_p2a_regionlive_phase3_safety.py | 291 +++++++++++-
 ?? outputs/.../phase3_estimation_v1/attempts/…dryrun_PHASE_3_DRY_RUN_COMPLETE/ (validation attempts)
 ?? docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v4.md
```

`git diff --check`: exit 0. Nothing committed.

## 19. Residual warnings

(a) Symlink tests skip where creation is unprivileged (enforcement remains resolve-based).
(b) Blob equality is Git-canonical (`hash-object --path`) rather than raw bytes — required
for correctness on autocrlf checkouts and equally strict against real modification; raw
hashes are persisted alongside for audit. (c) Validation dry-run attempt bundles
accumulate under `attempts/` per the never-delete discipline.

## 20. Whether fifth independent review may begin

**YES** — all §17/§18 items closed with introspection, execution, and adversarial-audit
evidence on a clean `git diff --check`.

## 21. Immediate next action

Fifth independent static review. On one exact `**FINAL VERDICT: APPROVE**` in the
canonical review-v5 file: commit the reviewed state, create the external authorization
**outside both worktrees** from the approved commit/blob hashes, then execute the first
real Phase 3 with `--authorization`. Phases 4–8 remain manager-gated.

**FINAL VERDICT: READY FOR FIFTH INDEPENDENT REVIEW** (no real Phase 3; no authorization
file; nothing committed).
