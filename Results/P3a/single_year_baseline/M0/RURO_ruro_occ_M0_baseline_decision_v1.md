# RURO `ruro_occ_M0` — Baseline-Decision Memo v1

Date: 2026-05-13

Scope: decide whether `ruro_occ_M0` (France 2016, joint singles+couples,
`estimation_spec_ruro_occ_M0.yaml`, completed run
`run_2026-05-13_15-02-16`, joint LL = −6,499.88) is credible enough to
serve as the empirical baseline for the JMP, and whether welfare
computation may proceed from it.

Evidence available for this evaluation: the MNL validation report
(2026-05-13, PASS), the low-token LLM post-estimation summary
(2026-05-13_150938), the v4 model-specification contract, the
`estimation_spec_ruro_occ_M0.yaml`, the naming-policy memo, and the
prior triage memo (`RURO_ruro_occ_M0_triage_memo_v1.md`). No new
estimation has been run since the triage; the substantive object of
this evaluation is therefore the same run as last time.

---

## 1. Verdict

`ruro_occ_M0` **fails the hard gates** for an empirical baseline as
specified in §22 of the v4 model contract. The data pipeline is sound,
the spec on paper is correct, the optimizer converged in 29 iterations
— but the optimum is locally indefinite, two preference parameters are
unidentified (no finite SE), the within-sample fit is catastrophic on
participation and hours, and none of the required identification or
stability cross-checks (recovery, seed stability, cross-engine) have
been performed. Welfare computation off this estimate would not be
interpretable.

The right move is not to run more diagnostics on this θ. It is to
simplify the spec in the female-singles consumption block, re-examine
why the model is predicting 100% participation everywhere, and only
then re-estimate. The next baseline is `M0a`, not a touched-up `M0`.

---

## 2. What works

The data side of the pipeline is in good shape and should not be
re-debugged in the next iteration.

The MNL validation report records all eight check categories as PASS on
the rebuilt 2026-05-13 parquet files. `loc4` varies within household
with median = 4.0 distinct values across working alternatives for all
three groups, `is_chosen` sums to exactly 1 per household, all 100
alternatives per household are present, all required RURO
proposal aliases (`log_q_E`, `log_q_H`, `log_q_W`, `log_q_Occ`, and
partner-suffixed analogues) are present and consistent, the per-layer
prior reconstruction is exact (`max | log_prior − Σ_layers | = 0` on
every row), `prior > 0` everywhere, and all M0-forbidden columns
(`lindi`, `industry`, `nace`, `job_id`, `type_id`, `log_q_job`,
`log_q_total`, `log_q_state`) are absent from both parquets.

The YAML spec parses cleanly as `model_family: regular` with a
dedicated `occupation_opportunity` block on `loc4` (reference 1), the
Mincer wage block with log-normal Jacobian, base `β_E · working`, and
the exclusion restrictions enforced by the parser. Metadata recorded in
the run output is correct: `prior_correction_applied = 1`,
`prior_correction_form = "-log(prior)"`, `market_centering_applied =
1`.

The solver runs end-to-end through the joint MNL likelihood in about
five minutes wall time and converges to `ModelStatus.OptimalLocal` /
`SolveStatus.NormalCompletion` on all three result blocks (`sm`, `sf`,
`couples`). No bound hits at strict tolerance. The full post-estimation
diagnostic battery now produces SEs, hours-bin distributions, occupation
shares, marginal utility diagnostics, parameter correlations, and a
parsable identification panel.

Nothing in the infrastructure is preventing a credible baseline.
Everything that's wrong is in the estimate itself.

---

## 3. What fails or remains weak

Four failures, in order of severity for a JMP baseline.

(a) **The Hessian is locally indefinite.** Condition number κ = 6.76 ×
10¹⁰ (hard gate is < 10⁷; failed by 3.8 orders of magnitude), two
negative eigenvalues with minimum eigenvalue −26.0, two negative
diagonal entries of the inverse-Hessian covariance matrix, and a
reported correlation of −1.035 between `β_c_sf` and `θ_c_sf` — a
correlation magnitude above 1 is mathematically impossible for any
valid covariance matrix, so the implied variance estimates are not
trustworthy as a system. The point estimate is not a local maximum of
the likelihood: there is a direction in parameter space along which the
log-likelihood is locally lower. The §22 hard gate (B2 in the v4
baseline spec) is failed.

