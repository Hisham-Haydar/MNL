# RURO Comparison To R reference And Action Plan

Date: May 11, 2026

This note compares the current French RURO code to the R reference's `ruro/Ruro_simulation_H.Rmd` and related R functions. It focuses on whether the current project can separately identify preferences and opportunities.

## the R reference's RURO Setup

the R reference's code separates three concepts:

1. A proposal distribution used to build simulated choice sets.
2. A RURO opportunity model for the availability of hours and wages.
3. A preference utility model that chooses among available alternatives.

In `ruro/Ruro_estimation_H.Rmd`, the likelihood is:

```text
probability of observed alternative
  = exp(util + hopp + wopp - prior)
    / sum over alternatives exp(util + hopp + wopp - prior)
```

Key references:

- `ruro/Ruro_estimation_H.Rmd:553-570` constructs `prior` as a log proposal density.
- `ruro/Ruro_estimation_H.Rmd:834-846` computes utility, hours opportunity, and wage opportunity.
- `ruro/Ruro_estimation_H.Rmd:853-859` applies `exp(util + hopp + wopp - prior)`.
- `ruro/Ruro_estimation_H.Rmd:867` defines the preference utility function.
- `ruro/Ruro_estimation_H.Rmd:899` defines the hours opportunity function.
- `ruro/Ruro_estimation_H.Rmd:923` defines the wage opportunity function.

In `ruro/Ruro_simulation_H.Rmd`, R reference can simulate outcomes because the data-generating parameters are known. That is the crucial difference from the French empirical application.

The opportunity generator is in `ruro/Ruro_functions_EMRWS.R`:

- `ruro/Ruro_functions_EMRWS.R:365` defines `f_choicesets_sim`.
- `ruro/Ruro_functions_EMRWS.R:396-413` builds focal-hour masses for male and female hours.
- `ruro/Ruro_functions_EMRWS.R:422-427` builds employment intensity terms using opportunity parameters and shifters.
- `ruro/Ruro_functions_EMRWS.R:433-452` transforms draws into hours.

The simulated choice stage then chooses using preference utility plus an extreme-value shock:

- `ruro/Ruro_simulation_H.Rmd:355` defines `ff_predchoice4`.
- `ruro/Ruro_simulation_H.Rmd:359-377` uses `util + gumb_draw`.

Because the R reference's simulation has known truth, separation between preferences and opportunity can be tested by recovery: generate with known parameters, estimate, and check whether the estimator recovers the known preference and opportunity parameters.

## Current Python/GAMSPy Setup

The current Python code mirrors the RURO likelihood structure:

- Preference utility is computed separately.
- Hours opportunity is computed separately.
- Wage opportunity is computed separately when the spec includes it.
- The job-choice branch can add a market opportunity component.
- The proposal correction is subtracted through `-log(prior)`.

Key references:

- `scripts/enhanced/estimation_engine.py:356` applies the singles likelihood index.
- `scripts/enhanced/estimation_engine.py:1245` applies the couples likelihood index.
- `scripts/enhanced/estimation_spec_v3.yaml` is the richer continuous wage RURO spec with consumption-leisure interactions.
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml` is the best current job-choice candidate.

The job-choice pruned spec is intentionally conservative:

- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml:18-20` declares the pruned job-choice model with fixed wage specification.
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml:45-53` keeps opportunity blocks but prunes unstable terms.
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml:53-105` defines market opportunity terms.
- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml:171-174` fixes `theta_c_sm` tightly.

## Main Differences From R Reference Design

| Dimension | R reference simulation | Current French code |
| --- | --- | --- |
| Object | Simulation and recovery environment | Empirical French 2016 estimation |
| Truth | Known parameters in the DGP | Unknown |
| Identification evidence | Can be checked by recovery | Must be inferred from diagnostics, restrictions, and robustness |
| Opportunity model | Continuous hours and wage opportunity DGP | Continuous RURO branch plus newer job-choice market opportunity branch |
| Prior convention | `prior` stored as log proposal density in R | Current French files store `prior` on original scale and `log_prior` separately |
| Strongest current output | Not applicable: simulation framework | Job-choice M2h pruned |
| Main weakness | Simulation does not prove empirical identification | Empirical continuous specs are unstable |

The current code is conceptually aligned with the R reference's likelihood. The current evidence is not yet aligned with the R reference's recovery standard.

## Why The French Continuous RURO Result Is Not Enough

The continuous French models are the closest analog to the R reference's `util + hopp + wopp - prior` setup. They are also the weak point empirically.

Observed diagnostics:

- The older base run did not converge.
- The v2 run has a Hessian condition number around `1.48e23` and 4 negative eigenvalues.
- The v3 run has a Hessian condition number around `2.45e27` and 3 negative eigenvalues.

Those diagnostics mean the optimizer can produce parameter values, but the local curvature does not support clean structural interpretation. In practice, this means some combination of preference and opportunity parameters can move together without the likelihood strongly distinguishing them.

## Why The Job-Choice Branch Is More Promising

The job-choice branch uses a richer empirical opportunity object: a generated job set with a proposal correction and a centered market opportunity component. The best current result is:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/estimation_results.json
```

