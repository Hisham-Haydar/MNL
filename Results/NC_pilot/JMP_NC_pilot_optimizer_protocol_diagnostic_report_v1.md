# JMP NC Pilot -- Optimizer-Protocol Diagnostic Report v1

*France RURO multi-year extension | v1 | 2026-05-25 00:48*

**Authorization:** `docs/France_case/NC_pilot/design/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md` s22  
**Script:** `scripts/pilot/_run_optimizer_protocol_diagnostic.py`  
**Generated:** 2026-05-25 00:48

**SCOPE:** Staged optimizer-protocol diagnostic — NOT production, NOT verdict-grade. No winner picked; no estimate accepted; no SE/welfare/SA2/promotion.

**Architecture note:** Each job runs in an isolated subprocess (2-hour watchdog) to prevent XLA/JAX memory accumulation across many long runs. Reused validated v2/benchmark float64 JAX LL kernel; no logic change.

---

## 1. Summary verdict

| Item | Value |
|---|---|
| Stage-1 LL spread (near-oracle starts) | 3.4120e-01 |
| Stage-1 basin agreement (< 0.01 threshold) | NO |
| Any Stage-1 start tolerance-converged | YES |
| Stage-2 any variant reached basin | YES |
| beta_l0_m verdict | [S1_A] ACTIVE_CONSTRAINT: grad_ll=-5.6104<0: wants to go below lower bound. Corner. |
| **Overall verdict** | **NEAR-ORACLE STARTS DISAGREE AFTER LARGE BUDGET -- multimodality evidenced.** |

---

## 2. Float64 confirmation

- `jax.config.update("jax_enable_x64", True)` set at worker startup, before any JAX array.
- All pkl arrays cast to `jnp.float64`. JAX `value_and_grad` (JIT) in float64 throughout.

---

## 3. Stage-1 — Near-oracle basin test

**Starts:** theta_CONOPT (S1_A) + three small perturbations (S1_C1: seed=42 mag=0.02; S1_C2: seed=7 mag=0.05; S1_C3: seed=99 mag=0.10). maxiter=1500, ftol=1e-9, gtol=1e-7.

| Job | Start description | Initial LL | Final LL | Term type | nit | |g|_final | ||dth||_CONOPT | Wall(s) |
|---|---|---|---|---|---|---|---|---|
| S1_A | theta_CONOPT | -16527.06696888 | -16526.99565010 | TOLERANCE_STOP (nit=3) | 3 | 9.269228 | 1.2219e-02 | 30.4 |
| S1_C1 | perturbed(seed=42,mag=0.02) | -16529.84342419 | -16527.13060417 | TOLERANCE_STOP (nit=112) | 112 | 30.440031 | 2.0105e-01 | 64.9 |
| S1_C2 | perturbed(seed=7,mag=0.05) | -16539.14051602 | -16527.08481216 | TOLERANCE_STOP (nit=486) | 486 | 26.437882 | 1.8537e-01 | 192.6 |
| S1_C3 | perturbed(seed=99,mag=0.10) | -16581.33302129 | -16527.33684803 | TOLERANCE_STOP (nit=579) | 579 | 14.030443 | 4.0645e-01 | 296.7 |

**LL spread across S1 starts:** 3.411979e-01  (threshold: 1e-02)
**Basin agreement verdict:** FAIL -- starts disagree

### S1_A bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-5.6104<0: wants to go below lower bound. Corner.

### S1_C1 bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-6.8627<0: wants to go below lower bound. Corner.

### S1_C2 bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-6.7268<0: wants to go below lower bound. Corner.

### S1_C3 bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-6.5518<0: wants to go below lower bound. Corner.

### Stage-1 iteration logs (first/last 10)

**S1_A — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -16526.99841803 | 89.345734 | 559 |
| 2 | -16526.99565764 | 36.579920 | 368 |
| 3 | -16526.99565010 | 9.269228 | 498 |

**S1_A — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -16526.99841803 | 89.345734 | 559 |
| 2 | -16526.99565764 | 36.579920 | 368 |
| 3 | -16526.99565010 | 9.269228 | 498 |

