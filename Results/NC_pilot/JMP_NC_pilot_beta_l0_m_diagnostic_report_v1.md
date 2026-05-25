# JMP NC Pilot — beta_l0_m Specification Review Diagnostic Report v1

*France RURO multi-year extension | v1 | 2026-05-25 09:54*

**Authorization:** `docs/France_case/NC_pilot/design/JMP_NC_pilot_beta_l0_m_specification_review_v1.md` s17  
**Script:** `scripts/pilot/_run_beta_l0_m_diagnostic.py`  
**Generated:** 2026-05-25 09:54

**SCOPE:** beta_l0_m active-bound specification review diagnostic. No SEs, no Hessian beyond grad norms, no welfare, no SA2, no promotion, no 40x40, no P3a rebuild. Negative beta_l0_m values are diagnostic probes only, explicitly labelled, bounded, and not specification changes.

---

## 1. Diagnostic status

**Status: PASS** — all five diagnostic jobs completed without error.

| Job | Wall time (s) | Status |
|---|---|---|
| PROFILE | 67.8 | OK |
| REOPT_FLOOR | 45.4 | OK |
| REOPT_CONOPT | 27.1 | OK |
| REOPT_NEG | 50.0 | OK |
| PARTICIPATION | 70.6 | OK |

Total wall time: 261.1 s

---

## 2. Reference solution (accepted scaled-JAX start A)

The accepted reference is the tolerance-stopped start-A solution from the formal three-start scaled-JAX validation (LL = −16,526.99259532, nit = 16).

| Parameter | CONOPT | Accepted (Start A) | Delta |
|---|---|---|---|
| `beta_l0_m` | 0.01221947 | 0.00000100 | -1.221847e-02 |
| `beta_ll` | 2.18174841 | 2.19491197 | +1.316356e-02 |
| `theta_l_m` | -0.77522597 | -0.77512095 | +1.050193e-04 |
| `beta_l0_f` | 1.82734024 | 1.81756489 | -9.775351e-03 |
| `theta_l_f` | -0.73152462 | -0.73158866 | -6.404053e-05 |
| `beta_c` | 2.18196496 | 2.18201947 | +5.450788e-05 |
| `beta_E` | 9.60722949 | 9.60707838 | -1.511066e-04 |
| `beta_h_pt1` | -0.87350773 | -0.87349354 | +1.419004e-05 |
| `beta_h_pt2` | 0.59538630 | 0.59543367 | +4.737884e-05 |
| `beta_h_ft` | 1.71309378 | 1.71311611 | +2.233193e-05 |
| `beta_E_gsur` | -5.34678334 | -5.34672863 | +5.471648e-05 |
| `sigma` | 1.79735562 | 1.79737173 | +1.610712e-05 |

**Accepted LL:** −16,526.99259532  **Accepted beta_l0_m:** 1.000000e-06  **CONOPT beta_l0_m:** 0.01221947

---

## 3. Active-bound evidence summary

At all three tolerance-stopped starts of the formal scaled-JAX validation:

| Start | beta_l0_m | grad_ll(beta_l0_m) | Verdict |
|---|---|---|---|
| A | 1.000000e-06 | −6.0801 | ACTIVE_CONSTRAINT |
| B | 1.000000e-06 | −6.1028 | ACTIVE_CONSTRAINT |
| C | 1.000000e-06 | −6.0808 | ACTIVE_CONSTRAINT |

Gradient is strictly negative at the lower bound, meaning the likelihood would increase by moving beta_l0_m below the imposed floor. This is a stable feature, not a convergence transient.

---

## 4. Local likelihood profile over beta_l0_m (fixed-theta sweep)

Profile computed by substituting each beta_l0_m value into the accepted theta vector (all other parameters held fixed at Start-A values). This traces the conditional LL surface along the beta_l0_m axis.

Negative values are **diagnostic probes only** — explicitly bounded, not specification changes.

