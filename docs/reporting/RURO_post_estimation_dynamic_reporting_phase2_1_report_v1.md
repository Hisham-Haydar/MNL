# RURO Post-Estimation — Phase 2.1 Report (v1)

## 1. Phase 2.1 verdict

Phase 2.1 succeeds. The CONOPT parser now produces an appendix-level
technical trace (final NSB, Step min/median/final, OK / MX shares,
inner-iteration stats, phase counts, warning indicators) that sits in
a collapsible "🔧 CONOPT Technical Trace (appendix)" block in both
HTML and Markdown. The main solver section is unchanged and remains
compact (solver status, model status, final objective, final RGmax,
infeasibility, Ninf, iterations, termination text). Backward
compatibility holds; non-CONOPT runs render the appendix as
*"Not applicable"* rather than emitting missing-field errors.

## 2. Files modified

* `scripts/enhanced/diagnostics_bundle.py`
  * New `parse_conopt_trace_from_text(text)` parser for CONOPT
    iteration rows + warning lines.
  * `build_diagnostics_bundle` now attaches
    `solver.data["conopt_trace"]` when the listing or solver-log
    parser emitted a trace dict and the solver family is CONOPT.
  * `not_applicable_fields` now includes `conopt_trace` for
    non-CONOPT solvers.
  * New renderers `render_conopt_trace_html` and
    `render_conopt_trace_markdown`.

* `scripts/enhanced/RURO_post_estimation_styled.py`
  * `_parse_listing_file` and `_parse_solver_log_file` now invoke
    `parse_conopt_trace_from_text` and store the result as
    `out["conopt_trace"]`.
  * `generate_html_report_styled` renders the CONOPT trace appendix
    right after the main solver bundle section.
  * `generate_llm_markdown_summary` renders the trace appendix right
    after the main solver Markdown block.

* `docs/reporting/RURO_post_estimation_dynamic_reporting_design_v1.md` —
  Phase 2.1 note appended.

## 3. CONOPT trace fields added

When the solver-log / listing-file parser captures a CONOPT iteration
table, the following fields populate `solver.data["conopt_trace"]`:

| Field                       | Type   | Source                                                |
|-----------------------------|--------|-------------------------------------------------------|
| `iteration_rows_parsed`     | int    | count of parsed iteration rows                        |
| `final_iteration`           | int    | last `Iter` index                                     |
| `final_objective`           | float  | last `Objective` / `Infeasibility` column             |
| `final_rgmax`               | float  | last `RGmax` column (CONOPT reduced gradient)         |
| `final_ninf`                | int    | last `Ninf` column                                    |
| `final_nsb`                 | int    | last `NSB` column (super-basic variables)             |
| `final_step`                | float  | last `Step` column                                    |
| `step_min`, `step_median`   | float  | across all parsed iteration rows                      |
| `ok_T_count`, `ok_F_count`  | int    | counts of `OK = T` and `OK = F`                       |
| `ok_T_share`, `ok_F_share`  | float  | shares (0..1)                                         |
| `mx_T_count`, `mx_F_count`  | int    | counts of `MX = T` / `MX = F`                         |
| `mx_T_share`                | float  | share of `MX = T` iterations                          |
| `in_itr_max`, `in_itr_mean` | int/float | over `InItr` column across parsed rows             |
| `phase_counts`              | dict   | `{phase_str: n_iterations_in_that_phase}`             |
| `warnings`                  | dict   | detected CONOPT warning categories (see below)        |

`warnings` carries:

* `evaluation_errors` — integer count parsed from the `EVALUATION
  ERRORS  N  M` listing line (summed);
* `domain_errors` — integer count from a `DOMAIN ERRORS N` line;
* `scaling`, `slow_convergence`, `time_limit`, `iteration_limit`,
  `infeasibility` — Booleans set when matching CONOPT warning text
  patterns appear;
* `warning_lines` — up to 20 raw lines from the artifact whose
  lower-cased text contains `warning`.

## 4. Technical solver appendix rendering

The trace lives in a single collapsible `<details>` block in the HTML
report, titled "🔧 CONOPT Technical Trace (appendix)" and placed
**after** the main solver section. The block carries:

* a scalar table (the fields in §3);
* a phase-count sub-table;
* a CONOPT warning-indicator sub-table plus an optional raw
  warning-lines bullet list.

In the LLM Markdown summary the same content appears under
`## CONOPT Technical Trace (appendix)` and is also placed after the
`## Solver Diagnostics` block. Both views render from
`solver.data["conopt_trace"]`, so HTML and Markdown stay in lock-step.

## 5. Main solver section unchanged

The compact bundle-driven solver section is unmodified by Phase 2.1.
It continues to render:

| Field                                          | Phase 2.1 behavior                  |
|------------------------------------------------|-------------------------------------|
| Solver name + family                           | unchanged                           |
| Objective / log-likelihood                     | unchanged                           |
| Wall time (seconds)                            | unchanged                           |
| **Solver status** (e.g. "Normal Completion")   | unchanged                           |
| **Model status** (e.g. "Locally Optimal")      | unchanged                           |
| **RGmax** (terminal reduced gradient)          | unchanged                           |
| **Termination text**                           | unchanged                           |
| **Max infeasibility**                          | unchanged                           |
| Equations / Variables / Nonzeros               | unchanged                           |
| Per-group convergence (non-CONOPT)             | unchanged                           |

