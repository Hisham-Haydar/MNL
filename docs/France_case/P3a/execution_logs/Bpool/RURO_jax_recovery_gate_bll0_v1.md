# JAX synthetic recovery gate — joint_pooled_v1_bll0

**Params:** 48  **Couples alts:** 401  **HH:** sm=2243 sf=2764 cou=7438

> Synthetic recovery on the validated JAX backend (use_actual_choice=True). Same 6 checks / thresholds / G3b verdict as the CONOPT gate; JAX optimizer + exact jax.hessian instead of CONOPT.

| Check | Result | Detail |
|---|---|---|
| 1 Synthetic DGP | PASS | one chosen alt/HH |
| 2 Shared recovery | FAIL | max\|err\|=0.1411 (beta_E_drgn4), thr=0.05 |
| 3 Group-specific | FAIL | thr=0.1 |
| 4 Two-start | FAIL | max\|warm-cold\|=3.700e+00, thr=1e-06 |
| 5 Hessian PD | FAIL | min_eig=-7.861e-01; NON-IDENTIFIED — Hessian non-PD (1 non-positive eigenvalue(s)); first bad direction loads on: theta_l_m (0.99) |
| 6 Contamination | DONE | see JSON |

**Checks 1-5: NOT all pass.**

### Check 3 blocks

| Block | max\|err\| | PASS |
|---|---|---|
| sm_leisure | 0.3366 | FAIL |
| sf_leisure | 0.3611 | FAIL |
| theta_c_singles | 0.0696 | PASS |
| m_leisure | 0.5245 | FAIL |
| f_leisure | 0.2474 | FAIL |
| beta_ll |  | PASS |

### Full JSON

```json
{
  "spec": "joint_pooled_v1_bll0",
  "n_params": 48,
  "n_hh": {
    "sm": 2243,
    "sf": 2764,
    "cou": 7438
  },
  "couples_alts": 401,
  "check1": {
    "passed": true
  },
  "check2": {
    "max_err": 0.14109634996147102,
    "worst": "beta_E_drgn4",
    "thresh": 0.05,
    "passed": false,
    "ll": 49702.86121887872,
    "max_grad": 21.20360508607815,
    "theta_hat": [
      0.37170227280683943,
      0.2334665225919517,
      0.06715148587046979,
      -0.4856852910771771,
      0.5505186130217923,
      -0.013017699740931487,
      0.12633608217504397,
      0.537970925005357,
      -0.44811823516913385,
      -0.10780981933781042,
      1e-06,
      -0.021491804228411283,
      0.0326217082843278,
      -0.3,
      1.9300529292148187,
      -0.25259976321850813,
      0.477804178789637,
      0.6800176592010758,
      -1.003505356804702,
      -1.144039382394561,
      -1.3388763145838878,
      -0.6545003593175271,
      0.9896849239593046,
      -1.4560671909591674,
      -1.7310673823382385,
      0.08455974704361165,
      0.36478304879775025,
      0.6627773566643961,
      0.12745904842809505,
      0.2789068450212969,
      0.16101727361792093,
      -0.07452719939831753,
      0.08946309120983494,
      -0.18498806264028253,
      -0.19048127578992832,
      -0.7278142262742071,
      -1.4658072643009539,
      -2.2890990797171176,
      0.2037282350554055,
      0.06762256357952315,
      -0.40413839330466444,
      0.8435862272761373,
      2.1852549947144038,
      -0.013317802120433566,
      0.3434813504487902,
      0.32591854318275715,
      -0.07556100818279245,
      0.4156569824812728
    ]
  },
  "check3": {
    "blocks": {
      "sm_leisure": {
        "n": 4,
        "max_err": 0.3365805757317008,
        "worst": "theta_l_sm",
        "passed": false
      },
      "sf_leisure": {
        "n": 5,
        "max_err": 0.3610793786650275,
        "worst": "theta_l_sf",
        "passed": false
      },
      "theta_c_singles": {
        "n": 1,
        "max_err": 0.06962489187898413,
        "worst": "theta_c_singles",
        "passed": true
      },
      "m_leisure": {
        "n": 7,
        "max_err": 0.5244809045290211,
        "worst": "theta_l_m",
        "passed": false
      },
      "f_leisure": {
        "n": 8,
        "max_err": 0.24740157642203403,
        "worst": "beta_l_nkids_f",
        "passed": false
      },
      "beta_ll": {
        "n": 0,
        "max_err": null,
        "passed": true
      }
    },
    "thresh": 0.1,
    "passed": false
  },
  "check4": {
    "max_diff": 3.7,
    "thresh": 1e-06,
    "passed": false,
    "ll_warm": 49702.86121887872,
    "ll_cold": 49703.23971204263,
    "disagreed": [
      [
        "theta_l_m",
        3.7
      ],
      [
        "beta_l_age_m",
        0.3319591729062605
      ],
      [
        "beta_l_age2_m",
        0.06833947030343368
      ],
      [
        "theta_l_sm",
        0.03487553143668126
      ],
      [
        "theta_l_sf",
        0.01797136952991857
      ],
      [
        "theta_l_f",
        0.015774332216381692
      ],
      [
        "beta_h_lh",
        0.015070876231180419
      ],
      [
        "beta_l_nkids_sf",
        0.013071754742219333
      ],
      [
        "beta_l0_sf",
        0.011967226670816511
      ],
      [
        "beta_l_nkids_f",
        0.011413508551102902
      ],
      [
        "beta_l0_f",
        0.011395382243813534
      ],
      [
        "beta_l0_sm",
        0.00910902782580525
      ],
      [
        "beta_l_age_sm",
        0.008619668681525389
      ],
      [
        "beta_l_age2_f",
        0.008226439256545759
      ],
      [
        "beta_E",
        0.005942508676082259
      ]
    ]
  },
  "check5": {
    "pd": false,
    "min_eig": -0.7860853803350892,
    "n_nonpos": 1,
    "verdict": "NON-IDENTIFIED \u2014 Hessian non-PD (1 non-positive eigenvalue(s)); first bad direction loads on: theta_l_m (0.99)",
    "passed": false
  },
  "check6": {
    "beta_e_dgp": {
      "sm": -1.94,
      "sf": -1.0,
      "cou": -0.71
    },
    "beta_e_pwavg": -1.2166666666666666,
    "beta_e_contaminated": -0.5453362052670071,
    "beta_e_clean": -1.144039382394561,
    "inside_range": false,
    "pref_displacement": {
      "sm_leisure": 0.18568529107717713,
      "sf_leisure": 1.0935111039814607,
      "theta_c_singles": 0.3835784924346078,
      "m_leisure": 0.059737667314280596,
      "f_leisure": 0.5036458175907588
    }
  },
  "all_checks_1_5_pass": false
}
```
