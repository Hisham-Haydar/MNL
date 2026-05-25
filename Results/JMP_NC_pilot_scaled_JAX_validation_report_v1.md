# JMP NC Pilot — Scaled-JAX Validation Report v1

*France RURO multi-year extension | v1 | 2026-05-25 02:21*

**Authorization:** `docs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md` s18  
**Script:** `scripts/pilot/_run_scaled_jax_validation.py`  
**Generated:** 2026-05-25 02:21

**SCOPE:** Formal scaled-JAX three-start validation — NOT production, NOT verdict-grade. No winner picked unless PASS; no SE/welfare/SA2/promotion.

**Architecture:** Each start runs in an isolated subprocess (2-hour watchdog). Reused validated v2 float64 JAX LL kernel (4th-order Taylor BC); no logic change. Scaling is a change of optimization coordinates only; model, data, bounds (native), and `theta_c=0.0` unchanged.

---

## 1. Halt-condition status

| Halt | Condition | Status |
|---|---|---|
| HS-X64   | JAX float64 unavailable | CLEAR |
| HS-SCALE | Scale not S2c rule / not recorded | CLEAR — exact 35-vector below |
| HS-START | Not exactly three scaled starts | CLEAR — A/B/C run |
| HS-CAP   | maxiter prevents tolerance stop | CLEAR — maxiter=2000, ftol=1e-9, gtol=1e-7 |
| HS-NAN   | NaN/Inf at any iterate | CLEAR |
| HS-AGREE | Not all tol-stop or spread > 0.1 | CLEAR |
| HS-ECON  | beta_l0_m interpreted economically | CLEAR — reported only |
| HS-SCOPE | SE/Hessian/welfare/SA2/promotion | CLEAR — none executed |
| HS-MUT   | Prior reports/oracle/pkl overwritten | CLEAR — not modified |

**Overall validation verdict: PASS**

---

## 2. Float64 confirmation

- `jax.config.update("jax_enable_x64", True)` set at subprocess startup, before any JAX array.
- All pkl arrays and theta vectors cast to `jnp.float64`. JAX `value_and_grad` (JIT) in float64 throughout.

---

## 3. S2c scaling rule and exact 35-element scale vector

**Rule:** `scale[i] = max(|theta_CONOPT[i]|, 1e-3)` (S2c diagnostic rule, verbatim).  
**Floored entries** (|theta_CONOPT| < 1e-3, floor binds):  
- `beta_l_age2_f` [index 6]: |theta_CONOPT| = 6.256e-04 → scale = 1e-3  
- `beta_w_pexp2`  [index 32]: |theta_CONOPT| = 6.000e-04 → scale = 1e-3  
All other 33 entries: scale[i] = |theta_CONOPT[i]|.  
Scale verified to match `result_S2c.json` to machine precision (max deviation = 0.00e+00).

**Exact 35-element scale vector (native parameter order):**

| # | Parameter | scale[i] | floored? |
|---|---|---|---|
| 0 | `beta_l0_m` | 1.221947258568049e-02 |  |
| 1 | `beta_l_age_m` | 5.690523740521559e-03 |  |
| 2 | `beta_l_age2_m` | 1.495248639589080e-03 |  |
| 3 | `theta_l_m` | 7.752259721771092e-01 |  |
| 4 | `beta_l0_f` | 1.827340238336211e+00 |  |
| 5 | `beta_l_age_f` | 2.292393746058093e-02 |  |
| 6 | `beta_l_age2_f` | 1.000000000000000e-03 | YES |
| 7 | `beta_l_nkids_f` | 2.390744727426523e-01 |  |
| 8 | `theta_l_f` | 7.315246178924519e-01 |  |
| 9 | `beta_c` | 2.181964958022478e+00 |  |
| 10 | `beta_E` | 9.607229487957513e+00 |  |
| 11 | `beta_h_pt1` | 8.735077255894893e-01 |  |
| 12 | `beta_h_pt2` | 5.953862953895495e-01 |  |
| 13 | `beta_h_ft` | 1.713093776601255e+00 |  |
| 14 | `beta_E_gsur` | 5.346783342279315e+00 |  |
| 15 | `beta_E_drgn2` | 7.185379438594310e-01 |  |
| 16 | `beta_E_drgn3` | 2.084718790447483e+00 |  |
| 17 | `beta_E_drgn4` | 1.536702691963134e+00 |  |
| 18 | `beta_E_drgn5` | 2.867230187712183e-01 |  |
| 19 | `beta_E_drgn6` | 8.493885440829149e-01 |  |
| 20 | `beta_E_drgn7` | 5.944869507736464e-01 |  |
| 21 | `beta_E_drgn8` | 1.401161434093296e+00 |  |
| 22 | `beta_occ_2_cm` | 1.617277853242267e+00 |  |
| 23 | `beta_occ_3_cm` | 2.346183302844021e+00 |  |
| 24 | `beta_occ_4_cm` | 4.368197735035088e-02 |  |
| 25 | `beta_occ_2_cf` | 1.098849976767484e+00 |  |
| 26 | `beta_occ_3_cf` | 1.108964657364105e+00 |  |
| 27 | `beta_occ_4_cf` | 4.438545611597099e-01 |  |
| 28 | `beta_w0` | 4.535555371106352e+00 |  |
| 29 | `beta_w_educL` | 1.855294733740334e+00 |  |
| 30 | `beta_w_educH` | 2.203686480202360e+00 |  |
| 31 | `beta_w_pexp` | 7.226260138546647e-03 |  |
| 32 | `beta_w_pexp2` | 1.000000000000000e-03 | YES |
| 33 | `sigma` | 1.797355621767536e+00 |  |
| 34 | `beta_ll` | 2.181748410441470e+00 |  |

