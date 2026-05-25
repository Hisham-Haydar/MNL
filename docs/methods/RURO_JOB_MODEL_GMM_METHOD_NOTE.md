# RURO Job-Model GMM Method Note

Date: 2026-05-12

Purpose: document the GMM job-model branch so it is clear what was implemented, what command was used, and how it differs from the continuous RURO branch and the non-GMM job grid.

## Short Answer

The GMM approach is implemented in the current project.

It is not just a proposal. The active job-model code supports:

- `--universe-mode gmm_occ`;
- occupation-specific GMM fitting;
- latent job-type IDs;
- optional within-type contract draws;
- job draws from the resulting job universe;
- baseline job assignment by GMM posterior component;
- downstream MNL preparation, estimation, and reporting with these job variables.

The main thing that was missing was one standalone method document. This file is that document.

## Where The GMM Code Lives

Core implementation:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/Job_model/sanity_checks_job.py`

Shared downstream pipeline:

- `scripts/enhanced/enh_RURO_euromod.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/enh_RURO_estimate_FR.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`

Current documentation and command provenance:

- `scripts/Job_model/README_job_model.md`
- `scripts/Job_model/ACCEPTANCE_TESTS.md`
- `scripts/Job_model/Commands_job.txt`
- `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
- `docs/RURO_ENHANCED_PIPELINE_COMMANDS.md`
- `docs/RURO_PROJECT_MEMORY_MAP.md`

Stale note:

- `scripts/Job_model/New Text Document.txt`

That stale note says GMM was not applied. It should not be used as current truth. The current code and current command file both include `gmm_occ`.

## Why This Branch Exists

The continuous RURO branch draws hours and wages as continuous random alternatives. That branch is close to the R reference's original RURO design.

The job-choice branch changes the opportunity object. Instead of treating hours and wages as separately drawn continuous dimensions, it builds finite job alternatives. A job alternative carries posted labor-market characteristics such as:

- `job_id`;
- `hours_rep`;
- `wage_rep`;
- `yem_rep`;
- `isco1`;
- optionally `type_id` and `type_draw_id`.

The GMM version is a more structured way to build this job universe. Instead of defining jobs only as a full grid of hours bins, wage bins, and occupation, it estimates latent job types within each occupation.

## What GMM Means In This Project

In this codebase, GMM means:

```text
For each ISCO occupation group:
    use observed working deciders;
    take log wage and hours;
    fit a Gaussian mixture model;
    keep latent mixture components as job types;
    represent each component by posted hours and wage;
    optionally add extra contract draws around each component;
    compute a prior probability for each job alternative.
```

The GMM is fitted within occupation, not across the whole labor market at once. The occupation variable is `loc_ruro` in the ready data and becomes `isco1` in the job universe.

## Inputs

The GMM universe step consumes the RURO-ready files created by `enh_RURO_prep.py`:

- `singles_RURO_ready.parquet`
- `couples_RURO_ready.parquet`

The relevant columns are:

- `lhw_base`: observed baseline hours;
- `yivwg_base`: observed baseline wage;
- `loc_ruro`: occupation/ISCO group;
- decider indicators such as `hh_IsHead` and `hh_IsPartner`;
- gender, household, and person identifiers carried downstream.

Only working observations with positive hours and positive wages are used to fit GMM components.

## GMM Fitting Details

The implementation is in `scripts/Job_model/enh_job_universe.py`, especially:

- `_fit_gmm_for_occ(...)`;
- `_build_job_universe_gmm_occ(...)`;
- `_write_gmm_diagnostics(...)`.

For each occupation:

1. Read observed hours and wages:

```text
lhw_base > 0
yivwg_base > 0
```

2. Transform wage:

```text
logw = log(yivwg_base)
X = [logw, lhw_base]
```

3. Standardize both dimensions:

```text
X_std = (X - mean(X)) / sd(X)
```

4. Fit Gaussian mixture models for:

```text
K = 1, ..., --gmm-kmax
```

5. Reject a candidate `K` if any component violates:

```text
component weight < --gmm-min-comp-weight
component hard-count < --gmm-min-comp-count
```

6. Among valid candidates, choose the model with the lowest BIC.

7. If no model passes the minimum weight/count constraints, fall back to `K=1`.

8. Compute representative posted values:

- with `--gmm-rep-stat mean`, use the GMM component mean, transformed back to original scale;
- with `--gmm-rep-stat trimmed_mean`, use trimmed observed values among hard-assigned observations.

The command you used sets:

```text
--gmm-kmax 6
--gmm-min-comp-count 50
--gmm-min-comp-weight 0.03
--gmm-rep-stat mean
--gmm-cov-type full
--gmm-contract-draws 3
```