(b) **Two preference parameters have no finite SE.** `β_c_sf` and
`θ_c_sf` return NA SE, NA t, NA p in the parameter table. This is the
direct fingerprint of the negative variances and is the
female-singles consumption block being unidentified at the current θ.
Gate B3 (all M0 parameters finite SEs) failed.

(c) **Catastrophic within-sample fit on participation and hours.**
Predicted participation is approximately 1.0000 for every group (sm,
sf, cou_m, cou_f), against observed 0.93–0.97. Non-participation is
mechanically excluded from the predicted distribution. Predicted
couples hours mean is 58.6 (male) and 58.1 (female) against observed
41.6 and 35.6 — the model is also predicting females in couples work
longer hours than males, the opposite of the observed pattern. L1
distance between observed and predicted hours-bin shares is 1.66 out
of a maximum of 2.0 for cou_f and 1.41 for cou_m. The hours
distribution is essentially being shifted onto the 41–60+ bins with
near-zero mass below and the part-time bins are empty in the
prediction. The minimum chosen-alternative probability is 1.56 × 10⁻⁸,
i.e. the model is confidently rejecting the actual choice for some
households.

(d) **No identification cross-checks performed.** Cross-engine
consistency between `gamspy_estimation_vectorized` and
`estimation_engine` at converged θ within 1e-6 per observation: not
done (gate B6 untested). Seed-stability re-estimation with two
alternative draw seeds and max-diff < 5%: not done (gate B5 untested).
Recovery test on synthetic data, R ≥ 50: not done (Gate C untested).

Items (a) and (b) are blocking. Items (c) and (d) are blocking
additionally for any welfare or decomposition claim.

---

## 4. Preference-estimation credibility

Mixed, with one block effectively broken.

Couples consumption and leisure preferences look reasonable in
isolation: `β_c = 5.26` (t = 11.4), `θ_c = 0.215` (t = 2.9 in absolute
value, p = 0.004), `β_l0_f = 5.70` (t = 47), `β_l0_m = 2.70` (t = 6.4),
`θ_l_f = −0.70`, `θ_l_m = −0.73` (both highly significant). Box-Cox MU
diagnostics report MUC and MUL positive and diminishing on all chosen
alternatives in all four groups, with zero negative MUC/MUL counts.

Singles consumption preferences are not credible at this θ. `β_c_sm =
0.72` and `β_c_sf = 0.46` are an order of magnitude smaller than the
couples `β_c = 5.26`. `θ_c_sm = −0.86` and `θ_c_sf = −1.09` deliver
strong consumption curvature; `θ_c (couples) = 0.215` does not. The
consumption scale where MUC = 1 is 0.84 for sm, 0.69 for sf, but 8.30
for couples — an order of magnitude jump across the singles/couples
partition that is unlikely to be substantive. Whether this is a
`c_scale` mismatch between the singles and couples blocks (one of the
items to check in §9 of the prior triage memo) or a genuine
identification break in the singles block, it is not safe to interpret
these point estimates.

Leisure shifters: `β_l_age_f`, `β_l_age2_f` are significant for
females in couples; `β_l_educH` is large and negative across all four
groups, consistent with high-education individuals taking less leisure;
`β_l_nkids` is not significant in either female block, which is
unusual and probably driven by the participation overfit (a model that
predicts 100% participation has no leverage on the children-leisure
interaction). The leisure-intercept × education-leisure correlation is
≥ 0.97 for every group, signalling that `β_l0_g` and `β_l_educH_g` are
identified as a single linear combination at this stage.

The preference-side bottom line: couples preferences could plausibly
be reported as preliminary; singles preferences cannot.

---

## 5. Opportunity-estimation credibility

The hours / employment opportunity block is **misbehaving badly**.

