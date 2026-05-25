# RURO Data Audit v1

**Date:** 2026-05-24

## Paths

- Singles pre-drop dump: `U:\EUROMOD-STORAGE\Data\processed\fr\2016\predrop_explore\predrop_full__singles.parquet`
- Couples pre-drop dump: `U:\EUROMOD-STORAGE\Data\processed\fr\2016\predrop_explore\predrop_full__couples.parquet`

## Spec-Contract Focal Bins (§5 of RURO_model_spec_contract_v1.md)

- PT1: h ∈ (18.5, 21.5)  (20-hour peak)
- PT2: h ∈ (29.5, 30.5)  (30-hour peak)
- FT:  h ∈ (37.5, 40.5)  (38-40 hour peak)

---

## Coverage Summary

### Singles

- Total columns (unfiltered frame): **961**, rows: **167,600**
- Kept by whitelist: **75**
- EUROMOD counterfactual `_em` columns: **339** (kept: **1**, dropped decomposition: **338**)
- Other dropped (EUROMOD inputs, pipeline intermediates): **548**
- Promotable (dropped_other, usable, non-constant): **716**

> **EUROMOD `_em` columns** are the tax-benefit calculations run on every draw alternative. Only `ils_dispy_em` (→ `consumption`) enters the estimation whitelist. The other `_em` columns are the accounting decomposition (earnings, taxes, benefits, social contributions); they are kept in the pre-drop dump for welfare analysis but dropped from the estimation parquet.

### Couples

- Total columns (unfiltered frame): **1466**, rows: **257,700**
- Kept by whitelist: **93**
- EUROMOD counterfactual `_em` columns: **161** (kept: **0**, dropped decomposition: **161**)
- Other dropped (EUROMOD inputs, pipeline intermediates): **1212**
- Promotable (dropped_other, usable, non-constant): **1097**

> **EUROMOD `_em` columns** are the tax-benefit calculations run on every draw alternative. Only `ils_dispy_em` (→ `consumption`) enters the estimation whitelist. The other `_em` columns are the accounting decomposition (earnings, taxes, benefits, social contributions); they are kept in the pre-drop dump for welfare analysis but dropped from the estimation parquet.

---

## Choice-Space and Full Group Blocks

## singles: pre-drop exploration

- Total columns in full frame: **961**, rows: **167,600**
- Kept by whitelist: **75**  |  Dropped: **886**
- Dropped variables that are usable (<= 20% missing, non-constant): **716** (promotion candidates)

### Choice space — singles (chosen alternatives, n=1,676)

- Employment rate (h>0): **0.935**
- Mass at h=0: **0.065**
- In PT1 (18.5, 21.5): 0.027   |   PT2 (29.5, 30.5): 0.021   |   FT (37.5, 40.5): 0.229
- Hours | working, quantiles [p10,p25,p50,p75,p90]: [27.0, 35.0, 37.0, 40.0, 50.0]
- Hours histogram (working): 0-10:0.0, 10-15:0.015, 15-18.5:0.022, PT1:0.029, 21.5-25:0.015, 25-29.5:0.042, PT2:0.023, 30.5-35:0.036, 35-37.5:0.338, FT:0.244, 40.5-45:0.06, 45+:0.175
  > **FLAG: Empirical peak bin is '35-37.5', not in contract focal bins {PT1, PT2, FT}. Report this mismatch; do NOT silently change the bins.**
- Hourly wage | working, quantiles [p10,p25,p50,p75,p90]: [8.82, 11.25, 14.0, 17.91, 23.91]

### EUROMOD counterfactual output columns — singles

Total `_em` columns: **339**  |  Kept in whitelist: **1**  |  Dropped (decomposition): **338**

> All `_em` columns are EUROMOD's tax-benefit calculations on each draw alternative (counterfactual). Only `ils_dispy_em` enters the estimation whitelist — it becomes `consumption` after normalisation. The remaining 338 columns are the accounting decomposition (earnings, taxes, benefits, social contributions) which sum back to `ils_dispy_em` via the identity below. They are dropped for estimation but available for welfare decomposition analysis.

**Accounting identity** (chosen rows):

```
ils_dispy_em = ils_origy_em + ils_ben_em - ils_sicdy_em - ils_tax_em
Max absolute residual: 0.00000000  ✓ holds
```

**Key columns (named):**

| Column | Status | Mean (chosen) | Label |
|---|---|---|---|
| `ils_dispy_em` | **KEPT** | 2160.1 | Disposable income (EUROMOD counterfactual) → consumption in model |
| `ils_origy_em` | dropped | 2634.2 | Original income (pre-tax+benefit, counterfactual) |
| `ils_earns_em` | dropped | 2421.9 | Gross earnings (counterfactual) |
| `ils_ben_em` | dropped | 251.2 | Total benefits (counterfactual) |
| `ils_bennt_em` | dropped | 116.1 | Non-means-tested benefits (counterfactual) |
| `ils_benmt_em` | dropped | 135.1 | Means-tested benefits (counterfactual) |
| `ils_tax_em` | dropped | 373.9 | Total taxes (counterfactual) |
| `ils_taxin_em` | dropped | 373.9 | Income tax (counterfactual) |
| `ils_taxwl_em` | dropped | 0.0 | Wealth/other tax (counterfactual) |
| `ils_sicdy_em` | dropped | 351.3 | Employee social insurance contributions (counterfactual) |
| `ils_sicee_em` | dropped | 333.8 | Employer social insurance contributions (counterfactual) |
| `ils_sicot_em` | dropped | 0.0 | Other social insurance (counterfactual) |
| `ils_b1_bun_em` | dropped | 93.6 | Unemployment benefit (counterfactual) |
| `ils_b1_bfa_em` | dropped | 40.5 | Family/child benefit (counterfactual) |
| `ils_b1_bsa_em` | dropped | 63.0 | Social assistance (counterfactual) |
| `ils_b1_bho_em` | dropped | 51.8 | Housing benefit (counterfactual) |
| `ils_b1_bhl_em` | dropped | 1.2 | Health/sickness benefit (counterfactual) |
| `ils_b1_bdi_em` | dropped | 0.3 | Disability benefit (counterfactual) |
| `ils_b1_bed_em` | dropped | 0.7 | Education benefit (counterfactual) |
| `ils_b2_bfaed_em` | dropped | 41.3 | Family+education aggregate (counterfactual) |
| `ils_b2_bsaho_em` | dropped | 114.8 | Social assistance+housing aggregate (counterfactual) |
| `ils_b2_bunwk_em` | dropped | 93.6 | Unemployment+in-work aggregate (counterfactual) |

<details><summary>All _em columns (click to expand)</summary>

