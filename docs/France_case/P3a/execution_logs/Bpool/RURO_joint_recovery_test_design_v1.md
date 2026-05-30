# Joint Recovery Test Design — Step 3a

**Project:** Unequal Job Opportunities and Well-Being Inequality (JMP)
**Session scope:** Step 3a — spec construction, routing verification, smoke test
**Date:** 2026-05-30
**Engine:** `scripts/enhanced/estimation_engine.py`
**Spec:** `scripts/bpool/specs/estimation_spec_joint_pooled_v1.yaml`
**Harness:** `scripts/bpool/joint_recovery_test.py`

---

## Prerequisites

### Wage 2016-real gate

All four checks PASS (max absolute deviation = 0 across both data splits):

| Split | Condition | Result |
|---|---|---|
| Singles (505,707 rows x 166 cols) | max\|wage - wage_nominal * CPI[data_year]\| = 0 | **PASS** |
| Couples (6,701,638 rows x 120 cols) | max_diff wage_male = 0 | **PASS** |
| Couples (6,701,638 rows x 120 cols) | max_diff wage_female = 0 | **PASS** |

The estimator-facing wage columns are deflated by the same `phi` basis as `ils_dispy_real`. All objects entering utility share the 2016-real basis. Year shifters (`beta_E_y2015`, `beta_E_y2017`) therefore absorb real aggregate offer-level shifts, not nominal drift. Reference: `RURO_build_fix_wage_idorighh_v1.md`.

### idorighh gate

All checks PASS on both splits:

| Split | Condition | Result |
|---|---|---|
| Singles | `idorighh` present, 0 nulls, `cluster_id == idorighh` on all rows | **PASS** |
| Couples | `idorighh` present, 0 nulls, `cluster_id == idorighh` on all rows | **PASS** |

The stable clustering key `idorighh` is confirmed present on all engine-ready parquets. Two-wave recurrence (approximately 1,105 singles and 1,600 couples appear in both 2016 and 2017) means standard errors must be reported in both unclustered and `idorighh`-clustered forms.

**PREREQUISITES SATISFIED.**

---

## Joint spec: estimation_spec_joint_pooled_v1.yaml

**File:** `C:\Users\hisham\Repo\MNL\scripts\bpool\specs\estimation_spec_joint_pooled_v1.yaml`

### 49-parameter count confirmed

The parser validation run produced:

```
n_params = 49
All assertions PASS
```

The full ordered parameter list (as returned by `spec.all_param_names`):

```
['beta_l0_sm', 'beta_l_age_sm', 'beta_l_age2_sm', 'theta_l_sm',
 'beta_l0_sf', 'beta_l_age_sf', 'beta_l_age2_sf', 'beta_l_nkids_sf', 'theta_l_sf',
 'theta_c_singles',
 'beta_l0_m', 'beta_l_age_m', 'beta_l_age2_m', 'theta_l_m',
 'beta_l0_f', 'beta_l_age_f', 'beta_l_age2_f', 'beta_l_nkids_f', 'theta_l_f',
 'beta_E', 'beta_h_pt1', 'beta_h_pt2', 'beta_h_ft', 'beta_h_lh',
 'beta_E_gsur',
 'beta_E_drgn2', 'beta_E_drgn3', 'beta_E_drgn4', 'beta_E_drgn5',
 'beta_E_drgn6', 'beta_E_drgn7', 'beta_E_drgn8',
 'beta_E_y2015', 'beta_E_y2017',
 'beta_E_drgur', 'beta_E_drgmd',
 'beta_occ_2_m', 'beta_occ_3_m', 'beta_occ_4_m',
 'beta_occ_2_f', 'beta_occ_3_f', 'beta_occ_4_f',
 'beta_w0', 'beta_w_educL', 'beta_w_educH', 'beta_w_pexp', 'beta_w_pexp2',
 'sigma',
 'beta_ll']
```