`β_E = −2.61` (t = −8.7), `β_h_pt1 = −0.52` (t = −4.8), `β_h_pt2 =
0.37` (t = 3.4), `β_h_ft = 1.46` (t = 29.3). On paper the focal-point
hierarchy looks right (FT > PT2 > 0 > PT1). The diagnostic problem is
that the *predicted* hours distribution sits almost entirely on the
41–60+ bins, with zero mass on the part-time bands the focal-point
parameters were supposed to capture. The combined value of
`O^E + O^H` on a working alternative at FT hours is large and
positive; on a PT1 alternative it is small and slightly negative; on
non-work it is `β_E + β_E_gsur · gsur + β_E_educH · educH`. With
`β_E` at −2.61 the implied non-work log-odds is large and negative
*before* adding the prior correction, but the prior correction
mechanically pushes mass back onto the non-work alternative — and yet
the predicted participation rate is still 1.000 for every group. This
combination strongly suggests one of three things:

- A sign-convention issue on `working` vs `1−working` somewhere in the
  hours-opportunity evaluation, so that `β_E · working` is functioning
  as `+β_E` on non-work and `−β_E` on work, the opposite of intent.
- A double-counted prior correction on non-work alternatives.
- A scaling issue between `O^E` and the leisure block such that the
  consumption + leisure contribution at non-work is dominated by a
  small but positive `BC(L_max, θ_l)` term that more than compensates
  for the participation log-odds.

I cannot distinguish these from the LLM summary alone. A targeted
diagnostic — printing `V_work, V_nonwork, P(work)` for a handful of
households at the converged θ — would localise the issue in an hour
of Claude Code work.

The wage block is fine. `β_w_educH = 0.31` (t = 20), `β_w_pexp = 0.017`
(t = 7.8), `β_w_pexp² = −2.1 × 10⁻⁴` (t = −4.2), `σ = 0.423` (t =
103). Predicted wage σ at 0.42 matches observed log-wage σ of 0.43–
0.45 across groups within rounding error. The wage block, including
the `−log w` Jacobian, is the most credible piece of the run. The
`gsur` market shifter `β_E_gsur = −0.77` is significant and has the
expected sign (higher local unemployment → lower employment
opportunity). `β_E_educH = 0.26` is small and only marginally
significant (p = 0.29), which is unusual given the structural role of
education in market access; it is probably also being affected by the
participation overfit.

The opportunity-side bottom line: wage opportunity is publishable in
principle, hours/employment opportunity is not interpretable yet.

---

## 6. Occupation-opportunity credibility

Mixed but the most defensible block in the run.

Twelve `β_occ_k_g` parameters, of which 9 are significant at p < 0.05
and 8 at p < 0.001. Signs are interpretable: nonroutine-cognitive
(`loc4 = 4`) is the high-opportunity category for all four groups
(`β_occ_4_cf = 1.15`, `β_occ_4_cm = 0.49`, `β_occ_4_sf = 0.79`,
`β_occ_4_sm = 0.02`). The routine-manual reference (`loc4 = 1`) is
relatively favourable for males (`β_occ_2_cm = −1.47`, `β_occ_3_cm =
−2.21`) and roughly neutral for females (`β_occ_2_cf = 0.21`,
`β_occ_3_cf = −0.19`). The male reference-category dominance and the
gendered routine-cognitive vs nonroutine-cognitive contrast match
what `loc4` is designed to capture in labour-market segmentation.

Observed-vs-predicted occupation shares are within 5–15 percentage
points across groups: predicted under-weights routine-manual for males
(sm: 28.8% pred vs 40.7% obs; cou_m: 34.0% vs 36.0%) and under-weights
nonroutine-cognitive for both genders. These misses are tolerable for
a first M0 result and would normally be the easiest opportunity layer
to interpret.

The caveat is that the occupation block does not stand independently
of the hours/participation pathology. Predicted occupation shares are
weighted by predicted choice probabilities, and choice probabilities
on non-work are mechanically zero. The occupation predictions
therefore mix structural occupation opportunity with the
participation overfit. Until participation predicts non-zero
non-employment, the `β_occ_k_g` estimates cannot be cleanly read as
"occupation opportunity holding labour supply fixed".

The occupation-side bottom line: it works in the sense the contract
intended, but it inherits the contamination from §5.

---

## 7. Prior / proposal-correction credibility

Mechanically clean. Conceptually still has one open question.

