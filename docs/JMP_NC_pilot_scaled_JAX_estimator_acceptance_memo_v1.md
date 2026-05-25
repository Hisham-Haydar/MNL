# JMP NC Pilot — Scaled-JAX Estimator Acceptance Memo v1

*France RURO multi-year extension | v1 | 2026-05-25*

**Document category: estimator-protocol acceptance memo, conditional.** Records
the verdict of the formal scaled-JAX validation and **conditionally accepts the
scaled-JAX estimator protocol for NC-pilot numerical estimation**, subject to a
`beta_l0_m` active-bound review before any inference or economic interpretation.
This is acceptance of an **optimization procedure**, not of an economic result.
The NC pilot is not promoted over M1-clean; welfare and SA2 remain unauthorized;
standard errors remain blocked pending the bound review. M1-clean 2016 active;
corrected pooled P3a unaffected.

---

## 1. Purpose

To certify, on the evidence of the three-start scaled-JAX validation, that the
vectorized JAX estimator equipped with the S2c scaling constitutes a reliable
numerical procedure for locating the NC-pilot couples-2016 maximum-likelihood
optimum — and to delimit precisely what that certification does and does not
license. The acceptance is conditional: it establishes that the procedure
converges reproducibly to a common optimum from heterogeneous starting points,
while reserving inference and economic interpretation until the active
lower-bound status of `beta_l0_m` has been adjudicated by a separate
specification review.

---

## 2. Evidence reviewed

The scaled-JAX validation executed three starts under the S2c scaling rule
`scale[i] = max(|θ_CONOPT[i]|, 1e-3)`, optimizing in scaled coordinates with
L-BFGS-B on the validated float64 v2 likelihood kernel, reporting on the native
scale, under the pilot bounds with `theta_c` fixed at 0.0:

| Start | Initialization | Initial LL | Final LL | Termination | nit | ‖Δθ‖ vs θ_CONOPT |
|---|---|---|---|---|---|---|
| A | scaled `theta_CONOPT` | −16,527.0670 | **−16,526.99260** | TOLERANCE_STOP | 16 | 2.045e-02 |
| B | scaled pilot defaults (cold) | −24,501.9737 | **−16,526.99747** | TOLERANCE_STOP | 631 | 6.926e-02 |
| C | scaled perturbed (seed 17, mag 0.05) | −16,616.9837 | **−16,526.99282** | TOLERANCE_STOP | 241 | 2.469e-02 |

The cross-start log-likelihood spread is **4.87 × 10⁻³**, which satisfies both
the 0.1 pilot-diagnostic threshold and the stricter 0.01 threshold stipulated in
the authorizing document. All three starts terminated by tolerance
(`CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH`), none by iteration cap.
The float64 kernel produced no non-finite objective or gradient values. At all
three converged points, `beta_l0_m` rests at its lower bound of 1 × 10⁻⁶ with a
strictly negative likelihood gradient (grad_ll ≈ −6.08 to −6.10), classified by
the projected-gradient diagnostic as an active lower-bound corner.

---

## 3. Scaled-JAX validation verdict

**PASS.** The validation satisfies its conjunctive acceptance criterion: all
three starts reached tolerance-based stops, and their final log-likelihoods agree
to 4.87 × 10⁻³ — within both the pilot and the stricter threshold. The agreement
is the more compelling for the heterogeneity of the initializations: start B
commenced 7,975 log-likelihood units below the optimum (from cold defaults) and
nonetheless converged to within 5 × 10⁻³ of the near-oracle starts A and C. The
near-oracle disagreement of 0.341 log-likelihood units observed in the unscaled
optimizer-protocol diagnostic has collapsed by approximately two orders of
magnitude under uniform scaling. The procedure thus locates a single, common
optimum reproducibly across the tested starting points.

---

## 4. What is now accepted

The **scaled-JAX estimator protocol is conditionally accepted** as the numerical
estimation procedure for NC-pilot couples-2016, where the protocol comprises:

1. **Backend and precision:** JAX in float64 (`jax_enable_x64`).
2. **Likelihood:** the validated v2 likelihood kernel (4th-order Taylor Box-Cox;
   preference, hours-, wage-, occupation-, and market/GSUR/region-opportunity
   components; proposal-weighted centering; −log prior).
3. **Scaling:** the S2c rule `scale[i] = max(|θ_CONOPT[i]|, 1e-3)`.
4. **Optimizer:** L-BFGS-B operating in scaled coordinates, with consistently
   transformed bounds.
