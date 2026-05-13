# Claude Code prompts — RURO `ruro_occ_M0a-clean` rename + participation diagnostic

Date: 2026-05-13

Purpose: two sequential prompts for Claude Code. Prompt 1 replaces the
M0a equality-constraint fallback with a proper renamed shared
parameter, removing the post-estimation `|corr| > 1` artifacts in the
consumption block. Prompt 2 decomposes the choice index at the M0a-clean
converged θ to identify which term is driving predicted participation
= 1.0000 across all four groups.

Run Prompt 1 first. After it finishes and a new estimation results file
exists, run Prompt 2 against that results file. Do not run them in
parallel.

---

## Prompt 1 — M0a-clean: proper rename of `θ_c_singles`

```text
You are repairing a constraint-handling artifact in the
`ruro_occ_M0a` estimation. The M0a YAML implemented the singles
consumption-curvature pool via a hard equality constraint
`theta_c_sm - theta_c_sf = 0` in expression_constraints. This works at
the optimizer level but produces a non-PSD post-estimation covariance
matrix (|corr| values of -4.67, -3.79, -3.71, -3.01 between
theta_c/beta_c pairs in the M0a results), because the
post-estimation Hessian is computed on the unconstrained parameter
vector and is rank-deficient along the constrained direction. The fix
is to actually rename the parameter so that the sf utility evaluation
references the same theta as sm, removing one parameter from the
estimable vector.

INPUT FILES (read+write where indicated):
- scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml             (read)
- scripts/enhanced/estimation_spec_parser.py                     (read+write if needed)
- scripts/enhanced/gamspy_estimation_vectorized.py               (read+write if needed)
- scripts/enhanced/estimation_engine.py                          (read+write if needed)
- scripts/enhanced/enh_RURO_estimate_FR.py                       (no changes; entrypoint)

GOAL: produce
- scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml   (the corrected spec)
- an estimation run at
  outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/
  with `n_estimated_params = 47` (one less than M0a's 48) and a
  post-estimation low-token Markdown summary in reports/.
- a short Markdown patch report at
  Results/RURO_ruro_occ_M0a_clean_rename_patch_v1.md that documents
  the parser/engine changes (if any) and the resulting parameter count.

STEP A — INVENTORY:
First, inspect scripts/enhanced/estimation_spec_parser.py and the two
engine files to determine how the parser currently handles the case
where the consumption box-cox exponent is shared between sm and sf.
There are three implementation strategies in increasing order of
invasiveness. Pick the LEAST invasive that works.

Strategy 1 (preferred, no parser change):
  In the YAML, drop `theta_c_sf` from initial_values and bounds
  entirely. In the parser's group-resolution logic (likely a function
  like `_resolve_group_param` or similar), ensure that when
  `theta_c_sf` is requested by the sf likelihood block and is not in
  the spec, it falls back to `theta_c_sm`. Many parsers already do
  this fallback (it's how shared couples params work). Check whether
  the existing fallback chain
  `params.get('theta_c_sf', params.get('theta_c_singles',
  params.get('theta_c_sm', params.get('theta_c'))))`
  is in place; if not, add it as a one-line change.

Strategy 2 (small parser change):
  Add a new parameter name `theta_c_singles` to the parser's
  recognised shared-singles parameter set. The sm and sf likelihood
  evaluations both look up `theta_c_singles` before falling back to
  their gendered names.

Strategy 3 (avoid):
  Modify the engine to treat (theta_c_sm, theta_c_sf) as a single
  parameter via constraint reduction at the symbolic level. This is
  more invasive than needed.

Determine which strategy works for the current parser. If Strategy 1
works out of the box (the fallback chain already exists), no parser
edit is needed — only the YAML changes.

STEP B — YAML EDIT:
Copy estimation_spec_ruro_occ_M0a.yaml to
estimation_spec_ruro_occ_M0a_clean.yaml. Apply these changes:

  1. Update `specification.name` to `"ruro_occ_M0a_clean"`.
  2. Update `specification.description` to:
     "M0a-clean: theta_c shared across singles via proper rename
      (not equality constraint); beta_l_educH removed from utility."
  3. In `initial_values:`, remove the line `theta_c_sf: -1.0`. Keep
     `theta_c_sm: -1.0` as the singles-shared name.
  4. In `optimization.bounds:`, remove the line
     `theta_c_sf: [-8.0, 0.95]`. Keep `theta_c_sm: [-8.0, 0.95]`.
  5. In `optimization.expression_constraints.constraints:`, REMOVE
     the `theta_c_singles_pool` (or equivalently-named) equality
     constraint that links theta_c_sm and theta_c_sf. If after this
     removal the constraints block is empty, leave it as
     `constraints: []` (do not delete the parent
     expression_constraints block).
  6. Add an inline comment near the consumption block explaining the
     change:
     "# M0a-clean: theta_c_sm is the shared singles curvature; the sf
     #  likelihood block looks up theta_c_sm as the fallback for
     #  theta_c_sf. See Strategy 1 in
     #  Results/RURO_ruro_occ_M0a_clean_rename_patch_v1.md."

STEP C — PARSER / ENGINE EDIT (only if Strategy 1 doesn't work
out of the box):
Make the minimum change needed to ensure both sm and sf utility
evaluations use the same theta_c value at every alternative. Confirm
that:
  - spec.all_param_names does not contain "theta_c_sf"
  - spec.all_param_names contains "theta_c_sm" exactly once
  - the engine's V evaluation for the sf likelihood pulls
    theta_c_sm (not theta_c_sf) at every alternative

Run `python -c "from estimation_spec_parser import parse_specification;
s = parse_specification('scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml');
print('n_params:', len(s.all_param_names));
print('theta_c_sm in:', 'theta_c_sm' in s.all_param_names);
print('theta_c_sf in:', 'theta_c_sf' in s.all_param_names)"` and
confirm: n_params = 47; theta_c_sm in: True; theta_c_sf in: False.

