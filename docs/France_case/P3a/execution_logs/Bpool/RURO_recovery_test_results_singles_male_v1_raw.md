# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** singles  **years:** 2016  **n_hh:** 300  **solver:** scipy-trustconstr  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | False | -3551.729 | 170 | 27.1 |
| cold | False | -3551.715 | 207 | 32.6 |

**G2** max|warm−cold| (testable) = 1.535e+00

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-3.072e+01**, max: 1.231e+04

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_drgmd', 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5', 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8', 'beta_E_drgur', 'beta_E_y2015', 'beta_E_y2017', 'beta_l0_f', 'beta_l0_m', 'beta_l0_sf', 'beta_l_age2_f', 'beta_l_age2_m', 'beta_l_age2_sf', 'beta_l_age_f', 'beta_l_age_m', 'beta_l_age_sf', 'beta_l_nkids_f', 'beta_l_nkids_sf', 'beta_ll', 'beta_occ_2_cf', 'beta_occ_2_cm', 'beta_occ_2_sf', 'beta_occ_3_cf', 'beta_occ_3_cm', 'beta_occ_3_sf', 'beta_occ_4_cf', 'beta_occ_4_cm', 'beta_occ_4_sf', 'theta_l_f', 'theta_l_m', 'theta_l_sf']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +0.0501 | 1.1999 | n/a | False | False |
| beta_l_age_sm | -0.6000 | +0.3996 | 0.9996 | n/a | True | False |
| beta_l_age2_sm | +0.1200 | -0.9992 | 1.1192 | n/a | True | False |
| theta_l_sm | -0.7500 | +0.2947 | 1.0447 | n/a | True | False |
| beta_l0_sf | +1.2500 | +2.4752 | 1.2252 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.5293 | 0.0707 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | -0.0211 | 0.1411 | n/a | True | True |
| beta_l_nkids_sf | -0.6000 | -0.5295 | 0.0705 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.6260 | 0.3760 | n/a | False | True |
| theta_c_singles | -0.7500 | +0.1433 | 0.8933 | n/a | True | False |
| beta_l0_m | +0.0125 | +4.1991 | 4.1866 | n/a | False | True |
| beta_l_age_m | -0.6000 | -0.5227 | 0.0773 | n/a | False | True |
| beta_l_age2_m | +0.1200 | -0.0349 | 0.1549 | n/a | True | True |
| theta_l_m | -0.7500 | -1.6601 | 0.9101 | n/a | False | True |
| beta_l0_f | +1.2500 | +2.4722 | 1.2222 | n/a | False | True |
| beta_l_age_f | -0.6000 | -0.5294 | 0.0706 | n/a | False | True |
| beta_l_age2_f | +0.1200 | -0.7704 | 0.8904 | n/a | True | True |
| beta_l_nkids_f | -0.6000 | -0.5223 | 0.0777 | n/a | False | True |
| theta_l_f | -1.2500 | -1.6194 | 0.3694 | n/a | False | True |
| beta_E | -3.0000 | -2.2035 | 0.7965 | n/a | False | False |
| beta_h_pt1 | +1.2000 | -1.5288 | 2.7288 | n/a | True | False |
| beta_h_pt2 | -1.2000 | -8.0692 | 6.8692 | n/a | False | False |
| beta_h_ft | +1.2000 | +0.6609 | 0.5391 | n/a | False | False |
| beta_h_lh | -1.2000 | -9.9981 | 8.7981 | n/a | False | False |
| beta_E_gsur | +1.2000 | -1.4328 | 2.6328 | n/a | True | False |
| beta_E_drgn2 | -1.2000 | -1.1703 | 0.0297 | n/a | False | True |
| beta_E_drgn3 | +1.2000 | +1.1702 | 0.0298 | n/a | False | True |
| beta_E_drgn4 | -1.2000 | -1.1712 | 0.0288 | n/a | False | True |
| beta_E_drgn5 | +1.2000 | +1.1706 | 0.0294 | n/a | False | True |
| beta_E_drgn6 | -1.2000 | -1.1881 | 0.0119 | n/a | False | True |
| beta_E_drgn7 | +1.2000 | +1.1706 | 0.0294 | n/a | False | True |
| beta_E_drgn8 | -1.2000 | -1.1786 | 0.0214 | n/a | False | True |
| beta_E_y2015 | +0.6000 | +0.5263 | 0.0737 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.5307 | 0.0693 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.1772 | 0.0228 | n/a | False | True |
| beta_E_drgmd | -1.2000 | -1.1761 | 0.0239 | n/a | False | True |
| beta_occ_2_sm | +1.2000 | -1.5719 | 2.7719 | n/a | True | False |
| beta_occ_3_sm | -1.2000 | -2.0134 | 0.8134 | n/a | False | False |
| beta_occ_4_sm | +1.2000 | +0.0752 | 1.1248 | n/a | False | False |
| beta_occ_2_sf | -1.2000 | -1.1722 | 0.0278 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.1763 | 0.0237 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.1760 | 0.0240 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.1731 | 0.0269 | n/a | False | True |
| beta_occ_3_cm | -1.2000 | -1.1717 | 0.0283 | n/a | False | True |
| beta_occ_4_cm | +1.2000 | +1.1780 | 0.0220 | n/a | False | True |
| beta_occ_2_cf | -1.2000 | -1.1786 | 0.0214 | n/a | False | True |
| beta_occ_3_cf | +1.2000 | +1.1767 | 0.0233 | n/a | False | True |
| beta_occ_4_cf | -1.2000 | -1.1760 | 0.0240 | n/a | False | True |
| beta_w0 | +2.5000 | +2.2904 | 0.2096 | n/a | False | False |
| beta_w_educL | -0.0750 | +0.1186 | 0.1936 | n/a | True | False |
| beta_w_educH | +0.2500 | +0.3032 | 0.0532 | n/a | False | False |
| beta_w_pexp | +0.0150 | +0.2002 | 0.1852 | n/a | False | False |
| beta_w_pexp2 | -0.0004 | -0.0305 | 0.0301 | n/a | False | False |
| sigma | +0.3750 | +0.3784 | 0.0034 | n/a | False | False |
| beta_ll | +2.5000 | +3.1563 | 0.6563 | n/a | False | True |