That means each occupation can have up to 6 latent job types, subject to size and weight restrictions, and each latent type receives 3 additional within-type contract draws beyond the representative draw.

## Output Job Universe

The main output is:

```text
job_universe_2016.parquet
job_universe_2016__meta.json
job_universe_2016__gmm_diagnostics.csv
```

In your GMM command, these are written under:

```text
Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm/
```

Important job-universe columns:

| Column | Meaning |
| --- | --- |
| `job_id` | unique alternative ID; `0` is non-employment |
| `job_idx` | sequential index for working jobs |
| `isco1` | ISCO occupation group |
| `type_id` | latent GMM component within occupation |
| `type_draw_id` | within-type draw ID; `0` is representative component |
| `hours_rep` | posted hours for the job alternative |
| `wage_rep` | posted wage for the job alternative |
| `yem_rep` | monthly earnings proxy, `wage_rep * hours_rep * 52 / 12` |
| `prior` | sampling/proposal prior |
| `log_prior` | log prior |
| `q_j_prior` | same proposal prior, used downstream |

For `gmm_occ`, `hours_bin` and `wage_bin` are set to `-1` because the GMM branch is not a rectangular hours-bin by wage-bin grid. The job dimensions are occupation and latent type.

## Prior Probability

The GMM branch computes a prior over jobs approximately as:

```text
prior(job in occupation o, type k, draw r)
    proportional to occupation share(o) * GMM mixture weight(k | o) / (1 + contract_draws)
```

Then a small Laplace smoothing constant is added and the probabilities are normalized.

This prior becomes part of the proposal correction in the downstream likelihood. It is not a preference parameter.

## Contract Draws

The option:

```text
--gmm-contract-draws R
```

adds `R` extra alternatives around each GMM component.

With `R = 3`, each latent type produces:

- `type_draw_id = 0`: representative component bundle;
- `type_draw_id = 1, 2, 3`: sampled bundles from the component covariance.

These extra draws increase job-offer richness but also increase the number of alternatives and the EUROMOD simulation burden.

## Baseline Job Assignment

The draw script is:

```text
scripts/Job_model/enh_job_draws.py
```

For `gmm_occ`, baseline assignment uses `_assign_baseline_job_gmm(...)`.

For a working person:

1. Use observed `loc_ruro`, `lhw_base`, and `yivwg_base`.
2. Look up the GMM fitted for that occupation.
3. Compute posterior component log-probabilities using the fitted component weights, means, and covariances.
4. Assign the person to the most likely component.
5. Use the representative `type_draw_id = 0` job for that component.
6. If assignment fails, fall back to the highest-prior working job.

For a non-working person, baseline `job_id` is `0`.

## Draw Generation

The job draw step creates:

```text
singles_RURO_ready_jobdraws.parquet
couples_RURO_ready_jobdraws.parquet
```

For deciders:

- draw `0` is the baseline alternative;
- draws `1..K` are simulated alternatives;
- with probability `pi0`, the draw can be non-employment;
- otherwise a working job is sampled from the job prior.

The draw file carries proposal-density variables such as:

- `prior`;
- `log_prior`;
- `log_q_job`;
- `log_q_state`;
- `log_q_total`.

These are used later to correct the simulated-choice likelihood.

## Exact GMM Command Chain You Used

The canonical command file is:

```text
scripts/Job_model/Commands_job.txt
```

The GMM universe command in that file is:

```powershell
python .\scripts\Job_model\enh_job_universe.py `
  --singles-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --output-dir "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm" `
  --year 2016 `
  --universe-mode gmm_occ `
  --gmm-kmax 6 `
  --gmm-min-comp-count 50 `
  --gmm-min-comp-weight 0.03 `
  --gmm-rep-stat mean `
  --gmm-cov-type full `
  --gmm-contract-draws 3 `
  --job-id-mode deterministic `
  --include-isco0 0 `
  --seed 13
```

The following draw command then uses that universe:

```powershell
python .\scripts\Job_model\enh_job_draws.py `
  --singles-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet" `
  --couples-path "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet" `
  --job-universe "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm/job_universe_2016.parquet" `
  --job-metadata "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/job_model_gmm/job_universe_2016__meta.json" `
  --n-draws 199 `
  --baseline-mode posted `
  --seed 13
```

Then EUROMOD is run on `*_jobdraws.parquet`, and MNL prep writes:

```text
fr_2016_RURO_mnl_job_gmm__singles.parquet
fr_2016_RURO_mnl_job_gmm__couples.parquet
```

## How It Enters Preference And Opportunity Estimation

