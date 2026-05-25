# RURO ruro_occ_M0 — Proposal-Adequacy Diagnostic v1

Date: 2026-05-13

## Verdict

**FLAG.** R_BC_C at M0 thetas: singles_male=0.133, singles_female=1.338, couples_household=6.708. Non-work median share lowest at 0.100; working-only rank-corr(C, L) lowest at -0.606. FLAG: R_BC_C at M0 theta lowest = 0.133 in marginal band [0.1, 0.3]. M0a is worth running, but plan to re-evaluate R_BC_C at the M0a converged theta. If R_BC_C drops further after pooling, draws-side widening may also be needed.

Thresholds (per the prompt):

- `R_BC_C(theta) >= 0.3` → identifiable; `< 0.1` → FAIL; `[0.1, 0.3]` → marginal.
- Median per-hh non-work share `< 5%` flags thin non-employment mass.
- Median rank-corr(C, L) over working alts `<= -0.85` flags consumption/leisure collinearity within choice sets.

Unweighted statistics throughout; EUROMOD household weight `dwt` is intentionally not applied (diagnostic, not population estimate).

## Input files

| dataset | path | size (B) | mtime | n_rows | n_columns | n_households |
| --- | --- | --- | --- | --- | --- | --- |
| singles | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet` | 21,500,551 | 2026-05-13T10:38:21.929304 | 167,600 | 75 | 1,676 |
| couples | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet` | 43,108,822 | 2026-05-13T10:38:22.968306 | 257,700 | 93 | 2,577 |

## Column resolution

| dataset | role | column used |
| --- | --- | --- |
| singles | hh_col | `idhh` |
| singles | chosen_col | `is_chosen` |
| singles | gender_col | `dgn` |
| singles | consumption_col | `consumption` |
| singles | leisure_col | `leisure` |
| singles | working_col | `working` |
| singles | hours_col | `hours` |
| singles | log_q_E_col | `log_q_E` |
| couples | hh_col | `idhh` |
| couples | chosen_col | `is_chosen` |
| couples | consumption_col | `consumption` |
| couples | leisure_male_col | `leisure_male` |
| couples | leisure_female_col | `leisure_female` |
| couples | working_male_col | `working_male` |
| couples | working_female_col | `working_female` |
| couples | hours_male_col | `hours_male` |
| couples | hours_female_col | `hours_female` |
| couples | log_q_E_male_col | `log_q_E_male` |
| couples | log_q_E_female_col | `log_q_E_female` |

Note: couples `consumption` is a household-level aggregate; both `couples_male` and `couples_female` views see the same C column. To avoid duplicated rows in D1a / D1b, couples C is reported once under `couples (household)`.

## D1 — Consumption and leisure variation

### D1a Raw consumption — within-hh std quantiles per group

| group | q10 | q25 | q50 | q75 | q90 | between_hh_std | R_C_raw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 5270.0638 | 5541.9270 | 5805.5208 | 6118.2610 | 6383.4210 | 887.9977 | 6.5378 |
| singles_female | 5294.3890 | 5569.9301 | 5840.8037 | 6112.5177 | 6357.2462 | 1665.0932 | 3.5078 |
| couples (household) | 7583.6330 | 7931.7647 | 8339.8595 | 8727.0347 | 9121.7730 | 1244.7280 | 6.7001 |

### D1b BIS — R_BC_C evaluated AT the M0 estimated thetas (verdict-relevant)

R_BC_C at the grid corner thetas can dip near zero for purely numerical reasons (e.g. Box-Cox compression near theta=-1 on large C). The verdict-relevant question is whether identification holds at the theta the estimator actually picked. M0 estimates: theta_c_sm = -0.856, theta_c_sf = -1.088, couples theta_c = +0.215.

| group | M0 theta | within_std q25 | q50 | q75 | between_std | R_BC_C |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | -0.8560 | 0.0010 | 0.0012 | 0.0015 | 0.0092 | 0.1329 |
| singles_female | -1.0884 | 0.0001 | 0.0002 | 0.0002 | 0.0001 | 1.3383 |
| couples (household) | +0.2153 | 4.7783 | 5.0709 | 5.3662 | 0.7559 | 6.7079 |

### D1b Box-Cox consumption — R_BC_C by anchor grid