No duplicates. All 6 new gender-specific occupation params present (`beta_occ_{2,3,4}_{m,f}`). All 12 old group-specific params (`*_sm/*_sf/*_cm/*_cf`) absent.

### Exact parameter partition table

| Block | Parameters | n | Category |
|---|---|---:|---|
| Singles male leisure | `beta_l0_sm`, `beta_l_age_sm`, `beta_l_age2_sm`, `theta_l_sm` | 4 | Group-specific |
| Singles female leisure | `beta_l0_sf`, `beta_l_age_sf`, `beta_l_age2_sf`, `beta_l_nkids_sf`, `theta_l_sf` | 5 | Group-specific |
| Singles consumption curvature | `theta_c_singles` | 1 | Group-specific |
| Couples male leisure | `beta_l0_m`, `beta_l_age_m`, `beta_l_age2_m`, `theta_l_m` | 4 | Group-specific |
| Couples female leisure | `beta_l0_f`, `beta_l_age_f`, `beta_l_age2_f`, `beta_l_nkids_f`, `theta_l_f` | 5 | Group-specific |
| Couples leisure interaction | `beta_ll` | 1 | Group-specific |
| **Group-specific subtotal** | | **20** | |
| Hours opportunity | `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_h_lh` | 5 | Shared |
| Market opportunity | `beta_E_gsur`, `beta_E_drgn2..8`, `beta_E_drgur`, `beta_E_drgmd` | 11 | Shared |
| Year shifters | `beta_E_y2015`, `beta_E_y2017` | 2 | Shared |
| Occupation opportunity | `beta_occ_{2,3,4}_m`, `beta_occ_{2,3,4}_f` | 6 | Shared |
| Wage technology | `beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` | 6 | Shared |
| **Shared subtotal** | | **29** | |
| **TOTAL** | | **49** | |

**Fixed (not in the 49):**
- `beta_c = 1.0` (scale numeraire — breaks the consumption/leisure scale ridge diagnosed in v1 recovery results)
- couples `theta_c = 0.0` (fixed)

### Occupation collapse map: old to new

The parent spec (`estimation_spec_bpool_p3a_v1.yaml`, 55 params) carried 12 occupation parameters across four marital-status/gender blocks. The joint spec collapses these to 6:

| Old params (parent, 55-param spec) | New params (joint, 49-param spec) | Rationale |
|---|---|---|
| `beta_occ_2_sm`, `beta_occ_2_cm` | `beta_occ_2_m` | Gender-specific, marital-status-pooled |
| `beta_occ_3_sm`, `beta_occ_3_cm` | `beta_occ_3_m` | Gender-specific, marital-status-pooled |
| `beta_occ_4_sm`, `beta_occ_4_cm` | `beta_occ_4_m` | Gender-specific, marital-status-pooled |
| `beta_occ_2_sf`, `beta_occ_2_cf` | `beta_occ_2_f` | Gender-specific, marital-status-pooled |
| `beta_occ_3_sf`, `beta_occ_3_cf` | `beta_occ_3_f` | Gender-specific, marital-status-pooled |
| `beta_occ_4_sf`, `beta_occ_4_cf` | `beta_occ_4_f` | Gender-specific, marital-status-pooled |

Net reduction: 55 - 6 = **49 parameters**.

### Key spec decisions from governance doc

Reference: `docs/France_case/_shared/governance/JMP_joint_estimation_spec_v1.md`

| Decision | Value | Governance reference |
|---|---|---|
| Parameter count | 49 = 29 shared + 20 group-specific | §1 |
| Occupation structure | Gender-specific (`male`/`female`), pooled across marital status | §1c |
| Wage basis | 2016-real (HICP-deflated at build stage) | §2 |
| Year variation | Aggregate offer level only (`beta_E_y2015`, `beta_E_y2017`); preferences/wage tech fixed | §2 |
| SE treatment | Point: repeated cross-section; report unclustered + `idorighh`-clustered | §2 |
| `beta_c` | Fixed at 1.0 (scale numeraire); not estimated | §1b |
| Couples `theta_c` | Fixed at 0.0; not estimated | §1b |
| 10x10 couples grid | Deferred; run on validated 30x30 (900-alt) | §4 |
| `beta_ll` identification | Try pooled identification; §5 fallback if inert | §5 |
| Recovery requirement | Joint recovery test (shared-from-pooled + contamination) required before any real-data decomposition | §6 |