**Optimization in scaled coordinates:** `z[i] = theta[i] / scale[i]`.  
**Bounds transformed consistently:** `bound_scaled = bound_native / scale[i]`.  
**All theta reported on native scale:** `theta[i] = z[i] * scale[i]`.

---

## 4. Three scaled starts

| Start | Description | maxiter | ftol | gtol |
|---|---|---|---|---|
| A | theta_CONOPT (native) / scale | 2000 | 1e-9 | 1e-7 |
| B | pilot defaults (native) / scale | 2000 | 1e-9 | 1e-7 |
| C | perturbed theta_CONOPT (seed=17, mag=0.05) / scale | 2000 | 1e-9 | 1e-7 |

External watchdog: 2-hour subprocess timeout per start. No Adam warm-up (scaling alone recovers basin per S2c).

---

## 5. Per-start results (native scale)

| Item | Start A | Start B | Start C |
|---|---|---|---|
| Initial LL | -16527.06696888 | -24501.97367248 | -16616.98368366 |
| Final LL | -16526.99259532 | -16526.99746997 | -16526.99282219 |
| LL change | +0.074374 | +7974.976203 | +89.990861 |
| Grad norm (start) | 6.102895 | 3141305.639127 | 21535.942244 |
| Grad norm (final) | 7.734310 | 34.245443 | 9.621592 |
| Termination | TOLERANCE_STOP (nit=16) | TOLERANCE_STOP (nit=631) | TOLERANCE_STOP (nit=241) |
| ||dtheta||_CONOPT | 2.0451e-02 | 6.9259e-02 | 2.4692e-02 |
| Wall time (s) | 40.5 | 282.5 | 129.7 |
| Bound hits | beta_l0_m | beta_l0_m | beta_l0_m |

### Start A — bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** — grad_ll=-6.0801<0: wants below lower bound. Corner.

### Start B — bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** — grad_ll=-6.1028<0: wants below lower bound. Corner.

### Start C — bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** — grad_ll=-6.0808<0: wants below lower bound. Corner.

### Iteration logs (first / last 10 per start)

**Start A — first 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 1 | -16527.06144101 | 8.970854 | 548 |
| 2 | -16527.05832239 | 53.895117 | 520 |
| 3 | -16527.05731503 | 79.377983 | 513 |
| 4 | -16526.99875348 | 327.978638 | 366 |
| 5 | -16526.99533818 | 174.689313 | 337 |
| 6 | -16526.99469832 | 54.120099 | 340 |
| 7 | -16526.99459805 | 45.016656 | 348 |
| 8 | -16526.99408745 | 81.347351 | 327 |
| 9 | -16526.99372940 | 76.951847 | 319 |
| 10 | -16526.99327189 | 41.381397 | 363 |

**Start A — last 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 7 | -16526.99459805 | 45.016656 | 348 |
| 8 | -16526.99408745 | 81.347351 | 327 |
| 9 | -16526.99372940 | 76.951847 | 319 |
| 10 | -16526.99327189 | 41.381397 | 363 |
| 11 | -16526.99299480 | 19.985378 | 326 |
| 12 | -16526.99285759 | 37.794551 | 335 |
| 13 | -16526.99272612 | 28.714022 | 343 |
| 14 | -16526.99262514 | 9.459221 | 329 |
| 15 | -16526.99259696 | 10.869915 | 329 |
| 16 | -16526.99259532 | 7.734310 | 355 |

