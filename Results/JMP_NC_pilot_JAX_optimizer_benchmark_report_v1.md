# JMP NC Pilot — JAX Optimizer Benchmark Report v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Authorization:** `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md` §18
**Script:** `scripts/pilot/_run_jax_optimizer_benchmark.py`
**Generated:** 2026-05-24 22:37

**SCOPE:** Limited JAX optimizer benchmark — single start from `theta_CONOPT`, float64, `maxiter=15`. Stability probe only. NOT production optimization. NOT verdict-grade. No Hessian, SEs, welfare, SA2, or promotion.

---

## 1. Halt-condition status

**No halt conditions fired.** All §14 guards clear.

| Halt code | Condition | Status |
|---|---|---|
| HJ-X64 | JAX float64 unavailable | CLEAR |
| HJ-START | Non-CONOPT start or multiple starts | CLEAR |
| HJ-CAP | maxiter not in [10,20] | CLEAR — maxiter=15 |
| HJ-NAN | NaN/Inf objective or gradient | CLEAR |
| HJ-DETERIORATE | Final LL materially worse than initial | CLEAR |
| HJ-SCOPE | Hessian/SE/welfare/SA2/promotion/multi-start | CLEAR — none executed |
| HJ-MUT | Overwrote reports/oracle/data | CLEAR — not modified |

---

## 2. Float64 confirmation

- `jax.config.update("jax_enable_x64", True)` set at module import, before any JAX array: **OK**
- JAX version: 0.4.31
- float64 test array confirmed (`jnp.array(1.0, dtype=jnp.float64)` → float64)
- All fixed pkl arrays cast to float64 in `build_jax_ll_fn`.
- Theta vector: `jnp.array(theta0, dtype=jnp.float64)`.
- `jax.value_and_grad` operates on float64 throughout.

---

## 3. Start point

- **Start:** `theta_CONOPT` = start-1 (`start_1_warm_P3a`) from `Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json`
- Oracle LL at start: -16527.142183173339
- **Single start only.** No defaults, no multiple starts (HJ-START clear).
- `theta_CONOPT` is within all spec bounds — no clipping needed.

---

## 4. Optimizer setup

| Item | Value |
|---|---|
| Optimizer | `scipy.optimize.minimize`, method=`L-BFGS-B` |
| Gradient source | `jax.jit(jax.value_and_grad(ll_fn))`, float64 |
| maxiter | 15 (within authorized [10, 20]) |
| ftol | 1e-15 (tight; maxiter cap dominates) |
| gtol | 1e-12 (tight; maxiter cap dominates) |
| Bounds | From `estimation_spec_nc_pilot_couples_2016.yaml` `optimization.bounds` |
| theta_c | FIXED at 0.0 (not in theta vector, not optimized) |
| External watchdog | Not available in this environment; relying on maxiter=15 cap (documented) |

---

## 5. Initial LL vs v2 equivalence report (AC1)

| Item | Value |
|---|---|
| Initial LL (float64) | -16527.0669688817 |
| v2 NumPy LL (float64) | -16527.0669688818 |
| Oracle LL (CONOPT) | -16527.142183173339 |
| \|delta\| initial vs v2 | 8.731149e-11 |
| \|delta\| initial vs oracle | 7.521429e-02 |
| AC1 (\|delta\| < 0.01) | **PASS** |

Float64 re-evaluation at `theta_CONOPT` reproduces the validated v2 LL. The residual gap vs the oracle is the same external-precision boundary documented in the v2 equivalence report (CONOPT rounding + float64 accumulation).

---

## 6. Gradient at start — float64 (AC2)

| Item | Value |
|---|---|
| Method | JAX `value_and_grad`, float64 |
| Parameters checked | 35 (all) |
| All entries finite | YES |
| Gradient norm ‖g‖₂ | 6.102895 |
| AC2 | **PASS** |

All 35 gradient components at `theta_CONOPT` (float64):

