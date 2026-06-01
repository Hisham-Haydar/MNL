# Step 4 — real-data joint baseline (joint_pooled_v1_bll0_tlmpin_gsplit)

**Params:** 49  **Couples alts:** 901  **Singles alts:** 101  **HH:** sm=2243 sf=2764 cou=7438
**Pinned:** {'theta_l_m': -0.8}

> The certified-baseline real-data joint MNL estimate (paper baseline). 47-param spec (beta_ll=0, theta_l_m=-0.8). REAL observed choices, pooled 2015-2017, couples 901 (30x30), singles 101. JAX backend, constrained two-stage optimizer warm-started from theta_star. Authorized by the 901 Check-5 re-gate (RURO_jax_recovery_gate_tlmpin_901_v1.md, PD min_eig +1.706).

## Deliverable 1 — estimate

- **negLL** = 238362.788142
- **max|grad|** = 3.261e+01  (optimizer: scipy)
- **in-bounds**: PASS — all params within spec bounds
- **params at a bound**: [('beta_l_age2_sf', 'hi', 1.0), ('beta_l0_m', 'lo', 1e-06), ('beta_l_age2_f', 'hi', 1.0)]

## Hessian @ MLE (PD verification)

- **PD** = True  **min_eig** = 4.080e-01  **cond** = 1.453e+06
- verdict: SEPARATELY IDENTIFIED


## Deliverable 2 — both SE flavors

Clustered on **idorighh** (cluster_id == idorighh): 9657 clusters over 12445 choice-sets; 2788 clusters span >1 choice-set (the 2016-2017 repeat HHs; max 2/cluster). Sandwich V = H⁻¹ B H⁻¹, B = Σⱼ sⱼsⱼ′.

### SE asymmetry by block (EXPECTED: opportunity tight, singles-leisure wide)

| Block | n | median SE (Hessian) | median SE (clustered) |
|---|---|---|---|
| market_hours_opp | 15 | 0.1023 | 0.1242 |
| occupation_opp | 6 | 0.0372 | 0.0495 |
| wage_opp | 6 | 0.0096 | 0.0124 |
| couples_leisure | 12 | 0.1404 | 0.1569 |
| singles_leisure | 10 | 0.3377 | 0.3917 |

### Full parameter table

