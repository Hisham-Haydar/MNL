# RURO Recovery Test Results — bpool_p3a_v1 (55 params)

**mode:** couples  **years:** 2016  **n_hh:** 999999  **solver:** gamspy-conopt  **seed:** 20260527

theta* generated generically from spec (initial+bounds), no param names hardcoded; synthetic choice drawn (vectorized) from theta* on the REAL alternatives.


## Starts
| start | success | LL | nit | sec |
|---|---|---|---|---|
| warm | True | -10862.011 | 12 | 21484.7 |
| cold | True | -10862.011 | 15 | 21214.8 |

**G2** max|warm−cold| (testable) = 4.150e-09

## G3 Conditioning
- PD: **False**
- cond: **inf**
- min eig: **-2.146e+02**, max: 1.654e+05

## G3b market-opportunity collinearity (generic)
- worst |corr| = **nan** (None)
- **Verdict: market-opp access shifters SEPARATELY IDENTIFIED**


_Inert on this slice (excluded from G1): ['beta_E_y2015', 'beta_E_y2017', 'beta_l0_sf', 'beta_l0_sm', 'beta_l_age2_sf', 'beta_l_age2_sm', 'beta_l_age_sf', 'beta_l_age_sm', 'beta_l_nkids_sf', 'beta_occ_2_sf', 'beta_occ_2_sm', 'beta_occ_3_sf', 'beta_occ_3_sm', 'beta_occ_4_sf', 'beta_occ_4_sm', 'theta_c_singles', 'theta_l_sf', 'theta_l_sm']_


## G1 / G4 per-param recovery

| param | theta* | theta_hat | abs_err | err/se | wrong_sign | inert |
|---|---|---|---|---|---|---|
| beta_l0_sm | +1.2500 | +1.2500 | 0.0000 | n/a | False | True |
| beta_l_age_sm | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_sm | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| theta_l_sm | -0.7500 | -0.7500 | 0.0000 | n/a | False | True |
| beta_l0_sf | +1.2500 | +1.2500 | 0.0000 | n/a | False | True |
| beta_l_age_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_l_age2_sf | +0.1200 | +0.1200 | 0.0000 | n/a | False | True |
| beta_l_nkids_sf | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| theta_l_sf | -1.2500 | -1.2500 | 0.0000 | n/a | False | True |
| theta_c_singles | -0.7500 | -0.7500 | 0.0000 | n/a | False | True |
| beta_l0_m | +0.0125 | +0.5553 | 0.5428 | n/a | False | False |
| beta_l_age_m | -0.6000 | -0.4757 | 0.1243 | n/a | False | False |
| beta_l_age2_m | +0.1200 | +0.1625 | 0.0425 | n/a | False | False |
| theta_l_m | -0.7500 | -0.5258 | 0.2242 | n/a | False | False |
| beta_l0_f | +1.2500 | +1.1860 | 0.0640 | n/a | False | False |
| beta_l_age_f | -0.6000 | -0.2629 | 0.3371 | n/a | False | False |
| beta_l_age2_f | +0.1200 | +0.0468 | 0.0732 | n/a | False | False |
| beta_l_nkids_f | -0.6000 | -0.1666 | 0.4334 | n/a | False | False |
| theta_l_f | -1.2500 | -0.8491 | 0.4009 | n/a | False | False |
| beta_E | -3.0000 | -3.2922 | 0.2922 | n/a | False | False |
| beta_h_pt1 | +1.2000 | +1.2717 | 0.0717 | n/a | False | False |
| beta_h_pt2 | -1.2000 | -0.8287 | 0.3713 | n/a | False | False |
| beta_h_ft | +1.2000 | +1.3132 | 0.1132 | n/a | False | False |
| beta_h_lh | -1.2000 | -1.0580 | 0.1420 | n/a | False | False |
| beta_E_gsur | +1.2000 | +1.3696 | 0.1696 | n/a | False | False |
| beta_E_drgn2 | -1.2000 | -1.1068 | 0.0932 | n/a | False | False |
| beta_E_drgn3 | +1.2000 | +1.0639 | 0.1361 | n/a | False | False |
| beta_E_drgn4 | -1.2000 | -1.3946 | 0.1946 | n/a | False | False |
| beta_E_drgn5 | +1.2000 | +0.9021 | 0.2979 | n/a | False | False |
| beta_E_drgn6 | -1.2000 | -1.3334 | 0.1334 | n/a | False | False |
| beta_E_drgn7 | +1.2000 | +1.6133 | 0.4133 | n/a | False | False |
| beta_E_drgn8 | -1.2000 | -0.9932 | 0.2068 | n/a | False | False |
| beta_E_y2015 | +0.6000 | +0.6000 | 0.0000 | n/a | False | True |
| beta_E_y2017 | -0.6000 | -0.6000 | 0.0000 | n/a | False | True |
| beta_E_drgur | +1.2000 | +1.5798 | 0.3798 | n/a | False | False |
| beta_E_drgmd | -1.2000 | -0.9849 | 0.2151 | n/a | False | False |
| beta_occ_2_sm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_sm | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_sm | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_sf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_3_sf | +1.2000 | +1.2000 | 0.0000 | n/a | False | True |
| beta_occ_4_sf | -1.2000 | -1.2000 | 0.0000 | n/a | False | True |
| beta_occ_2_cm | +1.2000 | +1.2696 | 0.0696 | n/a | False | False |
| beta_occ_3_cm | -1.2000 | -1.2155 | 0.0155 | n/a | False | False |
| beta_occ_4_cm | +1.2000 | +1.2397 | 0.0397 | n/a | False | False |
| beta_occ_2_cf | -1.2000 | -1.1445 | 0.0555 | n/a | False | False |
| beta_occ_3_cf | +1.2000 | +1.3137 | 0.1137 | n/a | False | False |
| beta_occ_4_cf | -1.2000 | -1.1237 | 0.0763 | n/a | False | False |
| beta_w0 | +2.5000 | +2.5253 | 0.0253 | n/a | False | False |
| beta_w_educL | -0.0750 | -0.0782 | 0.0032 | n/a | False | False |
| beta_w_educH | +0.2500 | +0.2492 | 0.0008 | n/a | False | False |
| beta_w_pexp | +0.0150 | -0.0304 | 0.0454 | n/a | True | False |
| beta_w_pexp2 | -0.0004 | +0.0197 | 0.0201 | n/a | False | False |
| sigma | +0.3750 | +0.3833 | 0.0083 | n/a | False | False |
| beta_ll | +2.5000 | +0.9851 | 1.5149 | n/a | False | False |