Mechanics: the MNL validation report records `(prior > 0).all()` on
both files (min prior 7.82 × 10⁻⁶ singles, 6.29 × 10⁻¹¹ couples),
`max | log(prior) − log_prior | = 0` exactly on every row, per-layer
reconstruction `log_prior = log_q_E + working · (log_q_H + log_q_W +
log_q_Occ)` exact, `log_q_Occ = 0` on all non-work rows, all four
proposal aliases present and consistent. The run metadata confirms
`prior_correction_applied = 1`, `prior_correction_form = "-log(prior)"`,
and the post-estimation report finds no missing aliases and no
forbidden diagnostic columns. The single-subtraction property
(`exactly one −log(prior) term per alternative`, contract §13) is
honoured.

The couples-side minimum prior (6.29 × 10⁻¹¹) is small but
mathematically fine — it is the product of two singles-side priors
(one per partner) and the smaller value reflects compounded
proposal-density mass for partner-specific draws. The validation
report does not flag it.

Open conceptual question: the `−log q` term is doing a lot of work in
the ρ²-vs-uniform-null statistic. `ll_null_uniform = −19,585.8`,
`ll_null_prior_corrected = −22,321.6`, `ll = −6,499.88`. The prior
itself accounts for roughly 13,000 nats of log-likelihood gap, and
the structural model (`U + O^E + O^H + O^W + O^Occ`) accounts for the
remaining ~15,800 nats above the prior-corrected null. The ρ² = 0.71
headline number reads "great fit", but it is computed against the
uniform null and overstates how much the structural index is doing
relative to the proposal. The right benchmarks for paper claims are
the prior-corrected ρ² (`= 0.7088`, identical to the uniform-null
number in the report; this is suspicious and warrants checking that
the two null-likelihood values are being computed correctly) and the
moment-level fit, not the absolute LL.

The proposal-correction side is the cleanest block of the run.

---

## 8. Identification concerns

The §22 hard gates of the v4 contract are listed below with each
gate's status.

| Gate | Required | Status |
|---|---|---|
| B1 | Optimizer converges with status "optimal" / "locally optimal" | PASS |
| B2 | Hessian has no negative eigenvalues; κ < 10⁷; smallest \|eig\| > 10⁻⁸ | **FAIL** (2 negative eigenvalues; κ = 6.76 × 10¹⁰; min eig = −26.0) |
| B3 | All M0 parameters return finite SEs | **FAIL** (`β_c_sf`, `θ_c_sf` NA) |
| B4 | No substantive parameter within 10⁻³ of a bound | PASS (`σ`, `β_c_sf`, `β_c_sm` near-bound at 5% but not pinned) |
| B5 | Seed-stability max-diff < 5% on `β_c`, `θ_c`, `β_l0_g`, `θ_l_g`, `β_E_g`, `β_occ_k_g` | **UNTESTED** |
| B6 | Cross-engine `joint_ll` agreement within 10⁻⁶ per obs at converged θ | **UNTESTED** |

Two gates failed, two gates untested. The two failures are not
numerical — they are structural. The negative eigenvalues and the
non-PSD covariance are the same problem expressed twice: the
female-singles consumption block is not identified, and the implied
likelihood is locally flat (or worse, locally decreasing) in some
direction through `(β_c_sf, θ_c_sf)`.

Extreme parameter correlations in the consumption and leisure blocks
add more identification stress on top of B2/B3:

- `corr(β_c_sf, θ_c_sf) = −1.035` (impossible for valid varcov)
- `corr(β_l0_sf, β_l_educH_sf) = 0.996`
- `corr(β_c_sm, θ_c_sm) = 0.988`
- `corr(β_l0_f, β_l_educH_f) = 0.979`
- `corr(β_l0_sm, β_l_educH_sm) = 0.971`
- `corr(β_w_pexp, β_w_pexp²) = −0.961`
- `corr(β_E, β_E_gsur) = −0.947`
- `corr(β_c, θ_c) = 0.935`

The `(β_l0, β_l_educH)` cluster across all four groups is partly
mechanical (one binary educH dummy) and partly diagnostic of
genuinely weak identification at this sample size. The `(β_c_g,
θ_c_g)` cluster across all consumption pairs reflects the
well-known Box-Cox curse-of-curvature, but at correlation 0.99+ the
two parameters are not separately identified by these data without
further restriction.

