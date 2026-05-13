# RURO Stijn Occ M0 — MNL Validation Report v1

Date: 2026-05-13

## Verdict

**PASS — MNL files are estimation-ready for `M0_stijn_occ`.** All eight check
categories below pass with strong margins, and a completed estimation run
already exercised these files end-to-end without errors.

The previously-recommended likelihood smoke-test is **superseded**: the
completed run `run_2026-05-13_15-02-16` evaluated the joint log-likelihood
on these exact parquets and converged, which is a stronger signal than any
isolated likelihood probe could provide.

### Completed estimation run (post-validation citation)

| Field | Value |
| --- | --- |
| Specification | `stijn_occ_M0` |
| Wage spec | `vw` |
| Optimisation | `L-BFGS-B`, analytical gradient, GAMSPy backend |
| Joint log-likelihood | **−6,499.881** |
| Total observations | **425,300** |
| Total groups (households) | **4,253** |
| Parameter count | **52** |
| Convergence — singles_male | `SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)` |
| Convergence — singles_female | `SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)` |
| Convergence — couples | `SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)` |
| Total walltime | 158.3 s |
| Proposal correction | `-log(prior)` applied once per alternative |
| Opportunity centering | enabled within each choice set |

Source: `outputs/estimates/fr/spec/stijn_occ/gamspy/estimation_spec_stijn_occ_M0/run_2026-05-13_15-02-16/estimation_results.json` and `estimation_summary.txt`.

---

## Validation script

```text
U:/Desktop/Nizam_Hisham/MNL/Results/_validation_stijn_occ_M0.py
U:/Desktop/Nizam_Hisham/MNL/Results/_validation_stijn_occ_M0.json
```

The script is read-only against
`Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl`. It
does not call the estimator, the post-estimator, or the data rebuild
pipeline.

---

## 1. File existence

| File | Exists | Size | Last modified |
| --- | --- | --- | --- |
| `fr_2016_RURO_mnl__singles.parquet` | yes | 21,500,551 B (20.5 MB) | 2026-05-13 10:38 |
| `fr_2016_RURO_mnl__couples.parquet` | yes | 43,108,822 B (41.1 MB) | 2026-05-13 10:38 |
| `fr_2016_RURO_mnl__mnlmeta.json` | yes | 57,973 B | 2026-05-13 10:38 |

All three files are present, sized as expected for a `99 draws + 1 observed`
build, and time-stamped from the 2026-05-13 rebuild.

---

## 2. Sample structure

| Group | Rows | Columns | Households (`idhh`) | Alts/hh (min / median / max) | Distinct alt counts | Chosen column | n_hh with exactly 1 chosen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| singles | 167,600 | 75 | 1,676 | 100 / 100 / 100 | `[100]` | `is_chosen` | 1,676 |
| couples | 257,700 | 93 | 2,577 | 100 / 100 / 100 | `[100]` | `is_chosen` | 2,577 |

`is_chosen` sums to exactly **1** for every household in both files. No
households fail the "exactly one chosen alternative" invariant. Every
household has exactly `100` alternatives = 1 observed (draw=0) + 99
simulated.

---

## 3. Required M0 columns

### Singles

| Column | Status |
| --- | --- |
| `loc4` | present |
| `working` | present |
| `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` | all present |
| `prior`, `log_prior` | present |
| `idhh`, `is_chosen` | present |
| `loc4_2`, `loc4_3`, `loc4_4` (numeric one-hot dummies) | **absent in parquet — engine-derived from `loc4` at evaluation time** |

### Couples

| Column | Status |
| --- | --- |
| `loc4_male`, `loc4_female` | present |
| `working_male`, `working_female` | present |
| `log_q_E_male`, `log_q_H_male`, `log_q_W_male`, `log_q_Occ_male` | all present |
| `log_q_E_female`, `log_q_H_female`, `log_q_W_female`, `log_q_Occ_female` | all present |
| `prior`, `log_prior` | present |
| `idhh`, `is_chosen` | present |
| `loc4_{2,3,4}_male`, `loc4_{2,3,4}_female` | **absent in parquet — engine-derived from `loc4_*` at evaluation time** |

The `loc4_2/3/4(_male/_female)` one-hot indicator columns are intentionally
not materialised in the MNL parquets — the estimation engine builds them
from `loc4` (and `loc4_male`/`loc4_female`) on the fly when it constructs
each shifter's design matrix. The completed estimation run at
`run_2026-05-13_15-02-16` confirms the engine handles this correctly: all
12 `beta_occ_{2,3,4}_{sm,sf,cm,cf}` coefficients are estimated with finite
gradients and finite standard errors.

No required columns are missing on either file.

---

## 4. Occupation variation

Computed across **simulated + observed working alternatives** within each
household.

| Group | Households | Median distinct `loc4` | Mean | Min | Max | % hh with only 1 distinct |
| --- | --- | --- | --- | --- | --- | --- |
| singles | 1,676 | **4.0** | 4.004 | 4 | 5 | 0.0 % |
| couples_male | 2,577 | **4.0** | 4.012 | 4 | 5 | 0.0 % |
| couples_female | 2,577 | **4.0** | 4.001 | 3 | 5 | 0.0 % |

Every household in every group has at least 3 distinct `loc4` values
across its working alternatives — well above the identification floor of
≥ 2 the rebuild plan called for. The 12 group-specific occupation
coefficients are therefore identified.

