# RURO Post-Estimation — Dynamic, Model-Aware Reporting (Design v1)

## 1. Purpose

Make the styled HTML report and the LLM/Markdown summary produced by
`scripts/enhanced/RURO_post_estimation_styled.py` dynamic, model-aware,
solver-aware and specification-agnostic. The package must work across
countries, years, model specifications and solvers — CONOPT/GAMSPy and
non-CONOPT (BFGS / L-BFGS-B / SciPy) — and the same numbers must appear
in HTML and Markdown.

## 2. Problem in current reporting

The legacy HTML report dumped every key in `fit_stats` into a single
**Model Fit Statistics** table. This mixed:

* true fit metrics (log-likelihood, AIC, BIC);
* null-model and pseudo-R² values whose interpretation depends on the
  null model used;
* bound diagnostics (`n_bounded_params`, `n_hit_lower_bound`);
* economic sanity checks (negative MUC / MUL counts).

The Markdown summary built its own `## Fit Statistics` table from the
same dict but separately, so HTML and Markdown could drift if either
side changed. There was no shared in-memory schema and no machine-readable
diagnostics artifact for downstream tools.

## 3. Shared diagnostics bundle

`scripts/enhanced/diagnostics_bundle.py` introduces a `DiagnosticsBundle`
dataclass containing typed sections:

* `estimation_metadata` — specification, wage spec, group, opt method,
  command line, timestamp;
* `data_metadata` — n_observations, n_groups, alts-per-set, mnl_base;
* `spec_metadata` — n_parameters, n_free, n_fixed, n_with_bounds;
* `solver` — solver name, status, model status, RGmax (CONOPT only),
  iterations, function evaluations, wall time, termination text,
  per-group convergence info;
* `likelihood_fit_core` — log-likelihood, AIC, BIC, AIC/n_obs;
* `null_model_fit` — ll_null_uniform, ll_null_prior_corrected, all four
  ρ² variants, with an explicit comparability note;
* `bounds_diagnostics` — counts plus an `at_or_near_bounds` list;
* `economic_sanity` — negative-MUC/MUL counts, monotonicity violations;
* `inference` — per-parameter rows (estimate, SE_hessian, SE_robust,
  t_h, t_r, p_r, fixed/free, bound status, primary_se selector);
* `robust_se` — cluster-SE artifact summary (T3/T4/T5/PE3 checks);
* `hessian` — condition number, eigenvalue counts;
* `gradient_score` — Python likelihood-gradient diagnostics;
* `probability_fit` — prob-sum errors, p_chosen distribution, top-10
  worst-fit households;
* `reproducibility` — timestamp, python, platform, git, package hashes;
* `warnings` and `limitations`.

Each section is a `Section(available, unavailable_reason, data)` so the
renderer can either show the table or print a one-line explanation.

## 4. Metric registry

`METRIC_REGISTRY` in `diagnostics_bundle.py` declares each metric as a
`MetricSpec(key, label, category, source, applicability, interpretation,
precision, threshold, profiles, appendix_only)`. Renderers consult the
registry to format values, gate metrics by profile, and emit interpretation
notes alongside thresholds.

## 5. Dynamic section logic

`SECTION_PROFILES` maps each section to the profiles that render it.
`section_is_visible(section_name, profile)` decides at render time.
When a section is unavailable, the renderer prints a "Not available
because …" line that names the missing input (e.g. *"Cluster-robust
SEs unavailable: supply `--cluster-se-json`"*).

Concretely:

* **CONOPT RGmax**: rendered only when `solver_log` / `listing_file`
  is supplied and the solver name indicates CONOPT/GAMS.
* **BFGS / L-BFGS-B**: per-group `success`, `message`, `n_iterations`,
  `n_function_evaluations`, `gradient_norm` are rendered from the
  results JSON.
* **Cluster-robust SE / T3-T5**: rendered only when `--cluster-se-json`
  is supplied.
* **Python likelihood gradient**: rendered only when
  `--gradient-diagnostics` is supplied with `--mnl-base` and
  `--spec-config`.
* **Welfare**: not computed here. Will appear only if an explicit welfare
  artifact is supplied as an input (this feature is documented as a
  future extension).

## 6. Fit statistics reorganization

The single "Model Fit Statistics" dump is replaced by four reorganized
sections, rendered in this order in both HTML and Markdown:

* **A. Core likelihood and sample statistics** — log-likelihood, n_obs,
  n_groups, alts/set, n_free, n_fixed, AIC, BIC, AIC/n_obs.
* **B. Null-model and pseudo-R² diagnostics** — ll_null_uniform,
  ll_null_prior_corrected, ρ² (uniform and prior-corrected), adjusted
  variants, plus a comparability note.
* **C. Bound / fixed-parameter diagnostics** — n_parameters, n_free,
  n_fixed, n_with_bounds, n_at_lower, n_at_upper, and a list of
  parameters at or near bounds (with side and distance).
