# FR P2a Region-Live — Phase-3 Remediation Report — v1

Date: 2026-07-24. Remediates the **REJECT** verdict of
`FR_P2a_region_live_phase3_code_review_v1.md` (§18 fixes 1–8, all binding). No real Phase-3
estimation was executed; no optimizer was invoked anywhere (production or tests). Nothing was
committed. The historical implementation report and rejected-review record are preserved
unchanged.

## 1. Remediation verdict

**READY FOR SECOND INDEPENDENT REVIEW.** All eight required fixes are implemented; 18/18
non-optimizing safety tests pass; the Phase 1–2 dry-run still passes with a byte-identical
regenerated stem; the canonical Phase-3 dry-run passes under the new transaction layout with
`optimizer_called: false`; zero pre-existing evidence files changed.

## 2. Rejected review addressed

| Review §18 fix | Where addressed |
|---|---|
| 1. Explicit 37↔47 mapping + round-trip/order/uniqueness/pin-bitwise tests | §8; tests 1–4 |
| 2. G-16 with ε=1e-9, persisted, S-3 stop | §10; tests 5–6 |
| 3. Hash every consumed file + post-optimization recheck | §11–12; test 17 |
| 4. Canonical root + exact subdirectory; test roots only behind non-production seams | §5; tests 8–9 |
| 5. Prior-success refusal; unique attempt staging; atomic publish | §6–7; tests 12–14 |
| 6. Exact accepted pin-name set + exact optimizer method/option-key set | §9, §13; tests 4, 10 |
| 7. Correct artifact hashing; complete console before replacement; no manifest self-hash | §7, §16; tests 15–16 |
| 8. Safe tests via fakes/dependency injection | §17; the whole suite |

No fix was bypassed, reinterpreted, or weakened; none was found inapplicable except the
single fixed-point impossibility documented in §11 (a config file cannot contain its own
hash), which is handled by recording + pre/post recheck instead.

## 3. Files inspected

All binding documents (decisions v2, plan v2, acceptance v1, implementation report v1,
code review v1, dry-run report v2); the runner, verify script, and config; the accepted
evidence set (`rebuild_manifest.json`, `dry_run_report.json`,
`pre_estimation_reload_verification.json`, stem mnlmeta); the dclaborsupply spec/loader/
JAX-likelihood/optimizer APIs referenced by the runner.

## 4. Files modified

Exactly the two authorized files: `scripts/p2a/run_p2a_regionlive_rebuild.py` (Phase-3
section fully rewritten; +~800/−370 net across both files) and
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+62: exact optimizer block,
`g16_inbounds_epsilon`, 12-entry `input_authentication`, `accepted_phase12_anchors`).
Created: `tests/p2a/test_p2a_regionlive_phase3_safety.py` (18 tests) and this report.
Unchanged: `verify_p2a_regionlive_reload.py`, both notebooks, `dclaborsupply-monorepo`
(clean), certified baseline, all thetas, all Phase 1–2 evidence, both historical Phase-3
documents.

## 5. Canonical path enforcement

Hard-coded constants `CANONICAL_REGIONLIVE_ROOT = MNL_ROOT/outputs/p2a_singles2016/
region_live_v1`, `CANONICAL_PHASE3_SUBDIR = phase3_estimation_v1`,
`CANONICAL_PHASE3_ROOT`, `CANONICAL_STEM`. The production CLI (`main → run_phase3` with no
underscore kwargs) refuses, before any write or lock: a resolved `--out` ≠ canonical root;
`run.output_root` ≠ canonical root; `phase3.output_subdir` ≠ `phase3_estimation_v1`. There
is no production test-root override; only underscore-private seams (`_txn_root`,
`_contract_fn`, `_estimate_fn`, `_minimize_fn`) exist for unit tests. Every Phase-3 write
goes through the transaction rooted at `CANONICAL_PHASE3_ROOT` (staging paths only).
Verified live: tests 8–9 (refusals leave zero filesystem traces).

## 6. Attempt and locking architecture

`Phase3Transaction` implements `.phase3.lock` (O_CREAT|O_EXCL exclusive creation; existing
lock → refusal with "manual inspection required"; never auto-deleted; removed only on a
normal controlled finish, left behind on crash as a fail-safe), `.staging/<attempt_id>/`
(attempt_id = UTC timestamp + pid + nanosecond suffix — a same-second collision found by
test 12 was fixed this way), `attempts/`, `complete/`. A real estimation refuses before the
contract if `complete/` exists (B.3, test 12); dry-runs and failed runs never touch
`complete/` (tests 11, 13). The pre-review loose dry-run files were migrated
**byte-preserved** (hash-verified) to `attempts/pre_review_dryrun_0_REJECTED_REVIEW/` and
are not classified as a successful result.

## 7. Transactional publication