**Start B — first 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 1 | -23512.96962275 | 3326851.024833 | 1480 |
| 2 | -21454.28003502 | 1534955.405267 | 398 |
| 3 | -18268.88513609 | 79826.389141 | 416 |
| 4 | -18002.17672327 | 157504.057999 | 436 |
| 5 | -17790.80768388 | 189333.105776 | 433 |
| 6 | -17640.74919587 | 155246.344833 | 416 |
| 7 | -17439.02323317 | 112430.164819 | 387 |
| 8 | -17130.24979011 | 95010.895279 | 439 |
| 9 | -16886.19066557 | 55912.393469 | 418 |
| 10 | -16774.53830727 | 57366.916278 | 655 |

**Start B — last 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 622 | -16526.99772289 | 30.615343 | 735 |
| 623 | -16526.99769542 | 25.761023 | 877 |
| 624 | -16526.99766879 | 21.468552 | 552 |
| 625 | -16526.99764765 | 18.593764 | 398 |
| 626 | -16526.99761213 | 20.161503 | 454 |
| 627 | -16526.99759043 | 10.725895 | 640 |
| 628 | -16526.99754462 | 11.021079 | 423 |
| 629 | -16526.99750972 | 17.535095 | 406 |
| 630 | -16526.99748239 | 16.765844 | 448 |
| 631 | -16526.99746997 | 34.245443 | 645 |

**Start C — first 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 1 | -16582.93031320 | 21616.693419 | 1204 |
| 2 | -16548.85957185 | 14322.235352 | 453 |
| 3 | -16537.30949549 | 22531.532500 | 447 |
| 4 | -16531.77374196 | 1562.070578 | 414 |
| 5 | -16531.21455737 | 1320.525959 | 436 |
| 6 | -16529.66519637 | 521.417392 | 930 |
| 7 | -16528.62278287 | 599.722622 | 741 |
| 8 | -16527.77696710 | 697.691981 | 403 |
| 9 | -16527.62988918 | 695.773219 | 394 |
| 10 | -16527.48816441 | 693.472923 | 390 |

**Start C — last 10:**

| Iter | LL | \|\|g\|\| | per-iter (ms) |
|---|---|---|---|
| 232 | -16526.99307018 | 10.997889 | 336 |
| 233 | -16526.99304328 | 53.214290 | 342 |
| 234 | -16526.99298427 | 9.269551 | 345 |
| 235 | -16526.99295856 | 11.536349 | 379 |
| 236 | -16526.99292353 | 15.941084 | 364 |
| 237 | -16526.99289202 | 20.657818 | 375 |
| 238 | -16526.99286434 | 23.214173 | 354 |
| 239 | -16526.99284523 | 17.545371 | 335 |
| 240 | -16526.99282821 | 11.562960 | 347 |
| 241 | -16526.99282219 | 9.621592 | 495 |

---

## 6. Agreement verdict

| Item | Value |
|---|---|
| Start A final LL | -16526.99259532 |
| Start B final LL | -16526.99746997 |
| Start C final LL | -16526.99282219 |
| LL spread (max-min) | 4.874648e-03 |
| All tolerance-stopped | YES |
| Agree within 0.1 (pilot threshold) | YES |
| Agree within 0.01 (strict) | YES |
| **Validation verdict** | **PASS** |

**All three starts tolerance-stopped and agree within the 0.1 LL pilot threshold.** The JAX optimizer protocol is validated. A single NC-pilot point estimate is numerically confirmed (no SE/verdict yet — those are the next gates).

---

## 7. beta_l0_m bound-hit verdict (Stage 3)

- **Start A:** value=1.000000e-06, grad_ll=-6.0801, verdict=**ACTIVE_CONSTRAINT** — grad_ll=-6.0801<0: wants below lower bound. Corner.
- **Start B:** value=1.000000e-06, grad_ll=-6.1028, verdict=**ACTIVE_CONSTRAINT** — grad_ll=-6.1028<0: wants below lower bound. Corner.
- **Start C:** value=1.000000e-06, grad_ll=-6.0808, verdict=**ACTIVE_CONSTRAINT** — grad_ll=-6.0808<0: wants below lower bound. Corner.

