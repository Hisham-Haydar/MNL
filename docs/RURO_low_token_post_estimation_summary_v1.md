# RURO Low-Token Post-Estimation Summary

Date: 2026-05-13

## Purpose

The post-estimation script now writes a compact Markdown summary intended for:

- Git commits,
- paper drafting,
- quick review by ChatGPT/Claude,
- sharing results without large plots, PDFs, or HTML.

The file is text-only and contains the essential tables needed to understand a
run without reading the full HTML report.

## Where It Is Generated

By default, every run of:

```text
scripts/enhanced/RURO_post_estimation_styled.py
```

writes a Markdown summary to:

```text
reports/
```

The filename is:

```text
{prefix}llm_summary_{YYYYMMDD_HHMMSS}.md
```

Example from the France 2016 Stijn occupation M0 run:

```text
reports/fr_2016_stijn_occ_gamspy_llm_summary_20260513_140315.md
```

## What It Contains

The Markdown summary includes:

- source paths for the estimation JSON, HTML report, CSV outputs, MNL base, and
  YAML specification;
- run metadata, including specification name, model family, prior correction,
  and opportunity centering;
- choice data footprint with rows, groups, alternatives per group, chosen rows,
  working rows, and column counts;
- proposal/prior diagnostics, including prior positivity, `log_prior =
  log(prior)`, Stijn proposal-alias reconstruction, and forbidden-column
  presence;
- warnings and review flags for ill-conditioned Hessians, very high predicted
  participation, small chosen probabilities, and proposal-column issues;
- utility/preference parameters by group (`beta_c`, `theta_c`, `beta_l0`,
  leisure shifters, `theta_l`, and `beta_cl` when present);
- **model index equation** (`V_ij = U + O^E + O^H + O^W + O^Occ − log_prior`,
  adapted to whichever opportunity blocks the YAML declares) and the softmax
  choice-probability formula;
- **specification block inventory** — one row per YAML opportunity block
  (`hours_opportunity`, `market_opportunity`, `wage_opportunity.mean_shifters`,
  `wage_opportunity.variance`, `occupation_opportunity`) with shifter count,
  declared variables, and coefficient names;
- **opportunity equations (symbolic)** — text-only block, one term per line
  for each shifter declared in the YAML, including the four `applies_to`
  occupation groups;
- **opportunity equations (numerical)** — a table binding each declared
  shifter to its estimated coefficient value, with the source group
  recorded;
- **per-block parameter counts and significance** — for each block:
  `n_params`, `n_estimable`, and significance hit counts at p < 0.001,
  0.01, 0.05, 0.10;
- convergence status by result block, including `n_iterations`,
  `n_function_evaluations`, `gradient_norm`, `log_likelihood`, and
  `walltime_seconds`;
- log-likelihood, null likelihoods, rho-squared, AIC, BIC, observations,
  groups, and parameters;
- observed vs predicted participation and mean hours by group;
- structural elasticity heuristics reported by the post-estimation script;
- marginal utility diagnostics;
- marginal utility distribution summaries, including negative MUC/MUL counts
  and percentages by group;
- probability diagnostics and worst-fit households;
- Hessian/identification diagnostics, with a one-line interpretation
  (well-/moderately/weakly/ill-conditioned thresholds and a flag for
  negative eigenvalues);
- **top 15 initial → final parameter movements** (ranked by |Δ|),
  exposing which coefficients moved most from their YAML initial values;
- high-correlation parameter pairs and weakest eigenvector diagnostics;
- parameters at bounds;
- all parameter estimates grouped by model block;
- observed and predicted hours-bin shares.
- wage-distribution summaries by group, with observed and predicted means and
  q10/q50/q90 for working alternatives;
- occupation-distribution shares for loc4-style columns when available,
  including loc4 labels and observed/predicted shares;
- **source environment** banner: `git_sha`, `git_branch`, and a `git_dirty`
  flag (best-effort, silent if git is unavailable);
- **per-group sample sizes**: `n_obs`, `n_households`, `alts_per_hh`,
  `n_chosen`, `n_working` for `singles_male`, `singles_female`,
  `couples_male`, `couples_female`;
- **sample descriptives** on chosen-alt rows for canonical X variables
  (`age_norm`, `age_norm2`, `educL`, `educM`, `educH`, `pexp_years`,
  `n_children`, `gsur`) — mean, std, min, max, n per group;
- **convergence health summary** — aggregated counts:
  `n_estimated_params`, log-likelihood, AIC, BIC, ρ², `n_significant_p<0.05`,
  `pct_significant_p<0.05`, `n_low_t<1.0`, `pct_low_t<1.0`,
  `n_degenerate_se`, `n_at_bound_strict`, Hessian condition number,
  `n_negative_eigenvalues`, `p_chosen_min`, `p_chosen_q10`, and a
  `review_priority_flags` field that lists any conditions warranting
  attention (e.g. `ill_conditioned_hessian`, `negative_eigenvalues_present`,
  `parameters_at_bounds`, `over_25pct_low_t`);
- **utility-block inventory rows** inside the Specification Block
  Inventory: `utility.consumption.coefficient`,
  `utility.consumption.box_cox_exponent`, `utility.leisure.intercept`,
  `utility.leisure.box_cox_exponent`, and `utility.leisure.shifters`;
- **observed hours quantiles** (q10/q25/q50/q75/q90) on chosen working
  alternatives by group, alongside the bin-based fit moments;
- **distribution-fit summary**: L1 and L2 distance between observed and
  predicted hours-bin shares, per group — a single-number summary of
  hours-fit quality per group;
- **observed vs implied log-wage σ**: observed mean and std of `log(wage)`
  on chosen working alternatives, alongside the model's estimated σ —
  per group;
- **parameters near bounds** (within 5% of the bound width) — picks up
  near-binding behaviour the strict "at bounds" check misses;
- **top significant coefficients** (top 15 by |t-value|) for fast
  identification of the strongest estimated effects.

It intentionally excludes:

- plots,
- embedded images,
- HTML styling,
- household-level long data,
- large generated outputs.

## Git Behavior

The `reports/` folder is explicitly allowed by `.gitignore`, so the Markdown
summary can be committed normally:

```powershell
git add reports/fr_2016_stijn_occ_gamspy_llm_summary_20260513_140315.md
git commit -m "Add low-token Stijn occupation M0 summary"
```

The large HTML, CSV, and plot files remain under `outputs/`, which is still
ignored unless a file is force-added.

## Command Example

The usual post-estimation command now writes the low-token summary
automatically:

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/stijn_occ/gamspy/estimation_spec_stijn_occ_M0/run_2026-05-13_11-27-40/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/stijn_occ/gamspy" `
  --prefix "fr_2016_stijn_occ_gamspy_" `
  --spec-config "scripts/enhanced/estimation_spec_stijn_occ_M0.yaml" `
  --auto-timestamp
```

## Optional Controls

To write the Markdown summary somewhere else:

```powershell
--llm-summary-dir "some/other/folder"
```

To disable the Markdown summary for a run:

```powershell
--no-llm-summary
```

## Scope

The exporter is country/year/specification agnostic. It uses the parsed
estimation results, active YAML specification, fit diagnostics, elasticities,
and identification diagnostics already computed by the post-estimation script.

If a future specification declares different opportunity blocks or shifters,
the Markdown parameter table is grouped from the YAML coefficient map where
available, then falls back to conservative parameter-name heuristics.
