# JMP NC Pilot beta_l0_m Specification Review v1

## 1. Purpose

This memo reviews the active lower-bound result for `beta_l0_m` in the NC pilot scaled-JAX estimator.

The scaled-JAX estimator protocol is conditionally accepted for NC pilot numerical estimation, but inference and economic interpretation remain blocked because `beta_l0_m` is an active bound parameter at the validated solution.

The purpose of this review is to define what the `beta_l0_m` corner means, why it matters, which explanations are plausible, and what diagnostic slice is authorized before standard errors or welfare are considered.

## 2. Current estimator status

The formal scaled-JAX validation passed.

Evidence:

- Report: `Results/JMP_NC_pilot_scaled_JAX_validation_report_v1.md`
- Accepted optimizer protocol: JAX float64, validated v2 likelihood kernel, S2c scaling, L-BFGS-B in scaled coordinates, native-scale reporting.
- Scaling rule: `scale[i] = max(abs(theta_CONOPT[i]), 1e-3)`.
- Model, data, native bounds, and `theta_c = 0` are unchanged.
- All three starts reached tolerance stops:
  - Start A, `theta_CONOPT`: LL = `-16526.99259532`, nit = 16.
  - Start B, cold/defaults: LL = `-16526.99746997`, nit = 631.
  - Start C, perturbed: LL = `-16526.99282219`, nit = 241.
- LL spread = `4.874648e-03`, passing both the 0.1 pilot threshold and the stricter 0.01 threshold.

This validates the numerical optimizer protocol. It does not yet validate inference, standard errors, welfare, or economic interpretation.

## 3. What beta_l0_m represents

`beta_l0_m` is the male leisure intercept/loading in the couples utility block.

It contributes to the level of male leisure utility, while other terms, including `theta_l_m` and the couples leisure interaction parameter `beta_ll`, shape curvature and complementarity with female leisure.

In the validated scaled-JAX solutions, the male leisure intercept is not behaving as a regular interior parameter. It is pressed to its lower bound while the likelihood gradient points further downward.

## 4. Evidence for active lower-bound corner

Across all three scaled-JAX validation starts:

| Start | Final `beta_l0_m` | Bound | `grad_ll(beta_l0_m)` | Verdict |
|---|---:|---:|---:|---|
| A | `1.0e-6` | lower | `-6.0801` | active constraint |
| B | `1.0e-6` | lower | `-6.1028` | active constraint |
| C | `1.0e-6` | lower | `-6.0808` | active constraint |

The sign is important. The gradient is negative at the lower bound, meaning the likelihood would like to move `beta_l0_m` below the imposed floor if it were allowed.

This is not a transient from an unconverged run. All three starts reached tolerance stops and agreed on the same objective value within `0.00487` LL units.

The parameter movement pattern is also informative:

- `beta_l0_m` moves from the CONOPT value `0.01221947` to `1e-6`.
- `beta_ll` rises from `2.18174841` to about `2.1941` to `2.1949`, a movement of roughly `+0.0123` to `+0.0132`.
- `beta_l0_f` remains interior around `1.816` to `1.818`.

That pattern suggests the standalone male leisure loading is being pushed to the regularity floor while the couples leisure-interaction term absorbs part of the effective male leisure weight.

## 5. Why this matters for inference

Conventional inverse-Hessian standard errors assume an interior optimum where the score is zero and the local curvature describes sampling uncertainty around an unconstrained maximum.

That regularity condition fails for `beta_l0_m`.

At the accepted scaled-JAX point:

- `beta_l0_m` is at the lower bound.
- The projected-gradient diagnostic says the constraint is active.
- The unconstrained score does not vanish.

Therefore, ordinary Hessian-based standard errors for `beta_l0_m` would not have their usual interpretation. Standard errors for the remaining parameters also depend on how the active constraint is handled.

This is why verdict-grade SEs are blocked until this review is resolved.

## 6. Why this matters for economic interpretation

Interpreting `beta_l0_m = 1e-6` as a direct economic result would be premature.

The corner could mean that married men's standalone leisure intercept is genuinely close to zero in this pilot specification. It could also mean that the male leisure intercept is weakly identified separately from the leisure interaction term or other preference terms.

The empirical asymmetry is important:

- Female leisure intercept `beta_l0_f` remains comfortably interior.
- Male leisure intercept `beta_l0_m` collapses to the floor.
- The interaction `beta_ll` rises.

