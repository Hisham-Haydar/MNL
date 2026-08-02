# FR P2a Region-Live — Phase-5 Inference Implementation Report — v1

**Mission:** JMP-M05B — Phase-5 Inference Implementation and Certification, ledger stages **I-1 (implementation)** and **I-2 (deterministic tests)**
**Binding design:** `FR_P2a_region_live_phase5_inference_design_v4.md` (+ methods review v1, recheck v1, micro-recheck v2, deputy acceptance v1, PI disclosure determination v1)
**Date:** 2026-08-01
**Target repository path:** `MNL/docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md`
**Commit status:** **UNCOMMITTED**, as are all new files at this stage.

**Scope actually performed:** implementation and deterministic tests only. **No commit. No full dry run. No real run. No inference results of record.** No accepted artifact, θ̂, pin, bound, datum, or package file was modified.

---

## 1. Verdict

**IMPLEMENTATION COMPLETE — TEST FLOOR GREEN — READY FOR STAGE I-3 (independent code review).**

All sixteen charter §8 minimum tests are implemented and passing, together with additional coverage: **53 tests, 53 passed, 0 failed**. No charter §15 halt fired. Three interpretation points and one scope observation are flagged in §7 and are **not** resolved by improvisation.

---

## 2. Binding-state verification (performed before any code was written)