That run has:

- `850600` rows and `4253` households.
- `prior_correction_applied = true`.
- `market_centering_applied = true`.
- Hessian condition number around `1.28e6`.
- `0` negative Hessian eigenvalues.
- No listed poorly identified parameters.

This is the best current empirical baseline. The limitation is interpretation: it separates preferences from a job-market opportunity index, not necessarily from the exact continuous hours/wage opportunity process in the R reference's simulation.

## Action Plan

### 1. Fix The Prior Convention Everywhere

Make the data convention universal:

```text
prior     = proposal probability/density, original scale, strictly positive
log_prior = log(prior)
```

Then use `-log_prior` in all likelihood implementations, or use `-log(prior)` only after asserting that `prior` is strictly positive and on the original scale.

Current issue to fix:

- `scripts/enhanced/enh_RURO_prep_mnl_basic.py:1449` sets `df["prior"] = np.log(prior_density)` in the singles continuous fallback.
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py:1573` does the same in the couples continuous fallback.

The recent `log_q_total` path is correct, but the fallback should not remain inconsistent.

### 2. Add A Continuous-RURO Recovery Test

This is the most important missing piece.

Procedure:

1. Take the French-shaped sample and generated alternatives.
2. Choose known preference parameters and known opportunity parameters.
3. Generate opportunities from the opportunity model.
4. Generate choices using utility plus Gumbel shocks.
5. Estimate the model with the current Python/GAMSPy estimator.
6. Compare estimated parameters to the known truth.

Minimum pass criteria:

- Preference signs and magnitudes are recovered within tolerance.
- Opportunity signs and magnitudes are recovered within tolerance.
- Recovery is stable across seeds.
- Recovery improves as the number of households or alternatives grows.
- Hessian has no negative eigenvalues at the recovered optimum.

Without this recovery test, the French empirical results cannot be benchmarked against the R reference's simulation standard.

### 3. Strengthen Exclusion Restrictions

The model needs variables that help one side of the likelihood without also loading on the other side.

Opportunity-only candidates:

- Region-by-education job availability.
- Occupation availability.
- Local unemployment or labor demand.
- Region-by-occupation shares.
- Job-type availability.
- Market tightness by skill group.

Preference-only candidates:

- Age and age squared.
- Children and child age groups.
- Household composition.
- Partner interactions.
- Non-labor income.
- Demographic terms that should affect preferences but not the objective job-offer process.

Avoid putting the same variables into both preference and opportunity blocks unless the theoretical reason is explicit and the resulting parameters remain stable.

### 4. Stabilize The Continuous RURO Specification

Before using the rich v3 continuous spec for interpretation:

1. Start from a minimal continuous model.
2. Estimate preference-only with opportunity fixed.
3. Estimate opportunity-only with preferences fixed.
4. Add hours opportunity.
5. Add wage opportunity.
6. Add interactions last.
7. Use multiple starts and multiple draw seeds.
8. Track Hessian eigenvalues, bounds, standard errors, and parameter drift at each step.

The current v3 interaction model should be treated as exploratory until this ladder is stable.

### 5. Keep The Job-Choice Pruned Model As The Baseline

For near-term empirical reporting, use `estimation_spec_job_M2h_pruned` as the baseline because it has the best diagnostics. Report it as:

```text
An empirical RURO-style job-choice model with separated preference and market-opportunity components.
```

Do not report it as:

```text
A final proof that continuous preferences and continuous opportunity are separately identified.
```

### 6. Define Diagnostic Gates For Identification Claims

Only claim separate identification after all of these pass:

| Gate | Current status |
| --- | --- |
| Separate preference and opportunity blocks in code | Pass |
| Correct proposal/prior correction in current French files | Pass |
| Continuous RURO convergence | Fail or weak |
| Continuous RURO positive Hessian curvature | Fail |
| Job-choice Hessian diagnostics | Pass for M2h pruned |
| Parameters away from problematic bounds | Partial |
| Simulation recovery against known truth | Missing |
| Stability across draw seeds and starts | Missing or incomplete |
| Clear exclusion restrictions | Partial |
| Out-of-sample or holdout validation | Missing |

## Suggested Wording For A Report

Use language like this:

> The current implementation follows the RURO likelihood structure by decomposing the choice index into preference utility, hours/wage opportunity, optional market opportunity, and a proposal correction. On the French 2016 data, the software can estimate these blocks jointly. However, the continuous RURO specifications currently show weak curvature diagnostics, so they do not yet support a strong claim that preferences and opportunities are separately identified. The most credible current empirical specification is the pruned job-choice model, which provides a more stable separation of preferences from market opportunity, but this should be treated as provisional until simulation recovery and robustness checks are completed.

## Bottom Line

Compared with the R reference's work, your code has the right architecture but not yet the same identification evidence. the R reference's simulation can validate separation because the true DGP is known. Your French empirical pipeline needs a recovery experiment and stronger robustness diagnostics before you can make the same claim.
