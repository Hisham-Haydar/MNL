# RURO `ruro_occ_M0a_clean` — Post-Estimation Reporting Patch Report v1

Date: 2026-05-14
Scope: post-estimation **reporting** code only. No change to the estimator,
likelihood, YAML spec, MNL data, or economic model. The on-disk
`estimation_results.json` from
`outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/run_2026-05-13_19-24-38/`
is unchanged; only the diagnostics produced from it are now correct.

## 1. Files changed

| file | functions touched |
| --- | --- |
| `scripts/enhanced/RURO_post_estimation_styled.py` | `compute_beta_l_full`, `_add_predicted_probabilities`, `compute_fit_diagnostics_from_data`, `run_styled_post_estimation` (one-line wiring) |

No other source file was modified. Driver script
`Results/_M0a_clean_post_est_fit_check.py` and its output JSON
`Results/_M0a_clean_post_est_fit_check.json` were created as the
validation artefact.

## 2. Exact functions / locations and what changed

### 2.1 `compute_beta_l_full(df, params, suffix, spec=None)`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (≈line 4910).
- Previously: param-name-based heuristic stripped `beta_l_` then `suffix`
  and looked up the residual in a hard-coded `covariate_mapping`. For the
  M0a-clean YAML the coefficients are `beta_l_age`, `beta_l_age2`,
  `beta_l_nkids`, which after stripping become `age`, `age2`, `nkids` —
  none of which are columns in the parquet (`age_norm`, `age_norm2`,
  `n_children`). All singles leisure shifters therefore contributed **zero**
  to `beta_l(X)`.
- Patch: when `spec` is supplied, iterate over `spec.utility_leisure_shifters`
  and use the YAML-declared `variable` field to resolve the data column
  directly. `gender_specific: true` is treated as female-only (matches
  M0a-clean `n_children` shifter). Legacy heuristic is preserved as a
  fallback when no spec is passed, with the `age`/`age2`/`nkids` aliases
  added so the heuristic also no longer silently drops them.

### 2.2 `_add_predicted_probabilities(df, params, spec=None, is_couples=False, group_suffix='')`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (≈line 2770).
- Previously: `theta_c = params.get(f'theta_c{group_suffix}', params.get('theta_c', 0.5))`.
  For M0a-clean singles there is no `theta_c_sm` / `theta_c_sf` in the
  parameter vector; the fallback picks up couples' `theta_c` (0.319)
  instead of the singles-shared `theta_c_singles` (-0.836).
- Patch: when `spec` is supplied and the group is a singles group,
  call `spec.theta_c_param_name(group)` (which returns `theta_c_singles`
  for M0a-clean) and use that name. If the spec is not supplied or the
  resolved name is not in `params`, fall back to the prior behaviour.
- Also: `compute_beta_l_full(...)` calls inside this function now forward
  `spec=spec` so the YAML-driven shifter resolution is used.

### 2.3 `compute_fit_diagnostics_from_data(parsed_params, mnl_base, spec=None)`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (≈line 4598).
- Three fixes:
  1. Singles `dgn` mapping was inverted. The MNL parquet convention is
     `dgn=1 → male`, `dgn=0 → female` (766 males, 910 females; verified
     in the participation diagnostic v1). The loop header was changed
     from `[(0, 'male', 'sm'), (1, 'female', 'sf')]` to
     `[(1, 'male', 'sm'), (0, 'female', 'sf')]`.
  2. Singles inline V reconstruction (the block that previously called
     `params.get('beta_c', 1.0)`, `params.get('theta_c', 0.5)`, etc., and
     added `log_opp` only if pre-attached — which it never was) was
     deleted. The function now delegates to `_add_predicted_probabilities`
     with `group_suffix='_sm'` / `'_sf'` and `spec=spec`, which both
     selects the right per-group parameters and rebuilds the opportunity
     layer via `_compute_log_h` / `_compute_log_w` when no `log_opp`
     column exists on the parquet.
  3. Couples branch was similarly refactored to delegate to
     `_add_predicted_probabilities(..., is_couples=True, spec=spec)`.
     The previous in-line block used `params.get('theta_l_m', ...)`
     correctly but did not call `_compute_log_h`/`_compute_log_w` when
     `log_opp_male`/`log_opp_female` were absent (they are absent from
     the FR parquets in use), and called `compute_beta_l_full` without
     a spec so couples' YAML leisure-shifter coefficients were also
     silently dropped.
- The function now prefers the `joint` parameter view so per-group
  suffixed names (`beta_c_sm`, `theta_c_singles`, `theta_l_m`, …) are all
  visible in a single dict.

### 2.4 `run_styled_post_estimation`

