---
name: feedback-bpool-chosen-row-is-reconstructed
description: "The B-pool chosen alternative does NOT copy survey yem — it reconstructs yem = lhw × yivwg × 52/12 (≈ yem00, base pay). Do not flag this as a build bug."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 917be933-6042-40a4-8ac3-d50e42fd85f4
---

# B-pool chosen-row earnings are reconstructed, not copied

When validating the B-pool priced parquets against the canonical
`fr_{year}.parquet`, the chosen-row `yem` will **not** equal observed survey `yem`
for workers with overtime/bonuses. Specifically:

- `lhw_chosen == lhw_obs` exactly (hours anchor preserved)
- `yivwg_chosen == yivwg_obs` exactly (wage anchor preserved)
- `yem_chosen ≈ lhw × yivwg × (52/12)` to float precision

This corresponds to **`yem00`-equivalent** (base pay at imputed hourly wage), not survey
`yem` which includes `yemxp` = overtime + bonuses. Per the DRD
([[reference-drd-fr-input-variables]]): `yem = yem00 + yemxp`.

**Why:** the choice-set alternatives are all built from `lhw × yivwg`, so the chosen
alternative uses the same formula for internal consistency. The IS-corrected MNL
estimator needs comparable utility values across alternatives — copying survey `yem`
on the chosen row only would produce a non-stationary utility scale.

## How to apply

When a validation shows `|yem_chosen − yem_obs| > 0` on chosen-row deciders:
1. Confirm `lhw_chosen == lhw_obs` (hours anchor intact).
2. Confirm `yem_chosen == lhw_chosen × yivwg_chosen × 52/12` to float precision.
3. If both hold, the chosen row is the **reconstructed** alternative — not a bug.
4. The survey-vs-reconstruction gap is the documented Layer-1 divergence (overtime,
   multi-job income, bonuses absent from `lhw × yivwg`).

## What IS a bug

- `lhw_chosen != lhw_obs` on a same-state worker → hours anchor bug, must fix.
- `yem_chosen != lhw × yivwg × 52/12` on same-lhw worker → reconstruction bug, must fix.
- Participation flips beyond the les-vs-yem definitional ~1.5% (see
  [[feedback-bpool-les-vs-yem-flips-are-structural]]) → genuine flag-setting bug.

See `scripts/bpool/validate_chosen_anchors.py` and `validate_chosen_flips.py` for the
read-only diagnostics that distinguish these cases.
