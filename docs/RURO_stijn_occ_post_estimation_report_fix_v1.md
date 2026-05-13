# RURO post-estimation report fix — spec-driven equation & parameter sections

Date: 2026-05-13

## Goal

Stop the post-estimation HTML report from putting Stijn-style M0 opportunity
parameters under a generic "Other Parameters" heading and from displaying
`log h(h|X) = (no hours parameters)`. Replace the hard-coded substring-match
rendering with a spec-driven renderer that reads the active YAML
specification and adapts to whichever opportunity blocks and shifters it
declares — country/year/spec agnostic.

This change is reporting-only. It does not touch the estimator, the model
parameters, or the estimation results.

## Files changed

| File | Change |
| --- | --- |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Added spec-driven equation renderers and a YAML-driven parameter classifier; rewired the model-specific HTML assembly to use them; kept legacy renderers as a fallback. |
| `docs/RURO_stijn_occ_post_estimation_report_fix_v1.md` | This note. |

No other scripts touched. No estimation re-run.

## What was wrong in the old report

Looking at the previous output of
`fr_2016_stijn_occ_gamspy_post_estimation_report_*.html` for the
`run_2026-05-13_11-27-40` estimate of `M0_stijn_occ`:

1. **`Hours Opportunity Function (All Groups)` showed
   `log h(h|X) = (no hours parameters)`.**
   The legacy renderer (`build_hours_opportunity_html_dynamic`) hard-coded
   parameter names from the older Stijn-style spec (`beta_work`, `beta_pt1`,
   `beta_ft`, `beta_gsur`, …). The current `M0_stijn_occ` YAML uses
   `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`, `beta_E_gsur`,
   `beta_E_educH`. None of these names matched any of the hard-coded checks,
   so the equation came up empty.

2. **The wage equation omitted `beta_w_pexp` and `beta_w_pexp2`.**
   The legacy renderer (`build_wage_equation_html_dynamic`) looked for
   `beta_pexp` / `beta_pexp2` (without the `_w_`), so the experience terms
   declared in the YAML were never displayed even though they were estimated.

3. **No occupation-opportunity equation was rendered at all.**
   The legacy renderer had no concept of the
   `occupation_opportunity` block. The 12 `beta_occ_*_{sm,sf,cm,cf}`
   parameters were therefore landing under the generic "Other Parameters"
   table (alongside `beta_E`, `beta_E_gsur`, `beta_E_educH`, `beta_h_ft`,
   etc.), giving the impression those were unclassified leftovers.

4. **The classifier itself was substring-based and brittle.**
   `classify_param` matched `beta_w` / `beta_pexp` / `sigma` / `beta_work` /
   `beta_pt` / `beta_ft` / `beta_gsur` by string containment, so:

   - `beta_E` → "other" (no match).
   - `beta_h_ft` → "other" (the check was `'beta_ft'`, which is *not* a
     substring of `beta_h_ft`).
   - `beta_E_gsur` → "other" (the check was `'beta_gsur'`, which is *not*
     a substring of `beta_e_gsur`).
   - `beta_E_educH` → "other".
   - `beta_occ_*` → "other".

   In total, 16 of the 52 estimated coefficients were ending up under
   "Other Parameters" simply because of name mismatches against assumptions
   from an older spec.

## The new approach: spec-driven rendering

`scripts/enhanced/RURO_post_estimation_styled.py` now re-reads the active
YAML directly (via `run_metadata['spec_config_path']`) to recover the four
opportunity blocks separately:

- `hours_opportunity.shifters`
- `market_opportunity.shifters` (only the non-occupation residual block —
  the parser appends occupation shifters here for the engine, but we use
  the raw YAML, so they stay distinct)
- `wage_opportunity.mean_shifters` and `wage_opportunity.variance.parameter`
- `occupation_opportunity.shifters` (plus `variable`, `reference`)

