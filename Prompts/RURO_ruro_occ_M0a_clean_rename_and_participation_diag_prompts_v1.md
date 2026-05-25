# Claude Code Prompts - RURO ruro_occ_M0a-clean and Participation Diagnostic

Date: 2026-05-13

Purpose: cleanly re-parameterize M0a so the singles consumption curvature is
a true shared parameter, then diagnose the persistent predicted-participation
pathology using a read-only decomposition. These are two related tasks, but
they should be run sequentially for traceability.

Use Prompt 1 first. It patches and validates the M0a-clean specification but
does not run estimation. After the user runs the M0a-clean estimation and
post-estimation, use Prompt 2 to diagnose the participation issue.

## Why These Prompts Replace the Earlier Drafts

The earlier equality-constraint M0a used a hard constraint
`theta_c_sm = theta_c_sf`. That gives the intended likelihood restriction, but
post-estimation inverts an unconstrained Hessian, so correlations involving the
constrained consumption-curvature block can become non-PSD and even exceed
absolute value 1. That is a reporting artifact from the parameterization.

The clean fix is not to prune insignificant parameters. The clean fix is to
remove the redundant singles curvature parameter from the parameter vector.
This prompt therefore requires a true shared parameter named
`theta_c_singles`.

The participation diagnostic is kept separate. Predicted participation equal
to 1.0000 across groups survived M0 and M0a, so it is probably not fixed by
another YAML simplification. It needs a decomposition of the structural choice
index and the post-estimation aggregation.

---

# Prompt 1 - Implement ruro_occ_M0a-clean with true theta_c_singles

Work locally in my RURO/MNL codebase.

Read:

- `Results/RURO_occ_M0a_simplification_plan_v1.md`
- `docs/archive/2026-05-26_round2_chain_compression/replaced_by_clean_corrected/RURO_occ_M0a_implementation_report_v1.md`
- `scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml`
- `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml`
- `scripts/enhanced/estimation_spec_parser.py`
- `scripts/enhanced/estimation_engine.py`
- `scripts/enhanced/gamspy_estimation_vectorized.py`
- `scripts/enhanced/gamspy_estimation.py` if it exists and is still used
- the latest M0a `estimation_results.json` for context only, if present

Do not run full estimation.
Do not run post-estimation.
Do not edit MNL parquets, draw scripts, EUROMOD scripts, or job-choice code.

## Goal

Create a clean M0a specification where singles male and singles female share
one consumption Box-Cox curvature parameter:

```yaml
utility:
  consumption:
    coefficient: "beta_c"
    box_cox_exponent: "theta_c"
    singles_box_cox_exponent: "theta_c_singles"
```

The clean parameter vector must contain `theta_c_singles` and must not contain
`theta_c_sm` or `theta_c_sf`. Couples keep their existing shared `theta_c`.

Create:

- `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml`
- `docs/RURO_occ_M0a_clean_implementation_report_v1.md`
- `Results/_M0a_clean_spec_check.py`

## Required Implementation

Implement Route A only: a true renamed shared parameter.

Do not implement the fallback route where `theta_c_sm` is reused for singles
female. That route is shorter but semantically misleading and risks hidden
engine assumptions.

### Parser requirements

Modify `scripts/enhanced/estimation_spec_parser.py` narrowly so:

1. `utility.consumption.singles_box_cox_exponent` is optional.
2. If present, `_build_parameter_list` emits the named parameter once for the
   singles consumption curvature.
3. If present, `_build_parameter_list` does not emit `theta_c_sm` or
   `theta_c_sf`.
4. Couples consumption remains unchanged and still uses the ordinary
   `box_cox_exponent` parameter, currently `theta_c`.
5. Old specs without `singles_box_cox_exponent` still parse exactly as before.

Use a small parser metadata field or property if needed so the engines can
detect the shared singles curvature without hard-coding the M0a-clean spec
name.

### Engine requirements

Modify the estimation code paths narrowly and symmetrically:

- `scripts/enhanced/estimation_engine.py`
- `scripts/enhanced/gamspy_estimation_vectorized.py`
- `scripts/enhanced/gamspy_estimation.py` if present and relevant

