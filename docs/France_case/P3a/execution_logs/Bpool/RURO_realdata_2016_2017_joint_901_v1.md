# Step 4 — real-data joint baseline (joint_pooled_v1_bll0_tlmpin)

**Params:** 47  **Couples alts:** 901  **Singles alts:** 101  **HH:** sm=2243 sf=2764 cou=7438
**Pinned:** {'theta_l_m': -0.8}

> The certified-baseline real-data joint MNL estimate (paper baseline). 47-param spec (beta_ll=0, theta_l_m=-0.8). REAL observed choices, pooled 2015-2017, couples 901 (30x30), singles 101. JAX backend, constrained two-stage optimizer warm-started from theta_star. Authorized by the 901 Check-5 re-gate (RURO_jax_recovery_gate_tlmpin_901_v1.md, PD min_eig +1.706).

## Deliverable 1 — estimate

- **negLL** = 238504.636097
- **max|grad|** = 4.420e+01  (optimizer: scipy)
- **in-bounds**: PASS — all params within spec bounds
- **params at a bound**: [('beta_l_age2_sf', 'hi', 1.0), ('beta_l0_m', 'lo', 1e-06), ('beta_l_age2_f', 'hi', 1.0)]

## Hessian @ MLE (PD verification)

- **PD** = True  **min_eig** = 4.588e-01  **cond** = 1.295e+06
- verdict: SEPARATELY IDENTIFIED


## Deliverable 2 — both SE flavors

Clustered on **idorighh** (cluster_id == idorighh): 9657 clusters over 12445 choice-sets; 2788 clusters span >1 choice-set (the 2016-2017 repeat HHs; max 2/cluster). Sandwich V = H⁻¹ B H⁻¹, B = Σⱼ sⱼsⱼ′.

### SE asymmetry by block (EXPECTED: opportunity tight, singles-leisure wide)

| Block | n | median SE (Hessian) | median SE (clustered) |
|---|---|---|---|
| market_hours_opp | 17 | 0.1022 | 0.1243 |
| occupation_opp | 6 | 0.0359 | 0.0470 |
| wage_opp | 6 | 0.0096 | 0.0124 |
| couples_leisure | 8 | 0.3143 | 0.3943 |
| singles_leisure | 10 | 0.3341 | 0.3874 |

### Full parameter table

