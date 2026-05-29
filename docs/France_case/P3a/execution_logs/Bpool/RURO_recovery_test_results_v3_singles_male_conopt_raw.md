# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** gamspy-conopt  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | True | -2501.766 | 15 | 30.0 |

**G2** max|warm−cold| (testable) = nan

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-4.050e+00**, max: 3.271e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'theta_l_f', 'theta_l_m', 'theta_l_sf']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +1.7797 | 0.5297 | n/a | False | False |
| beta_l_age_sm | -0.6000 | -0.4786 | 0.1214 | n/a | False | False |
| beta_l_age2_sm | +0.1200 | +0.3517 | 0.2317 | n/a | False | False |
| theta_l_sm | -0.7500 | -1.0481 | 0.2981 | n/a | False | False |
| beta_l0_sf | +1.2500 | +1.2500 | 0.0000 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.2500 | 0.0000 | n/a | False | True |
| theta_c_singles | -0.7500 | -0.7992 | 0.0492 | n/a | False | False |
| beta_l0_m | +0.0125 | +0.0125 | 0.0000 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| theta_l_m | -0.7500 | -0.7500 | 0.0000 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.2500 | 0.0000 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_f | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| beta_l_nkids_f | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| theta_l_f | -1.2500 | -1.2500 | 0.0000 | n/a | False | True |
| beta_E | -3.0000 | -9.0707 | 6.0707 | n/a | False | False |
| beta_h_pt1 | +1.2000 | +1.0865 | 0.1135 | n/a | False | False |
| beta_h_pt2 | -1.2000 | -1.5321 | 0.3321 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.1606 | 0.0394 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.1662 | 0.0338 | n/a | False | False |
| beta_E_gsur | +1.2000 | +8.5676 | 7.3676 | n/a | False | False |
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
| beta_occ_2_sm | +1.2000 | +1.3596 | 0.1596 | n/a | False | False |
| beta_occ_3_sm | -1.2000 | -0.7665 | 0.4335 | n/a | False | False |
| beta_occ_4_sm | +1.2000 | +1.3662 | 0.1662 | n/a | False | False |
| beta_occ_2_sf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_w0 | +2.5000 | +2.4121 | 0.0879 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.1139 | 0.0389 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.2687 | 0.0187 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.1633 | 0.1483 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0355 | 0.0351 | n/a | False | False |
| sigma | +0.3750 | +0.3684 | 0.0066 | n/a | False | False |
| beta_ll | +2.5000 | +2.5000 | 0.0000 | n/a | False | True |