Required behavior:

1. For singles male and singles female, use `theta_c_singles` when the parsed
   spec declares `utility.consumption.singles_box_cox_exponent`.
2. Fall back to the legacy `theta_c_sm` and `theta_c_sf` behavior when the key
   is absent.
3. Couples continue to use `theta_c`; do not route couples through
   `theta_c_singles`.
4. Do not touch the prior/proposal correction machinery.
5. Do not touch hours, wage, market, or occupation opportunity blocks except
   where a function signature must pass parser metadata through.

Audit every grep hit for `theta_c_sm`, `theta_c_sf`, `box_cox_exponent`, and
`consumption` in the touched engine files. Record the important hits in the
report.

### YAML requirements

Create `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` from the
current M0a YAML, then apply these exact changes:

1. Set `specification.name` to `ruro_occ_M0a_clean`.
2. Add `utility.consumption.singles_box_cox_exponent: "theta_c_singles"`.
3. Remove the hard equality constraint `theta_c_singles_pool`.
4. Remove any `param_diff` constraint linking `theta_c_sm` and `theta_c_sf`.
5. Remove `theta_c_sm` and `theta_c_sf` from `initial_values`.
6. Add `theta_c_singles: -1.0` to `initial_values`.
7. Remove `theta_c_sm` and `theta_c_sf` from bounds.
8. Add bounds for `theta_c_singles` equal to `[-8.0, 0.95]`.
9. Keep the two `mul_cou_*_positive` constraints verbatim.
10. Keep the four `beta_l_educH_*` leisure education shifters removed.
11. Do not change:
    - `hours_opportunity`
    - `wage_opportunity`
    - `market_opportunity`
    - `occupation_opportunity`
    - prior/proposal correction settings
    - MNL data paths
    - draw or EUROMOD settings

Expected final count: 47 estimated parameters.

## Validation Gates

Before declaring success, create and run:

```text
Results/_M0a_clean_spec_check.py
```

The script must print PASS/FAIL per gate and exit non-zero on any failure.

Gate A - M0a-clean parse:

- `spec.name == "ruro_occ_M0a_clean"`
- `len(spec.all_param_names) == 47`
- `theta_c_singles` is present
- `theta_c_sm` is absent
- `theta_c_sf` is absent
- all four `beta_l_educH_*` parameters are absent
- no expression constraint links any `theta_c_*` pair by `param_diff`
- the two `mul_cou_*_positive` constraints are still present

Gate B - backward compatibility:

- `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml` still parses.
- It still has 52 parameters.
- It still has separate `theta_c_sm` and `theta_c_sf`.
- Its opportunity blocks are unchanged.

Gate C - forward code-path check without estimation:

- Construct a tiny dummy singles dataset or minimal precompute object with a
  few singles male and singles female alternatives.
- Evaluate the consumption Box-Cox theta resolution path used by the engine.
- Verify both singles male and singles female use `theta_c_singles`.
- Verify no code path tries to read `theta_c_sf` under M0a-clean.
- If the exact engine forward pass cannot be invoked without a full
  optimization container, write a small resolver-level test and document the
  limitation clearly.

Gate D - syntax:

- Run `python -m py_compile` on every touched Python file and on the
  validation script.

## Report Requirements

Write:

```text
docs/RURO_occ_M0a_clean_implementation_report_v1.md
```

Include:

1. Files changed.
2. Why Route A (`theta_c_singles`) was chosen.
3. Exact YAML changes relative to equality-constraint M0a.
4. Parser changes with file and line references.
5. Engine changes with file and line references.
6. Validation gate results A-D.
7. A note that the equality-constraint M0a run is preserved as provenance but
   should not be cited as the clean M0a baseline.
8. Exact commands the user should run later for estimation and post-estimation.
9. Risks before re-estimation, especially any theta-related grep hits that
   were audited but not changed.

Do not run estimation. Stop after reporting the three output file paths and
the validation gate summary.

## Suggested User Commands After Prompt 1 Succeeds

