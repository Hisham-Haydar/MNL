# RURO Occupation-Opportunity Pipeline Audit v1

Date: 2026-05-12
Scope: enhanced continuous-draws branch (`scripts/enhanced/`) and the job-choice branch (`scripts/Job_model/`, `scripts/enhanced/enh_RURO_prep_mnl_basic.py`) on the France 2016 RURO pipeline.
Inputs: `docs/RURO_model_spec_contract_v3_stijn_occ.md`, `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`, `docs/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md`, `docs/RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md`.
Method: read-only inspection of source files and a column-schema read of the four production MNL parquet files on `Z:`. No code modified, no estimation run.

## 1. Files inspected

Documentation:
- [docs/RURO_model_spec_contract_v3_stijn_occ.md](docs/RURO_model_spec_contract_v3_stijn_occ.md)
- [docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md](docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md)
- [docs/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md](docs/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md)
- [docs/RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md](docs/RURO_STIJN_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md)

Code:
- [scripts/enhanced/enh_RURO_prep.py](scripts/enhanced/enh_RURO_prep.py) (sections around lines 404–430, 556–636)
- [scripts/enhanced/enh_RURO_draws.py](scripts/enhanced/enh_RURO_draws.py) (lines 460–636, 940–1260)
- [scripts/enhanced/enh_RURO_prep_mnl_basic.py](scripts/enhanced/enh_RURO_prep_mnl_basic.py) (lines 1361–1505, 1440–1455, 1572–1575, 1640–1700)
- [scripts/enhanced/estimation_engine.py](scripts/enhanced/estimation_engine.py) (lines 93–160, 294–360, 1181–1250)
- [scripts/enhanced/estimation_spec_parser.py](scripts/enhanced/estimation_spec_parser.py) (lines 60–90, 420–440)
- [scripts/enhanced/reduce_mnl_columns.py](scripts/enhanced/reduce_mnl_columns.py) (retained-column block)
- [scripts/Job_model/enh_job_universe.py](scripts/Job_model/enh_job_universe.py)
- [scripts/Job_model/enh_job_draws.py](scripts/Job_model/enh_job_draws.py)

Data (column-schema read only):
- `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet`
- `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet`
- `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm__singles.parquet`
- `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_job_gmm__couples.parquet`

## 2. Available occupation variables in raw/input data