Directory-level, not per-file: all five artifacts are written inside the unique staging
directory; on `PHASE_3_COMPLETE` (and only then, and only if `complete/` still does not
exist — rechecked inside finalize) the staging directory is atomically renamed to
`complete/`; every other status renames it to `attempts/<attempt_id>_<STATUS>/`.
Finalization order exactly per decision C: final status line appended to the in-memory
console → console written → theta/diagnostics/results written → per-artifact SHA-256 →
deterministic `bundle_sha256` over sorted `name:sha` pairs → manifest written **last** —
and the manifest is never in its own artifact-hash dictionary (tests 14–16).

## 8. Explicit 37-to-47 mapping

`build_phase3_parameter_map` / `project_full_to_free` / `expand_free_to_full` implement
decision D fully: 47 unique names, 10 unique pins equal to the accepted tuple, existence,
disjointness, union, 37 free; explicit integer index arrays; **the optimizer receives only
the ordered 37-vector with the 37 free bounds**; the package objective receives the
expanded 47-vector with the ten immutable pin values injected; the free gradient is the
projection of the full package gradient through the same indices. Exact round trips
(`project(expand(free)) == free`; template free-coordinate reproduction; pins bitwise) are
validated in the contract and persisted (`parameter_map` with names, indices, pin values,
round-trip results). Tests 1–3.

## 9. Pin-set validation

`ACCEPTED_PIN_NAMES` is an immutable ordered ten-name tuple in the runner; the YAML list
must equal it exactly including order; duplicates, omissions, extras, or reordering raise
StopRun (contract + `build_phase3_parameter_map`; test 4 covers duplicate, reordered, and
wrong-member cases).

## 10. G-16 in-bounds gate

`g16_inbounds_epsilon: 1.0e-9` added to config. After optimization, every one of the 37
free parameters must satisfy `lo − 1e-9 ≤ θ̂ ≤ hi + 1e-9`; per-parameter value, lb, ub,
distance-to-lower, distance-to-upper, and `in_bounds` are persisted in
`theta_estimated.csv` and the diagnostics; `g16_inbounds_ok` is persisted; any violation is
S-3 and prevents publication. Separately, the runner asserts non-bound free count == 35,
expected bound set == `{beta_l_age2_sm, beta_l_age2_sf}`, and detected final non-pin bound
set == that set exactly (tests 5–7).

## 11. Input authentication

`phase3.input_authentication` in the config lists all 12 consumed files with accepted
SHA-256 computed from the accepted PASS evidence on disk (unmodified): geometry parquet
`5bcf0e54…`, geometry meta `ff2d4422…`, stem parquet `8bf083ce…`, stem mnlmeta
`05be4030…`, certified YAML `492bcfa9…`, warm-start theta `c72e92b1…`, stored start theta
`930ef3aa…`, Phase 1–2 manifest `1ed3041f…`, dry-run report `ec50ea98…`, reload
verification `6f457de9…`, the current runner `efd2204a…`, and the config itself. The
config-self entry is the one fixed-point impossibility (a file cannot contain its own
hash): it is hashed and recorded in the contract evidence and rechecked pre/post instead.
The contract also verifies the Phase 1–2 manifest's recorded script/config hashes equal the
accepted anchors (`be11294b…` / `68d152e7…`) now in the config. Any mismatch → S-8 before
optimization. The canonical-stem/mnlmeta companionship and metadata fields are
hard-asserted (decision H).

## 12. Post-optimization input recheck

`_recheck_inputs` recomputes every consumed-input hash after optimization and before any
result write, comparing each to both the pre-optimization hash and the accepted hash; the
`input_recheck_after_optimization` table is persisted in the diagnostics and manifest; any
change → S-8, no result artifacts are written, and publication is prevented (test 17).

## 13. Optimizer-contract validation

`_validate_optimizer_contract` requires the YAML optimizer block keys to be exactly
`{method, options}`, `method == "L-BFGS-B"`, option-key set exactly
`{maxiter, maxcor, ftol, gtol}`, and values exactly `5000 / 30 / 1e-15 / 1e-10` (test 10).
The route/settings documentation moved to a sibling `optimizer_route_note` key. The direct
`scipy.optimize.minimize` route remains as authorized by the review (package objective
reused; wrapper cannot express `maxcor=30`), now driven on the 37-free vector.

## 14. Bound and gradient gates

Unchanged ratified values, now over the explicit mapping: bound-hit ε 1e-5 with the
derived-and-cross-checked expected set; `max|grad| < 1e-2` over exactly the 35 non-bound
free parameters (count asserted); pins bitwise-checked; two-sided objective gate with
`REVIEW_REQUIRED_TARGET_MISMATCH` (exit 4) on any material deviation.

## 15. Failure handling