These commands are for the user after the patch is validated. Do not execute
them in Prompt 1.

```powershell
python .\scripts\enhanced\enh_RURO_estimate_FR.py `
  --mnl-base "\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml" `
  --auto-timestamp `
  --verbose
```

```powershell
python .\scripts\enhanced\RURO_post_estimation_styled.py `
  --results-json "<LATEST_M0a_clean_RUN>/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/ruro_occ/gamspy" `
  --prefix "fr_2016_ruro_occ_gamspy_M0a_clean_" `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml" `
  --auto-timestamp `
  --compute-se
```

---

# Prompt 2 - Participation Pathology V-Decomposition Diagnostic

Run this only after Prompt 1 succeeds and after the user has run the
M0a-clean estimation and post-estimation.

Work locally in my RURO/MNL codebase.

Read:

- `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml`
- latest M0a-clean `estimation_results.json` under
  `outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/run_*/`
- latest M0a-clean low-token Markdown summary under `reports/`, if present
- `scripts/enhanced/estimation_engine.py`
- `scripts/enhanced/gamspy_estimation_vectorized.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`
- `scripts/enhanced/estimation_spec_parser.py`
- MNL parquets:
  - `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet`
  - `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet`

Fallback parquet paths if the Z drive is unavailable:

- `\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__singles.parquet`
- `\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl__couples.parquet`

Do not rerun estimation.
Do not modify Python or YAML files.
Do not modify parquet files.

## Symptom

Predicted participation was reported as 1.0000 for all four groups in the M0
and M0a post-estimation reports, while observed participation is below 1. This
survived a specification simplification, so diagnose whether the root cause is:

- post-estimation reporting,
- structural engine/index construction,
- prior/proposal correction,
- or a real specification artifact.

## Deliverables

Create:

- `Results/_participation_diag_ruro_occ_M0a_clean.py`
- `Results/_participation_diag_ruro_occ_M0a_clean.json`
- `Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md`

The diagnostic script must be reusable, deterministic, read-only on inputs,
and runnable in under five minutes.

## Group Definitions

Use these definitions:

- `singles_male`: singles parquet with `dgn == 1`
- `singles_female`: singles parquet with `dgn == 0`
- `couples_male`: couples parquet, male-suffixed columns
- `couples_female`: couples parquet, female-suffixed columns

Household ID:

- preferred: `idhh`
- fallbacks: `idhh_true`, `hh_id`

Chosen indicator:

- preferred: `is_chosen`
- fallback: `chosen`

Working indicators:

- singles: `working`, fallback `hours > 0`
- couples male: `working_male`, fallback `hours_male > 0`
- couples female: `working_female`, fallback `hours_female > 0`

Proposal-density columns:

- singles: `log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`
- couples male: `log_q_E_male`, `log_q_H_male`, `log_q_W_male`,
  `log_q_Occ_male`
- couples female: `log_q_E_female`, `log_q_H_female`, `log_q_W_female`,
  `log_q_Occ_female`

## Diagnostic Procedure

### D1 - Load and sanity-check inputs

Load the latest M0a-clean results JSON and confirm:

- specification is `ruro_occ_M0a_clean`
- parameter vector has 47 parameters
- `theta_c_singles` exists
- `theta_c_sm` and `theta_c_sf` do not exist

Load the MNL files and confirm:

- one chosen alternative per household
- exactly 100 alternatives per household
- required proposal aliases exist
- `prior > 0`
- `log_prior == log(prior)` within floating-point tolerance

### D2 - Re-evaluate or reconstruct V by component

Preferred route:

- Use the same forward-index code path as the estimator where feasible.

Fallback route:

- If the exact engine path cannot be invoked cleanly outside optimization,
  reconstruct the choice index component-by-component from the parsed spec,
  data, and estimated parameters. Document where the wrapper diverges from
  the exact estimator path, if anywhere.

For each group, sample up to 100 households with a fixed seed. For each
alternative, decompose:

```text
V_ij = U_ij
     + O_E_ij
     + O_H_ij
     + O_market_ij
     + O_W_ij
     + O_Occ_ij
     - log_prior_ij
```