This is consistent with a familiar labor-supply pattern: married men's labor supply may be less elastic in this couples sample, while female leisure and couples leisure interaction carry more of the variation. But that is a hypothesis to diagnose, not an accepted result.

## 7. Possible interpretation 1: legitimate monotonicity/regularity bound

The lower bound may be a regularity restriction intended to keep the standalone male leisure weight non-negative.

Under this interpretation, the data want the smallest admissible positive male leisure intercept. The active constraint is then a legitimate corner solution under the imposed utility regularity.

This interpretation would support either:

- keeping `beta_l0_m` bounded and free with boundary-aware inference; or
- fixing `beta_l0_m` at the regularity floor and estimating the remaining parameters as an active-set specification.

This interpretation is plausible because the lower bound is extremely small (`1e-6`) and the solution is stable across starts.

## 8. Possible interpretation 2: weak identification / normalization issue

The data may identify the effective male leisure contribution but not the decomposition between the standalone male intercept and the couples leisure interaction.

The pattern supporting this interpretation is:

- `beta_l0_m` falls by about `-0.012218`.
- `beta_ll` rises by about `+0.0123` to `+0.0132`.
- The fit remains stable across starts.

This suggests a near-substitution direction between `beta_l0_m` and `beta_ll`.

If this interpretation is correct, fixing `beta_l0_m` at the floor may have little effect on the remaining estimates and may be the cleanest pilot treatment.

## 9. Possible interpretation 3: misspecified male leisure utility block

The corner may reflect misspecification in the male leisure utility block.

Potential sources include:

- the functional form of male leisure utility;
- scaling of normalized leisure;
- the interaction between male and female leisure terms;
- weak separation assumptions in the couples utility block;
- insufficient flexibility in male participation or hours margins.

If diagnostics show that the corner materially distorts male participation or hours fit, this interpretation becomes more likely and a respecification memo would be needed.

## 10. Possible interpretation 4: pilot-data artefact

The result could be specific to the 2016 NC pilot sample or to the 900-alternative product draw design.

This is less likely than the weak-identification or regularity-bound explanations because:

- the optimizer protocol now converges cleanly from cold and near-oracle starts;
- the bound result is stable across all three starts;
- female leisure remains interior;
- the issue is localized rather than a general failure of the utility block.

Still, it should be checked against fit diagnostics and, later, against alternative pilot specifications before being treated as a paper-facing substantive claim.

## 11. Option A: keep beta_l0_m bounded and free

Under Option A, `beta_l0_m` remains a bounded free parameter with lower bound `1e-6`.

Advantages:

- Preserves the current specification exactly.
- Retains the active-bound result as a transparent feature of the constrained optimization.
- Avoids changing the parameter vector before diagnostics.

Risks:

- Standard Hessian SEs are not regular for an active-bound parameter.
- Inference would need boundary-aware treatment or active-set handling.
- A future reader may mistake the bound value for a regular interior estimate.

Option A is acceptable only if the follow-up diagnostic explicitly defines an inference treatment for the active constraint.

## 12. Option B: fix beta_l0_m at lower bound

Under Option B, `beta_l0_m` is fixed at `1e-6` for the pilot SE run.

Advantages:

- Converts the active constraint into an explicit specification restriction.
- Allows regular interior SEs for the remaining parameters, conditional on the active-set specification.
- Avoids treating the boundary parameter as if it were an unconstrained interior estimate.
- Matches the numerical finding that all validated starts choose the floor.

Risks:

- It imposes a modelling decision that must be documented.
- It may hide uncertainty about whether the floor itself is the correct regularity restriction.
- It should not be used if fixing `beta_l0_m` materially shifts other key parameters.

Option B is the leading immediate candidate if diagnostics show that fixing `beta_l0_m` at the floor leaves the rest of the model essentially unchanged.

## 13. Option C: relax lower bound and allow negative values

Under Option C, the lower bound is relaxed and `beta_l0_m` is allowed to move below zero.

This is not authorized as a specification change at this stage.

It may be useful only as a bounded diagnostic probe to learn whether:

- the likelihood improves materially below zero;
- the implied male leisure utility remains economically coherent;
- effective leisure weights stay positive over the relevant support.

Risks:

- Negative standalone male leisure loading may violate the intended regularity or monotonicity of the utility block.
- It may create implausible utility behavior.
- It changes the specification rather than simply diagnosing the active constraint.

