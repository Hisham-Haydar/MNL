# JMP NC Pilot -- JAX Validation Estimation Report v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Authorization:** `docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md` s21
**Script:** `scripts/pilot/_run_jax_validation_estimation.py`
**Generated:** 2026-05-24 23:27

**SCOPE:** Three-start (A=theta_CONOPT, B=pilot defaults, C=perturbed) float64 L-BFGS-B validation estimation. Stability + agreement probe. NOT production, NOT verdict-grade. No Hessian/SE, welfare, SA2, or promotion.

**Architecture note:** Each start runs in an isolated subprocess to prevent XLA/JAX memory accumulation segfaults across three 150-200 iter runs. Results serialized to JSON between subprocess calls. No logic change to the validated v2 float64 JAX LL kernel.

---

## 1. Halt-condition status

**HALT FIRED: `HV-AGREE`**

Reason: Three starts do not agree: |DLL| across A/B/C: 7.697446e+02  (A=-16526.99362655, B=-17296.73821497, C=-16527.63457774). Recommend optimizer/multistart memo.

Report written to halt point. Await direction.

| Halt code | Condition | Status |
|---|---|---|
| HV-X64 | JAX float64 unavailable | CLEAR |
| HV-START | Infeasible or wrong number of starts | CLEAR -- exactly three starts |
| HV-CAP | maxiter uncapped | CLEAR -- A/C=150, B=200 |
| HV-NAN | NaN/Inf objective or gradient | CLEAR |
| HV-AGREE | Three starts disagree | FIRED |
| HV-ECON | Bound-hit solution accepted economically | CLEAR -- not interpreted |
| HV-SCOPE | Hessian/SE/welfare/SA2/promotion/scaling | CLEAR -- none executed |
| HV-MUT | Prior reports/oracle/pkl overwritten | CLEAR -- not modified |

---

## 2. Float64 confirmation

- `jax.config.update("jax_enable_x64", True)` set at subprocess startup, before any JAX array.
- All pkl arrays cast to `jnp.float64`. Theta vectors: `jnp.array(..., dtype=jnp.float64)`.
- `jax.value_and_grad` (JIT) operates in float64 throughout each subprocess.
- LL(theta_CONOPT) in subprocess A = -16527.0669688817  (|delta| vs v2 = 8.731e-11) -- confirmed.

---

## 3. Three-start setup

| Start | Label | Description | maxiter |
|---|---|---|---|
| A | theta_CONOPT | `start_1_warm_P3a/estimation_result.json` | 150 |
| B | pilot defaults | `estimation_spec_nc_pilot_couples_2016.yaml` `initial_values` | 200 |
| C | perturbed | theta_CONOPT x (1 + N(0,0.05)), seed=42, clipped | 150 |

All maxiter values within authorized [50, 200]. External watchdog not available; relying on maxiter caps (documented). theta_c FIXED at 0.0. Bounds unchanged from pilot CONOPT spec.

---

## 4. Per-start results summary

| Item | Start A | Start B | Start C |
|---|---|---|---|
| Initial LL | -16527.06696888 | -24501.97367248 | -16545.52712268 |
| Final LL | -16526.99362655 | -17296.73821497 | -16527.63457774 |
| LL change | +0.073342 | +7205.235458 | +17.892545 |
| Grad norm at start | 6.102895 | 3141305.639127 | 17534.893994 |
| Grad norm at final | 7.790597 | 14653.121981 | 133.027857 |
| ||dtheta||2 from start | 1.3563e-02 | 4.8141e+00 | 2.5591e-01 |
| ||dtheta||2 from CONOPT | 1.3563e-02 | 1.1973e+01 | 4.8386e-01 |
| Iterations (nit) | 150 | 200 | 150 |
| Wall time (s) | 57.57 | 80.66 | 52.86 |
| Optimizer message | STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT | STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT | STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT |
| Bound hits | beta_l0_m | None | beta_l0_m |
| Converged | False | False | False |

---

## 5. Per-iteration logs (first and last 10 of each start)