If those don't print as expected, Strategy 1 is insufficient and
Strategy 2 is required.

STEP D — ESTIMATION:
Run:
  python .\scripts\enhanced\enh_RURO_estimate_FR.py `
    --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
    --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
    --group joint `
    --solver gamspy-conopt `
    --vectorized `
    --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml" `
    --warm-start none `
    --auto-timestamp `
    --verbose

`--warm-start none` is mandatory: M0a's converged theta is on the wrong
side of an indefinite Hessian. Use spec defaults.

STEP E — POST-ESTIMATION:
Run RURO_post_estimation_styled.py with --compute-se on the new
estimation_results.json. Save the low-token Markdown summary to
reports/. Read the resulting Convergence Health Summary and identify:
  - n_estimated_params (expect 47)
  - n_negative_eigenvalues (expect 0 if the rename was correct; 1 is
    a residual identification problem to address in M0b)
  - hessian_condition_number (expect < 10^10; the gate is 10^7 but
    10^10 vs M0a's 10.6 x 10^9 will tell us whether the rename also
    drove down kappa)
  - Top high-correlation pairs (expect all |corr| <= 1 if rename is
    correct)
  - Specifically, the rows where param_i is theta_c_sm or beta_c_sm
    should not show |corr| > 1 with any other parameter.

STEP F — PATCH REPORT:
Write Results/RURO_ruro_occ_M0a_clean_rename_patch_v1.md containing:
  1. Which strategy was used (1, 2, or 3) and why.
  2. The exact lines changed in the parser/engine (if any), with
     before/after.
  3. The diff between estimation_spec_ruro_occ_M0a.yaml and
     estimation_spec_ruro_occ_M0a_clean.yaml.
  4. The pre-estimation `n_params` confirmation from STEP C.
  5. A two-row results table: M0a vs M0a-clean on
     n_negative_eigenvalues, hessian_condition_number, max |corr|,
     log-likelihood, n_significant.
  6. A one-paragraph verdict on whether Gate B2 (zero negative
     eigenvalues, kappa < 10^7) is now passed. If yes, recommend
     proceeding to the participation diagnostic (Prompt 2 of this
     prompt pair). If no, recommend a follow-up specifically targeting
     whichever eigenvector is now driving the residual indefiniteness
     — but DO NOT pre-implement that follow-up.