The likelihood is doing something the optimizer is calling a local
maximum, but the data do not pin down `(β_c_sf, θ_c_sf)` and possibly
not `(β_c_sm, θ_c_sm)` either.

---

## 9. Whether to run recovery tests

Not yet.

The contract §23 / §16 Gate C recovery test on synthetic data — R ≥
50 Monte Carlo replications, mean bias < 10%, 95% coverage in
[0.92, 0.98] — is a major undertaking. Running it now would be the
wrong sequence:

- Recovery is designed to confirm that *if* the data were generated by
  the M0 spec at plausible `θ⁰`, the estimator would recover `θ⁰`. It
  answers the question: is the spec identified in principle on this
  sample size and proposal design.
- The current evidence already shows that on the actual data, the
  spec at the current θ is locally indefinite. Running recovery on the
  same spec is likely to surface the same `(β_c_sf, θ_c_sf)` problem
  but at additional 50× compute cost.
- Recovery is also expensive because it requires a working estimator
  for every Monte Carlo draw. With a current 5-minute wall time per
  estimation, R = 50 replications × 3 starts ≈ 12 hours minimum, more
  with realistic restarts.

The right ordering: first repair the spec so the female-singles
consumption block is identified and the participation prediction is
no longer pinned at 1.000. Re-estimate. Confirm Gate B passes on the
empirical France data. *Then* run recovery to confirm Gate C. Running
recovery on a spec that fails Gate B is wasted compute.

Cross-engine consistency (Gate B6) is the only check that should be
run on the existing θ. It is cheap (one evaluation per engine, no
optimization), and the result either confirms the two engines agree
or surfaces a coding bug. That check should be run regardless of next
steps and was item B in the prior triage.

---

## 10. Whether to proceed to welfare computation

**Not allowed, in any form, off this θ.**

The money-metric well-being calculation at the heart of the JMP
requires a credible utility function at chosen and counterfactual
consumption-leisure-occupation packages. The current θ delivers two
features that make welfare numbers off it uninterpretable:

- Female-singles consumption preferences have no standard error and
  show a correlation `corr(β_c_sf, θ_c_sf) = −1.035` — a money-metric
  evaluation on `sf` would be sensitive to which interior point of an
  identification flat is chosen.
- The leisure block at non-work is being mechanically excluded from
  the predicted distribution (predicted participation = 1.0000), which
  means the utility difference `U(work) − U(non-work)` that
  money-metric measures must traverse to compensate for opportunity
  differences is not anchored to data. Welfare differences computed
  off this θ would assign zero weight to the non-employment margin
  even though the non-employment margin is exactly where opportunity
  differences are supposed to show up in the JMP decomposition.

Even as a toy scaffold, welfare computation is risky here — a
prototype welfare number reported off this θ would invite the
question "what does this mean for inequality decomposition" and the
honest answer is "nothing yet". The cleaner play is to lock the
welfare scaffolding code on a known-good toy θ⁰ (a simulated
recovery θ, for example), so the welfare layer is ready to plug in
when M0a passes Gate B. The scaffolding can be written and tested
without committing to any France 2016 estimate.

This is the directly-asked welfare question and the answer is the
strictest of the three options the prompt offered: **not allowed**.

---

## 11. What not to claim yet

In order of how easy each is to overclaim by accident.

- **No point estimates of preference parameters for `sf`** should be
  reported anywhere outside an internal triage. The `(β_c_sf,
  θ_c_sf)` block is unidentified at this θ and any reported number
  for those two parameters is meaningless on its own. By extension,
  no "consumption-utility gender heterogeneity" claim using
  `β_c_sm / β_c_sf` is supported.
- **No claim of "preferences identified separately from
  opportunities"** is supported. The §16 hard gates explicitly list
  recovery and seed-stability as preconditions for an
  identification claim, and neither has been run.
- **No claim about the magnitude of `β_E`** as a structural
  participation log-odds is supported until the participation
  prediction stops being pinned at 1.000. The current `β_E = −2.61`
  may be a large negative number, but it is being identified off
  curvature rather than off non-employment data.
