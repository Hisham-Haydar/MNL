# Step 4 — real-data joint baseline (joint_pooled_v1_bll0_tlmpin)

**Params:** 47  **Couples alts:** 901  **Singles alts:** 101  **HH:** sm=2243 sf=2764 cou=7438
**Pinned:** {'theta_l_m': -0.8}

> The certified-baseline real-data joint MNL estimate (paper baseline). 47-param spec (beta_ll=0, theta_l_m=-0.8). REAL observed choices, pooled 2015-2017, couples 901 (30x30), singles 101. JAX backend, constrained two-stage optimizer warm-started from theta_star. Authorized by the 901 Check-5 re-gate (RURO_jax_recovery_gate_tlmpin_901_v1.md, PD min_eig +1.706).

## Deliverable 1 — estimate

- **negLL** = 238502.866126
- **max|grad|** = 4.404e+01  (optimizer: scipy)
- **in-bounds**: PASS — all params within spec bounds
- **params at a bound**: [('beta_l_age2_sf', 'hi', 1.0), ('beta_l0_m', 'lo', 1e-06), ('beta_l_age2_f', 'hi', 1.0)]

## Hessian @ MLE (PD verification)

- **PD** = True  **min_eig** = 4.589e-01  **max_eig** = 5.941e+05  **cond** = 1.295e+06
- verdict: SEPARATELY IDENTIFIED


## Deliverable 2 — both SE flavors

Clustered on **idorighh** (cluster_id == idorighh): 9657 clusters over 12445 choice-sets; 2788 clusters span >1 choice-set (the 2016-2017 repeat HHs; max 2/cluster). Sandwich V = H⁻¹ B H⁻¹, B = Σⱼ sⱼsⱼ′.

### SE asymmetry by block (EXPECTED: opportunity tight, singles-leisure wide)

| Block | n | median SE (Hessian) | median SE (clustered) |
|---|---|---|---|
| market_hours_opp | 17 | 0.1022 | 0.1243 |
| occupation_opp | 6 | 0.0359 | 0.0470 |
| wage_opp | 6 | 0.0096 | 0.0124 |
| couples_leisure | 8 | 0.3144 | 0.3944 |
| singles_leisure | 10 | 0.3342 | 0.3876 |

### Full parameter table