DO NOT:
- Touch the data pipeline, the rebuilt parquets, or the draws script.
- Change any other YAML block (utility leisure shifters, opportunity
  blocks, occupation block, wage block, bounds on substantive
  parameters).
- Modify the existing estimation_spec_ruro_occ_M0a.yaml. The original
  M0a YAML must remain available for diff and provenance.
- Run the participation diagnostic in this prompt. That is Prompt 2.

After STEP F is written, confirm the file paths of the four
deliverables (clean YAML, run folder, post-estimation Markdown summary,
patch report) and stop.
```

---

## Prompt 2 — participation V-decomposition diagnostic

Run only after Prompt 1 finishes and a new `estimation_spec_ruro_occ_M0a_clean` run exists.

```text
You are diagnosing why predicted participation is 1.0000 across all four
groups (sm, sf, cou_m, cou_f) in the M0a and M0a-clean estimations
despite the proposal-adequacy diagnostic confirming 10% median non-work
mass in the choice set and despite beta_E being significantly negative.
The proposal-adequacy diagnostic eliminated data-side variation as the
cause; the M0a-clean rename eliminated the constraint-handling artifact.
If predicted participation is still 1.0000 in M0a-clean, the bug is in
the choice-index evaluation or in the post-estimation reporting code,
not in the spec.

This prompt decomposes the choice index V_ij at the M0a-clean converged
theta into its components and identifies which component is driving the
work-vs-nonwork imbalance.

INPUT FILES (read-only, no modifications):
- outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/run_<latest>/estimation_results.json
- scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet

If M0a-clean's negative eigenvalue count is non-zero in Prompt 1's
patch report, still run this diagnostic on the M0a-clean run: a
non-PSD Hessian does not invalidate the V decomposition (V is computed
from theta directly, not from the Hessian).

GOAL: produce a single Markdown report at
Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md that decomposes
the work/non-work choice-index imbalance per group and identifies the
dominant culprit term.

STEP A — LOAD CONVERGED THETA AND DATA:
Read estimation_results.json. Extract the converged theta vector and
the parameter-name list. Confirm theta has 47 entries. Print the values
of the most relevant parameters for the diagnostic:
beta_E, beta_h_pt1, beta_h_pt2, beta_h_ft, beta_E_gsur, beta_E_educH,
beta_c, beta_c_sm, beta_c_sf, theta_c, theta_c_sm,
beta_l0_*, theta_l_*, beta_w0, sigma.

Load the two parquets. Apply the same per-group structure used in the
proposal-adequacy diagnostic:
- singles_male (dgn==1), singles_female (dgn==0): use `working`,
  `consumption`, `leisure`, `hours`, `loc4`, `log_q_E`, `log_prior`.
- couples_male: use `working_male`, `consumption` (household-shared),
  `leisure_male`, `hours_male`, `loc4_male`, `log_q_E_male`,
  `log_prior`.
- couples_female: same with `_female` suffixes.

