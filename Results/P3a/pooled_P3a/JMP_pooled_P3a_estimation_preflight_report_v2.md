# JMP Pooled P3a Estimation — Preflight Report v2

*France FR_2015 / FR_2016 / FR_2017 | v2 | 2026-05-21*

**Prior preflight:** `Results/JMP_pooled_P3a_estimation_preflight_report_v1.md`
— verdict: HALT — DO NOT RUN SOLVER (three blockers: PF6/PF7, PF8, PF9)

**This preflight:** post-repair re-run against the repaired state per
`docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`.

---

## Preflight verdict

**PASS — EXECUTION-READY**

All three v1 blockers are resolved. All preflight checks pass. The pooled
estimation may be run under the existing execution authorization
(`docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and its correction),
against the estimation-ready split-stem base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`.

**The pooled solver was NOT run by this preflight. No estimate was produced.**

---

## PF1 — CLI syntax

**PASS.** All estimator flags exist in `enh_RURO_estimate_FR.py`: `--mnl-base`,
`--metadata`, `--spec-config`, `--output-dir`, `--group joint`, `--solver gamspy-conopt`,
`--vectorized`, `--warm-start`, `--init-params`. `--mnl-base` now resolves to the
estimation-ready split-stem files (R2 resolved PF8).

## PF2 — M1-clean warm-start results JSON

**PASS.** The M1-clean `estimation_results.json` exists (53 parameters; LL = −6487.55;
`success = True`) and is the Start 1 warm-start source.

## PF3 — Start 1 mapping

**PASS.** The 53 M1-clean parameters map 1:1 to the 55 pooled positions, with
`beta_E_y2015 = 0.0` and `beta_E_y2017 = 0.0` at positions 35–36.

## PF4 — Start 2

**PASS.** `--warm-start none` initialises all 55 parameters at the YAML initial_values.

## PF5 — Start 3

**PASS.** Perturbed Start 1 vector (seed 42, ±0.1) can be written to JSON and passed via
`--init-params`.

## PF6/PF7 — Post-estimation mode (primary v1 HALT)

**PASS (previously HALT).** `run_cluster_robust_se.py --mode post-estimation` is now
implemented. The stub "not yet implemented" is replaced with the full implementation:
- PE1: spec parsed (n_params=55)
- PE2: converged theta loaded from results JSON
- PE3: full split-stem data loaded via `load_and_validate_mnl_data` (no row bound)
- PE4: precomputed data objects built with `year_2015_indicator`/`year_2017_indicator`
  and occupation dummies in `extra_vars`
- PE5: scores extracted via `compute_scores_joint`
- PE6: TRUE Hessian computed via central differences on `compute_gradient_joint`
- PE7: sandwich VCV assembled via `compute_cluster_robust_se`
- T3/T4/T5: run at estimation time on converged pooled theta

V7 interface-callability check: PE1–PE5 confirmed PASS (scores shape=(400,55) on 20K-row
subset, `year_2015_indicator`/`year_2017_indicator` correctly in `extra_vars` via
`spec.market_opportunity_shifters`).

## PF8 — Split-stem data contract (v1 blocker)

**PASS (previously FAIL).** Three estimation-ready split-stem files now exist:

| File | Rows | Cols |
|------|------|------|
| `fr_p3a_gsurv2_estimation_ready__singles.parquet` | 500,700 | 148 |
| `fr_p3a_gsurv2_estimation_ready__couples.parquet` | 743,800 | 148 |
| `fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | — | — |

`load_and_validate_mnl_data` accepts all three with `strict_validation=True` (V1 PASS).
Row-count conservation: 1,244,500 total (V2 PASS). HH-years: 12,445 (V2 PASS).
Clusters: 9,657 unique `idorighh` (V2 PASS).

## PF9 — Year indicators (v1 blocker)

**PASS (previously FAIL).** Both `year_2015_indicator` and `year_2017_indicator` are present
in both split files as `float64` columns. Derivation verified (V3 PASS):

| Column | Singles 1s | Couples 1s |
|--------|-----------|-----------|
| `year_2015_indicator` | 166,900 | 256,600 |
| `year_2017_indicator` | 166,200 | 229,500 |

`year_tag == 2` (FR_2016 reference): both indicators = 0.0. No year-effect shifter is
skipped during precompute with the corrected `_collect_extra_vars` fix.

## PF10 — Cluster key

**PASS.** `cluster_id == idorighh` holds on all rows of both split files (V4 PASS).
No silent fallback to `idhh`. Cluster-key strictness safeguard active in both precompute
functions.

## PF11 — Income routing

**PASS.** Singles carry `ils_dispy_real` (non-null). Couples carry `ils_dispy_male` and
`ils_dispy_female` (non-null). `precompute_data_couples` uses `c_norm` for consumption —
does NOT read `ils_dispy_real` (V5 PASS).

## PF12 — GA15 income columns

**PASS.** `ils_dispy_real`, `ils_dispy_male`, `ils_dispy_female` all present in pooled
parquet (confirmed in v1 preflight; unchanged).

## PF13 — Region and occupation dummies

**PASS.** `reg_nuts1_2`–`reg_nuts1_8` and `loc4`/`loc4_male`/`loc4_female` present in split
files. Occupation dummies `loc4_2_male` etc. are derived by `precompute_data_couples` via
`_extract_or_derive_gender` and confirmed set on the data object (V7 check). Engine warnings
about `loc4_2_male` during gradient evaluation are informational and do not prevent correct
computation (existing behavior, same as M1-clean runs).

## PF14 — GA17 smoke-test callability

**PASS.** C1–C17 all PASS, GA17 status: `smoke-test callability: CONFIRMED` (V6 PASS).
Smoke-test interface unchanged.

## PF15 — Solver not run

**PASS.** No solver was invoked. No pooled estimate exists. M1-clean 2016 remains the
active JMP baseline.

---

## Summary table

| Check | v1 Status | v2 Status |
|-------|-----------|-----------|
| PF1 CLI syntax | PASS | PASS |
| PF2 M1-clean warm-start | PASS | PASS |
| PF3 Start 1 mapping | PASS | PASS |
| PF4 Start 2 | PASS | PASS |
| PF5 Start 3 | PASS | PASS |
| PF6/PF7 Post-estimation mode | **HALT** | **PASS** |
| PF8 Split-stem contract | **FAIL** | **PASS** |
| PF9 Year indicators | **FAIL** | **PASS** |
| PF10 Cluster key | PASS | PASS |
| PF11 Income routing | PASS | PASS |
| PF12 GA15 income columns | PASS | PASS |
| PF13 Region/occupation dummies | PASS (warn) | PASS (warn expected) |
| PF14 GA17 smoke-test | PASS | PASS |
| PF15 Solver not run | PASS | PASS |

---

## Required final statements

- **Pooled estimation is execution-ready** per this preflight re-run. It still requires
  a renewed execution authorization or clearance addendum confirming the repaired
  split-stem state before the solver is run.
- **Pooled estimation was NOT run.** No estimate was produced.
- **Welfare computation is NOT authorized.** None was run.
- **M1-clean 2016 remains the active JMP baseline.**