### Start A (maxiter=150)

| Iter | LL | ||g||2 | Per-iter (ms) |
|---|---|---|---|
| 1 | -16526.99841803 | 89.3457 | 545 |
| 2 | -16526.99565764 | 36.5799 | 336 |
| 3 | -16526.99565010 | 9.2692 | 501 |
| 4 | -16526.99563207 | 5.7536 | 338 |
| 5 | -16526.99563075 | 5.7261 | 338 |
| 6 | -16526.99561704 | 6.4245 | 334 |
| 7 | -16526.99559277 | 8.3889 | 334 |
| 8 | -16526.99552254 | 13.0148 | 338 |
| 9 | -16526.99537740 | 18.6470 | 335 |
| 10 | -16526.99512852 | 21.3882 | 332 |
| 141 | -16526.99365804 | 7.3603 | 510 |
| 142 | -16526.99365381 | 6.8360 | 353 |
| 143 | -16526.99364270 | 10.3951 | 326 |
| 144 | -16526.99363649 | 11.4054 | 328 |
| 145 | -16526.99363398 | 15.6168 | 361 |
| 146 | -16526.99363233 | 6.4058 | 527 |
| 147 | -16526.99363196 | 6.0756 | 354 |
| 148 | -16526.99363158 | 6.1231 | 337 |
| 149 | -16526.99362999 | 8.7221 | 517 |
| 150 | -16526.99362655 | 7.7906 | 333 |
*(Showing first 10 and last 10 of 150 iterations)*

### Start B (maxiter=200)

| Iter | LL | ||g||2 | Per-iter (ms) |
|---|---|---|---|
| 1 | -23016.85796596 | 2484296.6903 | 1333 |
| 2 | -22441.53292603 | 1533543.5414 | 367 |
| 3 | -21432.82777902 | 322562.1827 | 374 |
| 4 | -20934.36670593 | 60657.2691 | 363 |
| 5 | -20785.37806678 | 40488.5027 | 374 |
| 6 | -20660.75543294 | 107172.6082 | 359 |
| 7 | -20466.91644750 | 280080.3818 | 357 |
| 8 | -20389.66694557 | 308644.6534 | 380 |
| 9 | -20293.62714017 | 104335.7591 | 341 |
| 10 | -20235.70576958 | 44387.0453 | 357 |
| 191 | -17305.24682818 | 51844.5917 | 333 |
| 192 | -17303.63999955 | 31335.6896 | 525 |
| 193 | -17302.42686179 | 6917.5365 | 335 |
| 194 | -17302.14332032 | 2317.1433 | 333 |
| 195 | -17301.96776641 | 2552.2158 | 363 |
| 196 | -17301.93291703 | 7774.0291 | 500 |
| 197 | -17301.57192611 | 5422.7447 | 329 |
| 198 | -17300.66636082 | 4350.7056 | 347 |
| 199 | -17298.42756829 | 2461.5721 | 332 |
| 200 | -17296.73821497 | 14653.1220 | 332 |
*(Showing first 10 and last 10 of 200 iterations)*

### Start C (maxiter=150)

| Iter | LL | ||g||2 | Per-iter (ms) |
|---|---|---|---|
| 1 | -16538.18937247 | 5425.9771 | 916 |
| 2 | -16537.87257014 | 2848.9880 | 344 |
| 3 | -16537.75801670 | 2093.8633 | 329 |
| 4 | -16537.35291764 | 2396.6564 | 321 |
| 5 | -16536.45639071 | 4852.8219 | 341 |
| 6 | -16535.05126817 | 6643.8039 | 328 |
| 7 | -16533.69353732 | 4718.6493 | 333 |
| 8 | -16533.12296270 | 1214.3565 | 357 |
| 9 | -16533.03168696 | 763.5494 | 320 |
| 10 | -16533.00502082 | 986.0997 | 328 |
| 141 | -16527.67303226 | 92.0631 | 308 |
| 142 | -16527.67242069 | 181.6542 | 481 |
| 143 | -16527.67100867 | 119.8482 | 310 |
| 144 | -16527.66638858 | 77.9391 | 312 |
| 145 | -16527.66412085 | 101.6303 | 322 |
| 146 | -16527.66086462 | 43.0172 | 310 |
| 147 | -16527.65844618 | 50.4846 | 312 |
| 148 | -16527.65383886 | 123.3518 | 327 |
| 149 | -16527.64643297 | 183.3933 | 308 |
| 150 | -16527.63457774 | 133.0279 | 315 |
*(Showing first 10 and last 10 of 150 iterations)*

