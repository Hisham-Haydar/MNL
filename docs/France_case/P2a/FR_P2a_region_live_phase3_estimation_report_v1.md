# FR P2a Region-Live — Phase-3 Estimation Report — v1

Date: 2026-07-27. Audit of the first and only real Phase-3 execution of the FR-2016
singles P2a region-live production rebuild. Read-only audit: no rerun, no optimizer
call, no Phase 4+, no Hessian/inference/post-estimation/welfare, no notebook, no
commit. Every number below was re-derived from the published bundle by independent
recomputation, not merely read from the manifest.

## 1. Phase-3 verdict

**PASS.** The single authorized real Phase-3 estimation completed and published an
immutable `complete/` bundle. Optimizer success; final negLL
19053.46553160093, |deviation| from the target 19053.46553160094 = **1.09e-11**
(tolerance 1e-4); all ten pins preserved bitwise; the bound set is exactly the two
expected parameters; G-16 clean over all 37 free parameters; max |gradient| over the
35 non-bound free parameters 1.10e-4 (< 1e-2); all ten input hashes verified before
and identically after optimization; the bundle hash reproduces; lock absent, staging
empty; both repositories clean at the approved revisions.

## 2. Execution authorization

The run executed through the scope-doc §8 CLI with the verified gate record embedded
in the manifest (`review_gate: REVIEW_V6_APPROVED`, `execution_ready: true`):
expected MNL HEAD `65bf2c18f7d287563d73e277ae29d7a2adc525c5` (the approved
checkpoint), expected nested HEAD = gitlink
`27756a06ea189339aa82915ed2124628afed20eb`, approved review
`docs/France_case/P2a/FR_P2a_region_live_phase3_code_review_v6.md` with SHA-256
`9c78d4e0a194e0b20904c6b9ec8f875525e1a6217d4d4f7a7192635b672ab341` — all exactly the
values recorded at the checkpoint commit. Both worktrees were recorded clean
(`dirty: false`) at run time. Package identity: all ten dclaborsupply modules under
the reviewed source root with Git-canonical blob equality (`package_identity_ok:
true`; the two known autocrlf raw-hash divergences show `blob_equal: true` as
designed).

## 3. Command and exit code

Attempt `20260727T063501Z_346680_cd2cd9164e644117b1ffe7608c737fef_estimate` (full
uuid4 id format from the approved fix), started 2026-07-27T06:35:01Z, wall 11.8 s.
Recorded command line: `scripts/p2a/run_p2a_regionlive_rebuild.py --phase 3`. The
published status `PHASE_3_COMPLETE` is reachable only through the exit-code-0
finalization branch, so the process exit code consistent with this bundle is **0**;
no operator-transcribed exit-code value was attached to this audit request, and any
operator observation other than 0 would contradict the on-disk evidence and must be
reported.

## 4. Repository revisions

At audit time: MNL HEAD `65bf2c18f7d287563d73e277ae29d7a2adc525c5`; nested
dclaborsupply HEAD `27756a06ea189339aa82915ed2124628afed20eb`; MNL gitlink equal to
the nested HEAD. `git status --porcelain --untracked-files=all` shows exactly the
five untracked files of the new `complete/` bundle and nothing else; the nested
status is empty. These match the manifest's recorded run-time revisions.

## 5. Review approval

The canonical review v6 carries exactly one `**FINAL VERDICT: APPROVE**` line under
`# 1. Sixth-review verdict`; its committed SHA-256 equals the gate value in §2. The
pre-fix review remains archived unchanged as
`FR_P2a_region_live_phase3_code_review_v6_pre_fix.md`.

## 6. Input provenance

All ten runtime labels authenticated pre-optimization with path identity and SHA-256
equality against the accepted anchors — geometry parquet `5bcf0e54…`, geometry meta
`ff2d4422…`, frozen stem `8bf083ce…`, stem mnlmeta `05be4030…`, certified spec
`492bcfa9…`, certified warm start `c72e92b1…`, stored region-live start theta
`930ef3aa…`, Phase 1–2 rebuild manifest `1ed3041f…`, accepted dry-run report
`ec50ea98…`, pre-estimation reload verification `6f457de9…`. The Phase 1–2 manifest
status and its original runner/config anchors (`be11294b…`/`68d152e7…`) were also
verified. Alias-identity checks all pass.

## 7. Starting parameter vector

Start theta from `theta_p2a_singles_2016_v1.csv` (raw SHA-256 `5f3722dc…`), with the
ten immutable pin values injected bitwise at start (applied-theta SHA-256
`9a9a4918…`; max pin adjustment vs the stored file 4.66e-07, the documented contract
behavior). Starting objective reproduced exactly: negLL(start) = 19053.46553160094,
deviation 0.0 from the pre-registered value.

## 8. Optimizer configuration

Checkpoint-exact `scipy.optimize.minimize` L-BFGS-B over the package-built JAX
objective (`build_jax_singles_ll` sm+sf, `jax.value_and_grad`, float64), on the
ordered 37-free vector with 37 free bounds and options exactly
`{maxiter: 5000, maxcor: 30, ftol: 1e-15, gtol: 1e-10}`; all fifteen safety-constant
equality checks true.

## 9. Optimizer termination

