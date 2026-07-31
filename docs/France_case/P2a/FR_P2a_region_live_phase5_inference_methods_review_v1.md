**Mission:** JMP-M05 Stage C — independent statistical-methods review  
**Mode:** independent, read-only review; no source edit, code, inference computation, or repository operation  
**Date:** 2026-07-31

## 1. Review verdict

The Phase-5 design is methodologically sound in its central construction, but it is not yet ready for manager acceptance in its present wording. The household score, sign convention, aggregation identity, sum scaling, conditional bread, household-level meat, and prohibition on ordinary symmetric Wald inference for the two bound coordinates are all correctly specified. The proposed 35-dimensional sandwich is a defensible covariance for the **restricted pseudo-true QMLE**, conditional on the two upper-bound constraints being strictly active in the population.

Seven narrow corrections are required. The most important is to separate a valid model-based Loewner comparison from claims about the misspecification-robust sandwich and downstream functional uncertainty. The memo currently proves an ordering for inverse-Hessian objects but then extends it, without justification, to robust standard errors and to the direction of decomposition-uncertainty bias. The remaining corrections concern the finite-sample-correction rationale, Wald-test indexing, the reporting schema for bound coordinates, several numerical-gate definitions, conditional language about future clustering and the regional channel, and durable retention under the disclosure fallback.

No finding is E2: none requires changing the accepted model, the accepted estimate, the conditional estimand, or the recommended Phase-5 baseline. All seven corrections can be merged in one pass.

## 2. Scope

This review evaluates the final Stage-B design against the twenty review questions, the four targeted corrections, and the Stage-C addendum's priority targets. It does not reconsider the accepted P2a specification, point estimate, pins, bounds, Phase-3 result, or Phase-4 curvature result. It does not compute a score, covariance, standard error, Wald statistic, p-value, welfare quantity, or decomposition quantity.

The statistical target reviewed here is limited to uncertainty for the accepted France 2016 singles P2a region-live constrained QMLE, with 1,555 household likelihood contributions, 37 free coordinates before active-set conditioning, 35 locally interior coordinates, two strictly active upper-bound coordinates, and ten fixed pins.

Repository facts are taken only from the accepted Stage-A audit and its evidence files, as the Stage-C addendum requires. Methodological judgments are made independently and are not inferred from the design author's internal consistency.

## 3. Sources reviewed

The following supplied files were reviewed in full:

1. `JMP_canonical_state_v1.md`;
2. `JMP_decision_log_v1.md`;
3. `JMP_M05_phase5_inference_mission_charter_v1.md`;
4. `JMP_M05_task_plan_v1.md`;
5. `JMP_M05_task_plan_manager_acceptance_v1.md`;
6. `JMP_M05_mission_ledger_v2.md`;
7. `FR_P2a_region_live_phase5_source_verification_v1.md`;
8. `phase5_parameter_map_v1.csv`;
9. `phase5_source_inventory_v1.json`;
10. `JMP_M05_source_verification_completeness_v1.md`;
11. `JMP_M05_stageB_author_addendum_v1.md`;
12. `FR_P2a_region_live_phase5_inference_design_v1.md`.

The accepted Phase-3 and Phase-4 manager memos and `phase4_diagnostics.json` were not supplied as standalone Stage-C attachments. Their relevant contents, paths, hashes, and accepted scalars were audited in the Stage-A source-verification report and inventory, and the completeness memo ratified that audit. Consistent with the addendum, this review therefore cites those repository facts through the audit rather than pretending to have independently reopened the repositories. This attachment limitation is not charged against the design memo.