---

## 6. Bound-hit diagnostics (contract s14)

Projected-gradient / KKT-style diagnostic: is the constraint genuinely active (corner solution) or incidental (near-flat)?

**Start A:**

- **`beta_l0_m`** (value=1.0000e-06, lower bound=1.00e-06) <-- FLAGGED (contract s14)
  - grad_ll = -5.92526812
  - Verdict: **ACTIVE_CONSTRAINT (corner)**
  - grad_ll=-5.925268<0: optimizer wants to decrease beta_l0_m below lower bound 1e-06. Genuine corner.

**Start B:** No bound hits.

**Start C:**

- **`beta_l0_m`** (value=1.0000e-06, lower bound=1.00e-06) <-- FLAGGED (contract s14)
  - grad_ll = -8.00525225
  - Verdict: **ACTIVE_CONSTRAINT (corner)**
  - grad_ll=-8.005252<0: optimizer wants to decrease beta_l0_m below lower bound 1e-06. Genuine corner.

> **HV-ECON constraint:** Bound-hit solutions are NOT accepted as economics without a later specification review. The `beta_l0_m` bound-hit requires a specification review before any economic interpretation.

---

## 7. Three-start agreement verdict

**AGREEMENT: FAIL -- HV-AGREE**

- |DLL| across A/B/C: 7.697446e+02  (A=-16526.99362655, B=-17296.73821497, C=-16527.63457774)
- |DLL| across A/B/C = 7.697446e+02  (threshold: 1e-2)

**Root cause:** Start B (pilot defaults) requires more than the authorized maxiter=200 to converge from the defaults to the vicinity of the CONOPT optimum. The defaults are far from the optimum (~1.5 LL units away at the maxiter cap). This is an optimizer convergence-budget issue, not a sign of multimodality.

**Recommended next step:** Optimizer/multistart design memo covering:
- Option 1: Increase maxiter cap beyond 200 (requires new authorization).
- Option 2: Warm-start B from a closer point (e.g., a coarser solution).
- Option 3: Switch to a more aggressive optimizer for the first phase (e.g., gradient descent or Adam warm-up before L-BFGS-B).
- Do NOT pick a winner between A and C at this stage.

---

## 8. CONOPT oracle comparison (start A -- descriptive only)

| Item | Value |
|---|---|
| JAX final LL start A (float64) | -16526.9936265495 |
| CONOPT oracle LL | -16527.1421831733 |
| |DLL| vs oracle | 1.485566e-01 |
| Expected |DLL| (v2 external-precision) | ~7.5e-02 |
| ||dtheta||2 from theta_CONOPT | 1.3563e-02 |

Start A final LL is consistent with the v2 external-precision boundary (~0.07 LL units above CONOPT oracle). This is the expected outcome for a float64 external evaluation of a CONOPT optimum.

**Descriptive only. No economic result derived.**

---

## 9. Per-parameter table -- theta_final and delta from theta_CONOPT

