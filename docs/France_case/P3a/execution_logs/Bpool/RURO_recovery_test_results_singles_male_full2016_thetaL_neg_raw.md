# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -9184.570 | 130 | 49.7 |
| cold | False | -9184.559 | 224 | 81.0 |

**G2** max|warm−cold| (testable) = 1.218e-02

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-7.750e+01**, max: 2.411e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'theta_l_f', 'theta_l_m', 'theta_l_sf']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +0.0509 | 1.1991 | n/a | False | False |
| beta_l_age_sm | -0.6000 | +0.3764 | 0.9764 | n/a | True | False |
| beta_l_age2_sm | +0.1200 | -0.9988 | 1.1188 | n/a | True | False |
| theta_l_sm | -0.7500 | -0.0511 | 0.6989 | n/a | False | False |
| beta_l0_sf | +1.2500 | +1.3337 | 0.0837 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.6330 | 0.0330 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.1048 | 0.0152 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.5646 | 0.0354 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.3138 | 0.0638 | n/a | False | True |
| theta_c_singles | -0.7500 | -0.0287 | 0.7213 | n/a | False | False |
| beta_l0_m | +0.0125 | +0.4398 | 0.4273 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.5611 | 0.0389 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.0284 | 0.0916 | n/a | False | True |
| theta_l_m | -0.7500 | -0.8314 | 0.0814 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.3285 | 0.0785 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.6161 | 0.0161 | n/a | False | True |
| beta_l_age2_f | +0.1200 | +0.1561 | 0.0361 | n/a | False | True |
| beta_l_nkids_f | -0.6000 | -0.8358 | 0.2358 | n/a | False | True |
| theta_l_f | -1.2500 | -1.3242 | 0.0742 | n/a | False | True |
| beta_E | -3.0000 | -1.8885 | 1.1115 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -1.4667 | 2.6667 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -2.4763 | 1.2763 | n/a | False | False |
| beta_h_ft | +1.2000 | +0.5185 | 0.6815 | n/a | False | False |
| beta_h_lh | -1.2000 | -9.9284 | 8.7284 | n/a | False | False |
| beta_E_gsur | +1.2000 | -1.4457 | 2.6457 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.2151 | 0.0151 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.2149 | 0.0149 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.1907 | 0.0093 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.2148 | 0.0148 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.2150 | 0.0150 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.2148 | 0.0148 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -1.2148 | 0.0148 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.6945 | 0.0945 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.8073 | 0.2073 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.2149 | 0.0149 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.2146 | 0.0146 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | -1.5262 | 2.7262 | n/a | True | False |
| beta_occ_3_sm | -1.2000 | -2.1305 | 0.9305 | n/a | False | False |
| beta_occ_4_sm | +1.2000 | +0.0396 | 1.1604 | n/a | False | False |
| beta_occ_2_sf | -1.2000 | -0.9514 | 0.2486 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.1552 | 0.0448 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.0956 | 0.1044 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.1862 | 0.0138 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.1869 | 0.0131 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.1856 | 0.0144 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1856 | 0.0144 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.1858 | 0.0142 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1560 | 0.0440 | n/a | False | True |
| beta_w0 | +2.5000 | +2.1437 | 0.3563 | n/a | False | False |
| beta_w_educL | -0.0750 | +0.1566 | 0.2316 | n/a | True | False |
| beta_w_educH | +0.2500 | +0.3466 | 0.0966 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.3464 | 0.3314 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0815 | 0.0811 | n/a | False | False |
| sigma | +0.3750 | +0.4272 | 0.0522 | n/a | False | False |
| beta_ll | +2.5000 | +2.5412 | 0.0412 | n/a | False | True |