For the methodological questions, the review also checked the primary literature: [Geyer (1994), constrained M-estimation](https://projecteuclid.org/journals/annals-of-statistics/volume-22/issue-4/On-the-Asymptotics-of-Constrained-M-Estimation/10.1214/aos/1176325768.full), [Andrews (1999), estimation on a boundary](https://dido.econ.yale.edu/~dwka/pub/p0988.pdf), [White (1982), misspecified QMLE](https://faculty.utrgv.edu/diego.escobari/teaching/Econ8370/Papers/White%281982%29Econometrica-Corey.pdf), and [Cameron and Miller (2015), cluster-robust inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf).

## 4. Likelihood and score definition

The memo defines the correct primitive contribution:

\[
V_{gj}=u_{gj}+\log h_{gj}+\log w_{gj}+\log m_{gj}-\log p_{gj},
\qquad
\ell_g=V_{g0}-\operatorname{logsumexp}_j(V_{gj}),
\]

with

\[
\operatorname{negLL}(x)=-\sum_{g=1}^{1555}\ell_g(x).
\]

This matches the verified production route. The memo correctly states that the wage-density, hours-offer, market/regional, occupation, and proposal-prior terms enter inside the alternative-specific index. It does not incorrectly decompose the household likelihood into a choice contribution plus separately additive density contributions.

The pin-fixed injection from the 37-vector to the 47-vector is also correctly defined. Pins remain at their accepted values; they are not replaced by zeros and are not differentiated. Consequently,

\[
s_g(x)=\nabla_x\ell_g(x)\in\mathbb R^{37}
\]

is the exact score of the verified household contribution under the accepted reparameterisation.

The sign convention is correct. The stored score is the gradient of the positive log-likelihood contribution, whereas the accepted bread is the Hessian of negative log-likelihood. Hence

\[
\sum_gs_g=\nabla_x\sum_g\ell_g=-\nabla_x\operatorname{negLL}.
\]

Because the objective is an unweighted household **sum**, no factor of (G), (1/G), survey weight, or alternative-row count is missing. The memo also complies with C-1 and F-1: the average negative log-likelihood is not used as evidence about density terms, and the invalid `ln(101)` benchmark is absent.

The recommended `jax.jacfwd` route is appropriate for a \(1555\times37\) Jacobian: forward mode scales with the 37 input tangents, whereas reverse-mode construction of all 1,555 output rows is the less attractive full-sample route. The 64-household `jacfwd`/`jacrev` agreement check is proportionate. The row-level \(157{,}055\times37\) Jacobian is correctly rejected because rows are alternatives inside household likelihood terms, not primitive additive contributions.

One gate-level clarification is still needed: T-4 must state the signed comparison explicitly as `max(abs(S.sum(0) + gradient_free_accepted))`, rather than the ambiguous phrase “free-gradient reproduction.” T-1 already has the correct sign.

## 5. Cluster interpretation

The verified structure is one household likelihood term per household cluster:

\[
G=1{,}555,qquad \#\{\ell_g\}=1{,}555,qquad
\text{terms per cluster}=1.
\]

Therefore the cluster score is identical to the primitive household score and

\[
\sum_{c=1}^{G}\left(\sum_{g\in c}s_g\right)
\left(\sum_{g\in c}s_g\right)'=\sum_{g=1}^{G}s_gs_g'.
\]

The memo's description “household-clustered and misspecification-robust,” accompanied by the explanation that it is algebraically the household-level OPG sandwich in this application, is accurate. The 101 alternatives are correctly treated as an implementation dimension inside one likelihood term, not as 101 independent observations.

The memo is also correct that the present sandwich does not add a within-household dependence adjustment beyond the household primitive. However, §20.3 contradicts the otherwise careful C-3 discipline when it says couples and pooled panels “will break” degeneracy. That is not known. They **may** do so, conditional on how their primitive likelihood contributions and repeated-unit structure are defined. The sentence must be made conditional.

The canonical row-order decision is sound. Each gender-specific loader order is already stable-`idhh` sorted; concatenating the two builder blocks and applying a stable argsort of the concatenated identifiers yields the same global `idhh`-ascending order used for the accepted Phase-4 regional design. T-3 makes the resulting artifact order unambiguous by requiring strict increase and equality to the sorted unique household IDs.

## 6. Model-based covariance

The bread is correctly sourced and scaled. The design requires:

1. loading the authoritative `hessian_free.npy` rather than the lossy CSV rendering;
2. verifying its file and bundle fingerprints;
3. checking the recorded asymmetry threshold;
4. symmetrising (H_s=(H+H')/2), as Phase 4 did;
5. selecting (H_{II}) by parameter name; and
6. obtaining solves through a Cholesky factorisation rather than an explicit matrix inverse.

For the restricted 35-dimensional model, the model-based object

\[
V_{\mathrm{model}}=H_{II}^{-1}
\]

has the correct sum-objective scaling. Since (H) is a Hessian of a sum, its inverse already has the sampling-scale factor implicit in it. Multiplying again by (G) or (1/G) would be an error. The average-objective algebra in §8.2 correctly demonstrates the equivalence.

The memo also correctly demotes this inverse-Hessian object to a diagnostic under possible misspecification. It is not the headline covariance for a pseudo-true QMLE unless the information-matrix equality is valid.

## 7. Robust covariance

The robust meat is constructed at the correct primitive level:

\[
S_I=S[:,I]\in\mathbb R^{1555\times35},
\qquad
M=S_I'S_I=\sum_{g=1}^{1555}s_{g,I}s_{g,I}',
\]

and the conditional sandwich is

\[
V_{\mathrm{robust}}=cH_{II}^{-1}MH_{II}^{-1}.
\]

This is the correct sandwich for the restricted pseudo-true QMLE when the active constraints can be treated as fixed equality restrictions asymptotically. Holding the two active coordinates fixed does not alter partial derivatives with respect to the other 35 coordinates, so taking the 35 columns from the verified 37-column primitive is valid.

The decision not to centre the meat is acceptable. The uncentred empirical second moment is the standard sandwich meat. In the restricted coordinates the published score-sum residual is only numerical non-stationarity, and W-5 requires both that residual and the omitted centring correction to be disclosed. Centring and non-centring are asymptotically equivalent here; the memo makes the convention visible.

The design must nevertheless correct one important comparison. The Loewner proof in §11.2 establishes only

\[
H_{II}^{-1}\preceq[H_s^{-1}]_{II}
\]

for the two **model-based inverse-information** objects. It does not establish a Loewner ordering between the restricted robust sandwich and any unrestricted or boundary-aware robust covariance, because the latter also depends on the full meat and its cross-blocks. The memo currently moves from the valid inverse-Hessian result to an unqualified statement that “conditional standard errors” are weakly smaller. That extension is unsupported.

## 8. Finite-sample correction

The inputs and arithmetic are coherent:

\[
G=N=1{,}555,qquad K=35,
\]

and therefore

\[
c=\frac{G}{G-1}\frac{N-1}{N-K}
=\frac{1555}{1554}\frac{1554}{1520}
=\frac{1555}{1520}
=1.0230263157894737.
\]

The alternative-row count (157{,}055) is correctly excluded from (N). Linking (K) to the locally estimated covariance object is also directionally correct: under strict population activity, the restricted estimating problem has local dimension 35, while the two boundary coordinates are fixed with probability approaching one.

The current justification is, however, too categorical. The assertion that (K) is “the number of exactly-satisfied first-order conditions” turns an HC1/CR1-style convention into an apparent theorem for nonlinear constrained M-estimation. It also places undue weight on whether a numerical optimizer residual is exactly zero. The more defensible statement is that (K=35) is the rank/dimension of the locally estimated restricted parameter vector and estimating system. The two-factor scalar is a transparent regression-analogue finite-sample convention, not an exact unbiasedness correction for this QMLE.

This distinction matters because Cameron and Miller describe the two-factor form in the linear-regression setting and note that cluster-only (G/(G-1)) is used for nonlinear extensions. The design may retain (1555/1520) as its pre-registered baseline—the numerical difference is immaterial—but it must remove the unsupported claims that a labour-economics referee necessarily expects it or that its nonlinear degrees-of-freedom interpretation follows mechanically from exact score equations.

## 9. Active-bound parameters

The direction and KKT analysis are correct. Both `beta_l_age2_sm` and `beta_l_age2_sf` equal their upper bound 1.0. For minimised negative log-likelihood subject to (x_j\le1), stationarity is

\[
\partial_j\operatorname{negLL}+\mu_j=0,
\qquad \mu_j\ge0.
\]

The accepted negative gradients therefore imply the positive multipliers reported in the memo. The feasible cone points toward non-positive movements in the two bound coordinates. ERR-1 is handled correctly.

The conditional 35-dimensional object is defensible for the stated estimand. If the population pseudo-true value has strictly positive multipliers, the same active set is selected with probability approaching one, the two constrained coordinates are locally constant, and ordinary asymptotic normality applies to the 35-dimensional restricted estimating system. Its bread is (H_{II}), not a Schur complement, and its meat is the 35-column score meat. This is consistent with the general constrained-M-estimation framework in Geyer and Andrews.

The memo also correctly prohibits every symmetric Wald interval, standard error, z-statistic, and p-value for the two bound coordinates. No boundary-aware alternative is required for the paper claims currently permitted, because those claims are explicitly conditional and exclude inference on the two coordinates themselves.

Three limitations must be stated more precisely:

- T-22 establishes strong **sample numerical KKT activity** relative to optimizer residuals. It is not a statistical test that proves strict activity of the population pseudo-true constraint.
- The inverse-Hessian Loewner comparison does not order robust covariance matrices or robust standard errors.
- Under genuine population strict activity, treating the boundary coordinates as fixed is the first-order asymptotic law of the constrained estimator; it does not automatically “understate” sampling variance. If active-set selection is non-negligible, no general directional ordering follows.

Accordingly, the downstream trigger must change. Material loading of a bound coordinate on a welfare functional is a reason to disclose conditioning and to consider bound/specification sensitivity. Boundary-aware or resampling inference becomes required if the paper wants inference on the bound coordinate, an unconditional claim integrating active-set selection, or a functional for which the strict-activity assumption is not defensible. Material loading alone does not prove that resampling is required, nor that the omitted uncertainty has a known positive direction.

T-19 is a useful gate on whether the accepted point is close enough to the restricted stationary point for the covariance calculation to be meaningful. Its coordinatewise comparison with 5% of the robust standard error is computable and conservative as a certification rule. T-22 is also useful as a numerical KKT gate, provided it is not promoted into proof of the population condition. W-4 is appropriately warning-tier with mandatory escalation because an interior estimate whose symmetric robust interval crosses a bound deserves review but is not thereby an active-bound estimate.

## 10. Fixed pins

The treatment of the ten pins is correct. They are imposed restrictions, not estimated coordinates. Eight are unreferenced by the singles likelihood and two multiply identically zero 2016 covariates. Their zero gradient reflects a flat likelihood direction, not a first-order condition and not infinite precision.

The literal `NA` convention is therefore superior to `0`, blank cells, or exclusion from the table. The two structural-inapplicability categories are source-verified, and the memo correctly creates no normalisation category. The mandatory footnote properly distinguishes the true normalisations outside the 47-vector.

The output schema is not yet internally consistent, however. Section 11.3 requires the bound rows to report bound value, bound side, gradient, and multiplier. Section 17.3 declares an exact parameter-table schema that contains none of those fields, while §17.2 separately mentions an undefined `flag` column. The implementation contract must either add explicit bound-diagnostic columns to the 47-row table or define a separate authoritative bound-parameter table. In either case, the five inferential fields must remain literal `NA` for both active-bound and pinned rows.

## 11. Regional/access inference

The memo properly distinguishes the ten-coordinate regional/urbanisation/GSUR access block from the complete opportunity mechanism and from the later welfare decomposition. It correctly separates:

- one continuous `gsur` rate;
- seven NUTS-1 indicators relative to region 1; and
- two urbanisation indicators relative to rural.

The proposed confirmatory and secondary nulls are substantively sensible: H0-A has ten restrictions; H0-B has seven; H0-C has two; and H0-G has one. Individual z-statistics are correctly treated as descriptive and unadjusted, while H0-A carries the confirmatory significance claim.

The Wald formula is not implementable as currently written. It declares \(R\in\mathbb R^{q\times35}\) but then inserts an undefined “\(V_{RR}\)-relevant” object, although \(V_{RR}\) itself is \(10\times10\). The memo must choose one of two equivalent, dimensionally valid formulations:

\[
W=(R\hat\theta_I-r)'(R V_I R')^{-1}(R\hat\theta_I-r),
\quad R\in\mathbb R^{q\times35},
\]

using the full \(35\times35\) covariance \(V_I\); or, more transparently,

\[
\theta_R=E_R\theta_I,
\quad V_{RR}=E_RV_IE_R',
\quad
W=(A\hat\theta_R-r)'(AV_{RR}A')^{-1}(A\hat\theta_R-r),
\]

where \(E_R\in\mathbb R^{10\times35}\) selects the access block and \(A\in\mathbb R^{q\times10}\) selects each null. All restrictions must be indexed by parameter name. The output must carry separate model-based and robust p-values if it carries both Wald statistics.

One phrase should also be narrowed. H0-B tests equality of the seven NUTS-1 intercept shifts to zero relative to region 1. Calling it the test that maps to a “common opportunity environment” counterfactual risks reviving the C-2/C-5 overclaim. It maps to a **common NUTS-1 intercept component**, not to common opportunities overall.

## 12. Numerical gates

The gate architecture is unusually strong in the right ways. It covers score identity and sign, exact shape, row completeness and order, float64, AD-mode agreement, parameter-name fingerprints, source hashes, bread symmetrisation, eigenvalue reproduction, factorisation-based solves, covariance symmetry, positive variances, correlation bounds, regional rank, active-set KKT strength, restricted-stationarity displacement, near-bound warnings, determinism, and post-evaluation immutability.

The priority gates are adequately tiered:

- T-19 is gating because a materially displaced restricted optimum would invalidate the covariance evaluated at the accepted point.
- T-22 is gating as a numerical strict-activity check, but must be labelled as such rather than as proof about the population.
- W-4 is warning-tier with mandatory escalation, which is appropriate for a nominally interior parameter whose robust Wald interval reaches a bound.
- T-16's 64-household forward/reverse agreement is a proportionate independent AD-route check.

Three definitions require repair:

1. The T-7/T-9 PSD tolerance `−1e-8 × max_eig` is excessively permissive for a 35-dimensional Gram matrix and is internally inconsistent with the `1e-10 × max_eig` rank tolerance. The memo calls it “one order” looser, although it is two orders looser. A Gram matrix formed as (S_I'S_I) should be PSD up to a backward-error tolerance tied to machine precision, dimension, and norm; at minimum, the PSD tolerance should not be looser than the declared rank tolerance without a concrete numerical-error bound.
2. T-4 must state the sign and norm explicitly: `max(abs(S.sum(0) + gradient_free_accepted)) <= 1e-12`.
3. W-4 must specify the headline robust interval, for example `theta_hat ± z_0.975 * se_robust`, and define how equality with a bound is treated. “Strictly inside” implies equality triggers the warning; this should be written explicitly.

Subject to these repairs, the PSD, rank, symmetry, score-identity, and fingerprint gates are adequate for certification.

## 13. Artifact and transaction contract

The `.npy`-authoritative score choice is proportionate and reproducible. The object is only about 0.44 MiB in raw float64 form, so size is not a reason to avoid a bit-exact artifact. The explicit `%.17g` CSV rendering, ordered-name file, row-index file, score summary, hashes, and manifest flags give a clear authoritative/non-authoritative distinction. D-7's canonical order makes the score hash deterministic and joinable.

The disclosure fallback is sensible in principle but incomplete as a certification contract. A hash and summaries do not preserve reproducibility if the authoritative bytes are merely left on one local machine outside version control. If the PI determines that household-level derived arrays cannot be committed, the memo must require the `.npy` to remain in a durable, access-controlled, immutable artifact store or restricted bundle; the manifest must record a non-public locator or custody identifier, hash, size, shape, order fingerprints, disclosure class, and retention responsibility. The public repository may contain only summaries and hashes. This review does not decide the licence question.

The staging/attempts/complete transaction pattern, dependency re-verification, one authorised real run, fresh-process reproducibility check, manifest-last rule, and environment logging are all adequate. The environment mandate correctly repairs the historical absence of JAX/jaxlib, platform, thread, and XLA metadata.

The artifact list must also be reconciled with the reporting correction in §10 of this review: either the parameter table gains the bound diagnostics or a dedicated authoritative bound-diagnostics artifact is added to the exact bundle set.

## 14. Interpretation limits

The memo succeeds on most interpretation boundaries. It explicitly separates local precision from identification, structural recovery, welfare, and decomposition. It prohibits causal readings, responsibility language, full-opportunity claims from the ten-coordinate block, average-negLL reasoning, and symmetric boundary Wald inference.

Four statements remain too strong:

1. The Loewner ordering is stated as though it applied to robust conditional versus marginal standard errors. It applies only to the inverse-Hessian comparison shown.
2. The memo says fixing active-bound coordinates and pins understates decomposition uncertainty and that the direction is known. That is not established. Under strict population activity, the constrained coordinates are first-order fixed; for structurally inapplicable pins, the current likelihood contains no information at all. Relative to a different unconstrained or respecified model, uncertainty is not ordered without further assumptions.
3. Section 20.3 says couples and pooled panels “will” make clustering non-degenerate. The correct statement is conditional.
4. H0-B is linked too directly to a common-opportunity counterfactual. It tests only the NUTS-1 intercept subchannel.

After these phrases are corrected, the paper-facing claim register is appropriately conservative.

## 15. Implementation feasibility

The design is implementable without reopening the accepted specification. The production likelihood already exposes the needed per-group vector; the 47-to-37 injection is verified; the 37-to-35 selection is name-keyed; the bread is persisted; household identifiers and canonical order are available; all four regional restrictions can be represented by fixed selection matrices; and the artifact/transaction structure is concrete.

The forward-mode score route is computationally appropriate and avoids the prohibited row-level Jacobian. Chunking at whole-household boundaries preserves the exact likelihood contribution. The cross-mode subset check and full-sample score identity together give adequate route validation.

Current implementation blockers are documentary, not structural: the malformed Wald notation, the missing bound-reporting fields, the ambiguous T-4/W-4 definitions, and the fallback-custody gap. Correcting them requires no optimizer, Hessian recomputation, model change, or new estimand.

## 16. Residual defects

| ID | Severity | Location | Defect | Consequence if uncorrected |
| --- | --- | --- | --- | --- |
| R-1 | Major | §§11.2, 19, 20.2 | Inverse-Hessian Loewner result is extended to robust SEs and to a claimed known direction of downstream uncertainty | Paper could misstate the conditional robust object's relation to an undefined marginal/boundary-aware covariance |
| R-2 | Moderate | §§10.3–10.4 | `K=35` is justified by “exactly-satisfied FOCs,” and the two-factor scalar is presented as a referee-expected nonlinear correction | Imports a linear-regression convention into constrained QMLE with a stronger rationale than the theory supports |
| R-3 | Major | §13.4; output test schema | Wald notation mixes a \(q\times35\) restriction with a \(10\times10\) covariance; model/robust p-value fields are not separated | Joint tests are not dimensionally implementable from the memo as written |
| R-4 | Moderate | §§11.3, 17.2–17.3 | Required bound value/side/gradient/multiplier have no declared output fields; `flag` conflicts with the exact schema | Implementation cannot satisfy both the boundary-reporting rule and the artifact contract |
| R-5 | Moderate | T-4, T-7/T-9, W-4 | Sign is ambiguous, PSD tolerance is too loose/internally misstated, and the near-bound interval does not name the SE | Gates can be implemented inconsistently or admit material indefiniteness |
| R-6 | Moderate | §§13.4, 20.3 | H0-B language overreaches and future cluster non-degeneracy is stated unconditionally | Violates C-2/C-3/C-5 language discipline |
| R-7 | Moderate | §17.1 fallback | “Stored outside version control” lacks durable restricted custody and locator requirements | Certification may retain only a hash, not reproducible authoritative bytes |

No residual defect requires changing the accepted model, estimate, active-set estimand, or Phase-5 baseline.

## 17. Required fixes

1. **Correct the boundary-covariance interpretation.** Limit the Loewner claim to \(H_{II}^{-1}\preceq[H_s^{-1}]_{II}\) for model-based inverse-information objects. Delete any general claim that the conditional robust SEs are weakly smaller than a marginal robust object. Replace the assertion that bound coordinates and pins necessarily understate downstream uncertainty in a known direction with: downstream inference is conditional on these restrictions and excludes active-set/specification uncertainty, whose magnitude and direction are not identified here. State that T-22 is numerical KKT evidence, not proof of population strict activity. Revise the later-method trigger as described in §9 of this review.

2. **Repair the finite-sample-correction rationale without changing the chosen scalar.** Define (K=35) as the local dimension/rank of the restricted estimating problem under strict activity. Describe (c=1555/1520) as a pre-registered HC1/CR1-style regression-analogue convention for this nonlinear sandwich, not an exact M-estimation unbiasedness correction and not something every labour-economics referee necessarily expects. Remove reliance on whether sample score equations are “exactly” satisfied.

3. **Make every regional Wald object dimensionally explicit.** Define the \(10\times35\) access selector \(E_R\), the \(10\times10\) covariance \(V_{RR}=E_RV_IE_R'\), and each \(q\times10\) restriction \(A\), or use a \(q\times35\) \(R\) with the full \(35\times35\) covariance. State \(r\), the solve, and the name-keyed rows for H0-A/B/C/G. Give separate `p_model` and `p_robust` fields when both Wald statistics are stored.

4. **Reconcile boundary reporting with the exact artifact schema.** Add `bound_value`, `bound_side`, `grad_negll`, and `multiplier` columns to the 47-row parameter table, or add a dedicated authoritative bound-diagnostics table to the exact bundle. Remove or define the stray `flag` column. Keep model SE, robust SE, ratio, z, and p as literal `NA` for active-bound and pinned rows.

5. **Repair the numerical-gate definitions.** Write T-4 as the signed max-norm identity; replace the T-7/T-9 `1e-8` relative PSD allowance with a machine-precision/backward-error tolerance or, at minimum, a threshold no looser than the `1e-10` rank convention unless quantitatively justified; and define W-4 using the robust 95% interval with equality to a bound explicitly triggering the warning. Preserve T-19 as gating, T-22 as a numerical KKT gate, and W-4 as warning plus mandatory escalation.

6. **Restore language discipline everywhere.** Replace “couples and pooled panels will break” degeneracy with a conditional statement tied to their future primitive contribution structure. Describe H0-B as testing the common NUTS-1 intercept component, not a common opportunity environment. Search the whole memo for equivalent unconditional or full-opportunity wording and apply the same correction.

7. **Complete the disclosure fallback.** Without deciding the licence question, require durable access-controlled retention of the authoritative `.npy` in an immutable restricted store or bundle when it cannot be committed. Record its custody/locator identifier, SHA-256, size, shape, row/column fingerprints, disclosure class, and retention responsibility in the manifest. Summaries and a hash alone are insufficient for internal reproducibility.

## 18. Whether manager acceptance may proceed

Manager acceptance should not freeze the present text. It may proceed after the seven fixes are incorporated and a targeted Stage-C recheck confirms:

- the conditional-35 estimand remains unchanged;
- no robust Loewner or known-direction uncertainty claim remains;
- the correction scalar is presented as a transparent convention;
- all Wald matrices conform dimensionally;
- the bound-reporting artifact is complete;
- the repaired numerical gates are exact and computable;
- C-2/C-3/C-5 language is consistent throughout; and
- the fallback preserves authoritative bytes under restricted custody.

The central D-2 decision may then be frozen: conditional \(35\times35\) model-based and robust covariance; \(H_{II}^{-1}\) bread; \(S_I'S_I\) meat; upper-bound rows excluded from symmetric Wald inference; conditional interpretation explicit. No alternative boundary-aware method is required for those limited claims. A separate method becomes necessary only if later work seeks inference on the bound coordinates, unconditional inference over active-set selection, or downstream inference for which strict population activity is not defensible.

No E2 escalation is required.

## 19. Immediate next action

Return this review to the Goal 1 Manager. Commission one narrow Stage-D remediation pass implementing fixes 1–7 in the design memo only, without modifying the accepted specification or producing code or inference. Return the revised memo to this reviewer for a targeted check of the corrected sections before the Goal 1 acceptance packet is issued.

APPROVE AFTER FIXES
