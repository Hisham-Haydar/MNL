# RURO Workspace Audit

Date: May 11, 2026

Workspace inspected: `\\crc\users\hisham\Desktop\Nizam_Hisham\MNL`

External data inspected: `Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016`

## High-Level Project Map

| Area | Purpose |
| --- | --- |
| `ruro/` | Original R notebooks and functions from the R reference's RURO work. Main files are `Ruro_simulation_H.Rmd`, `Ruro_estimation_H.Rmd`, `Ruro_estimation_new.Rmd`, and `Ruro_functions_EMRWS.R`. |
| `scripts/enhanced/` | Current Python/GAMSPy RURO implementation, French data preparation, estimation specs, estimation engines, and post-estimation tooling. |
| `scripts/Job_model/` | Job-choice related construction and diagnostics. |
| `outputs/estimates/fr/` | French estimation outputs, including continuous RURO and job-choice runs. |
| `Data/` | Project-local data documentation and external references. The main processed French estimation data are stored outside the repo under `Z:\Hisham`. |
| `docs/` | Project documentation and generated audit notes. |
| `tests/` | Test files for parts of the Python pipeline. |

## Key RURO Code Files

| File | Role |
| --- | --- |
| `scripts/enhanced/estimation_engine.py` | Main NumPy/SciPy likelihood implementation. Contains singles and couples likelihoods. |
| `scripts/enhanced/gamspy_estimation.py` | GAMSPy estimation implementation. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | Vectorized GAMSPy implementation. |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Builds MNL estimation files and prior/proposal corrections. |
| `scripts/enhanced/estimation_spec.yaml` | Base continuous variable-wage RURO spec. |
| `scripts/enhanced/estimation_spec_v2.yaml` | Continuous v2 spec with additional region structure and warm starts. |
| `scripts/enhanced/estimation_spec_v3.yaml` | Continuous v3 spec with consumption-leisure interaction terms. |
| `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml` | Best current job-choice empirical candidate. |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Post-estimation reporting and diagnostics. |

## R reference Reference Files

| File | Role |
| --- | --- |
| `ruro/Ruro_simulation_H.Rmd` | Simulation workflow and policy/reform simulation code. |
| `ruro/Ruro_estimation_H.Rmd` | R estimation likelihood with utility, hours opportunity, wage opportunity, and prior correction. |
| `ruro/Ruro_estimation_new.Rmd` | Additional/updated R estimation workflow. |
| `ruro/Ruro_functions_EMRWS.R` | Core R helper functions, including simulated choice-set construction. |

Important R references:

- `ruro/Ruro_estimation_H.Rmd:553-570`: builds the log proposal prior.
- `ruro/Ruro_estimation_H.Rmd:834-859`: likelihood formula with `util + hopp + wopp - prior`.
- `ruro/Ruro_functions_EMRWS.R:365`: `f_choicesets_sim`.
- `ruro/Ruro_functions_EMRWS.R:396-452`: opportunity generator for employment and hours.
- `ruro/Ruro_simulation_H.Rmd:355-377`: simulated choice using `util + gumb_draw`.

## Processed French Data

Location:

```text
Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016
```

Current MNL files inspected:

| File | Rows | Households | Alternatives per household | Notes |
| --- | ---: | ---: | ---: | --- |
| `fr_2016_RURO_mnl__singles.parquet` | 167,600 | 1,676 | 100 | Continuous RURO singles. |
| `fr_2016_RURO_mnl__couples.parquet` | 257,700 | 2,577 | 100 | Continuous RURO couples. |
| `fr_2016_RURO_mnl_job_gmm__singles.parquet` | 335,200 | 1,676 | 200 | Job-choice singles. |
| `fr_2016_RURO_mnl_job_gmm__couples.parquet` | 515,400 | 2,577 | 200 | Job-choice couples. |

Data checks:

- Every household has exactly one observed/chosen row.
- `prior` is strictly positive in the inspected files.
- `log_prior == log(prior)` in the inspected files.
- In files with `log_q_total`, `log_q_total == log_prior`.
- Singles files have within-household variation in hours, wage, consumption, and leisure.
- Couples files include consumption plus partner-specific variables such as `hours_male`, `hours_female`, `wage_male`, and `wage_female`.

## Estimation Output Inventory

The French output tree contains many historical runs. The key reviewed outputs are:

| Output | Interpretation |
| --- | --- |
| `outputs/estimates/fr/2016/estimation_results.json` | Older base continuous run. It did not converge because the iteration limit was reached. |
| `outputs/estimates/fr/spec/v2/gamspy/run_2026-02-02_18-05-03/estimation_results.json` | Continuous v2 run. Local optimum but Hessian is ill-conditioned and has negative eigenvalues. |
| `outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/estimation_results.json` | Continuous v3 run. Local optimum but Hessian condition number is about `2.45e27` with 3 negative eigenvalues. |
| `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46/estimation_results.json` | Job-choice run with better curvature but part-time hours terms hit lower bounds. |
| `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json` | Best current empirical candidate. Pruned job-choice model with prior correction, market centering, no negative Hessian eigenvalues, and no listed poorly identified parameters. |

## Best Current Candidate

Use this as the current baseline for empirical RURO-style reporting:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json
```

Main diagnostics:

- `joint_ll = -22203.6096`
- `n_obs_total = 850600`
- `n_groups_total = 4253`
- `prior_correction_applied = true`
- `prior_correction_form = "-log(prior)"`
- `market_centering_applied = true`
- Hessian condition number about `1.28e6`
- `n_negative_eigenvalues = 0`
- No listed poorly identified parameters

Main caveats:

- It is a job-choice market opportunity model, not the full continuous hours/wage RURO model.
- `theta_c_sm` is tightly fixed in the spec.
- It still needs recovery tests and stability checks before being used as proof of separate identification.

## Current Risk Register

| Risk | Current status | Recommended action |
| --- | --- | --- |
| Continuous RURO Hessian instability | Active risk | Rebuild continuous spec from a simpler ladder and test each block. |
| Inconsistent prior fallback convention | Active code risk | Fix fallback so `prior` is always original-scale and positive. |
| Preference/opportunity confounding | Active identification risk | Add and document exclusion restrictions. |
| Lack of simulation recovery | Missing evidence | Add continuous-RURO recovery on French-shaped data. |
| Bound-hit opportunity terms | Seen in some job-choice specs | Keep pruned baseline and add terms back one at a time. |
| Single-year empirical variation | Identification limitation | Add region/year/labor-market variation if data allow. |

## Recommended Near-Term File Changes

1. Patch `scripts/enhanced/enh_RURO_prep_mnl_basic.py` so the continuous fallback sets:

```python
df["prior"] = prior_density
df["log_prior"] = np.log(prior_density)
```

2. Add a small validation function after MNL construction:

```python
assert (df["prior"] > 0).all()
assert np.max(np.abs(np.log(df["prior"]) - df["log_prior"])) < 1e-8
```

3. Add a recovery-test script under `scripts/enhanced/` or `tests/` that simulates choices with known parameters and estimates them back.

4. Add a short model card for `estimation_spec_job_M2h_pruned.yaml` documenting exactly which variables are interpreted as preference shifters and which are interpreted as opportunity shifters.

## Documentation Produced From This Audit

This audit generated three documents:

- `docs/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`
- `docs/RURO_R_REFERENCE_COMPARISON_AND_ACTION_PLAN.md`
- `docs/RURO_WORKSPACE_AUDIT_2026-05-11.md`

The first file is the main answer to whether the French data currently identify preferences and opportunities separately. The second file explains the comparison with the R reference's simulation. This file records the workspace and data evidence used to reach the conclusion.