| group | theta | within_std q25 | q50 | q75 | between_std | R_BC_C |
| --- | --- | --- | --- | --- | --- | --- |
| singles_male | -1.000 | 0.0003 | 0.0004 | 0.0005 | 0.0078 | 0.0530 |
| singles_male | -0.500 | 0.0160 | 0.0187 | 0.0213 | 0.0160 | 1.1681 |
| singles_male | +0.000 | 0.9403 | 1.0175 | 1.0874 | 0.1795 | 5.6683 |
| singles_male | +0.215 | 5.7356 | 6.0783 | 6.4241 | 0.9877 | 6.1540 |
| singles_male | +0.500 | 66.4072 | 69.5113 | 72.5027 | 10.8728 | 6.3932 |
| singles_female | -1.000 | 0.0003 | 0.0004 | 0.0004 | 0.0002 | 1.7784 |
| singles_female | -0.500 | 0.0142 | 0.0170 | 0.0197 | 0.0037 | 4.5407 |
| singles_female | +0.000 | 0.8944 | 0.9686 | 1.0506 | 0.1843 | 5.2553 |
| singles_female | +0.215 | 5.5928 | 5.9327 | 6.2668 | 1.1452 | 5.1806 |
| singles_female | +0.500 | 65.8412 | 68.6225 | 71.5417 | 14.5576 | 4.7139 |
| couples (household) | -1.000 | 0.0001 | 0.0001 | 0.0001 | 0.0000 | 6.5097 |
| couples (household) | -0.500 | 0.0073 | 0.0084 | 0.0095 | 0.0013 | 6.6769 |
| couples (household) | +0.000 | 0.6560 | 0.7103 | 0.7609 | 0.1055 | 6.7312 |
| couples (household) | +0.215 | 4.7650 | 5.0568 | 5.3513 | 0.7538 | 6.7080 |
| couples (household) | +0.500 | 68.2584 | 71.6572 | 74.9003 | 10.6968 | 6.6989 |

### D1c Leisure — raw within-hh std + Box-Cox R_BC_L by theta

| group | scope | theta or 'raw' | within_std q25 | q50 | q75 | between_std | R_BC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | raw | — | 20.3155 | 20.9644 | 21.6091 | 2.0118 | 10.4208 |
| singles_male | BC | -1.000 | 0.0176 | 0.0191 | 0.0204 | 0.0019 | 10.1826 |
| singles_male | BC | -0.700 | 0.0473 | 0.0507 | 0.0535 | 0.0049 | 10.2633 |
| singles_male | BC | -0.500 | 0.0927 | 0.0987 | 0.1037 | 0.0096 | 10.2959 |
| singles_male | BC | +0.000 | 0.5236 | 0.5488 | 0.5707 | 0.0529 | 10.3653 |
| singles_female | raw | — | 20.1912 | 20.8461 | 21.5040 | 2.1248 | 9.8107 |
| singles_female | BC | -1.000 | 0.0175 | 0.0188 | 0.0201 | 0.0019 | 9.9284 |
| singles_female | BC | -0.700 | 0.0468 | 0.0499 | 0.0530 | 0.0050 | 9.9072 |
| singles_female | BC | -0.500 | 0.0919 | 0.0973 | 0.1027 | 0.0098 | 9.8931 |
| singles_female | BC | +0.000 | 0.5194 | 0.5429 | 0.5663 | 0.0551 | 9.8553 |
| couples_male | raw | — | 20.2582 | 20.9068 | 21.5349 | 2.1162 | 9.8795 |
| couples_male | BC | -1.000 | 0.0176 | 0.0190 | 0.0202 | 0.0019 | 10.0204 |
| couples_male | BC | -0.700 | 0.0473 | 0.0504 | 0.0532 | 0.0050 | 10.0017 |
| couples_male | BC | -0.500 | 0.0927 | 0.0981 | 0.1031 | 0.0098 | 9.9885 |
| couples_male | BC | +0.000 | 0.5236 | 0.5470 | 0.5679 | 0.0550 | 9.9519 |
| couples_female | raw | — | 20.2084 | 20.8773 | 21.4812 | 2.0867 | 10.0051 |
| couples_female | BC | -1.000 | 0.0175 | 0.0189 | 0.0202 | 0.0019 | 9.9579 |
| couples_female | BC | -0.700 | 0.0469 | 0.0500 | 0.0532 | 0.0050 | 9.9598 |
| couples_female | BC | -0.500 | 0.0920 | 0.0975 | 0.1031 | 0.0098 | 9.9668 |
| couples_female | BC | +0.000 | 0.5197 | 0.5439 | 0.5679 | 0.0545 | 9.9793 |