5. **Reporting:** all parameters reported on the native scale.
6. **Invariants:** the same model, data, and bounds as the pilot CONOPT
   specification; `theta_c` fixed at 0.0.

The acceptance is of this procedure's capacity to converge reliably to the
couples-2016 optimum. It is conditional on the `beta_l0_m` active-bound review
(§9, §12) preceding any inference or economic interpretation.

---

## 5. What is not accepted

This memo accepts a numerical procedure; it does **not** accept an economic
result. Specifically, none of the following is accepted or authorized by this
document:

- The converged parameter vector as an **economic estimate** of preferences or
  opportunities (the `beta_l0_m` corner is unresolved).
- **Inference** of any form — standard errors, the Hessian beyond a documented
  cheap diagnostic, or cluster-robust covariance.
- **Welfare** computation or **inequality decomposition.**
- **Sensitivity analysis (SA2)** or any **promotion** of the NC pilot.
- Displacement of **M1-clean 2016** as the active baseline.
- Any **scaling-up** of the choice set (40×40 / 1,600 alternatives), or extension
  to **pooled, singles**, or a **P3a rebuild.**

---

## 6. Interpretation of the resolved HV-AGREE halt

The HV-AGREE halt that arrested the original three-start validation — a
cross-start spread of approximately 770 log-likelihood units — is now resolved,
and resolved in the manner anticipated by the optimizer-protocol diagnostic
correction: the disagreement was an artifact of **optimizer conditioning**, not
of multimodality. The controlled Stage-2 contrast had already isolated scaling as
the operative variable, with scaled L-BFGS-B recovering the basin from cold
defaults where unscaled L-BFGS-B and an Adam warm-up both failed. The present
validation confirms that proposition under the decisive test the diagnostic could
not perform: with the scaling applied **uniformly across all three starts**, the
starts converge to a common optimum. A genuinely multimodal likelihood would not
be rendered concordant by a mere change of optimization coordinates; concordance
under rescaling is dispositive of conditioning as the cause. The cold-start
failure is therefore retired as a numerical, not a substantive, phenomenon.

---

## 7. Accepted optimizer protocol

The accepted protocol is, in full: **JAX float64; the validated v2 likelihood
kernel; the S2c scaling rule `scale[i] = max(|θ_CONOPT[i]|, 1e-3)`; L-BFGS-B in
scaled coordinates; native-scale reporting; the same model, data, and bounds as
the pilot CONOPT specification; and `theta_c` fixed at 0.0.** Tolerance settings
that permit a tolerance-based stop (ftol 1e-9, gtol 1e-7) and an iteration budget
sufficient for cold-start convergence (the cold start required 631 iterations;
the near-oracle starts, 16 and 241) are integral to the protocol. This protocol
supersedes the unscaled optimizer configuration for NC-pilot numerical estimation
and is the configuration to be used for any subsequent NC-pilot estimation runs
that this governance process authorizes.

---

## 8. Accepted scaling rule

The scaling rule is `scale[i] = max(|θ_CONOPT[i]|, 1e-3)`, applied componentwise
across the 35-parameter vector. The optimizer operates on rescaled coordinates
`θ̃[i] = θ[i] / scale[i]`, with bounds transformed consistently and all reported
quantities mapped back to the native scale via `θ[i] = θ̃[i] · scale[i]`. The 1
× 10⁻³ floor binds on precisely two near-zero parameters — `beta_l_age2_f` and
`beta_w_pexp2`, whose CONOPT magnitudes (≈ 6.3 × 10⁻⁴ and ≈ 6.0 × 10⁻⁴) fall
below the floor — and is the device that conditions the otherwise ill-scaled
gradient (parameter magnitudes span approximately seven orders of magnitude). The
rule is a change of optimization coordinates only; it leaves the model, the data,
the native-space bounds, and the fixed `theta_c` untouched, and is therefore
neutral with respect to the economic content of the estimates.

---

## 9. Status of beta_l0_m

The male leisure intercept `beta_l0_m` rests at its lower bound of 1 × 10⁻⁶ at
all three tolerance-converged points, with a strictly negative likelihood
gradient (grad_ll ≈ −6.08 to −6.10) that the projected-gradient diagnostic
classifies as an **active lower-bound corner**: the likelihood would be increased
by moving the parameter below the bound, were the bound not present. This is now
established as a **stable feature of the converged optimum**, observed
consistently across the oracle, perturbed, and cold-start solutions, and not a
convergence transient. Its economic content remains **uninterpreted**. A corner
solution on the male leisure intercept raises a substantive question — whether
the bound is an artifact of the parameterization or whether the datum genuinely
prefers a degenerate male leisure baseline, with attendant identification
implications — that must be adjudicated by specification review before the
estimate carries economic meaning. This memo records the corner as a numerical
fact and defers its interpretation.