STEP B — V DECOMPOSITION ON A 100-HOUSEHOLD SAMPLE PER GROUP:
For each of the four groups, sample 100 households uniformly at
random (set seed = 42 for reproducibility). For each sampled
household, compute the following at every alternative (100 alts/hh):

  U_ij        = preference utility term
                = beta_c_g * BC(C_ij, theta_c_g) + beta_l_g(Z_i) * BC(L_ij, theta_l_g)
                where for sm/sf:  beta_c_g  = beta_c_sm or beta_c_sf
                                   theta_c_g = theta_c_sm (shared singles)
                                   theta_l_g = theta_l_sm or theta_l_sf
                       for cm/cf: beta_c_g  = beta_c
                                   theta_c_g = theta_c
                                   theta_l_g = theta_l_m or theta_l_f
                beta_l_g(Z_i) includes age, age^2, n_children (female
                only) shifters.

  O_E_ij      = beta_E * working_ij
  O_H_ij      = beta_h_pt1 * working_pt1_ij + beta_h_pt2 * working_pt2_ij
                + beta_h_ft * working_ft_ij
  O_market_ij = beta_E_gsur * gsur_i * working_ij
                + beta_E_educH * educH_i * working_ij
  O_W_ij      = log_normal_density(wage_ij | Mincer mean, sigma)
                on working alts; 0 on non-work alts.
                = -0.5 * z^2 - log(sigma) - log(wage_ij)
                  z = (log wage_ij - mu_W(X_i)) / sigma
                  mu_W = beta_w0 + beta_w_educL * educL + beta_w_educH * educH
                         + beta_w_pexp * pexp + beta_w_pexp2 * pexp2
                NOTE: include the -log(wage) Jacobian. Without it, V_W
                will systematically over-weight high-wage alternatives.

  O_Occ_ij    = sum_k beta_occ_k_g * 1{loc4_ij = k} * working_ij
                with reference loc4 = 1 (omitted).
                k in {2, 3, 4}; g in {sm, sf, cm, cf} for couples
                partner-specific.

  V_ij        = U_ij + O_E_ij + O_H_ij + O_market_ij + O_W_ij + O_Occ_ij
                - log_prior_ij

Where the data column log_prior_ij is taken directly from the parquet
(it's pre-built by enh_RURO_prep_mnl_basic.py and already validated by
the MNL validation report; do NOT recompute it).

Box-Cox safety: clip C, L >= 1e-6 before transforming.

STEP C — V-COMPONENT TABLES PER GROUP:
For each group, compute the per-household average across alternatives,
SEPARATELY for working alts and for non-working alts (where working =
0 on at least one of the 100 alts). Report the median across the 100
sampled households of each component.

Output table per group:

  | term        | median over hh of mean on work alts | median over hh of mean on non-work alts | work - nonwork (median diff) |
  | U           |                                      |                                          |                              |
  | O_E         |                                      |                                          |                              |
  | O_H         |                                      |                                          |                              |
  | O_market    |                                      |                                          |                              |
  | O_W         |                                      |                                          |                              |
  | O_Occ       |                                      |                                          |                              |
  | - log_prior |                                      |                                          |                              |
  | V (total)   |                                      |                                          |                              |

The work-minus-nonwork column tells us which term contributes the most
to the work/non-work choice-index gap. The signs and magnitudes of
those gaps should be economically interpretable.

EXPECTED MAGNITUDES (rough sanity benchmarks):
  - U: small gap, sign ambiguous (consumption higher on work due to
    earnings; leisure lower).
  - O_E: equals beta_E ~ -2.76 on work, 0 on non-work; gap = -2.76.
    Negative gap means work is penalised; should DECREASE work
    probability.
  - O_H: 0 to ~1.5 on work (depending on hours bin), 0 on non-work.
    Positive gap, magnitude up to ~1.5.
  - O_market: beta_E_gsur*gsur + beta_E_educH*educH on work, 0 on
    non-work. Roughly -0.07 to +0.25 depending on covariates.
  - O_W: -0.5*z^2 - log(sigma) - log(wage). At median wage ~15,
    sigma=0.42, this is ~-0.5*(0)^2 - log(0.42) - log(15) ~ -1.83.
    Gap ~ -1.83 (work has more negative O_W).
  - O_Occ: 0 to ~1.15 on work depending on occupation, 0 on non-work.
    Gap is positive in nonroutine-cognitive groups.
  - -log_prior: large positive on work (proposal is wide), small
    positive on non-work (only q_E correction). Typical gap is
    +log(q_H * q_W * q_Occ) ~ +log(65 * 168 * empirical_loc4_share)
    ~ +log(65) + log(168) + log(0.3) ~ +4.17 + 5.12 - 1.20 ~ +8.09.
    POSITIVE GAP of ~+8 in favour of WORK.