| Param | Block | Estimate | SE (Hessian) | SE (clustered) | clu/H |
|---|---|---|---|---|---|
| beta_l0_sm | singles_leisure | 4.42868 | 0.8172 | 1.1204 | 1.37 |
| beta_l_age_sm | singles_leisure | 0.66682 | 0.4007 | 0.4912 | 1.23 |
| beta_l_age2_sm | singles_leisure | 0.36990 | 0.3356 | 0.3703 | 1.10 |
| theta_l_sm | singles_leisure | -1.79025 | 0.1742 | 0.1711 | 0.98 |
| beta_l0_sf | singles_leisure | 3.84812 | 0.7093 | 1.0244 | 1.44 |
| beta_l_age_sf | singles_leisure | 0.49021 | 0.3399 | 0.4130 | 1.22 |
| beta_l_age2_sf * | singles_leisure | 1.00000 | 0.3234 | 0.3243 | 1.00 |
| beta_l_nkids_sf | singles_leisure | 1.78179 | 0.5383 | 0.8016 | 1.49 |
| theta_l_sf | singles_leisure | -1.44045 | 0.1251 | 0.1537 | 1.23 |
| theta_c_singles | singles_leisure | 0.00951 | 0.0405 | 0.0838 | 2.07 |
| beta_l0_m * | couples_leisure | 0.00000 | 0.0999 | 0.1229 | 1.23 |
| beta_l_age_m | couples_leisure | -0.06986 | 0.0656 | 0.0674 | 1.03 |
| beta_l_age2_m | couples_leisure | 0.13150 | 0.0624 | 0.0638 | 1.02 |
| beta_l0_f | couples_leisure | 10.25929 | 1.4608 | 2.6613 | 1.82 |
| beta_l_age_f | couples_leisure | -1.92081 | 0.5814 | 0.7154 | 1.23 |
| beta_l_age2_f * | couples_leisure | 1.00000 | 0.5872 | 0.8051 | 1.37 |
| beta_l_nkids_f | couples_leisure | 0.52122 | 0.5641 | 0.9220 | 1.63 |
| theta_l_f | couples_leisure | -2.22729 | 0.0846 | 0.1014 | 1.20 |
| beta_E_m | couples_leisure | -0.33105 | 0.1755 | 0.2026 | 1.15 |
| beta_E_f | couples_leisure | -1.02351 | 0.1687 | 0.1908 | 1.13 |
| beta_h_pt1 | market_hours_opp | -1.42750 | 0.0516 | 0.0586 | 1.13 |
| beta_h_pt2_m | couples_leisure | -1.21080 | 0.1121 | 0.1202 | 1.07 |
| beta_h_pt2_f | couples_leisure | 0.39115 | 0.0531 | 0.0643 | 1.21 |
| beta_h_ft | market_hours_opp | 1.03385 | 0.0203 | 0.0270 | 1.33 |
| beta_h_lh | market_hours_opp | -1.24427 | 0.0320 | 0.0491 | 1.54 |
| beta_E_gsur | market_hours_opp | -1.40415 | 0.0879 | 0.0991 | 1.13 |
| beta_E_drgn2 | market_hours_opp | -0.07009 | 0.1321 | 0.1551 | 1.17 |
| beta_E_drgn3 | market_hours_opp | 0.08449 | 0.1529 | 0.1823 | 1.19 |
| beta_E_drgn4 | market_hours_opp | 0.00271 | 0.1583 | 0.1862 | 1.18 |
| beta_E_drgn5 | market_hours_opp | -0.14150 | 0.1374 | 0.1614 | 1.17 |
| beta_E_drgn6 | market_hours_opp | -0.05385 | 0.1531 | 0.1768 | 1.15 |
| beta_E_drgn7 | market_hours_opp | -0.18112 | 0.1460 | 0.1687 | 1.16 |
| beta_E_drgn8 | market_hours_opp | -0.34443 | 0.1353 | 0.1586 | 1.17 |
| beta_E_y2015 | market_hours_opp | -0.25097 | 0.0865 | 0.0930 | 1.07 |
| beta_E_y2017 | market_hours_opp | -0.06419 | 0.0914 | 0.0753 | 0.82 |
| beta_E_drgur | market_hours_opp | -0.53234 | 0.0922 | 0.1112 | 1.21 |
| beta_E_drgmd | market_hours_opp | -0.66440 | 0.1023 | 0.1242 | 1.21 |
| beta_occ_2_m | occupation_opp | -1.62646 | 0.0426 | 0.0556 | 1.30 |
| beta_occ_3_m | occupation_opp | -2.32786 | 0.0562 | 0.0703 | 1.25 |
| beta_occ_4_m | occupation_opp | 0.25724 | 0.0246 | 0.0316 | 1.28 |
| beta_occ_2_f | occupation_opp | 0.01789 | 0.0357 | 0.0474 | 1.33 |
| beta_occ_3_f | occupation_opp | -0.40414 | 0.0386 | 0.0515 | 1.33 |
| beta_occ_4_f | occupation_opp | 0.83757 | 0.0311 | 0.0403 | 1.30 |
| beta_w0 | wage_opp | 2.19709 | 0.0114 | 0.0146 | 1.28 |
| beta_w_educL | wage_opp | -0.06063 | 0.0095 | 0.0123 | 1.29 |
| beta_w_educH | wage_opp | 0.33837 | 0.0066 | 0.0086 | 1.31 |
| beta_w_pexp | wage_opp | 0.38165 | 0.0216 | 0.0279 | 1.29 |
| beta_w_pexp2 | wage_opp | -0.08183 | 0.0097 | 0.0126 | 1.29 |
| sigma | wage_opp | 0.38994 | 0.0021 | 0.0043 | 2.02 |

