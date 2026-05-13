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
- convergence status by result block;
- log-likelihood, null likelihoods, rho-squared, AIC, BIC, observations,
  groups, and parameters;
- observed vs predicted participation and mean hours by group;
- structural elasticity heuristics reported by the post-estimation script;
- marginal utility diagnostics;
- probability diagnostics and worst-fit households;
- Hessian/identification diagnostics;
- high-correlation parameter pairs;
- parameters at bounds;
- all parameter estimates grouped by model block;
- observed and predicted hours-bin shares.

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