EUROMOD-input level (per `enh_RURO_prep.py:556–636` and the contract's EUROMOD dictionary):
- `loc` — ISCO-08 1-digit occupation, codes `0..9`. Present in raw EUROMOD input for FR 2015–2017.
- `lindi` — NACE 1-digit industry (1 Agriculture, 2 Industry, 3 Services). Present in raw input but reserved for `M6` per contract §25.

No other occupation/industry variables in raw input.

## 3. Available occupation variables in intermediate files

`enh_RURO_prep.py` derives, for every working decider:
- `loc_raw` — verbatim copy of `loc` for traceability ([enh_RURO_prep.py:574](scripts/enhanced/enh_RURO_prep.py#L574)).
- `loc_armed` — flag for `loc == 0` (armed forces).
- `loc_ruro` — int16, cleaned `loc` with non-worker convention `-1` and unknown-worker convention `-2` ([enh_RURO_prep.py:586–588](scripts/enhanced/enh_RURO_prep.py#L586-L588)).
- `loc4` — 4-task collapse over `loc_ruro` (1 routine-manual, 2 nonroutine-manual, 3 routine-cognitive, 4 nonroutine-cognitive); preserves `-1`/`-2` sentinels ([enh_RURO_prep.py:593–636](scripts/enhanced/enh_RURO_prep.py#L593-L636)).

`enh_RURO_draws.py` also produces, when the occupation-draw path is active:
- `loc_ruro_draw`, `loc_ruro_obs` — drawn vs observed occupation.
- `log_q_occ` — per-row log of the empirical occupation proposal density ([enh_RURO_draws.py:1112, 1145–1170, 1255](scripts/enhanced/enh_RURO_draws.py#L1112)).
- `log_q_total = log_q_state + log_q_hours + log_q_wage + log_q_occ` ([enh_RURO_draws.py:1225](scripts/enhanced/enh_RURO_draws.py#L1225)).

So the occupation draw mechanism exists at the draws stage. The question is whether it propagates downstream.

## 4. Available occupation variables in final continuous MNL files

Schema read of `fr_2016_RURO_mnl__singles.parquet` (167,600 rows, 74 cols) and `fr_2016_RURO_mnl__couples.parquet` (257,700 rows, 80 cols):

Singles:
- `loc`, `loc4` — present.
- `lindi` — present (carried, not used).
- `prior`, `log_prior`, `log_q_state`, `log_q_total` — present.
- `working`, `working_pt1`, `working_pt2`, `working_ft`, `hours` — present.
- **Missing: `loc_ruro`, `loc_ruro_draw`, `loc_ruro_obs`, `log_q_occ`, `log_q_hours`, `log_q_wage`, `loc4_1..loc4_4` dummies, `isco1`.**

Couples:
- `loc4_male`, `loc4_female` — present.
- `log_q_state_male/female`, `log_q_total_male/female` — present.
- `prior`, `log_prior` — present.
- **Missing: `loc_male`/`loc_female`, `loc_ruro_*`, `log_q_occ_*`, per-layer log-proposals, `isco1_male/female`, `lindi_*`.**

Implication: the continuous MNL files retain `loc` and `loc4` as identifiers but **do not retain a separate `log_q_occ` column**. The per-layer factorization of `log_q_total` is lost at the MNL-build step.

## 5. Available occupation variables in final job-choice MNL files

`fr_2016_RURO_mnl_job_gmm__singles.parquet` (335,200 rows, 974 cols) carries the richest set:
- `loc`, `loc_raw`, `loc_ruro`, `loc_armed`, `loc4`, `isco1`, `loc_input`, `loc_ruro_draw`, `loc_ruro_obs`, plus `_em` variants from EUROMOD recomputation.
- `lindi`, `lindi_input`, `lindi_em` — industry, carried but not used.
- `prior`, `log_prior`, `log_q_state`, `log_q_job`, `log_q_total`.
- **Missing: a standalone `log_q_occ` column.** Occupation is bundled inside `log_q_job` because the job universe is `(hours_bin, wage_bin, isco1[, type_id])` and `q_job` is empirical over the full bundle.

Couples version has the same structure with `_male`/`_female` suffixes.

## 6. Whether LOC / LOC4 / ISCO is observed only for workers

By construction in `enh_RURO_prep.py:586–588`:
- `loc_ruro[~is_worker] = -1`.
- `loc_ruro` is `-2` where `loc` is missing among workers (unknown-worker).
- `loc4` inherits the same `-1` / `-2` sentinels.

So `loc4 ∈ {1..4}` is observed for workers only. For non-workers it is `-1`. For workers with missing ISCO it is `-2`. The raw `loc`/`loc_raw` columns may carry the original code regardless of working status for some observations, but the RURO-cleaned columns gate occupation to the working population, which is the convention the contract requires.

## 7. How non-work alternatives currently encode occupation

In the **continuous MNL** files, every alternative within a household reuses the decider's observed `loc4` (no per-alternative occupation draw was carried through to the MNL output). For non-employment alternatives (`hours = 0`, `working = 0`), `loc4` therefore takes the non-worker sentinel `-1` for non-workers, or the worker's observed `loc4` for workers; the column is not re-zeroed at the non-employment row.

In the **job-choice MNL** files, the occupation **is per alternative**: each row carries its own `loc_ruro_draw` (and `isco1`), so non-employment alternatives have `loc_ruro = -1` and working alternatives have `loc_ruro ∈ {1..9}`. This is the per-alternative occupation column the contract requires.

In neither file is the contract's strict non-work gating (`O^Occ = 0` if `h = 0`) implemented at the data level; it has to be enforced in the likelihood by multiplying every occupation indicator by `working`. The continuous MNL files do not currently carry per-row occupation indicators at all.

## 8. Whether alternatives currently draw occupation

- Continuous branch (`enh_RURO_draws.py`): the **code can draw occupation** by stratum and store `log_q_occ` ([lines 482–578, 1112–1170](scripts/enhanced/enh_RURO_draws.py#L482-L578)). However, the **resulting `log_q_occ` is not preserved in the final MNL parquet** — only `log_q_state` and `log_q_total` survive `enh_RURO_prep_mnl_basic.py`. Moreover the continuous MNL singles file has no per-alternative `loc4` variation, so even if a draw was performed upstream, it is not visible to the estimator.
- Job-choice branch (`scripts/Job_model/enh_job_draws.py`): occupation **is** drawn per alternative (jointly with hours and wage as part of `q_job`), and the result is retained as `loc_ruro_draw`/`isco1` in the MNL output, but `log_q_occ` is not stored separately — it is folded into `log_q_job`.

## 9. Whether the proposal/prior correction includes occupation

- **Continuous MNL files**: `log_prior = log_q_total = log_q_state + log_q_hours + log_q_wage` (continuous fallback in `enh_RURO_prep_mnl_basic.py:1361–1383`). When the draws path includes `log_q_occ`, it is summed into `log_q_total` *upstream* in `enh_RURO_draws.py:1225`, but because the continuous MNL files do not carry per-alternative occupation variation, the prior correction in the estimator's input does not include an effective `log_q_occ` term tied to a varying `loc4`. There is also the v2/v3 fallback bug at `enh_RURO_prep_mnl_basic.py:1448–1451` and `:1574` where, on the pure continuous-formula fallback path (no `log_q_total` column at all), `df["prior"] = np.log(prior_density)` is stored (log on the "prior" column) and `df["log_prior"] = df["prior"]` — this is a `log(log)` bug if that fallback fires.
- **Job-choice MNL files**: `log_prior = log_q_total = log_q_state + log_q_job` where `log_q_job` is the empirical density of the full `(hours_bin, wage_bin, isco1, type_id)` bundle. Occupation is therefore present inside the prior correction, but bundled, not as a separate `log_q_occ` term.

Neither file exposes a separate `log_q_occ` column. The contract §13's hard check `|log_prior − (log_q_E + working·(log_q_H + log_q_W + log_q_Occ))| < 1e-8` cannot be evaluated from the current MNL columns.

## 10. Current likelihood structure

In [estimation_engine.py:355–356](scripts/enhanced/estimation_engine.py#L355-L356):

```
log_market, _ = _compute_market_opportunity_singles(params, data, spec)
V = u + log_h + log_w + log_market − np.log(data.prior)
```

Same structure for couples at [estimation_engine.py:1245](scripts/enhanced/estimation_engine.py#L1245). `gamspy_estimation_vectorized.py` mirrors this. There is:
- a `utility` block (`u`),
- an hours-opportunity block (`log_h` = focal-point/`gsur`/working shifters),
- a wage-opportunity block (`log_w` = log-normal Mincer),
- a `market_opportunity` block (`log_market` = generic linear shifters with optional within-choice-set centering),
- the prior subtraction `− log(prior)`.

There is **no separate `occupation_opportunity` block** in the engine, the parser, or any YAML. `market_opportunity` is the closest existing hook (used in job-choice M2h for `beta_offer_isco1_*`), but per the contract it must remain distinct from `occupation_opportunity`.

## 11. What matches the occupation contract

- `loc` and `loc4` are computed in `enh_RURO_prep.py` with the correct non-worker (`-1`) and unknown-worker (`-2`) conventions (§13, §15).
- The occupation-draw machinery exists in `enh_RURO_draws.py` (stratum-based empirical `q_Occ`, `log_q_occ`, summation into `log_q_total`). The `q_Occ` definition matches the §7 minimum (empirical share among workers).
- The job-choice MNL files retain `loc_ruro` per alternative, which is the cleanest source of per-row occupation if the contract migrates to the job-choice branch — but the contract pins `M0` to the continuous branch.
- Prior subtraction is applied exactly once in both engines (§13: "exactly one `−log_prior` per alternative downstream of MNL prep").
- Couples are partner-additive in opportunity blocks already (`log_h`, `log_w`, `log_market`).

## 12. What does not match the occupation contract

Blocking issues for `M0`:

1. **No per-alternative occupation in the continuous MNL files.** The singles file carries one `loc4` per row but it does not vary across the 100 alternatives of a household. The couples file has `loc4_male`/`loc4_female` with the same problem. Without per-alternative variation, `O^Occ` cannot be identified.
2. **`log_q_occ` is not preserved in the final MNL.** `enh_RURO_prep_mnl_basic.py` keeps `log_q_state` and `log_q_total` but drops the per-layer `log_q_hours`/`log_q_wage`/`log_q_occ` columns. The contract requires all four log-component columns to be stored (contract §15).
3. **Continuous-formula fallback prior bug** at `enh_RURO_prep_mnl_basic.py:1448–1451` and `:1572–1575`: `df["prior"] = np.log(prior_density)` stores log-scale in the `prior` column, and `df["log_prior"] = df["prior"]`. Combined with the engine's `−np.log(data.prior)`, this yields a `−log(log)` if that path is hit. Recent runs use the `log_q_total` path and avoid this, but the bug remains.
4. **No `occupation_opportunity` block in the spec parser.** `estimation_spec_parser.py` parses `market_opportunity` only; there is no schema for `occupation_opportunity`, no `beta_occ_k` registration, and no rejection rule when a variable appears in both `utility` and an opportunity block (contract §20).
5. **No `O^Occ` term in either likelihood engine.** Adding it requires changes in both `estimation_engine.py` and `gamspy_estimation_vectorized.py`, partner-additive for couples.
6. **No occupation panels in `RURO_post_estimation_styled.py`.** The contract §16/§22 requires "Observed vs Predicted Occupation Distribution" and a labeled "Occupation Opportunity" parameter section.
7. **Naming hygiene.** `scripts/enhanced/RURO_post_estimation_styled.py`, the comparison plan doc, and several active YAMLs use "sector" when referring to `isco1`/`loc4`. Contract §4 forbids this for `M0`.

Non-blocking but flagged:

- `lindi` is carried in the continuous singles file and in the job-choice files. Contract §15 says it must be absent from `M0` artefacts; `reduce_mnl_columns.py` currently retains it. Either drop it from the MNL or document that it is held for `M6`.
- `θ_c_sm` is hard-fixed in `estimation_spec_job_M2h_pruned.yaml`. Contract §19/§24 forbids this at `M0`.

## 13. Minimal changes needed to add occupation opportunity

In execution order, with the smallest viable patch:

1. **Carry per-alternative `loc4` into the continuous MNL.** In `enh_RURO_draws.py`, when expanding to alternatives, write `loc4_draw` per row (singles: one column; couples: `loc4_male`/`loc4_female`). For non-employment rows, set `loc4 = -1`.
2. **Persist `log_q_occ` (and ideally `log_q_hours`, `log_q_wage`) in the final MNL.** In `enh_RURO_prep_mnl_basic.py`, add the per-layer log-proposal columns to the column-carry list. Verify upstream: `log_q_total == log_q_state + log_q_hours + log_q_wage + log_q_occ` within `1e-8`, and `prior == exp(log_q_total)`.
3. **Patch the fallback prior bug** at `enh_RURO_prep_mnl_basic.py:1448–1451` and `:1572–1575`: `df["prior"] = prior_density`, `df["log_prior"] = np.log(prior_density)`.
4. **Add an `occupation_opportunity` schema to `estimation_spec_parser.py`.** Block name distinct from `market_opportunity`; parses a `variable` (`loc4` or `loc`), a `reference` category, and a list of `beta_occ_k` parameters with bounds. Reject any spec that puts `loc`/`loc4` in `utility` or in any other opportunity block.
5. **Wire `O^Occ` into both engines.** In `estimation_engine.py` and `gamspy_estimation_vectorized.py`, compute `log_occ = Σ_{k≠ref} β_occ_k · 1{loc4 = k} · working` and add it into `V`. Partner-additive for couples.
6. **Build dummies in `estimation_utils.py`.** Derive `loc4_1..loc4_4` (and `_male`/`_female`) lazily from the carried `loc4` column.
7. **Reduce columns** in `reduce_mnl_columns.py` to keep `loc4`, `loc4_*`, `log_q_occ*`, plus the other per-layer log-proposal columns.
8. **Post-estimation** in `RURO_post_estimation_styled.py`: add an "Occupation Opportunity" table and an Observed-vs-Predicted occupation-share panel.
9. **YAML**: create `estimation_spec_stijn_occ_M0.yaml` with the contract §24 parameter set.

## 14. Which scripts need changes

| File | Change | Severity |
|------|--------|----------|
| `scripts/enhanced/enh_RURO_draws.py` | Ensure per-alternative `loc4` and `log_q_occ` are written into the continuous-branch draws output | blocking |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Keep per-layer `log_q_*` columns; patch fallback prior bug; carry `loc4` per row | blocking |
| `scripts/enhanced/reduce_mnl_columns.py` | Add per-layer log-proposal and occupation dummies to retained-columns set; consider dropping `lindi` for `M0` | blocking |
| `scripts/enhanced/estimation_spec_parser.py` | Parse `occupation_opportunity`; register `beta_occ_*`; cross-block exclusion check | blocking |
| `scripts/enhanced/estimation_engine.py` | Compute `log_occ`, add to `V` (singles + couples) | blocking |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Same as estimation_engine; GAMSPy equation block | blocking |
| `scripts/enhanced/estimation_utils.py` | Derive `loc4_k` and `loc4_k_male/female` dummies in precompute | blocking |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Occupation parameter table + observed/predicted shares; rename "sector" → "occupation" | high |
| New: `scripts/enhanced/estimation_spec_stijn_occ_M0.yaml` | New baseline spec per contract §24 | high |
| `scripts/enhanced/enh_RURO_prep.py` | No code change required; already produces `loc4` with correct sentinels | n/a |

`scripts/Job_model/*` is not touched at `M0`.

## 15. Main risks

1. **Per-alternative `loc4` variation may be thin.** The current continuous-branch draws code can draw occupation by stratum, but if downstream code has been writing only the observed `loc4` to every alternative of a household, regenerating the draws files (a full rebuild of `enh_RURO_draws.py` outputs) will be needed before `M0` can identify `β_occ_k`. This is a data-rebuild dependency, not just a column-keep change.
2. **`log_q_occ` consistency with `log_q_total`.** If only `log_q_total` is preserved and `log_q_occ` is recomputed from `loc4` empirical shares at MNL-build time, there is a real risk of `log_q_total ≠ log_q_state + log_q_hours + log_q_wage + log_q_occ`. The fix is to persist all four log-components at the draws step, not reconstruct them later.
3. **Identification on 4 categories, 4,253 households.** `loc4` gives only 3 free parameters per gender (12 across SM/SF/CM/CF). Identification should be feasible, but `loc4 = 2` (nonroutine-manual) is a small cell in France; expect a wide SE there. The contract suggests `loc4` over `loc` for this reason.
4. **Double-counting with `market_opportunity`.** Existing job-choice specs use `beta_offer_isco1_*` inside `market_opportunity`. If a future spec is migrated, those terms must be moved to `occupation_opportunity`, not duplicated.
5. **EUROMOD-output dependence on `loc`.** Contract §16 step 4 requires verifying that `ils_dispy` does not depend on `loc4`. If it does (likely only via specific tax regimes), the occupation draws would need EUROMOD re-runs per drawn occupation — much larger scope.
6. **Naming drift.** Renaming "sector" → "occupation" across YAMLs, code comments, and HTML labels is mechanical but easy to miss; grep-driven sweeps are required.
7. **Fallback prior bug is latent.** It does not bite current runs because the `log_q_total` path is active, but any spec that drops `log_q_total` from the upstream draws will silently hit the `log(log)` fallback.

## 16. Recommended first implementation step

**Verify and (if needed) regenerate the continuous-branch draws so that the resulting MNL parquet carries one `loc4` per alternative plus a per-row `log_q_occ`.**

Concretely:

1. Read `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet` and check whether `loc4` varies within `idhh`. If it does not, the rest of the contract cannot be tested.
2. If it does not vary, rerun `enh_RURO_draws.py` with occupation-draws enabled (the code path at `enh_RURO_draws.py:1112–1170` already supports this), then patch `enh_RURO_prep_mnl_basic.py` to keep `loc4`, `log_q_occ`, `log_q_hours`, `log_q_wage` in the carried columns.
3. After the rebuild, assert in a small diagnostic script: `(prior > 0).all()`, `|log(prior) − log_prior| < 1e-8`, `|log_q_total − (log_q_state + log_q_hours + log_q_wage + log_q_occ)| < 1e-8`, and `loc4` has at least 4 distinct values within each household's choice set on average.

Once this step passes, the parser/engine/spec/post-estimation changes (§13 items 4–9) can be implemented and `estimation_spec_stijn_occ_M0.yaml` can be estimated. Until per-alternative `loc4` variation is in the MNL file, adding `β_occ_k` to the engine would not be identified and the estimation would be wasted compute.