Each block drives both an equation section and the parameter-table
classifier, so the report is identical for any country/year/spec that
declares those blocks. Group routing for occupation shifters reads
`applies_to` (sm/sf/cm/cf).

### Key helpers added

| Function | Purpose |
| --- | --- |
| `_load_yaml_spec_blocks(spec_path)` | Re-parses the YAML and returns the four blocks plus utility-block metadata. |
| `_coef_to_block_map(blocks)` | Maps every coefficient name declared in any block to its block category. |
| `_strip_group_suffix(name)` / `_strip_group_prefix(name)` | Tolerates `beta_l0_sm`, `joint.beta_E`, etc. |
| `_classify_param_via_blocks(name, coef_map)` | Looks up the parameter via exact, prefix-stripped, suffix-stripped, or both-stripped match. |
| `_shifter_symbolic_term(sh)` / `_shifter_numerical_term(sh, value)` | Render `coef · var [· interaction1 · interaction2 …]` symbolically or with a numeric coefficient. |
| `_pick_value_for_group(coef, group, parsed_params)` | Resolves a coefficient's estimate for a specific group, with suffix fallback (`coef_sm`, etc.). |
| `build_model_index_equation_html(blocks)` | Top-level `V_ij = U + O^E + O^H + O^W + O^Occ − log prior` (terms hidden if their block is absent). |
| `build_employment_hours_opportunity_html_specdriven(blocks, parsed_params, group_labels)` | Symbolic + numerical-by-group rendering of `hours_opportunity.shifters ⊕ market_opportunity.shifters`. |
| `build_wage_opportunity_html_specdriven(blocks, parsed_params, group_labels)` | Symbolic + numerical-by-group rendering of `wage_opportunity.mean_shifters` and `σ`. |
| `build_occupation_opportunity_html_specdriven(blocks, parsed_params, group_labels)` | One sub-section per `applies_to`, symbolic + numerical, with the YAML's reference category shown. |

### How parameter classification maps to the M0 model

Coefficients are categorised once at the start of the parameter-table
section by `_coef_to_block_map(blocks)`:

| YAML block (raw, before parser-merge) | Param-table category | Section title in the report |
| --- | --- | --- |
| `utility.consumption` / `utility.leisure` (intercepts, shifters, θ exponents) | `preference` | Preference Parameters (Utility Function) |
| `hours_opportunity.shifters` | `hours_opp` | Employment and Hours Opportunity Parameters |
| `market_opportunity.shifters` (non-occupation) | `hours_opp` | Same Employment/Hours section (working-gated market access) |
| `wage_opportunity.mean_shifters` + `wage_opportunity.variance.parameter` | `wage_opp` | Wage Opportunity / Mincer Parameters |
| `occupation_opportunity.shifters` | `occupation_opp` | Occupation Opportunity Parameters |
| `beta_offer_*` (job-choice models) | `market_opp` | Job Market Opportunity Parameters |
| anything else | `other` | Other Parameters (omitted entirely if empty) |

For `M0_stijn_occ` this resolves cleanly:

- Preference: 26 params (`beta_c*`, `beta_l*`, `theta_c*`, `theta_l*`).
- Employment and Hours Opportunity: `beta_E`, `beta_h_pt1`, `beta_h_pt2`,
  `beta_h_ft`, `beta_E_gsur`, `beta_E_educH`.
- Wage Opportunity / Mincer: `beta_w0`, `beta_w_educL`, `beta_w_educH`,
  `beta_w_pexp`, `beta_w_pexp2`, `sigma`.
- Occupation Opportunity: all 12 `beta_occ_{2,3,4}_{sm,sf,cm,cf}`.
- Other Parameters: **empty / section absent**.

### How equation rendering supports country/year/spec agnosticism

- Nothing in the new renderers is keyed on the `stijn_occ_M0` spec name,
  on FR/2016, or on specific parameter names.
- A spec declaring different shifters (e.g. a future M1 with
  age-on-employment, or a Belgian variant with different focal-hours
  bands) will get a correctly populated equation as long as the YAML
  uses the four standard opportunity blocks.