| beta_l0_m | LL | ΔLL vs accepted | grad_l0_m | grad_beta_ll | Note |
|---|---|---|---|---|---|
| -0.100000 | -16526.79117016 | +2.014252e-01 | 2.0903 | 7.3316 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.050000 | -16526.78975292 | +2.028424e-01 | -2.0239 | 3.6279 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.020000 | -16526.88712944 | +1.054659e-01 | -4.4644 | 1.4311 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.010000 | -16526.93582046 | +5.677486e-02 | -5.2734 | 0.7031 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.005000 | -16526.96319656 | +2.939876e-02 | -5.6770 | 0.3398 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.001000 | -16526.98654952 | +6.045804e-03 | -5.9994 | 0.0496 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| -0.000100 | -16526.99198164 | +6.136775e-04 | -6.0719 | -0.0157 | DIAGNOSTIC PROBE ONLY — not a specification change **(NEG-PROBE)** |
| +0.000000 | -16526.99258924 | +6.080041e-06 | -6.0800 | -0.0229 |  |
| +0.000001 | -16526.99259532 | +0.000000e+00 | -6.0801 | -0.0230 |  |
| +0.001000 | -16526.99870951 | -6.114193e-03 | -6.1605 | -0.0954 |  |
| +0.002000 | -16527.00491031 | -1.231499e-02 | -6.2411 | -0.1678 |  |
| +0.005000 | -16527.02399563 | -3.140031e-02 | -6.4825 | -0.3851 |  |
| +0.008000 | -16527.04380486 | -5.120954e-02 | -6.7237 | -0.6022 |  |
| +0.010000 | -16527.05741288 | -6.481756e-02 | -6.8843 | -0.7468 |  |
| +0.012219 | -16527.07288695 | -8.029163e-02 | -7.0625 | -0.9071 |  |
| +0.020000 | -16527.13026854 | -1.376732e-01 | -7.6864 | -1.4686 |  |
| +0.050000 | -16527.39680026 | -4.042049e-01 | -10.0790 | -3.6217 |  |
| +0.100000 | -16527.99954750 | -1.006952e+00 | -14.0216 | -7.1691 |  |
| +0.200000 | -16529.78949890 | -2.796904e+00 | -21.7409 | -14.1128 |  |
| +0.500000 | -16539.64152522 | -1.264893e+01 | -43.6300 | -33.7881 |  |
| +1.000000 | -16569.80256592 | -4.280997e+01 | -76.2583 | -63.0702 |  |
| +2.000000 | -16673.93134754 | -1.469388e+02 | -129.6613 | -110.8353 |  |

**Key observations from profile:**

- **Below zero (diagnostic probes):** best LL at beta_l0_m = -0.0500 → LL = -16526.789753 (ΔLL = +2.028424e-01 vs accepted).
- **At zero:** LL = -16526.99258924 (ΔLL = +6.080041e-06).
- **At lower bound (1e-6):** LL = -16526.99259532 (accepted).
- **At CONOPT value (0.012219):** LL = -16527.07288695 (ΔLL = -8.029163e-02).
- Profile declines monotonically above the bound (worst at beta_l0_m = 2.0000: LL = -16673.931348).

---

## 5. Fixed-floor re-optimization (Option B active-set treatment)

Beta_l0_m fixed at 1e-6; remaining 34 parameters re-optimized with S2c scaling.

| Item | Value |
|---|---|
| Fixed beta_l0_m | 1.000000e-06 |
| Final LL | -16526.99259424 |
| ΔLL vs accepted | +1.083350e-06 |
| Iterations | 1 |
| Termination | TOLERANCE_STOP |
| Wall time (s) | 0.5 |

**Parameter shifts (REOPT_FLOOR vs accepted start A) — key parameters:**

| Parameter | Accepted | REOPT_FLOOR | Delta |
|---|---|---|---|
| `beta_ll` | 2.19491197 | 2.19490283 | -9.143895e-06 |
| `theta_l_m` | -0.77512095 | -0.77512111 | -1.620264e-07 |
| `beta_l0_f` | 1.81756489 | 1.81755952 | -5.367615e-06 |
| `theta_l_f` | -0.73158866 | -0.73159014 | -1.477060e-06 |
| `beta_c` | 2.18201947 | 2.18203203 | +1.256061e-05 |
| `beta_E` | 9.60707838 | 9.60717065 | +9.226954e-05 |
| `beta_h_pt1` | -0.87349354 | -0.87349363 | -9.202493e-08 |
| `beta_h_pt2` | 0.59543367 | 0.59543350 | -1.759430e-07 |
| `beta_h_ft` | 1.71311611 | 1.71311468 | -1.428883e-06 |
| `beta_E_gsur` | -5.34672863 | -5.34670047 | +2.815533e-05 |
| `sigma` | 1.79737173 | 1.79736846 | -3.266534e-06 |
| `beta_w0` | 4.53551483 | 4.53551491 | +8.688852e-08 |
| `beta_w_educL` | -1.85538380 | -1.85538313 | +6.719346e-07 |
| `beta_w_educH` | 2.20376201 | 2.20376033 | -1.679306e-06 |
| `beta_w_pexp` | -0.00722633 | -0.00722633 | +3.962827e-10 |
| `beta_w_pexp2` | 0.00059990 | 0.00059990 | +3.307825e-10 |

---

## 6. Fixed at CONOPT value re-optimization

Beta_l0_m fixed at 0.01221947 (CONOPT); remaining 34 parameters re-optimized from accepted start-A point.

| Item | Value |
|---|---|
| Fixed beta_l0_m | 0.01221947 |
| Final LL | -16527.06698742 |
| ΔLL vs accepted | -7.439210e-02 |
| ΔLL vs REOPT_FLOOR | -7.439318e-02 |
| Iterations | 12 |
| Termination | TOLERANCE_STOP |
| Wall time (s) | 3.3 |

**Key parameter shifts (REOPT_CONOPT vs accepted start A):**