| Param | Block | Estimate | SE (Hessian) | SE (clustered) | clu/H |
|---|---|---|---|---|---|
| beta_l0_sm | singles_leisure | 4.54812 | 0.8406 | 1.1551 | 1.37 |
| beta_l_age_sm | singles_leisure | 0.67759 | 0.4212 | 0.5197 | 1.23 |
| beta_l_age2_sm | singles_leisure | 0.38184 | 0.3530 | 0.3917 | 1.11 |
| theta_l_sm | singles_leisure | -1.86199 | 0.1752 | 0.1687 | 0.96 |
| beta_l0_sf | singles_leisure | 3.72955 | 0.6655 | 0.9644 | 1.45 |
| beta_l_age_sf | singles_leisure | 0.49904 | 0.3154 | 0.3834 | 1.22 |
| beta_l_age2_sf * | singles_leisure | 1.00000 | 0.3048 | 0.3116 | 1.02 |
| beta_l_nkids_sf | singles_leisure | 1.73813 | 0.5029 | 0.7413 | 1.47 |
| theta_l_sf | singles_leisure | -1.34955 | 0.1211 | 0.1541 | 1.27 |
| theta_c_singles | singles_leisure | 0.00713 | 0.0403 | 0.0839 | 2.08 |
| beta_l0_m * | couples_leisure | 0.00000 | 0.0996 | 0.1222 | 1.23 |
| beta_l_age_m | couples_leisure | -0.06695 | 0.0647 | 0.0657 | 1.01 |
| beta_l_age2_m | couples_leisure | 0.08774 | 0.0614 | 0.0620 | 1.01 |
| beta_l0_f | couples_leisure | 10.05563 | 1.3821 | 2.5045 | 1.81 |
| beta_l_age_f | couples_leisure | -1.77900 | 0.5432 | 0.6665 | 1.23 |
| beta_l_age2_f * | couples_leisure | 1.00000 | 0.5512 | 0.7480 | 1.36 |
| beta_l_nkids_f | couples_leisure | 0.58479 | 0.5291 | 0.8552 | 1.62 |
| theta_l_f | couples_leisure | -2.13187 | 0.0811 | 0.1005 | 1.24 |
| beta_E | market_hours_opp | -0.75295 | 0.1664 | 0.1892 | 1.14 |
| beta_h_pt1 | market_hours_opp | -1.43328 | 0.0517 | 0.0586 | 1.13 |
| beta_h_pt2 | market_hours_opp | -0.10363 | 0.0474 | 0.0555 | 1.17 |
| beta_h_ft | market_hours_opp | 1.04127 | 0.0204 | 0.0272 | 1.33 |
| beta_h_lh | market_hours_opp | -1.21904 | 0.0322 | 0.0495 | 1.54 |
| beta_E_gsur | market_hours_opp | -1.30587 | 0.0856 | 0.0947 | 1.11 |
| beta_E_drgn2 | market_hours_opp | -0.07467 | 0.1321 | 0.1552 | 1.18 |
| beta_E_drgn3 | market_hours_opp | 0.03160 | 0.1523 | 0.1814 | 1.19 |
| beta_E_drgn4 | market_hours_opp | -0.01671 | 0.1580 | 0.1855 | 1.17 |
| beta_E_drgn5 | market_hours_opp | -0.14008 | 0.1374 | 0.1613 | 1.17 |
| beta_E_drgn6 | market_hours_opp | -0.04843 | 0.1531 | 0.1768 | 1.15 |
| beta_E_drgn7 | market_hours_opp | -0.17509 | 0.1461 | 0.1691 | 1.16 |
| beta_E_drgn8 | market_hours_opp | -0.36549 | 0.1352 | 0.1591 | 1.18 |
| beta_E_y2015 | market_hours_opp | -0.25460 | 0.0865 | 0.0931 | 1.08 |
| beta_E_y2017 | market_hours_opp | -0.07012 | 0.0913 | 0.0753 | 0.82 |
| beta_E_drgur | market_hours_opp | -0.53053 | 0.0921 | 0.1112 | 1.21 |
| beta_E_drgmd | market_hours_opp | -0.66757 | 0.1022 | 0.1243 | 1.22 |
| beta_occ_2_m | occupation_opp | -1.59168 | 0.0425 | 0.0553 | 1.30 |
| beta_occ_3_m | occupation_opp | -2.29407 | 0.0561 | 0.0700 | 1.25 |
| beta_occ_4_m | occupation_opp | 0.29065 | 0.0244 | 0.0314 | 1.29 |
| beta_occ_2_f | occupation_opp | -0.04760 | 0.0344 | 0.0449 | 1.31 |
| beta_occ_3_f | occupation_opp | -0.47290 | 0.0374 | 0.0492 | 1.32 |
| beta_occ_4_f | occupation_opp | 0.77180 | 0.0296 | 0.0375 | 1.27 |
| beta_w0 | wage_opp | 2.19692 | 0.0114 | 0.0146 | 1.28 |
| beta_w_educL | wage_opp | -0.06077 | 0.0095 | 0.0123 | 1.29 |
| beta_w_educH | wage_opp | 0.33815 | 0.0066 | 0.0086 | 1.30 |
| beta_w_pexp | wage_opp | 0.38257 | 0.0216 | 0.0280 | 1.29 |
| beta_w_pexp2 | wage_opp | -0.08217 | 0.0097 | 0.0126 | 1.29 |
| sigma | wage_opp | 0.38980 | 0.0021 | 0.0043 | 2.02 |

(* = param at a bound)

## Deliverable 4 — beta_l0_m reading

