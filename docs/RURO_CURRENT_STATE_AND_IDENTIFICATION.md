# RURO Current State and Identification Assessment

Date: May 11, 2026

Scope: workspace at `\\crc\users\hisham\Desktop\Nizam_Hisham\MNL`, with processed French data under `Z:\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016`.

## Short Answer

The code can estimate separate RURO parameter blocks for preferences and opportunities. The empirical French evidence does not yet support the stronger claim that preferences and opportunities are separately identified in a reliable structural sense for the continuous RURO model.

The best current empirical candidate is the newer job-choice RURO branch, especially `estimation_spec_job_M2h_pruned`. That branch has a much healthier Hessian than the continuous French specs and applies the proposal/prior correction correctly. However, it is a pruned job-market opportunity model, not a full validation of Stijn's continuous hours/wage RURO opportunity model, and one preference curvature parameter is effectively fixed.

Therefore the safest statement today is:

> The current implementation can jointly estimate preference and opportunity components, and the job-choice branch gives a provisional empirical separation of preferences from market opportunity. For the French continuous RURO data, I cannot yet claim credible separate identification of opportunity and preferences.

## What The Estimator Is Doing

The active Python likelihood follows the RURO structure:

```text
choice index = utility preference component
             + hours opportunity component
             + wage opportunity component
             + optional market opportunity component
             - proposal/prior correction
```

Key code references:

- `scripts/enhanced/estimation_engine.py:294` defines `compute_likelihood_singles`.
- `scripts/enhanced/estimation_engine.py:356` computes singles value as `u + log_h + log_w + log_market - np.log(data.prior)`.
- `scripts/enhanced/estimation_engine.py:1181` defines `compute_likelihood_couples`.
- `scripts/enhanced/estimation_engine.py:1245` computes couples value as `u + log_h + log_w + log_market - np.log(data.prior)`.

This means the code is structurally capable of estimating separate preference and opportunity terms. The remaining question is empirical identification, not whether the code has separate parameter blocks.

## Current French Data State

The processed French MNL files currently used by recent runs are internally coherent on the prior correction convention.

| File | Households | Alternatives per household | Rows | Prior status |
| --- | ---: | ---: | ---: | --- |
| `fr_2016_RURO_mnl__singles.parquet` | 1,676 | 100 | 167,600 | `prior > 0`, `log_prior == log(prior)` |
| `fr_2016_RURO_mnl__couples.parquet` | 2,577 | 100 | 257,700 | `prior > 0`, `log_prior == log(prior)` |
| `fr_2016_RURO_mnl_job_gmm__singles.parquet` | 1,676 | 200 | 335,200 | `prior > 0`, `log_prior == log(prior)` |
| `fr_2016_RURO_mnl_job_gmm__couples.parquet` | 2,577 | 200 | 515,400 | `prior > 0`, `log_prior == log(prior)` |

Each household has exactly one observed/chosen row in these files. The singles files have within-household variation in hours, wage, consumption, and leisure. The couples files also contain household consumption and partner-specific variables such as `hours_male`, `hours_female`, `wage_male`, and `wage_female`.

This is enough for the likelihood to run, but not by itself enough to prove that preference and opportunity parameters are separately identified.

## Current Output Evidence

| Model/output | Data scale | Optimizer status | Hessian diagnostics | Identification assessment |
| --- | ---: | --- | --- | --- |
| `outputs/estimates/fr/2016/estimation_results.json` | 425,300 rows, 4,253 households | Failed: iteration limit reached | Large gradient reported | Not usable for identification claims |
| `outputs/estimates/fr/spec/v2/gamspy/run_2026-02-02_18-05-03/estimation_results.json` | 425,300 rows, 4,253 households | Local optimum | Condition number about `1.48e23`, 4 negative eigenvalues | Unstable |
| `outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/estimation_results.json` | 425,300 rows, 4,253 households | Local optimum | Condition number about `2.45e27`, 3 negative eigenvalues | Unstable |
| `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46/estimation_results.json` | 850,600 rows, 4,253 households | Local optimum | Condition number about `1.34e6`, 0 negative eigenvalues | Better, but part-time hours terms hit lower bounds |
| `outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json` | 850,600 rows, 4,253 households | Local optimum | Condition number about `1.28e6`, 0 negative eigenvalues, no flagged poorly identified parameters | Best current candidate, still provisional |