- **No claim of "the opportunity structure explains X% of
  inequality"**. That number requires welfare computation and is
  blocked by §10.
- **No occupation-opportunity claim** at the level of "routine
  occupations face systematically worse market access". The
  occupation block looks structurally right but is contaminated by
  the participation-prediction pathology.
- **No reference to ρ² = 0.71 as a baseline fit number.** The
  prior-corrected ρ² is the same 0.7088 and the model is doing badly
  on the moments — participation, hours distribution, hours mean.
- **No claim of "the baseline is set, moving on to robustness M1
  / M2"**. The baseline is not set. M0 is not Gate-B-clean.

What can be said publicly about the current state: the pipeline runs
end-to-end on the rebuilt data, the data preconditions are met, and
the first M0 estimation surfaced identification problems that require
spec refinement before downstream work.

---

## 12. Immediate next task

The simplification path is clear from the diagnostics. Tool, exact
deliverable, and saved filename for each step.

**Step 1 — fix the female-singles consumption block (Claude Code).**

Open `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml`. Pool the
consumption-curvature parameter across singles: replace `theta_c_sm`
and `theta_c_sf` with a single shared `theta_c_singles`. Keep
`beta_c_sm` and `beta_c_sf` separate, kept distinct from couples
`beta_c`. This is the smallest restriction consistent with the
identification evidence: the data identify a single curvature for
singles consumption, not two separate ones. Save the new spec as
`estimation_spec_ruro_occ_M0a.yaml`.

**Step 2 — confirm the participation-prediction pathology before
re-estimating (Claude Code).**

Compute, at the current converged θ, the per-household
`V_nonwork − max_j V_work,j` and the implied `P(non-work)` for a
sample of 100 households across all four groups. If `P(non-work)` is
mechanically zero for all of them, that confirms the structural
problem and rules out it being a post-estimation reporting artefact.
If `P(non-work)` is non-zero per the raw V-evaluations but the
reported predicted participation is 1.000 in the LLM summary, the
problem is in the post-estimation reporting code rather than the
estimator. Save as
`RURO_ruro_occ_M0_participation_check_v1.md` in `Results/`.

**Step 3 — re-estimate M0a from spec defaults (Claude Code +
`enh_RURO_estimate_FR.py`).**

Do **not** warm-start from M0. The M0 optimum is on the wrong side
of an indefinite Hessian. Use spec defaults or a small random
perturbation of them. Run from at least three start points; the
contract requires the M0 spec to converge with positive-definite
Hessian regardless of starting value, so any divergence between
starts is itself diagnostic. Save the run folder following existing
convention. Add the post-estimation low-token summary to
`reports/`. Save a follow-up triage as
`RURO_ruro_occ_M0a_triage_memo_v1.md`.

**Step 4 — once Gate B passes on M0a (Claude project chat + Claude
Code).**

Cross-engine consistency check at the M0a converged θ. Seed-stability
re-estimation with two alternative draw seeds. Save each as a
versioned memo. Only after both pass, plan recovery and welfare
scaffolding.

**Postponed:**

- Recovery test on real data.
- Welfare computation in any form.
- Climbing the M1–M6 ladder.
- Slides, supervisor figures, abstract numbers.

The principle: data preconditions are met, the spec on paper is
correct, but the spec contains one over-parameterised block that the
data cannot pin down. Simplify that block, re-estimate from a clean
start, and only then talk about whether `ruro_occ_M0a` is a baseline.

---

## Verdict label

**REJECT AND SIMPLIFY.**

`ruro_occ_M0` cannot be the JMP baseline as currently estimated. The
spec is not wrong on paper; the female-singles consumption block is
over-parameterised relative to what France 2016 can identify, and a
structural participation-prediction pathology is contaminating every
opportunity coefficient. The simplest defensible next step is
`M0a`: pool `θ_c` across singles, diagnose the participation issue,
re-estimate from spec defaults, and re-evaluate. Welfare computation
remains blocked until M0a clears Gate B.

---

## Suggested filename

Save this memo as: `RURO_ruro_occ_M0_baseline_decision_v1.md`
(category: technical memo / baseline-decision).
