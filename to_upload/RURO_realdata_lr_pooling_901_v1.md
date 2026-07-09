# Step 4 — LR pooling test (male vs female): joint_pooled_v1_bll0_tlmpin

> Deliverable 3. Tests whether beta_E and beta_h_pt2 can be pooled across male/female legs, or must be gender-specific. RESTRICTED = baseline (shared); RELAXED = coef split male/female (male legs = singles-male + couples-male; female legs = singles-female + couples-female), df=1. LR = 2(LL_relaxed - LL_restricted) ~ chi2(1).

**Restricted (baseline) negLL** = 238504.636097 (max|grad|=4.42e+01)  **Couples alts** = 901

| Param | shared | est_m | est_f | LR | p (chi2,df=1) | decision |
|---|---|---|---|---|---|---|
| beta_E | -0.7527 | -0.3586 | -0.9972 | 65.692 | 5.273e-16 | **relax to gender-specific** |
| beta_h_pt2 | -0.1037 | -1.1882 | 0.3734 | 206.563 | 7.723e-47 | **relax to gender-specific** |

### Notes

- Nesting check (relaxed negLL at the shared-value seed == restricted negLL) is reported per param in the JSON (`nesting_gap_at_seed`); it must be ~0 for the LR statistic to be valid.
- A REJECT means the baseline should relax that param to gender-specific (one increment, written reason) and be re-estimated before it is final. This script reports the decision; it does not mutate the certified spec.

## Full JSON

```json
{
  "spec": "joint_pooled_v1_bll0_tlmpin",
  "couples_alts": 901,
  "restricted_negLL": 238504.63609737591,
  "restricted_maxgrad": 44.20382666587236,
  "tests": [
    {
      "param": "beta_E",
      "shared_value": -0.7526509413610154,
      "relaxed_negLL": 238471.79023996263,
      "relaxed_maxgrad": 36.97912311415526,
      "nesting_gap_at_seed": 5.113543011248112e-08,
      "estimate_m": -0.358598057740476,
      "estimate_f": -0.9971798959110112,
      "LR_stat": 65.69171482656384,
      "df": 1,
      "p_value": 5.272705867882517e-16,
      "reject_pooling": true,
      "decision": "relax to gender-specific"
    },
    {
      "param": "beta_h_pt2",
      "shared_value": -0.10369457638006431,
      "relaxed_negLL": 238401.3547314288,
      "relaxed_maxgrad": 40.61355921737862,
      "nesting_gap_at_seed": 5.113543011248112e-08,
      "estimate_m": -1.1882061643994086,
      "estimate_f": 0.3733869331438328,
      "LR_stat": 206.562731894257,
      "df": 1,
      "p_value": 7.723410870267554e-47,
      "reject_pooling": true,
      "decision": "relax to gender-specific"
    }
  ]
}
```