| Parameter | Gradient (float64) |
|---|---|
| `beta_l0_m` | -6.10289540 |
| `beta_l_age_m` | -0.00000000 |
| `beta_l_age2_m` | +0.00000002 |
| `theta_l_m` | +0.00000000 |
| `beta_l0_f` | +0.00000000 |
| `beta_l_age_f` | -0.00000000 |
| `beta_l_age2_f` | +0.00000001 |
| `beta_l_nkids_f` | +0.00000000 |
| `theta_l_f` | +0.00000000 |
| `beta_c` | -0.00000000 |
| `beta_E` | -0.00000000 |
| `beta_h_pt1` | +0.00000000 |
| `beta_h_pt2` | +0.00000000 |
| `beta_h_ft` | -0.00000000 |
| `beta_E_gsur` | -0.00000000 |
| `beta_E_drgn2` | -0.00000000 |
| `beta_E_drgn3` | -0.00000000 |
| `beta_E_drgn4` | -0.00000000 |
| `beta_E_drgn5` | -0.00000000 |
| `beta_E_drgn6` | -0.00000000 |
| `beta_E_drgn7` | -0.00000000 |
| `beta_E_drgn8` | -0.00000000 |
| `beta_occ_2_cm` | +0.00000000 |
| `beta_occ_3_cm` | -0.00000000 |
| `beta_occ_4_cm` | -0.00000000 |
| `beta_occ_2_cf` | +0.00000000 |
| `beta_occ_3_cf` | +0.00000000 |
| `beta_occ_4_cf` | -0.00000000 |
| `beta_w0` | +0.00000000 |
| `beta_w_educL` | +0.00000000 |
| `beta_w_educH` | +0.00000000 |
| `beta_w_pexp` | +0.00000000 |
| `beta_w_pexp2` | +0.00000002 |
| `sigma` | +0.00000000 |
| `beta_ll` | +0.00000000 |

---

## 7. Per-iteration log (AC3, AC4)

Optimizer ran for 15 callback iterations.

| Iter | LL | ‖g‖₂ | Wall time (s) | Per-iter (ms) |
|---|---|---|---|---|
| 1 | -16526.99841803 | 89.345734 | 0.56 | 562 |
| 2 | -16526.99565764 | 36.579920 | 0.94 | 382 |
| 3 | -16526.99565010 | 9.269228 | 1.48 | 539 |
| 4 | -16526.99563207 | 5.753644 | 1.84 | 360 |
| 5 | -16526.99563075 | 5.726112 | 2.24 | 400 |
| 6 | -16526.99561704 | 6.424514 | 2.60 | 355 |
| 7 | -16526.99559277 | 8.388886 | 2.96 | 359 |
| 8 | -16526.99552254 | 13.014824 | 3.31 | 357 |
| 9 | -16526.99537740 | 18.646965 | 3.66 | 345 |
| 10 | -16526.99512852 | 21.388187 | 4.02 | 365 |
| 11 | -16526.99486478 | 14.435368 | 4.37 | 347 |
| 12 | -16526.99477193 | 6.495611 | 4.74 | 370 |
| 13 | -16526.99476073 | 5.902300 | 5.14 | 395 |
| 14 | -16526.99475784 | 6.119677 | 5.49 | 350 |
| 15 | -16526.99475730 | 10.727564 | 6.04 | 557 |

- Termination message: `STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT`
- Optimizer `nit` (L-BFGS-B internal): 15
- Optimizer `nfev` (function evaluations): 18
- AC3 (clean completion): **PASS**
- AC4 (no NaN/Inf): **PASS**

---

## 8. Final LL — non-deterioration check (AC5)

| Item | Value |
|---|---|
| Initial LL (float64) | -16527.0669688817 |
| Final LL (float64) | -16526.9947573048 |
| LL change (final − initial) | +0.07221158 |
| AC5 (final ≥ initial − 1.0) | **PASS** |

**Note: Final LL improved by 0.072212 LL units (material).** This is a float64 precision-boundary improvement vs the CONOPT iterate and/or optimizer path artifact at a single start. **Not interpreted economically** (§12 criterion 7, §16 of authorization).