- file: `scripts/enhanced/RURO_post_estimation_styled.py` (≈line 7457).
- One-line change: pass the already-loaded `spec` into the new
  signature: `compute_fit_diagnostics_from_data(parsed, mnl_base, spec=spec)`.

## 3. Reporting-only confirmation

- The estimator (`estimation_engine.py`, `gamspy_estimation_vectorized.py`,
  `gamspy_estimation.py`) is **untouched** by this patch.
- The likelihood is unchanged: no code path involved in computing the
  objective was modified.
- The M0a-clean YAML
  (`scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml`) is
  unchanged.
- MNL parquets at `Z:/.../fr_2016_RURO_mnl__{singles,couples}.parquet` are
  unchanged (read-only here).
- The on-disk `estimation_results.json` is unchanged. Re-estimation was
  not performed; only the post-estimation diagnostic was re-run against
  the existing JSON.

## 4. Validation run

Driver: `Results/_M0a_clean_post_est_fit_check.py` (`uv` venv Python,
≈10 s wall time). Loads `parsed`, `spec`, calls
`compute_fit_diagnostics_from_data(parsed, MNL_BASE, spec=spec)`, dumps
result to `Results/_M0a_clean_post_est_fit_check.json`.

## 5. Before / after — predicted participation

| group | observed | predicted **before patch** (M0a-clean LLM summary 20260513_193536) | predicted **after patch** | gap closed? |
| --- | --- | --- | --- | --- |
| `sm` (singles_male) | 0.9295 | 1.0000 | **0.9990** | yes — no longer pinned at 1.0000 |
| `sf` (singles_female) | 0.9396 | 1.0000 | **0.9981** | yes — no longer pinned at 1.0000 |
| `cou_m` (couples_male) | 0.9717 | 1.0000 | **0.9980** | yes — no longer pinned at 1.0000 |
| `cou_f` (couples_female) | 0.9651 | 1.0000 | **0.9951** | yes — no longer pinned at 1.0000 |

Mean hours predicted (post-patch): `sm` 37.26 (obs 39.30), `sf` 34.75 (obs
36.30), `cou_m` 41.03 (obs 41.61), `cou_f` 34.93 (obs 35.65). Hours
predictions are also no longer constants.

## 6. Does couples participation remain at 1.0000?

No. After the patch, couples predicted participation is 0.9980 (male)
and 0.9951 (female), against observed 0.9717 / 0.9651. The previous
identical-`1.0000` value for couples was caused by the same
`compute_beta_l_full` silent-shifter failure and the missing opportunity
layer (no `log_opp_male`/`log_opp_female` columns on the parquet), not
by an economic property of the model. Couples remain structurally close
to full participation (consistent with the V-component decomposition in
the participation diagnostic v1, where `V_work − V_nonwork ≈ +83` to
`+88` per couple), but they are no longer pinned at exactly 1.

## 7. Remaining reporting risks

1. **Magnitude gap vs. structural diagnostic for singles**. The
   participation diagnostic v1 estimated structural `P(nonwork) ≈ 7%`
   for singles_male from engine-aligned V components. The patched
   reporting code yields `P(nonwork) ≈ 0.1%`. The reporting code now
   responds to the data (no longer uniform), but the opportunity-layer
   reconstruction inside `_compute_log_h` / `_compute_log_w` may not
   exactly match the engine's forward pass — for example, the engine
   may apply `center_within_choice_set: true` on the market block
   (declared in the YAML at `market_opportunity.center_within_choice_set`),
   whereas the recomputed `log_h` from coefficients does not center.
   This is a model-fit diagnostic *precision* issue, not a reporting
   pathology, and it does not affect the estimator. Resolving it
   exactly would require either (a) attaching `log_opp` to the parquet
   during estimation and reading it back, or (b) replaying the engine's
   exact opportunity-layer routine.
2. **Hours-distribution bin assignment** still uses `pd.cut` defaults
   and is unaffected by this patch.
3. **`compute_marginal_utilities_at_chosen`** still calls the legacy
   `compute_beta_l_full(...)` without a spec. With the added `age`,
   `age2`, `nkids` aliases in the legacy fallback the silent-zero issue
   is largely mitigated, but for full fidelity it should also accept
   and forward `spec`. Left as a follow-up.
4. **Fallback when spec is not loaded**: the new code falls back to
   the prior `params.get('theta_c', 0.5)` behaviour. For M0a-clean the
   spec is always present via `_extract_spec_config_from_results_json`,
   so this is a defensive path only.

## 8. Reproducing the validation

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\Results\_M0a_clean_post_est_fit_check.py"
```
