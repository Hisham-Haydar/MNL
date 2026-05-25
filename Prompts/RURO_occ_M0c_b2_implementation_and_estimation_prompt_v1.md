# Claude Code prompt — `ruro_occ_M0c_b2` implementation, estimation, multi-start, and decision-tree report

Date: 2026-05-14

Single prompt for Claude Code. Implements the M0c_b2 specification (one bound
relaxation on `beta_l0_m`), runs the estimation with multi-start, generates
the post-estimation summary, and writes a decision-tree-aware report that
classifies the outcome into one of three branches without iterating further.

---

```text
Work locally in my RURO/MNL codebase.

The active diagnostic model is `ruro_occ_M0c_b2`. This is one final
identification cycle to test whether `beta_l0_m`'s 0.05 lower bound was set
too aggressively, after which the model is frozen for identification
purposes regardless of outcome.

Read:
- Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b_estimation_report_v1.md
- Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b_gate_A_parse_report_v1.md
- docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b_implementation_report_v1.md
- docs/RURO_occ_M0c_design_memo_v1.md
- scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml
- scripts/enhanced/estimation_spec_parser.py
- scripts/enhanced/gamspy_estimation_vectorized.py
- scripts/enhanced/estimation_engine.py
- scripts/enhanced/RURO_post_estimation_styled.py
- scripts/enhanced/expression_constraints.py
- Results/_M0b2_multistart_runner.py

Background:

M0c_b achieved partial success: `beta_ll` moved from the M0b2 upper bound
(2.0, NA SE) to an interior estimate (2.587, t = 6.64, p < 1e-11), and LL
improved by +2.14 nats with one fewer parameter (47 vs 48). But the
negative Hessian eigenvalue migrated from the (theta_c, beta_ll) corner
to `beta_l0_m`, which settled at its lower bound of 0.05. Gate B still
fails on all 5 criteria.

Two hypotheses for `beta_l0_m → 0.05`:
- **(A) bound set too aggressively.** The 0.05 lower bound was a numerical
  safety margin; the data may want `beta_l0_m` at, say, 0.005 or 0.001,
  not at 0.05. Relaxing the bound should let the optimizer find the
  interior.
- **(B) couples male autonomous leisure utility is structurally zero.** With
  `beta_ll = 2.587`, the leisure-leisure interaction absorbs all of male
  leisure utility, leaving the additive intercept with nothing to
  contribute. Relaxing the bound just produces a new boundary at the
  new lower limit.

M0c_b2 distinguishes between (A) and (B) by relaxing the bound to a
numerically meaningless value (1e-6). If `beta_l0_m` settles strictly
interior (e.g., > 1e-3), hypothesis (A) is correct. If it goes to the new
lower limit (≤ 1e-5), hypothesis (B) is correct and a subsequent
structural fix (M0c_c) would be needed — but M0c_b2 itself does NOT
implement that fix. M0c_b2 is purely the bound relaxation, with the
decision recorded for the next step.

Task:

Implement and estimate `ruro_occ_M0c_b2`. Then post-estimate with the
already-patched reporter. Then write a decision-tree-aware report that
classifies the outcome and recommends one of three next steps without
iterating further inside this task.

---

STEP 1 — YAML spec creation.

Create `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml` by copying
`scripts/enhanced/estimation_spec_ruro_occ_M0c_b.yaml` and applying:

(a) `specification.name`: change to `"ruro_occ_M0c_b2"`.

(b) `specification.description`: update to:
   "M0c_b2: relaxes M0c_b's beta_l0_m lower bound from 0.05 to 1e-6 to
    test whether the M0c_b boundary was numerical or structural. Final
    identification cycle before declaring the model frozen."

(c) In `optimization.bounds`, change:
   ```yaml
   beta_l0_m:  [0.05, 50.0]
   ```
   to:
   ```yaml
   beta_l0_m:  [1.0e-6, 50.0]
   ```

(d) In `initial_values`, change `beta_l0_m` from its M0c_b value
   (effectively 0.05 after warm-start) to **0.01** — an interior value
   away from any bound. This makes the spec-defaults start non-trivial.

(e) Everything else byte-identical to M0c_b. No changes to `theta_c`,
   `beta_ll`, opportunity blocks, proposal correction, or expression
   constraints.

STEP 2 — Parse-check (Gate A, brief).

Run a parse-check script equivalent to the M0c_b Gate-A test. Confirm:
- `spec.name == "ruro_occ_M0c_b2"`
- `len(spec.all_param_names) == 47`
- `'theta_c' not in spec.all_param_names`
- `spec.bounds['beta_l0_m'] == (1e-6, 50.0)`
- `spec.initial_values['beta_l0_m'] == 0.01`
- `spec.utility_consumption_theta_couples_fixed == 0.0`
- `spec.bounds['beta_ll'] == (0.0, 10.0)` (unchanged from M0c_b)

If any check fails, stop and report. Do not proceed to estimation.

Save: `Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_gate_A_parse_report_v1.md` (brief, one
page).

STEP 3 — Multi-start estimation (3 starts).

Adapt `Results/_M0b2_multistart_runner.py` to point at the M0c_b2 spec
and write `Results/_M0c_b2_multistart_runner.py`. Use 3 starts (skip
the perturb_defaults start that caused the GAMS overflow in M0b2):

| label | description | init `beta_l0_m` | init `beta_ll` | other |
|---|---|---|---|---|
| S1_spec_defaults | YAML defaults | 0.01 | 0.0 | all other params at YAML defaults |
| S2_warmstart_M0c_b | from M0c_b solution | 0.050 (M0c_b bound value) | 2.587 (M0c_b solution) | all other params from M0c_b |
| S3_dispersed_interior | interior far from any boundary | 1.0 | 5.0 | beta_c=2, theta_c_singles=-1.5 |

Each start uses `--warm-start none --init-params <path>`. Save init JSONs
to `Results/_M0c_b2_multistart_inits/`.

Run estimation for each start. Save run folders separately. Wait for all
three to complete (or fail explicitly).

Save: `Results/_M0c_b2_multistart_summary.json` with the same field
structure as `_M0b2_multistart_summary.json`.

STEP 4 — Post-estimation on the best run.

Identify the best run (lowest LL among successful starts). If multiple
starts return the same LL within 1e-3, pick the one with the smallest L2
distance to the M0c_b solution.

Run the standard post-estimation pipeline on the selected run. This
should use the already-patched `RURO_post_estimation_styled.py` with the
spec-aware `theta_c` display logic. Confirm the low-token Markdown
summary correctly shows `theta_c = 0.000` for couples groups (not the
0.5 fallback or NA).

Save: standard post-estimation outputs to the run folder.
Save: low-token Markdown summary to
   `reports/fr_2016_ruro_occ_gamspy_M0c_b2_llm_summary_<timestamp>.md`.

STEP 5 — Decision-tree branch classification.

Based on the M0c_b2 selected run, classify the outcome into exactly one
of three branches:

**Branch A — Bound was numerical, model identifies interior.**
   Conditions (ALL must hold):
   - `beta_l0_m > 1e-3` (well above the new bound)
   - 0 negative Hessian eigenvalues
   - 0 NA standard errors on the couples block (theta_c not relevant
     since fixed)
   - Couples fit moments preserved from M0c_b (participation within 2pp,
     mean hours within 5h, L1 < 0.6, wages within 5 EUR/h of observed)
   - Singles fit moments preserved
   - Multi-start: all three starts converge to same point (delta_L2 <
     0.1 across starts)

**Branch B — Bound was structural, beta_l0_m wants to be zero.**
   Conditions (ANY of the following):
   - `beta_l0_m ≤ 1e-5` (at or near new lower bound)
   - 1 or more negative Hessian eigenvalues that the M0c_b multi-start
     showed concentrated on `beta_l0_m` at the previous bound
   - Multi-start finds two different solutions where the difference is
     concentrated in `beta_l0_m`

**Branch C — Fit regression or new pathology.**
   Conditions (ANY of the following):
   - Couples fit moments regress materially from M0c_b (participation
     gap > 3pp, mean hours gap > 5h, L1 > 0.7, wages diverge > 10 EUR/h)
   - Singles fit regresses
   - LL worsens by > 5 nats compared to M0c_b (suggests M0c_b2 found a
     different local optimum that's worse on substantive moments)
   - Numerical breakdown (NaN/Inf in V or probability, or solver failure
     on all three starts)

If the result satisfies multiple conditions across branches, classify by
priority: C > B > A. (i.e., a regression takes precedence over a clean
interior; a clean interior is reported only if no failure conditions are
also met.)

STEP 6 — Write the report.

Save: `Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_estimation_report_v1.md`. Use the same
structure as `RURO_occ_M0c_b_estimation_report_v1.md` plus a new
section §13 "Branch classification". Specific fields required:

§1 — Commands run (3 starts).
§2 — Run folders (3 + selected).
§3 — Multi-start convergence status.
§4 — LL across starts (with delta vs M0c_b reference).
§5 — `beta_l0_m` final values across starts (3 numbers).
§6 — `beta_ll` final values across starts (3 numbers; should still be
       around 2.587 if the spec is internally consistent).
§7 — Identification diagnostics (kappa, neg eigs, NA SEs, bounds) for
       the selected run.
§8 — Fit moments (couples participation/hours/wages/L1, singles
       participation/hours) for the selected run, compared to observed
       and to M0c_b.
§9 — Cross-spec parameter comparison table: M0a-clean, M0b2, M0c_b,
       M0c_b2 on (LL, n_params, AIC, kappa, n_neg_eigs, n_NA_SE,
       n_at_bounds, predicted couples wage mean, couples participation,
       couples L1 hours, beta_ll, beta_l0_m, theta_c).
§10 — Parameter stability vs M0c_b (delta_L2, delta_max_abs, delta_mean_abs).
§11 — Top-10 correlation pairs from VarCov; confirm whether singles
       consumption block correlations persist (`beta_c_sm`, `beta_c_sf`,
       `theta_c_singles` still showing |corr| > 1?).
§12 — Warnings.
§13 — **Branch classification (A, B, or C)** with the specific values
       that triggered the classification.
§14 — Verdict (one of):
       - PASS — Branch A confirmed; model frozen; proceed to welfare
         scaffolding and M1.
       - FLAG — Branch B confirmed; document `beta_l0_m → 0` as a
         substantive finding; recommend M0c_c (fix `beta_l0_m = 0`
         structurally, parallel to M0c_b's fix of `theta_c = 0`); do
         NOT implement M0c_c in this task.
       - FAIL — Branch C confirmed; new pathology; supervisor memo
         required before further code work.
§15 — Recommended next action (exactly one):
       Branch A → "Freeze model. Begin welfare scaffolding in parallel
         with M1 region opportunity check."
       Branch B → "Implement M0c_c: fix `beta_l0_m = 0` structurally
         using the same mechanism as M0c_b's `theta_c = 0`. This is the
         final identification cycle; after M0c_c the model is frozen
         regardless of remaining boundary issues in the singles
         consumption block."
       Branch C → "Stop. Write supervisor memo documenting the
         regression. Do not proceed to further estimation."

STEP 7 — Do not iterate.

Do NOT implement M0c_c or any further variant inside this task. The
report's recommendation is the deliverable; the next implementation
prompt will be issued separately based on the branch classification.

Do NOT run welfare computation.
Do NOT modify opportunity blocks, wage opportunity, proposal correction,
   MNL data, draws, or EUROMOD scripts.
Do NOT change any parser, engine, or post-estimation code.

The only YAML change in this task is the `beta_l0_m` lower bound
relaxation and the corresponding initial-value change. Everything else
in the M0c_b2 YAML is byte-identical to M0c_b.

Deliverables:
1. scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml
2. Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_gate_A_parse_report_v1.md
3. Results/_M0c_b2_multistart_runner.py
4. Results/_M0c_b2_multistart_inits/{S1,S2,S3}_init.json
5. Results/_M0c_b2_multistart_summary.json
6. outputs/estimates/.../estimation_spec_ruro_occ_M0c_b2/run_<timestamp>/
   (three subfolders, one per start; selected run identified)
7. reports/fr_2016_ruro_occ_gamspy_M0c_b2_llm_summary_<timestamp>.md
8. Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_estimation_report_v1.md

Stop after deliverable 8 is written.
```

---

## Suggested filename for this prompt

Save as: `prompts/RURO_occ_M0c_b2_implementation_and_estimation_prompt_v1.md`
(category: coding prompt).