> **HS-ECON maintained.** `beta_l0_m` is reported but NOT interpreted economically. A specification review is required before any economic interpretation.

---

## 8. Per-parameter table (native scale)

| Parameter | scale[i] | A_final | B_final | C_final | A_delta | B_delta | C_delta |
|---|---|---|---|---|---|---|---|
| `beta_l0_m` | 1.2219e-02 | 0.000001 | 0.000001 | 0.000001 | -1.22e-02 | -1.22e-02 | -1.22e-02 |
| `beta_l_age_m` | 5.6905e-03 | -0.005690 | -0.005817 | -0.005723 | +9.31e-08 | -1.26e-04 | -3.27e-05 |
| `beta_l_age2_m` | 1.4952e-03 | 0.001496 | 0.001510 | 0.001503 | +1.20e-06 | +1.45e-05 | +8.11e-06 |
| `theta_l_m` | 7.7523e-01 | -0.775121 | -0.775252 | -0.775035 | +1.05e-04 | -2.64e-05 | +1.91e-04 |
| `beta_l0_f` | 1.8273e+00 | 1.817565 | 1.816424 | 1.818169 | -9.78e-03 | -1.09e-02 | -9.17e-03 |
| `beta_l_age_f` | 2.2924e-02 | -0.022926 | -0.022908 | -0.022913 | -1.65e-06 | +1.62e-05 | +1.06e-05 |
| `beta_l_age2_f` | 1.0000e-03 | 0.000625 | 0.000637 | 0.000621 | -2.99e-07 | +1.18e-05 | -4.88e-06 |
| `beta_l_nkids_f` | 2.3907e-01 | 0.238903 | 0.238701 | 0.238718 | -1.71e-04 | -3.73e-04 | -3.56e-04 |
| `theta_l_f` | 7.3152e-01 | -0.731589 | -0.731428 | -0.731492 | -6.40e-05 | +9.68e-05 | +3.24e-05 |
| `beta_c` | 2.1820e+00 | 2.182019 | 2.182642 | 2.182208 | +5.45e-05 | +6.77e-04 | +2.43e-04 |
| `beta_E` | 9.6072e+00 | 9.607078 | 9.574557 | 9.615510 | -1.51e-04 | -3.27e-02 | +8.28e-03 |
| `beta_h_pt1` | 8.7351e-01 | -0.873494 | -0.873028 | -0.873361 | +1.42e-05 | +4.80e-04 | +1.47e-04 |
| `beta_h_pt2` | 5.9539e-01 | 0.595434 | 0.595336 | 0.595642 | +4.74e-05 | -4.99e-05 | +2.55e-04 |
| `beta_h_ft` | 1.7131e+00 | 1.713116 | 1.713017 | 1.713058 | +2.23e-05 | -7.72e-05 | -3.56e-05 |
| `beta_E_gsur` | 5.3468e+00 | -5.346729 | -5.330247 | -5.349741 | +5.47e-05 | +1.65e-02 | -2.96e-03 |
| `beta_E_drgn2` | 7.1854e-01 | 0.718540 | 0.719687 | 0.716443 | +2.46e-06 | +1.15e-03 | -2.09e-03 |
| `beta_E_drgn3` | 2.0847e+00 | 2.084768 | 2.079810 | 2.082309 | +4.93e-05 | -4.91e-03 | -2.41e-03 |
| `beta_E_drgn4` | 1.5367e+00 | 1.536708 | 1.539089 | 1.534904 | +5.70e-06 | +2.39e-03 | -1.80e-03 |
| `beta_E_drgn5` | 2.8672e-01 | 0.286722 | 0.291054 | 0.282632 | -9.01e-07 | +4.33e-03 | -4.09e-03 |
| `beta_E_drgn6` | 8.4939e-01 | 0.849384 | 0.855281 | 0.846962 | -4.33e-06 | +5.89e-03 | -2.43e-03 |
| `beta_E_drgn7` | 5.9449e-01 | 0.594486 | 0.598935 | 0.589418 | -6.91e-07 | +4.45e-03 | -5.07e-03 |
| `beta_E_drgn8` | 1.4012e+00 | 1.401181 | 1.399618 | 1.398407 | +1.95e-05 | -1.54e-03 | -2.75e-03 |
| `beta_occ_2_cm` | 1.6173e+00 | -1.617248 | -1.617576 | -1.617348 | +2.99e-05 | -2.98e-04 | -7.01e-05 |
| `beta_occ_3_cm` | 2.3462e+00 | -2.346154 | -2.346627 | -2.346380 | +2.90e-05 | -4.44e-04 | -1.96e-04 |
| `beta_occ_4_cm` | 4.3682e-02 | 0.043682 | 0.042834 | 0.043446 | -3.24e-07 | -8.48e-04 | -2.36e-04 |
| `beta_occ_2_cf` | 1.0988e+00 | 1.098883 | 1.098995 | 1.098613 | +3.33e-05 | +1.45e-04 | -2.37e-04 |
| `beta_occ_3_cf` | 1.1090e+00 | 1.109033 | 1.109179 | 1.108799 | +6.81e-05 | +2.15e-04 | -1.66e-04 |
| `beta_occ_4_cf` | 4.4385e-01 | 0.443868 | 0.444041 | 0.443671 | +1.38e-05 | +1.87e-04 | -1.83e-04 |
| `beta_w0` | 4.5356e+00 | 4.535515 | 4.489212 | 4.542238 | -4.05e-05 | -4.63e-02 | +6.68e-03 |
| `beta_w_educL` | 1.8553e+00 | -1.855384 | -1.829451 | -1.860656 | -8.91e-05 | +2.58e-02 | -5.36e-03 |
| `beta_w_educH` | 2.2037e+00 | 2.203762 | 2.197415 | 2.204888 | +7.55e-05 | -6.27e-03 | +1.20e-03 |
| `beta_w_pexp` | 7.2263e-03 | -0.007226 | -0.004577 | -0.007415 | -7.14e-08 | +2.65e-03 | -1.89e-04 |
| `beta_w_pexp2` | 1.0000e-03 | 0.000600 | 0.000541 | 0.000604 | -6.42e-08 | -5.94e-05 | +4.23e-06 |
| `sigma` | 1.7974e+00 | 1.797372 | 1.789935 | 1.798948 | +1.61e-05 | -7.42e-03 | +1.59e-03 |
| `beta_ll` | 2.1817e+00 | 2.194912 | 2.194468 | 2.194064 | +1.32e-02 | +1.27e-02 | +1.23e-02 |