| Column | Status | Mean | Std | Min | Max |
|---|---|---|---|---|---|
| `aca_em` | dropped | 1.3 | 0.7 | 1.0 | 3.0 |
| `aco_em` | dropped | 1.3 | 0.6 | 1.0 | 3.0 |
| `afc_em` | dropped | 137824.3 | 1427294.2 | 0.0 | 51374820.0 |
| `amrrm_em` | dropped | 3.2 | 1.3 | 1.0 | 6.0 |
| `amrtn_em` | dropped | 2.8 | 1.3 | 1.0 | 6.0 |
| `ate_em` | dropped | 1.0 | 0.2 | 1.0 | 3.0 |
| `bch00_em` | dropped | 21.0 | 72.3 | 0.0 | 759.6 |
| `bch00_s_em` | dropped | 22.7 | 72.1 | 0.0 | 694.6 |
| `bchba_s_em` | dropped | 0.3 | 5.0 | 0.0 | 77.3 |
| `bchcc_em` | dropped | 0.1 | 4.3 | 0.0 | 166.4 |
| `bchcc_s_em` | dropped | 1.1 | 16.8 | 0.0 | 392.5 |
| `bched_em` | dropped | 8.0 | 20.4 | 0.0 | 158.0 |
| `bched_s_em` | dropped | 8.4 | 20.1 | 0.0 | 158.0 |
| `bchlg_em` | dropped | 3.2 | 22.8 | 0.0 | 169.2 |
| `bchlg_s_em` | dropped | 3.5 | 26.1 | 0.0 | 203.1 |
| `bchor_s_em` | dropped | 1.0 | 13.8 | 0.0 | 301.7 |
| `bchot_em` | dropped | 20.0 | 73.4 | 0.0 | 1063.7 |
| `bchot_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bchyc_em` | dropped | 3.0 | 23.4 | 0.0 | 262.8 |
| `bchyc_s_em` | dropped | 3.5 | 25.1 | 0.0 | 185.5 |
| `bdi_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bdi_s_em` | dropped | 0.3 | 10.7 | 0.0 | 437.9 |
| `bed_em` | dropped | 0.7 | 10.8 | 0.0 | 272.2 |
| `bfa_em` | dropped | 55.3 | 161.9 | 0.0 | 1547.8 |
| `bhl_em` | dropped | 1.2 | 17.9 | 0.0 | 416.7 |
| `bho_em` | dropped | 68.6 | 119.7 | 0.0 | 556.7 |
| `bhoot_em` | dropped | 4.2 | 27.1 | 0.0 | 342.1 |
| `bhotn_em` | dropped | 64.4 | 118.9 | 0.0 | 556.7 |
| `bhotn_s_em` | dropped | 47.6 | 104.6 | 0.0 | 612.4 |
| `bmact_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bpact_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsa00_em` | dropped | 38.4 | 119.9 | 0.0 | 1040.3 |
| `bsa00_s_em` | dropped | 51.8 | 126.2 | 0.0 | 844.0 |
| `bsa_em` | dropped | 18.4 | 95.9 | 0.0 | 1040.3 |
| `bsaoa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsaoa_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsaot_em` | dropped | 4.5 | 33.5 | 0.0 | 666.7 |
| `bsuwd_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsuwd_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bun_em` | dropped | 23.9 | 178.0 | 0.0 | 3367.5 |
| `bunct_em` | dropped | 81.9 | 284.1 | 0.0 | 4310.0 |
| `bunct_s_em` | dropped | 90.1 | 297.9 | 0.0 | 4280.0 |
| `bunctmy_s_em` | dropped | 1.0 | 2.9 | 0.0 | 12.0 |
| `bunmt_em` | dropped | 7.1 | 44.6 | 0.0 | 481.7 |
| `bunmt_s_em` | dropped | 3.5 | 36.5 | 0.0 | 507.0 |
| `bunmy_em` | dropped | 1.2 | 3.2 | 0.0 | 12.0 |
| `dag_em` | dropped | 43.6 | 11.0 | 18.0 | 65.0 |
| `dct_em` | dropped | 5.0 | 0.0 | 5.0 | 5.0 |
| `dcu_em` | dropped | 0.0 | 0.2 | 0.0 | 1.0 |
| `dcz_em` | dropped | 1.1 | 0.3 | 1.0 | 3.0 |
| `ddi_em` | dropped | 0.0 | 0.0 | 0.0 | 1.0 |
| `ddilv_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ddt_em` | dropped | 22033.9 | 422.8 | 22016.0 | 32016.0 |
| `dec_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `deh_em` | dropped | 3.6 | 1.3 | 0.0 | 5.0 |
| `dehde_em` | dropped | 380.2 | 124.9 | 0.0 | 500.0 |
| `dew_em` | dropped | 1936.2 | 333.0 | -1.0 | 2016.0 |
| `dey_em` | dropped | 14.0 | 4.3 | 0.0 | 18.0 |
| `dgn_em` | dropped | 0.5 | 0.5 | 0.0 | 1.0 |
| `dmb_em` | dropped | 6.4 | 3.3 | 2.0 | 11.0 |
| `dms_em` | dropped | 1.9 | 1.4 | 1.0 | 5.0 |
| `dncsy_em` | dropped | 0.0 | 0.0 | 0.0 | 1.0 |
| `drg01_em` | dropped | 2.1 | 0.6 | 1.0 | 3.0 |
| `drgmd_em` | dropped | 0.2 | 0.4 | 0.0 | 1.0 |
| `drgn1_em` | dropped | 4.3 | 2.3 | 1.0 | 8.0 |
| `drgn2_em` | dropped | 10.7 | 6.6 | 1.0 | 22.0 |
| `drgru_em` | dropped | 0.3 | 0.4 | 0.0 | 1.0 |
| `drgur_em` | dropped | 0.5 | 0.5 | 0.0 | 1.0 |
| `dsu00_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `dsu01_em` | dropped | 434.9 | 263.5 | 1.0 | 893.0 |
| `dsu02_em` | dropped | 315.9 | 201.2 | 0.0 | 637.0 |
| `dwt_em` | dropped | 2904.1 | 2248.9 | 529.3 | 41902.6 |
| `hours_em` | dropped | 35.2 | 13.0 | 0.0 | 70.0 |
| `i_bch_inclt1_em` | dropped | 86.4 | 617.5 | 0.0 | 6674.0 |
| `i_bch_inclt2_em` | dropped | 46.4 | 405.2 | 0.0 | 4514.6 |
| `i_bchcc_amt_em` | dropped | 23.0 | 78.9 | 0.0 | 392.5 |
| `i_bched_amt_em` | dropped | 10.0 | 21.1 | 0.0 | 158.0 |
| `i_bched_inclt_em` | dropped | 595.6 | 1023.0 | 0.0 | 3895.2 |
| `i_bchlg_inclt1_em` | dropped | 99.4 | 621.8 | 0.0 | 4871.6 |
| `i_bchlg_inclt2_em` | dropped | 49.7 | 310.9 | 0.0 | 2436.0 |
| `i_bchlg_nwa_em` | dropped | 0.2 | 0.4 | 0.0 | 1.0 |
| `i_bdi_inclt_em` | dropped | 965.0 | 316.2 | 800.4 | 2801.6 |
| `i_bho_c_em` | dropped | 58.3 | 9.6 | 53.2 | 113.5 |
| `i_bho_l_em` | dropped | 158.5 | 148.3 | 0.0 | 555.7 |
| `i_bho_l_lt_em` | dropped | 290.6 | 61.9 | 239.0 | 630.3 |
| `i_bho_minrate_em` | dropped | 0.2 | 0.2 | 0.0 | 0.4 |
| `i_bho_p0_em` | dropped | 35.2 | 1.9 | 34.7 | 56.9 |
| `i_bho_pp_em` | dropped | 281.5 | 367.5 | 34.7 | 4722.5 |
| `i_bho_r0_em` | dropped | 453.0 | 122.8 | 378.7 | 737.5 |
| `i_bho_rate_em` | dropped | 0.4 | 0.3 | 0.0 | 0.7 |
| `i_bho_rentbase_em` | dropped | 288.8 | 59.0 | 255.0 | 555.7 |
| `i_bho_rl_em` | dropped | 0.5 | 0.5 | 0.0 | 1.1 |
| `i_bho_tf_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_bho_tp_em` | dropped | 0.2 | 0.2 | 0.0 | 0.4 |
| `i_bsa00_amt_em` | dropped | 612.2 | 178.7 | 513.9 | 1759.7 |
| `i_bsa00_bonus_em` | dropped | 15.1 | 4.2 | 12.7 | 38.1 |
| `i_bsa00_ded_em` | dropped | 82.0 | 34.3 | 61.7 | 152.6 |
| `i_bsa00_faminc_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_bsa00_rand2_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_bsa00_rand_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_bsa00_wkinc_em` | dropped | 1970.5 | 1253.4 | 0.0 | 15207.5 |
| `i_bunmt_amt_em` | dropped | 6.0 | 50.2 | 0.0 | 494.3 |
| `i_bunmt_bonus_em` | dropped | 12.7 | 0.0 | 12.7 | 12.7 |
| `i_bunmt_inc_em` | dropped | 1758.5 | 1633.5 | 0.0 | 37463.9 |
| `i_imax_gt_all_em` | dropped | 210.3 | 548.9 | 0.0 | 15224.6 |
| `i_imax_gt_kt_em` | dropped | 165.7 | 271.8 | 0.0 | 4865.4 |
| `i_imax_nt_all_em` | dropped | 173.2 | 547.3 | 0.0 | 15224.6 |
| `i_imax_nt_kt_em` | dropped | 130.5 | 267.2 | 0.0 | 4865.4 |
| `i_loneparent_em` | dropped | 0.2 | 0.4 | 0.0 | 1.0 |
| `i_nDepRel_em` | dropped | 0.4 | 0.8 | 0.0 | 5.0 |
| `i_rngy_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_rngy_kt_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_scee_base_em` | dropped | 2371.3 | 1508.0 | 0.0 | 17380.0 |
| `i_takeup2_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_takeup_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_tingt1_em` | dropped | 173.5 | 484.2 | 0.0 | 13555.1 |
| `i_tingt2_em` | dropped | 161.2 | 550.6 | 0.0 | 15224.6 |
| `i_tingt_all_em` | dropped | 181.3 | 545.3 | 0.0 | 15224.6 |
| `i_tingt_kt_em` | dropped | 138.3 | 265.5 | 0.0 | 4865.4 |
| `i_tinqtdep_em` | dropped | 0.4 | 0.7 | 0.0 | 4.5 |
| `i_tinqtimax_em` | dropped | 1.0 | 0.0 | 1.0 | 1.0 |
| `i_tscerrd_coef_em` | dropped | 0.1 | 0.1 | 0.0 | 0.3 |
| `i_tscxc_bhl_em` | dropped | 0.1 | 1.1 | 0.0 | 25.8 |
| `i_tscxc_cap_em` | dropped | 15.9 | 139.5 | 0.0 | 4880.4 |
| `i_tscxc_earns_em` | dropped | 178.5 | 120.3 | 0.0 | 1429.5 |
| `i_tscxc_pen_em` | dropped | 0.0 | 0.9 | 0.0 | 35.7 |
| `i_tscxc_unemp_em` | dropped | 4.0 | 16.7 | 0.0 | 260.7 |
| `i_yempv_em` | dropped | 2050.0 | 1180.1 | 0.0 | 12484.0 |
| `idfather_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `idhh_em` | dropped | 3251243959.4 | 786268944.8 | 1495800000.0 | 4349000000.0 |
| `idhh_true_em` | dropped | 3251244.0 | 786268.9 | 1495800.0 | 4349000.0 |
| `idmother_em` | dropped | 234970167.7 | 9619438755.0 | 0.0 | 393810001000.0 |
| `idorighh_em` | dropped | 3251244.0 | 786268.9 | 1495800.0 | 4349000.0 |
| `idorigperson_em` | dropped | 325124334.5 | 78627000.4 | 149580001.0 | 434900001.0 |
| `idpartner_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `idperson_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `idperson_true_em` | dropped | 325124397.0 | 78626894.4 | 149580001.0 | 434900001.0 |
| `il_bsa00_em` | dropped | 2205.2 | 2163.1 | -2.8 | 59739.8 |
| `il_bunmt_em` | dropped | 1751.9 | 1635.8 | -626.0 | 37463.9 |
| `il_capy_em` | dropped | 193.7 | 1700.9 | 0.0 | 59517.5 |
| `il_crds_base_full_em` | dropped | 287.8 | 1705.9 | 0.0 | 59517.5 |
| `il_crds_base_red_em` | dropped | 2512.0 | 1617.8 | 0.0 | 19282.5 |
| `il_dpisilc_em` | dropped | 2293.2 | 1741.2 | 356.7 | 44803.6 |
| `il_rgby_em` | dropped | 1903.8 | 1666.3 | 0.0 | 37463.9 |
| `il_rngy_em` | dropped | 1842.5 | 1628.5 | -7.8 | 37463.9 |
| `il_rniy_bens_em` | dropped | 1842.0 | 1628.8 | -7.8 | 37463.9 |
| `il_rniy_em` | dropped | 1842.0 | 1628.8 | -7.8 | 37463.9 |
| `il_rniy_kt_em` | dropped | 1674.9 | 1208.5 | -19015.7 | 14443.5 |
| `il_temp_bun_em` | dropped | 93.6 | 299.0 | 0.0 | 4280.0 |
| `il_tscee_base_em` | dropped | 2371.3 | 1508.0 | 0.0 | 17380.0 |
| `il_tscxc_pen_em` | dropped | 0.6 | 22.9 | 0.0 | 939.2 |
| `ils_b1_bcb_em` | dropped | 4.9 | 35.5 | 0.0 | 516.6 |
| `ils_b1_bdi_em` | dropped | 0.3 | 10.7 | 0.0 | 437.9 |
| `ils_b1_bed_em` | dropped | 0.7 | 10.8 | 0.0 | 272.2 |
| `ils_b1_bfa_em` | dropped | 40.5 | 122.4 | 0.0 | 1062.9 |
| `ils_b1_bhl_em` | dropped | 1.2 | 17.9 | 0.0 | 416.7 |
| `ils_b1_bho_em` | dropped | 51.8 | 106.2 | 0.0 | 612.4 |
| `ils_b1_boa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b1_bsa_em` | dropped | 63.0 | 135.6 | 0.0 | 844.0 |
| `ils_b1_bsu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b1_bun_em` | dropped | 93.6 | 299.0 | 0.0 | 4280.0 |
| `ils_b1_bwk_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b2_bfaed_em` | dropped | 41.3 | 122.7 | 0.0 | 1062.9 |
| `ils_b2_bsaho_em` | dropped | 114.8 | 218.4 | 0.0 | 1282.9 |
| `ils_b2_bunwk_em` | dropped | 93.6 | 299.0 | 0.0 | 4280.0 |
| `ils_b2_penhl_em` | dropped | 1.5 | 20.8 | 0.0 | 437.9 |
| `ils_base_tin_em` | dropped | 2711.0 | 2581.1 | 0.0 | 67356.7 |
| `ils_base_tinto_em` | dropped | 2711.0 | 2581.1 | 0.0 | 67356.7 |
| `ils_base_tscdf_em` | dropped | 2799.8 | 2548.2 | 0.0 | 67356.7 |
| `ils_base_tscxc_em` | dropped | 2707.4 | 2584.0 | 0.0 | 67356.7 |
| `ils_ben_em` | dropped | 251.2 | 409.1 | 0.0 | 4280.0 |
| `ils_benmt_em` | dropped | 135.1 | 248.2 | 0.0 | 1498.8 |
| `ils_bennt_em` | dropped | 116.1 | 304.2 | 0.0 | 4280.0 |
| `ils_bensim_em` | dropped | 188.7 | 354.7 | 0.0 | 4280.0 |
| `ils_dispy_em` | **KEPT** | 2160.1 | 1541.1 | 512.9 | 41638.6 |
| `ils_earns_csg_em` | dropped | 2421.9 | 1631.3 | 0.0 | 19282.5 |
| `ils_earns_em` | dropped | 2421.9 | 1631.3 | 0.0 | 19282.5 |
| `ils_origrepy_em` | dropped | 2725.5 | 2569.3 | 0.0 | 67356.7 |
| `ils_origy_em` | dropped | 2634.2 | 2576.8 | -524.2 | 67356.7 |
| `ils_pen_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicct_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicdy_em` | dropped | 351.3 | 252.8 | 0.0 | 3822.6 |
| `ils_sicee_em` | dropped | 333.8 | 196.0 | 0.0 | 1610.7 |
| `ils_sicer_em` | dropped | 836.2 | 682.6 | 0.0 | 5878.3 |
| `ils_sicot_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicse_em` | dropped | 17.5 | 136.1 | 0.0 | 2646.1 |
| `ils_tax_em` | dropped | 373.9 | 810.2 | 0.0 | 23895.4 |
| `ils_taxin_em` | dropped | 373.9 | 810.2 | 0.0 | 23895.4 |
| `ils_taxsim_em` | dropped | 372.1 | 800.7 | 0.0 | 23895.4 |
| `ils_taxwl_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bdi_em` | dropped | 0.3 | 10.7 | 0.0 | 437.9 |
| `ils_udb_bed_em` | dropped | 0.7 | 10.8 | 0.0 | 272.2 |
| `ils_udb_bfa_em` | dropped | 40.5 | 122.4 | 0.0 | 1062.9 |
| `ils_udb_bhl_em` | dropped | 1.2 | 17.9 | 0.0 | 416.7 |
| `ils_udb_bho_em` | dropped | 51.8 | 106.2 | 0.0 | 612.4 |
| `ils_udb_boa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bsa_em` | dropped | 63.0 | 135.6 | 0.0 | 844.0 |
| `ils_udb_bsu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bun_em` | dropped | 93.6 | 299.0 | 0.0 | 4280.0 |
| `ils_udb_kfbcc_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_tis_em` | dropped | 723.4 | 975.2 | 0.0 | 25718.1 |
| `ils_udb_tpr_em` | dropped | 1.9 | 38.3 | 0.0 | 1250.0 |
| `ils_udb_xmp_em` | dropped | 22.1 | 100.6 | 0.0 | 1875.0 |
| `ils_udb_yds_em` | dropped | 2160.1 | 1541.1 | 512.9 | 41638.6 |
| `ils_udb_yem_em` | dropped | 2371.3 | 1508.0 | 0.0 | 17380.0 |
| `ils_udb_yiy_em` | dropped | 159.6 | 1653.3 | 0.0 | 59509.2 |
| `ils_udb_yot_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_ypp_em` | dropped | 0.6 | 22.9 | 0.0 | 939.2 |
| `ils_udb_ypr_em` | dropped | 34.0 | 288.4 | 0.0 | 6965.8 |
| `ils_udb_ypt_em` | dropped | 40.1 | 139.8 | 0.0 | 2000.0 |
| `ils_udb_yse_em` | dropped | 50.6 | 449.8 | 0.0 | 10249.2 |
| `kfb_em` | dropped | 25.5 | 73.3 | 0.0 | 1020.0 |
| `kfbcc_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `kfbmy_em` | dropped | 4.0 | 5.6 | 0.0 | 12.0 |
| `kivho_em` | dropped | 250.3 | 326.3 | 0.0 | 3115.0 |
| `lcs_em` | dropped | 0.1 | 0.3 | 0.0 | 1.0 |
| `les_em` | dropped | 3.3 | 0.9 | 2.0 | 9.0 |
| `lfs_em` | dropped | 27.5 | 21.0 | 0.0 | 50.0 |
| `lhw_em` | dropped | 35.2 | 13.0 | 0.0 | 70.0 |
| `lhw_f_em` | dropped | 1.4 | 1.0 | 1.0 | 4.0 |
| `lindi_em` | dropped | 6.5 | 3.5 | 0.0 | 12.0 |
| `liwftmy_em` | dropped | 8.6 | 5.1 | 0.0 | 12.0 |
| `liwmy_a_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `liwmy_em` | dropped | 10.2 | 3.9 | 0.0 | 12.0 |
| `liwmy_f_em` | dropped | 1.0 | 0.0 | 1.0 | 1.0 |
| `liwmy_s_em` | dropped | 2.3 | 7.1 | 0.0 | 36.0 |
| `liwptmy_em` | dropped | 1.6 | 3.9 | 0.0 | 12.0 |
| `liwwh_em` | dropped | 248.1 | 138.5 | 0.0 | 744.0 |
| `liwwh_f_em` | dropped | 1.1 | 0.4 | 1.0 | 4.0 |
| `lnu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `loc_em` | dropped | 4.6 | 2.5 | -1.0 | 9.0 |
| `loc_ruro_em` | dropped | 4.2 | 2.8 | -1.0 | 9.0 |
| `lowas_em` | dropped | 0.1 | 0.3 | 0.0 | 1.0 |
| `lpemy_em` | dropped | 0.0 | 0.1 | 0.0 | 6.0 |
| `lse_em` | dropped | 0.1 | 0.4 | 0.0 | 2.0 |
| `lse_s_em` | dropped | 0.0 | 0.2 | 0.0 | 1.0 |
| `lunmy_em` | dropped | 0.6 | 2.7 | 0.0 | 12.0 |
| `lunmy_f_em` | dropped | 1.0 | 0.0 | 1.0 | 1.0 |
| `lunmy_s_em` | dropped | 1.6 | 3.6 | 0.0 | 12.0 |
| `pdi00_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `pdi_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `pdimy_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `poa00_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `poa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `poamy_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `psu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `psumy_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tad_em` | dropped | 145.9 | 266.5 | -1624.2 | 3220.0 |
| `temp_convcoef_em` | dropped | 0.3 | 0.7 | 0.0 | 13.0 |
| `tin_s_em` | dropped | 146.4 | 486.1 | 0.0 | 13555.1 |
| `tingt_s_em` | dropped | 146.4 | 486.1 | 0.0 | 13555.1 |
| `tinqt_s_em` | dropped | 1.4 | 0.7 | 1.0 | 5.5 |
| `tinrf_s_em` | dropped | 6.7 | 18.5 | 0.0 | 98.4 |
| `tintace_s_em` | dropped | 221.9 | 123.1 | 0.0 | 1091.1 |
| `tintadb_s_em` | dropped | 0.5 | 8.9 | 0.0 | 195.3 |
| `tintadp_s_em` | dropped | 11.7 | 58.9 | 0.0 | 567.2 |
| `tintadt_s_em` | dropped | 63.9 | 661.3 | 0.0 | 23803.7 |
| `tintalm_s_em` | dropped | 184.3 | 311.8 | 0.0 | 1472.7 |
| `tintapv_s_em` | dropped | 27.5 | 87.3 | 0.0 | 689.8 |
| `tintart_s_em` | dropped | 5.0 | 27.3 | 0.0 | 374.0 |
| `tintcch_s_em` | dropped | 11.9 | 46.3 | 0.0 | 191.7 |
| `tintced_s_em` | dropped | 2.1 | 5.8 | 0.0 | 48.3 |
| `tintcee_s_em` | dropped | 6.7 | 18.5 | 0.0 | 98.4 |
| `tintcmi_s_em` | dropped | 9.0 | 30.8 | 0.0 | 283.8 |
| `tinto_s_em` | dropped | 0.3 | 12.2 | 0.0 | 498.9 |
| `tis_em` | dropped | 598.9 | 650.9 | -1065.2 | 12730.2 |
| `tmu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tscdf_s_em` | dropped | 13.8 | 12.6 | 0.0 | 336.1 |
| `tscee_s_em` | dropped | 333.8 | 196.0 | 0.0 | 1610.7 |
| `tsceepi00_s_em` | dropped | 150.8 | 66.0 | 0.0 | 269.3 |
| `tsceepi_s_em` | dropped | 259.0 | 149.1 | 0.0 | 1211.9 |
| `tsceepibc_s_em` | dropped | 51.8 | 58.6 | 0.0 | 611.8 |
| `tsceepicp_s_em` | dropped | 3.1 | 2.0 | 0.0 | 22.6 |
| `tsceepiwc_s_em` | dropped | 34.1 | 81.8 | 0.0 | 830.9 |
| `tsceesi_s_em` | dropped | 17.8 | 11.3 | 0.0 | 130.3 |
| `tsceeui_s_em` | dropped | 57.0 | 35.9 | 0.0 | 304.5 |
| `tscer_em` | dropped | 714.2 | 766.7 | 0.0 | 5863.3 |
| `tscer_s_em` | dropped | 836.6 | 682.8 | 0.0 | 5881.0 |
| `tscerap_s_em` | dropped | 16.1 | 10.3 | 0.0 | 118.2 |
| `tscerfa_s_em` | dropped | 87.0 | 72.9 | 0.0 | 912.4 |
| `tscerho_s_em` | dropped | 8.1 | 8.0 | 0.0 | 86.9 |
| `tscerir_s_em` | dropped | 35.7 | 31.4 | 0.0 | 356.3 |
| `tscerot_s_em` | dropped | 9.7 | 18.1 | 0.0 | 47.5 |
| `tscerpi_s_em` | dropped | 389.3 | 238.5 | 0.0 | 2066.0 |
| `tscerpicp_s_em` | dropped | 1.8 | 3.7 | 0.0 | 27.6 |
| `tscerrd_s_em` | dropped | 108.2 | 134.3 | 0.0 | 412.0 |
| `tscersi_s_em` | dropped | 303.5 | 193.0 | 0.0 | 2224.6 |
| `tsceruf_s_em` | dropped | 0.4 | 0.2 | 0.0 | 2.8 |
| `tscerui_s_em` | dropped | 95.0 | 59.7 | 0.0 | 507.2 |
| `tsckt_s_em` | dropped | 13.2 | 115.7 | 0.0 | 4047.2 |
| `tscse_s_em` | dropped | 17.5 | 136.1 | 0.0 | 2646.1 |
| `tscsedi_s_em` | dropped | 0.2 | 1.1 | 0.0 | 8.2 |
| `tscsefa_s_em` | dropped | 1.8 | 20.8 | 0.0 | 538.1 |
| `tscseir_s_em` | dropped | 0.2 | 1.3 | 0.0 | 7.9 |
| `tscsepi00_s_em` | dropped | 6.9 | 50.7 | 0.0 | 565.3 |
| `tscsepi_s_em` | dropped | 10.4 | 81.8 | 0.0 | 1353.9 |
| `tscsepicp_s_em` | dropped | 3.6 | 33.1 | 0.0 | 788.7 |
| `tscsesi_s_em` | dropped | 4.8 | 34.4 | 0.0 | 737.9 |
| `tscxc_s_em` | dropped | 198.4 | 202.8 | 0.0 | 5458.1 |
| `tscxcktrd_s_em` | dropped | 9.9 | 86.7 | 0.0 | 3035.4 |
| `tscxcnkrd_s_em` | dropped | 124.2 | 81.9 | 0.0 | 972.1 |
| `tu_bch_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `tu_bch_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_bchlg_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `tu_bchlg_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 1.0 |
| `tu_bho_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `tu_bho_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_bsa00_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `tu_bsa00_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_fiscalunit_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `tu_fiscalunit_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_household_fr_HeadID_em` | dropped | 325124397006.6 | 78626894442.8 | 149580001000.0 | 434900001000.0 |
| `twl_em` | dropped | 1.9 | 38.3 | 0.0 | 1250.0 |
| `wage_em` | dropped | 15.7 | 8.1 | 0.2 | 104.2 |
| `xhc_em` | dropped | 497.3 | 278.0 | 0.0 | 3548.7 |
| `xhcmomi_em` | dropped | 40.4 | 127.2 | 0.0 | 3430.4 |
| `xhcot_em` | dropped | 199.7 | 110.8 | 0.0 | 1146.4 |
| `xhcrt_em` | dropped | 257.2 | 274.1 | 0.0 | 2162.0 |
| `xmp_em` | dropped | 22.1 | 100.6 | 0.0 | 1875.0 |
| `xpp_em` | dropped | 15.3 | 87.2 | 0.0 | 1860.0 |
| `yds_em` | dropped | 2070.9 | 1874.1 | -128.3 | 54625.8 |
| `ydses_o_em` | dropped | 1857.3 | 1842.9 | -128.3 | 54625.8 |
| `yem00_em` | dropped | 2081.0 | 1198.0 | 0.0 | 12672.9 |
| `yem_em` | dropped | 2371.3 | 1508.0 | 0.0 | 17380.0 |
| `yemmy_em` | dropped | 11.3 | 2.8 | 0.0 | 12.0 |
| `yempv_a_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `yempv_em` | dropped | 271.4 | 957.1 | 0.0 | 22142.9 |
| `yempv_s_em` | dropped | 271.4 | 957.1 | 0.0 | 22142.9 |
| `yemxp_em` | dropped | 290.3 | 514.0 | 0.0 | 5368.1 |
| `yivwg_em` | dropped | 15.7 | 8.1 | 0.2 | 104.2 |
| `yiy_em` | dropped | 159.6 | 1653.3 | 0.0 | 59509.2 |
| `ymwdt_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `yot_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ypp_em` | dropped | 0.6 | 22.9 | 0.0 | 939.2 |
| `ypr_em` | dropped | 34.0 | 288.4 | 0.0 | 6965.8 |
| `ypt_em` | dropped | 40.1 | 139.8 | 0.0 | 2000.0 |
| `yptmp_em` | dropped | 25.3 | 116.5 | 0.0 | 2000.0 |
| `yse_em` | dropped | 50.6 | 449.8 | 0.0 | 10249.2 |
| `ysemy_em` | dropped | 0.3 | 1.6 | 0.0 | 12.0 |

</details>

#### Within-role correlation — preference candidates

|            |   age_norm |   age_norm2 |   educH |   educL |   n_children |
|:-----------|-----------:|------------:|--------:|--------:|-------------:|
| age_norm   |      1     |      -0.244 |  -0.132 |   0.147 |       -0.102 |
| age_norm2  |     -0.244 |       1     |  -0.009 |   0.073 |       -0.27  |
| educH      |     -0.132 |      -0.009 |   1     |  -0.35  |        0.011 |
| educL      |      0.147 |       0.073 |  -0.35  |   1     |       -0.068 |
| n_children |     -0.102 |      -0.27  |   0.011 |  -0.068 |        1     |

#### Within-role correlation — wage-opportunity candidates

|             |   educL |   educH |   pexp_years |   pexp_years2 |
|:------------|--------:|--------:|-------------:|--------------:|
| educL       |   1     |  -0.35  |        0.246 |         0.282 |
| educH       |  -0.35  |   1     |       -0.322 |        -0.334 |
| pexp_years  |   0.246 |  -0.322 |        1     |         0.965 |
| pexp_years2 |   0.282 |  -0.334 |        0.965 |         1     |

#### Within-role correlation — hours-opportunity candidates

|       |   gsur |   educH |
|:------|-------:|--------:|
| gsur  |  1     |  -0.766 |
| educH | -0.766 |   1     |

### Within-role VIF — singles

**VIF — preference (singles)** (n_obs=1,676)

| Variable | VIF |
|---|---|
| age_norm | 1.14 |
| age_norm2 | 1.19 |
| educH | 1.15 |
| educL | 1.17 |
| n_children | 1.12 |

NOTE: Polynomial pairs `age_norm` vs `age_norm2` are mechanically collinear — high VIF expected and acceptable.

**VIF — wage-opportunity (singles)** (n_obs=1,676)

| Variable | VIF |
|---|---|
| educL | 1.20 |
| educH | 1.23 |
| pexp_years | 14.93 ⚠ HIGH |
| pexp_years2 | 15.25 ⚠ HIGH |

NOTE: Polynomial pairs `pexp_years` vs `pexp_years2` are mechanically collinear — high VIF expected and acceptable.

**VIF — hours-opportunity (singles)** (n_obs=1,676)

| Variable | VIF |
|---|---|
| gsur | 2.42 |
| educH | 2.42 |

### GSUR strength check — singles

**GSUR strength check — singles** (LPM, OLS, chosen rows, n=1,676)

- Outcome: `working`
- GSUR column: `gsur`
- Controls: ['age_norm', 'age_norm2', 'educH', 'n_children']

| Statistic | Value |
|---|---|
| Coefficient | -0.601188 |
| SE | 0.220713 |
| t-stat | -2.724 |
| Sign | negative ✓ (as expected) |

> **Interpretation:** this is a STRENGTH CHECK only. A negative coefficient indicates the opportunity shifter (gsur) retains a meaningful association with employment conditional on preference shifters. This is NOT evidence of identification — that requires the Monte Carlo recovery test (§17 of the model spec contract).

### Promotion shortlist (DROPPED but usable — decide role on ECONOMIC grounds)

| column   | dtype   |   pct_missing |   n_unique |
|:---------|:--------|--------------:|-----------:|
| dms      | float64 |             0 |          4 |
| dmb      | float64 |             0 |          4 |
| ddi      | float64 |             0 |          2 |
| drg01    | float64 |             0 |          3 |
| dcz      | float64 |             0 |          3 |
| drgur    | float64 |             0 |          2 |
| drgmd    | float64 |             0 |          2 |
| drgru    | float64 |             0 |          2 |
| ddt      | float64 |             0 |          2 |
| dsu01    | float64 |             0 |        577 |
| dsu02    | float64 |             0 |        254 |
| dncsy    | float64 |             0 |          2 |
| dcu      | float64 |             0 |          2 |
| dehde    | float64 |             0 |          8 |
| dey      | float64 |             0 |          5 |
| dew      | float64 |             0 |         52 |
| drgn2    | float64 |             0 |         22 |
| les      | int64   |             0 |          3 |
| liwmy_s  | float64 |             0 |         21 |
| lowas    | float64 |             0 |          2 |
| lindi    | float64 |             0 |         13 |
| lse_s    | float64 |             0 |          2 |
| lunmy    | float64 |             0 |         13 |
| lunmy_s  | float64 |             0 |         13 |
| liwmy    | float64 |             0 |         13 |
| liwwh    | float64 |             0 |        195 |
| lfs      | float64 |             0 |         14 |
| lcs      | float64 |             0 |          2 |
| liwftmy  | float64 |             0 |         13 |
| liwptmy  | float64 |             0 |         13 |
| lpemy    | float64 |             0 |          2 |
| lse      | float64 |             0 |          2 |
| lhw_f    | float64 |             0 |          3 |
| liwwh_f  | float64 |             0 |          4 |
| ypr      | float64 |             0 |         90 |
| yemxp    | float64 |             0 |        728 |
| yem00    | float64 |             0 |       1473 |
| yprrt    | float64 |             0 |         90 |
| yptmp    | float64 |             0 |         86 |
| yse      | float64 |             0 |         55 |

_These are candidates only. Promote by editing the whitelist with a written economic reason; data cannot assign a variable to preferences vs opportunity._


## couples: pre-drop exploration

- Total columns in full frame: **1466**, rows: **257,700**
- Kept by whitelist: **93**  |  Dropped: **1373**
- Dropped variables that are usable (<= 20% missing, non-constant): **1097** (promotion candidates)

### Choice space — couples (male) (chosen alternatives, n=2,577)

- Employment rate (h>0): **0.972**
- Mass at h=0: **0.028**
- In PT1 (18.5, 21.5): 0.005   |   PT2 (29.5, 30.5): 0.010   |   FT (37.5, 40.5): 0.265
- Hours | working, quantiles [p10,p25,p50,p75,p90]: [35.0, 35.0, 40.0, 45.0, 55.0]
- Hours histogram (working): 0-10:0.0, 10-15:0.003, 15-18.5:0.006, PT1:0.006, 21.5-25:0.007, 25-29.5:0.012, PT2:0.01, 30.5-35:0.016, 35-37.5:0.308, FT:0.273, 40.5-45:0.053, 45+:0.305
  > **FLAG: Empirical peak bin is '35-37.5', not in contract focal bins {PT1, PT2, FT}. Report this mismatch; do NOT silently change the bins.**
- Hourly wage | working, quantiles [p10,p25,p50,p75,p90]: [10.06, 12.27, 15.29, 20.62, 27.87]

#### Within-role correlation — preference candidates (male)

|                 |   age_norm_male |   age_norm2_male |   educH_male |   educL_male |   n_children_male |
|:----------------|----------------:|-----------------:|-------------:|-------------:|------------------:|
| age_norm_male   |           1     |            0.028 |       -0.068 |        0.104 |            -0.15  |
| age_norm2_male  |           0.028 |            1     |       -0.063 |        0.042 |            -0.514 |
| educH_male      |          -0.068 |           -0.063 |        1     |       -0.327 |             0.097 |
| educL_male      |           0.104 |            0.042 |       -0.327 |        1     |            -0.064 |
| n_children_male |          -0.15  |           -0.514 |        0.097 |       -0.064 |             1     |

#### Within-role correlation — wage-opportunity candidates (male)

|                  |   educL_male |   educH_male |   pexp_years_male |   pexp_years2_male |
|:-----------------|-------------:|-------------:|------------------:|-------------------:|
| educL_male       |        1     |       -0.327 |             0.228 |              0.238 |
| educH_male       |       -0.327 |        1     |            -0.32  |             -0.319 |
| pexp_years_male  |        0.228 |       -0.32  |             1     |              0.969 |
| pexp_years2_male |        0.238 |       -0.319 |             0.969 |              1     |

#### Within-role correlation — hours-opportunity candidates (male)

|            |   gsur_male |   educH_male |
|:-----------|------------:|-------------:|
| gsur_male  |       1     |       -0.741 |
| educH_male |      -0.741 |        1     |

### Choice space — couples (female) (chosen alternatives, n=2,577)

- Employment rate (h>0): **0.965**
- Mass at h=0: **0.035**
- In PT1 (18.5, 21.5): 0.028   |   PT2 (29.5, 30.5): 0.042   |   FT (37.5, 40.5): 0.201
- Hours | working, quantiles [p10,p25,p50,p75,p90]: [24.0, 32.0, 35.0, 40.0, 45.0]
- Hours histogram (working): 0-10:0.0, 10-15:0.02, 15-18.5:0.027, PT1:0.029, 21.5-25:0.03, 25-29.5:0.072, PT2:0.043, 30.5-35:0.06, 35-37.5:0.353, FT:0.208, 40.5-45:0.031, 45+:0.127
  > **FLAG: Empirical peak bin is '35-37.5', not in contract focal bins {PT1, PT2, FT}. Report this mismatch; do NOT silently change the bins.**
- Hourly wage | working, quantiles [p10,p25,p50,p75,p90]: [8.86, 11.13, 13.84, 17.25, 22.48]

#### Within-role correlation — preference candidates (female)

|                   |   age_norm_female |   age_norm2_female |   educH_female |   educL_female |   n_children_female |
|:------------------|------------------:|-------------------:|---------------:|---------------:|--------------------:|
| age_norm_female   |             1     |              0.127 |         -0.129 |          0.141 |              -0.196 |
| age_norm2_female  |             0.127 |              1     |         -0.164 |          0.121 |              -0.57  |
| educH_female      |            -0.129 |             -0.164 |          1     |         -0.353 |               0.106 |
| educL_female      |             0.141 |              0.121 |         -0.353 |          1     |              -0.107 |
| n_children_female |            -0.196 |             -0.57  |          0.106 |         -0.107 |               1     |

#### Within-role correlation — wage-opportunity candidates (female)

|                    |   educL_female |   educH_female |   pexp_years_female |   pexp_years2_female |
|:-------------------|---------------:|---------------:|--------------------:|---------------------:|
| educL_female       |          1     |         -0.353 |               0.25  |                0.278 |
| educH_female       |         -0.353 |          1     |              -0.309 |               -0.33  |
| pexp_years_female  |          0.25  |         -0.309 |               1     |                0.964 |
| pexp_years2_female |          0.278 |         -0.33  |               0.964 |                1     |

#### Within-role correlation — hours-opportunity candidates (female)

|              |   gsur_female |   educH_female |
|:-------------|--------------:|---------------:|
| gsur_female  |         1     |         -0.807 |
| educH_female |        -0.807 |          1     |

### EUROMOD counterfactual output columns — couples

Total `_em` columns: **161**  |  Kept in whitelist: **0**  |  Dropped (decomposition): **161**

> All `_em` columns are EUROMOD's tax-benefit calculations on each draw alternative (counterfactual). Only `ils_dispy_em` enters the estimation whitelist — it becomes `consumption` after normalisation. The remaining 338 columns are the accounting decomposition (earnings, taxes, benefits, social contributions) which sum back to `ils_dispy_em` via the identity below. They are dropped for estimation but available for welfare decomposition analysis.

**Key columns (named):**

| Column | Status | Mean (chosen) | Label |
|---|---|---|---|
| `ils_origy_em` | dropped | 3351.2 | Original income (pre-tax+benefit, counterfactual) |
| `ils_earns_em` | dropped | 3222.2 | Gross earnings (counterfactual) |
| `ils_ben_em` | dropped | 126.7 | Total benefits (counterfactual) |
| `ils_bennt_em` | dropped | 72.0 | Non-means-tested benefits (counterfactual) |
| `ils_benmt_em` | dropped | 54.7 | Means-tested benefits (counterfactual) |
| `ils_tax_em` | dropped | 495.0 | Total taxes (counterfactual) |
| `ils_taxin_em` | dropped | 495.0 | Income tax (counterfactual) |
| `ils_taxwl_em` | dropped | 0.0 | Wealth/other tax (counterfactual) |
| `ils_sicdy_em` | dropped | 472.0 | Employee social insurance contributions (counterfactual) |
| `ils_sicee_em` | dropped | 431.1 | Employer social insurance contributions (counterfactual) |
| `ils_sicot_em` | dropped | 0.0 | Other social insurance (counterfactual) |
| `ils_b1_bun_em` | dropped | 69.7 | Unemployment benefit (counterfactual) |
| `ils_b1_bfa_em` | dropped | 35.4 | Family/child benefit (counterfactual) |
| `ils_b1_bsa_em` | dropped | 13.6 | Social assistance (counterfactual) |
| `ils_b1_bho_em` | dropped | 6.3 | Housing benefit (counterfactual) |
| `ils_b1_bhl_em` | dropped | 1.5 | Health/sickness benefit (counterfactual) |
| `ils_b1_bdi_em` | dropped | 0.0 | Disability benefit (counterfactual) |
| `ils_b1_bed_em` | dropped | 0.2 | Education benefit (counterfactual) |
| `ils_b2_bfaed_em` | dropped | 35.5 | Family+education aggregate (counterfactual) |
| `ils_b2_bsaho_em` | dropped | 19.9 | Social assistance+housing aggregate (counterfactual) |
| `ils_b2_bunwk_em` | dropped | 69.7 | Unemployment+in-work aggregate (counterfactual) |

<details><summary>All _em columns (click to expand)</summary>

| Column | Status | Mean | Std | Min | Max |
|---|---|---|---|---|---|
| `bdi_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bdi_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bho_em` | dropped | 12.1 | 38.6 | 0.0 | 278.7 |
| `bhoot_em` | dropped | 2.0 | 12.6 | 0.0 | 154.4 |
| `bhotn_em` | dropped | 10.1 | 37.1 | 0.0 | 278.7 |
| `bhotn_s_em` | dropped | 4.3 | 32.9 | 0.0 | 554.6 |
| `bsa00_em` | dropped | 7.5 | 55.5 | 0.0 | 829.4 |
| `bsa00_s_em` | dropped | 7.0 | 53.9 | 0.0 | 801.4 |
| `bsa_em` | dropped | 3.3 | 42.8 | 0.0 | 829.4 |
| `bsaoa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsaoa_s_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `bsaot_em` | dropped | 2.8 | 47.2 | 0.0 | 1905.6 |
| `bun_em` | dropped | 18.5 | 172.3 | 0.0 | 4064.2 |
| `bunct_em` | dropped | 65.3 | 269.2 | 0.0 | 4064.2 |
| `bunct_s_em` | dropped | 69.4 | 276.7 | 0.0 | 4035.8 |
| `bunctmy_s_em` | dropped | 0.7 | 2.4 | 0.0 | 12.0 |
| `bunmt_em` | dropped | 2.8 | 26.7 | 0.0 | 482.5 |
| `bunmt_s_em` | dropped | 0.3 | 8.0 | 0.0 | 259.8 |
| `bunmy_em` | dropped | 0.8 | 2.6 | 0.0 | 12.0 |
| `i_bch_inclt1_em` | dropped | 565.7 | 1502.9 | 0.0 | 11352.9 |
| `i_bch_inclt2_em` | dropped | 310.8 | 999.6 | 0.0 | 4514.6 |
| `i_bchcc_amt_em` | dropped | 6.9 | 45.8 | 0.0 | 392.5 |
| `i_bched_amt_em` | dropped | 18.0 | 28.0 | 0.0 | 161.9 |
| `i_bched_inclt_em` | dropped | 1225.2 | 1245.5 | 0.0 | 4362.6 |
| `i_bchlg_inclt1_em` | dropped | 631.2 | 1995.0 | 0.0 | 9044.3 |
| `i_bchlg_inclt2_em` | dropped | 315.6 | 997.6 | 0.0 | 4522.6 |
| `i_bchlg_nwa_em` | dropped | 1.0 | 1.0 | 0.0 | 2.0 |
| `i_bdi_inclt_em` | dropped | 1541.7 | 1014.6 | 0.0 | 4002.3 |
| `i_bho_c_em` | dropped | 50.2 | 32.7 | 0.0 | 125.6 |
| `i_bho_l_em` | dropped | 56.7 | 129.4 | 0.0 | 572.5 |
| `i_bho_l_lt_em` | dropped | 266.8 | 170.4 | 0.0 | 688.2 |
| `i_bho_minrate_em` | dropped | 0.1 | 0.1 | 0.0 | 0.4 |
| `i_bho_p0_em` | dropped | 25.6 | 15.8 | 0.0 | 57.3 |
| `i_bho_pp_em` | dropped | 226.4 | 406.5 | 0.0 | 4999.1 |
| `i_bho_r0_em` | dropped | 455.1 | 282.9 | 0.0 | 762.8 |
| `i_bho_rate_em` | dropped | 0.1 | 0.2 | 0.0 | 0.7 |
| `i_bho_rentbase_em` | dropped | 269.7 | 170.9 | 0.0 | 606.9 |
| `i_bho_rl_em` | dropped | 0.2 | 0.4 | 0.0 | 1.1 |
| `i_bho_tf_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_bho_tp_em` | dropped | 0.1 | 0.1 | 0.0 | 0.4 |
| `i_bsa00_amt_em` | dropped | 715.6 | 465.2 | 0.0 | 1901.4 |
| `i_bsa00_bonus_em` | dropped | 17.7 | 11.5 | 0.0 | 47.0 |
| `i_bsa00_ded_em` | dropped | 104.7 | 65.1 | 0.0 | 152.6 |
| `i_bsa00_faminc_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_bsa00_rand2_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_bsa00_rand_em` | dropped | 0.5 | 0.3 | 0.0 | 1.0 |
| `i_bsa00_wkinc_em` | dropped | 2564.0 | 1715.0 | 0.0 | 22230.5 |
| `i_bunmt_amt_em` | dropped | 1.9 | 29.2 | 0.0 | 494.3 |
| `i_bunmt_bonus_em` | dropped | 9.2 | 5.7 | 0.0 | 12.7 |
| `i_bunmt_inc_em` | dropped | 2948.2 | 2747.9 | 0.0 | 26846.6 |
| `i_imax_gt_all_em` | dropped | 341.5 | 615.1 | 0.0 | 8812.7 |
| `i_imax_gt_kt_em` | dropped | 300.2 | 518.3 | 0.0 | 8685.2 |
| `i_imax_nt_all_em` | dropped | 248.1 | 584.9 | 0.0 | 8812.7 |
| `i_imax_nt_kt_em` | dropped | 208.6 | 487.5 | 0.0 | 8685.2 |
| `i_loneparent_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_nDepRel_em` | dropped | 1.0 | 1.1 | 0.0 | 6.0 |
| `i_rngy_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_rngy_kt_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `i_scee_base_em` | dropped | 3100.1 | 1985.0 | 0.0 | 27120.0 |
| `i_takeup2_em` | dropped | 0.4 | 0.3 | 0.0 | 1.0 |
| `i_takeup_em` | dropped | 0.4 | 0.3 | 0.0 | 1.0 |
| `i_tingt1_em` | dropped | 264.3 | 550.3 | 0.0 | 8753.2 |
| `i_tingt2_em` | dropped | 260.0 | 583.3 | 0.0 | 8812.7 |
| `i_tingt_all_em` | dropped | 251.6 | 525.3 | 0.0 | 8812.7 |
| `i_tingt_kt_em` | dropped | 216.4 | 438.3 | 0.0 | 8685.2 |
| `i_tinqtdep_em` | dropped | 0.5 | 0.7 | 0.0 | 5.0 |
| `i_tinqtimax_em` | dropped | 1.3 | 0.7 | 0.0 | 2.0 |
| `i_tscerrd_coef_em` | dropped | 0.0 | 0.1 | -0.0 | 0.3 |
| `i_tscxc_bhl_em` | dropped | 0.1 | 1.4 | 0.0 | 39.3 |
| `i_tscxc_cap_em` | dropped | 11.2 | 38.5 | 0.0 | 788.8 |
| `i_tscxc_earns_em` | dropped | 237.5 | 165.2 | 0.0 | 2057.0 |
| `i_tscxc_pen_em` | dropped | 0.0 | 0.3 | 0.0 | 14.1 |
| `i_tscxc_unemp_em` | dropped | 3.7 | 16.0 | 0.0 | 245.8 |
| `i_yempv_em` | dropped | 2513.4 | 1380.4 | 0.0 | 15848.3 |
| `il_bsa00_em` | dropped | 2697.9 | 1866.2 | -95.7 | 20583.6 |
| `il_bunmt_em` | dropped | 2277.6 | 1652.6 | -473.8 | 20101.6 |
| `il_capy_em` | dropped | 136.5 | 469.6 | 0.0 | 9619.6 |
| `il_crds_base_full_em` | dropped | 179.8 | 471.2 | 0.0 | 9619.6 |
| `il_crds_base_red_em` | dropped | 3291.6 | 2218.8 | 0.0 | 27649.2 |
| `il_dpisilc_em` | dropped | 2646.5 | 1556.9 | -97.9 | 15129.0 |
| `il_rgby_em` | dropped | 2414.6 | 1697.1 | -11.3 | 21785.5 |
| `il_rngy_em` | dropped | 2347.0 | 1638.2 | -94.6 | 20101.6 |
| `il_rniy_bens_em` | dropped | 2347.0 | 1638.2 | -94.6 | 20101.6 |
| `il_rniy_em` | dropped | 2347.0 | 1638.2 | -94.6 | 20101.6 |
| `il_rniy_kt_em` | dropped | 2245.7 | 1536.0 | -3323.2 | 19960.1 |
| `il_temp_bun_em` | dropped | 69.7 | 276.7 | 0.0 | 4035.8 |
| `il_tscee_base_em` | dropped | 3100.1 | 1985.0 | 0.0 | 27120.0 |
| `il_tscxc_pen_em` | dropped | 0.1 | 4.5 | 0.0 | 204.2 |
| `ils_b1_bcb_em` | dropped | 20.0 | 62.2 | 0.0 | 427.7 |
| `ils_b1_bdi_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b1_bed_em` | dropped | 0.2 | 5.4 | 0.0 | 178.4 |
| `ils_b1_bfa_em` | dropped | 35.4 | 81.7 | 0.0 | 732.3 |
| `ils_b1_bhl_em` | dropped | 1.5 | 22.2 | 0.0 | 633.3 |
| `ils_b1_bho_em` | dropped | 6.3 | 35.0 | 0.0 | 554.6 |
| `ils_b1_boa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b1_bsa_em` | dropped | 13.6 | 74.1 | 0.0 | 1905.6 |
| `ils_b1_bsu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b1_bun_em` | dropped | 69.7 | 276.7 | 0.0 | 4035.8 |
| `ils_b1_bwk_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_b2_bfaed_em` | dropped | 35.5 | 81.8 | 0.0 | 732.3 |
| `ils_b2_bsaho_em` | dropped | 19.9 | 96.2 | 0.0 | 1905.6 |
| `ils_b2_bunwk_em` | dropped | 69.7 | 276.7 | 0.0 | 4035.8 |
| `ils_b2_penhl_em` | dropped | 1.5 | 22.2 | 0.0 | 633.3 |
| `ils_base_tin_em` | dropped | 3430.1 | 2389.1 | 0.0 | 27798.3 |
| `ils_base_tinto_em` | dropped | 3430.1 | 2389.1 | 0.0 | 27798.3 |
| `ils_base_tscdf_em` | dropped | 3471.5 | 2376.3 | 0.0 | 27798.3 |
| `ils_base_tscxc_em` | dropped | 3429.8 | 2389.3 | 0.0 | 27798.3 |
| `ils_ben_em` | dropped | 126.7 | 306.0 | 0.0 | 4035.8 |
| `ils_benmt_em` | dropped | 54.7 | 135.5 | 0.0 | 1905.6 |
| `ils_bennt_em` | dropped | 72.0 | 277.8 | 0.0 | 4035.8 |
| `ils_bensim_em` | dropped | 113.1 | 289.4 | 0.0 | 4035.8 |
| `ils_earns_csg_em` | dropped | 3222.2 | 2235.9 | 0.0 | 27649.2 |
| `ils_earns_em` | dropped | 3222.2 | 2235.9 | 0.0 | 27649.2 |
| `ils_origrepy_em` | dropped | 3422.1 | 2376.6 | -92.9 | 27798.3 |
| `ils_origy_em` | dropped | 3351.2 | 2394.3 | -248.8 | 27798.3 |
| `ils_pen_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicct_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicdy_em` | dropped | 472.0 | 355.3 | 0.0 | 5008.9 |
| `ils_sicee_em` | dropped | 431.1 | 247.9 | 0.0 | 2782.3 |
| `ils_sicer_em` | dropped | 1173.7 | 869.1 | 0.0 | 10363.5 |
| `ils_sicot_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_sicse_em` | dropped | 40.8 | 221.3 | 0.0 | 3394.6 |
| `ils_tax_em` | dropped | 495.0 | 734.7 | 0.0 | 10969.2 |
| `ils_taxin_em` | dropped | 495.0 | 734.7 | 0.0 | 10969.2 |
| `ils_taxsim_em` | dropped | 493.1 | 727.6 | 0.0 | 10969.2 |
| `ils_taxwl_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bdi_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bed_em` | dropped | 0.2 | 5.4 | 0.0 | 178.4 |
| `ils_udb_bfa_em` | dropped | 35.4 | 81.7 | 0.0 | 732.3 |
| `ils_udb_bhl_em` | dropped | 1.5 | 22.2 | 0.0 | 633.3 |
| `ils_udb_bho_em` | dropped | 6.3 | 35.0 | 0.0 | 554.6 |
| `ils_udb_boa_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bsa_em` | dropped | 13.6 | 74.1 | 0.0 | 1905.6 |
| `ils_udb_bsu_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_bun_em` | dropped | 69.7 | 276.7 | 0.0 | 4035.8 |
| `ils_udb_kfbcc_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_tis_em` | dropped | 965.1 | 1038.7 | 0.0 | 15978.1 |
| `ils_udb_tpr_em` | dropped | 1.9 | 43.2 | 0.0 | 1666.7 |
| `ils_udb_xmp_em` | dropped | 15.0 | 98.3 | 0.0 | 2321.7 |
| `ils_udb_yds_em` | dropped | 2511.0 | 1375.5 | -97.9 | 14130.0 |
| `ils_udb_yem_em` | dropped | 3100.1 | 1985.0 | 0.0 | 27120.0 |
| `ils_udb_yiy_em` | dropped | 93.8 | 375.8 | 0.0 | 9619.6 |
| `ils_udb_yot_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `ils_udb_ypp_em` | dropped | 0.1 | 4.5 | 0.0 | 204.2 |
| `ils_udb_ypr_em` | dropped | 42.8 | 222.0 | 0.0 | 5726.2 |
| `ils_udb_ypt_em` | dropped | 7.3 | 53.5 | 0.0 | 1200.0 |
| `ils_udb_yse_em` | dropped | 122.1 | 769.8 | 0.0 | 14577.5 |
| `temp_convcoef_em` | dropped | 0.3 | 1.0 | 0.0 | 13.0 |
| `tin_s_em` | dropped | 214.2 | 538.6 | 0.0 | 8753.2 |
| `tis_em` | dropped | 681.6 | 993.1 | -39.4 | 9997.5 |
| `tu_bch_fr_HeadID_em` | dropped | 315192352572.0 | 81233983641.9 | 148300002000.0 | 435030001000.0 |
| `tu_bch_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 1.0 |
| `tu_bchlg_fr_HeadID_em` | dropped | 315192352572.0 | 81233983641.9 | 148300002000.0 | 435030001000.0 |
| `tu_bchlg_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 1.0 |
| `tu_bho_fr_HeadID_em` | dropped | 315192352572.0 | 81233983641.9 | 148300002000.0 | 435030001000.0 |
| `tu_bho_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_bsa00_fr_HeadID_em` | dropped | 315192352572.4 | 81233983642.1 | 148300002000.0 | 435030001000.0 |
| `tu_bsa00_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_fiscalunit_fr_HeadID_em` | dropped | 315192352584.4 | 81233983647.5 | 148300002000.0 | 435030001000.0 |
| `tu_fiscalunit_fr_IsDepChild_em` | dropped | 0.0 | 0.0 | 0.0 | 0.0 |
| `tu_household_fr_HeadID_em` | dropped | 315192352572.0 | 81233983641.9 | 148300002000.0 | 435030001000.0 |

