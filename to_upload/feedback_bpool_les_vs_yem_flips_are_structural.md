---
name: feedback-bpool-les-vs-yem-flips-are-structural
description: The ~1.5% participation flips on chosen-row deciders are 100% explained by les vs yem survey disagreement. Do not flag as a build bug.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 917be933-6042-40a4-8ac3-d50e42fd85f4
---

# Chosen-row participation flips are structural, not a bug

Observed across all 6 priced FR B-pool files (2015/2016/2017 × singles/couples):
**280 / 18,283 decider chosen rows (1.5%) have working_state(yem>0) disagreeing with
working_state(observed yem>0)**. Every single one of the 280 falls into one of two
clean definitional buckets:

| Pattern | n | les_obs | yem_obs | lhw_obs | Why the B-pool is right |
|---|---:|---|---|---|---|
| A1: obs nonworker → chosen worker | 102 | 3 (Employee) | 0 | >0 | Employee with positive hours but zero recorded earnings (survey gap). B-pool recovers via `lhw × yivwg`. |
| A2: obs worker → chosen nonworker | 178 | 5 or 7 (Unempl/Inactive) | >0 | 0 | Unemployed/inactive with residual end-of-year earnings. B-pool correctly uses `lhw=0` → non-worker. |

`les_ch == les_obs` in every flipped row — labour status is preserved exactly. The
B-pool's working-state rule is `les ∈ {1,2,3,10} AND lhw > 0`, which is more
robust than the naive `yem > 0` test that an external validator might use.

## How to apply

- A new validator showing ~280 chosen-row participation flips → expected, not a bug.
- The 102 A1 cases are why couples files show median |Δ ils_dispy| ~ €130 against
  any naive baseline that uses canonical survey `yem`.
- See `validate_chosen_flips.py` for the read-only proof.

See [[reference-drd-fr-input-variables]] for the authoritative `les` codes.