| Param | Block | Estimate | SE (Hessian) | SE (clustered) | clu/H |
|---|---|---|---|---|---|
| beta_l0_sm | singles_leisure | 4.54866 | 0.8406 | 1.1551 | 1.37 |
| beta_l_age_sm | singles_leisure | 0.67753 | 0.4211 | 0.5196 | 1.23 |
| beta_l_age2_sm | singles_leisure | 0.38188 | 0.3529 | 0.3916 | 1.11 |
| theta_l_sm | singles_leisure | -1.86161 | 0.1752 | 0.1687 | 0.96 |
| beta_l0_sf | singles_leisure | 3.72851 | 0.6652 | 0.9640 | 1.45 |
| beta_l_age_sf | singles_leisure | 0.49864 | 0.3152 | 0.3832 | 1.22 |
| beta_l_age2_sf * | singles_leisure | 1.00000 | 0.3047 | 0.3116 | 1.02 |
| beta_l_nkids_sf | singles_leisure | 1.73949 | 0.5029 | 0.7414 | 1.47 |
| theta_l_sf | singles_leisure | -1.34909 | 0.1211 | 0.1541 | 1.27 |
| theta_c_singles | singles_leisure | 0.00758 | 0.0403 | 0.0838 | 2.08 |
| beta_l0_m * | couples_leisure | 0.00000 | 0.0996 | 0.1222 | 1.23 |
| beta_l_age_m | couples_leisure | -0.06724 | 0.0647 | 0.0657 | 1.01 |
| beta_l_age2_m | couples_leisure | 0.08775 | 0.0614 | 0.0620 | 1.01 |
| beta_l0_f | couples_leisure | 10.05224 | 1.3822 | 2.5053 | 1.81 |
| beta_l_age_f | couples_leisure | -1.78025 | 0.5431 | 0.6663 | 1.23 |
| beta_l_age2_f * | couples_leisure | 1.00000 | 0.5510 | 0.7479 | 1.36 |
| beta_l_nkids_f | couples_leisure | 0.58572 | 0.5290 | 0.8549 | 1.62 |
| theta_l_f | couples_leisure | -2.13174 | 0.0811 | 0.1006 | 1.24 |
| beta_E | market_hours_opp | -0.75265 | 0.1664 | 0.1893 | 1.14 |
| beta_h_pt1 | market_hours_opp | -1.43327 | 0.0517 | 0.0586 | 1.13 |
| beta_h_pt2 | market_hours_opp | -0.10370 | 0.0474 | 0.0555 | 1.17 |
| beta_h_ft | market_hours_opp | 1.04132 | 0.0204 | 0.0272 | 1.33 |
| beta_h_lh | market_hours_opp | -1.21848 | 0.0322 | 0.0495 | 1.54 |
| beta_E_gsur | market_hours_opp | -1.30619 | 0.0856 | 0.0947 | 1.11 |
| beta_E_drgn2 | market_hours_opp | -0.07503 | 0.1321 | 0.1553 | 1.18 |
| beta_E_drgn3 | market_hours_opp | 0.03131 | 0.1523 | 0.1814 | 1.19 |
| beta_E_drgn4 | market_hours_opp | -0.01686 | 0.1580 | 0.1855 | 1.17 |
| beta_E_drgn5 | market_hours_opp | -0.14021 | 0.1374 | 0.1613 | 1.17 |
| beta_E_drgn6 | market_hours_opp | -0.04846 | 0.1531 | 0.1768 | 1.15 |
| beta_E_drgn7 | market_hours_opp | -0.17515 | 0.1461 | 0.1691 | 1.16 |
| beta_E_drgn8 | market_hours_opp | -0.36569 | 0.1352 | 0.1591 | 1.18 |
| beta_E_y2015 | market_hours_opp | -0.25461 | 0.0865 | 0.0931 | 1.08 |
| beta_E_y2017 | market_hours_opp | -0.06947 | 0.0913 | 0.0753 | 0.82 |
| beta_E_drgur | market_hours_opp | -0.53049 | 0.0921 | 0.1112 | 1.21 |
| beta_E_drgmd | market_hours_opp | -0.66754 | 0.1022 | 0.1243 | 1.22 |
| beta_occ_2_m | occupation_opp | -1.59165 | 0.0425 | 0.0553 | 1.30 |
| beta_occ_3_m | occupation_opp | -2.29410 | 0.0561 | 0.0700 | 1.25 |
| beta_occ_4_m | occupation_opp | 0.29064 | 0.0244 | 0.0314 | 1.29 |
| beta_occ_2_f | occupation_opp | -0.04758 | 0.0344 | 0.0449 | 1.31 |
| beta_occ_3_f | occupation_opp | -0.47292 | 0.0374 | 0.0492 | 1.32 |
| beta_occ_4_f | occupation_opp | 0.77179 | 0.0296 | 0.0375 | 1.27 |
| beta_w0 | wage_opp | 2.19682 | 0.0114 | 0.0146 | 1.28 |
| beta_w_educL | wage_opp | -0.06076 | 0.0095 | 0.0123 | 1.29 |
| beta_w_educH | wage_opp | 0.33820 | 0.0066 | 0.0086 | 1.30 |
| beta_w_pexp | wage_opp | 0.38278 | 0.0216 | 0.0280 | 1.29 |
| beta_w_pexp2 | wage_opp | -0.08224 | 0.0097 | 0.0126 | 1.29 |
| sigma | wage_opp | 0.38983 | 0.0021 | 0.0043 | 2.02 |

(* = param at a bound)

## Deliverable 4 — beta_l0_m reading