</details>

### Within-role VIF — couples

**VIF — preference (male)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| age_norm_male | 1.04 |
| age_norm2_male | 1.36 |
| educH_male | 1.13 |
| educL_male | 1.13 |
| n_children_male | 1.40 |

**VIF — wage-opportunity (male)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| educL_male | 1.15 |
| educH_male | 1.21 |
| pexp_years_male | 16.33 ⚠ HIGH |
| pexp_years2_male | 16.38 ⚠ HIGH |

**VIF — hours-opportunity (male)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| gsur_male | 2.22 |
| educH_male | 2.22 |

**VIF — preference (female)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| age_norm_female | 1.06 |
| age_norm2_female | 1.51 |
| educH_female | 1.17 |
| educL_female | 1.16 |
| n_children_female | 1.52 |

**VIF — wage-opportunity (female)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| educL_female | 1.19 |
| educH_female | 1.22 |
| pexp_years_female | 14.24 ⚠ HIGH |
| pexp_years2_female | 14.57 ⚠ HIGH |

**VIF — hours-opportunity (female)** (n_obs=2,577)

| Variable | VIF |
|---|---|
| gsur_female | 2.86 |
| educH_female | 2.86 |

### GSUR strength check — couples

**GSUR strength check — couples (male)** (LPM, OLS, chosen rows, n=2,577)

