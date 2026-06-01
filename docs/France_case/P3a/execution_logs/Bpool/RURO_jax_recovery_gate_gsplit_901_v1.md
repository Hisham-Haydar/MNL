# JAX synthetic recovery gate — joint_pooled_v1_bll0_tlmpin_gsplit

**Params:** 49  **Couples alts:** 901  **HH:** sm=2243 sf=2764 cou=7438

> Synthetic recovery on the validated JAX backend (use_actual_choice=True). Same 6 checks / thresholds / G3b verdict as the CONOPT gate; JAX optimizer + exact jax.hessian instead of CONOPT.

| Check | Result | Detail |
|---|---|---|
| 1 Synthetic DGP | PASS | one chosen alt/HH |
| 2 Shared recovery | FAIL | max\|err\|=0.4701 (beta_E_drgn8), thr=0.05 |
| 3 Group-specific | FAIL | thr=0.1 |
| 4 Two-start | FAIL | max\|warm-cold\|=1.114e-04, thr=1e-06 |
| 5 Hessian PD | PASS | min_eig=1.532e+00; SEPARATELY IDENTIFIED |
| 6 Contamination | DONE | see JSON |

**Checks 1-5: NOT all pass.**

### Check 3 blocks

| Block | max\|err\| | PASS |
|---|---|---|
| sm_leisure | 0.2487 | FAIL |
| sf_leisure | 0.4140 | FAIL |
| theta_c_singles | 0.0556 | PASS |
| m_leisure | 0.0716 | PASS |
| f_leisure | 0.1217 | FAIL |
| beta_ll |  | PASS |
| relaxed_gsplit | 1.2287 | FAIL |

### Relaxed (gender-split) param recovery

The gsplit-specific criterion: each relaxed param must recover to tolerance (thr=0.1) on synthetic data — the gender split must be IDENTIFIABLE, not merely real-data-fittable.

| Param | true | recovered | \|err\| | PASS |
|---|---|---|---|---|
| beta_E_m | -0.3600 | -0.2127 | 0.1473 | FAIL |
| beta_E_f | -1.0000 | -0.2119 | 0.7881 | FAIL |
| beta_h_pt2_m | -1.1900 | +0.0387 | 1.2287 | FAIL |
| beta_h_pt2_f | +0.3700 | -0.1144 | 0.4844 | FAIL |

**Relaxed params recovery: NOT all recover.**

### beta_l0_m (couples-male leisure intercept)

`beta_l0_m = +0.03545` — **interior** (floor=1e-06). theta_l_m is pinned, so beta_l0_m at its floor is acceptable (weakly-identified intercept).

### Certification verdict

- Check 5 PD @ MLE: **PASS** (min_eig=1.532e+00)
- Interior MLE (no bound binds): **YES** (binding: none)
- Relaxed params recover: **NO**

>> **NOT CERTIFIED** — Check 5 not PD OR relaxed params do not recover; the relaxation introduced an identification problem the real-data fit masked. Diagnose before the baseline is final.

---

## Interpretation — the gender split does NOT recover on synthetic data (STOP)

**Bottom line.** Check 5 is PD at 901 (min_eig +1.532, 0 non-positive eigenvalues,
interior MLE, beta_l0_m interior at +0.0354) — so the 49-param model is *locally*
identified. **But three of the four relaxed gender-split params do not recover on
synthetic data, and the non-recovery is a TIGHT-SE BIAS, not a wide-SE weak-ID
phenomenon.** Per the gate's stop condition, the gsplit baseline is **NOT certified**;
the split must be diagnosed before it is final for the paper.

