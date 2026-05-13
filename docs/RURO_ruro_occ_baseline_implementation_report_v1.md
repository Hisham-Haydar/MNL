# RURO R reference Occupation Baseline - Implementation Report v1

Date: 2026-05-12

Target: first feasible continuous RURO baseline with additive
occupation opportunity (`M0_ruro_occ`), using `loc4` occupation opportunity
and no occupation effects in utility, hours opportunity, or wage opportunity.

Inputs read:
- `docs/RURO_ruro_occ_baseline_spec_v1.md`
- `docs/RURO_occ_pipeline_audit_v1.md`
- `docs/RURO_model_spec_contract_v4_ruro_occ.md`

## 1. Files changed

| File | Change |
|---|---|
| `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` | New runnable spec for `ruro_occ_M0`; uses `model_family: regular`, Mincer wage mean, base `beta_E`, dedicated `occupation_opportunity`, and 12 group-specific occupation coefficients. |
| `scripts/enhanced/estimation_spec_parser.py` | Added top-level `occupation_opportunity` parsing, enforces that `loc4`/`loc` do not appear in utility/hours/wage/market blocks, appends occupation shifters to the engine market-opportunity list, and fixes the `spec.name = gsur` shadowing bug. |
| `scripts/enhanced/estimation_engine.py` | Adds `applies_to: sm/sf/cm/cf` routing for market/occupation shifters and fixes log-normal wage opportunity by adding the required `-log(wage)` Jacobian. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Same group routing and log-normal Jacobian fixes for the vectorized GAMSPy path used by the run command. |
| `scripts/enhanced/gamspy_estimation.py` | Adds the log-normal Jacobian and supports the `beta_w_pexp`/`beta_w_pexp2` names in the non-vectorized wage mean. |
| `scripts/enhanced/estimation_utils.py` | Aligns PT1 hours band to `[18.5, 21.5]`. |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Aligns PT1 band, fixes fallback prior storage (`prior` density, `log_prior = log(prior)`), creates proposal-component aliases (`log_q_E/H/W/Occ`), computes prior from per-layer components when available, and drops M0-forbidden job/industry proposal artifacts from the final keep set. |
| `scripts/enhanced/reduce_mnl_columns.py` | Keeps proposal-component aliases and drops `lindi`/`industry`/`nace` for M0 reductions. |
| `docs/RURO_ruro_occ_baseline_implementation_report_v1.md` | This report. |

The job-choice branch under `scripts/Job_model/` was not modified.

## 2. New columns required

Required in the rebuilt MNL parquet:

- Singles: `loc4`, `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`.
- Couples: `loc4_male`, `loc4_female`, plus `log_q_E_male`, `log_q_H_male`, `log_q_W_male`, `log_q_Occ_male`, and the `_female` analogues.

The draw script currently writes proposal components as `log_q_state`,
`log_q_hours`, `log_q_wage`, `log_q_occ`. The MNL prep now aliases these to
the frozen names:

```text
log_q_state -> log_q_E
log_q_hours -> log_q_H
log_q_wage  -> log_q_W
log_q_occ   -> log_q_Occ
```

M0-forbidden output columns are no longer in the active MNL keep set:
`lindi`, `industry`, `nace`, `job_id`, `type_id`, `hours_bin`, `wage_bin`,
`log_q_job`, `log_q_state`, and `log_q_total`.

Existing parquet files were built before this change and still need to be
rebuilt.

## 3. New parameters added

Employment and hours opportunity:
- `beta_E`
- `beta_h_pt1`
- `beta_h_pt2`
- `beta_h_ft`
- `beta_E_gsur`
- `beta_E_educH`

Wage opportunity:
- `beta_w0`
- `beta_w_educL`
- `beta_w_educH`
- `beta_w_pexp`
- `beta_w_pexp2`
- `sigma`

Occupation opportunity, reference `loc4 = 1`:
- Singles male: `beta_occ_2_sm`, `beta_occ_3_sm`, `beta_occ_4_sm`
- Singles female: `beta_occ_2_sf`, `beta_occ_3_sf`, `beta_occ_4_sf`
- Couples male: `beta_occ_2_cm`, `beta_occ_3_cm`, `beta_occ_4_cm`
- Couples female: `beta_occ_2_cf`, `beta_occ_3_cf`, `beta_occ_4_cf`

The spec now has 52 parameters in total.

## 4. How occupation enters the opportunity block

Occupation enters only through `occupation_opportunity`:

```yaml
occupation_opportunity:
  variable: "loc4"
  reference: 1
  shifters:
    - {variable: "loc4_2", coefficient: "beta_occ_2_sm", applies_to: "sm", interaction: ["working"]}
    - {variable: "loc4_3", coefficient: "beta_occ_3_sm", applies_to: "sm", interaction: ["working"]}
    - {variable: "loc4_4", coefficient: "beta_occ_4_sm", applies_to: "sm", interaction: ["working"]}
    # same structure for sf, cm, cf
```