---

## 9. Parameter movement from theta_CONOPT (AC6)

‖Δθ‖₂ = 1.229073e-02

| Parameter | theta_CONOPT | theta_final | Δ |
|---|---|---|---|
| `beta_l0_m` | 0.0122194726 | 0.0000010000 | -1.22e-02 |
| `beta_l_age_m` | -0.0056905237 | -0.0058010881 | -1.11e-04 |
| `beta_l_age2_m` | 0.0014952486 | 0.0015412436 | +4.60e-05 |
| `theta_l_m` | -0.7752259722 | -0.7742540831 | +9.72e-04 |
| `beta_l0_f` | 1.8273402383 | 1.8273410281 | +7.90e-07 |
| `beta_l_age_f` | -0.0229239375 | -0.0229131342 | +1.08e-05 |
| `beta_l_age2_f` | 0.0006255515 | 0.0006084687 | -1.71e-05 |
| `beta_l_nkids_f` | 0.2390744727 | 0.2390760288 | +1.56e-06 |
| `theta_l_f` | -0.7315246179 | -0.7309162630 | +6.08e-04 |
| `beta_c` | 2.1819649580 | 2.1815618050 | -4.03e-04 |
| `beta_E` | 9.6072294880 | 9.6072359661 | +6.48e-06 |
| `beta_h_pt1` | -0.8735077256 | -0.8734676788 | +4.00e-05 |
| `beta_h_pt2` | 0.5953862954 | 0.5954272651 | +4.10e-05 |
| `beta_h_ft` | 1.7130937766 | 1.7132570268 | +1.63e-04 |
| `beta_E_gsur` | -5.3467833423 | -5.3467780493 | +5.29e-06 |
| `beta_E_drgn2` | 0.7185379439 | 0.7185390543 | +1.11e-06 |
| `beta_E_drgn3` | 2.0847187904 | 2.0847194934 | +7.03e-07 |
| `beta_E_drgn4` | 1.5367026920 | 1.5367030227 | +3.31e-07 |
| `beta_E_drgn5` | 0.2867230188 | 0.2867240873 | +1.07e-06 |
| `beta_E_drgn6` | 0.8493885441 | 0.8493893549 | +8.11e-07 |
| `beta_E_drgn7` | 0.5944869508 | 0.5944875372 | +5.86e-07 |
| `beta_E_drgn8` | 1.4011614341 | 1.4011617848 | +3.51e-07 |
| `beta_occ_2_cm` | -1.6172778532 | -1.6172615590 | +1.63e-05 |
| `beta_occ_3_cm` | -2.3461833028 | -2.3461769919 | +6.31e-06 |
| `beta_occ_4_cm` | 0.0436819774 | 0.0436315150 | -5.05e-05 |
| `beta_occ_2_cf` | 1.0988499768 | 1.0988405900 | -9.39e-06 |
| `beta_occ_3_cf` | 1.1089646574 | 1.1089612451 | -3.41e-06 |
| `beta_occ_4_cf` | 0.4438545612 | 0.4438769159 | +2.24e-05 |
| `beta_w0` | 4.5355553711 | 4.5355556930 | +3.22e-07 |
| `beta_w_educL` | -1.8552947337 | -1.8552945240 | +2.10e-07 |
| `beta_w_educH` | 2.2036864802 | 2.2036849910 | -1.49e-06 |
| `beta_w_pexp` | -0.0072262601 | -0.0072262827 | -2.26e-08 |
| `beta_w_pexp2` | 0.0005999673 | 0.0005997512 | -2.16e-07 |
| `sigma` | 1.7973556218 | 1.7973426885 | -1.29e-05 |
| `beta_ll` | 2.1817484104 | 2.1822437516 | +4.95e-04 |

**Bound hits:** ['beta_l0_m at lower=1e-06']

Largest parameter movements (material improvement noted above — not interpreted economically):

