# FR P2a Region-Live — Phase-4 Implementation Report — v1

Date: 2026-07-27. Implements Phase-4 curvature, Hessian-rank and
regional-identification diagnostics per the manager acceptance
(`FR_P2a_region_live_phase3_manager_acceptance_v1.md` §15) and the ratified
D-3/D-4 gates (decisions v2; plan v2 §13–§14, G-5..G-9). Implementation and
non-optimizing validation ONLY: no real Hessian evaluated, no optimizer, theta
untouched, no SE/inference/post-estimation/welfare/notebooks, nothing committed.

## 1. Implementation verdict

**READY FOR INDEPENDENT PHASE-4 REVIEW.** Phase 4 is implemented in the production
runner behind the same execution-contract discipline as Phase 3: `--phase 4` alone
is a non-evaluating dry-run (verified live and in a subprocess test — Hessian never
evaluated), a real run requires `--execute-phase4` plus the identical Git/review-v6
gates, and every diagnostic gate is a pure, unit-tested function. The suite passes
**44/44 in three consecutive runs**, the accepted Phase-3 `complete/` bundle is
re-verified byte-identical on every run, and `git diff --check` exits 0.

## 2. Manager authorization

Phase 4 was authorized by the Phase-3 manager acceptance §15, effective after
checkpoint commit `c7d558a36489520a0f8487abf939d5300deaffb1` (current HEAD), scoped
to curvature and rank/identification diagnostics of the accepted estimate only.
Phases 5–8 remain refused (verified: exit 2 for phases 5–8).

## 3. Files inspected

Read in full: manager decisions v2 (D-3/D-4 gate values, D-7 identification scope),
production rebuild plan v2 (§5 free/regional partition, §13–§14 Phase-4 batteries,
§19 gate table G-5..G-9), the Phase-3 manager acceptance and estimation report, the
runner, the run config, the accepted `complete/` bundle (all five artifacts), the
frozen-stem schema (design columns `gsur, reg2..reg8, drgur, drgmd` all present),
and the package derivative surface (`build_jax_singles_ll` float64; x64 enabled in
the package engine loader; `jax.hessian` route per plan v2 §6).

## 4. Files modified

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (+715/−5): Phase-4 constants,
   nine pure/contract functions, transaction integration, `run_phase4` CLI
   entrypoint, `--execute-phase4`, phase-5+ refusal.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+31): declarative
   `phase4:` block (subdir, accepted-bundle binding, ratified gates, regional
   lists) — runner asserts exact equality with its immutable constants.
3. `tests/p2a/test_p2a_regionlive_phase3_safety.py` (+273/−3): tests 33–44,
   updated phase-refusal test 10, updated test 29 (accepted `complete/` now
   legitimately exists — the dry-run must leave it byte-identical).

Created: this report. Untouched: dclaborsupply-monorepo (clean), the certified
baseline, the accepted Phase-3 bundle, all Phase 1–2 evidence, notebooks, thetas.

## 5. Phase-3 bundle binding