**S1_C1 — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -16528.84530640 | 2587.707911 | 954 |
| 2 | -16528.78918952 | 1423.522730 | 344 |
| 3 | -16528.76781867 | 827.684516 | 340 |
| 4 | -16528.73977587 | 819.677808 | 338 |
| 5 | -16528.62815626 | 1894.244349 | 348 |
| 6 | -16528.44146921 | 3082.141269 | 341 |
| 7 | -16528.16976506 | 3324.568906 | 335 |
| 8 | -16527.89466101 | 1206.338065 | 350 |
| 9 | -16527.86313883 | 418.657427 | 338 |
| 10 | -16527.86068949 | 183.776101 | 335 |

**S1_C1 — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 103 | -16527.14354015 | 57.284043 | 327 |
| 104 | -16527.13922150 | 47.571816 | 329 |
| 105 | -16527.13620762 | 232.785276 | 341 |
| 106 | -16527.13302438 | 46.496916 | 320 |
| 107 | -16527.13138737 | 61.949594 | 321 |
| 108 | -16527.13084261 | 12.161171 | 334 |
| 109 | -16527.13071096 | 21.015770 | 305 |
| 110 | -16527.13066725 | 32.257351 | 456 |
| 111 | -16527.13061943 | 16.344542 | 335 |
| 112 | -16527.13060417 | 30.440031 | 324 |

**S1_C2 — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -16535.67657782 | 2919.539040 | 1147 |
| 2 | -16535.06952606 | 4807.001292 | 552 |
| 3 | -16534.72983150 | 1370.372679 | 373 |
| 4 | -16534.47319440 | 1822.776697 | 546 |
| 5 | -16532.36628101 | 7193.833846 | 373 |
| 6 | -16531.45075418 | 5135.023291 | 363 |
| 7 | -16531.10777785 | 1467.513275 | 375 |
| 8 | -16531.05515595 | 695.580666 | 357 |
| 9 | -16531.03546108 | 1182.811666 | 369 |
| 10 | -16530.99605466 | 1709.869489 | 359 |

**S1_C2 — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 477 | -16527.09066319 | 35.026000 | 317 |
| 478 | -16527.08909902 | 53.346537 | 314 |
| 479 | -16527.08687385 | 68.483724 | 314 |
| 480 | -16527.08557745 | 78.569380 | 304 |
| 481 | -16527.08552072 | 25.343217 | 468 |
| 482 | -16527.08529263 | 18.954867 | 310 |
| 483 | -16527.08509470 | 37.713459 | 315 |
| 484 | -16527.08488215 | 12.396139 | 461 |
| 485 | -16527.08482234 | 9.567586 | 305 |
| 486 | -16527.08481216 | 26.437882 | 467 |

**S1_C3 — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -16559.52039859 | 10847.398971 | 1621 |
| 2 | -16558.59658517 | 8938.907393 | 391 |
| 3 | -16557.84004144 | 3579.200210 | 393 |
| 4 | -16557.48255999 | 3480.250994 | 392 |
| 5 | -16553.85729277 | 8202.345456 | 389 |
| 6 | -16549.80654130 | 11449.081014 | 393 |
| 7 | -16545.55585999 | 8747.260961 | 389 |
| 8 | -16544.22726248 | 1762.311920 | 394 |
| 9 | -16544.15054581 | 409.895381 | 392 |
| 10 | -16544.14161220 | 487.812358 | 388 |

**S1_C3 — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 570 | -16527.34109830 | 63.778319 | 532 |
| 571 | -16527.34088268 | 40.420542 | 515 |
| 572 | -16527.34072191 | 53.723554 | 517 |
| 573 | -16527.34004038 | 97.416390 | 520 |
| 574 | -16527.33893386 | 116.445481 | 505 |
| 575 | -16527.33858746 | 245.737994 | 782 |
| 576 | -16527.33727627 | 128.382282 | 509 |
| 577 | -16527.33691009 | 33.287064 | 508 |
| 578 | -16527.33685703 | 12.775686 | 516 |
| 579 | -16527.33684803 | 14.030443 | 522 |

---