The slice pre-test that supports the marital-status collapse: sm estimates (`-1.498/-2.087/0.064`) vs cm (`-1.579/-2.403/0.326`) are close and same-signed within the male gender; sf (`-0.021/-0.498/0.831`) vs cf (`0.094/-0.355/0.807`) similarly close within female. Cross-gender differences (sm vs sf, cm vs cf) are sharp — the correct pattern for gender-specific, marital-status-pooled occupation opportunity.

---

## Joint likelihood routing

### Shared param routing proof

**File:** `C:\Users\hisham\Repo\MNL\scripts\enhanced\estimation_engine.py`

The three joint functions:

```python
compute_likelihood_joint(theta, data_singles_male, data_singles_female, data_couples, spec)  # line 2266
compute_gradient_joint(theta, data_singles_male, data_singles_female, data_couples, spec)    # line 2319
compute_scores_joint(theta, data_singles_male, data_singles_female, data_couples, spec)      # line 2371
```

All three accept `Optional[PrecomputedDataSingles]` for male/female singles and `Optional[PrecomputedDataCouples]` for couples, plus a single shared `spec: EstimationSpec`. They sum contributions by calling `compute_likelihood_singles` / `compute_gradient_singles` / `compute_scores_singles` and `compute_likelihood_couples` / `compute_gradient_couples` / `compute_scores_couples` on the respective data objects, accumulating over one common `theta` vector.

`spec.all_param_names` is a single 49-element list. `theta` is a single vector; `params = dict(zip(spec.all_param_names, theta))`. Shared parameters (hours, market, occupation, wage) occupy exactly one index each. Group-specific parameters (`_sm`, `_sf`, `_m`, `_f` suffixes) occupy separate indices. The gradient functions return a vector of length 49; per-group contributions add to overlapping indices for shared params and to non-overlapping indices for group-specific params. Gradients accumulate correctly by summation. **PASS.**

### Occupation applies_to: male/female routing to both singles and couples genders

**Parser** (`estimation_spec_parser.py`, lines 703-718): occupation shifters from `occupation_opportunity.shifters` are appended verbatim to `market_opportunity_shifters` with their `applies_to` tag preserved. No interpretation happens at parse time.

**Singles path** (`_compute_market_opportunity_singles`, engine.py lines 112-117):

```python
if applies_to in {"male", "sm"} and not data.is_male:
    continue
if applies_to in {"female", "sf"} and data.is_male:
    continue
if applies_to in {"cm", "cf", "household"}:
    continue
```

- `applies_to: male` — active when `data.is_male == True`, skipped when `False`. `beta_occ_*_m` fires for `data_singles_male` (is_male=True) and is silently skipped for `data_singles_female` (is_male=False). **CORRECT.**
- `applies_to: female` — mirror image. **CORRECT.**

**Couples path** (`_compute_market_opportunity_couples`, engine.py lines 224 and 254):

```python
if applies_to in ("male", "cm", "both"):   # line 224
    # uses data.loc4_2_male, data.working_male
if applies_to in ("female", "cf", "both"): # line 254
    # uses data.loc4_2_female, data.working_female
```

- `applies_to: male` — enters the `"male"` branch at line 224, reads `loc4_2_male`, `working_male`. **CORRECT.**
- `applies_to: female` — enters the `"female"` branch at line 254, reads `loc4_2_female`, `working_female`. **CORRECT.**

**Cross-group sharing:** `beta_occ_2_m` is a single entry in `spec.all_param_names` (index 36). The same `theta` vector is passed to all three sub-calls. `params["beta_occ_2_m"]` is found identically in `compute_likelihood_singles(theta, data_singles_male, spec)` and in the male branch of `compute_likelihood_couples(theta, data_couples, spec)`. A single shared coefficient covers both `singles_male` and `couples_male`. **PASS.**