`_phase4_verify_phase3_bundle` requires: exact five-file set; per-artifact SHA-256
equality with the Phase-3 manifest; recomputed deterministic bundle hash equal to
BOTH the manifest record and the immutable constant
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` (also mirrored
in YAML and re-asserted equal); manifest status `PHASE_3_COMPLETE` with
`optimizer_called: true` and every recorded gate flag passing. The configured
bundle dir must resolve to the canonical `phase3_estimation_v1/complete`. The
accepted theta is taken from `estimation_results.json` (authoritative
full-precision vector), required bitwise-equal to the diagnostics `final_theta`
and its recorded SHA, within 1e-12 relative of the CSV table (which carries
pandas ~16-digit formatting, ≤1 ulp representational), and its ten pins must be
bitwise-identical to the accepted pin values. Theta is never altered.

## 6. Derivative route

The Phase-4 contract first re-runs the complete Phase-3 input contract (all ten
authenticated inputs, spec/pin/map/round-trip battery, objective at the stored
start). It then builds `negll_free(x) = tot(base.at[free_idx].set(x))` over the
ordered 37-free vector with the ten pins fixed bitwise in the base vector, and
constructs `jax.hessian(negll_free)` and `jax.grad(negll_free)` WITHOUT evaluating
them (`derivative_route: loaded=true, evaluated=false` in the dry-run manifest).
Consistency gates at the accepted estimate: |negLL(theta_hat) − 19053.46553160093|
≤ 1e-6 (measured 0.0 in the live dry-run) and, in the real run,
max|grad − published gradient_free_projection| ≤ 1e-6 (S-8 on failure) — the
Phase-3 gates are recomputed only as recorded consistency values, never re-gated.

## 7. Free-parameter Hessian

Real run only: exact `jax.hessian` of negLL over the 37-free vector at the
accepted estimate (float64), stored raw (pre-symmetrization) as both
`hessian_free.csv` (named rows/columns) and `hessian_free.npy`.

## 8. Symmetry gate

`_phase4_symmetry` (G-6, D-4): `max|H − Hᵀ| ≤ 1e-8·max|H|` evaluated BEFORE
symmetrization; the symmetrized `Hs = (H + Hᵀ)/2` feeds all spectral work.
Unit-tested: exact-symmetric pass, above-threshold fail, within-tolerance pass.

## 9. Rank tolerance

`ε_rank = 1e-10 × max|eigenvalue|` (D-3), applied uniformly to the free Hessian
(G-7), the regional design matrix (R-1, relative to its largest singular value)
and the Schur complement (R-4). Unit-tested at the exact threshold value.

## 10. Full-Hessian rank

G-7: eigenvalues of `Hs` via `eigh`; rank = #{eig > ε_rank} must equal **37**;
G-5 PD (`min_eig > 0` strictly) with the `n_nonpos` counter at eig ≤ 1e-8 also
recorded. Unit-tested: full-rank pass, deficient (rank 36) fail, negative-eigen
PD fail.

## 11. Condition-number gate

G-8 three-tier (D-4): ≤ 1e7 clean; 1e7–1e10 warning (recorded, no halt);
> 1e10 hard failure (S-4). Non-PD spectra report condition = ∞ = failure. The
actual value is recorded against the certified pooled baseline anchor 1.295e6.
Unit-tested at 1e6 / 1e8 / 1e11.

## 12. Regional-parameter binding

`_phase4_regional_names` derives the block from the accepted specification — the
free `beta_E_*` covariate parameters (year dummies are pinned; the bare `beta_E`
intercept does not match) — and requires exact ordered agreement with BOTH the
canonical plan list (plan v2 §5/§14, mirrored as the immutable constant) and the
YAML list: `beta_E_gsur, beta_E_drgn2..8, beta_E_drgur, beta_E_drgmd`. Any
conflict raises S-5 `regional-names`; nothing is guessed. Verified live: the real
spec derivation returned exactly these ten. Unit-tested: agreement, config
conflict, extra spec name, missing spec name.

## 13. Regional design rank

R-1 (hard): the 10-column household-level design matrix (`gsur, reg2..reg8,
drgur, drgmd`; columns taken from the hash-authenticated frozen stem, verified
household-constant, one row per `idhh`, shape 1,555 × 10 asserted in the contract)
must have rank 10 under ε_rank; singular values and |corr| > 0.9 pairs are
reported (warning sub-check). Unit-tested: full rank, exact collinearity → rank 9
with the pair flagged.

## 14. Regional Hessian subblock

R-2 (hard): the raw 10×10 regional subblock is extracted from the symmetrized
Hessian, symmetrized again defensively, and must be positive definite
(`min_eig > 0` strictly). Persisted as `regional_hessian_subblock.csv` with
parameter-named rows/columns. Unit-tested pass and (degenerate-pair) fail.

## 15. Conditional Schur complement

R-4 (hard): `S_R = H_RR − H_RO · H_OO⁻¹ · H_OR` computed via the numerically
stable `np.linalg.solve(H_OO, H_OR)` — never an explicit inverse; a singular
solve raises S-5. The plan-v1 `pinv(rcond 1e-10)` construction is recomputed only
as an informational cross-check (`solve_vs_pinv_max_abs_diff`). Gates: rank == 10
under ε_rank AND `min_eig > 0` strictly; full spectrum persisted
(`regional_schur_complement.csv`). R-3 loading shares (regional squared loading
of every eigenvector; warning flag at ≥ 0.5 on the three smallest) are recorded
as warning-only and never gate (D-3). Unit-tested: analytic block-matrix equality
at 1e-10, solve-vs-pinv agreement, rank/min-eig failures, loading-share warning.

## 16. Output transaction

Identical design to Phase 3, on
`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/`: exclusive lock
(same `.phase3.lock` filename via the shared transaction class), uuid4
collision-resistant attempts allocated under the lock, immutable `complete/`,
atomic directory-level publication, dry-run/STOPPED attempts under `attempts/`.
The shared `Phase3Transaction` gained a `success_status` constructor parameter
(default `PHASE_3_COMPLETE`, so Phase-3 behavior is bit-identical; Phase 4 passes
`PHASE_4_COMPLETE`) — a defect the new transaction test caught before any real
run. `_phase4_finalize` preserves the decision-C order: console → artifact hashes
(manifest NEVER self-hashed) → manifest LAST → exact eight-file set check →
atomic publish. Hard gate failures publish STOPPED evidence (S-4 curvature / S-5
regional) with full diagnostics — never a PASS. The post-evaluation input recheck
and runtime-map fingerprint stability run before any artifact write (S-8).

## 17. Dry-run behavior

`--phase 4` without `--execute-phase4` forces the dry-run: full contract
(bundle binding, theta load, regional identification, design validation,
objective consistency, derivative-route construction) and STOPS —
structurally before the evaluation branch. Live canonical dry-run: exit 0,
`PHASE_4_DRY_RUN_COMPLETE`, `hessian_evaluated: false`,
`optimizer_called: false`, `execution_ready: false`,
`review_gate: AWAITING_REVIEW_V6_APPROVE`, negLL(theta_hat) dev 0.00e+00, all
ten regional names identified, no `complete/`, lock released, staging empty.
A real run requires `--execute-phase4` + `_verify_execution_gates` (the same
expected-HEADs / gitlink / full-cleanliness / review-v6 battery as Phase 3);
`_phase4_run` independently refuses an unverified real call before any
transaction.

## 18. Test coverage

Twelve new tests (suite 32 → 44; **44 passed × 3 consecutive runs**, ~20 s each):
33 bundle-hash binding (tamper/missing/status/gates variants); 34 exact
regional-name binding (agreement + three conflict modes); 35 symmetry gate;
36 rank tolerance + full-rank pass/fail + PD/n_nonpos; 37 condition
clean/warning/failure tiers; 38 regional design rank + collinearity flag;
39 Schur analytic correctness + raw-PD pass + solve-vs-pinv; 40 Schur rank and
min-eig failure gates + loading-share warning; 41 Phase-4 transactional
publication, exact eight-file bundle, no manifest self-hash, and complete-result
overwrite refusal; 42 subprocess canonical dry-run proving the Hessian is never
evaluated; 43 phases 5–8 refusal; 44 execute-without-gates refusal (public and
private routes, lock never appears) + YAML/constant equality with mutation
refusals. Test 10 now also covers Phase-4 canonical out/config refusals; test 29
asserts the accepted Phase-3 bundle stays byte-identical under dry-runs. The
37-free mapping battery (tests 01–04) is shared and unchanged. No test evaluates
the real Hessian; the real objective is touched only by the two subprocess
dry-runs (single objective evaluations).

## 19. Phase-3 regression safety

All 32 pre-existing tests pass unchanged except the two documented updates
(tests 10/29, both strengthened, not weakened). The Phase-3 code paths are
untouched except: the transaction `success_status` parameter (default preserves
Phase-3 behavior exactly — proven by the unchanged transaction battery 14/15/16
and 31/32) and the new `--execute-phase4` CLI flag. The accepted `complete/`
bundle re-verified byte-identical (deterministic hash `2cf23764…`) inside every
suite run. Live checks: canonical Phase-3 dry-run route exercised via test 29
(exit 0, non-optimizing); nested monorepo clean; certified baseline spec and
warm-start hashes re-authenticated in every contract run.

## 20. Prohibited-operation audit

No real Phase-4 Hessian evaluated (structural dry-run + manifest flags + test
42). No optimizer invoked anywhere (Phase 4 has no scipy import; FakeMin
monkeypatching covers the Phase-3 estimator tests). No theta altered (read-only
bundle binding; pins bitwise-verified). No clustered inference/SE (no scores,
no sandwich — Phase 5 refused). No post-estimation/welfare/synthetic
recovery/notebooks. dclaborsupply-monorepo unmodified and clean. Nothing
committed; no history touched. Validation wrote only new attempt evidence under
`phase4_curvature_v1/attempts/` and the never-delete Phase-3 dry-run bundles
from test 29.

## 21. Git diff summary

```text
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml |  +31/−0
 M scripts/p2a/run_p2a_regionlive_rebuild.py          | +715/−5
 M tests/p2a/test_p2a_regionlive_phase3_safety.py     | +273/−3
 ?? docs/France_case/P2a/FR_P2a_region_live_phase4_implementation_report_v1.md
 ?? outputs/.../phase4_curvature_v1/attempts/…  (dry-run + 1 STOPPED bundle)
 ?? outputs/.../phase3_estimation_v1/attempts/… (test-29 dry-run bundles)
