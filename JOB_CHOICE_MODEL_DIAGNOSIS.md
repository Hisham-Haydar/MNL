# Job-Choice RURO: Data Flow, Estimated Model, and Identification Diagnosis

This note summarizes what the current job-choice pipeline does end-to-end, what is estimated, and where identification/fit issues likely come from.

## 1) End-to-end pipeline (what happens step by step)

### Step A: Build job universe
- Script: `scripts/Job_model/enh_job_universe.py`
- Input: `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet`
- Main action:
  - Build discrete jobs from `(hours_bin, wage_bin, isco1)` cells.
  - Compute representative hours/wage per cell (mean/median/mode depending on options).
  - Assign deterministic `job_id`.
- Output:
  - `job_universe_YYYY.parquet`
  - `job_universe_YYYY__meta.json`

### Step B: Generate job draws
- Script: `scripts/Job_model/enh_job_draws.py`
- Input: ready data + job universe
- Main action:
  - For each decision-maker, keep baseline draw `0` and sample `n_draws` jobs.
  - Store proposal-density terms (`log_q_*`) used later for correction.
- Output:
  - `singles_RURO_ready_jobdraws.parquet`
  - `couples_RURO_ready_jobdraws.parquet`

### Step C: Run EUROMOD on drawn alternatives
- Script: `scripts/enhanced/enh_RURO_euromod.py`
- Input: draws + microdata template + EUROMOD config
- Main action:
  - Simulate taxes/transfers for each draw.
  - Produce disposable income (`ils_dispy_em`) by alternative.
- Output:
  - `combined_draws_em.parquet`

### Step D: Build MNL estimation data
- Script: `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- Input: draws + EUROMOD output + GSUR lookup
- Main action:
  - Merge EUROMOD results into draws and set canonical consumption from `ils_dispy_em`.
  - Restrict to RURO deciders.
  - Merge GSUR with fallback by full age bracket.
  - Build core variables (consumption, leisure, hours, priors, chosen flags, etc.).
  - Normalize consumption/leisure.
  - Set prior from proposal density (`log_q_total` or joint version for couples).
  - Filter to essential columns and write final MNL files.
- Output:
  - `fr_2016_RURO_mnl_job__singles.parquet`
  - `fr_2016_RURO_mnl_job__couples.parquet`
  - `fr_2016_RURO_mnl_job__mnlmeta.json`

### Step E: Estimate parameters
- Entry script: `scripts/enhanced/enh_RURO_estimate_FR.py`
- Engine path (vectorized GAMSPy): `scripts/enhanced/gamspy_estimation_vectorized.py`
- Main action:
  - Load MNL data by group.
  - Precompute arrays (`consumption`, `leisure`, priors, observed choice index, shifters).
  - Build vectorized log-likelihood and solve with selected GAMSPy solver.
- Output:
  - `estimation_results.json`
  - `estimation_summary.txt`
  - per-group parameter CSVs

### Step F: Post-estimation report
- Script: `scripts/enhanced/RURO_post_estimation_styled.py`
- Main action:
  - Fit stats, MU diagnostics, Hessian diagnostics, plots (hours/wage/job/loc distributions).
  - Includes prior-corrected null fit diagnostics for sampled alternatives.


## 2) Model that is currently estimated

Let `i` be household/decision-maker, `j` alternative (draw/job), and `g` group.

For singles (conceptual form):

`Index_ij = U_pref(c_ij, l_ij; theta_g) + log_h_ij + log_w_ij + log_market_ij - log(prior_ij)`

with

`U_pref = beta_l(X_i) * BC(l_ij, theta_l) + beta_c * BC(c_ij, theta_c) + beta_cl * BC(c_ij, theta_c) * BC(l_ij, theta_l)` (if interaction enabled).

Choice probability:

`P_ij = exp(Index_ij) / sum_k exp(Index_ik)`

Important for job-choice specs used here:
- `wage_spec: fw` => no separate wage-density term estimated (`log_w` effectively not adding parameters).
- `hours_opportunity.shifters: []` => no separate hours-density term (`log_h` effectively not adding parameters).
- Opportunity mostly enters via `market_opportunity` block.

For couples:
- Same logic, with male/female leisure components and shared household consumption component.


## 3) Why identification is hard in this setup

The estimated index is additive:

`U_pref + log_market - log(prior)` (plus optional `log_h`, `log_w` terms).

Main implication:
- Without strong excluded variation, preference and opportunity can substitute each other in-sample.
- You identify the combined index well enough for prediction, but decomposition into "taste" vs "opportunity" can be weak/unstable.


## 4) Evidence from recent runs

### A) `job_choice_v0_plus_stable` (IPOPT)
- Run: `run_2026-02-05_10-48-29`
- LL about `-22411.64`
- Prior-corrected rho2 about `0.1069`
- Negative MUC/MUL in report: `0 / 0`
- Still weak ID signs: very large condition number and negative Hessian eigenvalues.

### B) `job_choice_v0_plus_b_stable_beta_cl` (IPOPT, soft MU constraints)
- Run: `run_2026-02-05_11-07-11`
- LL about `-22161.64` (better fit)
- Prior-corrected rho2 about `0.1169` (better fit)
- But MU diagnostics degrade: high shares of negative MUC/MUL.
- Condition number remains very large, negative eigenvalues remain.

### C) `job_choice_v0_plus_id_strict` (CONOPT)
- Run: `run_2026-02-05_11-36-48`
- LL about `-24364.10` (much worse fit)
- Prior-corrected rho2 about `0.0291` (underfit)
- Some parameters pinned at bounds.

Interpretation:
- Strict exclusion improves conceptual separation but loses too much fit.
- Richer specs recover fit but reintroduce overlap/confounding and unstable decomposition.


## 5) Where issues are most likely

1. **Preference-opportunity confounding by construction**
- Utility and opportunity both enter additively in the same index.

2. **Weak excluded, job-varying demand shifters**
- `gsur` helps, but mostly on participation margin.
- It may not generate enough within-working-alternative variation by itself.

3. **Overlap when adding opportunity terms tied to wage/hours bins**
- Utility already reacts to `c` and `l`, which are induced by wage/hours job bundles.
- Adding `wage_bin`/`hours_bin` in opportunity can duplicate the same signal.

4. **Boundary-driven solutions**
- Several runs show parameters at bounds, which indicates weak curvature in objective for some dimensions.

5. **Single-country-year estimation**
- Limited exogenous variation can make decomposition less stable.


## 6) Practical path to a model that fits better and is more identifiable

1. Keep `v0_plus` as baseline reference (best current fit-vs-regularity compromise).
2. Use a **semi-strict** opportunity block:
   - Keep `working + gsur`
   - Add only one of `{wage_bin, hours_bin}` (not both initially).
3. Keep `beta_cl` off until semi-strict baseline is stable.
4. If adding `beta_cl`, add stronger regularization:
   - stronger soft MU weights
   - MU constraints at multiple `(c, l)` points, not one anchor only.
5. Use multi-start checks:
   - if very different params but similar LL, decomposition is still weak.
6. Prefer holdout predictive checks for model comparison:
   - compare out-of-sample LL and prior-corrected rho2.
7. If possible, pool multiple years to increase identifying variation.


## 7) Discussion checklist

- Are we prioritizing:
  - best in-sample fit, or
  - interpretable decomposition of preference vs opportunity?
- Which variables are allowed in opportunity but excluded from utility?
- Should we enforce stronger economic regularity (MUC/MUL) even at fit cost?
- Do we have additional labor-demand instruments by occupation/region/year?

