# RURO Post-Estimation — Phase 2 Migration Report (v1)

## 1. Phase 2 verdict

Phase 2 succeeds. Four additional sections are now rendered from the
shared `DiagnosticsBundle` in both the styled HTML report and the
LLM/Markdown summary: per-block parameter table, identification /
Hessian diagnostics, solver / convergence diagnostics, and probability
/ fit diagnostics. CONOPT RGmax is now parsed from the CONOPT
iteration-log tabular format. Solver-family classification is
specification-agnostic and falls back gracefully when the
`opt_method` field in `estimation_results.json` is misleading.
Backward compatibility holds: old single-year commands continue to
produce the same legacy artifacts (now rendered alongside the
bundle-driven views).

## 2. Files modified

* `scripts/enhanced/diagnostics_bundle.py` —
  * solver-family classification (CONOPT / IPOPT / KNITRO / BFGS /
    trust-constr / other / unknown);
  * CONOPT iteration-log RGmax extractor
    (`parse_conopt_rgmax_from_text`) and CONOPT termination-text
    extractor (`parse_conopt_termination_text`);
  * `block_map` argument to `build_diagnostics_bundle` plus the
    specification-agnostic `_block_for_param` helper;
  * inference rows now carry `block`;
  * hessian section enriched with `eigenvalues`,
    `top_correlations`, `poorly_identified_params`,
    `eigenvector_diagnostics`;
  * solver section carries `solver_family`,
    `not_applicable_fields`, `not_applicable_note`;
  * new HTML renderers: `render_param_table_html`,
    `render_identification_html`, `render_solver_html`,
    `render_probability_fit_html`;
  * new Markdown renderers: `render_param_table_markdown`,
    `render_identification_markdown`,
    `render_probability_fit_markdown`.

* `scripts/enhanced/RURO_post_estimation_styled.py` —
  * pre-load cluster-SE / solver-log / listing-file inputs in
    `run_styled_post_estimation` and feed them into the bundle build
    *before* HTML render;
  * wire CONOPT iteration-log RGmax parser into both
    `_parse_listing_file` and `_parse_solver_log_file`;
  * pass `block_map` (derived from the existing YAML
    `_coef_to_block_map`) into both bundle builds;
  * inject four new bundle-driven sections into the styled HTML
    (solver, identification, probability-fit, per-block parameters);
  * inject the same four sections into the LLM Markdown summary;
  * rename the legacy "Parameter Estimates by Category" HTML heading
    to "(legacy view)" so the bundle-driven block view is the
    canonical Phase-2 source.

* `docs/reporting/RURO_post_estimation_dynamic_reporting_design_v1.md` —
  Phase-2 update appended under §17 with a pointer to this report.

## 3. Bundle sections migrated