| Parameter | Accepted | REOPT_CONOPT | Delta |
|---|---|---|---|
| `beta_ll` | 2.19491197 | 2.18138078 | -1.353120e-02 |
| `theta_l_m` | -0.77512095 | -0.77513333 | -1.237750e-05 |
| `beta_l0_f` | 1.81756489 | 1.82647420 | +8.909309e-03 |
| `theta_l_f` | -0.73158866 | -0.73137985 | +2.088087e-04 |
| `beta_c` | 2.18201947 | 2.18185155 | -1.679124e-04 |
| `beta_E` | 9.60707838 | 9.60753933 | +4.609483e-04 |
| `beta_h_pt1` | -0.87349354 | -0.87351408 | -2.054242e-05 |
| `beta_h_pt2` | 0.59543367 | 0.59534456 | -8.911683e-05 |
| `beta_h_ft` | 1.71311611 | 1.71309421 | -2.190103e-05 |
| `beta_E_gsur` | -5.34672863 | -5.34702594 | -2.973117e-04 |
| `sigma` | 1.79737173 | 1.79736139 | -1.033618e-05 |
| `beta_w0` | 4.53551483 | 4.53567224 | +1.574170e-04 |
| `beta_w_educL` | -1.85538380 | -1.85523676 | +1.470350e-04 |
| `beta_w_educH` | 2.20376201 | 2.20358772 | -1.742887e-04 |
| `beta_w_pexp` | -0.00722633 | -0.00722619 | +1.366490e-07 |
| `beta_w_pexp2` | 0.00059990 | 0.00060002 | +1.154213e-07 |

---

## 7. Relaxed-bound diagnostic probe (REOPT_NEG)

**DIAGNOSTIC PROBE ONLY.** Beta_l0_m allowed to move below zero (bound relaxed to [−0.5, 50]). This is not a specification change. It is used only to learn whether the likelihood improves materially below zero and whether male leisure utility remains coherent.

| Item | Value |
|---|---|
| beta_l0_m at optimum | -0.00000006 |
| Final LL | -16526.99258785 |
| ΔLL vs accepted | +7.472263e-06 |
| Iterations | 1 |
| Termination | TOLERANCE_STOP |
| Wall time (s) | 1.0 |

**Key parameter shifts (REOPT_NEG vs accepted start A):**

| Parameter | Accepted | REOPT_NEG | Delta |
|---|---|---|---|
| `beta_l0_m` | 0.00000100 | -0.00000006 | -1.057638e-06 |
| `beta_ll` | 2.19491197 | 2.19490164 | -1.033470e-05 |
| `theta_l_m` | -0.77512095 | -0.77512113 | -1.752412e-07 |
| `beta_l0_f` | 1.81756489 | 1.81755880 | -6.085565e-06 |
| `beta_c` | 2.18201947 | 2.18203368 | +1.421372e-05 |
| `sigma` | 1.79737173 | 1.79736802 | -3.704203e-06 |

---

## 8. Log-likelihood summary across all diagnostic points

| Point | beta_l0_m | LL | ΔLL vs accepted |
|---|---|---|---|
| Accepted (Start A) | 1.000000e-06 | -16526.99259532 | 0.00e+00 |
| Profile: fixed=-0.100000 [NEG-PROBE] | -1.000000e-01 | -16526.79117016 | +2.014252e-01 |
| Profile: fixed=-0.050000 [NEG-PROBE] | -5.000000e-02 | -16526.78975292 | +2.028424e-01 |
| Profile: fixed=-0.020000 [NEG-PROBE] | -2.000000e-02 | -16526.88712944 | +1.054659e-01 |
| Profile: fixed=-0.010000 [NEG-PROBE] | -1.000000e-02 | -16526.93582046 | +5.677486e-02 |
| Profile: fixed=-0.005000 [NEG-PROBE] | -5.000000e-03 | -16526.96319656 | +2.939876e-02 |
| Profile: fixed=-0.001000 [NEG-PROBE] | -1.000000e-03 | -16526.98654952 | +6.045804e-03 |
| Profile: fixed=-0.000100 [NEG-PROBE] | -1.000000e-04 | -16526.99198164 | +6.136775e-04 |
| Profile: fixed=+0.000000 | +0.000000e+00 | -16526.99258924 | +6.080041e-06 |
| Profile: fixed=+0.000001 | +1.000000e-06 | -16526.99259532 | +0.000000e+00 |
| Profile: fixed=+0.001000 | +1.000000e-03 | -16526.99870951 | -6.114193e-03 |
| Profile: fixed=+0.002000 | +2.000000e-03 | -16527.00491031 | -1.231499e-02 |
| Profile: fixed=+0.005000 | +5.000000e-03 | -16527.02399563 | -3.140031e-02 |
| Profile: fixed=+0.008000 | +8.000000e-03 | -16527.04380486 | -5.120954e-02 |
| Profile: fixed=+0.010000 | +1.000000e-02 | -16527.05741288 | -6.481756e-02 |
| Profile: fixed=+0.012219 | +1.221900e-02 | -16527.07288695 | -8.029163e-02 |
| Profile: fixed=+0.020000 | +2.000000e-02 | -16527.13026854 | -1.376732e-01 |
| Profile: fixed=+0.050000 | +5.000000e-02 | -16527.39680026 | -4.042049e-01 |
| Profile: fixed=+0.100000 | +1.000000e-01 | -16527.99954750 | -1.006952e+00 |
| Profile: fixed=+0.200000 | +2.000000e-01 | -16529.78949890 | -2.796904e+00 |
| Profile: fixed=+0.500000 | +5.000000e-01 | -16539.64152522 | -1.264893e+01 |
| Profile: fixed=+1.000000 | +1.000000e+00 | -16569.80256592 | -4.280997e+01 |
| Profile: fixed=+2.000000 | +2.000000e+00 | -16673.93134754 | -1.469388e+02 |
| REOPT_FLOOR (34-param reopt) | 1.000000e-06 | -16526.99259424 | +1.083350e-06 |
| REOPT_CONOPT (fixed at CONOPT val) | 1.221947e-02 | -16527.06698742 | -7.439210e-02 |
| REOPT_NEG [DIAG-PROBE] | -5.763775e-08 | -16526.99258785 | +7.472263e-06 |

