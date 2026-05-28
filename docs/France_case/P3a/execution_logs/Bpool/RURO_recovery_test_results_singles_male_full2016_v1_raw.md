# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -9157.949 | 134 | 50.0 |
| cold | False | -9157.949 | 223 | 83.5 |

**G2** max|warm−cold| (testable) = 8.630e-03

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-8.404e+01**, max: 2.334e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'theta_l_f', 'theta_l_m', 'theta_l_sf']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +0.0501 | 1.1999 | n/a | False | False |
| beta_l_age_sm | -0.6000 | +0.0534 | 0.6534 | n/a | True | False |
| beta_l_age2_sm | +0.1200 | -0.9992 | 1.1192 | n/a | True | False |
| theta_l_sm | -0.7500 | +0.3683 | 1.1183 | n/a | True | False |
| beta_l0_sf | +1.2500 | +1.3365 | 0.0865 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.5978 | 0.0022 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.0475 | 0.0725 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.5970 | 0.0030 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.3389 | 0.0889 | n/a | False | True |
| theta_c_singles | -0.7500 | +0.0088 | 0.7588 | n/a | True | False |
| beta_l0_m | +0.0125 | +0.5434 | 0.5309 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.5974 | 0.0026 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.1512 | 0.0312 | n/a | False | True |
| theta_l_m | -0.7500 | -0.8219 | 0.0719 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.3374 | 0.0874 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.5969 | 0.0031 | n/a | False | True |
| beta_l_age2_f | +0.1200 | -0.1840 | 0.3040 | n/a | True | True |
| beta_l_nkids_f | -0.6000 | -0.6077 | 0.0077 | n/a | False | True |
| theta_l_f | -1.2500 | -1.3289 | 0.0789 | n/a | False | True |
| beta_E | -3.0000 | -1.9919 | 1.0081 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -1.2991 | 2.4991 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -2.4260 | 1.2260 | n/a | False | False |
| beta_h_ft | +1.2000 | +0.3855 | 0.8145 | n/a | False | False |
| beta_h_lh | -1.2000 | -9.9968 | 8.7968 | n/a | False | False |
| beta_E_gsur | +1.2000 | -1.5919 | 2.7919 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.2015 | 0.0015 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.2015 | 0.0015 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.1957 | 0.0043 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.2015 | 0.0015 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.2015 | 0.0015 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.2015 | 0.0015 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -1.1957 | 0.0043 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.5968 | 0.0032 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.6064 | 0.0064 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.1967 | 0.0033 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.1967 | 0.0033 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | -1.5392 | 2.7392 | n/a | True | False |
| beta_occ_3_sm | -1.2000 | -2.1582 | 0.9582 | n/a | False | False |
| beta_occ_4_sm | +1.2000 | +0.0311 | 1.1689 | n/a | False | False |
| beta_occ_2_sf | -1.2000 | -1.1966 | 0.0034 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.1969 | 0.0031 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.1969 | 0.0031 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.1969 | 0.0031 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.1969 | 0.0031 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.1966 | 0.0034 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1969 | 0.0031 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.1969 | 0.0031 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1968 | 0.0032 | n/a | False | True |
| beta_w0 | +2.5000 | +2.1374 | 0.3626 | n/a | False | False |
| beta_w_educL | -0.0750 | +0.1602 | 0.2352 | n/a | True | False |
| beta_w_educH | +0.2500 | +0.3448 | 0.0948 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.3710 | 0.3560 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0950 | 0.0946 | n/a | False | False |
| sigma | +0.3750 | +0.4285 | 0.0535 | n/a | False | False |
| beta_ll | +2.5000 | +2.5604 | 0.0604 | n/a | False | True |