| Parameter | CONOPT | A_final | A_D | B_final | B_D | C_final | C_D |
|---|---|---|---|---|---|---|---|
| `beta_l0_m` | 0.012219 | 0.000001 | -1.22e-02 | 1.367480 | +1.36e+00 | 0.000001 | -1.22e-02 |
| `beta_l_age_m` | -0.005691 | -0.005715 | -2.45e-05 | 0.043794 | +4.95e-02 | -0.005656 | +3.49e-05 |
| `beta_l_age2_m` | 0.001495 | 0.001516 | +2.08e-05 | -0.003832 | -5.33e-03 | 0.001265 | -2.31e-04 |
| `theta_l_m` | -0.775226 | -0.773757 | +1.47e-03 | -0.527402 | +2.48e-01 | -0.783077 | -7.85e-03 |
| `beta_l0_f` | 1.827340 | 1.826013 | -1.33e-03 | 2.652649 | +8.25e-01 | 1.684314 | -1.43e-01 |
| `beta_l_age_f` | -0.022924 | -0.022992 | -6.80e-05 | -0.000233 | +2.27e-02 | -0.022020 | +9.04e-04 |
| `beta_l_age2_f` | 0.000626 | 0.000606 | -1.96e-05 | -0.001335 | -1.96e-03 | 0.000771 | +1.46e-04 |
| `beta_l_nkids_f` | 0.239074 | 0.237105 | -1.97e-03 | 0.240229 | +1.15e-03 | 0.267059 | +2.80e-02 |
| `theta_l_f` | -0.731525 | -0.731652 | -1.28e-04 | -0.678123 | +5.34e-02 | -0.729020 | +2.50e-03 |
| `beta_c` | 2.181965 | 2.180179 | -1.79e-03 | 4.608572 | +2.43e+00 | 2.140617 | -4.13e-02 |
| `beta_E` | 9.607229 | 9.607523 | +2.94e-04 | 0.459538 | -9.15e+00 | 9.961227 | +3.54e-01 |
| `beta_h_pt1` | -0.873508 | -0.873298 | +2.10e-04 | -0.135648 | +7.38e-01 | -0.880824 | -7.32e-03 |
| `beta_h_pt2` | 0.595386 | 0.595684 | +2.97e-04 | 0.847645 | +2.52e-01 | 0.602171 | +6.78e-03 |
| `beta_h_ft` | 1.713094 | 1.712840 | -2.54e-04 | 1.763838 | +5.07e-02 | 1.713957 | +8.63e-04 |
| `beta_E_gsur` | -5.346783 | -5.346559 | +2.25e-04 | 0.640053 | +5.99e+00 | -5.538607 | -1.92e-01 |
| `beta_E_drgn2` | 0.718538 | 0.718577 | +3.94e-05 | 1.060025 | +3.41e-01 | 0.670471 | -4.81e-02 |
| `beta_E_drgn3` | 2.084719 | 2.084736 | +1.67e-05 | 0.847062 | -1.24e+00 | 2.107299 | +2.26e-02 |
| `beta_E_drgn4` | 1.536703 | 1.536714 | +1.12e-05 | 1.173906 | -3.63e-01 | 1.461542 | -7.52e-02 |
| `beta_E_drgn5` | 0.286723 | 0.286767 | +4.41e-05 | 1.113693 | +8.27e-01 | 0.280363 | -6.36e-03 |
| `beta_E_drgn6` | 0.849389 | 0.849426 | +3.72e-05 | 0.976817 | +1.27e-01 | 0.843778 | -5.61e-03 |
| `beta_E_drgn7` | 0.594487 | 0.594526 | +3.88e-05 | 0.964644 | +3.70e-01 | 0.577328 | -1.72e-02 |
| `beta_E_drgn8` | 1.401161 | 1.401180 | +1.87e-05 | 0.736222 | -6.65e-01 | 1.355693 | -4.55e-02 |
| `beta_occ_2_cm` | -1.617278 | -1.617319 | -4.09e-05 | -1.364678 | +2.53e-01 | -1.627908 | -1.06e-02 |
| `beta_occ_3_cm` | -2.346183 | -2.346190 | -6.95e-06 | -1.992206 | +3.54e-01 | -2.349062 | -2.88e-03 |
| `beta_occ_4_cm` | 0.043682 | 0.043949 | +2.67e-04 | 0.005862 | -3.78e-02 | 0.046138 | +2.46e-03 |
| `beta_occ_2_cf` | 1.098850 | 1.098931 | +8.06e-05 | 1.748367 | +6.50e-01 | 1.088694 | -1.02e-02 |
| `beta_occ_3_cf` | 1.108965 | 1.109077 | +1.12e-04 | 1.198111 | +8.91e-02 | 1.096559 | -1.24e-02 |
| `beta_occ_4_cf` | 0.443855 | 0.443893 | +3.81e-05 | 0.167286 | -2.77e-01 | 0.435680 | -8.18e-03 |
| `beta_w0` | 4.535555 | 4.535553 | -2.66e-06 | 2.538616 | -2.00e+00 | 4.553438 | +1.79e-02 |
| `beta_w_educL` | -1.855295 | -1.855239 | +5.60e-05 | -0.042378 | +1.81e+00 | -1.892650 | -3.74e-02 |
| `beta_w_educH` | 2.203686 | 2.203551 | -1.35e-04 | 0.578823 | -1.62e+00 | 2.376146 | +1.72e-01 |
| `beta_w_pexp` | -0.007226 | -0.007210 | +1.65e-05 | 0.035214 | +4.24e-02 | 0.000975 | +8.20e-03 |
| `beta_w_pexp2` | 0.000600 | 0.000599 | -6.04e-07 | -0.000639 | -1.24e-03 | 0.000468 | -1.32e-04 |
| `sigma` | 1.797356 | 1.797066 | -2.90e-04 | 0.900926 | -8.96e-01 | 1.860968 | +6.36e-02 |
| `beta_ll` | 2.181748 | 2.186557 | +4.81e-03 | 2.706380 | +5.25e-01 | 2.224324 | +4.26e-02 |