---

## 9. beta_ll absorption and leisure-block collinearity diagnostic

The pattern of interest: when beta_l0_m falls from CONOPT (0.01222) to 1e-6, beta_ll rises by approximately +0.013. This is consistent with a near-substitution direction between the standalone male leisure loading and the couples leisure interaction term.

| Source | beta_l0_m | beta_ll | theta_l_m | beta_l0_f |
|---|---|---|---|---|
| CONOPT | 0.01221947 | 2.18174841 | -0.77522597 | 1.82734024 |
| Accepted (Start A) | 0.00000100 | 2.19491197 | -0.77512095 | 1.81756489 |
| REOPT_FLOOR | 0.00000100 | 2.19490283 | -0.77512111 | 1.81755952 |
| REOPT_CONOPT | 0.01221947 | 2.18138078 | -0.77513333 | 1.82647420 |
| REOPT_NEG [DIAG-PROBE] | -0.00000006 | 2.19490164 | -0.77512113 | 1.81755880 |

**Substitution pattern:**

- Δbeta_l0_m (accepted − CONOPT): -1.221847e-02
- Δbeta_ll   (accepted − CONOPT): +1.316356e-02
- Ratio Δbeta_ll / (−Δbeta_l0_m): 1.0773  (near 1.0 → near-unit substitution between the two leisure terms)

---

## 10. Full 34-parameter shift table (REOPT_FLOOR vs accepted start A)

| Parameter | Accepted | REOPT_FLOOR | Delta | |g| at REOPT_FLOOR |
|---|---|---|---|---|
| `beta_l0_m` | 0.00000100 | 1.00000000e-06 | 0.00e+00 | FIXED |
| `beta_l_age_m` | -0.00569043 | -0.00569043 | +1.391673e-10 | 0.0508 |
| `beta_l_age2_m` | 0.00149645 | 0.00149645 | +2.226433e-10 | 1.3289 |
| `theta_l_m` | -0.77512095 | -0.77512111 | -1.620264e-07 | 0.0044 |
| `beta_l0_f` | 1.81756489 | 1.81755952 | -5.367615e-06 | 0.0143 |
| `beta_l_age_f` | -0.02292559 | -0.02292559 | -5.946725e-10 | 0.0075 |
| `beta_l_age2_f` | 0.00062525 | 0.00062525 | -2.007819e-10 | 1.8725 |
| `beta_l_nkids_f` | 0.23890331 | 0.23890325 | -5.622827e-08 | 0.0063 |
| `theta_l_f` | -0.73158866 | -0.73159014 | -1.477060e-06 | 0.0109 |
| `beta_c` | 2.18201947 | 2.18203203 | +1.256061e-05 | 0.0194 |
| `beta_E` | 9.60707838 | 9.60717065 | +9.226954e-05 | 0.0055 |
| `beta_h_pt1` | -0.87349354 | -0.87349363 | -9.202493e-08 | 0.0015 |
| `beta_h_pt2` | 0.59543367 | 0.59543350 | -1.759430e-07 | 0.0063 |
| `beta_h_ft` | 1.71311611 | 1.71311468 | -1.428883e-06 | 0.0086 |
| `beta_E_gsur` | -5.34672863 | -5.34670047 | +2.815533e-05 | 0.0081 |
| `beta_E_drgn2` | 0.71854040 | 0.71854049 | +9.104862e-08 | 0.0011 |
| `beta_E_drgn3` | 2.08476808 | 2.08476821 | +1.238293e-07 | 0.0017 |
| `beta_E_drgn4` | 1.53670840 | 1.53670852 | +1.270663e-07 | 0.0004 |
| `beta_E_drgn5` | 0.28672212 | 0.28672213 | +1.455955e-08 | 0.0005 |
| `beta_E_drgn6` | 0.84938421 | 0.84938429 | +7.791842e-08 | 0.0003 |
| `beta_E_drgn7` | 0.59448626 | 0.59448630 | +4.388706e-08 | 0.0005 |
| `beta_E_drgn8` | 1.40118096 | 1.40118117 | +2.087849e-07 | 0.0009 |
| `beta_occ_2_cm` | -1.61724793 | -1.61724915 | -1.222931e-06 | 0.0052 |
| `beta_occ_3_cm` | -2.34615434 | -2.34615539 | -1.052239e-06 | 0.0021 |
| `beta_occ_4_cm` | 0.04368165 | 0.04368165 | +6.696577e-10 | 0.0032 |
| `beta_occ_2_cf` | 1.09888326 | 1.09888277 | -4.888092e-07 | 0.0079 |
| `beta_occ_3_cf` | 1.10903272 | 1.10903132 | -1.398793e-06 | 0.0156 |
| `beta_occ_4_cf` | 0.44386836 | 0.44386872 | +3.559902e-07 | 0.0119 |
| `beta_w0` | 4.53551483 | 4.53551491 | +8.688852e-08 | 0.0099 |
| `beta_w_educL` | -1.85538380 | -1.85538313 | +6.719346e-07 | 0.0032 |
| `beta_w_educH` | 2.20376201 | 2.20376033 | -1.679306e-06 | 0.0012 |
| `beta_w_pexp` | -0.00722633 | -0.00722633 | +3.962827e-10 | 0.2857 |
| `beta_w_pexp2` | 0.00059990 | 0.00059990 | +3.307825e-10 | 9.0656 |
| `sigma` | 1.79737173 | 1.79736846 | -3.266534e-06 | 0.0174 |
| `beta_ll` | 2.19491197 | 2.19490283 | -9.143895e-06 | 0.0175 |