| Section            | Phase 1 status          | Phase 2 status                                                                   |
|--------------------|-------------------------|----------------------------------------------------------------------------------|
| Fit-stats A/B/C/D  | Bundle-driven (HTML+MD) | unchanged                                                                        |
| Inference table    | JSON + CSV only         | now also rendered as **per-block tables** in HTML and Markdown                   |
| Solver / convergence | JSON only             | **HTML + Markdown** sections with solver-family branching                        |
| Identification / Hessian | JSON only         | **HTML + Markdown** sections (cond #, eigenvalues, correlations, poorly-id'd)    |
| Probability fit    | JSON only               | **HTML + Markdown** sections (prob-sum, p_chosen dist, worst-fit households)     |

## 4. Parameter table migration

The bundle's `inference.data["rows"]` is enriched with a `block` field
derived from `_block_for_param(name, block_map)`. `block_map` is built
by `RURO_post_estimation_styled.py` from the existing
`_coef_to_block_map(yaml_spec_blocks)` and passed into the bundle
builder. When the YAML map does not classify a parameter, the bundle
falls back to substring heuristics that are not country-, year-, or
model-specific (e.g. `beta_w*` → `wage_opportunity`,
`beta_occ_*` → `occupation_opportunity`, etc.).

The HTML renderer (`render_param_table_html`) emits one sub-table per
block (`preference`, `employment_hours_opportunity`,
`market_opportunity`, `wage_opportunity`, `occupation_opportunity`,
`other`), each carrying `estimate`, `se_hessian`, `t_hessian`,
`se_robust`, `t_robust`, `p_robust`, `fixed`, `at_lower`, `at_upper`,
`primary_se`. The Markdown renderer
(`render_param_table_markdown`) emits the equivalent tables.

The legacy "Parameter Estimates by Category" HTML section is kept and
renamed *(legacy view)*; it draws from the same parameter dataframe so
numbers match.

## 5. Identification diagnostics migration

The bundle's `hessian` section now carries the full payload that the
legacy `generate_identification_diagnostics_html` consumed
(`condition_number`, `min_eigenvalue`, `max_eigenvalue`,
`n_negative_eigenvalues`, `eigenvalues`, `top_correlations`,
`poorly_identified_params`, `eigenvector_diagnostics`).

`render_identification_html` renders:

* the scalar table (with inline warnings for κ > 10¹⁰ and negative
  eigenvalues);
* a bullet list of poorly-identified parameters (first 30 shown);
* a top-15 parameter-correlation table.

`render_identification_markdown` renders the same information in
Markdown. The legacy HTML panel is preserved next to the bundle
section.

## 6. Solver diagnostics migration

`render_solver_html` and the updated `render_solver_section_markdown`
branch on `solver_family`:

* `conopt` → render solver status, model status, RGmax, termination
  text, max infeasibility, equations / variables / nonzeros, solve
  time;
* `bfgs` / `ipopt` / `knitro` / `trust-constr` / `other` → render
  per-group success / message / iterations / nfev / gradient_norm
  from the results JSON, and emit a clear note listing CONOPT-only
  fields that are *not applicable* to this solver.

`solver_family` is classified from the solver name; if the metadata
`opt_method` is a misleading fallback (e.g. an estimator records
`"L-BFGS-B"` but actually ran CONOPT), the bundle overrides the
classification when:

* a non-empty CONOPT listing-file dict is available; *or*
* a CONOPT-style solver-log dict is available; *or*
* `metadata.solver_artifacts.saved` is true.

This makes the classification robust across solvers without
hard-coding country, year, model, or solver assumptions.

## 7. Probability and fit diagnostics migration

`render_probability_fit_html` and `render_probability_fit_markdown`
both consume `bundle.probability_fit.data`:

* `prob_sum_errors` (per-key table);
* `p_chosen_dist` (per-key table);
* `worst_fit_households_top10` (rank, idhh, group, p_chosen, ll_i).

In Phase 1 these existed only in JSON; in Phase 2 they appear in HTML
*and* Markdown driven from the same data.

## 8. HTML and Markdown parity

Both formats now consume the same `DiagnosticsBundle` for:

* A/B/C/D fit statistics (Phase 1);
* per-block parameter table (Phase 2);
* identification / Hessian (Phase 2);
* solver / convergence (Phase 2);
* probability fit (Phase 2).

Phase-2 sections all check `Section.available`; if a section is
unavailable, the renderer prints the same "Not available because …"
sentence in both formats (the unavailable_reason text is shared).

## 9. CONOPT RGmax parsing

`parse_conopt_rgmax_from_text(text)` recognises the CONOPT iteration
table headers (`Iter Phase Ninf Infeasibility RGmax NSB …` *and*
`Iter Phase Ninf Objective RGmax NSB …`) and walks subsequent
numeric rows. The 5th numeric column is RGmax in CONOPT's standard
format (scientific notation). The function returns the **last**
RGmax value seen across all iteration blocks, which is the terminal
value at convergence.

Validation: parsed `5.4e-08` from the pooled P3a corrected run's
`solver.lst` iteration table where CONOPT prints
`14   4  -1.9084331307E+04 5.4E-08`. The previous Phase-1 parser
expected `RGmax = value` form and returned `None` for the same file.

`parse_conopt_termination_text(text)` captures the CONOPT termination
sentence (e.g. *"Optimal solution. Reduced gradient less than
tolerance."*) and exposes it as `termination_text` for the solver
section.

## 10. Non-CONOPT solver handling

For BFGS / L-BFGS-B / IPOPT / KNITRO / trust-constr / other:

* `bundle.solver.data["solver_family"]` is set to the appropriate
  value;
* the HTML and Markdown solver renderers omit the CONOPT-specific
  rows;
* `not_applicable_fields` lists `rgmax`, `model_status`, `equations`,
  `variables`, `nonzeros`, `max_infeasibility`, `generation_time_s`,
  `solve_time_s` (the ones that are CONOPT-only);
* a `not_applicable_note` sentence is emitted next to the table:
  *"Solver is 'L-BFGS-B' (family=bfgs); CONOPT/GAMS-specific fields
  are not applicable."*

This satisfies the requirement that unavailable metrics state *why*
they are unavailable rather than silently dropping.

## 11. Backward compatibility

* Existing commands work unchanged (`--help`, the legacy single-year
  command, and the existing pooled P3a + cluster-SE + solver-log +
  listing-file + gamspy-diagnostics command).
* No CLI flag default has changed.
* The default profile is still `standard`; the bundle-driven sections
  appear in `standard` and `full`.
* Legacy HTML sections are kept (renamed *(legacy view)* where the
  bundle replaces them) so any downstream consumer that scraped the
  legacy text still finds it.
* `diagnostics_bundle.json`, `enhanced_parameter_table.csv`,
  `solver_diagnostics.json` and `inference_diagnostics.json` are
  unchanged in name and shape; only their contents are richer (the
  per-row `block` field is new; the rest is additive).

## 12. Validation performed

* `python scripts/enhanced/RURO_post_estimation_styled.py --help` —
  confirmed `--report-profile`, `--cluster-se-json`, `--solver-log`,
  `--listing-file`, `--gradient-diagnostics`, `--gamspy-diagnostics`
  all present.
* **Smoke 1**: single-year FR-2016 GAMSPy run (no new flags) —
  produced all legacy artifacts + bundle JSON / CSV / solver-
  diagnostics JSON. HTML contains all four reorganized fit sections,
  the bundle-driven solver section (correctly noting `bfgs` family
  with CONOPT-not-applicable fields), the bundle parameter table
  (block distribution `preference: 33, wage_opportunity: 12,
  employment_hours_opportunity: 4`), and the legacy "(legacy view)"
  sections. Markdown summary contains the same parity sections.
* **Smoke 2 (corrected pooled P3a, with `--cluster-se-json`,
  `--solver-log`, `--listing-file`, `--gamspy-diagnostics`,
  `--report-profile full`)** — produced:
  * `solver_family=conopt` (auto-corrected from the misleading
    `opt_method=L-BFGS-B` metadata via listing-file detection);
  * `rgmax=5.4e-08` (parsed from the CONOPT iteration log);
  * `solver_status="Normal Completion"`,
    `model_status="Locally Optimal"`;
  * `primary_se_for_run=robust` (cluster-SE primary; Hessian
    diagnostic);
  * block distribution: `preference: 23,
    employment_hours_opportunity: 14, occupation_opportunity: 12,
    wage_opportunity: 6`;
  * Hessian section: `condition_number ≈ 3.32e9`,
    `n_negative_eigenvalues=5` (warning surfaced);
  * HTML carries all four bundle sections plus the legacy panels.
* Estimation was **not** rerun; solver was **not** invoked.

## 13. Remaining limitations

* The legacy "Parameter Estimates by Category" HTML section, the
  legacy `generate_identification_diagnostics_html` panel, and the
  legacy `prob_diag_html` block are **kept side-by-side** with the
  new bundle-driven sections for backward compatibility. Removing
  them entirely is a Phase-3 cleanup once downstream consumers have
  migrated to the bundle JSON.
* CONOPT RGmax parser handles the "Objective" and "Infeasibility"
  header variants; other CONOPT iteration-log layouts (e.g. KNITRO
  format, mixed-objective columns) are not yet recognised.
* `bundle.solver` does not yet split per-group success/message for
  CONOPT; it shows the listing-file aggregate plus a per-group block
  carried over from the results JSON. This is sufficient for
  CONOPT joint runs but should be revisited if a CONOPT run produces
  per-group convergence output.
* Welfare diagnostics still have no input plumbing — by design.
* No per-choice-set score sign check is computed.

## 14. Next recommended phase

Phase 3 should focus on:

1. **Legacy section removal under `standard` / `full` profile** —
   keep the legacy renderers only under `technical` for one release
   cycle, then delete them entirely.
2. **Inference-table sign visualisation** — render `p_robust`-coded
   significance stars in the bundle HTML to match the legacy "by
   category" view feature parity, then retire the legacy view.
3. **Welfare input contract** — define `--welfare-json` and have
   `build_diagnostics_bundle` consume it.
4. **Per-iteration CONOPT trace** — capture the full RGmax /
   infeasibility trajectory for diagnostic plots.
5. **Cross-run comparison in the bundle** — promote the comparison
   block from `extended_diagnostics.json` into the bundle so the
   styled HTML can render comparison tables alongside primary
   results.
