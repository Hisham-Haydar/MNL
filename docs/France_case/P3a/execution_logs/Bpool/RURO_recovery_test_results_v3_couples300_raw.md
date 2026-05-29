# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** couples  **years:** 2016  **n_hh:** 300  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -7140.617 | 52 | 94.3 |
| cold | False | -6955.215 | 396 | 494.2 |

**G2** max|warm−cold| (testable) = 4.825e+01

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-2.307e+02**, max: 7.465e+03

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_y2015', 'beta_E_y2017', 'beta_l0_sf', 'beta_l0_sm', 'beta_l_age2_sf', 'beta_l_age2_sm', 'beta_l_age_sf', 'beta_l_age_sm', 'beta_l_nkids_sf', 'beta_occ_2_sf', 'beta_occ_2_sm', 'beta_occ_3_sf', 'beta_occ_3_sm', 'beta_occ_4_sf', 'beta_occ_4_sm', 'theta_c_singles', 'theta_l_sf', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +1.4993 | 0.2493 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.6678 | 0.0678 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.1646 | 0.0446 | n/a | False | True |
| theta_l_sm | -0.7500 | -0.6402 | 0.1098 | n/a | False | True |
| beta_l0_sf | +1.2500 | +1.4993 | 0.2493 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.5965 | 0.0035 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.1646 | 0.0446 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.5965 | 0.0035 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.2913 | 0.0413 | n/a | False | True |
| theta_c_singles | -0.7500 | -0.7115 | 0.0385 | n/a | False | True |
| beta_l0_m | +0.0125 | +0.0024 | 0.0101 | n/a | False | False |
| beta_l_age_m | -0.6000 | -0.5642 | 0.0358 | n/a | False | False |
| beta_l_age2_m | +0.1200 | -0.0763 | 0.1963 | n/a | True | False |
| theta_l_m | -0.7500 | -1.4465 | 0.6965 | n/a | False | False |
| beta_l0_f | +1.2500 | +1.6199 | 0.3699 | n/a | False | False |
| beta_l_age_f | -0.6000 | -0.5649 | 0.0351 | n/a | False | False |
| beta_l_age2_f | +0.1200 | +0.3327 | 0.2127 | n/a | False | False |
| beta_l_nkids_f | -0.6000 | -0.3380 | 0.2620 | n/a | False | False |
| theta_l_f | -1.2500 | -1.3283 | 0.0783 | n/a | False | False |
| beta_E | -3.0000 | -3.0164 | 0.0164 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -0.7677 | 1.9677 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -0.8110 | 0.3890 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.5541 | 0.3541 | n/a | False | False |
| beta_h_lh | -1.2000 | -0.7579 | 0.4421 | n/a | False | False |
| beta_E_gsur | +1.2000 | +0.9484 | 0.2516 | n/a | False | False |
| beta_E_drgn2 | -1.2000 | -1.2135 | 0.0135 | n/a | False | False |
| beta_E_drgn3 | +1.2000 | +1.1359 | 0.0641 | n/a | False | False |
| beta_E_drgn4 | -1.2000 | -1.1235 | 0.0765 | n/a | False | False |
| beta_E_drgn5 | +1.2000 | +1.1282 | 0.0718 | n/a | False | False |
| beta_E_drgn6 | -1.2000 | -1.1468 | 0.0532 | n/a | False | False |
| beta_E_drgn7 | +1.2000 | +1.1894 | 0.0106 | n/a | False | False |
| beta_E_drgn8 | -1.2000 | -1.1584 | 0.0416 | n/a | False | False |
| beta_E_y2015 | +0.6000 | +0.6678 | 0.0678 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.6678 | 0.0678 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.0923 | 0.1077 | n/a | False | False |
| beta_E_drgmd | -1.2000 | -1.0040 | 0.1960 | n/a | False | False |
| beta_occ_2_sm | +1.2000 | +1.2007 | 0.0007 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.2007 | 0.0007 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.2007 | 0.0007 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -1.2007 | 0.0007 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.2007 | 0.0007 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.2007 | 0.0007 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | -0.2116 | 1.4116 | n/a | True | False |
| beta_occ_3_cm | -1.2000 | -1.2674 | 0.0674 | n/a | False | False |
| beta_occ_4_cm | +1.2000 | +1.3876 | 0.1876 | n/a | False | False |
| beta_occ_2_cf | -1.2000 | -0.5989 | 0.6011 | n/a | False | False |
| beta_occ_3_cf | +1.2000 | -1.0258 | 2.2258 | n/a | True | False |
| beta_occ_4_cf | -1.2000 | +0.6645 | 1.8645 | n/a | True | False |
| beta_w0 | +2.5000 | +2.3081 | 0.1919 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.2825 | 0.2075 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.4624 | 0.2124 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.2322 | 0.2172 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0992 | 0.0988 | n/a | False | False |
| sigma | +0.3750 | +0.5311 | 0.1561 | n/a | False | False |
| beta_ll | +2.5000 | +2.3946 | 0.1054 | n/a | False | False |