# RURO Occupation-Opportunity M0 — Strict Estimation Triage Memo v1

Date: 2026-05-13

Scope: France 2016, `estimation_spec_ruro_occ_M0`, joint singles+couples,
GAMSPy CONOPT vectorized. Triage of the FIRST converged M0 optimum
(predecessor run `run_2026-05-13_11-27-40`, 29 iterations, joint_ll = −6499.88;
post-estimation re-run inspected here is `run_2026-05-13_15-02-16`, which
warm-started at the same theta and exited in 1 iteration — this is why every
"Initial → Final Movement" row reads Δ = 0 and is not a separate failure).

Verdict, stated once up front so it is not lost in the detail: **this run is
diagnostic only. It is not publishable. It is not yet prototype-usable for
welfare or decomposition. The optimum reached is locally indefinite, the
within-sample fit is catastrophic on hours and participation, and two
preference parameters have no standard error.**

---

## 1. What has been successfully completed

The data and code pipeline is in good standing. This is the first time the
M0_ruro_occ spec has both estimable inputs and an executing solver run.

- The full RURO occupation-opportunity rebuild has landed. Per the rebuild report,
  all 9 post-MNL canary checks pass: `loc4` varies within household (median
  4.0 distinct values across simulated working alternatives for singles and
  for each partner of couples), all four proposal-component aliases
  (`log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ` and partner-suffixed
  analogues) are present, `prior > 0` everywhere, `log_prior == log(prior)`,
  per-layer prior reconstruction holds (`max_abs_log_prior_minus_log_density
  = 0` for both datasets), and no M0-forbidden columns
  (`lindi`/`industry`/`nace`/`log_q_job`/`log_q_state`/`log_q_total`) remain
  in the keep set. The two distinct prior-mass minima in the uploaded summary
  (`7.82e−06` singles vs `6.29e−11` couples) are consistent with two
  partner-specific component multiplications and are not by themselves a
  problem.
- The YAML spec `estimation_spec_ruro_occ_M0` parses cleanly as
  `model_family: regular`, exposes a dedicated `occupation_opportunity`
  block with `loc4` reference category 1, uses Mincer-form wage opportunity
  with the log-normal Jacobian, and applies `−log(prior)` prior correction
  exactly once per alternative. `prior_correction_applied = 1`,
  `prior_correction_form = "-log(prior)"`, `market_centering_applied = 1`.
  These metadata fields are now present in the run output, as required by
  the §22 diagnostics list of the model contract.
- The solver terminates with `ModelStatus.OptimalLocal` and `SolveStatus.
  NormalCompletion`. Twenty-nine CONOPT iterations on the predecessor run,
  no bound hits at strict tolerance (`n_at_bound_strict = 0`), no degenerate
  SEs in the diagnostic sense (`n_degenerate_se = 0`), no parameters
  exactly at their bounds.
- The post-estimation script produces the full diagnostic battery — SEs
  for 50 of 52 parameters, identification panel, fit moments by group,
  hours-bin distribution, observed/predicted wages, occupation distribution,
  marginal-utility diagnostics, parameter correlation panel.

The infrastructure is doing what it should. The estimate it produced is
not.

---

## 2. What the first M0_ruro_occ estimation currently shows

A locally indefinite optimum, catastrophic hours and participation fit,
two unidentified preference parameters, and an extreme male-female asymmetry
in the consumption-utility block that the data cannot anchor.

Headline numbers:

| metric | value |
|---|---|
| joint log-likelihood | −6,499.88 |
| ρ² (vs uniform null) | 0.708807 |
| n_parameters | 52 |
| Hessian condition number | 6.76 × 10¹⁰ |
| n negative Hessian eigenvalues | 2 |
| min eigenvalue | −26.008 |
| max eigenvalue | 1.42 × 10¹⁰ |
| negative variances from varcov | 2 |
| n parameters with NA SE | 2 (`beta_c_sf`, `theta_c_sf`) |
| % parameters with |t| < 1 | 17.3% |
| min chosen-alt probability | 1.56 × 10⁻⁸ |
| predicted participation (all four groups) | ≈ 1.000 |
| predicted mean hours, couples male | 58.6 vs observed 41.6 |
| predicted mean hours, couples female | 58.1 vs observed 35.6 |
| L1 distance, hours-bin shares, cou_f | 1.66 (out of 2.00 max) |
| L1 distance, hours-bin shares, cou_m | 1.41 |