- beta_l0_m = **1e-06** (floor = 1e-06)
- gradient at MLE = 4.404e+01
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
  "negLL": 238502.86612599975,
  "max_grad": 44.04419809570307,
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
    "min_eig": 0.45888132962345707,
    "max_eig": 594054.454517772,
    "cond": 1294570.9841915632,
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
      "median_se_hessian": 0.3341997039292502,
      "median_se_clustered": 0.3875826464567077,
      "max_se_hessian": 0.8406434600324904
    },
    "couples_leisure": {
      "n": 8,
      "median_se_hessian": 0.3143741357419783,
      "median_se_clustered": 0.394368836501121,
      "max_se_hessian": 1.3820691300223953
    },
    "market_hours_opp": {
      "n": 17,
      "median_se_hessian": 0.10221662099216607,
      "median_se_clustered": 0.12429367334369126,
      "max_se_hessian": 0.1663585115729399
    },
    "occupation_opp": {
      "n": 6,
      "median_se_hessian": 0.03588233408237622,
      "median_se_clustered": 0.047026688273740805,
      "max_se_hessian": 0.05607940914327406
    },
    "wage_opp": {
      "n": 6,
      "median_se_hessian": 0.009618266098521521,
      "median_se_clustered": 0.012419637437747252,
      "max_se_hessian": 0.021615155037670305
    }
  },
  "beta_l0_m": {
    "value": 1e-06,
    "floor": 1e-06,
    "gradient": 44.04419809570307,
    "at_floor": true,
    "se_hessian": 0.09960337148788326,
    "se_clustered": 0.1222217649252682
  },
  "params": [
    {
      "param": "beta_l0_sm",
      "block": "singles_leisure",
      "estimate": 4.548122345175691,
      "se_hessian": 0.8406434600324904,
      "se_clustered": 1.1550669434578524,
      "clu_over_hess": 1.3740271570223241,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sm",
      "block": "singles_leisure",
      "estimate": 0.6775947842192139,
      "se_hessian": 0.42123097296672024,
      "se_clustered": 0.5196907094365196,
      "clu_over_hess": 1.233742869799791,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sm",
      "block": "singles_leisure",
      "estimate": 0.38184069681390853,
      "se_hessian": 0.35301853119875304,
      "se_clustered": 0.39172723578829965,
      "clu_over_hess": 1.1096506306853144,
      "at_bound": false
    },
    {
      "param": "theta_l_sm",
      "block": "singles_leisure",
      "estimate": -1.8619919160925784,
      "se_hessian": 0.17519247502691102,
      "se_clustered": 0.1687308344225801,
      "clu_over_hess": 0.9631169055443829,
      "at_bound": false
    },
    {
      "param": "beta_l0_sf",
      "block": "singles_leisure",
      "estimate": 3.7295510390925677,
      "se_hessian": 0.6655399058926351,
      "se_clustered": 0.9644499714360675,
      "clu_over_hess": 1.44912418158086,
      "at_bound": false
    },
    {
      "param": "beta_l_age_sf",
      "block": "singles_leisure",
      "estimate": 0.4990358628980907,
      "se_hessian": 0.31538087665974734,
      "se_clustered": 0.3834380571251158,
      "clu_over_hess": 1.215793618136184,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_sf",
      "block": "singles_leisure",
      "estimate": 1.0,
      "se_hessian": 0.30480781271029,
      "se_clustered": 0.3116048346825734,
      "clu_over_hess": 1.0222993692709041,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_sf",
      "block": "singles_leisure",
      "estimate": 1.738133225246802,
      "se_hessian": 0.5028932657456546,
      "se_clustered": 0.7412533064122087,
      "clu_over_hess": 1.473977396203806,
      "at_bound": false
    },
    {
      "param": "theta_l_sf",
      "block": "singles_leisure",
      "estimate": -1.3495473502462407,
      "se_hessian": 0.12112753963773078,
      "se_clustered": 0.15405808990875944,
      "clu_over_hess": 1.2718667478058054,
      "at_bound": false
    },
    {
      "param": "theta_c_singles",
      "block": "singles_leisure",
      "estimate": 0.007126004699915052,
      "se_hessian": 0.040266651817405734,
      "se_clustered": 0.0838637304985079,
      "clu_over_hess": 2.0827093069172644,
      "at_bound": false
    },
    {
      "param": "beta_l0_m",
      "block": "couples_leisure",
      "estimate": 1e-06,
      "se_hessian": 0.09960337148788326,
      "se_clustered": 0.1222217649252682,
      "clu_over_hess": 1.2270846167103537,
      "at_bound": true
    },
    {
      "param": "beta_l_age_m",
      "block": "couples_leisure",
      "estimate": -0.06694825275203518,
      "se_hessian": 0.06471243131534758,
      "se_clustered": 0.06566421391321123,
      "clu_over_hess": 1.0147078788189174,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_m",
      "block": "couples_leisure",
      "estimate": 0.08774135272064552,
      "se_hessian": 0.06139374105891218,
      "se_clustered": 0.06196130446376852,
      "clu_over_hess": 1.0092446460350366,
      "at_bound": false
    },
    {
      "param": "beta_l0_f",
      "block": "couples_leisure",
      "estimate": 10.055626310508115,
      "se_hessian": 1.3820691300223953,
      "se_clustered": 2.5044694110227113,
      "clu_over_hess": 1.812115875116991,
      "at_bound": false
    },
    {
      "param": "beta_l_age_f",
      "block": "couples_leisure",
      "estimate": -1.7789956843476422,
      "se_hessian": 0.5431647117829123,
      "se_clustered": 0.6665159080769738,
      "clu_over_hess": 1.2270972204530135,
      "at_bound": false
    },
    {
      "param": "beta_l_age2_f",
      "block": "couples_leisure",
      "estimate": 1.0,
      "se_hessian": 0.5511615099305092,
      "se_clustered": 0.7479917270316464,
      "clu_over_hess": 1.3571189452724188,
      "at_bound": true
    },
    {
      "param": "beta_l_nkids_f",
      "block": "couples_leisure",
      "estimate": 0.584785236813507,
      "se_hessian": 0.5291448999960734,
      "se_clustered": 0.8552086719969851,
      "clu_over_hess": 1.6162088531956584,
      "at_bound": false
    },
    {
      "param": "theta_l_f",
      "block": "couples_leisure",
      "estimate": -2.131866531380854,
      "se_hessian": 0.08109996297922134,
      "se_clustered": 0.10049479554154322,
      "clu_over_hess": 1.239147243104057,
      "at_bound": false
    },
    {
      "param": "beta_E",
      "block": "market_hours_opp",
      "estimate": -0.7529548430141862,
      "se_hessian": 0.1663585115729399,
      "se_clustered": 0.1892491353244691,
      "clu_over_hess": 1.137598151937617,
      "at_bound": false
    },
    {
      "param": "beta_h_pt1",
      "block": "market_hours_opp",
      "estimate": -1.433275798484949,
      "se_hessian": 0.051656169810193456,
      "se_clustered": 0.058602945822448356,
      "clu_over_hess": 1.1344810511073562,
      "at_bound": false
    },
    {
      "param": "beta_h_pt2",
      "block": "market_hours_opp",
      "estimate": -0.10363082541113637,
      "se_hessian": 0.0474168322767,
      "se_clustered": 0.055518031706538795,
      "clu_over_hess": 1.170850709354948,
      "at_bound": false
    },
    {
      "param": "beta_h_ft",
      "block": "market_hours_opp",
      "estimate": 1.0412743528344788,
      "se_hessian": 0.020384658511405047,
      "se_clustered": 0.02716194230312892,
      "clu_over_hess": 1.3324698222406834,
      "at_bound": false
    },
    {
      "param": "beta_h_lh",
      "block": "market_hours_opp",
      "estimate": -1.2190350798390366,
      "se_hessian": 0.03218590539628246,
      "se_clustered": 0.04954507201207676,
      "clu_over_hess": 1.5393406337980264,
      "at_bound": false
    },
    {
      "param": "beta_E_gsur",
      "block": "market_hours_opp",
      "estimate": -1.3058667347293582,
      "se_hessian": 0.08563560164313445,
      "se_clustered": 0.09473085277371411,
      "clu_over_hess": 1.1062087607964957,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn2",
      "block": "market_hours_opp",
      "estimate": -0.07466612762719231,
      "se_hessian": 0.13206081070148026,
      "se_clustered": 0.1552386442442006,
      "clu_over_hess": 1.175508793408161,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn3",
      "block": "market_hours_opp",
      "estimate": 0.03159617569008276,
      "se_hessian": 0.1523367821480957,
      "se_clustered": 0.18142959568448855,
      "clu_over_hess": 1.190976946776452,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn4",
      "block": "market_hours_opp",
      "estimate": -0.016707793568140644,
      "se_hessian": 0.15802358737986305,
      "se_clustered": 0.18547496217258488,
      "clu_over_hess": 1.1737169447161908,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn5",
      "block": "market_hours_opp",
      "estimate": -0.14007635550330758,
      "se_hessian": 0.1374187214919977,
      "se_clustered": 0.16125578587274886,
      "clu_over_hess": 1.1734630050545134,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn6",
      "block": "market_hours_opp",
      "estimate": -0.048433191783215424,
      "se_hessian": 0.15306879153864927,
      "se_clustered": 0.17676352264801415,
      "clu_over_hess": 1.154797923673305,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn7",
      "block": "market_hours_opp",
      "estimate": -0.17508650003720416,
      "se_hessian": 0.1460734835217352,
      "se_clustered": 0.16908606640293233,
      "clu_over_hess": 1.1575411383803478,
      "at_bound": false
    },
    {
      "param": "beta_E_drgn8",
      "block": "market_hours_opp",
      "estimate": -0.36549028015432433,
      "se_hessian": 0.13521133859282522,
      "se_clustered": 0.15909918287349414,
      "clu_over_hess": 1.1766704222388085,
      "at_bound": false
    },
    {
      "param": "beta_E_y2015",
      "block": "market_hours_opp",
      "estimate": -0.25459569824173545,
      "se_hessian": 0.08649338257970549,
      "se_clustered": 0.0930791045778846,
      "clu_over_hess": 1.076141339392181,
      "at_bound": false
    },
    {
      "param": "beta_E_y2017",
      "block": "market_hours_opp",
      "estimate": -0.07012144408048226,
      "se_hessian": 0.09133609890844858,
      "se_clustered": 0.07528006723064563,
      "clu_over_hess": 0.8242093556689253,
      "at_bound": false
    },
    {
      "param": "beta_E_drgur",
      "block": "market_hours_opp",
      "estimate": -0.5305342868425534,
      "se_hessian": 0.09211338095371296,
      "se_clustered": 0.11124348142170942,
      "clu_over_hess": 1.2076799295599556,
      "at_bound": false
    },
    {
      "param": "beta_E_drgmd",
      "block": "market_hours_opp",
      "estimate": -0.6675673672278012,
      "se_hessian": 0.10221662099216607,
      "se_clustered": 0.12429367334369126,
      "clu_over_hess": 1.2159829990194764,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_m",
      "block": "occupation_opp",
      "estimate": -1.5916842150197459,
      "se_hessian": 0.04245119026156662,
      "se_clustered": 0.055324447056952546,
      "clu_over_hess": 1.3032484299277889,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_m",
      "block": "occupation_opp",
      "estimate": -2.2940674287017147,
      "se_hessian": 0.05607940914327406,
      "se_clustered": 0.07002987505650309,
      "clu_over_hess": 1.2487627121317877,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_m",
      "block": "occupation_opp",
      "estimate": 0.29064955725626124,
      "se_hessian": 0.024401549621630974,
      "se_clustered": 0.03143814236990742,
      "clu_over_hess": 1.2883666347992422,
      "at_bound": false
    },
    {
      "param": "beta_occ_2_f",
      "block": "occupation_opp",
      "estimate": -0.047599435902102444,
      "se_hessian": 0.03438927651252598,
      "se_clustered": 0.04489324930848974,
      "clu_over_hess": 1.3054432620045897,
      "at_bound": false
    },
    {
      "param": "beta_occ_3_f",
      "block": "occupation_opp",
      "estimate": -0.47290326041076725,
      "se_hessian": 0.03737539165222646,
      "se_clustered": 0.04916012723899188,
      "clu_over_hess": 1.3153073470485868,
      "at_bound": false
    },
    {
      "param": "beta_occ_4_f",
      "block": "occupation_opp",
      "estimate": 0.7717986224166334,
      "se_hessian": 0.029617311825752494,
      "se_clustered": 0.0375468105168302,
      "clu_over_hess": 1.267731883897138,
      "at_bound": false
    },
    {
      "param": "beta_w0",
      "block": "wage_opp",
      "estimate": 2.196923590682181,
      "se_hessian": 0.01137420205782299,
      "se_clustered": 0.014612547645113395,
      "clu_over_hess": 1.2847096939923908,
      "at_bound": false
    },
    {
      "param": "beta_w_educL",
      "block": "wage_opp",
      "estimate": -0.06077063649780535,
      "se_hessian": 0.00951731308755271,
      "se_clustered": 0.012255680277888436,
      "clu_over_hess": 1.2877248195099436,
      "at_bound": false
    },
    {
      "param": "beta_w_educH",
      "block": "wage_opp",
      "estimate": 0.3381499459577857,
      "se_hessian": 0.0066197365332938095,
      "se_clustered": 0.008636256007811205,
      "clu_over_hess": 1.3046223160658068,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp",
      "block": "wage_opp",
      "estimate": 0.38257285906903615,
      "se_hessian": 0.021615155037670305,
      "se_clustered": 0.027951668212654213,
      "clu_over_hess": 1.293151409922381,
      "at_bound": false
    },
    {
      "param": "beta_w_pexp2",
      "block": "wage_opp",
      "estimate": -0.08217204773132075,
      "se_hessian": 0.009719219109490335,
      "se_clustered": 0.01258359459760607,
      "clu_over_hess": 1.2947125129959067,
      "at_bound": false
    },
    {
      "param": "sigma",
      "block": "wage_opp",
      "estimate": 0.38980296959638056,
      "se_hessian": 0.0021188279734493543,
      "se_clustered": 0.004276672298475438,
      "clu_over_hess": 2.018414119534779,
      "at_bound": false
    }
  ],
  "diagnostics": {
    "solver": "L-BFGS-B (scipy, box) -> optimistix BFGS polish (JAX)",
    "solver_family": "bfgs",
    "chosen_optimizer": "scipy",
    "start_negLL": 238502.866934018,
    "n_iterations": 530,
    "n_function_evaluations": 598,
    "scipy_stage1_seconds": 452.76726937294006,
    "optimistix_stage2_seconds": 135.33119344711304,
    "estimation_seconds": 588.0984628200531,
    "final_max_grad": 44.04419809570307,
    "scipy_final_max_grad": 44.04419809570307,
    "gradient_kind": "max|grad| (analytical JAX gradient; scipy L-BFGS-B stall floor -- the BFGS-family analogue of CONOPT RGmax)",
    "hessian_seconds": 80.96555352210999,
    "sandwich_seconds": 121.58024883270264,
    "post_estimation_seconds": 202.54580235481262,
    "total_seconds": 896.156167268753
  },
  "cluster_key": "cluster",
  "flat_directions": [
    "beta_l0_f",
    "beta_l0_sm",
    "beta_l0_sf"
  ]
}
```
