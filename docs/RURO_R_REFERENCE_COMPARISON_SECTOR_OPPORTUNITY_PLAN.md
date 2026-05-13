# RURO Comparison With R reference And Sector Opportunity Extension Plan

Date: May 11, 2026

Scope: compare the current French RURO code with the R reference work and propose a cleaner extension with three opportunity layers: labor time, wages, and sector.

Files compared:

- `ruro/Ruro_estimation_H.Rmd`
- `ruro/Ruro_estimation_new.Rmd`
- `ruro/Ruro_functions_EMRWS.R`
- `ruro/Ruro_simulation_H.Rmd`
- Current Python/GAMSPy pipeline under `scripts/enhanced/`
- Current job-choice pipeline under `scripts/Job_model/`

## Short Answer

the R reference's empirical estimation has two explicit opportunity components:

```text
utility + hours opportunity + wage opportunity - proposal prior
```

His hours opportunity also includes the employment/non-employment margin, so it is better described as a labor-time opportunity block rather than only an hours density.

Your current continuous RURO branch is structurally close to the R reference's model: preferences, hours opportunity, wage opportunity, and prior correction.

Your current job-choice branch is different. It already introduces something close to a third opportunity object through discrete jobs:

```text
job = hours_bin + wage_bin + isco1 occupation + latent type_id
```

and through a `market_opportunity` block with `beta_offer_*` parameters. But this is not yet a clean continuous-RURO third layer. Sector/occupation is bundled inside the empirical job draw and then adjusted by a market-opportunity index. It is not yet a separately defined sector opportunity density with its own proposal correction and structural interpretation.

The recommended next step is to explicitly factor the opportunity model as:

```text
employment / labor-time opportunity
+ sector opportunity
+ hours conditional on sector
+ wage conditional on sector and/or hours
```

In likelihood form:

```text
V = U(consumption, leisure)
  + O_time(employment, hours | X)
  + O_sector(sector | X)
  + O_wage(wage | sector, hours, X)
  - log q(employment, sector, hours, wage | X)
```

This would be closer to the R reference's logic, but extended with your proposed sector dimension.

## 1. What R reference Does

### 1.1 Choice-Set Proposal

In `Ruro_estimation_new.Rmd`, R reference builds estimation choice sets using a simple proposal distribution:

- Draw non-employment with probability `pi0`.
- Otherwise draw hours uniformly on `[h_min, h_max]`.
- In variable-wage mode, draw wages uniformly on `[w_min, w_max]`.
- Store the proposal density as `prior` on the log scale.

Code references:

- `ruro/Ruro_estimation_new.Rmd:126-165`: repeats each household and draws random hours/wages.
- `ruro/Ruro_estimation_new.Rmd:166-178`: assigns fixed-wage or variable-wage alternatives.
- `ruro/Ruro_estimation_new.Rmd:553-575`: computes the log proposal prior.

For variable wages:

```text
prior = log(q_hours * q_wage)
```

For fixed wages:

```text
prior = log(q_hours)
```

### 1.2 Likelihood

the R reference's likelihood is:

```text
P(observed choice) =
    exp(util + hopp + wopp - prior)
  / sum_j exp(util_j + hopp_j + wopp_j - prior_j)
```

Code references:

- `ruro/Ruro_estimation_new.Rmd:839-868`: likelihood.
- `ruro/Ruro_estimation_new.Rmd:874-904`: utility.
- `ruro/Ruro_estimation_new.Rmd:906-928`: hours/labor-time opportunity.
- `ruro/Ruro_estimation_new.Rmd:930-956`: wage opportunity.

The three parts are:

| Component | Code name | Meaning |
| --- | --- | --- |
| Preferences | `util` | Utility from consumption and leisure, with demographic shifters. |
| Labor-time opportunity | `hopp` | Availability/intensity of employment and focal hours. |
| Wage opportunity | `wopp` | Log-normal density of observed or simulated wages, conditional on working. |
| Proposal correction | `prior` | Log density of the proposal used to generate alternatives. |

### 1.3 Simulation

the R reference's simulation is also important because it shows how he uses the estimated opportunity model to generate counterfactual opportunity sets.

In `Ruro_functions_EMRWS.R`, the simulation generator:

- Computes gender-specific hour density normalizers `gamma0_m` and `gamma0_f`.
- Uses estimated `hopp` parameters to determine employment intensity.
- Draws hours from a piecewise distribution with peaks around part-time and full-time schedules.
- Draws wages from the estimated log-normal wage opportunity model in variable-wage mode.

Code references:

- `ruro/Ruro_functions_EMRWS.R:365`: `f_choicesets_sim`.
- `ruro/Ruro_functions_EMRWS.R:396-413`: hour density normalizers and focal-hour mass.
- `ruro/Ruro_functions_EMRWS.R:419-452`: employment intensity and hours draws.
- `ruro/Ruro_functions_EMRWS.R:461-470`: wage draws from the wage opportunity model.

Then `Ruro_simulation_H.Rmd` simulates choices using utility plus Gumbel shocks:

- `ruro/Ruro_simulation_H.Rmd:279-354`: simulation wrapper.
- `ruro/Ruro_simulation_H.Rmd:355-381`: predicted choice by maximum `util + gumb_draw`.

So the structure is:

```text
1. Estimate preferences and opportunity densities.
2. Use opportunity densities to simulate feasible alternatives.
3. Use preference utility plus random shocks to pick alternatives.
```

## 2. What Your Current Code Does

### 2.1 Continuous RURO Branch

Your continuous branch is closest to Stijn.

The active likelihood in Python/GAMSPy has the same form:

```text
U + log_h + log_w + log_market - log(prior)
```

Important files:

- `scripts/enhanced/enh_RURO_draws.py`: continuous hours/wage draws.
- `scripts/enhanced/enh_RURO_euromod.py`: counterfactual EUROMOD outputs.
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`: MNL construction and priors.
- `scripts/enhanced/gamspy_estimation_vectorized.py`: current production vectorized estimator.
- `scripts/enhanced/estimation_engine.py`: NumPy/SciPy reference likelihood.
- `scripts/enhanced/estimation_spec_v3.yaml`: rich continuous RURO spec.

The main difference is empirical performance: your continuous French outputs currently do not give stable Hessian diagnostics, so they are not yet strong enough for final identification claims.

### 2.2 Job-Choice Branch

Your job-choice branch is different from R reference because it changes the object being drawn.

Instead of drawing continuous hours and wage independently, it builds a job universe:

```text
job = (hours_bin, wage_bin, isco1, optional type_id)
```

Important files:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/Job_model/run_job_ruro_pipeline.py`
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml`

The job universe code explicitly states:

```text
A "job" is a discrete bundle: (hours_bin, wage_bin, isco1-digit occupation).
```

The job draw code uses:

```text
prior = pi0                      for non-employment
prior = (1 - pi0) * q_job         for employment
log_q_total = log_q_state + log_q_job
```

So in your current job-choice data, the proposal density is already decomposed into:

```text
employment state proposal + job proposal
```

The current best model, `estimation_spec_job_M2h_pruned.yaml`, adds a market opportunity block:

- `beta_offer_working`
- `beta_offer_isco1_*`
- `beta_offer_type_2`
- `beta_offer_gsur_*`

This is conceptually close to a third opportunity object, but it is not named or structured as a sector density. It is a market/job access index.

### 2.3 Current Sector Data Availability

I checked the processed French MNL files:

- The current job-choice MNL files contain `isco1`, `loc`, `loc4`, `type_id`, and `job_id`.
- They do not currently expose a NACE/sector variable in the final MNL files.
- The continuous MNL files contain `loc`/`loc4`, but not a clean sector variable.

This matters because `ISCO` is occupation, while `NACE` is sector/industry. If by "sector" you mean industry, you need to carry a NACE-like variable through the pipeline. If you are willing to use occupation as a first proxy, your current `isco1` or `loc4` variables are already available.

## 3. Key Differences Between R reference And Your Current Work

| Dimension | R reference | Your continuous RURO | Your job-choice RURO |
| --- | --- | --- | --- |
| Opportunity layers | Labor time and wage | Labor time and wage | Employment/job bundle plus market index |
| Sector/occupation | Not modeled as separate layer | Not modeled as separate layer | ISCO/loc/type embedded in job bundle and market terms |
| Proposal distribution | Simple uniform hours/wage proposal | Continuous proposal, now with `log_q_total` in current files | Empirical job proposal `q_job` |
| Prior correction | `- prior`, where `prior` is log proposal density | `- log(prior)`, where current files store original-scale prior | `- log(prior)`, with `prior = exp(log_q_total)` |
| Simulation logic | Estimated opportunity generates alternatives | Current continuous branch can generate alternatives, but not yet stable empirically | Job universe generates discrete job alternatives |
| Sector extension readiness | Would need new layer | Needs data and likelihood extension | Closest starting point because jobs already include ISCO/type |
| Identification risk | Two opportunity components already hard | Continuous results unstable | Better diagnostics, but sector/job availability is not yet cleanly separated |

## 4. Recommended New Model

If you want to extend the R reference's approach, define the opportunity decomposition explicitly.

### Singles

For a single person:

```text
V_ij =
    U(C_ij, L_ij; preference parameters)
  + O_E(e_ij | X_i)
  + 1[e_ij = 1] * O_S(s_ij | X_i)
  + 1[e_ij = 1] * O_H(h_ij | s_ij, X_i)
  + 1[e_ij = 1] * O_W(w_ij | h_ij, s_ij, X_i)
  - log q(e_ij, s_ij, h_ij, w_ij | X_i)