The McFadden ρ² of 0.71 is the only "good" headline number, and it is
misleading here for reasons developed in §6.

---

## 3. Positive signs

These are the things that should not be re-debugged in the next pass.

- The model and pipeline can run end-to-end through M0 on the rebuilt data
  in ~5 min wall time. Nothing in the pipeline blew up.
- The implementation contract is being honoured by the run: occupation
  appears in `O^Occ` only, never in utility; the four R reference proposal
  aliases are read and used; the log-normal Jacobian for `O^W` is present;
  market centering is on.
- The Mincer wage block is mostly clean. `β_w_educH = 0.306` (t = 20),
  `β_w_pexp = 0.0174` (t = 7.8), `β_w_pexp² = −2.06e−04` (t = −4.2),
  `σ = 0.423` (t = 103). These are the right signs and broadly plausible
  magnitudes; predicted log-wage σ at 0.42 sits next to observed log-wage σ
  of 0.44–0.45 across groups. The Mincer intercept is identified.
- Occupation opportunity coefficients are mostly significant, signs are
  interpretable (negative `β_occ_2` and `β_occ_3` for males, positive
  `β_occ_4` everywhere), and the gender × routine-cognitive contrast
  matches what `loc4` is meant to capture (`β_occ_4_cf = 1.15`,
  `β_occ_2_cf = 0.21`, but `β_occ_2_cm = −1.47`).
- Marginal utility diagnostics are clean: zero negative MUC and zero
  negative MUL across all four groups; both Box-Cox specifications return
  positive, diminishing MU on chosen alternatives.
- The structural elasticity heuristics fall in a defensible range
  (compensated ≈ 1.7, extensive ≈ 0.5, intensive ≈ 1.2 for all four groups).
  These are not policy elasticities but they are not pathological.
- No bound hits at strict tolerance. Near-bound parameters (`σ`,
  `β_c_sf`, `β_c_sm`) are within 5% of the lower bound but not pinned.

These are real positives. None of them rescue the run.

---

## 4. Red flags

In rough order of severity for the JMP.

1. **Two preference parameters have no standard error.** `β_c_sf` and
   `θ_c_sf` come back with `NA` SE, `NA` t, `NA` p. This is not "small SE",
   it is "the inverse Hessian block for this pair is non-PSD". Their
   reported parameter correlation is **−1.035** — a correlation magnitude
   above 1 is mathematically impossible for a valid covariance matrix and
   is the direct fingerprint of the two negative variances reported in
   `varcov`. The female-singles consumption block is unidentified at the
   current optimum.
2. **The Hessian is not at a local maximum.** Two negative eigenvalues
   (min eigenvalue −26.0). The model contract §22 of
   `RURO_model_spec_contract_v4_ruro_occ.md` lists "no negative Hessian
   eigenvalues" as a hard gate before any welfare/decomposition use. That
   gate is failed.
3. **Predicted participation is essentially 100% for every group**
   (sm = 1.0000, sf = 1.0000, cou_m = 1.0000, cou_f = 1.0000) against
   observed ≈ 0.93–0.97. Non-participation is mechanically excluded. For
   an opportunity-decomposition paper, this is fatal: the extensive margin
   is exactly where opportunity differences are supposed to show up. The
   model cannot currently reproduce non-employment at all.
4. **Hours predictions are systematically too high and too clustered.**
   For couples, the predicted mass collapses onto 41–60+ bins; for
   singles, it collapses onto the 21–30 and 31–40 bins with zero mass
   below or above. Predicted mean hours for couples is 58 against observed
   42 (male) / 36 (female). The hours-opportunity layer is over-fitting
   focal points in a degenerate way.
5. **An extreme male-female asymmetry in the consumption-utility block.**
   `β_c_sm = 0.72`, `β_c_sf = 0.46`, but the shared couple
   `β_c = 5.26`. `θ_c` is also discontinuous across the partition:
   `θ_c_sm = −0.86`, `θ_c_sf = −1.09`, `θ_c (couples) = 0.215`. The
   couples-vs-singles consumption scale differs by an order of magnitude.
   This is the kind of artefact one expects when the female-singles block
   is partly absorbing what should be opportunity variation.
