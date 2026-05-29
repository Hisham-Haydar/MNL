# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** gamspy-conopt  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | True | -2734.013 | 10 | 31.1 |
| cold | True | -2734.013 | 13 | 34.5 |

**G2** max|warm−cold| (testable) = 6.000e-01

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-1.565e+01**, max: 3.616e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sm', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sm', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sm', 'beta_l_nkids_f', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sm', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sm', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sm', 'theta_l_f', 'theta_l_m', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +0.0500 | 1.2000 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.1148 | 0.4852 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.2307 | 0.1107 | n/a | False | True |
| theta_l_sm | -0.7500 | -1.0609 | 0.3109 | n/a | False | True |
| beta_l0_sf | +1.2500 | +1.2500 | 0.0000 | n/a | False | False |
| beta_l_age_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | False |
| beta_l_age2_sf | +0.1200 | +0.1200 | 0.0000 | n/a | False | False |
| beta_l_nkids_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | False |
| theta_l_sf | -1.2500 | -1.2500 | 0.0000 | n/a | False | False |
| theta_c_singles | -0.7500 | -0.7342 | 0.0158 | n/a | False | False |
| beta_l0_m | +0.0125 | +0.0125 | 0.0000 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| theta_l_m | -0.7500 | -0.7500 | 0.0000 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.2500 | 0.0000 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_f | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| beta_l_nkids_f | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| theta_l_f | -1.2500 | -1.2500 | 0.0000 | n/a | False | True |
| beta_E | -3.0000 | -4.0376 | 1.0376 | n/a | False | False |
| beta_h_pt1 | +1.2000 | +1.2601 | 0.0601 | n/a | False | False |
| beta_h_pt2 | -1.2000 | -0.7363 | 0.4637 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.2959 | 0.0959 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.2568 | 0.0568 | n/a | False | False |
| beta_E_gsur | +1.2000 | +2.0114 | 0.8114 | n/a | False | False |
| beta_E_drgn2 | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.6000 | 0.0000 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -1.0662 | 0.1338 | n/a | False | False |
| beta_occ_3_sf | +1.2000 | +1.3124 | 0.1124 | n/a | False | False |
| beta_occ_4_sf | -1.2000 | -0.9639 | 0.2361 | n/a | False | False |
| beta_occ_2_cm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_w0 | +2.5000 | +2.4479 | 0.0521 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.0173 | 0.0577 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.2158 | 0.0342 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.0854 | 0.0704 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0265 | 0.0261 | n/a | False | False |
| sigma | +0.3750 | +0.3803 | 0.0053 | n/a | False | False |
| beta_ll | +2.5000 | +2.5000 | 0.0000 | n/a | False | True |