The `PrecomputedDataCouples` struct has `loc4_2_male` and `loc4_2_female` (estimation_utils.py lines 585-596), built from `loc4_male` and `loc4_female` columns on the couples parquet. The singles data has `loc4_2` (estimation_utils.py line 482). The engine reads `getattr(data, var_name)` for singles and `data.loc4_2_male` / `data.loc4_2_female` for couples. Both attributes exist. **PASS.**

### Year shifter activation on pooled data

Year shifters (`beta_E_y2015`, `beta_E_y2017`) have `applies_to: household` in the spec (spec lines 162-167).

**Singles engine (engine.py line 116-117):**
```python
if applies_to in {"cm", "cf", "household"}:
    continue
```
`applies_to: household` **skips the year shifters for all singles** (both male and female). The singles parquets carry `year_2015_indicator` and `year_2017_indicator` columns (estimation_utils.py lines 813-814), but the engine never uses them for singles because of the `household` skip.

**Couples engine (engine.py line 194-222):** `applies_to == "household"` is handled by a dedicated branch that reads `data.year_2015_indicator` directly (no `_male`/`_female` suffix) and interacts it with `working_male + working_female`. This works because `PrecomputedDataCouples` stores `year_2015_indicator` as a household-level attribute (estimation_utils.py line 576).

**Routing gap identified:** Year shifters are DEAD for singles. The spec intends these as shared market-access parameters across a pooled 2015-2017 dataset, but the `applies_to: household` tag causes both singles engines (numpy and GAMSPy vectorised) to skip them entirely. The year fixed effect identified only affects the couples sub-LL, not singles. **FAIL / NEED-FIX.**

**Status at Step 3a:** The routing gap is documented but the fix is deferred to Step 3b authorization. The smoke test passes at the current spec state because `beta_E_y2015` and `beta_E_y2017` are still present in the 49-element theta vector and receive finite gradient contributions from the couples sub-LL. The gap does not affect spec validation or smoke-test correctness; it affects estimation semantics on the singles sub-LL. Two fix options are recorded below.

**Fix options (for Step 3b):**

- **Option A (recommended, ~3 lines):** Keep `applies_to: household` in the spec for the couples engine. Add `year_2015_indicator_male = year_2015_indicator` and `year_2015_indicator_female = year_2015_indicator` aliases to `build_precomputed_data_couples` in `estimation_utils.py` (year is household-level so both point to the same array). Change the two year-shifter entries in the spec from `applies_to: household` to `applies_to: both`. The singles engine will then read `data.year_2015_indicator` via `getattr(data, var_name)` (the attribute exists on `PrecomputedDataSingles`), and the couples engine will read the new aliased male/female attributes. Net change: 2 spec lines + 2 utils lines.

- **Option B (engine fix, ~3 locations):** In `_compute_market_opportunity_singles`, remove `"household"` from the skip-list so it falls through to the normal `getattr(data, var_name)` path. Keep `applies_to: household` in the spec. Same one-token change required in the GAMSPy builder (`gamspy_estimation_vectorized.py` line 581) and the gradient function.

### beta_ll couples-only confirmation

`spec.couples_interaction_coef == "beta_ll"` (confirmed by parser). It enters utility only inside `_compute_utility_couples` at engine.py line 1508 via `beta_interact * bc_l_male * bc_l_female`. The singles utility function (`_compute_utility_singles`) has no such term. In the gradient for singles, the index for `beta_ll` is looked up but the derivative is zero (the parameter does not appear in the singles log-likelihood expression); NumPy returns 0 for that column. Net gradient for `beta_ll` is the couples-only contribution. **PASS.**

### Verdict summary