`success: true`, `status_code: 0`, message
`CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH`; iterations 1, function
evaluations 3, gradient evaluations 3, 1.3 s optimize wall. Single-iteration
convergence is the expected behavior for a warm start already at the provisional
optimum: the run's purpose was exact reproduction through the production gate, and
the objective improved only in the last representable digit.

## 10. Starting objective

negLL(start) = 19053.46553160094; absolute deviation from the pre-registered target
0.0 (G-0/pre-opt tolerance 1e-4).

## 11. Final objective

negLL(final) = 19053.46553160093 (`final_ll` −19053.46553160093 across
`estimation_results.json`, `optimizer_diagnostics.json`, and the console line).

## 12. Target-objective gate

|19053.46553160093 − 19053.46553160094| = **1.0913936421e-11** ≤ 1e-4 → G-1 PASS
(recomputed independently; equals the recorded `g1_abs_dev_full`).

## 13. Gradient diagnostics

The full 47-element final gradient is published (`gradient_final`, mirrored in the
`grad` column of `theta_estimated.csv` — verified bitwise). Recomputed maximum
absolute gradient over the 35 non-bound free parameters:
**1.0992597206e-4** < 1e-2 → G-3 PASS (bit-equal to the recorded gate value). The
two bound parameters carry outward-pointing gradients (beta_l_age2_sm −8.45e-1,
beta_l_age2_sf −1.47e0), consistent with binding bounds and excluded from G-3 by
design; the 37-element free projection is also published.

## 14. Pin preservation

All ten pins (beta_l0_m, beta_l_age_m, beta_l_age2_m, beta_l0_f, beta_l_age_f,
beta_l_age2_f, beta_l_nkids_f, theta_l_f, beta_E_y2015, beta_E_y2017; interleaved
indices [10–17, 31, 32]) verified **bitwise identical** (IEEE-754 byte comparison)
between the accepted pin values, the applied start vector, and the final estimate.
Round-trip checks (`project∘expand` exact, pins bitwise accepted) true.

## 15. Bound and G-16 diagnostics

Recomputed from the published bounds-and-distances table: bound hits (ε = 1e-5) are
exactly `{beta_l_age2_sm, beta_l_age2_sf}` — equal to the derived expectation, the
config expectation, and the recorded G-15 set; no unexpected hit. G-16 (ε = 1e-9)
recomputed over all 37 free parameters: **zero violations**; every free parameter's
`in_bounds` flag in `theta_estimated.csv` is true. Structure gate: 37 free, 10 pins,
35 non-bound free — all confirmed.

## 16. Post-optimization input recheck

All ten inputs re-hashed after optimization and before any result write:
pre = post = accepted for every label. Runtime-map fingerprint identical pre and
post (`f9a5ba9f4d7db55c6b9913376974855f79e65ac0b9e696debb8958b7b4a5d0de`), equal to
the value recorded at contract time.

## 17. Output bundle

`complete/` contains exactly the five required files: `phase3_console.log` (500 B),
`theta_estimated.csv` (5,311 B, 47 rows, names bit-matching the specification order,
values bit-matching the published theta), `optimizer_diagnostics.json` (29,104 B),
`estimation_results.json` (7,015 B), `phase3_manifest.json` (28,578 B). All four
artifact SHA-256 values reproduce exactly, and the deterministic bundle hash
recomputes to the recorded `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`.
The manifest is absent from its own artifact-hash dictionary (no self-hash).

## 18. Transaction and lock state

`complete/` exists and only for status `PHASE_3_COMPLETE`; `.phase3.lock` absent;
`.staging/` empty; no new `attempts/` entry was created by the run (the newest
attempts remain the committed pre-run dry-runs). The attempt id carries the full
uuid4 token, and publication was the atomic directory rename into `complete/`.

## 19. Prohibited-operation audit

No Phase-4+ operation, Hessian, standard error, clustered inference,
post-estimation, welfare, or synthetic-recovery computation exists anywhere in the
bundle; the 11.8 s wall time and the console (contract → single optimize → publish)
exclude any such work. This audit itself only read files and ran read-only git
queries; nothing was modified, rerun, or committed.

## 20. Baseline and P2a status

The certified 47-parameter pooled baseline (`joint_pooled_v1_bll0_tlmpin`, negLL
238504.6360973987) is untouched: the certified spec and warm-start files re-hash to
their accepted anchors (`492bcfa9…`, `c72e92b1…`) and the tracked tree is unchanged.
P2a region-live remains **PROVISIONAL** per the scope doc §13 and the result's own
status field: Phases 4–8 pending, no identification claim, no inference, no
manuscript or welfare use.

## 21. Whether Phase 4 may run

From the estimation-quality standpoint there is no impediment: every Phase-3 gate
passed and the result is published and immutable. However, Phases 4–8 remain
**manager-gated** (scope doc §10/§13); Phase 4 may run only after (a) the manager
authorizes it explicitly and (b) the `complete/` bundle and this report are
committed so the result being built upon is itself a recorded revision. This audit
grants no Phase-4 authorization.

## 22. Immediate next action

Commit the five-file `complete/` bundle and this estimation report as the Phase-3
result checkpoint (manager action; nothing was committed by this audit). Then decide
Phase-4 authorization against the recorded revisions
(MNL `65bf2c1…` + result commit, nested `27756a0…`, bundle SHA `2cf23764…`).

**FINAL VERDICT: PASS** (read-only audit; no Phase 3 rerun; nothing committed).