* **D. Economic sanity diagnostics** — negative MUC / MUL counts and
  percentages, monotonicity violations. Labelled clearly as *not* a
  model-fit statistic.

The legacy single-table dump is preserved inside a collapsed
`<details>` block in HTML and under a heading
*"Fit Statistics (legacy combined table — kept for backward
compatibility)"* in Markdown. Nothing is removed.

## 7. Solver diagnostics across solvers

`render_solver_section_markdown` (and the equivalent bundle fields)
branches on the solver name:

* `conopt` / `gams` → render solver status, model status, RGmax, max
  infeasibility, equations / variables / nonzeros, termination text;
* `bfgs` / `scipy` / `l-bfgs` → render per-group success flag, message,
  iterations, function evaluations, gradient norm from results JSON;
* anything else → render whatever solver fields are present, generically.

CONOPT RGmax is **never confused** with the Python likelihood
gradient — they live in different bundle sections.

## 8. Gradient and score diagnostics

`gradient_score` in the bundle is the Python likelihood-gradient at
converged θ. When `--gradient-diagnostics` is supplied with
`--mnl-base` + `--spec-config`, the existing
`_compute_gradient_diagnostics` is called, and the bundle is populated
with `inf_norm`, `l2_norm`, top-10 components and a label note:
*"This is NOT necessarily the solver reduced gradient when bounds or
constraints are active."*

## 9. Inference and robust SE reporting

`bundle.inference.data["rows"]` carries one row per parameter with:
`estimate`, `se_hessian`, `t_hessian`, `se_robust`, `t_robust`,
`p_robust`, `fixed`, `at_lower_bound`, `at_upper_bound`, `primary_se`.

When `cluster_se_data` is supplied, `primary_se` is `"robust"` and the
Hessian SE is labelled diagnostic/classical. Otherwise `primary_se` is
`"hessian"`. The `inference_diagnostics.json` artifact stores the full
per-parameter table; `enhanced_parameter_table.csv` provides the same
table in a spreadsheet-friendly form.

## 10. Bound and fixed-parameter diagnostics

Computed once in the bundle, used in both HTML and Markdown:

* counts: `n_parameters`, `n_free_parameters`, `n_fixed_parameters`,
  `n_parameters_with_bounds`, `n_at_lower_bound`, `n_at_upper_bound`;
* `at_or_near_bounds`: list of `{parameter, side, estimate, bound, distance}`
  using `tol_at_bound=1e-6` and `tol_near_bound=1e-3`.

## 11. Economic sanity diagnostics

These are emitted in a dedicated section **D**, never under "Model Fit
Statistics". Supported keys (sourced from `mu_results.totals` when MU
diagnostics are computed): `negative_muc_count`, `negative_muc_pct`,
`negative_mul_count`, `negative_mul_pct`, `monotonicity_violations`.

## 12. HTML and Markdown parity

Both renderers consume the **same** `DiagnosticsBundle`. HTML calls
`render_fit_stats_split_html(bundle)`; Markdown calls
`render_fit_stats_split_markdown(bundle)`. Both renderers honour
`section_is_visible(...)` for profile gating, so when the user switches
profile the same sections appear / disappear in both formats.

The HTML report can carry richer presentation (the existing model
specification panels, plots, collapsible technical sections); the
Markdown summary is the decision-relevant view plus links/paths to the
heavier artifacts on disk. Both are now driven by the same numbers.

## 13. Report profiles

`--report-profile` accepts `decision`, `standard` (default), `full`,
`technical`.

* **decision** — only adoption-relevant diagnostics: A, B, D, inference,
  warnings/limitations. No solver internals, no Hessian eigenvalues,
  no Python score.
* **standard** — A, B, C, D, inference, solver overview, robust SE
  (when present), reproducibility. *Default*.
* **full** — adds Hessian diagnostics, Python score, probability fit,
  worst-fit households.
* **technical** — full plus the legacy combined fit-stats appendix and
  all internal debug fields.

`SECTION_PROFILES` is the single source of truth for which profile
shows which section.

## 14. Output artifacts

Existing outputs continue to be produced:

* HTML report (`{prefix}post_estimation_report_{ts}.html`);
* Markdown/LLM summary under `reports/`;
* `{prefix}params.csv`, `{prefix}elasticities.csv`,
  `{prefix}params_with_se.csv` (when `--compute-se` was used).

New canonical artifacts written by `write_bundle_artifacts(...)`:

* `{prefix}diagnostics_bundle.json` — full bundle, single normalized
  schema;
* `{prefix}enhanced_parameter_table.csv` — per-parameter inference
  rows including primary-SE selector and bound status;
* `{prefix}solver_diagnostics.json` — only when the solver section is
  available (i.e. when solver metadata exists or solver-log/listing
  parsed cleanly);
* `{prefix}inference_diagnostics.json` — only when inference, robust SE,
  or Hessian data is available.