Use `log_prior` directly from the parquet for the final prior correction.

Report component medians for work and non-work alternatives, plus the
work-minus-nonwork gap:

| group | component | median work | median nonwork | work - nonwork |

At minimum include:

- `U`
- `O_E`
- `O_H`
- `O_market`
- `O_W`
- `O_Occ`
- `-log_prior`
- total `V`

### D3 - Structural non-work probability

For each sampled household, compute a softmax over all 100 alternatives.

Report:

- median structural `P(nonwork)` per group
- q10, q25, q75, q90 of structural `P(nonwork)`
- observed chosen non-work share per group
- post-estimation reported predicted participation, if available

Interpretation:

- If structural `P(nonwork)` is roughly non-zero and comparable to observed
  non-work rates, but the report says participation is 1.0000, the root cause
  is post-estimation reporting.
- If structural `P(nonwork)` is essentially zero, the issue is in the
  structural index, prior correction, or the specification.

### D4 - Audit likely code paths

Use `rg` and file reads to inspect relevant code paths. Cite file and line
numbers in the report.

Check these hypotheses:

H1. Working gate or sign convention bug:

- `working == 1` is used where non-work should be used, or vice versa.
- Working-gated opportunity shifters fire on non-work alternatives.

H2. Prior correction bug:

- `-log_prior` is applied twice.
- `+log_prior` is used instead of `-log_prior`.
- `log_q_E` is combined with another employment-prior term already included
  in `log_prior`.

H3. Wage opportunity/Jacobian bug:

- `O_W` is missing the `-log(wage)` Jacobian for the log-normal density.
- Non-work alternatives receive a wage-density contribution.

H4. Post-estimation aggregation bug:

- predicted participation is computed only over working alternatives.
- non-work alternatives are filtered out before aggregation.
- couples non-work is misclassified because only one partner's working
  indicator is checked.

### D5 - Non-work contribution audit

For non-work rows in the sample, print and store:

- `O_H`
- `O_market`
- `O_W`
- `O_Occ`
- `log_prior`
- each proposal alias used for the group

Expected:

- working-gated opportunity contributions are zero on non-work rows.
- occupation opportunity is zero on non-work rows.
- wage opportunity is zero on non-work rows.
- `log_prior` for non-work alternatives equals the employment proposal
  component relevant to non-work, not the full working draw density.

If these expectations fail, identify the responsible code path.

## Output Report

Write:

```text
Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md
```

Keep it short, but include:

1. Input files and timestamps.
2. Parameter sanity checks.
3. Sample size used per group.
4. Component decomposition table.
5. Structural `P(nonwork)` table.
6. Non-work contribution audit summary.
7. Suspect code paths with file:line references.
8. Final verdict.

The final verdict must end with exactly one of these sentences:

```text
ROOT CAUSE: post-estimation reporting code at <file>:<lineno>. Spec-side and engine code are correct. Recommended fix: <one-line description>.
```

or

```text
ROOT CAUSE: engine code at <file>:<lineno>. The structural index itself produces P(nonwork) approximately zero. Recommended fix: <one-line description>.
```

or

```text
ROOT CAUSE: prior-correction logic at <file>:<lineno>. log_prior is <double-counted | mis-signed | applied to the wrong alternatives>. Recommended fix: <one-line description>.
```

or, if no bug is found and the decomposition shows the model truly predicts
almost universal work:

```text
ROOT CAUSE: specification/data fit artifact, not a code bug. The structural index assigns near-zero probability to non-work alternatives. Recommended fix: inspect the largest V component gaps and revise the specification or proposal design.
```

After writing the three files, print their paths and stop. Do not implement
the fix in this task.

---

# Sequencing Summary

1. Run Prompt 1.
2. Confirm `Results/_M0a_clean_spec_check.py` passes.
3. User runs the M0a-clean estimation and post-estimation commands.
4. Run Prompt 2.
5. Paste back only:
   - the verdict line,
   - the component table,
   - the suspect code path section.

Then decide whether the next task is a one-line post-estimation reporting fix
or a more careful engine/prior-correction patch.
