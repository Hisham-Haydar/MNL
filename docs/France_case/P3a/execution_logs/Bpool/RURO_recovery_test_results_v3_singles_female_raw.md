# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -11667.258 | 187 | 78.2 |
| cold | False | -11667.111 | 193 | 83.4 |

**G2** max|warm−cold| (testable) = 3.651e-01

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-1.013e-11**, max: 3.458e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sm', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sm', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sm', 'beta_l_nkids_f', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sm', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sm', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sm', 'theta_l_f', 'theta_l_m', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +2.7292 | 1.4792 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.4790 | 0.1210 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | -0.0193 | 0.1393 | n/a | True | True |
| theta_l_sm | -0.7500 | -1.4555 | 0.7055 | n/a | False | True |
| beta_l0_sf | +1.2500 | +6.4335 | 5.1835 | n/a | False | False |
| beta_l_age_sf | -0.6000 | -1.1183 | 0.5183 | n/a | False | False |
| beta_l_age2_sf | +0.1200 | +0.9000 | 0.7800 | n/a | False | False |
| beta_l_nkids_sf | -0.6000 | +4.4991 | 5.0991 | n/a | True | False |
| theta_l_sf | -1.2500 | -2.3744 | 1.1244 | n/a | False | False |
| theta_c_singles | -0.7500 | -0.0144 | 0.7356 | n/a | False | False |
| beta_l0_m | +0.0125 | +2.4832 | 2.4707 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.0001 | 0.5999 | n/a | False | True |
| beta_l_age2_m | +0.1200 | -0.0887 | 0.2087 | n/a | True | True |
| theta_l_m | -0.7500 | -0.7956 | 0.0456 | n/a | False | True |
| beta_l0_f | +1.2500 | +2.6431 | 1.3931 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.4802 | 0.1198 | n/a | False | True |
| beta_l_age2_f | +0.1200 | -0.2675 | 0.3875 | n/a | True | True |
| beta_l_nkids_f | -0.6000 | -0.0611 | 0.5389 | n/a | False | True |
| theta_l_f | -1.2500 | -1.8641 | 0.6141 | n/a | False | True |
| beta_E | -3.0000 | -1.0597 | 1.9403 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -0.9520 | 2.1520 | n/a | True | False |
| beta_h_pt2 | -1.2000 | +0.1366 | 1.3366 | n/a | True | False |
| beta_h_ft | +1.2000 | +0.6666 | 0.5334 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.6080 | 0.4080 | n/a | False | False |
| beta_E_gsur | +1.2000 | -2.3502 | 3.5502 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.1560 | 0.0440 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.1560 | 0.0440 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.1560 | 0.0440 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +0.4583 | 0.7417 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.1561 | 0.0439 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.1548 | 0.0452 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -0.8835 | 0.3165 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.4782 | 0.1218 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.2362 | 0.3638 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.1560 | 0.0440 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.1547 | 0.0453 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | +1.1606 | 0.0394 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.1559 | 0.0441 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.1719 | 0.0281 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -0.0205 | 1.1795 | n/a | False | False |
| beta_occ_3_sf | +1.2000 | -0.5014 | 1.7014 | n/a | True | False |
| beta_occ_4_sf | -1.2000 | +0.8260 | 2.0260 | n/a | True | False |
| beta_occ_2_cm | +1.2000 | +1.1560 | 0.0440 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.1560 | 0.0440 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.1606 | 0.0394 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1544 | 0.0456 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.1605 | 0.0395 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1547 | 0.0453 | n/a | False | True |
| beta_w0 | +2.5000 | +2.2244 | 0.2756 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.1022 | 0.0272 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.3387 | 0.0887 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.1854 | 0.1704 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0294 | 0.0290 | n/a | False | False |
| sigma | +0.3750 | +0.4017 | 0.0267 | n/a | False | False |
| beta_ll | +2.5000 | +3.0763 | 0.5763 | n/a | False | True |