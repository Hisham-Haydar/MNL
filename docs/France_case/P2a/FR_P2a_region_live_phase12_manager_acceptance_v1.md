# FR P2a Region-Live — Phase 1–2 Manager Acceptance — v1

Date: 2026-07-24. Records the manager verdict on the Phase 1–2 dry-run evidence
(`FR_P2a_region_live_dry_run_report_v2.md` and the `region_live_v1/` evidence bundle).
Governed by `FR_P2a_region_live_manager_decisions_v2.md` (canonical) and
`FR_P2a_region_live_production_rebuild_plan_v2.md`.

## 1. Manager verdict

**Phase 1–2: ACCEPTED as PASS.** The production rebuild's data-wiring reconstruction (Phase 1)
and package-load / objective-reproduction verification (Phase 2) are accepted on the evidence
below. **Phase 3 (estimation) implementation and execution: AUTHORIZED** (§9).
**Phases 4–8: NOT YET AUTHORIZED** (§10).

## 2. Evidence accepted

- G-0 frozen-inputs gate: PASS (all items).
- G-18 data-wiring battery: PASS in full — funnel, mapping, region/urbanisation/GSUR revival,
  take-up determinism (seed 20162016; rates 0.548/0.265), choice geometry, band overwrite,
  three-frame reconciliation with **zero differing columns**, five-column idempotence.
- Households: **1,555** (714 singles-male + 841 singles-female); alternatives per household:
  **101**; engine-ready frame 157,055 × 194.
- Run-level free parameters: **37**; run-level pins: **10** (bounds-clamped at certified
  warm-start values); occupation block free; parameter ordering verified against both stored
  theta CSVs.
- G-19 objective reproduction at the stored region-live theta: **JAX negLL =
  19053.46553160094, absolute deviation from the full-precision target = 0.0**;
  **NumPy/JAX difference = 3.64e-12**; 4-dp anchor deviation 3.16e-05.
- Fresh-process pre-estimation reload: **PASS** (`abs_dev_full = 0.0` in a new process;
  `pre_estimation_reload_verification.json`).
- Resolved T3 cluster count: **1,555** (D-6 self-ratified; pooled default 9,657 never used).
- Attempt-0 G-0 STOP correctly preserved under `audit_attempt_0_g0_stop/`.

## 3. Canonical hashes

| Artifact | SHA-256 |
|---|---|
| Frozen draw-geometry parquet (`region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet`) | `5bcf0e5409ef74c57f6de24efdfd24d0075132dc3138ddb57a22740b916cf235` |
| Frozen engine-ready stem (`region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet`) — byte-identical to all three pre-existing region-live frames | `8bf083ce3be17f8c74af894bc3748718cbb0a991eb9a411db7188e806d1e9f0d` |
| Certified spec YAML (`estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`) | `492bcfa9c766bfcb5d8536f5e920cc0b00ffa600b7b89db60b250365f331f211` |
| Accepted stored region-live theta vector (`trial` column, float64 bytes) | `5f3722dc2092cda0af47cec39cb2cbbb7050dd153df1edf9dd9de8a231d76c9b` |
| Phase 1–2 runner at acceptance (`run_p2a_regionlive_rebuild.py`) | `be11294bf6e0456a37afc713d0e1bd843f574e2dfd136d60968b6519594c4475` |
| Run-config at acceptance (`p2a_regionlive_rebuild_v1.yaml`) | `68d152e70cb73b6616a8b16a63edfb90298945c65fa15dd8580399033059d8fe` |

## 4. Phase 1 status

**ACCEPTED.** `er_b` was reconstructed independently from the frozen priced-draw artifacts +
frozen geometry + raw-source region/urbanisation/GSUR revival (never reading an engine-ready
frame), passed every G-18 gate, and froze to a canonical stem that is byte-identical to the
pre-existing region-live frames. The formerly missing `propagate_regionlive.py` logic is now
superseded by a committed, reproducible production path.

## 5. Phase 2 status

**ACCEPTED.** Package-load verification passed: loader liveness (region dummies, urbanisation
one-hot, GSUR arrays equal to the frozen columns; prior strictly positive; `log_prior`
consistency dev 0.0), 47-name binding with 10 pins / 37 free, warm-start equality (max-abs 0.0
vs the full-precision stored `certified` column), structural `wage_spec = vw` with
`loc_empirical`/`vw_occupation` inactive, proposal correction data-carried and centered with
proposal weights, and exact objective reproduction on both backends.

## 6. Baseline status

**The 47-parameter pooled model `joint_pooled_v1_bll0_tlmpin` (negLL 238504.6360973987) remains
the formal certified JMP baseline.** Nothing in Phase 1–2 or in the Phase-3 authorization
changes, replaces, or competes with it.

## 7. P2a status

**P2a region-live remains PROVISIONAL.** The accepted Phase 1–2 evidence establishes
reproducible data wiring and objective reproduction only. No inference validity, no
identification claim, and no strict-estimation verdict is implied. The strict verdict requires
Phases 3–8 and a separate manager review (decisions v2, D-7: synthetic recovery is mandatory
before any promotion or structural-identification claim).

## 8. Welfare status

**Welfare remains NON-REPORTABLE.** The existing P2a welfare/inequality outputs were computed on
the provisional theta and inherit its status; no welfare number may be reported or used in the
manuscript until the region-live track passes its strict verdict and welfare is separately
re-certified. No welfare readiness is declared.

## 9. Phase 3 authorization

**AUTHORIZED — implementation and execution of Phase 3 (estimation) only**, per plan v2 §11 and
the ratified gates (G-1/G-2/G-3/G-4/G-15/G-16; D-2/D-5): the validated JAX objective through the
dclaborsupply engine, L-BFGS-B with the pre-registered checkpoint settings
(`maxiter=5000, maxcor=30, ftol=1e-15, gtol=1e-10`), the accepted stored region-live theta as
the configured starting vector, the 10 pins preserved, outputs confined to
`region_live_v1/phase3_estimation_v1/`, and full optimizer/gradient/bound diagnostics persisted.
An objective materially away from the target 19053.46553160094 (beyond 1e-4) is
REVIEW_REQUIRED_TARGET_MISMATCH, not automatic acceptance.

## 10. Phases not authorized

**Phases 4–8 are NOT YET AUTHORIZED**: Hessian/eigenvalue/rank/condition diagnostics (Phase 4),
region × urbanisation identification tests, cluster-robust inference (Phase 5), post-estimation
(Phase 6), the strict fresh-process cold-reload gate (Phase 7), and the strict-verdict package /
promotion decision (Phase 8) all await manager review of the Phase-3 evidence. No synthetic
recovery, no identification certification, no welfare re-run.

## 11. Immediate next action

Implement Phase-3 support in `scripts/p2a/run_p2a_regionlive_rebuild.py` + the run-config
(implementation and static validation only — no estimation execution), submit the
implementation for independent code review, and only then execute the real Phase-3 run under
this authorization.
