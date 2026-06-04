# RURO Welfare — Stage Four, Increment Four-A: post-Two-O baseline policy + welfare-pricing config preparation

**Date:** 2026-06-04
**Increment:** STAGE FOUR, INCREMENT FOUR-A only — declare the post-Two-O baseline policy and
prepare the welfare-pricing configuration, gated on a metadata/path readiness check.
**Status:** complete. **Baseline policy declared; welfare-pricing config block added
(`welfare.stage4`); metadata/path readiness gate PASSES (overall READY = True).** Prices
nothing, swaps nothing, promotes nothing.

> **No production parquet swapped, overwritten, moved, or deleted; no baseline promoted to
> canonical; no re-estimation; no `V_i^dir`; no redrawn-node pricing; no `W^3` promotion;
> nothing beyond `W^3`.** This increment is declarative + config + a read-only path check. Not
> committed automatically.

---

## Task 1 — baseline policy memo (post-Two-O)

The Two-O dispositive test is settled: **OPTION A CONFIRMED** (Three-B2 REAL-DATA IMMATERIAL +
Three-B3 Check-5 PD at 901, `is_final = True`). The post-Two-O baseline policy is therefore:

1. **Estimation canonical is unchanged.** The canonical estimate remains
   `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` (the certified 47-param
   `joint_pooled_v1_bll0_tlmpin` MLE). It is **not** replaced by the rebuilt real-data estimate
   (`theta_hat_rebuilt_realdata_901_v1.csv`), which Three-B2 showed moves by ≤ ~1 % of a
   certified clustered SE.

2. **Certified production priced / engine-ready files are NOT swapped in this increment.** The
   certified engine-ready stem `fr_p3a_bpool_engine_ready` and the production assembled priced
   files remain the production artifacts, untouched.

3. **The staged reproducible baseline is authorised ONLY as the welfare-pricing reference
   candidate, not canonical production.** The Three-B1 staged engine-ready stem
   (`fr_p3a_bpool_engine_ready_staged_threeB1`) — the Two-O Option-A instrument — is the
   reference the welfare-pricing path will use for population-faithful existing-node work,
   because it is the internally coherent, determinism-validated, component-correct baseline.
   Its `role` in config is `welfare_pricing_reference_candidate_only`.

4. **Any production swap remains a supervisor-level SEPARATE authorisation.** Nothing in this
   increment authorises swapping the staged baseline into production, promoting it to canonical,
   or replacing the certified estimate. `production_swap_authorised: false`,
   `promote_staged_to_canonical: false` in config.

The metadata gate confirms these invariants hold:
`estimation_canonical_is_certified_theta_hat = True`, `production_swap_authorised = False`,
`promote_staged_to_canonical = False`.

---

## Task 2 — welfare-pricing config preparation

Added the `welfare.stage4` block to `scripts/welfare/configs/welfare_stage1_w3.yaml` (the
welfare source reads it; nothing is hardcoded). It records:

| element | value |
|---|---|
| staged engine-ready stem | `fr_p3a_bpool_engine_ready_staged_threeB1` (singles 101 + couples 901) |
| staged priced dir | `staging_threeB1_priced` (assembled staged priced long files) |
| staged chunk dir | `staging_twoN` (Two-N per-chunk staged parquet + completion markers) |
| pinned EUROMOD pairing | from `run_bpool_euromod_chunk._SYSTEM_PAIRING` (2015→FR_2014, 2016→FR_2015, 2017→FR_2016) |
| pinned CPI `phi_y` | from `run_bpool_euromod_chunk._CPI` (2015:1.0031, 2016:1.0, 2017:0.9886) |
| pinned input schema | from `run_bpool_euromod_chunk._RAW_SCHEMA` (122/124/128 cols) + Three-A pinned config |
| **population-batch requirement** | `population_batch_required: true` — Two-L/Two-N: means-tested benefits need the representative population in the EUROMOD batch; isolated/bounded per-node batches are **unfaithful**; price at production-chunk (population) scale |
| **no-double-deflation rule** | `no_double_deflation: true` — EUROMOD inputs stay nominal + system-year consistent; the 2016-real deflation is estimator-facing only; post-EUROMOD CPI `phi_y` applied once (`ils_dispy_real = ils_dispy × phi`); counterfactual wages expressed in the draw's nominal frame before pricing, returned to real via `phi_y` |

The pinned EUROMOD references are **sourced from the build module**, not re-hardcoded, so the
welfare path matches the build exactly. The block also carries explicit `scope_guards`
(`prices_redrawn_node`, `computes_v_dir`, `promotes_w3`, `swaps_production`, `re_estimates` —
all `false`) for the welfare source to assert.

---

## Task 3 — readiness gate for population-faithful existing-node parity (metadata/path ONLY)

A **read-only** gate: confirms every referenced staged path exists and matches the recorded
Three-A / Three-B1 provenance. **It prices nothing and writes no parquet.**

| check | result |
|---|---|
| staged singles engine-ready | exists; **505,707 rows**, 5,007 HH, **101 alts uniform** |
| staged couples engine-ready | exists; **6,701,638 rows**, 7,438 HH, **901 alts uniform** |
| staged `__mnlmeta.json` | exists |
| staged priced dir (`staging_threeB1_priced`) | exists; 6 assembled priced parquet |
| staged chunk dir (`staging_twoN`) | exists; 21 chunk parquet + 21 completion markers |
| staged stem identity matches Three-B1 | ✓ |
| singles/couples rows match Three-B1 | ✓ / ✓ |
| singles/couples alts match Three-B1 (101 / 901) | ✓ / ✓ |
| Three-A determinism / component coherence | ✓ / ✓ |
| Three-A validated-reproducible-candidate | ✓ |
| pinned EUROMOD config + build-module constants resolvable | ✓ |
| estimation canonical = certified `theta_hat` | ✓ |
| production swap authorised / promote to canonical | **False / False** |

**OVERALL READY (metadata/path) = True.** All five sub-gates pass
(`staged_engine_ready_ok`, `staged_paths_ok`, `provenance_xref_ok`, `pinned_refs_ok`,
`baseline_policy_ok`). The referenced staged baseline is path-consistent and provenance-matched
for the later (separately authorised) population-faithful existing-node parity work.

This gate is **metadata/path only**; it does not run any EUROMOD pricing, does not price any
existing or redrawn node, and does not compute any welfare quantity.

---

## Files

- **Driver:** `scripts/welfare/run_stage4a_baseline_policy.py` (reads `welfare.stage4` +
  Three-A/B1/B3 provenance; runs the metadata/path readiness gate). Ruff-clean; prices nothing.
- **Config:** `scripts/welfare/configs/welfare_stage1_w3.yaml` — added the `welfare.stage4`
  block (baseline policy + welfare-pricing reference + pinned EUROMOD refs + pricing discipline +
  scope guards). YAML validated.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage4a_baseline_policy.json` (policy +
  config summary + readiness gate).
- **Unchanged:** certified `theta_hat_realdata_901_v1.csv`, rebuilt
  `theta_hat_rebuilt_realdata_901_v1.csv`, certified engine-ready stem
  `fr_p3a_bpool_engine_ready`, production priced files, and the staged baseline.

## Explicit scope statement

No production swap; no canonical promotion; no `V_i^dir`; no redrawn-node pricing; no `W^3`
promotion; no re-estimation; nothing beyond `W^3`. This increment declares the post-Two-O
baseline policy, prepares the welfare-pricing config, and runs a metadata/path readiness gate
only. Pricing the existing nodes at population scale, and anything involving redrawn nodes
(`V_i^dir`) or `W^3` promotion, remain separate authorisations.