---

## 9. Runtime

| Start | Wall time (s) | Termination |
|---|---|---|
| A | 40.5 | TOLERANCE_STOP (nit=16) |
| B | 282.5 | TOLERANCE_STOP (nit=631) |
| C | 129.7 | TOLERANCE_STOP (nit=241) |
| **Total** | **452.8** | — |

---

## 10. What was not executed

- No CONOPT run. No GAMSPy estimation.
- No Hessian. No SEs. No cluster-robust SEs.
- No welfare. No SA2. No pilot promotion. No M1-clean displacement.
- No 40x40 product set. No pooled/singles. No P3a rebuild.
- Prior reports, oracle JSONs, pkl, and all production/pilot data: NOT modified.
- Model formula, data, bounds (native), and theta_c=0.0: UNCHANGED.

---

## Required Final Statements

- **Formal scaled-JAX three-start validation** (A=scaled theta_CONOPT, B=scaled defaults, C=scaled perturbed seed=17 mag=0.05) — NOT production, NOT verdict-grade.
- **Scaling = S2c rule `scale[i]=max(|theta_CONOPT[i]|,1e-3)`.** Floor binds on `beta_l_age2_f` (6.256e-04→1e-3) and `beta_w_pexp2` (6.000e-04→1e-3). Exact 35-vector recorded in §3. Optimization in scaled coordinates; all reporting on native scale.
- **Model, data, bounds (native), theta_c=0.0: UNCHANGED.**
- **maxiter=2000, ftol=1e-9, gtol=1e-7** — tolerance stops achievable (HS-CAP clear).
- **Agreement verdict:** PASS  
  LL spread = 4.874648e-03 (threshold 0.1: PASS; threshold 0.01: PASS).
- **`beta_l0_m` reported but NOT interpreted economically** (HS-ECON). Specification review required before any economic interpretation.
- **No SE/Hessian (beyond cheap diagnostic if applicable), welfare, SA2, promotion, scaling-up, denser product, pooled, singles, or P3a rebuild.**
- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**
- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.
- NC pilot not promoted.

---

*Status: scaled-JAX validation v1. Formal three-start scaled validation; verdict: PASS. No SE/welfare/SA2/promotion. M1-clean 2016 active.*