| Claim | Verdict |
|---|---|
| `compute_likelihood_joint` / `compute_gradient_joint` / `compute_scores_joint` accept three data objects | PASS (engine.py lines 2266, 2319, 2371) |
| `applies_to: male` routes `beta_occ_*_m` to singles_male AND couples_male | PASS |
| Shared params (single index in 49-element vector) vs group-specific params (_sm/_sf/_m/_f) | PASS |
| `beta_ll` is couples-only | PASS |
| Year shifters (`beta_E_y2015`, `beta_E_y2017`) activate on pooled data | **ROUTING GAP — dead for singles; fix deferred to Step 3b** |
| `estimate_joint_vectorized_gamspy` accepts three data objects | PASS (gamspy_estimation_vectorized.py lines 1573-1576) |
| Single shared parameter vector, no per-group duplication | PASS |
| Occupation `applies_to: male/female` handled correctly in GAMSPy builder | PASS (gamspy_estimation_vectorized.py lines 577-582, 1023-1061) |

---

## Recovery harness design (Step 3a scaffold)

**Harness file:** `C:\Users\hisham\Repo\MNL\scripts\bpool\joint_recovery_test.py`

The harness is structured in two tiers. The smoke test (Step 3a) runs at invocation time with `--smoke` and does NOT launch the optimizer. The six full recovery checks (Step 3b) are scaffolded as callables that raise `NotImplementedError` until Step 3b is authorised and `--run` is passed.

### CLI parameters

`--spec`, `--engine-ready-stem`, `--years`, `--n-hh`, `--seed`, `--solver`, `--starts`, `--threads`, `--report`, `--smoke`, `--run`

Default spec: `scripts/bpool/specs/estimation_spec_joint_pooled_v1.yaml`
Default stem: `fr_p3a_bpool_d1w1`
Default years: `2015,2016,2017`
Default n-hh: 100 per group (smoke test)
Default seed: 20260530

### Smoke test criteria (C0-C7)

The smoke test (`--smoke`) validates seven criteria without running the optimizer:

| ID | Criterion |
|---|---|
| C0 | n_params == 49; new occ params present (`beta_occ_{2,3,4}_m/f`); old marital-specific occ params absent |
| C1 | All three engine-ready parquets load via `build_data_objects` (splits singles parquet by `dgn`, applies `n_hh` cap per group) |
| C2 | `cluster_ids` non-null on `data_sm`, `data_sf`, `data_cou` |
| C3 | `generate_theta_star` produces a finite 49-vector, all components non-zero |
| C4 | `compute_likelihood_joint` finite at theta_star |
| C5 | `compute_gradient_joint` finite, length 49 |
| C6 | `compute_scores_joint` correct shape `(n_groups_total, 49)`, finite, `cluster_ids` aligned |
| T1 | `scores.sum(axis=0) == -gradient` within `1e-6` (sign consistency check) |

### Six scaffolded checks (Step 3b, NOT auto-run)

Each check is defined as a callable that raises `NotImplementedError` with an authorization message at smoke-test time. They implement the six tests required by the governance doc (§6 of `JMP_joint_estimation_spec_v1.md`):

**Check 1 — Synthetic DGP** (`run_synthetic_dgp`): Gumbel-max draws for all three groups from production choice sets (singles: 101 alts, couples: 901 alts) under a single shared theta_star. Installs `actual_choice` on copies of the three data objects. Uses ONE shared opportunity block across all groups, guaranteed by `generate_theta_star` operating on the joint spec.

**Check 2 — Shared-from-pooled recovery** (`run_shared_recovery`): Re-estimate from pooled joint LL (`compute_likelihood_joint`) and assess recovery of the 29 shared parameters. Metric: `max|theta_hat - theta_star|` on the shared param subset. Shared params are identified as all params in `spec.all_param_names` without a group-specific suffix. This is the test the individual-group slices structurally could not run.