**Why this is NOT the benign 47-param "weak-curvature, wide-SE" story.** In the
certified 47-param 901 gate, the Check-2/3 residuals sat in the *flattest* Hessian
directions (singles-leisure) — wide SEs, errors comparable to those SEs, identified
but imprecise. Here the opposite holds. A post-MLE Hessian diagnostic (exact
`jax.hessian` at the warm MLE, **same seed 20260530**, smallest eigenvalues
`[1.532, 5.11, 5.44, 9.59, ...]` — reproduces the gate's PD verdict) shows the
relaxed params are **well-curved**, yet recover **many SEs from truth**:

| Param | true | recovered | \|err\| | SE(Hessian) | err / SE | curvature H_ii |
|---|---|---|---|---|---|---|
| beta_E_m | -0.36 | -0.213 | 0.147 | 0.228 | 0.65 (OK) | 2.32e2 (> median) |
| beta_E_f | -1.00 | -0.212 | 0.788 | 0.223 | **3.53** | 1.70e2 |
| beta_h_pt2_m | -1.19 | +0.039 | 1.229 | 0.064 | **19.2** | 2.50e2 |
| beta_h_pt2_f | +0.37 | -0.114 | 0.484 | 0.063 | **7.7** | 2.57e2 |

(median |H_ii| over all 49 params = 2.30e2; the relaxed params are AT or ABOVE it,
i.e. among the better-curved directions — not flat.)

**What this means.** `beta_h_pt2_m` recovers at **+0.039 against a true −1.19**
(wrong sign, ~19 SE away); `beta_h_pt2_f` and `beta_E_f` are 3.5–7.7 SE off. The
optimizer lands **confidently (tight SE) at the WRONG gender-split values**. A PD
Hessian certifies *local* curvature; it cannot detect that the synthetic likelihood
optimum sits far from the DGP truth. Both starts reach the same basin (Check 4
negLL agree to 9 sig figs), so this is not a multi-modality / convergence artefact —
it is a **genuine identification failure of the gender split** that the PD Hessian and
the real-data fit both mask. The flattest Hessian directions remain singles-leisure
(`theta_l_sm/sf`); the relaxed params do not load the bottom eigenvectors at all,
confirming their non-recovery is *bias*, not flatness.

**Why the real-data fit (commit 0b16478, PD min_eig +0.408) masked it.** Real-data
estimation only asks "is there an interior PD optimum?" — yes. It never asks "does the
estimated split equal a known truth?" The synthetic gate is the only test that poses
that question, and the split fails it. The LR pooling test (beta_E LR=65.7,
beta_h_pt2 LR=206.6) rejected *pooling* — it showed male≠female improves in-sample
fit — but rejecting pooling is NOT the same as the two gendered coefficients being
*separately recoverable*. The data prefers a split; it cannot pin *which* split.

**This does NOT invalidate the 47-param certified baseline** (`joint_pooled_v1_bll0_tlmpin`,
RURO_jax_recovery_gate_tlmpin_901_v1.md) — that gate passed Check 5 and its shared
beta_E / beta_h_pt2 are recovered. It is specifically the *gendered relaxation* that
is not synthetic-identifiable at 901.

### Recommended diagnosis before the gsplit baseline can be final

1. **Per-param profile likelihood** for `beta_h_pt2_m`, `beta_h_pt2_f`, `beta_E_f`
   on synthetic data: is the profile genuinely single-peaked at the wrong value
   (hard non-ID / DGP-vs-fit mismatch), or is there a long flat shoulder the tight
   marginal SE hides (correlated ridge)?
2. **Pairwise correlation** of the 4 relaxed params in `cov = H^-1` (are
   beta_h_pt2_m and beta_h_pt2_f near-perfectly anti-correlated, i.e. only their
   *sum* or a contrast is identified?).
3. **theta_star provenance**: the 4 relaxed true values come from the spec
   `initial_values` (the real-data LR point estimates), not a synthetic-truth CSV.
   Confirm the DGP draw used exactly those values (it did — `_full_theta` inserts
   them by name) so the "truth" is well-defined; then the non-recovery is real.
4. **Consider a less aggressive relaxation**: split only `beta_h_pt2` (the larger
   LR signal) and keep `beta_E` pooled, or split only on the sign-flip channel, and
   re-gate — to locate which gendered coefficient breaks recovery.

Until (1)–(4) resolve, the **47-param baseline remains the certified spec**; the
49-param gsplit is an in-sample improvement that is **not synthetic-identified** and
should not be reported as the paper baseline without this caveat.

### Full JSON

```json
{
  "spec": "joint_pooled_v1_bll0_tlmpin_gsplit",
  "n_params": 49,
  "n_hh": {
    "sm": 2243,
    "sf": 2764,
    "cou": 7438
  },
  "couples_alts": 901,
  "check1": {
    "passed": true
  },
  "check2": {
    "max_err": 0.4701468209694469,
    "worst": "beta_E_drgn8",
    "thresh": 0.05,
    "passed": false,
    "ll": 54366.325834421084,
    "max_grad": 0.004537927225669591,
    "theta_hat": [
      0.335333783340699,
      0.2533281691322983,
      0.07109178960946787,
      -0.597328627896941,
      0.4533029661729975,
      -0.042199788004926984,
      0.11565496977364141,
      0.49998474038421803,
      -0.3952249954107514,
      -0.09380067745448337,
      0.03544650464006419,
      -0.08157190157669046,
      -0.03900721148845757,
      1.6829826185458567,
      -0.2634895641834311,
      0.20130599304226784,
      0.5542822385536397,
      -0.7462897402614243,
      -0.21272154014716685,
      -0.2118755772123167,
      -1.3071488177035024,
      0.03869746841703866,
      -0.11437658762906265,
      1.0045492441945305,
      -1.5302142067868383,
      -1.747099101321415,
      0.319676853249753,
      0.4521892338104337,
      0.9228243300012624,
      0.5143542119898924,
      0.3372147974495349,
      0.2391401954278006,
      0.4620672472373374,
      0.2699444568439316,
      -0.08776123475896935,
      -0.02851520347965178,
      -0.6556754643372183,
      -1.5642841040982707,
      -2.3034073877976793,
      0.1626546604352869,
      0.060909571732300286,
      -0.4369383509400523,
      0.8170305421687611,
      2.202681300001225,
      -0.017211488396632682,
      0.34986823838914405,
      0.2754952173681579,
      -0.05226763508614722,
      0.4191126056014973
    ]
  },
  "warm_converged": true,
  "warm_bound_binding": [],
  "beta_l0_m": {
    "value": 0.03544650464006419,
    "floor": 1e-06,
    "at_floor": false,
    "status": "interior"
  },
  "check3": {
    "blocks": {
      "sm_leisure": {
        "n": 4,
        "max_err": 0.24872967898108284,
        "worst": "beta_l0_sm",
        "passed": false
      },
      "sf_leisure": {
        "n": 5,
        "max_err": 0.41397261842340993,
        "worst": "theta_l_sf",
        "passed": false
      },
      "theta_c_singles": {
        "n": 1,
        "max_err": 0.05561574999565707,
        "worst": "theta_c_singles",
        "passed": true
      },
      "m_leisure": {
        "n": 6,
        "max_err": 0.07164602856071366,
        "worst": "beta_l_age_m",
        "passed": true
      },
      "f_leisure": {
        "n": 8,
        "max_err": 0.12166615577459788,
        "worst": "beta_l_nkids_f",
        "passed": false
      },
      "beta_ll": {
        "n": 0,
        "max_err": null,
        "passed": true
      },
      "relaxed_gsplit": {
        "n": 4,
        "max_err": 1.2286974684170386,
        "worst": "beta_h_pt2_m",
        "passed": false
      }
    },
    "thresh": 0.1,
    "passed": false
  },
  "relaxed_recovery": {
    "thresh": 0.1,
    "params": {
      "beta_E_m": {
        "true": -0.36,
        "recovered": -0.21272154014716685,
        "abs_err": 0.14727845985283314,
        "passed": false
      },
      "beta_E_f": {
        "true": -1.0,
        "recovered": -0.2118755772123167,
        "abs_err": 0.7881244227876834,
        "passed": false
      },
      "beta_h_pt2_m": {
        "true": -1.19,
        "recovered": 0.03869746841703866,
        "abs_err": 1.2286974684170386,
        "passed": false
      },
      "beta_h_pt2_f": {
        "true": 0.37,
        "recovered": -0.11437658762906265,
        "abs_err": 0.48437658762906266,
        "passed": false
      }
    },
    "all_passed": false
  },
  "check4": {
    "max_diff": 0.00011143806042168691,
    "thresh": 1e-06,
    "passed": false,
    "ll_warm": 54366.325834421084,
    "ll_cold": 54366.32583442365,
    "disagreed": [
      [
        "theta_l_sm",
        0.00011143806042168691
      ],
      [
        "beta_l0_sm",
        3.700130451617101e-05
      ],
      [
        "theta_l_sf",
        3.427502874453481e-05
      ],
      [
        "beta_l_age_sm",
        2.8962146983668724e-05
      ],
      [
        "beta_l_nkids_sf",
        2.883221323174423e-05
      ],
      [
        "beta_E_f",
        1.4873960815092735e-05
      ],
      [
        "beta_E_m",
        1.3044925896904536e-05
      ],
      [
        "beta_E_drgn6",
        1.2809432369698115e-05
      ],
      [
        "beta_E_drgn7",
        1.2177230426846375e-05
      ],
      [
        "beta_E_drgn2",
        1.1878206081672449e-05
      ],
      [
        "beta_E_drgn8",
        1.1199222098523531e-05
      ],
      [
        "beta_E_drgn3",
        9.969918695784674e-06
      ],
      [
        "beta_l0_sf",
        9.124456822107163e-06
      ],
      [
        "beta_l_age2_sm",
        8.03945079871915e-06
      ],
      [
        "beta_E_drgn5",
        7.185439391821369e-06
      ]
    ]
  },
  "check5": {
    "pd": true,
    "min_eig": 1.5319218421753928,
    "n_nonpos": 0,
    "verdict": "SEPARATELY IDENTIFIED",
    "passed": true
  },
  "check6": {
    "note": "beta_E not in spec"
  },
  "all_checks_1_5_pass": false
}
```