```

Where:

- `O_E` is employment/non-employment opportunity.
- `O_S` is sector opportunity.
- `O_H` is hours or labor-time opportunity conditional on sector.
- `O_W` is wage opportunity conditional on sector and possibly hours.
- `q` is the proposal density used to generate alternatives.

### Couples

For couples, sum partner-specific opportunities:

```text
V_hj =
    U(C_hj, L_mhj, L_fhj)
  + O_E_m + O_S_m + O_H_m + O_W_m
  + O_E_f + O_S_f + O_H_f + O_W_f
  - log q_joint
```

The joint prior should equal:

```text
q_joint = q_male * q_female
```

or, on the log scale:

```text
log_q_joint = log_q_male + log_q_female
```

## 5. What Counts As Sector Opportunity

You need to choose one interpretation:

### Option A: Occupation Opportunity, Fastest Path

Use existing `isco1` or `loc4`.

Pros:

- Already present in current MNL files.
- Already used in the job-choice universe.
- Existing `beta_offer_isco1_*` terms can be renamed/reinterpreted as occupation opportunity.
- Minimum data engineering.

Cons:

- ISCO is occupation, not industry sector.
- The interpretation is "occupation access", not sector access.

### Option B: True Sector Opportunity, Better Research Design

Use NACE or another industry/sector code.

Pros:

- Matches the word "sector" more directly.
- Better for labor-demand and industry-shock interpretation.
- Allows sector-specific policy or demand scenarios.

Cons:

- Current final MNL files do not carry NACE.
- You need to add the sector variable earlier in data prep and carry it through draws, EUROMOD, MNL construction, estimation, and post-estimation.

Recommendation: start with Option A as a prototype, then move to Option B if the source data have reliable NACE/industry information.

## 6. Implementation Plan

### Phase 0: Decide Sector Definition

Decide whether the new layer is:

```text
occupation opportunity: ISCO / loc / loc4
```

or:

```text
sector opportunity: NACE / industry
```

For thesis/report language, do not call ISCO a sector unless you explicitly define it as an occupation-sector proxy.

### Phase 1: Data Audit

Check the raw and prepared French files for:

- `nace`
- `nace1`
- `sector`
- `industry`
- `loc`
- `loc4`
- `isco1`

Current final MNL status:

- Job-choice MNL has `isco1`, `loc`, `loc4`, `type_id`, `job_id`.
- Continuous MNL has `loc`, `loc4`.
- Final MNL does not currently expose NACE.

If NACE exists upstream, add it to:

- `scripts/enhanced/enh_france_data_prep.py`
- `scripts/enhanced/enh_RURO_prep.py`
- `scripts/enhanced/enh_RURO_draws.py` or the job draw scripts
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/reduce_mnl_columns.py`
- `scripts/enhanced/estimation_utils.py`

### Phase 2: Define The Proposal Factorization

Do not add a sector opportunity term unless the proposal correction is clean.

For a true three-layer proposal, store:

```text
log_q_state
log_q_sector
log_q_hours_given_sector
log_q_wage_given_sector_hours
log_q_total
prior = exp(log_q_total)
log_prior = log_q_total
```

For a discrete job proposal, you can keep:

```text
log_q_state
log_q_job
log_q_total
```

