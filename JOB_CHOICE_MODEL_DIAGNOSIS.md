# Job-Choice RURO: Data Flow, Estimated Model, and Identification Diagnosis

This note summarizes what the current job-choice pipeline does end-to-end, what is estimated, and where identification/fit issues likely come from.

## 1) End-to-end pipeline (what happens step by step)

### Step A: Build job universe
- Script: `scripts/Job_model/enh_job_universe.py`
- Input: `singles_RURO_ready.parquet`, `couples_RURO_ready.parquet`
- Main action:
  - Build discrete jobs from `(hours_bin, wage_bin, isco1)` cells (grid modes).
  - Optional: build **latent job types** per occupation (GMM mode), with posted reps and optional within-type contract draws.
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

## 2) Applied edits (comprehensive summary)

This is the consolidated list of code changes applied in response to the identification‑stabilizing prompt and subsequent requests.

### A. Job universe and draws (job-choice pipeline)
- **New universe mode `gmm_occ`** in `scripts/Job_model/enh_job_universe.py`:
  - Fits **GMM within each ISCO1** on `(log yivwg_base, lhw_base)` using working deciders.
  - Chooses `K_o` by BIC subject to **min count/weight** constraints (fallback to `K=1`).
  - Produces **posted bundles** per type (mean or trimmed mean).
  - **Optional within‑type contract draws** via `--gmm-contract-draws` (adds `type_draw_id`).
  - Outputs `type_id`, `type_draw_id`, `hours_rep`, `wage_rep`, `yem_rep`.
  - Metadata stores GMM params, scalers, and deterministic `job_id_map`.
- **New baseline mode `posted`** in `scripts/Job_model/enh_job_draws.py`:
  - Draw=0 uses posted reps from the universe (default).
  - `cell_rep` retained as legacy alias.
  - For `gmm_occ`, baseline job_id is assigned by **posterior argmax** within occupation.
  - Proposal priors remain (`q_j_prior`, `log_q_*`) and are applied unchanged.
- **Sanity checks** extended in `scripts/Job_model/sanity_checks_job.py`:
  - For `gmm_occ`, enforce `type_id` + `type_draw_id` + finite reps.
  - Validate `job_id=0` has zero hours/wage/yem and `type_draw_id=-1`.
- **Documentation updated**:
  - `scripts/Job_model/README_job_model.md` updated with `gmm_occ` usage and new args.
  - `scripts/Job_model/ACCEPTANCE_TESTS.md` updated with GMM checks + `type_draw_id`.

### B. Identification ladder in estimation (job-choice)
- **Offer-tier ladder (M0–M3)** implemented via YAML (market_opportunity.tier):
  - M0: working indicator only.
  - M1: `gsur × working`.
  - M2: `gsur × working × isco1` (base omitted).
  - M3: one extra dimension (`hours_bin` OR `wage_bin`) with `gsur` interactions.
- **Choice‑set centering** (optional):
  - `market_opportunity.center_within_choice_set` with `center_weights` (uniform/proposal).
  - Implemented with safe GAMS aliasing to avoid compile errors.
- **Offer‑only exclusions enforced**:
  - Variables declared offer‑only are blocked from preferences at parse time.
- **Shifter scaling**:
  - `market_opportunity.variable_scales` supported (e.g., `gsur: 10.0`) for stability.
- **Specs created/extended**:
  - `estimation_spec_job_M0.yaml` → `M3` family (+ centered/scaled variants).

### C. Post‑estimation reporting (job-choice aware)
- **Model‑aware branch** in `RURO_post_estimation_styled.py`:
  - Adds **Job Market Opportunity Equation** section when `beta_offer_*` exist.
  - Flags degenerate/zero SEs in parameter tables to avoid false confidence.


## 3) Identification-stabilizing edits that were implemented (summary view)

These are code-level changes already applied to support the identification ladder and stabilization tests:

1) **Offer-tier ladder via YAML (`market_opportunity.tier`)**
   - M0: working indicator only
   - M1: `gsur × working`
   - M2: `gsur × working × isco1`
   - M3: optional `gsur × working × (hours_bin OR wage_bin)` (one dimension only)

2) **Choice-set centering (optional)**
   - Added centered opportunity index within choice set.
   - Implemented using GAMS alias set to avoid compile errors.
   - YAML: `market_opportunity.center_within_choice_set` + `center_weights`.

3) **Offer-only exclusions enforced**
   - If a variable is declared offer-only (e.g., `gsur`), it is blocked from preferences.

4) **Offer shifter scaling**
   - Added `market_opportunity.variable_scales` (e.g., `gsur: 10.0`) to rescale shifters.
   - Applied consistently in the vectorized GAMSPy estimator (singles + couples).

5) **New specs created for tests**
   - `estimation_spec_job_M2_centered.yaml`
   - `estimation_spec_job_M2_lite.yaml`
   - `estimation_spec_job_M2_scaled.yaml`
   - `estimation_spec_job_M2_lite_scaled.yaml`


## 4) Model that is currently estimated

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


## 5) Why identification is hard in this setup

The estimated index is additive:

`U_pref + log_market - log(prior)` (plus optional `log_h`, `log_w` terms).

Main implication:
- Without strong excluded variation, preference and opportunity can substitute each other in-sample.
- You identify the combined index well enough for prediction, but decomposition into "taste" vs "opportunity" can be weak/unstable.


## 6) Evidence from recent runs

### A) Baseline job-choice (older v0_plus family)
- `run_2026-02-05_10-48-29` (v0_plus / IPOPT): LL ~ -22411.64, rho2_prior ~ 0.1069, but weak ID.
- `run_2026-02-05_11-07-11` (v0_plus_b / IPOPT): LL ~ -22161.64, but MU regularity degraded and ID weak.
- `run_2026-02-05_11-36-48` (v0_plus_id / CONOPT): LL ~ -24364.10, underfit, several bounds.

### B) Identification ladder tests (M1/M2 family)
- **M1** (`job_choice_M1_participation_opportunity`):  
  LL ~ -24603.36; condition number = inf; negative eigenvalues; stable but weak curvature.
- **M2 centered** (`job_choice_M2_occupation_access_centered`):  
  LL ~ -23869.11; several offer params hit bounds; ID still weak (cond = inf).
- **M2 no centering** (`job_choice_M2_occupation_access`):  
  LL ~ -23676.59 (best LL so far), but very large offer coefficients and bound hits.
- **M2 scaled** (`job_choice_M2_occupation_access_scaled`):  
  LL ~ -23641.81; offer magnitudes stabilized; still cond = inf; theta_c hit upper bound.
- **M2 lite** (`job_choice_M2_occupation_access_lite_centered`):  
  LL ~ -24370.06; fewer bounds, but curvature still weak.
- **M2 lite scaled** (`job_choice_M2_occupation_access_lite_scaled`):  
  LL ~ -24370.06; coefficients small; ID still weak (cond = inf).

Interpretation so far:
- M2 improves LL, but the offer block is still weakly identified in a single year.
- Scaling reduces extreme magnitudes but does not fix curvature.


## 7) Where issues are most likely

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


## 8) Practical path to a model that fits better and is more identifiable

1. **Stack multiple years** (best fix):
   - gsur varies more → offer block becomes identifiable.
2. **If staying single-year**, keep opportunity block lean:
   - `working + gsur` only (M1), or M2‑lite with very few occupation interactions.
3. **Only add extra dimensions (M3)** once M2 is stable across years.
4. Use multi-start / warm-start comparisons to detect instability.
5. Prefer holdout predictive checks (out-of-sample LL, rho2).


## 9) Discussion checklist

- Are we prioritizing:
  - best in-sample fit, or
  - interpretable decomposition of preference vs opportunity?
- Which variables are allowed in opportunity but excluded from utility?
- Should we enforce stronger economic regularity (MUC/MUL) even at fit cost?
- Do we have additional labor-demand instruments by occupation/region/year?