6. **Some chosen alternatives are being assigned essentially zero
   probability.** `p_chosen_min = 1.56e-08`, `p_chosen_q10 = 0.013`. The
   ten worst-fit households contribute `ll_i ≈ −15` to −18 each. A model
   that confidently rejects a household's actual choice is a model with
   unmodelled heterogeneity at that household — typically a sign of
   feasible-set misspecification, which is exactly the layer at issue here.
7. **Extreme parameter correlations across the consumption block.**
   `corr(β_c_sf, θ_c_sf) = −1.035` (impossible if PSD),
   `corr(β_c_sm, θ_c_sm) = 0.988`, `corr(β_c, θ_c) = 0.935`,
   `corr(β_c_sm, β_c) = −0.918`, `corr(θ_c_sm, β_c) = −0.916`. These four
   pairs together say the consumption block is one-dimensional after
   partial identification of `θ`. Standard `(β_c, θ_c)` correlation near 1
   in Box-Cox utility is a known curse, but the singles-vs-couples
   correlations are diagnostic of a different problem: the joint estimator
   cannot separate consumption preferences across the partition.
8. **Leisure intercept vs. education leisure shifter correlations near 1.**
   `corr(β_l0_sf, β_l_educH_sf) = 0.996`,
   `corr(β_l0_f, β_l_educH_f) = 0.979`,
   `corr(β_l0_sm, β_l_educH_sm) = 0.971`. With only one
   binary educH dummy at this stage, this is partly mechanical — but at
   correlations this high, the run is functionally estimating
   `β_l0 + β_l_educH × 1{educH=1}` as a single linear combination.

The ρ² number is large because the prior already does most of the work.
`ll_null_prior_corrected = −22,321.6` vs `ll = −6499.88` looks like a huge
improvement, but a substantial part of that gap is the proposal absorbing
the chosen alternative's structural component. The relevant comparison for
identifying *behaviour* is not ρ² against a uniform-over-alternatives null;
it is whether `O^E + O^H + O^W + O^Occ + U` improves predicted moments
over the prior. On participation and hours, it does not.

---

## 5. Optimizer concerns

CONOPT terminates with `OptimalLocal` and `NormalCompletion` and reports no
bound hits — but the optimum it reached is locally indefinite (§7), so
"optimal" should be read as "stationary first-order conditions to the
solver's tolerance", not as "credible interior maximum".

- The predecessor run converged in 29 iterations with no gradient norm
  reported (CONOPT does not emit one in the run JSON used by the
  diagnostics script; absence of this field is a logging gap, not a
  failure).
- The re-run logged in the uploaded summary does 1 iteration because it
  was warm-started at the predecessor theta. This is **not** a separate
  optimization failure; it is the post-estimation script's normal
  behaviour. It does mean the "Initial → Final Movement" table in the
  uploaded report is not informative for the underlying run.
- The convergence I have evidence for is single-start, single-solver,
  no perturbation, no seed-stability check, no cross-engine consistency
  check. The model contract requires (i) at least two alternative draw
  seeds with max-diff < 5% on key parameters, and (ii) `joint_ll`
  agreement between the GAMSPy vectorized path and the NumPy/SciPy path
  within `1e−6` per observation at the converged θ. Neither has been
  performed. The current optimum is therefore not known to be a unique
  local maximum.
- Multistart from at least three distinct initial vectors (spec default,
  small random perturbation of current, large random) is required before
  this θ can be claimed as the M0 maximum.

---

## 6. Fit concerns

This is the dominant problem after §7.

- **Participation.** Predicted ≈ 1.00 vs observed 0.93–0.97 across all
  four groups. The extensive margin is broken. For an
  opportunity-decomposition paper this is not a calibration nuisance, it
  is a structural failure: `β_E` is identified off the participation
  margin, and a model that does not produce non-participation will not
  identify `β_E` in any meaningful sense. `β_E = −2.61` (t = −8.65) does
  have a large absolute t-value, but with predicted participation pinned
  at 1.0, it is being identified by the curvature of `−log q_E` rather
  than by data on non-workers.
- **Hours, couples.** Observed couples hours are concentrated in 21–40
  (about 77% of cou_f, 73% of cou_m). The model puts about 67% of cou_f
  mass on 51–60+ and ~72% of cou_m mass on 51–60+. The model is also
  predicting cou_f works longer hours on average than cou_m — observed
  shows the reverse. The hours-opportunity focal-point parameters
  (`β_h_ft = 1.46`, `β_h_pt2 = 0.37`, `β_h_pt1 = −0.52`, base `β_E = −2.61`)
  are interacting destructively for couples.