```

`git diff --check` exit 0; HEAD `c7d558a` untouched; both worktrees otherwise
clean; nested repo clean at `27756a0`.

## 22. Residual warnings

- The first Phase-4 dry-run attempt is a preserved `STOPPED` bundle: the initial
  csv/json theta equality check was bitwise and tripped on the accepted CSV's
  pandas ~16-digit formatting (≤1 ulp on 15 of 47 values). Resolved by making the
  JSON theta authoritative (bitwise-bound to diagnostics `final_theta` + SHA)
  with a 1e-12 relative CSV cross-check; the STOPPED evidence is retained under
  the never-delete discipline.
- The plan-v1 text specifies the Schur complement via `pinv(rcond 1e-10)`; the
  task directive requires a stable solve. The solve is the implemented gate; the
  pinv construction is recorded as an informational cross-check so review can
  compare both (agreement asserted < 1e-8 in the analytic unit test).
- R-3 threshold-direction wording differs across sources (plan v2: warning flag
  at share ≥ 0.5; the task prompt: "values below 0.5 are a warning only"). The
  implementation follows plan v2/D-3 (flag at ≥ 0.5, matching the flat-direction
  narrative), records all raw shares so either reading is auditable, and in all
  cases the diagnostic is warning-only and never gates.
- The Phase-4 lock file retains the shared `.phase3.lock` filename (same
  transaction class, separate root). Functionally isolated; a rename was not
  worth divergent transaction code.
- Estimated real-run cost is modest (37 forward-over-reverse passes over the
  1,555×101 objective); the wall time will be recorded in the manifest.

## 23. Whether independent review may begin

**YES.** The implementation is complete, statically clean, dry-run-validated
end-to-end against the real accepted bundle, and every gate is deterministically
unit-tested; no real Hessian has been evaluated, preserving the review's ability
to gate the first real Phase-4 run.

## 24. Immediate next action

Independent Phase-4 review of this diff. On approval: commit, then execute the
single real Phase-4 run via
`--phase 4 --execute-phase4 --expected-mnl-head <post-commit SHA>
--expected-dclaborsupply-head 27756a0… --approved-review …code_review_v6.md
--approved-review-sha256 <committed hash>`, and bring the resulting curvature /
rank / regional-identification verdict (PASS = real-data LOCAL identification
only, D-7 — no synthetic-recovery claim) back for the Phase-5 decision.

**FINAL VERDICT: READY FOR INDEPENDENT PHASE-4 REVIEW** (no real Hessian; no
optimizer; nothing committed).