but then `log_q_job` bundles sector, hours, and wage. That is simpler, but less transparent.

Recommended factorization:

```text
q(e, s, h, w | X)
  = q_e(e | X)
    * q_s(s | e = 1, X)
    * q_h(h | s, e = 1, X)
    * q_w(w | h, s, e = 1, X)
```

### Phase 3: Add A `sector_opportunity` Spec Block

Add a new YAML block rather than overloading `market_opportunity`:

```yaml
sector_opportunity:
  variable: "nace1"      # or "isco1" / "loc4" for prototype
  reference: 1
  applies_to: "both"
  center_within_choice_set: true
  center_weights: "proposal"
  shifters:
    - variable: "sector_2"
      coefficient: "beta_sector_2"
      interaction: ["working"]
    - variable: "sector_3"
      coefficient: "beta_sector_3"
      interaction: ["working"]
    - variable: "sector_unemployment"
      coefficient: "beta_sector_unemp"
      interaction: ["working"]
    - variable: "sector_share_region"
      coefficient: "beta_sector_share"
      interaction: ["working"]
```

Keep this separate from preferences. Do not initially add sector dummies to utility. Otherwise you are trying to estimate both "people like sector S" and "sector S is available", which is hard to separately identify.

### Phase 4: Extend The Estimator

Files to update:

- `scripts/enhanced/estimation_spec_parser.py`
  - Parse `sector_opportunity`.
  - Add `beta_sector_*` parameters to the parameter list.
  - Add bounds and initial values.

- `scripts/enhanced/gamspy_estimation_vectorized.py`
  - Add `log_sector` for singles and couples.
  - Add `log_sector` into the composite utility before the prior correction.
  - Apply within-choice-set centering, ideally proposal-weighted.

- `scripts/enhanced/estimation_engine.py`
  - Add the same `log_sector` component to the NumPy/SciPy reference likelihood.

- `scripts/enhanced/gamspy_estimation.py`
  - Add non-vectorized support only if you still need that path.

- `scripts/enhanced/estimation_utils.py`
  - Load sector dummies and sector-level shifters into the precomputed data classes.

- `scripts/enhanced/RURO_post_estimation_styled.py`
  - Report sector opportunity parameters and observed-vs-predicted sector distributions.

### Phase 5: Draws And Job Universe

Two possible implementations:

#### Path 1: Incremental, Based On Existing Job Universe

Use current job universe:

```text
job = hours_bin + wage_bin + isco1 + type_id
```

Then add an explicit sector/occupation opportunity term in estimation:

```text
log_sector = beta_sector_isco2 * isco1_2 + ...
```

This is the fastest path, but `log_q_job` still bundles sector, hours, and wage.

#### Path 2: Clean Stijn-Style Factorization

Build a new sector-aware draw system:

1. Draw employment.
2. Draw sector from empirical or modeled `q_s`.
3. Draw hours conditional on sector.
4. Draw wage conditional on sector and hours.
5. Store all log proposal pieces separately.

Potential new files:

- `scripts/Job_model/enh_sector_universe.py`
- `scripts/Job_model/enh_sector_draws.py`

or extend:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`

The clean factorized version is better for research claims but more work.

### Phase 6: Specification Ladder

Do not jump directly to the full model. Estimate a ladder:

| Spec | Purpose |
| --- | --- |
| `sector_M0` | Current M2h pruned baseline, no new sector layer. |
| `sector_M1` | Add sector/occupation availability intercepts only. |
| `sector_M2` | Add sector availability with region and education interactions. |
| `sector_M3` | Add hours opportunity conditional on sector. |
| `sector_M4` | Add wage opportunity conditional on sector. |
| `sector_M5` | Optional sector preferences in utility, only after opportunity layer is stable. |

At every step check:

- Convergence.
- Hessian eigenvalues.
- Parameters at bounds.
- Standard errors.
- Observed vs predicted sector shares.
- Observed vs predicted hours distribution by sector.
- Observed vs predicted wage distribution by sector.
- Stability across seeds and draw counts.

### Phase 7: Identification Strategy

A sector opportunity layer will not identify itself just because it is in the formula. You need variation that shifts sector availability without being pure preference.

Good opportunity-only shifters:

- Region-by-sector employment shares.
- Region-by-sector unemployment.
- Sector vacancy or labor-demand proxies.
- Sector employment growth.
- Education-by-sector availability.
- Lagged local sector composition.

Preference-side variables should be different:

- Age.
- Children.
- Household composition.
- Non-labor income.
- Education only if it is theoretically a taste shifter; otherwise use it mostly as an opportunity/productivity shifter.

Best practice for the first sector model:

```text
sector variables enter opportunity only
sector does not enter utility
```

Then, after the opportunity layer is stable, test a separate sector-preference layer.

## 7. How This Would Differ From Stijn

Your proposed model would be a real extension of Stijn, not just a translation.

Stijn:

```text
V = U + O_time + O_wage - log q(time, wage)
```

Your proposed sector RURO:

```text
V = U + O_time + O_sector + O_wage - log q(time, sector, wage)
```

or, if hours and wages are conditional on sector:

```text
V = U
  + O_employment
  + O_sector
  + O_hours_given_sector
  + O_wage_given_sector_hours
  - log q(employment, sector, hours, wage)