- **Hours, singles.** Predicted mass is concentrated in two adjacent bins
  (21–30 and 31–40), zero elsewhere. Observed has visible mass at PT1, PT2,
  and 41–60+. The intensive distribution is degenerate.
- **Wage distribution.** Predicted mean wages are 1–3 EUR/h above
  observed for all four groups, and the predicted 90th percentile is
  about 8–10% high. Tolerable but not great.
- **Occupation distribution.** Acceptable. Predicted shares for the four
  `loc4` classes within group are within 5–15 percentage points of
  observed. Routine-manual is underestimated for males (sm 28.8% pred vs
  40.7% obs; cou_m 34.0% pred vs 36.0% obs), nonroutine-cognitive is
  underestimated for both genders.
- **Worst-fit households.** Ten households contribute `ll_i` between −14
  and −18, corresponding to `p_chosen ≈ 1e−6` to 1e−8 on chosen
  alternatives. These are individual cases the model is
  near-certainly-wrong about.
- **L1 distance on hours bins.** cou_f 1.66, cou_m 1.41, sf 0.80, sm
  0.53 (out of a 2.00 maximum). The singles fits are bad; the couples
  fits are nearly maximally bad.

A run that cannot reproduce the joint hours-participation distribution
cannot be used as the structural baseline of a welfare-inequality
decomposition. If `β_E` and the focal-point parameters cannot place mass
where the data places it, then the decomposition will mis-allocate
inequality between preferences and opportunities by construction.

---

## 7. Hessian and identification concerns

These are the diagnostics that decide whether the optimum can be trusted
at all, irrespective of fit.

- Condition number κ = 6.76 × 10¹⁰. The model contract hard gate is
  κ < 10⁷. Failed by three orders of magnitude.
- Two negative eigenvalues (min eigenvalue −26.0). The hard gate is
  zero. Failed. A negative eigenvalue means there is a direction in
  parameter space in which the log-likelihood is *locally lower* than at
  this θ — i.e., this is not a local maximum of the likelihood, it is at
  best a saddle.
- Two negative diagonal entries in the covariance matrix
  (`negative_variances_from_varcov = 2`). The named SE-less parameters are
  `β_c_sf` and `θ_c_sf`.
- The reported correlation `corr(β_c_sf, θ_c_sf) = −1.035` confirms the
  varcov is non-PSD. A valid covariance matrix has all
  correlations in [−1, 1] up to floating-point error.
- Three other pairs sit at correlations |ρ| > 0.97 (the female-leisure
  intercept × educH pair across all four leisure groups). These can be
  alleviated by data variation or by re-parameterization, but at this
  level they signal that several `(β_l0, β_l_educH)` pairs are estimated
  as a single linear combination.
- The female-singles consumption block is the proximate
  identification problem. The likely root causes, ranked:
  - The female-singles sample (n_hh = 910) is small, and within it the
    chosen-alt distribution of consumption may not span enough variation
    in transformed consumption to identify `β_c_sf` and `θ_c_sf`
    separately. Box-Cox `(β, θ)` are known to be weakly identified when
    the support of the transformed argument is narrow.
  - `θ_c_sf` is at −1.09, which makes BC(C, θ) very curved. At this
    curvature, `β_c_sf · BC(C, θ_c_sf)` is approximately a constant on
    most of the chosen-alt domain, and the level is absorbed by the
    leisure block.
- Until §7 is fixed, **no standard error in this run can be taken
  literally**. Reported SEs for the other 50 parameters are derived from
  the same non-PSD inverse Hessian. The most defensible reading is that
  for those parameters the SE direction was orthogonal to the indefinite
  block, but verifying this requires re-computing standard errors on the
  positive-semidefinite projection of the Hessian, or equivalently using
  the BHHH/sandwich form.

---

## 8. Whether this can be used as the baseline yet

No. This run is **diagnostic only**.

Concretely, what it can and cannot support right now.

| Use case | Status |
|---|---|
| Confirm the M0_ruro_occ pipeline runs end-to-end on rebuilt data | Yes |
| Confirm the spec matches the model contract on paper | Yes |
| Provide initial values for the next M0 estimation pass | Yes |
| Surface identification problems for triage (i.e., this memo) | Yes |
| Prototype-usable baseline for an internal results table | **No** |
| Welfare / money-metric well-being computation | **No** |
| Inequality decomposition into opportunity vs preference | **No** |
| Robustness ladder M1 / M2 / M3 / M4 / M6 | **No** |
| External presentation, slides, or supervisor figures of point
  estimates | **No** |