### `loc4` support

Valid task-group support is `loc4 ∈ {1, 2, 3, 4}`. Two sentinel values
also appear in the data:

| Sentinel | Convention | Where observed |
| --- | --- | --- |
| `-1` | **Non-work** alternative. Hours = 0, wage = 0, occupation undefined. | All non-work rows. |
| `-2` | **Invalid / missing observed occupation** at the original baseline (draw = 0). The draw script's mode-imputation replaces `-2` with the pooled-mode task group when *sampling* working occupations for draws ≥ 1, but the observed draw = 0 row keeps the original `-2`. | 7 singles draw-0 rows, 31 couples-male draw-0 rows, 3 couples-female draw-0 rows. |

So the `Max distinct = 5` outliers come from the small set of households
where the observed (draw=0) `loc4` is `-2` and the 99 simulated working
draws cover all of `{1, 2, 3, 4}`. This is the expected behaviour, not a
data error. Working-alternative overall counts:

| loc4 | singles | couples_male | couples_female |
| --- | --- | --- | --- |
| -2 | 7 | 31 | 3 |
| 1 | 43,764 | 62,393 | 61,831 |
| 2 | 23,042 | 33,433 | 33,482 |
| 3 | 14,234 | 21,991 | 22,601 |
| 4 | 69,740 | 113,799 | 114,090 |

---

## 5. Prior invariants

| Invariant | Singles | Couples |
| --- | --- | --- |
| `min(prior)` | 7.819e-06 | 6.290e-11 |
| `n_prior ≤ 0` | **0** | **0** |
| `n_prior = NaN` | **0** | **0** |
| `max |log(prior) − log_prior|` | **0.000e+00** | **0.000e+00** |
| `n_rows`	with `|diff| > 1e-8` | 0 | 0 |
| Singles reconstruction: `log_prior == log_q_E + working·(log_q_H + log_q_W + log_q_Occ)` — max abs error | **0.000e+00** | — |
| Couples reconstruction: `log_prior == [male component] + [female component]` — max abs error | — | **0.000e+00** |
| `n_rows` with reconstruction error > 1e-8 | 0 | 0 |

All four invariants you asked for hold **exactly** (machine-precision
zero), on every row of both files (167,600 singles + 257,700 couples).

---

## 6. Non-work handling

Non-work alternatives (`working == 0` for singles; `working_male == 0` /
`working_female == 0` for couples) gate off the occupation contribution
exactly:

| Group | n_nonwork rows | `loc4` unique values on non-work | `log_q_Occ` (or `_male`/`_female`) on non-work — max\|·\| | n_nonzero |
| --- | --- | --- | --- | --- |
| singles | 16,813 | `[-1]` | **0.000e+00** | 0 |
| couples_male | 26,053 | `[-1]` | **0.000e+00** | 0 |
| couples_female | 25,693 | `[-1]` | **0.000e+00** | 0 |

Non-work alternatives are uniformly `loc4 = -1` and contribute zero to
`log_q_Occ`. No occupation-opportunity terms are active on non-work
alternatives.

---

## 7. Forbidden M0 columns

| Column | Singles parquet | Couples parquet |
| --- | --- | --- |
| `lindi` | absent | absent |
| `industry` | absent | absent |
| `nace` | absent | absent |
| `job_id` | absent | absent |
| `type_id` | absent | absent |
| `log_q_job` | absent | absent |
| `log_q_total` | absent | absent |
| `log_q_state` | absent | absent (Stijn aliases `log_q_E/H/W/Occ` are used instead) |

Couples-side suffix variants (`*_male`, `*_female`) of all forbidden
names are also absent. The frozen-spec exclusion contract holds in both
files.

---

## 8. Estimation-readiness verdict

**PASS.**

| Check | Result |
| --- | --- |
| 1. Files exist | PASS |
| 2. Sample structure (rows, households, alts/hh, exactly 1 chosen) | PASS |
| 3. Required M0 columns | PASS (`loc4_*` numeric dummies engine-derived, all other required columns present) |
| 4. Occupation variation (median ≥ 3) | PASS (median = 4.0 for all three groups) |
| 5. Prior invariants | PASS (max diff exactly 0 on every row) |
| 6. Non-work gating | PASS (`log_q_Occ` = 0 on all non-work rows) |
| 7. Forbidden M0 columns | PASS (all absent) |
| 8. Estimation already ran successfully | PASS (`run_2026-05-13_15-02-16` converged, joint LL = −6,499.88) |

The completed estimation at
`outputs/estimates/fr/spec/stijn_occ/gamspy/estimation_spec_stijn_occ_M0/run_2026-05-13_15-02-16/`
finished with `SolveStatus.NormalCompletion (ModelStatus.OptimalLocal)`
on all three result blocks (`singles_male`, `singles_female`, `couples`)
and produced finite estimates for all 52 parameters. No separate
likelihood smoke-test is required.

---

## Files produced

| File | Purpose |
| --- | --- |
| `Results/_validation_stijn_occ_M0.py` | Re-runnable validation script |
| `Results/_validation_stijn_occ_M0.json` | Machine-readable check results |
| `Results/RURO_stijn_occ_M0_mnl_validation_report_v1.md` | This report |
