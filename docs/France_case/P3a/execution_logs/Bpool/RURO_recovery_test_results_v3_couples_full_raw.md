# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** couples  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -60707.633 | 334 | 4570.9 |
| cold | False | -60707.717 | 271 | 3964.7 |

**G2** max|warm−cold| (testable) = 5.057e-02

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-1.410e-03**, max: 1.343e+05

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_y2015', 'beta_E_y2017', 'beta_l0_sf', 'beta_l0_sm', 'beta_l_age2_sf', 'beta_l_age2_sm', 'beta_l_age_sf', 'beta_l_age_sm', 'beta_l_nkids_sf', 'beta_occ_2_sf', 'beta_occ_2_sm', 'beta_occ_3_sf', 'beta_occ_3_sm', 'beta_occ_4_sf', 'beta_occ_4_sm', 'theta_c_singles', 'theta_l_sf', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +1.8680 | 0.6180 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.6051 | 0.0051 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | -0.0453 | 0.1653 | n/a | True | True |
| theta_l_sm | -0.7500 | -1.2781 | 0.5281 | n/a | False | True |
| beta_l0_sf | +1.2500 | +1.8349 | 0.5849 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.6176 | 0.0176 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | -0.0259 | 0.1459 | n/a | True | True |
| beta_l_nkids_sf | -0.6000 | -0.5914 | 0.0086 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.2622 | 0.0122 | n/a | False | True |
| theta_c_singles | -0.7500 | -1.3077 | 0.5577 | n/a | False | True |
| beta_l0_m | +0.0125 | +0.0177 | 0.0052 | n/a | False | False |
| beta_l_age_m | -0.6000 | -0.1227 | 0.4773 | n/a | False | False |
| beta_l_age2_m | +0.1200 | +0.1116 | 0.0084 | n/a | False | False |
| theta_l_m | -0.7500 | -2.3015 | 1.5515 | n/a | False | False |
| beta_l0_f | +1.2500 | +7.8001 | 6.5501 | n/a | False | False |
| beta_l_age_f | -0.6000 | -1.4741 | 0.8741 | n/a | False | False |
| beta_l_age2_f | +0.1200 | +0.6086 | 0.4886 | n/a | False | False |
| beta_l_nkids_f | -0.6000 | +0.6312 | 1.2312 | n/a | True | False |
| theta_l_f | -1.2500 | -1.8796 | 0.6296 | n/a | False | False |
| beta_E | -3.0000 | -0.8009 | 2.1991 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -1.6939 | 2.8939 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -0.0670 | 1.1330 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.1053 | 0.0947 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.0170 | 0.1830 | n/a | False | False |
| beta_E_gsur | +1.2000 | -1.3444 | 2.5444 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | +0.0709 | 1.2709 | n/a | True | False |
| beta_E_drgn3 | +1.2000 | +0.2514 | 0.9486 | n/a | False | False |
| beta_E_drgn4 | -1.2000 | +0.7725 | 1.9725 | n/a | True | False |
| beta_E_drgn5 | +1.2000 | +0.1657 | 1.0343 | n/a | False | False |
| beta_E_drgn6 | -1.2000 | +0.2966 | 1.4966 | n/a | True | False |
| beta_E_drgn7 | +1.2000 | +0.1284 | 1.0716 | n/a | False | False |
| beta_E_drgn8 | -1.2000 | -0.0236 | 1.1764 | n/a | False | False |
| beta_E_y2015 | +0.6000 | +0.5957 | 0.0043 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.5987 | 0.0013 | n/a | False | True |
| beta_E_drgur | +1.2000 | -0.1659 | 1.3659 | n/a | True | False |
| beta_E_drgmd | -1.2000 | -0.7118 | 0.4882 | n/a | False | False |
| beta_occ_2_sm | +1.2000 | +1.1188 | 0.0812 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.1232 | 0.0768 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.1230 | 0.0770 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -1.1235 | 0.0765 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.1235 | 0.0765 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.1230 | 0.0770 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | -1.5789 | 2.7789 | n/a | True | False |
| beta_occ_3_cm | -1.2000 | -2.4050 | 1.2050 | n/a | False | False |
| beta_occ_4_cm | +1.2000 | +0.3405 | 0.8595 | n/a | False | False |
| beta_occ_2_cf | -1.2000 | +0.0806 | 1.2806 | n/a | True | False |
| beta_occ_3_cf | +1.2000 | -0.3711 | 1.5711 | n/a | True | False |
| beta_occ_4_cf | -1.2000 | +0.7945 | 1.9945 | n/a | True | False |
| beta_w0 | +2.5000 | +2.2164 | 0.2836 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.1068 | 0.0318 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.3524 | 0.1024 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.3682 | 0.3532 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0768 | 0.0764 | n/a | False | False |
| sigma | +0.3750 | +0.4119 | 0.0369 | n/a | False | False |
| beta_ll | +2.5000 | +5.0779 | 2.5779 | n/a | False | False |