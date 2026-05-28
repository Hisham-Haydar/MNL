# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -11140.581 | 187 | 77.2 |
| cold | False | -11140.614 | 260 | 107.5 |

**G2** max|warm−cold| (testable) = 3.535e-02

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-2.562e+01**, max: 3.328e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sm', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sm', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sm', 'beta_l_nkids_f', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sm', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sm', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sm', 'theta_l_f', 'theta_l_m', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +1.4302 | 0.1802 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.8796 | 0.2796 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.5344 | 0.4144 | n/a | False | True |
| theta_l_sm | -0.7500 | -2.8047 | 2.0547 | n/a | False | True |
| beta_l0_sf | +1.2500 | +0.0510 | 1.1990 | n/a | False | False |
| beta_l_age_sf | -0.6000 | -0.6304 | 0.0304 | n/a | False | False |
| beta_l_age2_sf | +0.1200 | -0.9969 | 1.1169 | n/a | True | False |
| beta_l_nkids_sf | -0.6000 | -1.1066 | 0.5066 | n/a | False | False |
| theta_l_sf | -1.2500 | +0.1257 | 1.3757 | n/a | True | False |
| theta_c_singles | -0.7500 | +0.0473 | 0.7973 | n/a | True | False |
| beta_l0_m | +0.0125 | +0.6495 | 0.6370 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.6549 | 0.0549 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.0792 | 0.0408 | n/a | False | True |
| theta_l_m | -0.7500 | -1.6816 | 0.9316 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.4562 | 0.2062 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.7131 | 0.1131 | n/a | False | True |
| beta_l_age2_f | +0.1200 | -0.0199 | 0.1399 | n/a | True | True |
| beta_l_nkids_f | -0.6000 | -0.5916 | 0.0084 | n/a | False | True |
| theta_l_f | -1.2500 | -1.4089 | 0.1589 | n/a | False | True |
| beta_E | -3.0000 | -1.4983 | 1.5017 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -0.7894 | 1.9894 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -0.0682 | 1.1318 | n/a | False | False |
| beta_h_ft | +1.2000 | -0.0303 | 1.2303 | n/a | True | False |
| beta_h_lh | -1.2000 | -9.9645 | 8.7645 | n/a | False | False |
| beta_E_gsur | +1.2000 | -2.6232 | 3.8232 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -0.6353 | 0.5647 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | -0.0707 | 1.2707 | n/a | True | True |
| beta_E_drgn4 | -1.2000 | -0.5646 | 0.6354 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.7614 | 0.5614 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | +0.0321 | 1.2321 | n/a | True | True |
| beta_E_drgn7 | +1.2000 | +1.1950 | 0.0050 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -0.7593 | 0.4407 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +1.1989 | 0.5989 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.2081 | 0.3919 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.4041 | 0.2041 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.1986 | 0.0014 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | +1.1963 | 0.0037 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.1979 | 0.0021 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +0.9904 | 0.2096 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -0.0124 | 1.1876 | n/a | False | False |
| beta_occ_3_sf | +1.2000 | -0.5137 | 1.7137 | n/a | True | False |
| beta_occ_4_sf | -1.2000 | +0.8360 | 2.0360 | n/a | True | False |
| beta_occ_2_cm | +1.2000 | +2.4035 | 1.2035 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -0.9445 | 0.2555 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +2.7698 | 1.5698 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1978 | 0.0022 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +0.9936 | 0.2064 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1976 | 0.0024 | n/a | False | True |
| beta_w0 | +2.5000 | +2.2201 | 0.2799 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.1156 | 0.0406 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.3437 | 0.0937 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.1922 | 0.1772 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0314 | 0.0311 | n/a | False | False |
| sigma | +0.3750 | +0.4010 | 0.0260 | n/a | False | False |
| beta_ll | +2.5000 | +2.5547 | 0.0547 | n/a | False | True |