Option C requires explicit justification before any production use.

## 14. Option D: reparameterize or respecify the male leisure block

Under Option D, the male leisure block is changed to address weak identification or functional-form pressure.

Possible directions include:

- reparameterizing the male leisure intercept to separate level and interaction effects;
- rescaling leisure terms;
- fixing one of the near-collinear terms;
- modifying the interaction structure;
- reviewing whether `beta_ll` and `beta_l0_m` are jointly over-flexible for the pilot sample.

Option D is broader than the immediate diagnostic need. It should be considered only if the diagnostic shows material instability in fit or in other key parameters when `beta_l0_m` is fixed or profiled.

## 15. Recommended diagnostic checks

Authorize a narrow diagnostic slice before choosing the final SE protocol.

Required checks:

1. Local likelihood profile around `beta_l0_m` near the lower bound:
   - at `1e-6`;
   - at small positive values above the floor;
   - optionally at small negative values only as a diagnostic probe if explicitly bounded and labelled.

2. Fit implications for male participation and male hours:
   - compare predicted participation/hours fit at the floor and nearby values;
   - report whether the corner is connected to a particular margin.

3. Fixed-parameter diagnostic:
   - fix `beta_l0_m = 1e-6`;
   - re-optimize the remaining parameters if cheap;
   - compare LL and parameter movement against the accepted scaled-JAX solution.

4. Relaxed-bound diagnostic:
   - only as a diagnostic;
   - do not adopt negative values as a specification without a separate decision;
   - test whether effective male leisure utility remains coherent.

5. Collinearity/substitution diagnostic:
   - inspect the local relationship between `beta_l0_m`, `beta_ll`, `theta_l_m`, and related leisure terms;
   - report whether `beta_l0_m` is redundant with `beta_ll` or other leisure parameters.

## 16. Recommended immediate decision

Do not interpret `beta_l0_m` economically yet.

Do not compute final SEs yet.

Do not relax the lower bound as a specification change.

Proceed to a narrow `beta_l0_m` diagnostic slice. The leading provisional treatment is Option B, fixing `beta_l0_m` at the lower bound for a later SE run, but only if diagnostics show negligible movement in the remaining parameters and no material fit deterioration.

## 17. What is authorized next

The next authorized task is a diagnostic report:

`Results/JMP_NC_pilot_beta_l0_m_diagnostic_report_v1.md`

Authorized diagnostics:

- local likelihood profile for `beta_l0_m`;
- fixed-`beta_l0_m` re-optimization of remaining parameters, if cheap and controlled;
- limited relaxed-bound probe only if explicitly labelled diagnostic;
- male participation and hours fit checks;
- parameter-shift diagnostics, especially for `beta_ll`, `theta_l_m`, `beta_l0_f`, `beta_occ_*`, `beta_E_gsur`, region terms, and wage terms;
- recommendation among Options A-D.

## 18. What is not authorized

Not authorized:

- final SE computation;
- Hessian or cluster-robust SE production;
- welfare computation;
- SA2 issuance;
- NC pilot promotion;
- M1-clean replacement;
- 40x40 product expansion;
- full P3a rebuild;
- production data modification;
- frozen YAML modification;
- unbounded relaxation of `beta_l0_m`;
- economic interpretation of the active-bound result.

M1-clean 2016 remains the active baseline. Corrected pooled P3a remains unaffected.

## 19. Required follow-up report

The follow-up report must be:

`Results/JMP_NC_pilot_beta_l0_m_diagnostic_report_v1.md`

It must state:

- whether the diagnostic PASSED, FAILED, or HALTED;
- whether `beta_l0_m` should remain bounded/free, be fixed at the bound, be relaxed, or be respecified;
- whether SE computation is ready after the diagnostic;
- whether the fixed-bound active-set treatment leaves the remaining estimates stable;
- whether `beta_ll` absorbs the male leisure intercept in a way consistent with weak identification;
- whether male participation and hours fit changes materially;
- that no welfare was computed;
- that no SA2 was issued;
- that the NC pilot was not promoted;
- that M1-clean 2016 remains active.

The current review disposition is: the scaled-JAX estimator protocol is conditionally accepted for numerical estimation, but inference is blocked until `beta_l0_m` is resolved. The next gate is the narrow `beta_l0_m` diagnostic slice.