- Outcome: `working_male`
- GSUR column: `gsur_male`
- Controls: ['age_norm_male', 'age_norm2_male', 'educH_male', 'n_children']

| Statistic | Value |
|---|---|
| Coefficient | -0.339334 |
| SE | 0.109598 |
| t-stat | -3.096 |
| Sign | negative ✓ (as expected) |

> **Interpretation:** this is a STRENGTH CHECK only. A negative coefficient indicates the opportunity shifter (gsur) retains a meaningful association with employment conditional on preference shifters. This is NOT evidence of identification — that requires the Monte Carlo recovery test (§17 of the model spec contract).

**GSUR strength check — couples (female)** (LPM, OLS, chosen rows, n=2,577)

- Outcome: `working_female`
- GSUR column: `gsur_female`
- Controls: ['age_norm_female', 'age_norm2_female', 'educH_female', 'n_children']

| Statistic | Value |
|---|---|
| Coefficient | -0.091369 |
| SE | 0.158894 |
| t-stat | -0.575 |
| Sign | negative ✓ (as expected) |

> **Interpretation:** this is a STRENGTH CHECK only. A negative coefficient indicates the opportunity shifter (gsur) retains a meaningful association with employment conditional on preference shifters. This is NOT evidence of identification — that requires the Monte Carlo recovery test (§17 of the model spec contract).

