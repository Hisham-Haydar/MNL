# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** couples  **years:** 2016  **n_hh:** 300  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -6479.273 | 353 | 439.6 |
| cold | False | -6527.245 | 295 | 389.5 |

**G2** max|warm−cold| (testable) = 6.691e+00

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-1.728e+02**, max: 1.638e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_y2015', 'beta_E_y2017', 'beta_l0_sf', 'beta_l0_sm', 'beta_l_age2_sf', 'beta_l_age2_sm', 'beta_l_age_sf', 'beta_l_age_sm', 'beta_l_nkids_sf', 'beta_occ_2_sf', 'beta_occ_2_sm', 'beta_occ_3_sf', 'beta_occ_3_sm', 'beta_occ_4_sf', 'beta_occ_4_sm', 'theta_c_singles', 'theta_l_sf', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +2.6153 | 1.3653 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.3671 | 0.2329 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.0404 | 0.0796 | n/a | False | True |
| theta_l_sm | -0.7500 | -2.0610 | 1.3110 | n/a | False | True |
| beta_l0_sf | +1.2500 | +3.2874 | 2.0374 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.5202 | 0.0798 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | -0.1025 | 0.2225 | n/a | True | True |
| beta_l_nkids_sf | -0.6000 | -0.3549 | 0.2451 | n/a | False | True |
| theta_l_sf | -1.2500 | -2.7206 | 1.4706 | n/a | False | True |
| theta_c_singles | -0.7500 | -1.6110 | 0.8610 | n/a | False | True |
| beta_l0_m | +0.0125 | +0.0004 | 0.0121 | n/a | False | False |
| beta_l_age_m | -0.6000 | +0.0469 | 0.6469 | n/a | True | False |
| beta_l_age2_m | +0.1200 | -0.9819 | 1.1019 | n/a | True | False |
| theta_l_m | -0.7500 | +0.9452 | 1.6952 | n/a | True | False |
| beta_l0_f | +1.2500 | +0.0571 | 1.1929 | n/a | False | False |
| beta_l_age_f | -0.6000 | -0.4172 | 0.1828 | n/a | False | False |
| beta_l_age2_f | +0.1200 | -0.9850 | 1.1050 | n/a | True | False |
| beta_l_nkids_f | -0.6000 | -1.2839 | 0.6839 | n/a | False | False |
| theta_l_f | -1.2500 | +0.1159 | 1.3659 | n/a | True | False |
| beta_E | -3.0000 | +0.7473 | 3.7473 | n/a | True | False |
| beta_h_pt1 | +1.2000 | -1.9009 | 3.1009 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -0.2042 | 0.9958 | n/a | False | False |
| beta_h_ft | +1.2000 | +0.1625 | 1.0375 | n/a | False | False |
| beta_h_lh | -1.2000 | -9.9900 | 8.7900 | n/a | False | False |
| beta_E_gsur | +1.2000 | -3.3501 | 4.5501 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.0699 | 0.1301 | n/a | False | False |
| beta_E_drgn3 | +1.2000 | +0.7379 | 0.4621 | n/a | False | False |
| beta_E_drgn4 | -1.2000 | -0.2904 | 0.9096 | n/a | False | False |
| beta_E_drgn5 | +1.2000 | -0.6194 | 1.8194 | n/a | True | False |
| beta_E_drgn6 | -1.2000 | +3.4964 | 4.6964 | n/a | True | False |
| beta_E_drgn7 | +1.2000 | +0.7479 | 0.4521 | n/a | False | False |
| beta_E_drgn8 | -1.2000 | +3.3555 | 4.5555 | n/a | True | False |
| beta_E_y2015 | +0.6000 | +0.5143 | 0.0857 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.5873 | 0.0127 | n/a | False | True |
| beta_E_drgur | +1.2000 | -0.0466 | 1.2466 | n/a | True | False |
| beta_E_drgmd | -1.2000 | -0.4565 | 0.7435 | n/a | False | False |
| beta_occ_2_sm | +1.2000 | +1.1743 | 0.0257 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.5658 | 0.3658 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.1021 | 0.0979 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -1.0912 | 0.1088 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.0953 | 0.1047 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.3839 | 0.1839 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | -1.8366 | 3.0366 | n/a | True | False |
| beta_occ_3_cm | -1.2000 | -1.8866 | 0.6866 | n/a | False | False |
| beta_occ_4_cm | +1.2000 | +0.7446 | 0.4554 | n/a | False | False |
| beta_occ_2_cf | -1.2000 | -0.0888 | 1.1112 | n/a | False | False |
| beta_occ_3_cf | +1.2000 | -0.6285 | 1.8285 | n/a | True | False |
| beta_occ_4_cf | -1.2000 | +0.6666 | 1.8666 | n/a | True | False |
| beta_w0 | +2.5000 | +2.2913 | 0.2087 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.1800 | 0.1050 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.3046 | 0.0546 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.3930 | 0.3780 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0959 | 0.0956 | n/a | False | False |
| sigma | +0.3750 | +0.3749 | 0.0001 | n/a | False | False |
| beta_ll | +2.5000 | +0.0002 | 2.4998 | n/a | False | False |