- beta_l0_m = **1e-06** (floor = 1e-06)
- gradient at MLE = 4.420e+01
- SE (Hessian) = 0.0996, SE (clustered) = 0.1222
- **Reading: **AT FLOOR** — couples-male baseline leisure preference effectively absent.**

> At the 901 SYNTHETIC gate beta_l0_m was interior at +0.019 (did not jam its floor). This real-data reading is the finding the synthetic result anticipated — stated, not pre-assumed.

## Deliverable 3 — LR pooling test

> Run separately once the gender-relaxation design for beta_E / beta_h_pt2 is fixed (it requires a spec/routing decision, not just a re-fit). Pending. Check 6 of the 901 gate flagged beta_E lands outside the group-specific range under forced sharing — the motivation for the test.

## Full JSON

```json
{
  "spec": "joint_pooled_v1_bll0_tlmpin",
  "n_params": 47,
  "fixed_params": {
    "theta_l_m": -0.8
  },
  "n_hh": {
    "sm": 2243,
    "sf": 2764,
    "cou": 7438
  },
  "couples_alts": 901,
  "singles_alts": 101,
  "negLL": 238504.6360973987,
  "max_grad": 44.20306158002317,
  "optimizer": "scipy",
  "in_bounds": true,
  "out_of_bounds": [],
  "at_bound": [
    [
      "beta_l_age2_sf",
      "hi",
      1.0
    ],
    [
      "beta_l0_m",
      "lo",
      1e-06
    ],
    [
      "beta_l_age2_f",
      "hi",
      1.0
    ]
  ],
  "hessian": {
    "pd": true,
    "min_eig": 0.4587910453370293,
    "cond": 1294561.527158389,
    "verdict": "SEPARATELY IDENTIFIED"
  },
  "cluster_summary": {
    "n_clusters": 9657,
    "n_groups": 12445,
    "n_multi_group_clusters": 2788,
    "max_groups_per_cluster": 2
  },
  "block_se": {
    "singles_leisure": {
      "n": 10,
      "median_se_hessian": 0.33408899254267077,
      "median_se_clustered": 0.38744477446017817,
      "max_se_hessian": 0.8406013373206254
    },
    "couples_leisure": {
      "n": 8,
      "median_se_hessian": 0.3143222296230558,
      "median_se_clustered": 0.394276998269639,
      "max_se_hessian": 1.3822369885215
    },
    "market_hours_opp": {
      "n": 17,
      "median_se_hessian": 0.10221786662109422,
      "median_se_clustered": 0.12429590452426412,
      "max_se_hessian": 0.16636035488473486
    },
    "occupation_opp": {
      "n": 6,
      "median_se_hessian": 0.03588210181990972,
      "median_se_clustered": 0.04702543817373295,
      "max_se_hessian": 0.056079364440453285
    },
    "wage_opp": {
      "n": 6,
      "median_se_hessian": 0.009619165435554104,
      "median_se_clustered": 0.012421005664438486,
      "max_se_hessian": 0.02161752138105084
    }
  },
  "beta_l0_m": {
    "value": 1e-06,
    "floor": 1e-06,
    "gradient": 44.20306158002317,
    "at_floor": true,
    "se_hessian": 0.09961637883538013,
    "se_clustered": 0.12223931777670424
  },
  "params": [
    {
      "param": "beta_l0_sm",
      "block": "singles_leisure",
      "estimate": 4.548663369591292,
      "se_hessian": 0.8406013373206254,
      "se_clustered": 1.155108348336803,
      "clu_over_hess": 1.3741452660766076,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sm",
      "block": "singles_leisure",
      "estimate": 0.6775305440791358,
      "se_hessian": 0.4211271415660584,
      "se_clustered": 0.5195514685676663,
      "clu_over_hess": 1.2337164178865185,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sm",
      "block": "singles_leisure",
      "estimate": 0.38188009486033064,
      "se_hessian": 0.35294070925375587,
      "se_clustered": 0.3916423377360453,
      "clu_over_hess": 1.109654759192043,
      "at_bound": false
    },
    {
      "param": "theta_l_sm",
      "block": "singles_leisure",
      "estimate": -1.8616120265204585,
      "se_hessian": 0.17516038520323154,
      "se_clustered": 0.16874322312150847,
      "clu_over_hess": 0.9633640787311726,
      "at_bound": false
    },
    {
      "param": "beta_l0_sf",
      "block": "singles_leisure",
      "estimate": 3.728508753936399,
      "se_hessian": 0.6652267268401157,
      "se_clustered": 0.9639822398049165,
      "clu_over_hess": 1.4491032920218272,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sf",
      "block": "singles_leisure",
      "estimate": 0.49863621035046235,
      "se_hessian": 0.3152372758315857,
      "se_clustered": 0.38324721118431104,
      "clu_over_hess": 1.2157420475523315,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sf",
      "block": "singles_leisure",
      "estimate": 1.0,
      "se_hessian": 0.30474590233369014,
      "se_clustered": 0.31161996381532436,
      "clu_over_hess": 1.0225566986430132,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_sf",
      "block": "singles_leisure",
      "estimate": 1.7394925331921767,
      "se_hessian": 0.5028854045988782,
      "se_clustered": 0.7414031290908883,
      "clu_over_hess": 1.4742983636247338,
      "at_bound": false
    },
    {
      "param": "theta_l_sf",
      "block": "singles_leisure",
      "estimate": -1.349085275197915,
      "se_hessian": 0.12111422724008461,
      "se_clustered": 0.15407651340983347,
      "clu_over_hess": 1.2721586631140185,
      "at_bound": false
    },
    {
      "param": "theta_c_singles",
      "block": "singles_leisure",
      "estimate": 0.007580978321100435,
      "se_hessian": 0.04029784658434222,
      "se_clustered": 0.08383598259535242,
      "clu_over_hess": 2.080408500734305,
      "at_bound": false
    },
    {
      "param": "beta_l0_m",
      "block": "couples_leisure",
      "estimate": 1e-06,
      "se_hessian": 0.09961637883538013,
      "se_clustered": 0.12223931777670424,
      "clu_over_hess": 1.2271005953620275,
      "at_bound": true
    },
    {
      "param": "beta_l_age_m",
      "block": "couples_leisure",
      "estimate": -0.06723689745235506,
      "se_hessian": 0.06471357647379156,
      "se_clustered": 0.06566790030886467,
      "clu_over_hess": 1.0147468875477714,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_m",
      "block": "couples_leisure",
      "estimate": 0.08775048918478498,
      "se_hessian": 0.06139570516726118,
      "se_clustered": 0.061968742838661856,
      "clu_over_hess": 1.0093335139622477,
      "at_bound": false
    },
    {
      "param": "beta_l0_f",
      "block": "couples_leisure",
      "estimate": 10.052237044896547,
      "se_hessian": 1.3822369885215,
      "se_clustered": 2.505339082023552,
      "clu_over_hess": 1.8125249887165662,
      "at_bound": false
    },
    {
      "param": "beta_l_age_f",
      "block": "couples_leisure",
      "estimate": -1.780253386288037,
      "se_hessian": 0.5430593015255067,
      "se_clustered": 0.6663146787625738,
      "clu_over_hess": 1.226964857964555,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_f",
      "block": "couples_leisure",
      "estimate": 1.0,
      "se_hessian": 0.5509875360175956,
      "se_clustered": 0.7478551927659338,
      "clu_over_hess": 1.3572996553991945,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_f",
      "block": "couples_leisure",
      "estimate": 0.5857198501055841,
      "se_hessian": 0.5290280804107315,
      "se_clustered": 0.8549206172506537,
      "clu_over_hess": 1.6160212451991263,
      "at_bound": false
    },
    {
      "param": "theta_l_f",
      "block": "couples_leisure",
      "estimate": -2.131739110508045,
      "se_hessian": 0.08110834835608967,
      "se_clustered": 0.10055009377997262,
      "clu_over_hess": 1.2397009163412862,
      "at_bound": false
    },
    {
      "param": "beta_E",
      "block": "market_hours_opp",
      "estimate": -0.75265301737783,
      "se_hessian": 0.16636035488473486,
      "se_clustered": 0.18925494184334984,
      "clu_over_hess": 1.1376204503439407,
      "at_bound": false
    },
    {
      "param": "beta_h_pt1",
      "block": "market_hours_opp",
      "estimate": -1.4332708022989755,
      "se_hessian": 0.05165596163608044,
      "se_clustered": 0.05860255756369286,
      "clu_over_hess": 1.1344781068359862,
      "at_bound": false
    },
    {
      "param": "beta_h_pt2",
      "block": "market_hours_opp",
      "estimate": -0.10369544637185832,
      "se_hessian": 0.04741676156892751,
      "se_clustered": 0.05551789535339789,
      "clu_over_hess": 1.1708495796933358,
      "at_bound": false
    },
    {
      "param": "beta_h_ft",
      "block": "market_hours_opp",
      "estimate": 1.0413227078263703,
      "se_hessian": 0.020384831121307942,
      "se_clustered": 0.027161967401187172,
      "clu_over_hess": 1.3324597706769912,
      "at_bound": false
    },
    {
      "param": "beta_h_lh",
      "block": "market_hours_opp",
      "estimate": -1.2184848074097656,
      "se_hessian": 0.032185175540688865,
      "se_clustered": 0.04954196950386983,
      "clu_over_hess": 1.539279145494742,
      "at_bound": false
    },
    {
      "param": "beta_E_gsur",
      "block": "market_hours_opp",
      "estimate": -1.306190335762088,
      "se_hessian": 0.08563464238435889,
      "se_clustered": 0.09472899423674676,
      "clu_over_hess": 1.1061994491851692,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn2",
      "block": "market_hours_opp",
      "estimate": -0.07502860797260201,
      "se_hessian": 0.1320651096576924,
      "se_clustered": 0.1552524173646832,
      "clu_over_hess": 1.175574818868446,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn3",
      "block": "market_hours_opp",
      "estimate": 0.03131377038298806,
      "se_hessian": 0.15234088429729042,
      "se_clustered": 0.18144514365196357,
      "clu_over_hess": 1.191046937195643,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn4",
      "block": "market_hours_opp",
      "estimate": -0.01685855646065593,
      "se_hessian": 0.15802532154482282,
      "se_clustered": 0.1854829364322333,
      "clu_over_hess": 1.1737545262935745,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn5",
      "block": "market_hours_opp",
      "estimate": -0.1402066979956915,
      "se_hessian": 0.1374196399477378,
      "se_clustered": 0.16125884465948667,
      "clu_over_hess": 1.1734774208462138,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn6",
      "block": "market_hours_opp",
      "estimate": -0.0484589776197602,
      "se_hessian": 0.1530721881414365,
      "se_clustered": 0.17676898374584515,
      "clu_over_hess": 1.1548079758454433,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn7",
      "block": "market_hours_opp",
      "estimate": -0.17515265702873883,
      "se_hessian": 0.14607958047935748,
      "se_clustered": 0.16910336991279507,
      "clu_over_hess": 1.1576112784407337,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn8",
      "block": "market_hours_opp",
      "estimate": -0.3656941546069446,
      "se_hessian": 0.1352167411906113,
      "se_clustered": 0.15911351775627589,
      "clu_over_hess": 1.1767294223721747,
      "at_bound": false
    },
    {
      "param": "beta_E_y2015",
      "block": "market_hours_opp",
      "estimate": -0.25460641123851746,
      "se_hessian": 0.08649461413068478,
      "se_clustered": 0.09308107442149832,
      "clu_over_hess": 1.0761487909624299,
      "at_bound": false
    },
    {
      "param": "beta_E_y2017",
      "block": "market_hours_opp",
      "estimate": -0.06947110737619774,
      "se_hessian": 0.09134056628138662,
      "se_clustered": 0.07528752833816656,
      "clu_over_hess": 0.8242507289284088,
      "at_bound": false
    },
    {
      "param": "beta_E_drgur",
      "block": "market_hours_opp",
      "estimate": -0.530487815363722,
      "se_hessian": 0.09211308599007884,
      "se_clustered": 0.11124193756827971,
      "clu_over_hess": 1.207667036367245,
      "at_bound": false
    },
    {
      "param": "beta_E_drgmd",
      "block": "market_hours_opp",
      "estimate": -0.6675446983120384,
      "se_hessian": 0.10221786662109422,
      "se_clustered": 0.12429590452426412,
      "clu_over_hess": 1.2159900087233257,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_m",
      "block": "occupation_opp",
      "estimate": -1.5916485115155634,
      "se_hessian": 0.04245053296757038,
      "se_clustered": 0.055322226028616646,
      "clu_over_hess": 1.3032162887302134,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_m",
      "block": "occupation_opp",
      "estimate": -2.294101394919219,
      "se_hessian": 0.056079364440453285,
      "se_clustered": 0.07003076670720539,
      "clu_over_hess": 1.248779607364597,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_m",
      "block": "occupation_opp",
      "estimate": 0.29064315448057115,
      "se_hessian": 0.024401457463440693,
      "se_clustered": 0.03143779795478355,
      "clu_over_hess": 1.2883573861063422,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_f",
      "block": "occupation_opp",
      "estimate": -0.04758052424554271,
      "se_hessian": 0.034389042183499995,
      "se_clustered": 0.04489174559667067,
      "clu_over_hess": 1.3054084308928475,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_f",
      "block": "occupation_opp",
      "estimate": -0.4729186216832488,
      "se_hessian": 0.03737516145631945,
      "se_clustered": 0.04915913075079522,
      "clu_over_hess": 1.3152887863306693,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_f",
      "block": "occupation_opp",
      "estimate": 0.7717937415014848,
      "se_hessian": 0.02961687487363659,
      "se_clustered": 0.03754487058716397,
      "clu_over_hess": 1.2676850865377587,
      "at_bound": false
    },
    {
      "param": "beta_w0",
      "block": "wage_opp",
      "estimate": 2.1968218592232938,
      "se_hessian": 0.011375738312588226,
      "se_clustered": 0.014614831623384145,
      "clu_over_hess": 1.284736974584901,
      "at_bound": false
    },
    {
      "param": "beta_w_educL",
      "block": "wage_opp",
      "estimate": -0.060763939524428885,
      "se_hessian": 0.00951816236243495,
      "se_clustered": 0.012257233391141181,
      "clu_over_hess": 1.2877730936295477,
      "at_bound": false
    },
    {
      "param": "beta_w_educH",
      "block": "wage_opp",
      "estimate": 0.33820279250009355,
      "se_hessian": 0.0066206496078800555,
      "se_clustered": 0.008637672513189337,
      "clu_over_hess": 1.304656344131031,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp",
      "block": "wage_opp",
      "estimate": 0.38277970535929984,
      "se_hessian": 0.02161752138105084,
      "se_clustered": 0.0279550296329183,
      "clu_over_hess": 1.293165351390502,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp2",
      "block": "wage_opp",
      "estimate": -0.08224249604353946,
      "se_hessian": 0.009720168508673258,
      "se_clustered": 0.012584777937735792,
      "clu_over_hess": 1.294707795086727,
      "at_bound": false
    },
    {
      "param": "sigma",
      "block": "wage_opp",
      "estimate": 0.3898254999925787,
      "se_hessian": 0.002119196389441875,
      "se_clustered": 0.0042773949315643624,
      "clu_over_hess": 2.018404218162567,
      "at_bound": false
    }
  ],
  "cluster_key": "cluster",
  "flat_directions": [
    "beta_l0_f",
    "beta_l0_sm",
    "beta_l0_sf"
  ]
}
```