The continuous French runs are the main reason not to claim full separate identification yet. A local optimum with a Hessian condition number around `1e23` to `1e27` and negative eigenvalues is not credible evidence of separately identified structural preference and opportunity parameters.

The job-choice pruned model is materially better. Its result summary records:

- `joint_ll = -22203.6096`
- `n_obs_total = 850600`
- `n_groups_total = 4253`
- `prior_correction_applied = true`
- `prior_correction_form = "-log(prior)"`
- `market_centering_applied = true`
- Hessian condition number about `1.28e6`
- `n_negative_eigenvalues = 0`

But this still needs to be described carefully. It supports a provisional separation between preferences and a centered job-market opportunity index. It does not yet prove the full continuous RURO separation used in Stijn's simulation.

## Important Prior Convention Issue

The current processed French files used by recent runs are okay: `prior` is on the density/probability scale and `log_prior` is its logarithm.

There is still a code-path risk in `scripts/enhanced/enh_RURO_prep_mnl_basic.py`:

- Lines `1361-1383` correctly use `log_q_total`, set `prior = exp(log_q_total)`, and set `log_prior = log(prior)`.
- Lines `1448-1451` in the singles continuous fallback set `df["prior"] = np.log(prior_density)`.
- Lines `1572-1575` in the couples continuous fallback do the same.

That fallback is inconsistent with `estimation_engine.py`, which subtracts `np.log(data.prior)`. If that fallback path is used, the estimator may take the log of a log-density rather than the log of a density. Recent `log_q_total` based files avoid this problem, but the fallback should still be fixed before treating the pipeline as robust.

Recommended canonical convention:

```text
prior     = proposal density/probability on original scale, always positive
log_prior = log(prior)
likelihood correction = -log_prior, or equivalently -log(prior)
```

## Identification Interpretation

Separate parameter blocks are not the same as separate identification. In the French empirical setting, preference and opportunity terms can both explain the same observed outcome:

- A person works full time because they prefer consumption and dislike leisure less.
- A person works full time because full-time opportunities are more available.
- A person does not work because they prefer leisure, because wage offers are low, or because opportunities are scarce.

The likelihood can distinguish these only if the model has enough independent variation. This usually requires exclusion restrictions and external opportunity shifters:

- Variables that enter opportunity but not preferences, such as local labor demand, occupation availability, unemployment, region-by-education job shares, or job-type availability.
- Variables that enter preferences but not opportunity, such as household demographics, children, age profiles, and partner interactions where theoretically justified.
- Stable diagnostics across specifications, seeds, draw counts, and starting values.

The current continuous specs use rich utility and opportunity terms, but their Hessian diagnostics say the data and specification are not separating them cleanly. The job-choice specs add market opportunity terms and centering, which is why they are more promising.

## What You Can Claim Now

Reasonable current claim:

> The code implements a RURO likelihood with separate preference, hours-opportunity, wage-opportunity, and job-market opportunity components. On the French 2016 data, the continuous RURO specifications can be estimated but do not yet provide stable evidence of separate identification. The newer job-choice specifications, especially the pruned M2h version, are the strongest current empirical candidate for separating preferences from opportunity, but they should be reported as provisional pending simulation recovery and additional identification checks.

Claims to avoid for now:

- "Preferences and opportunities are separately identified on the French data."
- "The continuous RURO model is production-ready for structural interpretation."
- "The job-choice opportunity estimates are directly comparable to Stijn's continuous hours/wage opportunity DGP."

## Minimum Next Steps

1. Fix the continuous fallback prior convention in `enh_RURO_prep_mnl_basic.py`.
2. Add tests that enforce `prior > 0` and `max(abs(log_prior - log(prior)))` near zero for every MNL output file.
3. Run a Stijn-style simulation recovery test on French-shaped data with known preference and opportunity parameters.
4. Strengthen exclusion restrictions so some variables affect opportunity only and others affect preferences only.
5. Re-estimate a simpler continuous RURO spec before adding interactions.
6. Treat `estimation_spec_job_M2h_pruned` as the current empirical baseline, not as final proof.
7. Only claim separate identification after convergence, Hessian, bounds, seed stability, draw stability, and recovery diagnostics all pass.