```

This is more realistic for labor markets, but it increases identification pressure. You need stronger diagnostics and stronger exclusion restrictions than the R reference's two-opportunity model.

## 8. How This Differs From Your Current Job-Choice Model

Current job-choice model:

```text
Draw job_id from empirical q_job.
job_id already contains hours, wage, ISCO, and type.
Estimate a market-opportunity index with beta_offer_* terms.
```

Proposed sector-opportunity model:

```text
Draw or define sector explicitly.
Estimate a sector opportunity density O_sector.
Estimate hours and wage opportunity conditional on sector.
Keep a transparent proposal correction for each proposal layer.
```

The difference is transparency and interpretation.

Current:

```text
sector/occupation opportunity is embedded in job access
```

Proposed:

```text
sector opportunity is a named, separate layer
```

## 9. Recommended First Concrete Step

Start with an occupation-sector prototype using existing `isco1` or `loc4`, because it is already in the processed data.

Concrete first version:

```text
V = U + O_time + O_wage + O_occ - log q
```

where:

```text
O_occ = beta_occ_2 * 1[isco1 = 2] * working
      + beta_occ_3 * 1[isco1 = 3] * working
      + ...
```

This is basically a cleaned-up and renamed version of the current `beta_offer_isco1_*` idea.

Then decide whether to replace `isco1` with true NACE sector after you verify the upstream data.

## 10. Files Most Likely To Change

Data/draws:

- `scripts/enhanced/enh_france_data_prep.py`
- `scripts/enhanced/enh_RURO_prep.py`
- `scripts/enhanced/enh_RURO_draws.py`
- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/reduce_mnl_columns.py`

Estimation:

- `scripts/enhanced/estimation_spec_parser.py`
- `scripts/enhanced/gamspy_estimation_vectorized.py`
- `scripts/enhanced/estimation_engine.py`
- `scripts/enhanced/estimation_utils.py`
- `scripts/enhanced/gamspy_estimation.py` if needed

Specs:

- New `scripts/enhanced/estimation_spec_sector_M1.yaml`
- New `scripts/enhanced/estimation_spec_sector_M2.yaml`
- Possibly revise `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml`

Post-estimation:

- `scripts/enhanced/RURO_post_estimation_styled.py`
- `scripts/enhanced/sanity_checks.py`
- `scripts/Job_model/sanity_checks_job.py`

## 11. Main Risks

1. Calling ISCO a sector when it is occupation.
2. Adding sector to both utility and opportunity too early.
3. Double-counting sector through both `q_job` and `O_sector` without a clear proposal correction.
4. Adding many sector parameters when the French sample has only 4,253 households.
5. Repeating the continuous v3 problem: many flexible parameters but weak Hessian diagnostics.
6. Losing the good diagnostics of M2h pruned by expanding too fast.

## 12. Recommended Claim After This Extension

If implemented and validated, the stronger claim would be:

> The model extends the RURO opportunity framework by decomposing job availability into labor-time opportunity, sector/occupation opportunity, and wage opportunity. This allows the model to distinguish whether a worker's observed choice is driven by preferences over consumption and leisure, the availability of hours, the availability of sectors/occupations, or the wage distribution within those sectors.

Before validation, use the weaker claim:

> The current job-choice branch already contains an implicit occupation/job availability channel. The next methodological step is to make that channel explicit as a separate sector or occupation opportunity layer, following the R reference's additive opportunity-density logic.

