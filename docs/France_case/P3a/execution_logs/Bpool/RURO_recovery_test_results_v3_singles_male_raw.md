# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 999999  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -9737.315 | 133 | 45.1 |
| cold | False | -9737.315 | 222 | 77.3 |

**G2** max|warm−cold| (testable) = 1.077e-02

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-5.785e-12**, max: 2.600e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'theta_l_f', 'theta_l_m', 'theta_l_sf']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +5.1025 | 3.8525 | n/a | False | False |
| beta_l_age_sm | -0.6000 | -0.6029 | 0.0029 | n/a | False | False |
| beta_l_age2_sm | +0.1200 | -0.1977 | 0.3177 | n/a | True | False |
| theta_l_sm | -0.7500 | -2.3128 | 1.5628 | n/a | False | False |
| beta_l0_sf | +1.2500 | +1.4808 | 0.2308 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.0130 | 0.1070 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.3404 | 0.0904 | n/a | False | True |
| theta_c_singles | -0.7500 | -0.0518 | 0.6982 | n/a | False | False |
| beta_l0_m | +0.0125 | +0.9865 | 0.9740 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| beta_l_age2_m | +0.1200 | +0.0460 | 0.0740 | n/a | False | True |
| theta_l_m | -0.7500 | -0.9198 | 0.1698 | n/a | False | True |
| beta_l0_f | +1.2500 | +1.4790 | 0.2290 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| beta_l_age2_f | +0.1200 | +0.0307 | 0.0893 | n/a | False | True |
| beta_l_nkids_f | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| theta_l_f | -1.2500 | -1.3461 | 0.0961 | n/a | False | True |
| beta_E | -3.0000 | -1.9628 | 1.0372 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -1.2761 | 2.4761 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -2.1132 | 0.9132 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.1423 | 0.0577 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.4093 | 0.2093 | n/a | False | False |
| beta_E_gsur | +1.2000 | -1.3677 | 2.5677 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.1892 | 0.0108 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.1885 | 0.0115 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.1880 | 0.0120 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.1908 | 0.0092 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.1896 | 0.0104 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.1880 | 0.0120 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -1.1885 | 0.0115 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.5787 | 0.0213 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.5787 | 0.0213 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.1896 | 0.0104 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.1880 | 0.0120 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | -1.4996 | 2.6996 | n/a | True | False |
| beta_occ_3_sm | -1.2000 | -2.0890 | 0.8890 | n/a | False | False |
| beta_occ_4_sm | +1.2000 | +0.0629 | 1.1371 | n/a | False | False |
| beta_occ_2_sf | -1.2000 | -1.1880 | 0.0120 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.1868 | 0.0132 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.1868 | 0.0132 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.1868 | 0.0132 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.1874 | 0.0126 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.1862 | 0.0138 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1868 | 0.0132 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.1885 | 0.0115 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1862 | 0.0138 | n/a | False | True |
| beta_w0 | +2.5000 | +2.1670 | 0.3330 | n/a | False | False |
| beta_w_educL | -0.0750 | +0.1460 | 0.2210 | n/a | True | False |
| beta_w_educH | +0.2500 | +0.3307 | 0.0807 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.3228 | 0.3078 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0753 | 0.0749 | n/a | False | False |
| sigma | +0.3750 | +0.4237 | 0.0487 | n/a | False | False |
| beta_ll | +2.5000 | +2.5974 | 0.0974 | n/a | False | True |