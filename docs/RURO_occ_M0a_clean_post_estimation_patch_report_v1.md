# RURO `ruro_occ_M0a_clean` - Post-Estimation Reporting Patch Report v1

Date: 2026-05-14
Scope: post-estimation **reporting** code only. No change to the estimator,
likelihood, YAML spec, MNL data, or economic model. The on-disk
`estimation_results.json` from
`outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/run_2026-05-13_19-24-38/`
is unchanged; only the diagnostics produced from it are now correct.

## 1. Files changed

| file | functions touched |
| --- | --- |
| `scripts/enhanced/RURO_post_estimation_styled.py` | `compute_beta_l_full`, `_compute_opportunity_from_spec` (new), `_add_predicted_probabilities`, `compute_fit_diagnostics_from_data`, `run_styled_post_estimation` (one-line wiring) |

No other source file was modified. Driver script
`Results/_M0a_clean_post_est_fit_check.py` (created in patch v0) is the
validation artefact and was re-run unchanged.

## 2. Exact functions / locations and what changed

### 2.1 `compute_beta_l_full(df, params, suffix, spec=None)`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (around line 4910).
- Previously: param-name-based heuristic stripped `beta_l_` then `suffix`
  and looked up the residual in a hard-coded `covariate_mapping`. For the
  M0a-clean YAML the coefficients are `beta_l_age`, `beta_l_age2`,
  `beta_l_nkids`, which after stripping become `age`, `age2`, `nkids` -
  none of which are columns in the parquet (`age_norm`, `age_norm2`,
  `n_children`). All singles leisure shifters therefore contributed
  **zero** to `beta_l(X)`.
- Patch: when `spec` is supplied, iterate `spec.utility_leisure_shifters`
  and use the YAML-declared `variable` field to resolve the data column
  directly. `gender_specific: true` is treated as female-only (matches
  M0a-clean `n_children` shifter). The legacy heuristic is preserved as
  a fallback when no spec is passed, with `age`/`age2`/`nkids` aliases
  added so the heuristic also no longer silently drops them.

### 2.2 NEW `_compute_opportunity_from_spec(df, params, spec, applies_key, partner)`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (around line 2758).
- This function mirrors the structural diagnostic
  (`Results/_participation_diag_ruro_occ_M0a_clean.py`) and rebuilds
  the full opportunity index from the parsed spec:
  - `O_E` and `O_H` from `spec.hours_shifters` (variables `working`,
    `working_pt1`, `working_pt2`, `working_ft` read directly from the
    parquet, not recomputed from `hours`).
  - `O_market` and `O_Occ` from `spec.market_opportunity_shifters`.
    Note: the spec parser appends `occupation_opportunity` shifters
    onto `market_opportunity_shifters` with `interaction=['working']`
    and `applies_to in {sm, sf, cm, cf}`, so both indices live on the
    same list. The new helper applies `variable_scales`, expands
    interaction lists, and filters by `applies_to == applies_key`.
    Occupation variable names of the form `loc4_k` are decoded as
    `(loc4 == k).astype(float)`.
  - `O_W` is the lognormal wage density with the per-row mean built
    from `spec.wage_mean_shifters` and `sigma`. Zero on non-work rows.
- For couples, `partner='male' | 'female'` selects partner-suffixed
  columns (`working_male`, `hours_male`, `wage_male`, `loc4_male`,
  `gsur_male`, `educH_male`, ...). For singles `partner=None` uses bare
  column names. The function is called twice for couples (once per
  partner) and once for singles.