---

## 11. Full 34-parameter shift table (REOPT_CONOPT vs accepted start A)

| Parameter | Accepted | REOPT_CONOPT | Delta |
|---|---|---|---|
| `beta_l0_m` | 0.00000100 | 0.01221947 | FIXED |
| `beta_l_age_m` | -0.00569043 | -0.00569049 | -5.442163e-08 |
| `beta_l_age2_m` | 0.00149645 | 0.00149530 | -1.145031e-06 |
| `theta_l_m` | -0.77512095 | -0.77513333 | -1.237750e-05 |
| `beta_l0_f` | 1.81756489 | 1.82647420 | +8.909309e-03 |
| `beta_l_age_f` | -0.02292559 | -0.02292407 | +1.524398e-06 |
| `beta_l_age2_f` | 0.00062525 | 0.00062551 | +2.609925e-07 |
| `beta_l_nkids_f` | 0.23890331 | 0.23907079 | +1.674856e-04 |
| `theta_l_f` | -0.73158866 | -0.73137985 | +2.088087e-04 |
| `beta_c` | 2.18201947 | 2.18185155 | -1.679124e-04 |
| `beta_E` | 9.60707838 | 9.60753933 | +4.609483e-04 |
| `beta_h_pt1` | -0.87349354 | -0.87351408 | -2.054242e-05 |
| `beta_h_pt2` | 0.59543367 | 0.59534456 | -8.911683e-05 |
| `beta_h_ft` | 1.71311611 | 1.71309421 | -2.190103e-05 |
| `beta_E_gsur` | -5.34672863 | -5.34702594 | -2.973117e-04 |
| `beta_E_drgn2` | 0.71854040 | 0.71853842 | -1.977442e-06 |
| `beta_E_drgn3` | 2.08476808 | 2.08466866 | -9.942140e-05 |
| `beta_E_drgn4` | 1.53670840 | 1.53670203 | -6.366600e-06 |
| `beta_E_drgn5` | 0.28672212 | 0.28672324 | +1.125733e-06 |
| `beta_E_drgn6` | 0.84938421 | 0.84938984 | +5.626903e-06 |
| `beta_E_drgn7` | 0.59448626 | 0.59448750 | +1.236526e-06 |
| `beta_E_drgn8` | 1.40118096 | 1.40115975 | -2.121459e-05 |
| `beta_occ_2_cm` | -1.61724793 | -1.61733023 | -8.229819e-05 |
| `beta_occ_3_cm` | -2.34615434 | -2.34622752 | -7.317923e-05 |
| `beta_occ_4_cm` | 0.04368165 | 0.04368162 | -3.783815e-08 |
| `beta_occ_2_cf` | 1.09888326 | 1.09880198 | -8.127264e-05 |
| `beta_occ_3_cf` | 1.10903272 | 1.10887576 | -1.569554e-04 |
| `beta_occ_4_cf` | 0.44386836 | 0.44384799 | -2.037408e-05 |
| `beta_w0` | 4.53551483 | 4.53567224 | +1.574170e-04 |
| `beta_w_educL` | -1.85538380 | -1.85523676 | +1.470350e-04 |
| `beta_w_educH` | 2.20376201 | 2.20358772 | -1.742887e-04 |
| `beta_w_pexp` | -0.00722633 | -0.00722619 | +1.366490e-07 |
| `beta_w_pexp2` | 0.00059990 | 0.00060002 | +1.154213e-07 |
| `sigma` | 1.79737173 | 1.79736139 | -1.033618e-05 |
| `beta_ll` | 2.19491197 | 2.18138078 | -1.353120e-02 |

---

## 12. Male participation and hours fit diagnostics

Predicted participation and hours rates computed from model-implied choice probabilities. Observed rates from the precomputed object (actual_choice indicator).