No CONOPT trace fields are promoted to the main section. The trace
is appendix-only.

## 6. Non-CONOPT behavior

When `solver_family` is not `conopt`:

* `solver.data["conopt_trace"]` is omitted entirely;
* `solver.data["not_applicable_fields"]` includes `conopt_trace`;
* the HTML appendix renders a single-line "Not applicable: solver is
  X (family=Y); CONOPT iteration-trace fields are CONOPT/GAMS-specific."
  inside the collapsible block;
* the Markdown appendix renders the same one-line message under the
  `## CONOPT Technical Trace (appendix)` heading.

This is by design — a clearly labelled "not applicable" is a stable
signal for downstream consumers, not a missing-field error.

## 7. HTML and Markdown parity

Both renderers (`render_conopt_trace_html` and
`render_conopt_trace_markdown`) consume the same
`solver.data["conopt_trace"]` dict. The renderers branch identically
on three cases:

* solver section not available → empty render (HTML) / one-line note
  (Markdown);
* non-CONOPT family → "Not applicable" message;
* CONOPT but no trace → "trace not available in supplied artifacts"
  message;
* CONOPT with trace → full scalar + phase + warnings render.

This preserves the Phase-2 parity guarantee: same data, same
availability gating, same wording.

## 8. Validation performed

* `python scripts/enhanced/RURO_post_estimation_styled.py --help` —
  flags intact.
* **Single-year FR-2016 (non-CONOPT, no new options)** —
  * `solver_family = bfgs`,
  * `conopt_trace` absent from bundle,
  * `not_applicable_fields` includes `conopt_trace`,
  * HTML appendix carries *"Not applicable: solver is L-BFGS-B
    (family=bfgs); CONOPT iteration-trace fields are CONOPT/GAMS-
    specific."*,
  * No CONOPT field appears as a missing-field error,
  * Markdown summary mirrors the HTML.
* **Pooled P3a corrected, with `--cluster-se-json`, `--solver-log`,
  `--listing-file`, `--gamspy-diagnostics`, `--report-profile full`** —
  * `solver_family = conopt`,
  * Main solver section: `rgmax = 5.4e-08`, `solver_status = "Normal
    Completion"`, `model_status = "Locally Optimal"` — unchanged
    from Phase 2,
  * `solver.data["conopt_trace"]`:
    * `iteration_rows_parsed = 4`, `final_iteration = 14`,
    * `final_objective ≈ -19084.331307`, `final_rgmax = 5.4e-08`,
    * `final_nsb = 54`,
    * `step_min = 1.0`, `step_median = 1.0`,
    * `ok_T_count = 3, ok_F_count = 0, ok_F_share = 0.0`,
    * `mx_T_count = 0, mx_T_share = 0.0`,
    * `in_itr_max = 13`, `in_itr_mean = 10.0`,
    * `phase_counts = {"4": 4}`;
  * HTML appendix renders all of the above plus the phase-count
    sub-table; Markdown summary mirrors it.
  * Trace section appears **after** the main solver section in both
    formats (positionally verified).

Estimation was **not** rerun; solver was **not** invoked.

## 9. Remaining limitations

* The CONOPT trace parser captures only the *summary* iteration rows
  CONOPT prints (typically every 5–10 iterations + the final). A full
  per-iteration trace would require parsing the GAMS PROFILE output
  or a `CONOPT.OPT` file with `outdiff = yes`. Out of scope for this
  phase.
* The warning detector recognises a fixed set of CONOPT keywords. New
  CONOPT messages introduced by future versions need to be added to
  `text_warning_patterns` in `parse_conopt_trace_from_text`.
* `phase_counts` reports raw counts of parsed iteration rows in each
  phase, not their wall-clock or function-evaluation cost.
* The trace currently does not separate "input-point" rows
  (Phase 0 setup) from "real" iteration rows; in practice both header
  variants ("Infeasibility" header for Phase 0 setup,
  "Objective" header for the main solve) are parsed but a single row
  near the start may show `step` absent. Downstream consumers should
  trust `final_iteration` + `iteration_rows_parsed`, not the absolute
  count of rows.
* RGmax disambiguation: `final_rgmax` is **CONOPT/GAMS reduced
  gradient**. It is *not* the Python likelihood-gradient (score at θ);
  the latter lives in `bundle.gradient_score` and is populated only
  when `--gradient-diagnostics` is supplied. Both renderers label
  this explicitly.

## 10. Next recommended phase

Phase 3 should consider:

1. **Per-iteration CONOPT trace plot** — exposing the entire RGmax /
   infeasibility / Step trajectory as a small inline SVG or PNG in
   the HTML appendix, sourced from the parsed iteration rows.
2. **CONOPT.OPT parsing** — when a user supplies a CONOPT options file
   alongside the listing, parse the active tolerance settings
   (`Tol_Optimality`, `Lim_Iteration`, `Lim_Time`, etc.) and include
   them in the appendix.
3. **GAMS PROFILE merge** — when `PROFILE = 1` is set, GAMS emits a
   per-block profile of generation / solve / output costs; parse and
   surface that under a sibling "GAMS Profile (appendix)" block.
4. **Cross-run trace comparison** — promote
   `comparison_diagnostics` (already in `extended_diagnostics.json`)
   to also expose two `conopt_trace` dicts side-by-side for
   stability-of-convergence diagnostics across re-runs.