## 4. Stage-2 — Cold-start recovery test (defaults)

| Job | Method | Initial LL | Final LL | Term type | nit | |g|_final | Reached basin? | Wall(s) |
|---|---|---|---|---|---|---|---|---|
| S2a | Long L-BFGS-B (maxiter=1500) | -24501.97367248 | -16576.28780525 | CAP_HIT (nit=1500) | 1500 | 466.490663 | NO | 1377.2 |
| S2b | Adam(500 steps)->L-BFGS-B (maxiter=1000) | -19589.87377510 | -16627.73641480 | CAP_HIT (nit=1000) | 1000 | 2116.368528 | NO | 731.2 |
| S2c | Scaled L-BFGS-B (maxiter=1500) | -24501.97367248 | -16526.99746997 | TOLERANCE_STOP (nit=631) | 631 | 34.245443 | YES | 276.3 |

**Basin threshold used:** within 1.0 LL unit of best Stage-1 final LL (-16526.99565010)
**Cold-start recovery verdict:** PASS -- at least one variant reached the basin

### S2a bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-3.6542<0: wants to go below lower bound. Corner.

### S2b bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-5.2216<0: wants to go below lower bound. Corner.

### S2c bound-hit diagnostics

- `beta_l0_m` at lower bound 1.00e-06 (value=1.000000e-06)
  - **beta_l0_m** verdict: **ACTIVE_CONSTRAINT** -- grad_ll=-6.1028<0: wants to go below lower bound. Corner.

### Stage-2 iteration logs (first/last 10)

**S2a — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -23016.85796596 | 2484296.690344 | 2465 |
| 2 | -22441.53292603 | 1533543.541355 | 703 |
| 3 | -21432.82777902 | 322562.182691 | 701 |
| 4 | -20934.36670593 | 60657.269095 | 688 |
| 5 | -20785.37806678 | 40488.502715 | 677 |
| 6 | -20660.75543294 | 107172.608195 | 706 |
| 7 | -20466.91644750 | 280080.381835 | 712 |
| 8 | -20389.66694557 | 308644.653442 | 683 |
| 9 | -20293.62714017 | 104335.759091 | 715 |
| 10 | -20235.70576958 | 44387.045336 | 728 |

**S2a — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1491 | -16580.07818454 | 4541.876283 | 688 |
| 1492 | -16578.85356664 | 8686.130774 | 637 |
| 1493 | -16578.43728456 | 2288.061267 | 1005 |
| 1494 | -16577.31621108 | 2716.260518 | 672 |
| 1495 | -16576.61033341 | 2280.468556 | 687 |
| 1496 | -16576.39238356 | 680.408405 | 686 |
| 1497 | -16576.36412392 | 1546.524553 | 658 |
| 1498 | -16576.32342100 | 611.136845 | 688 |
| 1499 | -16576.30480315 | 274.141010 | 700 |
| 1500 | -16576.28780525 | 466.490663 | 659 |

**S2b — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -19509.54638154 | 797463.852256 | 1717 |
| 2 | -19344.48038742 | 449232.278733 | 553 |
| 3 | -19192.71320673 | 161571.889460 | 582 |
| 4 | -19166.93004138 | 71733.212702 | 574 |
| 5 | -19162.06284169 | 33425.865399 | 578 |
| 6 | -19157.67417268 | 41616.336950 | 601 |
| 7 | -19152.87417486 | 87397.083649 | 583 |
| 8 | -19142.94771884 | 154045.441273 | 595 |
| 9 | -19120.23767832 | 237904.330938 | 597 |
| 10 | -19068.41799020 | 312380.037587 | 600 |

**S2b — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 991 | -16629.98602558 | 1527.745346 | 363 |
| 992 | -16629.94486263 | 7436.190160 | 360 |
| 993 | -16629.79040081 | 3813.411757 | 351 |
| 994 | -16629.49905273 | 1124.270368 | 348 |
| 995 | -16629.05951653 | 6195.981164 | 377 |
| 996 | -16628.71422145 | 7792.001316 | 354 |
| 997 | -16628.41678535 | 6488.246564 | 359 |
| 998 | -16628.13295482 | 2670.523961 | 380 |
| 999 | -16627.90764672 | 1682.513595 | 359 |
| 1000 | -16627.73641480 | 2116.368528 | 375 |