(* = param at a bound)

## Deliverable 4 — beta_l0_m reading

- beta_l0_m = **1e-06** (floor = 1e-06)
- gradient at MLE = 3.261e+01
- SE (Hessian) = 0.0999, SE (clustered) = 0.1229
- **Reading: **AT FLOOR** — couples-male baseline leisure preference effectively absent.**

> At the 901 SYNTHETIC gate beta_l0_m was interior at +0.019 (did not jam its floor). This real-data reading is the finding the synthetic result anticipated — stated, not pre-assumed.

## Deliverable 3 — LR pooling test

> Run separately once the gender-relaxation design for beta_E / beta_h_pt2 is fixed (it requires a spec/routing decision, not just a re-fit). Pending. Check 6 of the 901 gate flagged beta_E lands outside the group-specific range under forced sharing — the motivation for the test.

## Full JSON

```json
{
  "spec": "joint_pooled_v1_bll0_tlmpin_gsplit",
  "n_params": 49,
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
  "negLL": 238362.78814200818,
  "max_grad": 32.6059938273413,
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
    "min_eig": 0.4079965169623501,
    "cond": 1453328.5445323896,
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
      "median_se_hessian": 0.33770590424048275,
      "median_se_clustered": 0.39167426476862727,
      "max_se_hessian": 0.817187724310588
    },
    "couples_leisure": {
      "n": 12,
      "median_se_hessian": 0.14040626174797688,
      "median_se_clustered": 0.15687426565105597,
      "max_se_hessian": 1.4607812012018133
    },
    "market_hours_opp": {
      "n": 15,
      "median_se_hessian": 0.10226473001976666,
      "median_se_clustered": 0.12422124860906014,
      "max_se_hessian": 0.15827284282259366
    },
    "occupation_opp": {
      "n": 6,
      "median_se_hessian": 0.037165847622837034,
      "median_se_clustered": 0.04945720934306176,
      "max_se_hessian": 0.05624490695889216
    },
    "wage_opp": {
      "n": 6,
      "median_se_hessian": 0.009623252901733298,
      "median_se_clustered": 0.012421009532748554,
      "max_se_hessian": 0.021617183244461803
    }
  },
  "beta_l0_m": {
    "value": 1e-06,
    "floor": 1e-06,
    "gradient": 32.6059938273413,
    "at_floor": true,
    "se_hessian": 0.09992162173168673,
    "se_clustered": 0.12293558033445247
  },
  "params": [
    {
      "param": "beta_l0_sm",
      "block": "singles_leisure",
      "estimate": 4.428684219911562,
      "se_hessian": 0.817187724310588,
      "se_clustered": 1.120365818966399,
      "clu_over_hess": 1.371001773076785,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sm",
      "block": "singles_leisure",
      "estimate": 0.6668207450650255,
      "se_hessian": 0.40071967828540056,
      "se_clustered": 0.49117042027460944,
      "clu_over_hess": 1.2257207391866292,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sm",
      "block": "singles_leisure",
      "estimate": 0.3699041047999929,
      "se_hessian": 0.3355575421216946,
      "se_clustered": 0.37034923387861596,
      "clu_over_hess": 1.103683235778094,
      "at_bound": false
    },
    {
      "param": "theta_l_sm",
      "block": "singles_leisure",
      "estimate": -1.7902481257384688,
      "se_hessian": 0.17416258094118514,
      "se_clustered": 0.1710613854985218,
      "clu_over_hess": 0.9821936754387521,
      "at_bound": false
    },
    {
      "param": "beta_l0_sf",
      "block": "singles_leisure",
      "estimate": 3.8481239717963707,
      "se_hessian": 0.709323650626547,
      "se_clustered": 1.024381591062784,
      "clu_over_hess": 1.4441666933817106,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sf",
      "block": "singles_leisure",
      "estimate": 0.49020815113719285,
      "se_hessian": 0.33985426635927085,
      "se_clustered": 0.4129992956586386,
      "clu_over_hess": 1.2152246905208592,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sf",
      "block": "singles_leisure",
      "estimate": 1.0,
      "se_hessian": 0.3234364626815949,
      "se_clustered": 0.3242948414919303,
      "clu_over_hess": 1.0026539333358353,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_sf",
      "block": "singles_leisure",
      "estimate": 1.781787227310545,
      "se_hessian": 0.538335210020693,
      "se_clustered": 0.8016475510490144,
      "clu_over_hess": 1.4891233865572346,
      "at_bound": false
    },
    {
      "param": "theta_l_sf",
      "block": "singles_leisure",
      "estimate": -1.4404485510439382,
      "se_hessian": 0.12505837961204028,
      "se_clustered": 0.15374796279934252,
      "clu_over_hess": 1.2294095227869088,
      "at_bound": false
    },
    {
      "param": "theta_c_singles",
      "block": "singles_leisure",
      "estimate": 0.009507439232846887,
      "se_hessian": 0.04047756843310895,
      "se_clustered": 0.08383814993144066,
      "clu_over_hess": 2.0712249568544876,
      "at_bound": false
    },
    {
      "param": "beta_l0_m",
      "block": "couples_leisure",
      "estimate": 1e-06,
      "se_hessian": 0.09992162173168673,
      "se_clustered": 0.12293558033445247,
      "clu_over_hess": 1.2303201069390535,
      "at_bound": true
    },
    {
      "param": "beta_l_age_m",
      "block": "couples_leisure",
      "estimate": -0.0698610697652116,
      "se_hessian": 0.06564186751883741,
      "se_clustered": 0.06742993708205404,
      "clu_over_hess": 1.0272397728889036,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_m",
      "block": "couples_leisure",
      "estimate": 0.13149791577090666,
      "se_hessian": 0.0623849231484579,
      "se_clustered": 0.06376540703951875,
      "clu_over_hess": 1.0221284858807262,
      "at_bound": false
    },
    {
      "param": "beta_l0_f",
      "block": "couples_leisure",
      "estimate": 10.259290544834185,
      "se_hessian": 1.4607812012018133,
      "se_clustered": 2.661318667079805,
      "clu_over_hess": 1.8218461908534185,
      "at_bound": false
    },
    {
      "param": "beta_l_age_f",
      "block": "couples_leisure",
      "estimate": -1.9208089256372491,
      "se_hessian": 0.5813959214669292,
      "se_clustered": 0.7154310323558795,
      "clu_over_hess": 1.2305401636646576,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_f",
      "block": "couples_leisure",
      "estimate": 1.0,
      "se_hessian": 0.5871528523460445,
      "se_clustered": 0.8051334028662586,
      "clu_over_hess": 1.3712500921169757,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_f",
      "block": "couples_leisure",
      "estimate": 0.5212237553923443,
      "se_hessian": 0.5640556498974776,
      "se_clustered": 0.9220472770313908,
      "clu_over_hess": 1.6346743042091352,
      "at_bound": false
    },
    {
      "param": "theta_l_f",
      "block": "couples_leisure",
      "estimate": -2.2272947496567244,
      "se_hessian": 0.08462404569090673,
      "se_clustered": 0.10135352471331341,
      "clu_over_hess": 1.1976917894414063,
      "at_bound": false
    },
    {
      "param": "beta_E_m",
      "block": "couples_leisure",
      "estimate": -0.331052597077322,
      "se_hessian": 0.17552973528644483,
      "se_clustered": 0.20260728460417862,
      "clu_over_hess": 1.1542618934253293,
      "at_bound": false
    },
    {
      "param": "beta_E_f",
      "block": "couples_leisure",
      "estimate": -1.023511207905809,
      "se_hessian": 0.16867795299249444,
      "se_clustered": 0.1908129509676595,
      "clu_over_hess": 1.131226384850366,
      "at_bound": false
    },
    {
      "param": "beta_h_pt1",
      "block": "market_hours_opp",
      "estimate": -1.4274956916619763,
      "se_hessian": 0.051632711081642045,
      "se_clustered": 0.05856313409609458,
      "clu_over_hess": 1.1342254332431643,
      "at_bound": false
    },
    {
      "param": "beta_h_pt2_m",
      "block": "couples_leisure",
      "estimate": -1.2107990564065296,
      "se_hessian": 0.11213457050345933,
      "se_clustered": 0.12018350491812538,
      "clu_over_hess": 1.0717792414821594,
      "at_bound": false
    },
    {
      "param": "beta_h_pt2_f",
      "block": "couples_leisure",
      "estimate": 0.391147139939206,
      "se_hessian": 0.05307305326213536,
      "se_clustered": 0.0643463940446809,
      "clu_over_hess": 1.2124117624600361,
      "at_bound": false
    },
    {
      "param": "beta_h_ft",
      "block": "market_hours_opp",
      "estimate": 1.033848786496891,
      "se_hessian": 0.020314635704531736,
      "se_clustered": 0.026998559552911135,
      "clu_over_hess": 1.3290201185782704,
      "at_bound": false
    },
    {
      "param": "beta_h_lh",
      "block": "market_hours_opp",
      "estimate": -1.2442712312066109,
      "se_hessian": 0.031981878896430616,
      "se_clustered": 0.04914208617363717,
      "clu_over_hess": 1.5365603231998275,
      "at_bound": false
    },
    {
      "param": "beta_E_gsur",
      "block": "market_hours_opp",
      "estimate": -1.4041475001055892,
      "se_hessian": 0.08788888881268488,
      "se_clustered": 0.09911649345423064,
      "clu_over_hess": 1.1277477141106522,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn2",
      "block": "market_hours_opp",
      "estimate": -0.07008944205625103,
      "se_hessian": 0.1321442886275773,
      "se_clustered": 0.15509847243273495,
      "clu_over_hess": 1.1737054551774804,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn3",
      "block": "market_hours_opp",
      "estimate": 0.08449016031171955,
      "se_hessian": 0.1528623912290191,
      "se_clustered": 0.18227244451737526,
      "clu_over_hess": 1.1923956118434251,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn4",
      "block": "market_hours_opp",
      "estimate": 0.002706425272723623,
      "se_hessian": 0.15827284282259366,
      "se_clustered": 0.1861840579930468,
      "clu_over_hess": 1.1763487321810384,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn5",
      "block": "market_hours_opp",
      "estimate": -0.1415002895353318,
      "se_hessian": 0.1374426641353082,
      "se_clustered": 0.16139726993157247,
      "clu_over_hess": 1.1742879909012944,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn6",
      "block": "market_hours_opp",
      "estimate": -0.05384696565161733,
      "se_hessian": 0.15310609260135086,
      "se_clustered": 0.17683134016580834,
      "clu_over_hess": 1.1549595261779162,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn7",
      "block": "market_hours_opp",
      "estimate": -0.18111664131943836,
      "se_hessian": 0.1459570595881354,
      "se_clustered": 0.16874963513982275,
      "clu_over_hess": 1.1561594596109561,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn8",
      "block": "market_hours_opp",
      "estimate": -0.3444290883177278,
      "se_hessian": 0.1352620011500923,
      "se_clustered": 0.15859176701489566,
      "clu_over_hess": 1.172478343262981,
      "at_bound": false
    },
    {
      "param": "beta_E_y2015",
      "block": "market_hours_opp",
      "estimate": -0.25096553818628475,
      "se_hessian": 0.08648175883924772,
      "se_clustered": 0.09295521690030176,
      "clu_over_hess": 1.0748534505766343,
      "at_bound": false
    },
    {
      "param": "beta_E_y2017",
      "block": "market_hours_opp",
      "estimate": -0.06418587593114504,
      "se_hessian": 0.09136717944121948,
      "se_clustered": 0.07530483536661751,
      "clu_over_hess": 0.8242000664479789,
      "at_bound": false
    },
    {
      "param": "beta_E_drgur",
      "block": "market_hours_opp",
      "estimate": -0.5323375715092442,
      "se_hessian": 0.0921618281100344,
      "se_clustered": 0.11123961577458745,
      "clu_over_hess": 1.2070031384552786,
      "at_bound": false
    },
    {
      "param": "beta_E_drgmd",
      "block": "market_hours_opp",
      "estimate": -0.664401512023075,
      "se_hessian": 0.10226473001976666,
      "se_clustered": 0.12422124860906014,
      "clu_over_hess": 1.2147027482989445,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_m",
      "block": "occupation_opp",
      "estimate": -1.6264560776683907,
      "se_hessian": 0.0426256848092271,
      "se_clustered": 0.055603192325412776,
      "clu_over_hess": 1.30445276302931,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_m",
      "block": "occupation_opp",
      "estimate": -2.327864310695183,
      "se_hessian": 0.05624490695889216,
      "se_clustered": 0.07027092850731353,
      "clu_over_hess": 1.2493740732591594,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_m",
      "block": "occupation_opp",
      "estimate": 0.25723735179042845,
      "se_hessian": 0.02463311009250926,
      "se_clustered": 0.031593362840747284,
      "clu_over_hess": 1.282556799449964,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_f",
      "block": "occupation_opp",
      "estimate": 0.017887959385597996,
      "se_hessian": 0.03572460762634832,
      "se_clustered": 0.04744115108881824,
      "clu_over_hess": 1.3279684296330383,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_f",
      "block": "occupation_opp",
      "estimate": -0.40413624473750515,
      "se_hessian": 0.038607087619325756,
      "se_clustered": 0.05147326759730528,
      "clu_over_hess": 1.3332595326755243,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_f",
      "block": "occupation_opp",
      "estimate": 0.8375712533560713,
      "se_hessian": 0.031131183522449056,
      "se_clustered": 0.040334871355546406,
      "clu_over_hess": 1.2956420794750854,
      "at_bound": false
    },
    {
      "param": "beta_w0",
      "block": "wage_opp",
      "estimate": 2.1970911702854434,
      "se_hessian": 0.011371738360623598,
      "se_clustered": 0.01459135767266003,
      "clu_over_hess": 1.2831246384620367,
      "at_bound": false
    },
    {
      "param": "beta_w_educL",
      "block": "wage_opp",
      "estimate": -0.06062930626475335,
      "se_hessian": 0.009524175496464334,
      "se_clustered": 0.01225554083355725,
      "clu_over_hess": 1.2867823401728455,
      "at_bound": false
    },
    {
      "param": "beta_w_educH",
      "block": "wage_opp",
      "estimate": 0.33837148485275514,
      "se_hessian": 0.0066255039633583155,
      "se_clustered": 0.008648019260013346,
      "clu_over_hess": 1.30526210652659,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp",
      "block": "wage_opp",
      "estimate": 0.38164849380924687,
      "se_hessian": 0.021617183244461803,
      "se_clustered": 0.027942672315834867,
      "clu_over_hess": 1.2926139358601967,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp2",
      "block": "wage_opp",
      "estimate": -0.08182995029517566,
      "se_hessian": 0.009722330307002262,
      "se_clustered": 0.012586478231939858,
      "clu_over_hess": 1.2945947971830134,
      "at_bound": false
    },
    {
      "param": "sigma",
      "block": "wage_opp",
      "estimate": 0.3899432737224143,
      "se_hessian": 0.0021216882945318265,
      "se_clustered": 0.00428403846733421,
      "clu_over_hess": 2.019164869022162,
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