| Publishable in any form | **No** |

The hard gates failed: negative Hessian eigenvalues; κ > 10⁷ by 3.8
orders of magnitude; two parameters with no finite SE; no seed-stability
check; no cross-engine consistency check; recovery test not yet run.
Welfare cannot be computed off an indefinite Hessian — even if one were
willing to overlook §7 on identification, the participation fit alone
prevents a credible opportunity / preference decomposition (§6).

---

## 9. What must be checked before re-estimation

These are pre-conditions for the *next* run, not the run after that.

1. **Verify the female-singles consumption variation in chosen alternatives.**
   Compute the support, mean, and standard deviation of
   `BC(C/c_scale, θ_c_sf)` over chosen alternatives for `sf` only.
   If standard deviation is small relative to the mean (say < 0.1 of mean
   in absolute terms), `β_c_sf` and `θ_c_sf` cannot be jointly identified
   from these chosen alternatives, and a re-parameterization is required.
2. **Inspect the within-household consumption variation** across the 100
   sampled alternatives for `sf`. The MNL likelihood identifies utility
   shape from variation *within* household choice sets. If alternatives
   within an sf household have nearly identical consumption (because EUROMOD
   transfers smooth out the wage × hours variation), `β_c_sf` is identified
   off a near-flat axis. Plot mean within-household range and variance of
   `BC(C)` for `sf`.
3. **Re-check whether the female-singles leisure block can absorb female
   consumption identification.** Compute the partial correlation of
   `BC(L)` and `BC(C)` within the sf chosen-alt panel. High partial
   correlation here means the leisure block is doing the consumption
   block's job — which is exactly what the `(β_l0_sf, β_l_educH_sf)`
   correlation of 0.996 already hints at.
4. **Sanity-check the predicted-participation = 1 result.** Compute, by
   hand, `P(working) = Σ_{j: working_j=1} exp(V_ij) / Σ_j exp(V_ij)` for
   a small number of households at the converged θ. If `V_{i,j=non-work}`
   is being driven to −∞ by something other than `β_E`, that is a sign
   that the non-work alternative's prior `q` or the consumption side is
   misspecified at zero hours.
5. **Cross-engine LL consistency check** at the converged θ between
   `gamspy_estimation_vectorized.py` and `estimation_engine.py` (or
   `gamspy_estimation.py`). Hard gate: agreement within `1e−6` per
   observation. If this fails, one engine has a coding bug and the run is
   not credible regardless of fit or Hessian.
6. **Numerical Hessian check.** Re-compute the Hessian at the converged θ
   using the post-estimation script's numerical SE path (the
   `--compute-se` flag) instead of, or alongside, whatever GAMSPy
   returned. Compare condition number, eigenvalues, and the two negative
   variances. If both methods agree on the indefinite block, the problem
   is structural identification, not numerical noise.
7. **Confirm the consumption scaling.** The post-estimation report says
   `C where MUC=1` is 0.84 for sm, 0.69 for sf, but 8.30 for couples.
   The unit jump between singles and couples is a tell. Verify that
   `c_scale` is the same — or correctly different — across the singles
   and couples blocks. The 10× couples scale may explain the order-of-
   magnitude jump in `β_c` between partitions.
8. **Check whether `β_E = −2.61` is too negative on the prior scale.**
   `O^E + O^H` at the predicted hours peaks reaches values that, combined
   with the wage and occupation opportunity components, deliver
   `exp(V_working) >> exp(V_nonwork)` for every household. If the prior
   `q_E` is already heavily weighted toward working alternatives, the
   structural `β_E` may be over-shifted toward non-work merely to keep
   the prior-corrected probability balanced — and the post-estimation
   summary will still mark `β_E` significant because of curvature, not
   because of data.
9. **Recompute correlations on the regularized inverse Hessian.** Project
   the Hessian onto its positive-semidefinite cone (eigenvalue truncation
   at zero), invert, and recompute SEs and correlations. This is not a
   fix for identification but it produces *interpretable* SEs for the 50
   identified parameters, separating them from the two pathological ones.