### D1d Rank correlation between C and L, per household

Reported two ways: over all 100 alts (includes non-work cluster) and over working alts only (the operationally relevant slice for the consumption/leisure separability question).

| group | scope | n_hh | median | q10 | q90 |
| --- | --- | --- | --- | --- | --- |
| singles_male | all 100 alts | 766 | -0.7062 | -0.7767 | -0.6304 |
| singles_male | working alts only | 766 | -0.6025 | -0.6800 | -0.5091 |
| singles_female | all 100 alts | 910 | -0.7127 | -0.7835 | -0.6273 |
| singles_female | working alts only | 910 | -0.6061 | -0.6944 | -0.5009 |
| couples_male | all 100 alts | 2,577 | -0.4757 | -0.5754 | -0.3594 |
| couples_male | working alts only | 2,577 | -0.4192 | -0.5276 | -0.2871 |
| couples_female | all 100 alts | 2,577 | -0.4760 | -0.5771 | -0.3667 |
| couples_female | working alts only | 2,577 | -0.4177 | -0.5330 | -0.2976 |

## D2 — Non-employment mass

### D2a Share of non-work alternatives per household

| group | q10 | q25 | q50 | q75 | q90 | pct hh share < 5% | pct < 10% | pct == 0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| singles_male | 0.0700 | 0.0800 | 0.1000 | 0.1200 | 0.1400 | 0.0170 | 0.4530 | 0.0000 |
| singles_female | 0.0600 | 0.0800 | 0.1000 | 0.1200 | 0.1400 | 0.0187 | 0.4473 | 0.0000 |
| couples_male | 0.0600 | 0.0800 | 0.1000 | 0.1200 | 0.1400 | 0.0167 | 0.4334 | 0.0000 |
| couples_female | 0.0600 | 0.0800 | 0.1000 | 0.1200 | 0.1400 | 0.0241 | 0.4579 | 0.0000 |

### D2b Observed (chosen) non-employment vs proposal median

| group | obs nonwork rate | proposal median share | gap (obs - proposal) |
| --- | --- | --- | --- |
| singles_male | 0.0705 | 0.1000 | -0.0295 |
| singles_female | 0.0604 | 0.1000 | -0.0396 |
| couples_male | 0.0283 | 0.1000 | -0.0717 |
| couples_female | 0.0349 | 0.1000 | -0.0651 |

### D2c Mean log_q_E on working vs non-work

| group | log_q_E column | mean (working) | mean (non-work) | diff |
| --- | --- | --- | --- | --- |
| singles_male | `log_q_E` | -0.1054 | -2.3026 | 2.1972 |
| singles_female | `log_q_E` | -0.1054 | -2.3026 | 2.1972 |
| couples_male | `log_q_E_male` | -0.1054 | -2.3026 | 2.1972 |
| couples_female | `log_q_E_female` | -0.1054 | -2.3026 | 2.1972 |

## Diagnostic summary

R_BC_C at M0 thetas: singles_male=0.133, singles_female=1.338, couples_household=6.708. Non-work median share lowest at 0.100; working-only rank-corr(C, L) lowest at -0.606. FLAG: R_BC_C at M0 theta lowest = 0.133 in marginal band [0.1, 0.3]. M0a is worth running, but plan to re-evaluate R_BC_C at the M0a converged theta. If R_BC_C drops further after pooling, draws-side widening may also be needed.

## Files produced

| file | purpose |
| --- | --- |
| `Results/_proposal_adequacy_diag_ruro_occ_M0.py` | reusable script |
| `Results/_proposal_adequacy_diag_ruro_occ_M0.json` | machine-readable results |
| `Results/P3a/single_year_baseline/M0/RURO_ruro_occ_M0_proposal_adequacy_diag_v1.md` | this report |