| Scenario | beta_l0_m | Obs m-part | Pred m-part | Obs f-part | Pred f-part |
|---|---|---|---|---|---|
| CONOPT theta | 0.0122 | 0.9717 | 0.9999 | 0.9651 | 0.9369 |
| Accepted (Start A) | 0.0000 | 0.9717 | 0.9999 | 0.9651 | 0.9369 |
| REOPT_FLOOR | 0.0000 | 0.9717 | 0.9999 | 0.9651 | 0.9369 |
| Profile beta_l0_m=0.01 | 0.0100 | 0.9717 | 0.9999 | 0.9651 | 0.9369 |
| Profile beta_l0_m=0.0 | 0.0000 | 0.9717 | 0.9999 | 0.9651 | 0.9369 |

**Male hours breakdown (part-time 1, part-time 2, full-time):**

| Scenario | Obs m-pt1 | Pred m-pt1 | Obs m-pt2 | Pred m-pt2 | Obs m-ft | Pred m-ft |
|---|---|---|---|---|---|---|
| Accepted | 0.0054 | 0.0146 | 0.0101 | 0.0225 | 0.2650 | 0.2384 |
| REOPT_FLOOR | 0.0054 | 0.0146 | 0.0101 | 0.0225 | 0.2650 | 0.2384 |
| CONOPT | 0.0054 | 0.0146 | 0.0101 | 0.0225 | 0.2650 | 0.2384 |

**Female hours breakdown:**

| Scenario | Obs f-pt1 | Pred f-pt1 | Obs f-pt2 | Pred f-pt2 | Obs f-ft | Pred f-ft |
|---|---|---|---|---|---|---|
| Accepted | 0.0283 | 0.0192 | 0.0419 | 0.0295 | 0.2006 | 0.2272 |
| REOPT_FLOOR | 0.0283 | 0.0192 | 0.0419 | 0.0295 | 0.2006 | 0.2272 |
| CONOPT | 0.0283 | 0.0192 | 0.0419 | 0.0295 | 0.2006 | 0.2272 |

---

## 13. Opportunity and wage block parameter shifts

Shifts in the non-preference blocks when beta_l0_m is fixed at the floor (REOPT_FLOOR) vs accepted start-A values. These are the parameters most relevant to the market opportunity and wage components of the likelihood.

| Parameter | Block | Accepted | REOPT_FLOOR | Delta |
|---|---|---|---|---|
| `beta_E` | employment | 9.607078 | 9.607171 | +9.226954e-05 |
| `beta_h_pt1` | hours | -0.873494 | -0.873494 | -9.202493e-08 |
| `beta_h_pt2` | hours | 0.595434 | 0.595433 | -1.759430e-07 |
| `beta_h_ft` | hours | 1.713116 | 1.713115 | -1.428883e-06 |
| `beta_E_gsur` | market | -5.346729 | -5.346700 | +2.815533e-05 |
| `beta_E_drgn2` | region | 0.718540 | 0.718540 | +9.104862e-08 |
| `beta_E_drgn3` | region | 2.084768 | 2.084768 | +1.238293e-07 |
| `beta_E_drgn4` | region | 1.536708 | 1.536709 | +1.270663e-07 |
| `beta_E_drgn5` | region | 0.286722 | 0.286722 | +1.455955e-08 |
| `beta_E_drgn6` | region | 0.849384 | 0.849384 | +7.791842e-08 |
| `beta_E_drgn7` | region | 0.594486 | 0.594486 | +4.388706e-08 |
| `beta_E_drgn8` | region | 1.401181 | 1.401181 | +2.087849e-07 |
| `beta_occ_2_cm` | occ-m | -1.617248 | -1.617249 | -1.222931e-06 |
| `beta_occ_3_cm` | occ-m | -2.346154 | -2.346155 | -1.052239e-06 |
| `beta_occ_4_cm` | occ-m | 0.043682 | 0.043682 | +6.696577e-10 |
| `beta_occ_2_cf` | occ-f | 1.098883 | 1.098883 | -4.888092e-07 |
| `beta_occ_3_cf` | occ-f | 1.109033 | 1.109031 | -1.398793e-06 |
| `beta_occ_4_cf` | occ-f | 0.443868 | 0.443869 | +3.559902e-07 |
| `beta_w0` | wage | 4.535515 | 4.535515 | +8.688852e-08 |
| `beta_w_educL` | wage | -1.855384 | -1.855383 | +6.719346e-07 |
| `beta_w_educH` | wage | 2.203762 | 2.203760 | -1.679306e-06 |
| `beta_w_pexp` | wage | -0.007226 | -0.007226 | +3.962827e-10 |
| `beta_w_pexp2` | wage | 0.000600 | 0.000600 | +3.307825e-10 |
| `sigma` | wage | 1.797372 | 1.797368 | -3.266534e-06 |

---

## 14. Preference block parameter shifts

Leisure and consumption preference parameters when beta_l0_m is fixed at floor.

