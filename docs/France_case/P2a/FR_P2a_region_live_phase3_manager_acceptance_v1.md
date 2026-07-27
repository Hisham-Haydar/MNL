# FR P2a Region-Live — Phase-3 Manager Acceptance — v1

Date: 2026-07-27. Records the accepted FR-2016 singles P2a region-live Phase-3
production-estimation checkpoint. Based on the passed audit
(`FR_P2a_region_live_phase3_estimation_report_v1.md`, FINAL VERDICT: PASS) and a
fresh pre-acceptance re-verification of the published bundle. No code, config, test,
input, parameter file, notebook, or existing output was modified; Phase 3 was not
rerun; no optimizer call; no Phase 4+ operation.

## 1. Manager verdict

**Phase 3: ACCEPTED.** The first and only real Phase-3 estimation, executed through
the approved scope-doc §8 CLI at the approved checkpoint revision, is accepted as
the region-live production estimate. **Phase 4 curvature and rank diagnostics:
AUTHORIZED after this checkpoint commit. Phases 5–8: NOT AUTHORIZED.**

## 2. Phase-3 result accepted

Accepted bundle:
`outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/complete/` — exactly
`phase3_console.log`, `theta_estimated.csv`, `optimizer_diagnostics.json`,
`estimation_results.json`, `phase3_manifest.json` (attempt
`20260727T063501Z_346680_cd2cd9164e644117b1ffe7608c737fef_estimate`, wall 11.8 s).
All four non-manifest artifact hashes re-verified against the manifest at
acceptance time.

## 3. Canonical repository revisions

Execution revision (recorded in the manifest's verified gate record and current at
acceptance): MNL HEAD `65bf2c18f7d287563d73e277ae29d7a2adc525c5`; nested
dclaborsupply HEAD = MNL gitlink `27756a06ea189339aa82915ed2124628afed20eb`;
approved review `FR_P2a_region_live_phase3_code_review_v6.md`, SHA-256
`9c78d4e0a194e0b20904c6b9ec8f875525e1a6217d4d4f7a7192635b672ab341`. Package
identity: all ten dclaborsupply modules Git-canonically blob-equal at that nested
commit.

## 4. Canonical bundle hash

Deterministic bundle SHA-256 (sorted `filename:sha256` lines over the four
non-manifest artifacts), recomputed independently at acceptance:

`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`

equal to the manifest's recorded `bundle_sha256`. The manifest carries no
self-hash.

## 5. Objective result

negLL(start) = 19053.46553160094 (deviation 0.0 from the pre-registered value);
negLL(final) = **19053.46553160093**; |deviation| from the target
19053.46553160094 = 1.0913936421e-11 ≤ 1e-4 → G-1 PASS.

## 6. Optimizer result

`optimizer_called: true`; checkpoint-exact scipy L-BFGS-B
(maxiter 5000, maxcor 30, ftol 1e-15, gtol 1e-10) over the package JAX objective on
the ordered 37-free vector; `success: true`, status code 0, message
`CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH`; 1 iteration, 3 function and
3 gradient evaluations — the expected exact-reproduction behavior from the warm
start.

## 7. Gradient gate

Max |gradient| over the 35 non-bound free parameters = 1.0992597206e-4 < 1e-2 →
G-3 PASS (recomputed independently in the audit; bit-equal to the recorded gate).
The full 47-element gradient and the 37-element free projection are published in
the bundle.

## 8. Pin preservation

All ten pins (beta_l0_m, beta_l_age_m, beta_l_age2_m, beta_l0_f, beta_l_age_f,
beta_l_age2_f, beta_l_nkids_f, theta_l_f, beta_E_y2015, beta_E_y2017) **bitwise
unchanged** from the accepted pin values through the applied start vector to the
final estimate (IEEE-754 byte equality, re-verified at acceptance).

## 9. Bound and G-16 gates

G-15: bound hits exactly `{beta_l_age2_sm, beta_l_age2_sf}` = the derived and
configured expectation; no unexpected hit. G-16 (ε = 1e-9): zero violations over
all 37 free parameters. Structure: 47 parameters, 37 free, 10 pins, 35 non-bound
free — all confirmed.

## 10. Input provenance

All ten runtime inputs authenticated by path identity and SHA-256 against the
accepted anchors before optimization and re-hashed identically after (pre = post =
accepted for every label; geometry `5bcf0e54…`, frozen stem `8bf083ce…`, certified
spec `492bcfa9…`, certified warm start `c72e92b1…`, start theta `930ef3aa…`, plus
the Phase 1–2 evidence anchors). Runtime-map fingerprint unchanged pre/post
(`f9a5ba9f…`).

## 11. Transaction state

`complete/` exists only for status `PHASE_3_COMPLETE`; `.phase3.lock` absent;
`.staging/` empty; the successful bundle was published by atomic directory rename
and is immutable — the runner refuses any further real Phase-3 run while
`complete/` exists.

## 12. Certified baseline status

**The pooled 47-parameter baseline (`joint_pooled_v1_bll0_tlmpin`, negLL
238504.6360973987) remains the formal certified baseline.** It is untouched by
this checkpoint; the certified spec and warm-start files re-hash to their accepted
anchors.

## 13. P2a status

**P2a region-live remains PROVISIONAL.** This acceptance records an exact
production reproduction through the reviewed gate; it makes no identification
claim and authorizes no manuscript use. The result's own status field records
`PROVISIONAL - Phase 3 estimation; Phases 4-8 pending; no identification claim`.

## 14. Welfare status

**Welfare remains non-reportable.** No welfare, decomposition, or distributional
use of this estimate is authorized.

## 15. Phase-4 authorization

**Phase 4 (curvature and rank diagnostics) is AUTHORIZED, effective after this
checkpoint commit**, against the recorded revisions: this acceptance commit's MNL
SHA, nested HEAD `27756a06…`, and bundle SHA `2cf23764…`. Scope: Hessian/curvature
and rank/identification diagnostics of the accepted estimate only. Phase 4 requires
its own plan and gates before execution; nothing in this document executes it.

## 16. Phases not authorized

**Phases 5–8 are NOT AUTHORIZED** (standard errors/clustered inference beyond
Phase-4 diagnostics, post-estimation reporting, welfare, synthetic recovery, and
any manuscript integration). Each requires a separate manager decision after
Phase-4 results.

## 17. Notebook status

The pipeline notebooks (`fr_singles_pipeline_v1.ipynb`, `fr_singles_pipeline_v2.ipynb`)
**must not yet run their estimation, inference, post-estimation, or welfare
sections.** The production estimate exists solely in the audited `complete/`
bundle; notebook re-estimation would bypass the execution gate.

## 18. Immediate next action

Commit this acceptance, the estimation audit report, and the five `complete/`
bundle files as one checkpoint
(`results(p2a): record accepted Phase-3 production estimate`), verify both
repositories are fully clean, and record the new MNL SHA. Then plan Phase 4
against the recorded revisions. Do not run Phase 4 in this step.

**Phase 3: ACCEPTED. Phase 4: AUTHORIZED after this commit. Phases 5–8: NOT
AUTHORIZED.**