- If the YAML cannot be loaded (path missing, parse error), the renderer
  falls back to the legacy hard-coded renderers, so old runs keep working.
- The model-index equation at the top of the report adapts: a spec without
  an occupation block simply omits `O^Occ` from `V_ij`.

## Regenerated HTML report

```text
U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/stijn_occ/
  gamspy/estimation_spec_stijn_occ_M0/run_2026-05-13_12-10-38/
  fr_2016_stijn_occ_gamspy_specdriven_post_estimation_report_20260513_121058.html
```

Source artefacts:

- Estimation results (unchanged):
  `outputs/estimates/fr/spec/stijn_occ/gamspy/estimation_spec_stijn_occ_M0/run_2026-05-13_11-27-40/estimation_results.json`
- MNL parquets used for fit diagnostics:
  `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__{singles,couples}.parquet`
- Spec used for equation rendering:
  `scripts/enhanced/estimation_spec_stijn_occ_M0.yaml`

Verification of section presence (raw counts of headings in the HTML):

| Heading | Occurrences |
| --- | --- |
| Model Index | 1 |
| Employment and Hours Opportunity | 2 (equation section + table title) |
| Wage Opportunity / Mincer | 2 |
| Occupation Opportunity | 2 |
| Other Parameters | 0 (section omitted because empty) |
| `(no hours parameters)` placeholder | 0 |

## Preserved diagnostics and outputs

The following report elements are untouched by this change and were
verified present in the regenerated HTML:

- Convergence diagnostics, identification diagnostics (Hessian eigenvalues,
  condition number, eigenvector-based weak-identification panel)
- MUC / MUL well-behavedness panels and comparison plots
- Marginal utility μ contour plots for the four couple sub-groups
- Hours-distribution and wage-distribution observed-vs-predicted plots
- Participation and mean-hours fit tables and plots
- Elasticities table (CSV + HTML)
- Parameter CSV exports per group
- Bounded-parameter highlighting (hit-bound / bounded rows) and p-value
  colour coding

## Remaining reporting limitations

- **Legacy `Group-Specific Parameters` section still needs cleanup.**
  The new spec-driven opportunity equation sections and the new
  "Parameter Estimates by Category" section are correctly separated, but the
  older `Group-Specific Parameters` block is still emitted later in the HTML.
  In the joint `M0_stijn_occ` report it can show parameters from other groups
  under a group heading, for example couple-male or couple-female occupation
  parameters under single-male/single-female headings. Until that legacy block
  is removed or rewritten, use the spec-driven opportunity sections and the
  categorized parameter tables as the authoritative parameter display.
- **Per-group numerical equations** for the employment/hours and wage
  blocks rely on `ParsedParameters.groups`. In joint estimation the parser
  collapses to a single `joint` group; the renderer therefore shows one
  consolidated numerical line. If the user wants four separate lines
  (sm/sf/cm/cf) for these blocks, the joint-result parser needs to expose
  per-group views — that is independent of this fix.
- **Group labels** still use the short identifiers (`sm`, `sf`, `cm`, `cf`,
  `joint`). The renderers accept a `group_labels` mapping so longer
  display names can be plugged in later without code changes.
- The fallback path for `applies_to: "both"` shifters lands the rendered
  section in a single `both` group block in the occupation equation;
  splitting per group would require an additional pass over
  `ParsedParameters.groups` and is not required for the M0 spec (which
  fully partitions `applies_to` across sm/sf/cm/cf).
- Pre-existing static-typing warnings in legacy hard-coded renderers
  (`build_hours_opportunity_html_dynamic`,
  `build_wage_equation_html_dynamic`, …) are unchanged. Those functions
  remain as fallbacks but are not exercised when the YAML loads cleanly.
- This fix touches only the regular RURO path. Job-choice (`beta_offer_*`)
  reports retain their existing dedicated section verbatim.