The parser rejects `loc4`/`loc` variables in utility, hours opportunity, wage
opportunity, or residual market opportunity. Internally, the occupation
shifters are appended to `market_opportunity_shifters` so the existing engines
evaluate:

```text
O_occ = beta_occ_{k,g} * 1{group = g} * 1{loc4 = k} * working
```

There is still no occupation-by-hours or occupation-by-wage effect.

## 5. How non-work alternatives are handled

For non-work alternatives:

- `working = 0`
- `hours = 0`
- `wage = 0`
- `loc4 = -1` by draw convention
- all `loc4_1` through `loc4_4` dummies are zero
- `log_q_H = log_q_W = log_q_Occ = 0`

So occupation, hours focal points, residual market shifters, and wage
opportunity all contribute zero. The non-work index is:

```text
U(nonwork) - log_q_E(nonwork)
```

Observed working rows with `loc4 = -2` are retained as unknown occupation
rows, not as a fifth occupation category. In M0, only `loc4 = 2`, `loc4 = 3`,
and `loc4 = 4` enter the occupation-opportunity layer; `loc4 = 1` is omitted.
Therefore `loc4 = -2` sets all occupation dummies to zero and contributes zero
to `O^Occ`. This is numerically safe for estimation, but it should be
documented as unknown observed occupation rather than interpreted as the
reference category. Simulated working alternatives draw only valid
`loc4 in {1, 2, 3, 4}`.

## 6. How prior correction is handled

The final MNL convention is:

```text
prior = proposal density on the original scale
log_prior = log(prior)
```

When per-layer proposal columns are available, MNL prep computes:

```text
singles:
log_prior = log_q_E + working * (log_q_H + log_q_W + log_q_Occ)

couples:
log_prior = [male component] + [female component]
```

The engines subtract `log(prior)` once. The previous fallback bug that stored
`prior = log(density)` has been fixed.

The wage opportunity now uses the correct log-normal density for wage in
levels:

```text
log f_W(w) = log f_logW(log w) - log w
```

## 7. How to run the model

Data rebuild is required before estimation is meaningful. The current MNL
parquet files have `loc4` fixed within each household's working alternatives,
so occupation coefficients are unidentified.

Rebuild order:

```powershell
$PY = "U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe"

# 1. Rebuild draws with pooled empirical occupation sampling.
& $PY scripts/enhanced/enh_RURO_draws.py --occ-spec empirical --occ-strata __all__ ...

# 2. Run enh_RURO_euromod.py on the rebuilt draws.

# 3. Run enh_RURO_prep_mnl_basic.py to rebuild:
#    fr_2016_RURO_mnl__singles.parquet
#    fr_2016_RURO_mnl__couples.parquet
```

Use the existing full argument lists in `docs/RURO_ENHANCED_PIPELINE_COMMANDS.md`;
the key draw change is `--occ-spec empirical --occ-strata __all__`.

Canary before estimation:

```powershell
& $PY -c "import pandas as pd; df=pd.read_parquet(r'Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet'); w=df[df.working==1]; print(w.groupby('idhh')['loc4'].nunique().median())"
```

The median should be at least 3. If it is 1, the occupation draw rebuild did
not take effect.

Estimation:

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0.yaml" `
  --auto-timestamp `
  --verbose
```

Do not warm-start from a job-choice run.

Post-estimation:

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0/run_YYYY-MM-DD_HH-MM-SS/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/ruro_occ/gamspy" `
  --prefix "fr_2016_ruro_occ_gamspy_" `
  --compute-se `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0.yaml" `
  --auto-timestamp
```

## 8. What remains unimplemented

Still required after this code pass:

- Rebuild the data with `--occ-spec empirical --occ-strata __all__`.
- Run the `loc4` variation canary and prior-component consistency checks on the rebuilt files.
- Add a dedicated post-estimation occupation panel for observed vs predicted `loc4` distributions.
- Add a recovery harness and a formal NumPy-vs-GAMSPy consistency diagnostic.
- The non-vectorized GAMSPy path has the wage correction, but the production
  command should remain `--vectorized`; the vectorized and NumPy paths are the
  maintained paths for this spec.

## 9. Gate-A scorecard

| Gate | Status |
|---|---|
| YAML parses as `regular` | PASS |
| `spec.name == ruro_occ_M0` | PASS |
| Dedicated `occupation_opportunity` block | PASS |
| `loc4` excluded from utility/hours/wage/market blocks | PASS |
| 12 occupation coefficients (`sm/sf/cm/cf`) | PASS |
| Base `beta_E * working` included | PASS |
| Mincer wage mean declared | PASS |
| Log-normal wage Jacobian included | PASS |
| PT1 band `[18.5, 21.5]` | PASS |
| proposal-component aliases retained | PASS |
| M0-forbidden job/industry artifacts dropped from final keep set | PASS on rebuild |
| Current parquet identified for occupation | FAIL until data rebuild |