When `run_extended_diagnostics` runs in the same invocation with
`--cluster-se-json` / `--solver-log` / `--listing-file` /
`--gradient-diagnostics`, the bundle is rebuilt with those inputs and
the JSON is rewritten so it reflects the full set of available
diagnostics.

## 15. Backward compatibility

Existing commands keep working unchanged:

```bash
python scripts/enhanced/RURO_post_estimation_styled.py \
  --results-json   ... \
  --mnl-base       ... \
  --output-dir     ... \
  --prefix         ... \
  --spec-config    ... \
  --auto-timestamp \
  --compute-se
```

When `--report-profile` is omitted, `standard` is used. The legacy
single combined fit-stats table is preserved inside a collapsed
`<details>` block in HTML and under a clearly-labelled heading in
Markdown. All existing function signatures keep their previous
arguments; new arguments are added with safe defaults.

## 16. Validation performed

* `--help` confirms the new `--report-profile` flag with choices
  `{decision, standard, full, technical}`;
* a smoke run on an existing FR-2016 single-year result JSON (without
  any new options) produces all legacy artifacts plus the new
  `diagnostics_bundle.json` / `enhanced_parameter_table.csv` and the
  four reorganized fit-stats sections in both HTML and Markdown;
* a smoke run on the pooled P3a corrected results with
  `--cluster-se-json`, `--solver-log`, `--listing-file`,
  `--gamspy-diagnostics`, `--gradient-diagnostics` produces the
  enriched bundle (including CONOPT RGmax when present in the listing
  file and Python likelihood gradient when supplied).

Estimation was **not** rerun. The solver was **not** invoked.

## 17. Remaining limitations

### Phase-2 status (2026-05-22 update)

Phase 2 has migrated four further sections from legacy inline code to
the shared `DiagnosticsBundle`:

* **Parameter table by block** — `render_param_table_html` and
  `render_param_table_markdown` render one sub-table per block
  (`preference`, `employment_hours_opportunity`,
  `market_opportunity`, `wage_opportunity`, `occupation_opportunity`,
  `other`). Each row carries `block`, `estimate`, `se_hessian`,
  `t_hessian`, `se_robust`, `t_robust`, `p_robust`, `fixed`,
  `at_lower_bound`, `at_upper_bound`, `primary_se`. The block label is
  derived from the YAML spec via `_coef_to_block_map` when available,
  with substring fallbacks for legacy specs (no France / P3a / SA2
  hard-coding).
* **Identification & Hessian** — `render_identification_html` and
  `render_identification_markdown` consume the enriched
  `bundle.hessian` section (condition number, eigenvalue extremes,
  `n_negative_eigenvalues`, `poorly_identified_params`,
  `top_correlations`).
* **Solver & convergence diagnostics** — `render_solver_html` (and
  the existing `render_solver_section_markdown`) branch on
  `solver_family`. For CONOPT/GAMS they show RGmax, model status,
  termination text, equations / variables / nonzeros. For
  non-CONOPT solvers (BFGS / L-BFGS-B / IPOPT / KNITRO / trust-constr)
  they show per-group success / message / iterations / nfev /
  gradient_norm and emit a clear *"CONOPT-specific fields are not
  applicable"* note instead of silently omitting them.
* **Probability & fit summary** — `render_probability_fit_html` and
  `render_probability_fit_markdown` render `prob_sum_errors`,
  `p_chosen_dist` and the top-10 worst-fit households.

CONOPT RGmax is now parsed from the CONOPT iteration-log tabular
format (`Iter Phase ... RGmax NSB ...`) via
`parse_conopt_rgmax_from_text`, in addition to the explicit
`RGmax = value` and `Reduced gradient norm = value` patterns. The
last numeric RGmax value across all iteration blocks is taken as the
terminal value. The CONOPT termination sentence
(e.g. *"Optimal solution. Reduced gradient less than tolerance."*)
is captured as `termination_text`.

### What still remains

* The legacy "Parameter Estimates by Category" HTML section, the
  legacy `generate_identification_diagnostics_html` panel, and the
  legacy `prob_diag_html` block are **kept alongside** the new
  bundle-driven sections (each renamed *(legacy view)*). Removing
  them entirely is a Phase-3 cleanup once consumers have migrated
  to the bundle JSON.
* Score sign check (per-choice-set) is not yet computed in the
  bundle.
* Welfare diagnostics: the bundle has a slot in `SECTION_PROFILES`
  but still no input plumbing — will be added when a welfare
  artifact contract is defined.
* Metric thresholds in the registry are not yet surfaced as inline
  HTML warnings (the bundle's `warnings` list already surfaces them
  in the Markdown decision summary).

See [`docs/RURO_post_estimation_dynamic_reporting_phase2_report_v1.md`](RURO_post_estimation_dynamic_reporting_phase2_report_v1.md)
for the Phase-2 validation report.