| Object | Required | Observed | Result |
| --- | --- | --- | --- |
| MNL HEAD | `983a2ecf1d16592b9f90085f6a6b690b8a964110` | identical | PASS |
| MNL worktree at session start | clean | clean | PASS |
| `Job_Market_paper` HEAD | `7195fc50f6a73e20bdf62fc4baae48c18dedd345` | identical | PASS |
| `Job_Market_paper` worktree | clean | clean | PASS |
| Nested `dclaborsupply` gitlink | `27756a06ea189339aa82915ed2124628afed20eb` | identical | PASS |
| Numerical anchor is ancestor of HEAD | `982c5221…` ⊂ HEAD | verified; delta is **11 documentation files only** | PASS |
| Phase-3 bundle | `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` | rehashed identical | PASS |
| Phase-4 bundle | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` | rehashed identical | PASS |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | rehashed identical | PASS |

Rehash used the accepted manifest-excluded hash-of-hashes verbatim. The anchor→HEAD delta is exactly the 11 Phase-5 evidence files recorded in ledger §1; no source, config, spec or theta file changed.

---

## 3. Architecture

Charter §7 permits *"one Phase-5 runner **or** a narrowly integrated Phase-5 branch in the existing P2a runner."* **A separate Phase-5 runner was chosen.** Grounds:

- the existing runner `run_p2a_regionlive_rebuild.py` refuses `--phase > 4` by design and is the file the Phase-3 review-v6 and Phase-4 review-v7 approved; editing it would change an approved, hash-recorded object for no scientific gain;
- the charter §15 halt *"unrelated dirty worktree"* and the requirement that no accepted artifact change are both satisfied trivially by adding files;
- the Phase-3/4 contract is nevertheless **reused verbatim by import**, not re-implemented, so no likelihood or loader logic is duplicated (charter §7 final clause).

`_phase5_contract` calls `p34._phase4_contract`, which itself reruns the **entire Phase-3 contract** (ten authenticated inputs, spec ordering, pin identity, round-trips, loader structure, prior-correction identity), rebinds the immutable Phase-3 bundle, and revalidates θ̂, the pins and the published free gradient. Phase 5 then adds only what is new: the Phase-4 bundle, the 47→37→35 name-keyed map with its T-17 fingerprints, and the authoritative bread.

---

## 4. File inventory with SHA-256

All five are **uncommitted**. Four are new; `.gitignore` is the only modified tracked file.

| # | Path | Status | SHA-256 |
| --- | --- | --- | --- |
| 1 | `scripts/p2a/phase5_inference.py` | **new** — pure helpers | `1a442fea1b6ee2ab4f5b5b25d87a477258e76698c630382e5d2530297529a757` |
| 2 | `scripts/p2a/run_p2a_phase5_inference.py` | **new** — runner | `932bc953d374d5ab641f556a6da432ead5667cfa943d1a8365dc3349dc5928b3` |
| 3 | `scripts/p2a/configs/p2a_phase5_inference_v1.yaml` | **new** — Phase-5 config | `3f9e43286057f9d16daa4078064b972600aa0ddb0000ba4eaa1e48882c0581a4` |
| 4 | `tests/p2a/test_p2a_regionlive_phase5_inference.py` | **new** — 53 tests | `e432561fe7d41ce2092a95f065962cc4d74260834a532abd65f00cce4686ad70` |
| 5 | `.gitignore` | **modified** — restricted-custody coverage | `09e1945563b082d75f63f18f7c9164be4a4c84f407dc06bffc66634d3b5503d5` |
| 6 | `docs/France_case/P2a/FR_P2a_region_live_phase5_implementation_report_v1.md` | **new** — this report | *(self)* |

**A separate Phase-5 config was created rather than extending the Phase-3/4 canonical config**, so that `p2a_regionlive_rebuild_v1.yaml` — an object the accepted reviews bind to — is byte-unchanged. The Phase-5 runner loads it read-only.

---

## 5. Helper → design-section map

Every helper is pure in the charter §7 sense: explicit inputs, explicit record out, no transaction I/O, no accepted-artifact access.

| Charter §7 category | Helper | Design section |
| --- | --- | --- |
| parameter mapping | `build_phase5_parameter_map` | §7.2 (three index spaces, by name) |
| | `parameter_order_fingerprints`, `check_parameter_order_fingerprints` | §7.4 — **T-17** |
| | `restrict_by_name` | §7.2 / §8.1 (name-keyed, never positional) |
| canonical score ordering | `canonical_row_order` | §6.3 — **D-7**, `idhh`-ascending stable argsort |
| | `check_cluster_contract` | §6.1 — **T-3** |
| score aggregation | `build_score_matrix` | §5.4 — `jacfwd`, household-blocked |
| | `chunk_route_invariance` | §14 — **T-11** |
| | `jacrev_subset_scores`, `mode_agreement` | §5.4 / §14 — **T-16** |
| | `check_score_matrix` | §14 — **T-2** |
| | `score_identity` | §5.3 / §14 — **T-1**, **T-4** |
| | `centring_diagnostic` | §9.2 — **W-5** |
| bread construction | `load_bread` | §8.1 — **T-5**, loaded not recomputed |
| | `symmetrise_bread` | §8.1 — **T-6**, mandatory symmetrisation |
| | `cholesky_bread` | §8.3 |
| restricted meat | `build_meat` | §9.1 (exact by-name column selection) |
| | `meat_psd_gate` | §15 / §16.2 — **T-7**, certified `κ_BE` |
| finite-sample correction | `finite_sample_correction` | §10 — **T-10**, **D-1**, CR0 retained |
| covariance diagnostics | `build_covariances` | §8.2 / §9.1 — **T-8**, solves only |
| | `covariance_validity` | §15 — **T-9** |
| | `correlation_matrix` | §15 — **T-18** |
| | `effective_rank` | §15 — **W-3** |
| | `robust_model_ratio` | §13.6 — **W-1** |
| | `stationarity_gate` | §11.5 — **T-19** |
| | `kkt_activity_gate` | §11.5 — **T-22** |
| | `near_boundary_warning` | §11.5 / §16.2 — **W-4** |
| regional selectors / restrictions | `regional_selector` (`E_R ∈ ℝ^{10×35}`) | §13.4 |
| | `restriction_rows` (`A ∈ ℝ^{q×10}`) | §13.4 |
| | `wald_statistic`, `regional_tests` | §13.4 — **T-14**, `p_model`/`p_robust` |
| | `regional_eigen_report` | §13.5 — **W-2** |
| | `individual_diagnostics` | §13.3 |
| reporting-table population | `build_parameter_table`, `validate_parameter_table` | §17.3 — 47 rows × 13 columns |
| | `check_pin_gradients`, `PIN_CATEGORIES`, `PIN_TABLE_FOOTNOTE` | §12.3–§12.5 — **D-4** |
| disclosure / custody metadata | `custody_metadata`, `custody_gate` | §17.1 / §18.5 — **T-23** |
| | `assert_restricted_path_outside_git` | PI determination v1 |
| manifest and bundle hashing | `phase5_bundle_hash`, `check_bundle_membership` | §17.2 (Phase-4 algorithm verbatim) |
| runtime / scope gates | `check_x64_enabled` | §14 — **T-15** |
| | `NoOptimizerGuard` | §14 — **T-20** |
| | `fresh_process_reproduction` | §14 / §16.3 — **T-12** |
| register | `summarise_gates`, `GATING_TIERS`, `HALT_REGISTER` | §14–§16, §18.6 |

**Gate coverage: T-1 … T-20, T-22, T-23 (22 gating) and W-1 … W-5 (5 warning) — all implemented as formulas from design v4 §14–§16.** Design v4 defines no T-21; its absence is asserted by test 16c. Warnings never gate (`summarise_gates`).

Frozen constants implemented literally: `atol=rtol=1e-8`; T-4 `1e-12` **signed max-norm** (a *sum*, not a difference); asymmetry threshold `2.3588019878151842e-4`; rank convention `1e-10`; T-9 set **equal to** the rank convention, never looser; **`κ_BE_certified = 6.0424e-12`**, upward-rounded from the exact `κ_BE = K·G·u/(1−G·u) = 6.042388811523458e-12` and 16.55× tighter than `1e-10`; `c = 1555/1520 = 1.0230263157894737`; `z₀.₉₇₅ = 1.959963984540054`; χ² 95 % criticals 18.3070 / 14.0671 / 5.9915 / 3.8415.

---

## 6. Test-by-test results

Command: `python -m pytest tests/p2a/test_p2a_regionlive_phase5_inference.py -v`
Result: **53 passed, 0 failed, 10.52 s.** Full output is attached to the return packet.

| Charter §8 item | Tests | Result |
| --- | --- | --- |
| 1 — exact 47/37/35 map and fingerprints | `01`, `01b`, `01c`, `01d` | **PASS** — counts, in-place free order, pins `{10–17,31,32}`, active `{2,6}`, by-name projections; T-17 bound to `phase4_manifest → contract.parameter_map`; positional-agreement-without-name-agreement rejected |
| 2 — active-bound / pin status | `02`, `02b`, `02c` | **PASS** — both at **upper** 1.0, `dist_ub = 0`, μ > 0; ten pins carry exactly-zero gradient; **no normalisation category**; T-22 ratios reproduce 7,683 / 13,356 |
| 3 — cluster count and canonical order | `03`, `03b` | **PASS** — stable argsort, permutation-invariance of `Σs_g` and `Σs_g s_g′`; G = 1,555 asserted **explicitly** (never the library's P3a-pooled `9657`); 157,055 rows |
| 4 — synthetic score-identity fixture | `04`, `04b` | **PASS** — T-1/T-4 on a synthetic S, and under **real forward AD** through the iota (T-16 and T-11 exactness also shown) |
| 5 — production-route score aggregation | `05` | **PASS** — real spec + `load_singles` + `build_jax_singles_ll(per_group=True)` on **4 households**; identity holds; `per` ≤ 0 and `−Σper = negLL`; `cluster_id == idhh`. **The 1,555-household scoring was not run.** |
| 6 — bread hash and symmetrisation | `06`, `06b`, `06c` | **PASS** — hash, raw asymmetry `1.819e-12` matching Phase 4, min/max eig and condition reproduce to `rtol 1e-10`, rank 37, Cholesky; CSV shown non-round-tripping [F-4]; tampering rejected |
| 7 — PSD / backward-error incl. certified T-7 | `07`, `07b`, `07c` | **PASS** — exact `κ_BE` derived and shown ≠ leading-order `K·G·u`; certified constant ≥ exact with margin < 1.2e-17; 16.55×; T-9 tolerance = rank convention |
| 8 — covariance algebra and correction | `08`, `08b`, `08c` | **PASS** — `c = 1555/1520`, telescoping exact, +1.1448 %; N = 157,055 **rejected**; solves vs `inv`/`pinv`; CR0 recoverable as `V_robust/c`; no sample scaling (average-scale form identical); T-19 |
| 9 — regional restriction dims and name-keying | `09`, `09b` | **PASS** — `E_R` 10×35 at interior 13–22, `A` q×10, `R = A E_R` q×35; `gsur` stated separately, in neither H0-B nor H0-C; separate `p_model`/`p_robust`; criticals verified; rank-deficient `V_RR` halts |
| 10 — NA reporting contract | `10`, `10b`, `10c` | **PASS** — 13 columns in order, **no `flag`**, 47 rows; literal `"NA"` in the five inferential fields for all 12 non-interior rows; pinned `grad_negll` structurally 0.0 and **never** SE 0; footnote names `theta_l_m`; W-4 triggers on **equality** |
| 11 — custody metadata and T-23 | `11`, `11b`, `11c`, `11d` | **PASS** — all custody fields; row/column fingerprints (column == T-17 value); every missing field halts; `committed_to_git=True` halts; store proven outside both Git trees; `.gitignore` verified by `git check-ignore`; closed bundle membership, manifest self-excluded |
| 12 — no optimizer / respecification / welfare / EUROMOD | `12`, `12b`, `12c`, `12d` | **PASS** — guard traps `scipy.optimize.minimize` and restores it; prohibited modules refused; **token-level** source scan (comments/strings stripped) finds no forbidden route, no `jax.hessian`, no `scipy.optimize` import |
| 13 — transaction and failure preservation | `13`, `13b`, `13c` | **PASS** — `attempts/dryrun_<ts>…_STOPPED` preserved, lock exclusion, prior attempts never overwritten, exception-evidence policy, custody locator redacted |
| 14 — review binding and revision gates | `14`, `14b`, `14c`, `14d`, `14e` | **PASS** — §18.1 gate implemented: **the dry run refuses to start** without HEADs, clean worktrees and the Phase-5 review path/hash/APPROVE; Phase-3 review-v6 and Phase-4 review-v7 explicitly rejected as authorizers; live HEAD/gitlink/bundles re-verified; Phase-3/4 runner and config proven unmodified |
| 15 — dry run cannot publish `complete/` | `15`, `15b` | **PASS** — `finish("PHASE_5_COMPLETE")` raises unconditionally; dry-run status is deliberately **not** the success status, so it always routes to `attempts/`; no `complete/` exists |
| 16 — real run refused pending authorization | `16`, `16b`, `16c` | **PASS** — no `--execute*` flag exists; `"real"` is not a mode; `refuse_real_run` raises; **flipping `PHASE5_REAL_RUN_AUTHORIZED` fails closed** (every mode refused), so enabling a real run requires a reviewed code change, not a flag |
| additional | `17`–`22` | **PASS** — T-12 never silently downgrades; warnings never gate; meat invariant to score sign and row order; helper-category completeness; **`21`: full contract bound against the real accepted state**; `22`: nothing written, accepted artifacts unchanged |

**Test 21 is the integration proof.** It calls `_phase5_contract` directly — no transaction, no lock, no staging, no artifact, no score, nothing written — and asserts against the *real* accepted state: Phase-4 bundle hash, T-5 across all five anchors, T-6 with the Phase-4 eigenvalues, T-15, T-17, T-3 (G = 1,555, 157,055 rows), regional free positions 15–24 and interior 13–22, group counts **714/841**, strictly increasing cluster ids, `negLL(θ̂) = 19053.46553160093` to `1e-6`, and `sha256(θ̂ bytes) = c024b893…`. Those values cannot be produced without a genuine end-to-end contract execution.

### Regression check on the pre-existing suites

`python -m pytest tests/ --deselect …::test_29 --deselect …::test_42` → **113 passed, 2 deselected.**

Both deselections are **pre-existing tests that write production attempt bundles into the accepted output tree**, which would dirty the worktree (a charter §15 halt). Additionally, `test_42_phase4_subprocess_dry_run_never_evaluates_hessian` **fails at HEAD independently of this work**: its final assertion is `not (phase4_curvature_v1/complete).exists()`, but that directory is the *accepted Phase-4 bundle*, committed at the numerical anchor `982c522`. The test went stale when Phase 4 was accepted. **This is reported, not fixed** — it is unrelated to Phase 5 and repairing an accepted committed test is outside this mission's scope.

One consequence was cleaned up: running `test_42` once created two untracked Phase-4 dry-run attempt directories. They were removed, restoring the exact starting state. They were incidental to a test invocation, not evidence of any authorized run.

---

## 7. UNKNOWNs, ambiguities and interpretations — flagged, not improvised

**A-1 — Chunking is a memory knob, not a work reduction, under forward mode.** Design §5.4's memory argument is stated against *reverse* mode. In forward mode `jacfwd` over a household chunk still costs 37 JVPs over that builder's full data, so *C* sub-chunks multiply compute by ≈ *C*. The implemented baseline is therefore `chunk_size: 0` — one chunk per builder (714 and 841), the natural household-blocked partition — with T-11 comparing it against `chunk_size = 128`. The design permits this: T-11 reads *"**if** chunked."* **No design deviation; an implementation-level observation for the reviewer.**

**A-2 — Bundle membership under restricted custody.** Design §17.2 lists `phase5_scores_free.npy` as a member of the `complete/` bundle; PI determination v1 forbids household-level bytes in any Git tree. Implemented: restricted members live in the restricted store, and their `name:sha256` entries are folded into the **same** hash-of-hashes, so bundle membership stays *closed* and the restricted bytes stay bound to the bundle hash. **Interpretation — requires manager confirmation.**

**A-3 — `phase5_score_row_index.csv` classified as restricted.** Design §17.2 marks it authoritative and committed. It is a 1,555-row vector of household identifiers, i.e. row-level microdata-derived output, which PI determination v1 covers. It was classified **restricted**. **Interpretation — requires a manager ruling**; reclassifying it is a one-line change to `PHASE5_RESTRICTED_ARTIFACTS`.

**A-4 — W-2 "weakest direction" of `V_RR`.** Design §13.5 motivates W-2 from the regional *design*'s smallest singular value. For `V_RR`, a **covariance**, the least-well-supported direction is the one with the **largest** eigenvalue. `regional_eigen_report` reports the full spectrum and names the dominant loading of the largest-eigenvalue direction. **Interpretation, stated so the reviewer can overrule.**

**A-5 — `complete/` is never created, by design of this stage.** Design §17.2 writes the bundle to `complete/`; charter §11/§15 forbid creating or promoting it. `Phase5Transaction.finish` refuses unconditionally. The charter governs; recorded for completeness.

**A-6 — Phase-4 contract constructs, but never evaluates, `jax.hessian`/`jax.grad`.** Reusing `_phase4_contract` verbatim means those closures are *built*. Phase 5 discards both immediately (`ctx.pop`), records `phase4_derivative_routes_discarded: true` and `bread_recomputed: false`, and evaluates neither. **No Hessian is recomputed** (design §2, plan §2.5).

**A-7 — Permanent inherited UNKNOWNs are now closed going forward.** Phase-3/4 JAX/jaxlib versions, platform and thread/XLA flags remain unrecoverable [audit §19]. The Phase-5 manifest records all of them plus peak memory and chunk size (§18.5). Observed here: Python 3.12.2, NumPy 2.3.5, pandas 2.3.3, SciPy 1.16.2, **JAX 0.10.1, jaxlib 0.10.1**, Windows-2022Server-10.0.20348-SP0, AMD64.

**A-8 — Not exercised at this stage:** `_phase5_evaluate` and `_finalize` end-to-end. That *is* the full 1,555-household dry run, which this stage forbids. Every constituent helper is unit-tested, and the contract that feeds them is integration-tested (test 21). **First end-to-end exercise is ledger stage I-6.**

---

## 8. Confirmation that nothing accepted changed

Asserted in code (`test_14c`, `test_22`) and verified at the shell:

- `scripts/p2a/run_p2a_regionlive_rebuild.py` — unmodified
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` — unmodified
- `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` — unmodified
- `theta_p2a_singles_2016_v1.csv` — unmodified
- `phase3_estimation_v1/complete/`, `phase4_curvature_v1/complete/` — unmodified; both bundles rehash to their accepted values
- **`dclaborsupply-monorepo` — not modified in any way; inspected read-only.** No E2 package-modification need arose, and no `PKG-M02` deficiency was identified.
- No θ̂, pin, bound, draw, pricing or input datum touched.
- No `complete/` created or promoted anywhere.