The sum of all gaps should approximately equal V_work_mean -
V_nonwork_mean. If V_work >> V_nonwork (say by 10+), then
P(non-work | household) is essentially zero, matching the reported
predicted participation = 1.0000.

STEP D — IDENTIFY THE DOMINANT CULPRIT:
The expected magnitudes above suggest -log_prior is the largest
positive contributor to the work-nonwork gap (~+8) and U+O_E is the
largest negative contributor (~-2.76 from O_E plus whatever U
contributes). The net expected gap is roughly +5 in favour of work
before O_H and O_Occ are added.

A net gap of +5 would imply P(non-work) ~ exp(-5) ~ 0.0067 per
non-work alternative, summed over ~10 non-work alts ~ 0.067 = 6.7%
non-employment. That's roughly consistent with observed 5-7%
non-employment rates.

A net gap of +10 or +15 would imply P(non-work) << 1%, matching
the reported 1.0000 participation pathology.

So the diagnostic question is: which component is overshooting?
Possibilities:
  (a) -log_prior is too large because the prior is being added with
      the wrong sign somewhere (e.g., the data column log_prior
      represents log(q) but the engine is treating it as log(1/q)
      and the formula V = U + O - log_prior is computing V = U + O +
      log(1/q) instead of V = U + O - log(q)). Symptom: -log_prior
      gap is ~+16 instead of ~+8.
  (b) O_W is being computed without the -log(wage) Jacobian. Symptom:
      O_W gap is ~0 instead of ~-1.83 (i.e., positive instead of
      negative). This would make work more attractive by ~1.83.
  (c) Box-Cox transform applied wrong on non-work consumption. At
      non-work the household still has positive disposable income
      (from transfers, partner). If U on non-work is computed using
      a clipped C ~ 0 instead of the actual transfer income,
      U_nonwork is artificially low. Symptom: U gap is very positive
      (>> +2).
  (d) Leisure normalization wrong at h = 0. If L_nonwork is normalized
      to a value that makes BC(L_nonwork, theta_l) very large in
      magnitude, U_nonwork could blow up in either direction. Symptom:
      U gap has unusual sign or magnitude.

Report which expected magnitude is most off in the actual numbers, and
identify the suspect engine code path.

STEP E — POST-ESTIMATION VS STRUCTURAL P(NON-WORK):
For the same 100 sampled households per group, compute:
  P(non-work | household) = sum_{j: working_j=0} exp(V_ij) /
                            sum_{k=1..100} exp(V_ik)

Use the standard log-sum-exp stabilisation:
  V_max = max_j V_ij
  P(j) = exp(V_ij - V_max) / sum_k exp(V_ik - V_max)

Report the median, q10, q25, q75, q90 of P(non-work) across the 100
sampled households per group.

Compare to:
  - The post-estimation reported predicted_participation (this is
    `1 - mean[P(non-work | household)]`, so the comparison is direct).
  - The observed (chosen-alt) non-employment rate: roughly 3-7% per
    group from M0a's chosen sample.

If structural P(non-work) is essentially 0 for nearly all 100 households,
the choice-index evaluation is the bug. Identify the term from STEP C
that drives it.

If structural P(non-work) is non-zero (say 5-10% median) but the
post-estimation report says 1.0000, the bug is in the post-estimation
script's participation calculation. Look at the RURO_post_estimation_styled.py
code path that computes pred_participation.

STEP F — WRITE THE REPORT:
Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md