---

## 10. Why inference is not yet authorized

Inference is withheld for a principled, not merely procedural, reason. Standard
errors derived from the inverse Hessian presuppose an **interior** maximum at
which the score is zero and the curvature is informative about sampling
variability. At the present optimum, `beta_l0_m` is at an active constraint with a
non-zero projected gradient, so the regularity conditions underpinning the usual
asymptotic covariance do not hold for that parameter, and the Hessian-based
covariance for the remaining parameters is conditioned on a boundary solution
whose validity is itself unresolved. Computing standard errors before
adjudicating the corner would therefore produce numbers of uncertain
interpretation and risk lending spurious precision to a solution whose
specification is in question. Inference is accordingly blocked until the
`beta_l0_m` review determines whether the corner is to be retained, the bound
respecified, or the parameterization revised.

---

## 11. What remains blocked

- **Standard errors and all inference** (Hessian beyond a cheap documented
  diagnostic; cluster-robust covariance) — blocked pending the `beta_l0_m`
  review.
- **Economic interpretation of `beta_l0_m`** and of the converged vector —
  pending the same review.
- **Welfare** computation and **inequality decomposition.**
- **SA2** and any **promotion** of the NC pilot.
- **M1-clean 2016 displacement.**
- **Choice-set scaling-up** (40×40 / 1,600), **pooled**, **singles**, and **P3a
  rebuild.**
- No change to the model formula, data, or bounds; prior reports, oracle JSONs,
  and the precomputed object remain unmodified.

---

## 12. Next gate

**`docs/JMP_NC_pilot_beta_l0_m_specification_review_v1.md`.** The next document is
a specification/bounds review of the `beta_l0_m` active lower-bound corner, which
must determine — before any inference or economic interpretation — whether the
corner reflects (i) a benign parameterization artifact for which the bound or the
parameterization should be revised, (ii) a genuine data-driven degeneracy of the
male leisure baseline with identification consequences, or (iii) a feature to be
retained and handled by boundary-aware inference. Only upon the disposition of
that review does the subsequent gate — verdict-grade estimation with appropriate
(possibly boundary-aware) standard errors — become available, and only thereafter
the welfare and decomposition stages that constitute the paper's contribution.

---

## 13. Required final statements

- **The scaled-JAX estimator protocol is conditionally accepted for NC-pilot
  numerical estimation,** subject to the `beta_l0_m` active-bound review before
  any inference or economic interpretation.
- **The accepted protocol is:** JAX float64; the validated v2 likelihood kernel;
  the S2c scaling `scale[i] = max(|θ_CONOPT[i]|, 1e-3)`; L-BFGS-B in scaled
  coordinates; native-scale reporting; the same model, data, and bounds; and
  `theta_c` fixed at 0.0.
- **This is an estimator-protocol acceptance, not an economic result.**
- **The NC pilot is not promoted over M1-clean 2016.**
- **Welfare remains unauthorized; SA2 remains unauthorized.**
- **Standard errors remain blocked until `beta_l0_m` is reviewed.**
- **`beta_l0_m` is an active lower-bound corner** at all three tolerance-converged
  points and **requires a specification/bounds review before inference or
  economic interpretation.**
- **The next gate is `docs/JMP_NC_pilot_beta_l0_m_specification_review_v1.md`.**
- M1-clean 2016 active; corrected pooled P3a unaffected; prior reports, oracle
  JSONs, and the precomputed object unmodified.

---

*Status: scaled-JAX estimator acceptance memo v1 — conditional acceptance of the
numerical protocol. Three-start scaled validation PASSED (LL spread 4.87e-03,
both thresholds; three tolerance stops). HV-AGREE resolved as conditioning, not
multimodality. beta_l0_m a stable active lower-bound corner, uninterpreted;
inference blocked pending its review. Estimator-protocol acceptance, not an
economic result; NC pilot not promoted; welfare/SA2 unauthorized; M1-clean 2016
active. Next: docs/JMP_NC_pilot_beta_l0_m_specification_review_v1.md.*