### Worktree status at return

```
MNL  (C:\Users\hisham\Repo\MNL)         HEAD 983a2ecf1d16592b9f90085f6a6b690b8a964110
 M .gitignore
?? scripts/p2a/configs/p2a_phase5_inference_v1.yaml
?? scripts/p2a/phase5_inference.py
?? scripts/p2a/run_p2a_phase5_inference.py
?? tests/p2a/test_p2a_regionlive_phase5_inference.py
   (+ this uncommitted report)

dclaborsupply-monorepo                   HEAD 27756a06ea189339aa82915ed2124628afed20eb
   clean — no modification of any kind

Job_Market_paper                         HEAD 7195fc50f6a73e20bdf62fc4baae48c18dedd345
   clean — untouched by this mission stage
```

The only tracked-file modification is `.gitignore`, which the prompt explicitly requires ("ensure .gitignore coverage"). It adds restricted-custody patterns and changes no behaviour.

---

## 9. Halt-condition report

No charter §15 halt fired.

| Halt | Status |
| --- | --- |
| source/bundle/revision mismatch | not triggered — all anchors verified twice |
| score-identity failure | not triggered — T-1/T-4 pass synthetically, under real AD, and on the production route |
| parameter-order ambiguity | not triggered — two independent sources agree by name; T-17 binds them |
| need to change likelihood/model/specification | not triggered |
| package-modification requirement | not triggered — inspection only |
| T-1…T-23 implementation ambiguity | not triggered — see §7 A-1…A-4 for interpretations that do **not** rise to ambiguity halts |
| disclosure/custody infeasibility | not triggered — durable store outside all Git trees; unconfigured store is itself a halt |
| any path creating/promoting `complete/` | not triggered — refused in code |
| unrelated dirty worktree | not triggered — both trees clean apart from intended files |
| no commit / no full dry run | honoured |

---

## 10. Next authorized action

Ledger stage **I-3**: independent code review by **Codex 5.6, maximum reasoning, read-only**, producing `docs/France_case/P2a/FR_P2a_region_live_phase5_code_review_v1.md` with first heading `# 1. Phase-5 review verdict` and one exact `**FINAL VERDICT: APPROVE**` line — the form the implemented gate parser requires. The reviewer should rule explicitly on **A-2, A-3 and A-4**.

Only after review APPROVE come I-5 (exact-state commit) and I-6 (the single full dry run). **The production real run remains refused by construction and is the deputy programme director's decision alone.**