**Check 3 — Group-specific recovery** (`run_group_specific_recovery`): Assess recovery of the 20 group-specific preference parameters: singles-male leisure block (`_sm` suffix + `theta_c_singles`), singles-female leisure block (`_sf` suffix), couples leisure blocks (`_m`, `_f` suffixes) + `beta_ll`. If `beta_ll` recovery fails under the pooled DGP, flags §5 fallback (fix `beta_ll = 0`, sweep, document opportunity-share robustness).

**Check 4 — Two-start basin agreement** (`run_two_start_agreement`): Run optimizer from warm start (`theta_star`) and cold start (spec initial values). Check full 49-vector agreement: `max|theta_warm - theta_cold|`. Unlike the individual-group slices, no inert parameters are expected in the joint spec — every parameter has cross-group identification through the pooled likelihood, so any disagreement is a genuine flat direction, not slice-inertness.

**Check 5 — Hessian identification** (`run_hessian_check`): Compute numerical Hessian at theta_hat. Apply the 3-state G3b verdict: IDENTIFIED (PD), NEAR-COLLINEAR (PD but worst market-opp |corr| > 0.9), or NON-IDENTIFIED (non-PD). A non-PD Hessian here is a real joint identification failure — the slice verdict (where non-PD was the expected fingerprint of inert cross-group params) does not transfer. Eigenvector loading diagnostics identify the flat direction if non-PD.

**Check 6 — Contamination characterisation** (`run_contamination_check`): Perturb one group's leisure parameters in theta_star and re-estimate forcing the shared opportunity block g. Report shared-param movement (delta relative to unperturbed). `# HOOK: welfare decomposition shares — add here in Step 4`. Quantifies the §3 failure mode and provides the robustness paragraph: "under [X]% misspecification of group preferences, the opportunity share moves by [Y] points."

### Helper utilities

`generate_theta_star` — builds a plausible, non-trivial, in-bounds theta_star from spec initial values and bounds without naming any parameter; fully spec-driven; deterministic given RNG seed.

`draw_synthetic_choice` — Gumbel-max vectorised synthetic choice draw; returns `actual_choice` array.

`numerical_hessian` — central-difference Hessian with optional thread-pool parallelism over columns.

`_hessian_verdict` — 3-state G3b logic with PD/pinv/eigenvector-loading diagnostics; adapted from `recovery_test.py` without single-group mode assumptions.

---

## Smoke test results

**Run invoked with:** `--smoke --n-hh 100 --years 2015,2016,2017`

**Exit code:** 0

| Check | Result | Detail |
|---|---|---|
| n_params == 49 | **PASS** | got 49 |
| new occ params present | **PASS** | missing: set() |
| old occ params absent | **PASS** | still present: set() |
| data objects load | **PASS** | sm=100 sf=100 cou=100 groups [4.9s] |
| cluster_ids non-null (sm) | **PASS** | singles_male: 100 ids OK |
| cluster_ids non-null (sf) | **PASS** | singles_female: 100 ids OK |
| cluster_ids non-null (cou) | **PASS** | couples: 100 ids OK |
| theta_star finite | **PASS** | len=49 n_nonzero=49 |
| compute_likelihood_joint finite | **PASS** | negLL=5421.304067 |
| compute_gradient_joint finite | **PASS** | shape=(49,) max\|g\|=1.823e+02 |
| compute_scores_joint finite+aligned | **PASS** | shape=(300, 49) finite=True cids_len=300 expected_groups=300 |
| T1 score_sum == -gradient | **PASS** | max\|score_sum - (-grad)\|=8.527e-14 |

**Overall result: SMOKE TEST PASSED**

**Errors/tracebacks:** None. An initial invocation failed with exit code 2 because `--years` was passed as space-separated values (`2015 2016 2017`) instead of comma-separated (`2015,2016,2017`). This was a CLI invocation issue, not a code bug. No changes were made to the script. The second invocation succeeded immediately.

---

## Explicit scope statement

"This document covers Step 3a only: spec construction, routing verification, and smoke test.
No real-data joint estimation was run. No welfare or decomposition was computed.
No 10x10 couples alternative set was built or switched to.
Full recovery test (Step 3b) requires separate authorization."