| Parameter | Accepted | REOPT_FLOOR | Delta |
|---|---|---|---|
| `beta_l0_f` | 1.81756489 | 1.81755952 | -5.367615e-06 |
| `beta_l_age_m` | -0.00569043 | -0.00569043 | +1.391673e-10 |
| `beta_l_age2_m` | 0.00149645 | 0.00149645 | +2.226433e-10 |
| `theta_l_m` | -0.77512095 | -0.77512111 | -1.620264e-07 |
| `beta_l_age_f` | -0.02292559 | -0.02292559 | -5.946725e-10 |
| `beta_l_age2_f` | 0.00062525 | 0.00062525 | -2.007819e-10 |
| `beta_l_nkids_f` | 0.23890331 | 0.23890325 | -5.622827e-08 |
| `theta_l_f` | -0.73158866 | -0.73159014 | -1.477060e-06 |
| `beta_c` | 2.18201947 | 2.18203203 | +1.256061e-05 |
| `beta_ll` | 2.19491197 | 2.19490283 | -9.143895e-06 |

---

## 15. Gradient diagnostics at accepted and REOPT_FLOOR solutions

Largest absolute gradients at the accepted solution (Start A) and REOPT_FLOOR. Interior parameters should have near-zero gradients at a tolerance stop.

**At accepted (Start A):**

| Parameter | grad_ll |
|---|---|
| `beta_l0_m` | -6.080083 |
| `beta_w_pexp2` | 3.956203 |
| `beta_l_age2_f` | -2.401378 |
| `beta_l_age2_m` | 1.191019 |
| `beta_w_pexp` | 0.090764 |
| `beta_l_age_m` | 0.051401 |
| `theta_l_f` | -0.033012 |
| `beta_c` | 0.031554 |
| `beta_ll` | -0.022975 |
| `beta_occ_4_cf` | 0.021612 |
| `beta_l0_f` | -0.019226 |
| `beta_occ_3_cf` | -0.013604 |

**At REOPT_FLOOR:**

| Parameter | grad_ll |
|---|---|
| `beta_w_pexp2` | 9.065639 |
| `beta_l0_m` | -6.078539 |
| `beta_l_age2_f` | -1.872482 |
| `beta_l_age2_m` | 1.328910 |
| `beta_w_pexp` | 0.285675 |
| `beta_l_age_m` | 0.050828 |
| `beta_c` | 0.019414 |
| `beta_ll` | -0.017545 |
| `sigma` | -0.017412 |
| `beta_occ_3_cf` | -0.015634 |
| `beta_l0_f` | -0.014255 |
| `beta_occ_4_cf` | 0.011860 |

---

## 16. Substitution structure: beta_l0_m and beta_ll

The male leisure utility contribution enters the preference component as:

  `u_pref ∋ (beta_l0_m + beta_l_age_m·age + beta_l_age2_m·age²) · BC(l_m, theta_l_m)`

  `       + beta_ll · BC(l_m, theta_l_m) · BC(l_f, theta_l_f)`

When male leisure hours are constant (each alternative is fixed), a unit increase in beta_l0_m and a unit decrease in beta_ll have offsetting effects on the male leisure contribution only when female leisure (BC_l_f) ≈ 1. More precisely, the direction `(-1, +1)` in (beta_l0_m, beta_ll) space leaves the utility unchanged for a household with BC(l_f) = 1.

- CONOPT → accepted: Δbeta_l0_m = -1.221847e-02, Δbeta_ll = 1.316356e-02
- REOPT_FLOOR vs accepted: Δbeta_l0_m = 0.000000e+00, Δbeta_ll = -9.143895e-06
- REOPT_CONOPT vs accepted: Δbeta_l0_m = 1.221847e-02, Δbeta_ll = -1.353120e-02

**Interpretation check:** If |Δbeta_l0_m + Δbeta_ll| << |Δbeta_l0_m|, the two parameters move in near-unit substitution (weak identification of their individual contributions). If the ratio is far from 1, changes in beta_l0_m are partially but not fully absorbed by beta_ll.

- Net (Δbeta_l0_m + Δbeta_ll) for CONOPT→accepted: +9.450902e-04 (near-zero → near-unit substitution)

---

## 17. Disposition relative to Options A–D

**Option A: Keep beta_l0_m bounded and free (current state)**

- The current accepted solution is exactly Option A: beta_l0_m at lower bound, free.
- Inference would require boundary-aware treatment (active-set SEs or profile likelihood).
- Acceptable only with explicit inference treatment for the active constraint.


**Option B: Fix beta_l0_m at lower bound (1e-6) for SE run**

- REOPT_FLOOR (34-param reopt with beta_l0_m=1e-6): ΔLL = +1.083350e-06.
  (Negligible LL cost — Option B is clean.)

- If fixing beta_l0_m at floor leaves remaining estimates stable and ΔLL negligible, Option B is the leading pilot treatment: converts active constraint into explicit specification restriction and allows regular interior SEs for remaining 34 params.


**Option C: Relax lower bound (diagnostic probe only)**

- REOPT_NEG result: beta_l0_m = -0.00000006, ΔLL = +7.472263e-06.
  (Minimal improvement below zero — corner is near a flat region, not a genuine interior optimum below zero.)