The GMM job branch feeds the same estimator entrypoint:

```text
scripts/enhanced/enh_RURO_estimate_FR.py
```

The important distinction is the specification file. Job-choice specifications live in files such as:

- `scripts/enhanced/estimation_spec_job_M2c.yaml`
- `scripts/enhanced/estimation_spec_job_M2_scaled.yaml`
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml`
- `scripts/enhanced/estimation_spec_job_M3.yaml`

The preference block still estimates utility from consumption and leisure.

The job/opportunity block can use market-opportunity shifters such as:

- `working`;
- `isco1`;
- `hours_bin`;
- `wage_bin`;
- `gsur`;
- interactions like `gsur * working * isco1`.

In job-choice specs, variables such as `gsur` can be explicitly marked as offer-only through:

```yaml
market_opportunity:
  offer_only_vars: ["gsur", "reg2", "reg3", "reg4", "reg5", "reg6", "reg7", "reg8"]
```

This is one of the reasons the job branch is better suited than the continuous branch for separating opportunity from preferences.

## Difference From Non-GMM Job Grid

The job-model code supports several universe modes.

| Mode | Meaning |
| --- | --- |
| `empirical_pruned` | observed `(hours_bin, wage_bin, isco1)` cells, rare cells dropped |
| `empirical_all` | all observed cells kept |
| `full_grid` | complete grid over occupation, hours bins, and wage bins |
| `gmm_occ` | latent job types within occupation using GMM |

The `full_grid` approach creates jobs like:

```text
isco1 x hours_bin x wage_bin
```

The `gmm_occ` approach creates jobs like:

```text
isco1 x latent_type x type_draw
```

So GMM is less rectangular and more data-driven. It tries to represent clusters of observed job contracts within each occupation rather than forcing every occupation to have the same hours/wage grid.

## Difference From Continuous Enhanced RURO

Continuous RURO command markers:

- `enh_RURO_draws.py`;
- `*_RURO_draws.parquet`;
- `fr_2016_RURO_mnl`;
- `scenarios_2016`;
- continuous specs such as `estimation_spec_v3.yaml`.

GMM job-model markers:

- `scripts/Job_model/enh_job_universe.py`;
- `--universe-mode gmm_occ`;
- `job_model_gmm`;
- `*_jobdraws.parquet`;
- `fr_2016_RURO_mnl_job_gmm`;
- job-choice specs such as `estimation_spec_job_M2c.yaml`.

## Diagnostics To Check

After the GMM universe step, inspect:

```text
job_universe_2016__gmm_diagnostics.csv
job_universe_2016__meta.json
```

Useful checks:

- number of components per occupation;
- whether any occupation fell back to `K=1`;
- component weights;
- component counts;
- representative hours and wages;
- number of alternatives after contract draws;
- whether `type_id` and `type_draw_id` are present in final MNL files.

The acceptance-test checklist is:

```text
scripts/Job_model/ACCEPTANCE_TESTS.md
```

## Current Interpretation

The GMM branch is best understood as a job-offer discretization method, not as a preference model by itself.

It defines the set and proposal distribution of possible jobs. Preferences are still estimated later from choices over simulated alternatives, conditional on EUROMOD disposable income and leisure.

The current safe claim is:

```text
The code can estimate preferences using GMM-built job alternatives.
The GMM part defines opportunity alternatives and proposal probabilities.
Preference parameters are still estimated in the downstream RURO likelihood.
```

## Main Remaining Risks

1. Occupation is not the same as industry sector.

The GMM branch uses `isco1`, which is occupation. It is sector-like only in the loose sense that it adds job-market categories. A true NACE/industry-sector opportunity model still needs a dedicated sector variable carried through data prep, job universe, draw generation, MNL prep, specs, estimation, and reporting.

2. More diagnostics are needed before final structural claims.

The job branch is the strongest current route for separating preferences and opportunities, but final claims still need:

- fit diagnostics by group;
- sensitivity to `Kmax`, covariance type, and contract draws;
- comparison against full-grid job model;
- checks that opportunity shifters are not leaking into preference terms;
- robustness of GSUR and occupation effects.

3. `gmm-contract-draws` trades richness for computation.

More contract draws improve within-type variation but increase EUROMOD work and estimator size.

## Best Files To Read Next

Read in this order:

1. `scripts/Job_model/Commands_job.txt`
2. `scripts/Job_model/README_job_model.md`
3. `scripts/Job_model/ACCEPTANCE_TESTS.md`
4. `docs/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
5. `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md`
6. `docs/RURO_R_REFERENCE_COMPARISON_SECTOR_OPPORTUNITY_PLAN.md`