If any of items 1–4 reveal the underlying problem, items 5–9 may be
unnecessary. Run them in order.

---

## 10. Recommended next technical actions

In priority order, with the tool to use stated explicitly. Save outputs
under the existing versioned-file convention.

**A. Build identification diagnostic memo (Claude Code or Codex).**

- Tool: Claude Code (preferred — direct access to the parquet files).
- Inputs: `fr_2016_RURO_mnl__singles.parquet`,
  `fr_2016_RURO_mnl__couples.parquet`, the converged
  `estimation_results.json`.
- Task: produce the diagnostic numbers requested in §9 items 1–4 and 7.
  In particular, compute and report: within-household variance and range
  of `BC(C, θ_c_sf)` and `BC(L, θ_l_sf)` for `sf`; partial corr(BC(C),
  BC(L)) | (X) within sf chosen-alt panel; `P(working)` distribution
  across households at the converged θ; the consumption-scale value used
  for singles vs couples; the empirical fraction of working observations
  by group.
- Save as: `RURO_ruro_occ_M0_identification_diag_v1.md` in `Results/`.
- Next: read this memo *before* re-estimating. If it confirms that
  `β_c_sf`, `θ_c_sf` are unidentified by data, drop one of them in the
  next spec (most defensibly: fix `θ_c_sf = θ_c_sm` or pool consumption
  curvature across singles).

**B. Cross-engine consistency check (Claude Code).**

- Tool: Claude Code.
- Task: at converged θ, evaluate `joint_ll` and per-group LL on both
  `gamspy_estimation_vectorized` and either `gamspy_estimation` or
  `estimation_engine`. Report differences in per-observation log-
  likelihood. The hard gate is `1e−6` per observation.
- Save as: `RURO_ruro_occ_M0_cross_engine_check_v1.md` in `Results/`.

**C. Recompute SEs on regularized Hessian (Claude Code).**

- Tool: Claude Code.
- Task: take the Hessian from `estimation_results.json`, replace negative
  eigenvalues with `1e−10`, invert, recompute SEs and correlations. The
  goal is not to defend these SEs as valid — they are not — but to
  separate the 2 pathological parameters from the rest, so the next
  re-spec is informed.
- Save as: `RURO_ruro_occ_M0_se_repair_v1.md` in `Results/`.

**D. Plan the M0a re-spec (Claude project chat).**

- Tool: this chat.
- Inputs: outputs of A, B, C.
- Task: decide between (a) pooling `θ_c` across singles, (b) fixing
  `θ_c_sf = θ_c_sm`, (c) restricting `β_c_sf` to a tight band around
  `β_c_sm`, or (d) re-parameterizing the singles consumption block in
  level-then-curvature form. Decide also whether to soften `β_E` bounds,
  whether the focal-point parameters in `O^H` need a different
  parameterization (the part-time / full-time dummies are evidently
  pushing too hard), and whether to drop the leisure-education interaction
  shifter at this step.
- Save as: `RURO_ruro_occ_M0a_respec_plan_v1.md`.

**E. Run M0a (Claude Code, then the existing PowerShell command in
`docs/France_case/RURO_ruro_occ_baseline_implementation_report_v1.md`).**

- Tool: Claude Code to update the YAML; the existing
  `enh_RURO_estimate_FR.py` command to run it.
- Important: do **not** warm-start M0a from the M0 results. The M0
  optimum is on the wrong side of an indefinite Hessian. Use spec
  defaults — or better, a small perturbation of the spec defaults — and
  re-run with at least three start points.
- Save run folder following existing convention. Add the post-estimation
  Markdown summary to `reports/`. Save a follow-up triage as
  `RURO_ruro_occ_M0a_triage_memo_v1.md`.

**F. Postpone until M0a passes the hard gates.**

- The recovery test (§23 of model contract).
- Seed-stability check (§22 item 9).
- Welfare computation in any form.
- Climbing the M1–M6 ladder.
- Slides, supervisor figures, abstract updates touching point estimates.

The principle behind the ordering: the data side is fixed; the spec side
is the problem. Re-estimating before diagnosing the indefinite block
would just re-discover the same indefinite block from a different start.
The next 1–2 days should produce the diagnostic memos A/B/C, then
re-spec, then re-run.

---

## Suggested filename

Save this memo as: `RURO_ruro_occ_M0_triage_memo_v1.md`
(category: technical memo / estimation triage).