Structure:

  # RURO ruro_occ_M0a_clean — Participation Diagnostic v1

  ## Verdict (one paragraph)
  One of:
  - REPORTING BUG: structural P(non-work) is non-zero per household
    but post-estimation predicted_participation is 1.0000. Identify the
    post-estimation code path.
  - ENGINE BUG: structural P(non-work) is ~0 per household; one V
    component is overshooting. Identify the suspect term and the
    likely engine code path.
  - SPEC ARTIFACT: structural P(non-work) is ~0 and all V components
    match expected magnitudes; the model genuinely predicts no
    non-employment at this theta. (Unlikely given the inputs.)

  ## Converged theta highlights
  (parameter values that matter for V, from STEP A)

  ## V decomposition tables per group
  (four tables from STEP C)

  ## Sanity check vs expected magnitudes
  (per-group: which term is most off relative to STEP D's benchmarks)

  ## Structural P(non-work) per household
  (table from STEP E, per group)

  ## Comparison to post-estimation predicted_participation
  (one row per group)

  ## Suspect code path
  (specific file:line references in
   scripts/enhanced/gamspy_estimation_vectorized.py or
   scripts/enhanced/RURO_post_estimation_styled.py)

  ## Recommended next action
  ONE specific next step, tied to the verdict. Examples:
  - "Fix the sign of log_prior in gamspy_estimation_vectorized.py
    line NNN" if the prior is overshooting.
  - "Add the -log(wage) Jacobian to estimation_engine.py line NNN"
    if O_W is missing it.
  - "Fix pred_participation aggregation in
    RURO_post_estimation_styled.py line NNN" if reporting is the bug.

  ## Files produced
  Results/_participation_diag_ruro_occ_M0a_clean.py    (script)
  Results/_participation_diag_ruro_occ_M0a_clean.json  (numbers)
  Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md (this report)

TECHNICAL REQUIREMENTS:
- Use pandas + numpy only. No estimator, no GAMSPy, no EUROMOD.
- Read-only on the parquet files and estimation_results.json.
- Total runtime under 5 minutes on 400 households x 100 alts = 40k
  observations.
- Save the script to Results/_participation_diag_ruro_occ_M0a_clean.py
  so it can be re-run after any subsequent estimation.
- Save a machine-readable JSON with the per-group component medians.
- Use the same seed (42) so the sampled households are reproducible.

DO NOT:
- Modify any source code in scripts/. This is a diagnostic, not a
  patch. The "recommended next action" section names suspect code
  paths but does not change them.
- Re-run the estimator.
- Modify the M0a-clean YAML or run folder.

After the report is written, confirm the three output file paths and
stop. The next prompt (a code-side patch) will be issued separately
based on the diagnostic's verdict.
```

---

## Sequencing and what to do with results

Run Prompt 1. Wait for the patch report. Three possible outcomes:

| Patch report says | What it means | Next |
|---|---|---|
| Gate B2 PASSED (0 negative eigenvalues, κ < 10⁷) | Rename alone fixed identification | Run Prompt 2 to diagnose the participation pathology |
| Gate B2 partially improved (1 → 0 negative eigenvalues but κ still > 10⁷) | Rename removed the constraint artifact; the high κ is now a real high-correlation issue but not a singularity | Run Prompt 2; address κ later via targeted pooling if needed |
| Gate B2 still failed (1+ negative eigenvalues) | A real residual identification problem exists beyond the constraint artifact | Run Prompt 2 anyway (V decomposition does not need the Hessian) and plan M0b based on the residual eigenvector |

Run Prompt 2 against the M0a-clean run. Three possible verdicts:

| Verdict | Likely fix |
|---|---|
| REPORTING BUG | One-line patch in `RURO_post_estimation_styled.py` to the `pred_participation` aggregation |
| ENGINE BUG | A specific term in `gamspy_estimation_vectorized.py` or `estimation_engine.py` is computed wrong — most likely candidates are the wage Jacobian, the prior sign, or the consumption at non-work |
| SPEC ARTIFACT | Genuine model failure (unlikely given the diagnostics so far) |

Paste the verdict and the "Suspect code path" section into this chat after Prompt 2 finishes. I'll write the engine-side patch prompt as a Prompt 3 once we know what we're patching.

## Suggested filename for this prompt pair

Save as: `prompts/RURO_ruro_occ_M0a_clean_rename_and_participation_diag_prompts_v1.md`
(category: coding prompt).