**S2c — first 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 1 | -23512.96962275 | 3326851.024833 | 1748 |
| 2 | -21454.28003502 | 1534955.405267 | 441 |
| 3 | -18268.88513609 | 79826.389141 | 427 |
| 4 | -18002.17672327 | 157504.057999 | 445 |
| 5 | -17790.80768388 | 189333.105776 | 421 |
| 6 | -17640.74919587 | 155246.344833 | 423 |
| 7 | -17439.02323317 | 112430.164819 | 429 |
| 8 | -17130.24979011 | 95010.895279 | 437 |
| 9 | -16886.19066557 | 55912.393469 | 402 |
| 10 | -16774.53830727 | 57366.916278 | 575 |

**S2c — last 10 iterations:**

| Iter | LL | ||g|| | per-iter (ms) |
|---|---|---|---|
| 622 | -16526.99772289 | 30.615343 | 360 |
| 623 | -16526.99769542 | 25.761023 | 357 |
| 624 | -16526.99766879 | 21.468552 | 398 |
| 625 | -16526.99764765 | 18.593764 | 380 |
| 626 | -16526.99761213 | 20.161503 | 362 |
| 627 | -16526.99759043 | 10.725895 | 599 |
| 628 | -16526.99754462 | 11.021079 | 363 |
| 629 | -16526.99750972 | 17.535095 | 375 |
| 630 | -16526.99748239 | 16.765844 | 346 |
| 631 | -16526.99746997 | 34.245443 | 566 |

---

## 5. Stage-3 -- beta_l0_m verdict

**Verdict:** [S1_A] ACTIVE_CONSTRAINT: grad_ll=-5.6104<0: wants to go below lower bound. Corner.

> HV-ECON: No economic interpretation regardless of verdict. If corner is confirmed at a converged point, a specification review is required before any economic interpretation.

---

## 6. Runtime

| Job | Wall time (s) | Term type |
|---|---|---|
| S1_A | 30.4 | TOLERANCE_STOP |
| S1_C1 | 64.9 | TOLERANCE_STOP |
| S1_C2 | 192.6 | TOLERANCE_STOP |
| S1_C3 | 296.7 | TOLERANCE_STOP |
| S2a | 1377.2 | CAP_HIT |
| S2b | 731.2 | CAP_HIT |
| S2c | 276.3 | TOLERANCE_STOP |
| **Total** | **2969.4** | -- |

---

## 7. What was not executed

- No CONOPT run. No GAMSPy estimation.
- No Hessian. No SEs. No cluster-robust SEs.
- No welfare. No SA2. No pilot promotion. No M1-clean displacement.
- No 40x40 product set. No pooled/singles. No P3a rebuild.
- Prior reports, oracle JSONs, pkl, and all production/pilot data: NOT modified.
- No winner picked; no estimate accepted; no economic interpretation.

---

## Required Final Statements

- **Diagnostic optimizer-protocol run only** -- staged (Stage 1: near-oracle basin test; Stage 2: cold-start recovery). NOT production, NOT verdict-grade.
- **No winner is picked** from any stage; no start is accepted as an estimate.
- **float64 mandatory** (`jax_enable_x64=True` before any array); JAX `value_and_grad` (JIT) throughout each subprocess.
- **`beta_l0_m` NOT interpreted economically.** Corner-vs-transient verdict reported at tolerance-converged points only (if none converged: deferred).
- **Same model, data, bounds as pilot CONOPT spec.** `theta_c` FIXED at 0.0. No formula/data/bound changes.
- **No Hessian/SE, welfare, SA2, or promotion.** No scaling-up. No denser product.
- **Prior reports, oracle JSONs, pkl, and all production/pilot data: UNMODIFIED.**
- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.
- NC pilot not promoted.

---

*Status: optimizer-protocol diagnostic v1. Staged diagnostic; no estimate accepted; no inference/welfare/SA2/promotion. M1-clean 2016 active.*
