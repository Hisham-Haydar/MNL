# JAX synthetic recovery gate — joint_pooled_v1_bll0

**Params:** 48  **Couples alts:** 401  **HH:** sm=2243 sf=2764 cou=7438

> Synthetic recovery on the validated JAX backend (use_actual_choice=True). Same 6 checks / thresholds / G3b verdict as the CONOPT gate; JAX optimizer + exact jax.hessian instead of CONOPT.

| Check | Result | Detail |
|---|---|---|
| 1 Synthetic DGP | PASS | one chosen alt/HH |
| 2 Shared recovery | FAIL | max\|err\|=0.1405 (beta_E_drgn4), thr=0.05 |
| 3 Group-specific | FAIL | thr=0.1 |
| 4 Two-start | FAIL | max\|warm-cold\|=8.336e+00, thr=1e-06 |
| 5 Hessian PD | FAIL | min_eig=-9.653e-02; NON-IDENTIFIED — Hessian non-PD (1 non-positive eigenvalue(s)); first bad direction loads on: theta_l_m (1.00) |
| 6 Contamination | DONE | see JSON |

**Checks 1-5: NOT all pass.**

### Check 3 blocks

| Block | max\|err\| | PASS |
|---|---|---|
| sm_leisure | 0.3407 | FAIL |
| sf_leisure | 0.3630 | FAIL |
| theta_c_singles | 0.0690 | PASS |
| m_leisure | 1.1609 | FAIL |
| f_leisure | 0.2453 | FAIL |
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
    "max_err": 0.14050624213088292,
    "worst": "beta_E_drgn4",
    "thresh": 0.05,
    "passed": false,
    "ll": 49702.78718230242,
    "max_grad": 32.074100350260196,
    "theta_hat": [
      0.36985655567326736,
      0.23250153984355448,
      0.06683854534343606,
      -0.481600184073166,
      0.5490027096527057,
      -0.012921742090145034,
      0.12604873030311192,
      0.5368634696819647,
      -0.44619126901663586,
      -0.10718092740324921,
      1e-06,
      -0.012389522651957072,
      0.014557603440820624,
      0.33642411261261396,
      1.9249434250203588,
      -0.25185545229901535,
      0.47626140904974024,
      0.6778698668251572,
      -1.0007668640959309,
      -1.1421586860355184,
      -1.3391091270329754,
      -0.6542411535764919,
      0.9902233697030551,
      -1.456509494125417,
      -1.7315052304153409,
      0.08503827885216517,
      0.3657450579014603,
      0.6633674644949842,
      0.1278937864453258,
      0.2793299384915266,
      0.1615674519154119,
      -0.07453007863421018,
      0.08943248284048172,
      -0.18502206191475273,
      -0.19040554933797454,
      -0.7279256159732697,
      -1.4655409057501723,
      -2.288919966755668,
      0.20391447244235225,
      0.0671692600681868,
      -0.40460636082093393,
      0.8431214127307656,
      2.185266241612865,
      -0.013318997049358598,
      0.34348597211927523,
      0.32588687526503624,
      -0.07554854199721814,
      0.41565859500134567
    ]
  },
  "warm_converged": false,
  "warm_bound_binding": [
    [
      "beta_l0_m",
      "lo"
    ]
  ],
  "check3": {
    "blocks": {
      "sm_leisure": {
        "n": 4,
        "max_err": 0.3406656827357119,
        "worst": "theta_l_sm",
        "passed": false
      },
      "sf_leisure": {
        "n": 5,
        "max_err": 0.3630063448175255,
        "worst": "theta_l_sf",
        "passed": false
      },
      "theta_c_singles": {
        "n": 1,
        "max_err": 0.0689959999444229,
        "worst": "theta_c_singles",
        "passed": true
      },
      "m_leisure": {
        "n": 7,
        "max_err": 1.1609050171416349,
        "worst": "theta_l_m",
        "passed": false
      },
      "f_leisure": {
        "n": 8,
        "max_err": 0.24525378404611536,
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
    "max_diff": 8.336424112612614,
    "thresh": 1e-06,
    "passed": false,
    "ll_warm": 49702.78718230242,
    "ll_cold": 49703.03923106349,
    "disagreed": [
      [
        "theta_l_m",
        8.336424112612614
      ],
      [
        "beta_l_age_m",
        1.013453485581594
      ],
      [
        "beta_l_age2_m",
        0.5648181907711192
      ],
      [
        "beta_l0_m",
        0.14400496870057775
      ],
      [
        "theta_l_sm",
        0.036017453775559705
      ],
      [
        "theta_l_f",
        0.02156137953285997
      ],
      [
        "theta_l_sf",
        0.017253771281846297
      ],
      [
        "beta_l0_sf",
        0.016472435138282893
      ],
      [
        "beta_h_lh",
        0.01590334941342575
      ],
      [
        "beta_l_nkids_f",
        0.014539089171196062
      ],
      [
        "beta_l_nkids_sf",
        0.014318384826938257
      ],
      [
        "beta_l0_sm",
        0.010663419370050775
      ],
      [
        "beta_l_age2_f",
        0.010220979893022397
      ],
      [
        "beta_l_age_sm",
        0.009128817462421251
      ],
      [
        "beta_E",
        0.0066273379222350215
      ]
    ]
  },
  "check5": {
    "pd": false,
    "min_eig": -0.0965285018414808,
    "n_nonpos": 1,
    "verdict": "NON-IDENTIFIED \u2014 Hessian non-PD (1 non-positive eigenvalue(s)); first bad direction loads on: theta_l_m (1.00)",
    "passed": false
  },
  "check6": {
    "beta_e_dgp": {
      "sm": -1.94,
      "sf": -1.0,
      "cou": -0.71
    },
    "beta_e_pwavg": -1.2166666666666666,
    "beta_e_contaminated": -0.5473989678591881,
    "beta_e_clean": -1.1421586860355184,
    "inside_range": false,
    "pref_displacement": {
      "sm_leisure": 1.431600184073166,
      "sf_leisure": 0.957740252240705,
      "theta_c_singles": 0.30116991796230164,
      "m_leisure": 0.8242368179315904,
      "f_leisure": 0.4542365826329702
    }
  },
  "all_checks_1_5_pass": false
}
```