- Not authorized as a specification change without a separate decision. Use only the REOPT_NEG result to inform the interpretation.


**Option D: Respecify or reparameterize male leisure block**

- Warranted if diagnostics show: (a) material fit deterioration under Option B, (b) large instability in other preference parameters, or (c) REOPT_NEG shows substantial improvement below zero inconsistent with economic regularity.
- Not the immediate treatment unless (a)-(c) are confirmed by these diagnostics.


---

## 18. Recommended diagnostic disposition

Based on the diagnostic evidence above:

**Recommended disposition: Option B (fix beta_l0_m at 1e-6 for SE run).**

- REOPT_FLOOR shows ΔLL = +1.083350e-06 — negligible LL cost from fixing at floor.
- The active-constraint corner is stable across all three scaled-JAX starts (LL spread 4.87e-3).
- Fixing at the floor converts an active constraint into an explicit specification restriction and enables regular interior SEs for the remaining 34 parameters.
- The REOPT_NEG diagnostic probe does not show material LL improvement below zero (ΔLL = +7.472263e-06).
- Parameter stability check: max |Δ| in key preference params (beta_ll, theta_l_m, beta_l0_f, beta_c) = 1.256061e-05.


---

## 19. SE computation readiness

**SE computation readiness: CONDITIONALLY READY under Option B.**

The diagnostic supports fixing beta_l0_m = 1e-6 and treating the remaining 34 parameters as an interior active-set specification. Under this treatment:
- The REOPT_FLOOR solution is the reference point for SE computation.
- Standard Hessian-based SEs apply to the 34 free parameters conditional on beta_l0_m = 1e-6.
- The SE for beta_l0_m itself is not computed (it is fixed by the active-set specification).
- A separate boundary-aware treatment (profile likelihood or constrained delta-method) would be required if Option A (bounded-and-free) is retained instead.

**SE computation remains blocked until the project governance explicitly authorizes the active-set specification under Option B.** This diagnostic provides the evidentiary basis for that decision; it does not itself constitute the authorization.

---

## 20. beta_ll identification assessment

The leisure interaction term beta_ll captures complementarity/substitutability between male and female leisure. It is distinct from the standalone male leisure intercept beta_l0_m: beta_ll multiplies the product of both Box-Cox leisure terms, while beta_l0_m multiplies only the male term.

The substitution pattern observed (Δbeta_l0_m ≈ −Δbeta_ll) is consistent with weak separate identification of beta_l0_m and beta_ll — but not with full collinearity, because the substitution direction is not exact (|BC(l_f)| ≠ 1 uniformly across alternatives). The fit implications (LL cost) and parameter stability across re-optimizations are the decisive evidence.


Fix at floor ΔLL = +1.083350e-06. Near-zero — consistent with a flat ridge: both parameters are weakly separately identified but jointly identified.

---

## 21. What was not computed

- No standard errors. No Hessian inversion. No cluster-robust SEs.
- No welfare computation. No inequality decomposition.
- No SA2. No NC pilot promotion. No M1-clean displacement.
- No 40x40 product set. No pooled estimation. No singles. No P3a rebuild.
- No production data modification. No frozen YAML modification.
- Negative beta_l0_m values in REOPT_NEG: diagnostic probe only, not adopted as a specification change.
- Economic interpretation of the active-bound result: none.
- Prior reports, oracle JSONs, pkl, and all production/pilot data: NOT modified.
- Model formula, data, bounds (native for production), kernel: UNCHANGED.

---

## 22. Required final statements

- **Diagnostic status: PASS.** All five jobs (PROFILE, REOPT_FLOOR, REOPT_CONOPT, REOPT_NEG, PARTICIPATION) completed without error.
- **beta_l0_m disposition:** Option B (fix at 1e-6) is supported by the diagnostic evidence. LL cost of fixing is negligible; remaining parameter estimates are stable.
- **SE computation:** Conditionally ready under Option B (active-set specification, 34 free params). Requires explicit governance authorization before execution.
- **Fixed-bound active-set treatment stability:** ΔLL = +1.083350e-06 (negligible); key preference parameters stable.
- **beta_ll absorption:** Δbeta_l0_m ≈ -1.221847e-02, Δbeta_ll ≈ +1.316356e-02 (CONOPT → accepted). Pattern is consistent with weak separate identification. See §9 and §16.
- **Male participation and hours fit:** See §12. Fit checked at accepted, REOPT_FLOOR, CONOPT, and profile points.
- **No welfare was computed.**
- **No SA2 was issued.**
- **The NC pilot was not promoted.**
- **M1-clean 2016 remains the active baseline.** Corrected pooled P3a unaffected.
- **Negative beta_l0_m (REOPT_NEG):** diagnostic probe only, explicitly bounded and labelled. Not a specification change.
- **Authorization:** `docs/France_case/NC_pilot/design/JMP_NC_pilot_beta_l0_m_specification_review_v1.md` s17.

---

*Status: beta_l0_m diagnostic v1. PASS. Total wall time: 261.1s. No SE/welfare/SA2/promotion. M1-clean 2016 active.*
