# FR P2a Region-Live — Phase-4 Manager Acceptance — v1

Date: 2026-07-30. Records the accepted FR-2016 singles P2a region-live Phase-4
curvature and regional-identification checkpoint. Based on the successful
authorized rerun (`FR_P2a_region_live_phase4_execution_report_v2.md`, exit 0)
and independent re-verification of the published bundle at acceptance time. No
numerical artifact modified; Phase 4 not rerun; no optimizer/gradient/Hessian
invoked by this acceptance; Phase 5 not started.

## 1. Manager verdict

**Phase 4: ACCEPTED.** The single authorized real Phase-4 run, executed through
the approved review-v7 gate at the corrected R-1 checkpoint, is accepted as the
region-live curvature and regional-identification record.
**Phase-5 planning: AUTHORIZED after this checkpoint commit. Phase-5 execution:
NOT YET AUTHORIZED.**

## 2. Accepted repository state

Execution revision (recorded in the manifest's verified gate record and
re-verified at acceptance): MNL HEAD
`fee60723ed27d6979976a3dc85b09cde3096e011`; nested dclaborsupply HEAD = MNL
gitlink `27756a06ea189339aa82915ed2124628afed20eb`; approved Phase-4 review v7
SHA-256 `cd0bb6ee5a0cbe130e65cdb211d9eb6d38ede1143e7b2431583013fd9a708d0c`;
`review_gate: PHASE4_REVIEW_V7_APPROVED`, `execution_ready: true`. Both
worktrees were fully clean at execution and at acceptance (apart from the
intended result and memos being committed here).

## 3. Accepted Phase-3 dependency

Phase 4 diagnosed the immutable accepted Phase-3 bundle
(`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`,
negLL 19053.46553160093, theta pins bitwise-preserved), re-verified inside the
run's contract and unchanged after it.

## 4. Accepted Phase-4 bundle

`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/` —
exactly eight files (console, diagnostics, manifest, Hessian CSV + NPY,
eigenvalues, regional subblock, Schur complement). All seven non-manifest
artifact hashes re-verified against the manifest; the deterministic bundle
SHA-256 recomputes to

`5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`

with the manifest excluded from its own hash map. `status: PHASE_4_COMPLETE`;
`optimizer_called: false`; `gradient_evaluated: true`;
`hessian_evaluated: true`.

## 5. Hessian construction

Exact `jax.hessian` of the package-built negative log likelihood over the
ordered 37-free vector at the accepted Phase-3 estimate, all ten pins fixed
bitwise outside differentiation; raw-Hessian symmetry deviation 1.82e-12
against tolerance 2.36e-4 (G-6 PASS), spectral work on the symmetrized matrix.
The pre-evaluation gradient reproduced the published Phase-3 free-gradient
projection to 8.88e-16.

## 6. Full-Hessian curvature

G-5/G-7 PASS: the 37×37 free Hessian is strictly positive definite
(minimum eigenvalue **0.1037326963880782**, zero eigenvalues ≤ 1e-8) with full
numerical rank **37** under ε_rank = 1e-10·max eig (4.20e-6).

## 7. Numerical conditioning

G-8 PASS, clean tier: condition number **405,353.9** ≤ 1e7 — roughly 3×
better-conditioned than the certified pooled baseline's anchor 1.295e6.

## 8. Regional design identification

R-1 PASS on the corrected source: the design was built from the
**production likelihood loader arrays**
(`regional_design_source: production_likelihood_loader_arrays`), 1,555 × 10 in
the canonical order (`gsur, reg2..reg8, drgur, drgmd` mapped to
`beta_E_gsur, beta_E_drgn2..8, beta_E_drgur, beta_E_drgmd`), household-constant
and finite, reduced at the loader's own group boundaries — numerical rank
**10** under the unchanged tolerance. The earlier rank-3 result is the audited
false failure of the dead stored columns (preserved STOPPED attempt
`52f34b54…`), superseded by this corrected run.

## 9. Raw regional Hessian block

R-2 PASS: the 10×10 regional subblock of the symmetrized Hessian is strictly
positive definite, minimum eigenvalue **3.3787399166319405**.

## 10. Conditional Schur complement

R-4 PASS: the conditional regional information matrix
`H_RR − H_RN·H_NN⁻¹·H_NR` (stable solve, no explicit inverse) has rank **10**
with strictly positive minimum eigenvalue **2.255741652065068**. The plan-v2
§14 verdict `region_urbanisation_identification: PASS` (R-1 ∧ R-2 ∧ R-4).

## 11. Regional loading diagnostic

R-3 (warning-only): no smallest-eigenvector regional loading share reached the
0.5 threshold (shares ≈ 0.0000/0.0000/0.0001) — the region-dead flat
directions are demonstrably lifted; the weakest curvature directions are not
regional. Warnings list empty.

## 12. Input and provenance integrity

All ten authenticated inputs matched their accepted SHA-256 anchors before
evaluation and re-verified identically afterwards (post-evaluation recheck
all-ok; runtime-map fingerprint stable). The execution-gate record in the
manifest binds the run to the exact commit, gitlink, and approved review-v7
hash above. Package identity: all dclaborsupply modules Git-canonically
blob-equal at the nested commit.

## 13. Scientific interpretation

At the accepted region-live estimate, the log-likelihood is locally strictly
concave in all 37 free directions with healthy conditioning, and the ten
regional/urbanisation parameters (`gsur`, seven NUTS-1 region dummies,
`drgur`, `drgmd`) carry strictly positive conditional information after
partialling out the 27 nuisance directions. This is the real-data
local-identification evidence the region-live programme required: the regional
block that was flat in the region-dead fit is now identified on the data that
actually enter the likelihood.

## 14. Limits of the evidence

Per D-7, this is **local** identification at a point estimate obtained as an
exact warm-start reproduction: it is not synthetic-recovery certification, not
a global-identification claim, and carries no standard errors or inference
(Phase 5 has not run). The design-rank statement concerns the estimation
sample's household-level design; no claim extends beyond the frozen 1,555
household sample.

## 15. Phase-5 authorization

**Phase-5 planning is AUTHORIZED effective after this checkpoint commit**:
prepare the cluster-robust inference plan per plan v2 §15 (chunked per-group
scores, T1 score identity, meat/sandwich on the 35-parameter SE block, T3
cluster count resolved per D-6, T4/T5 checks) against the recorded revisions
and this accepted bundle. **Phase-5 execution is NOT YET AUTHORIZED** — it
requires its own implementation, review, and an explicit execution mandate.

## 16. Synthetic-recovery requirement

Unchanged and separate (D-7): synthetic recovery remains mandatory before P2a
promotion to a certified structural result, before any claim that the
regional/access block is structurally identified, and before P2a can replace
the certified pooled baseline. Nothing in this acceptance discharges it.

## 17. Notebook and welfare restrictions

**P2a remains PROVISIONAL.** The pipeline notebooks must not run their
estimation, inference, post-estimation, or welfare sections. **Welfare and
decomposition remain non-reportable** on P2a. **The pooled 47-parameter
baseline (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987) remains the
formal certified baseline.**

## 18. Immediate next action

Commit this acceptance, the execution report v2, and the eight-file
`complete/` bundle as one checkpoint
(`results(p2a): record accepted Phase-4 curvature diagnostics`), verify both
repositories fully clean, and record the new MNL SHA. Then begin the Phase-5
design memo against the recorded revisions. Do not execute Phase 5.

**Phase 4: ACCEPTED. Phase-5 planning: AUTHORIZED after this commit. Phase-5
execution: NOT YET AUTHORIZED.**