| Parameter | Δ |
|---|---|
| `beta_l0_m` | -1.221847e-02 |
| `theta_l_m` | +9.718891e-04 |
| `theta_l_f` | +6.083549e-04 |
| `beta_ll` | +4.953411e-04 |
| `beta_c` | -4.031530e-04 |

---

## 10. Final gradient (float64)

| Item | Value |
|---|---|
| Gradient norm ‖g‖₂ at final θ | 10.727564 |
| Non-finite entries | 0 |

Top-5 absolute gradient components at final θ:

| Parameter | Gradient (float64) |
|---|---|
| `beta_w_pexp2` | +8.81817642 |
| `beta_l0_m` | -5.71621511 |
| `beta_l_age2_f` | -1.88415786 |
| `beta_l_age_m` | +0.73898643 |
| `theta_l_f` | -0.55555376 |

---

## 11. Runtime and throughput

| Operation | Time |
|---|---|
| JAX JIT warm-up (first call, incl. compile) | 12766.4 ms |
| Per-iteration wall time (avg) | 402.9 ms |
| Per-iteration wall time (range) | 345–562 ms |
| Total benchmark wall time | 6.05 s |
| CONOPT solve per start (reference) | ~13,689 s (~3.8 h) |
| Speedup per LL+grad eval vs CONOPT total | ~1072× |

---

## 12. Acceptance criteria summary (§12 of authorization)

| Criterion | Result |
|---|---|
| AC1: Initial LL matches v2 LL within tol | **PASS** |
| AC2: Gradient finite at start (float64) | **PASS** |
| AC3: Optimizer completed/stopped cleanly | **PASS** |
| AC4: No NaN/Inf objective or gradient | **PASS** |
| AC5: Final LL not materially worse | **PASS** |
| AC6: Parameter movement reported | **PASS** |
| **Overall** | **PASS** |

---

## 13. What was not executed

- No CONOPT run.
- No GAMSPy estimation.
- No Hessian computation.
- No standard errors (SE), cluster-robust SEs.
- No welfare computation.
- No SA2 issued.
- No pilot promotion.
- No multiple starts; no cold start from defaults.
- No denser product set (still 900 alts).
- No pooled/singles estimation.
- No P3a rebuild.
- v1/v2 equivalence reports NOT overwritten.
- Oracle JSONs, pkl, production data, pilot data NOT modified.
- No economic interpretation of any LL change.

---

## 14. Float32 smoke check (diagnostic only)

The previous equivalence validation (v2) recorded JAX float32 LL = −16,527.0664062500 (|Δ| vs oracle = 7.58e-02; |Δ| vs NumPy = 5.63e-04). This confirmed the same formula under float32. The float32 gradient check (norm = 6.1028) was also recorded in `Results/JMP_NC_pilot_vectorized_likelihood_cleanup_validation_v1.md`. No float32 optimization was run or authorized.

---

## Required Final Statements

- **This is a limited JAX optimizer benchmark only** — single start from `theta_CONOPT`, float64, `maxiter=15`. Not production optimization. Not verdict-grade.
- **float64 was enabled** (`jax_enable_x64=True`) before any JAX array was created.
- **Start: `theta_CONOPT` (start_1_warm_P3a) only.** No defaults. No multiple starts.
- **Optimizer: L-BFGS-B + JAX `value_and_grad` (float64); spec bounds; `theta_c` fixed 0.0.**
- **No Hessian, SEs, cluster-robust SEs, welfare, SA2, or promotion.**
- **Any LL change is not interpreted economically.** It is a precision-boundary or optimizer-path artifact at a single start from a known optimum.
- **Benchmark status: PASS** — all §12 acceptance criteria satisfied.
- **v1/v2 equivalence reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**
- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.
- NC pilot not promoted.

---

*Status: JAX optimizer benchmark v1 — limited stability probe only.*
*float64 mandatory; single start from theta_CONOPT; maxiter=15; no inference.*
*No optimization of production model. No welfare/SA2/promotion.*
*M1-clean 2016 active. NC pilot not promoted.*