Every caught failure produces a STOPPED (or review-required) **attempt bundle**: the
manifest is written inside the staging directory before the atomic move to `attempts/`; the
persisted console ends with the `FINAL STATUS:` line; `complete/` is never altered
(tests 13, 18). A lock-acquisition refusal writes nothing (cannot enter the transaction). A
hard crash leaves the lock as the designed fail-safe.

## 16. Artifact hashing

`_bundle_hashes` hashes exactly the four non-manifest artifacts present and derives
`bundle_sha256` from the sorted `name:sha` pairs; the manifest records both and never
contains its own hash (test 15 verifies against an independently computed console hash).

## 17. Unit tests

`tests/p2a/test_p2a_regionlive_phase3_safety.py` — **18/18 PASS** (pytest 8.4.2, 1.5 s),
covering exactly the mandated list: mapping counts/ordering; free↔full round trip; exact
pin preservation; duplicate/reordered/wrong pin refusal; G-16 pass and fail; expected
bound-set validation; canonical-root refusal; wrong-subdirectory refusal; optimizer
method/options/keys mismatch refusal; dry-run cannot call an injected optimizer; successful
bundle cannot be overwritten (transaction + CLI B.3); failed attempt cannot mutate a
successful bundle; artifact-set publication in a temporary directory; manifest no-self-hash;
console final-status line; pre/post input-hash change detection; STOPPED evidence written
before exit. All via fake objectives/optimizers and temporary roots — the real optimizer and
estimation data are never touched (first run surfaced and fixed the attempt-ID collision;
final run: `18 passed`).

## 18. Phase 1–2 regression

`--phase 2 --dry-run` against a scratch root: **exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`**,
G-19 `|dev_full| = 0.00e+00`, NumPy/JAX 3.64e-12, and the regenerated stem hashed
**`8bf083ce…` byte-identically** once more. Accepted Phase 1–2 evidence untouched.

## 19. Phase-3 dry-run

Canonical command: **exit 0, `PHASE_3_DRY_RUN_COMPLETE`** under the new transaction —
contract passed the full remediated battery (12-file authentication, anchors, pin identity,
map + round trips, derived at-bound set, 35-count, mnlmeta asserts, `negLL(start)` dev
**0.00e+00**); bundle published to
`attempts/20260724T135254Z_…_dryrun_PHASE_3_DRY_RUN_COMPLETE/`; `optimizer_called: false`;
lock released; `complete/` absent; pre-review evidence migrated byte-preserved to
`attempts/pre_review_dryrun_0_REJECTED_REVIEW/` (both file hashes equal their pre-migration
values).

## 20. Prohibited-operation audit

No real estimation, optimizer call, EUROMOD, draw regeneration, Hessian/rank, clustered
inference, post-estimation, welfare, or synthetic recovery was executed. `scipy.optimize`
remains barred outside the real Phase-3 branch (asserted at phase3-start and dry-run end).
Phases > 3 refused (exit 2, verified). No notebook, package, certified-baseline, theta, or
Phase 1–2 evidence file changed — the sweep found **0 changed files** among all files
present both before and after; the only moves were the two mandated pre-review relocations.

## 21. Git diff summary

```
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml    (+62)
 M scripts/p2a/run_p2a_regionlive_rebuild.py             (Phase-3 section rewrite)
 D phase3_estimation_v1/phase3_manifest.json  \  relocated byte-identically into
 D phase3_estimation_v1/phase3_console.log    /  attempts/pre_review_dryrun_0_REJECTED_REVIEW/
?? outputs/.../phase3_estimation_v1/attempts/            (new transaction layout)
?? tests/p2a/                                            (safety suite)
?? docs/France_case/P2a/FR_P2a_region_live_phase3_remediation_report_v1.md
```

`dclaborsupply-monorepo`: clean. Current runner SHA-256 `efd2204a…` (recorded in the config
authentication table); nothing committed.

## 22. Residual warnings

None blocking. Two documented residuals for the reviewer: (a) the config-self hash is
recorded-not-preregistered (fixed-point impossibility, §11); (b) the module-presence guard
remains defense-in-depth rather than a complete call audit (as the first review already
noted, with no prohibited calls found statically).

## 23. Whether second independent review may begin

**YES.** All §18 fixes are implemented with test evidence, the regression and dry-run gates
are green, and the transaction protects all prior evidence. Suggested focus: the
`Phase3Transaction` semantics, the mapping helpers, and the recheck-before-write ordering
in `_phase3_estimate`.

## 24. Immediate next action

Second independent static review of the runner/config/tests against this report. Only an
APPROVE verdict unblocks the first real Phase-3 execution (canonical command without
`--dry-run`), which will publish to `phase3_estimation_v1/complete/` under the lock and
transaction. Phases 4–8 remain manager-gated.

**FINAL VERDICT: READY FOR SECOND INDEPENDENT REVIEW** (no real Phase 3 executed; nothing
committed).