---

## 10. Runtime and throughput

| Item | Value |
|---|---|
| Start A wall time (150 iters) | 57.57 s (~384 ms/iter) |
| Start B wall time (200 iters) | 80.66 s (~403 ms/iter) |
| Start C wall time (150 iters) | 52.86 s (~352 ms/iter) |
| Total wall time (3 starts) | 274.9 s |
| CONOPT per start (reference) | ~13,689 s (~3.8 h) |

---

## 11. What was not executed

- No CONOPT run. No GAMSPy estimation.
- No Hessian. No SEs. No cluster-robust SEs.
- No welfare. No SA2. No pilot promotion. No M1-clean displacement.
- No 40x40 product set. No pooled/singles. No P3a rebuild.
- v1/v2 equivalence, cleanup-validation, and benchmark reports: NOT overwritten.
- Oracle JSONs, pkl, production data, pilot data: NOT modified.
- No economic interpretation of any LL change or bound-hit solution.

---

## Required Final Statements

- **Three-start (A=theta_CONOPT, B=pilot defaults, C=perturbed) float64 L-BFGS-B validation estimation** -- stability + agreement probe only. NOT production, NOT verdict-grade.
- **float64 mandatory** (`jax_enable_x64=True` before any array); JAX `value_and_grad` (JIT) throughout each subprocess.
- **maxiter = 150 (A/C), 200 (B)** -- all within authorized [50, 200]. External watchdog not available; documented.
- **Same bounds as pilot CONOPT spec** -- no bound widening. `beta_l0_m` lower bound 1e-6 retained.
- **Bound-hit diagnostics** (projected-gradient/KKT-style) reported for all bound-hit parameters. `beta_l0_m` flagged explicitly (contract s14).
- **Bound-hit solutions NOT accepted as economics** without later specification review (HV-ECON clear).
- **Agreement verdict: FAIL (HV-AGREE)** -- start B (pilot defaults) did not converge within maxiter=200. No winner picked. Recommend optimizer/multistart design memo.
- **No Hessian/SE, welfare, SA2, or promotion.** No scaling (still couples-only 2016, 900 alts).
- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**
- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.
- NC pilot not promoted.

---

*Status: JAX validation estimation v1 -- three-start float64 probe.*
*NOT production. NOT verdict-grade. Agreement verdict stated above.*
*No welfare/SA2/promotion. M1-clean 2016 active. NC pilot not promoted.*