### Promotion shortlist (DROPPED but usable — decide role on ECONOMIC grounds)

| column       | dtype   |   pct_missing |   n_unique |
|:-------------|:--------|--------------:|-----------:|
| dwt_male     | float64 |             0 |       2575 |
| dms_male     | float64 |             0 |          4 |
| dmb_male     | float64 |             0 |          4 |
| ddi_male     | float64 |             0 |          2 |
| drg01_male   | float64 |             0 |          3 |
| dcz_male     | float64 |             0 |          3 |
| drgur_male   | float64 |             0 |          2 |
| drgmd_male   | float64 |             0 |          2 |
| drgru_male   | float64 |             0 |          2 |
| ddt_male     | float64 |             0 |          2 |
| dsu01_male   | float64 |             0 |        703 |
| dsu02_male   | float64 |             0 |        238 |
| dehde_male   | float64 |             0 |          8 |
| dey_male     | float64 |             0 |          5 |
| dew_male     | float64 |             0 |         51 |
| drgn2_male   | float64 |             0 |         22 |
| les_male     | int64   |             0 |          3 |
| loc_male     | float64 |             0 |         11 |
| lowas_male   | float64 |             0 |          2 |
| lindi_male   | float64 |             0 |         13 |
| lunmy_male   | float64 |             0 |         13 |
| liwmy_male   | float64 |             0 |         13 |
| liwwh_male   | float64 |             0 |        206 |
| lfs_male     | float64 |             0 |         14 |
| lhw_male     | float64 |             0 |     229200 |
| lcs_male     | float64 |             0 |          2 |
| liwftmy_male | float64 |             0 |         13 |
| liwptmy_male | float64 |             0 |         13 |
| lpemy_male   | float64 |             0 |          5 |
| lse_male     | float64 |             0 |          2 |
| ypr_male     | float64 |             0 |        284 |
| yemxp_male   | float64 |             0 |       1535 |
| yem00_male   | float64 |             0 |       2344 |
| yprrt_male   | float64 |             0 |        284 |
| yptmp_male   | float64 |             0 |         34 |
| yse_male     | float64 |             0 |        144 |
| yiy_male     | float64 |             0 |        569 |
| ypp_male     | float64 |             0 |          4 |
| ypt_male     | float64 |             0 |         48 |
| yivwg_male   | float64 |             0 |     231575 |

_These are candidates only. Promote by editing the whitelist with a written economic reason; data cannot assign a variable to preferences vs opportunity._


---