### 2.3 `_add_predicted_probabilities`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (around line 2880).
- Two changes:
  1. `theta_c` lookup now consults `spec.theta_c_param_name(group)`
     for singles groups, so M0a-clean picks up `theta_c_singles`
     instead of falling back to couples' `theta_c`.
  2. The opportunity-layer branch (the "no `log_opp` column on the
     parquet" path) now calls `_compute_opportunity_from_spec` for
     singles and twice (one per partner) for couples, instead of the
     old `_compute_log_h + _compute_log_w` pair. The old pair was
     missing the entire `market_opportunity` and `occupation_opportunity`
     contributions, which is why the previous patch left singles
     stuck near 0.999.
  3. The Box-Cox is now applied to **raw** `consumption` / `leisure`
     (and `leisure_male`/`leisure_female` for couples), not the
     normalised `c_norm`/`l_norm` columns. The estimator
     (`gamspy_estimation_vectorized.py:347-348`) reads raw consumption
     and leisure into `data.consumption` / `data.leisure` before the
     Box-Cox, so the reporter must do the same. The earlier reporter
     used `c_norm` / `l_norm` when present, which gave V values blown
     out by an order of magnitude (manual sanity check on 100
     households showed reporter V std = 60.5 vs diagnostic V std =
     7.87 before the fix; after the fix the V series matches the
     diagnostic to within 1e-14).

### 2.4 `compute_fit_diagnostics_from_data(parsed_params, mnl_base, spec=None)`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (around line 4598).
- Three fixes already in v0 (the previous patch):
  1. Singles `dgn` mapping corrected (`dgn=1` is male, `dgn=0` is female).
  2. Singles inline V reconstruction replaced by delegation to
     `_add_predicted_probabilities`.
  3. Couples branch also delegates to `_add_predicted_probabilities`.
- v1 adds: pulls the **joint** parameter view so per-group suffixed
  names (`beta_c_sm`, `theta_c_singles`, `theta_l_m`, `beta_l_age_sm`,
  ...) are all visible in a single dict.

### 2.5 `run_styled_post_estimation`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (around line 7457).
- One-line change: pass the already-loaded `spec` into
  `compute_fit_diagnostics_from_data(parsed, mnl_base, spec=spec)`.

## 3. Reporting-only confirmation

- The estimator (`estimation_engine.py`,
  `gamspy_estimation_vectorized.py`, `gamspy_estimation.py`) is
  **untouched** by this patch.
- The likelihood is unchanged: no code path involved in computing the
  objective was modified.
- The M0a-clean YAML
  (`scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml`) is
  unchanged.
- MNL parquets at `Z:/.../fr_2016_RURO_mnl__{singles,couples}.parquet`
  are unchanged (read-only here).
- The on-disk `estimation_results.json` is unchanged. Re-estimation was
  not performed; only the post-estimation diagnostic was re-run against
  the existing JSON.

## 4. Validation run

Driver: `Results/_M0a_clean_post_est_fit_check.py` (uv venv Python,
about 10 s wall time). Loads `parsed`, `spec`, calls
`compute_fit_diagnostics_from_data(parsed, MNL_BASE, spec=spec)`, dumps
result to `Results/_M0a_clean_post_est_fit_check.json`.

A targeted cross-check was also performed: on the same 100-household
sample used by `Results/_participation_diag_ruro_occ_M0a_clean.py`
(`SAMPLE_SEED=17`), the patched reporter's V vector matches the
structural diagnostic's V vector to within 1e-14, confirming that
the reporter and the diagnostic now reconstruct the choice index in
exactly the same way.

## 5. Before / after - predicted participation

| group | observed | v0 (M0a-clean LLM summary 20260513_193536) | post-v0 patch (`log_h + log_w` only) | post-v1 patch (full spec-driven opportunity) | structural diagnostic (100 hh sample) |
| --- | --- | --- | --- | --- | --- |
| `sm`    (singles_male)   | 0.9295 | 1.0000 | 0.9990 | **0.9129** | 0.912 (= 1 - 0.088) |
| `sf`    (singles_female) | 0.9396 | 1.0000 | 0.9981 | **0.9540** | 0.950 (= 1 - 0.050) |
| `cou_m` (couples_male)   | 0.9717 | 1.0000 | 0.9980 | **1.0000** | ~ 1.0000 (P(nonwork) ~ 0) |
| `cou_f` (couples_female) | 0.9651 | 1.0000 | 0.9951 | **1.0000** | ~ 1.0000 (P(nonwork) ~ 0) |

Predicted singles participation now matches the structural
participation diagnostic to within sampling noise; the couples
prediction of ~ 1.0000 is the structural diagnostic's verdict for
this estimated model, not a reporting bug (the V_work - V_nonwork gap
for couples is around +83 to +88 nats per household, see Section 4 of
the participation diagnostic). Mean hours predicted: `sm` 35.65 (obs
39.30), `sf` 35.03 (obs 36.30), `cou_m` 59.69, `cou_f` 59.58. The
high mean-hours predictions for couples reflect that the household V
concentrates on the highest-hours alternative for couples - again a
model-fit observation, not a reporting issue.

## 6. Does couples participation remain at 1.0000?

Yes - and the structural diagnostic confirms this is the correct
behaviour for the current estimated parameters, not an artefact of
the reporter. The participation diagnostic v1 (Sections 4-5) shows
couples' V_work exceeds V_nonwork by +83 to +88 nats per household,
giving P(nonwork) numerically indistinguishable from zero. The
patched reporter therefore aligns with the structural diagnostic
for couples; the question of whether the underlying model fits
couples' participation well is an economic question for the
modeller, not a reporting bug.

## 7. Remaining reporting risks

1. **Couples mean predicted hours (~59)** is much larger than observed
   (~41). The reporter aggregates `sum_j prob_j * hours_j`. Because the
   estimated V for couples concentrates on the highest-hours
   alternative, the expected-hours statistic is dominated by that
   alternative. This is a model-fit signal, not a reporting bug, but
   the hours-distribution table will look skewed until the model fits
   couples' hours better.
2. **`compute_marginal_utilities_at_chosen`** still calls the legacy
   `compute_beta_l_full(...)` without a spec. With the added `age`,
   `age2`, `nkids` aliases in the legacy fallback the silent-zero
   issue is largely mitigated, but for full fidelity it should also
   accept and forward `spec`. Left as a follow-up.
3. **Fallback when spec is not loaded**: if the spec config cannot be
   resolved (`_extract_spec_config_from_results_json` fails to find
   one in the JSON), the reporter falls back to the prior
   `_compute_log_h + _compute_log_w` path, which is missing the
   market and occupation contributions. For M0a-clean the spec is
   always present, so this is a defensive path only.

## 8. Reproducing the validation

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\Results\_M0a_clean_post_est_fit_check.py"
```
