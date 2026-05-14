# RURO `ruro_occ_M0a_clean` — Verdict Memo v1

Date: 2026-05-14

Scope: consolidated verdict on `ruro_occ_M0a_clean` (France 2016,
joint singles+couples, estimation run `2026-05-13_19-24-38`,
joint LL = −6,521.43, 47 parameters), after the post-estimation
reporting patch v2 (no estimator change) documented in
`docs/RURO_occ_M0a_clean_post_estimation_patch_report_v1.md`. Evidence
package: structural participation diagnostic, post-patch fit-check
JSON, post-patch low-token summary (`reports/...20260514_102334.md`),
and the RURO continuous-MNL variable dictionary.

This memo supersedes the earlier `RURO_ruro_occ_M0a_clean_baseline_decision`
draft. The newly available post-patch LLM summary contains diagnostics
that were not visible before the patch and that materially update the
verdict for couples and for the consumption block.

---

## 1. Verdict

**`ruro_occ_M0a_clean` is PROTOTYPE-USABLE FOR SINGLES ONLY. It is NOT a
JMP baseline. Welfare and decomposition remain blocked.**

In one paragraph: the post-estimation reporting patch is doing its job —
the patched reporter reproduces the structural choice index `V` to within
1e-14 on a 100-household cross-check, and singles predicted participation
now matches observed within sampling error. But the now-honest diagnostic
exposes two failures that the pre-patch bug had been hiding: (a) couples
predicted moments are extreme (mean wage 140 EUR/hr against observed 16,
mean hours 60 against observed 41, L1 hours-bin distance 1.7/2.0, worst-fit
per-household log-likelihood −46), and (b) the singles consumption block
still has a non-PSD covariance — `β_c_sm`, `β_c_sf`, and `θ_c_singles`
report NA standard errors, with multiple `|corr| > 1` pairs among
`(β_c, θ_c, β_c_sm, β_c_sf, θ_c_singles, σ)`. The proper-rename M0a-clean
removed the equality-constraint artifact but did not remove the underlying
identification gap, which is now visible because the constraint is no
longer mechanically suppressing it. M0a-clean clears one of the v4 contract
§22 hard gates (singles fit reasonable) and fails three (Gate B2 Hessian
PSD, Gate B3 finite SEs, and the implicit couples-fit gate). The model is
useful as a diagnostic and as scaffolding for M0b; it is not paper-ready.

---

## 2. What the reporting patch fixed

The patch addressed real defects in `RURO_post_estimation_styled.py` that
caused predicted participation to read 1.0000 across all four groups. The
fixes were strictly to the reporting code; the estimator, likelihood, YAML,
MNL parquets, draws, and EUROMOD logic were not touched.

Three concrete defects fixed:

(a) `compute_beta_l_full` used a name-stripping heuristic
(`beta_l_age → age`) that did not match the parquet column `age_norm`.
Singles leisure shifters silently contributed zero to `β_l(X)`.
Replaced with a spec-driven lookup that resolves each shifter via
`spec.utility_leisure_shifters`, using the YAML-declared `variable`
field. The legacy heuristic remains as a fallback with `age`,
`age2`, and `nkids` aliases added so silent zero is no longer
possible even without a spec.

(b) `_add_predicted_probabilities` reconstructed only `O^E + O^H`
(via `_compute_log_h + _compute_log_w`) and omitted
`market_opportunity` and `occupation_opportunity` entirely. A new
helper `_compute_opportunity_from_spec` was added that mirrors the
structural diagnostic and rebuilds the full opportunity index
including market and occupation contributions.

(c) The reporter applied Box-Cox to normalized `c_norm`/`l_norm`
columns while the estimator
(`gamspy_estimation_vectorized.py:347-348`) applies Box-Cox to raw
`consumption`/`leisure`. Switched the reporter to raw columns.
This alone changed the singles V-vector standard deviation from
60.5 to 7.87 on the 100-household diagnostic sample.

The strongest evidence that the patch is correct is the cross-check on
the 100-household sample (SAMPLE_SEED=17): the patched reporter's V
matches the structural participation diagnostic's V to within 1e-14.
Two independent re-implementations of the choice-index formula now
agree to floating-point precision. The reporting bug is fixed.

What the patch did NOT do (correctly): it did not re-estimate, did not
change the on-disk `estimation_results.json`, did not modify the YAML
spec, and did not touch any data file. All "what the model says"
statements below refer to the same converged θ̂ as before; only the
reporting of that θ̂ is now correct.

---

## 3. What the current diagnostics show

The post-patch evidence package contains four artefacts, and their
combined picture is the basis of this verdict.

**`_M0a_clean_post_est_fit_check.json` (patched reporter, all 4,253
households):**

| group | obs participation | pred participation | obs mean hours | pred mean hours |
|---|---|---|---|---|
| sm | 0.9295 | 0.9129 | 39.30 | 35.65 |
| sf | 0.9396 | 0.9540 | 36.30 | 35.03 |
| cou_m | 0.9717 | 1.0000 | 41.61 | 59.69 |
| cou_f | 0.9651 | 1.0000 | 35.65 | 59.58 |

**`fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260514_102334.md`
(rerun with patched reporter on same θ̂):**

- 47 estimated parameters, joint LL = −6,521.43, ρ² = 0.708.
- 31 of 47 significant at p < 0.05 (66.0%; was 35/52 at M0).
- Hessian: 1 negative eigenvalue, min = −4.47, max = 1.50e10,
  κ = 9.94e9.
- Three preference parameters return **NA standard errors**:
  `β_c_sf` (0.677), `β_c_sm` (0.748), `θ_c_singles` (−0.836).
- Worst-fit households all couples, all with `ll_i = −46.05` (per-hh
  probability ≈ 1e−20).
- `p_chosen_min` = 2.45e−155, `p_chosen_q25` = 3.52e−109. These are
  not numerical underflow — they are honest statements that the
  model assigns essentially zero probability to the actually-chosen
  alternative for a substantial fraction of couples.
- **Predicted couples wage moments are extreme**: predicted mean
  hourly wage 139.92 EUR (cou_m) and 140.14 EUR (cou_f) against
  observed 17.66 and 15.17. Predicted q90 of 166 EUR/h. This was
  not visible in the pre-patch summary, which reported 19.81 and
  18.23, because the V used for the wage aggregate then was wrong.
- Predicted hours-bin distribution for couples: 0% mass below
  hours-bin 21–30, 0.9% in 21–30 (observed 26–39%), 5.6% in 31–40
  (observed 38–47%), 43.7% in 51–60 (observed 2–6%), 31.4% in 60+
  (observed 0.5–2.5%). L1 distance 1.7/2.0 for cou_f, 1.43 for
  cou_m. Singles hours-bin L1 distance is more reasonable: 0.41
  (sf), 0.72 (sm).

**`_participation_diag_ruro_occ_M0a_clean.json` (structural V
decomposition, 100-hh sample per group):**

- Singles V_work − V_nonwork median: −10.6 (sm), −9.9 (sf).
  Implied P(non-work) median: 0.074 (sm), 0.035 (sf). Matches
  observed non-employment rates of 0.070 and 0.060 well.
- Couples V_work − V_nonwork median per partner: +82.8 (cou_m),
  +87.9 (cou_f). Implied P(non-work) ≈ 1e−38. Observed couples
  non-employment per partner: 0.028 (cou_m), 0.035 (cou_f).
- Component breakdown for couples shows the gap is dominated by
  `U` (+91.4 cou_m, +97.3 cou_f) — preference utility makes work
  enormously more attractive than non-work. `−log_prior` adds
  another +8.4. Opportunity terms net to roughly −17 partially
  offsetting.

**Correlation panel** (top high-correlation pairs):

| pair | corr |
|---|---|
| `θ_c_singles`, `β_c` | **−1.27** |
| `β_c_sm`, `β_c` | **−1.20** |
| `β_c_sf`, `β_c` | **−1.19** |
| `θ_c_singles`, `σ` | **+1.15** |
| `β_c_sm`, `σ` | **+1.10** |
| `β_c_sf`, `σ` | **+1.10** |
| `β_c_sm`, `β_c_sf` | **−1.03** |
| `β_c_sf`, `θ_c_singles` | **−1.03** |
| `β_c_sm`, `θ_c_singles` | **−1.02** |
| `β_c`, `θ_c` | +1.01 |

Ten pairs with `|corr| > 1`. All involve the consumption block.
This is the same kind of non-PSD signature as M0, just in a different
location: at M0 it was inside the singles `(β_c_sf, θ_c_sf)` pair,
at M0a-clean it spans singles consumption, couples consumption, and
the wage-block σ.

---

## 4. Singles fit

Substantially restored by the patch. Defensible for prototype use, not
yet paper-ready because the underlying consumption block is still
ill-identified (see §7).

(a) **Participation**: sm 0.913 predicted vs 0.929 observed (−1.6 pp,
within sampling error for n=766). sf 0.954 predicted vs 0.940 observed
(+1.4 pp). Both within an order of sampling noise.

(b) **Mean hours conditional on working**: sm 35.7 predicted vs 39.3
observed (−9%). sf 35.0 predicted vs 36.3 observed (−4%). Tolerable
miss; consistent with the focal-point parameterization slightly
underweighting the upper end of full-time.

(c) **Hours distribution L1 distance**: 0.72 (sm), 0.41 (sf). Out of
maximum 2.0. These are reasonable. The shape is reasonable too:
predicted mass in part-time bins is in the right ballpark, the
21–30 and 31–40 bins are slightly mis-weighted but in tolerable
proportions, the long tail above 41 hours is under-predicted.

(d) **Wage moments**: predicted mean 12.6 EUR/h (sm), 12.7 (sf) vs
observed 16.2 (sm), 15.1 (sf). The predicted distribution is shifted
left by about 25%. This is a model-fit issue (the Mincer mean
captures population-average wages, not conditional-on-chosen
wages), not a reporting bug. The implied σ at chosen = 0.42 matches
observed σ_log_wage of 0.43–0.45 within rounding.

(e) **Occupation distribution**: predicted shares within 5–25 pp of
observed for both singles groups. Routine-manual is over-predicted
for males (28% pred vs 41% obs) and under-predicted for females
(26% pred vs 19% obs); the nonroutine-cognitive category is over-
or under-predicted in opposite directions for the two genders.
Tolerable.

(f) **Structural P(non-work) per household** matches reported
participation_predicted to within sampling error — the reporter and
the structural diagnostic agree on what the model says singles do.

Bottom line for singles: the patched reporter is faithful, the fit is
defensible at the within-sample moments level, and the singles-side
occupation-opportunity coefficients (the JMP value-add) are
significant with sensible signs. The remaining concerns are
identification (§7) and the consumption-block standard errors.

---

## 5. Couples fit

Catastrophic. The model concentrates predicted probability mass on
extreme alternatives.

(a) **Participation**: 1.0000 predicted (both partners) vs 0.972
(cou_m) and 0.965 (cou_f) observed. Structural diagnostic shows
P(non-work per partner) ≈ 1e−38. The model mechanically excludes
non-employment.

(b) **Mean hours**: 59.7 (cou_m) and 59.6 (cou_f) predicted vs 41.6
and 35.6 observed. Predicted female hours exceed predicted male
hours — the opposite of observed.

(c) **Hours-bin distribution**: predicted mass is essentially all in
51–60 (44%) and 60+ (31%) for both partners. Observed mass is
concentrated in 21–30 and 31–40 (70–77%), with the 51–60 and 60+
bins together accounting for 3–8%. L1 distance is 1.70 for cou_f
and 1.43 for cou_m. The maximum possible L1 distance is 2.0; cou_f
is at 85% of maximum mismatch.

(d) **Mean wage**: 139.92 (cou_m) and 140.14 (cou_f) predicted vs
17.66 and 15.17 observed. Predicted q10 of 103–105 EUR/h is higher
than observed q90 of 22–28 EUR/h. This is the choice-probability-
weighted predicted wage; because the model concentrates probability
on the highest-wage alternatives in the choice set (the lognormal
proposal samples a wide range, and the model picks the top tail),
the conditional mean is dragged to extreme values. **This was not
visible in the pre-patch summary**, which reported 19.81 and 18.23
because the V used in the aggregation was wrong.

(e) **Occupation distribution**: predicted couples-male `loc4 = -2`
(unknown-occupation working) is 7e−64 — i.e. zero. The unknown
sentinel never gets weight in prediction because the structural V
puts massive penalties on it. Observed share is 1.2%. Routine-
cognitive (loc4=3) is over-predicted by a factor of 2–2.5; nonroutine
manual (loc4=2) over-predicted by factor 1.9.

(f) **Worst-fit households**: ten worst-fit households are all
couples, all with `ll_i = −46.05` (= log of 1e−20). For comparison,
worst-fit singles get `ll_i ≈ −18` (= log of 1.5e−8). Couples
worst-fit is twenty-eight orders of magnitude worse.

(g) **`p_chosen_q25` = 3.5e−109**. A quarter of all households (or a
quarter of couples, equivalently) have predicted probability on
their actually chosen alternative below 1e−109. The model is
confidently rejecting a quarter of the data.

Bottom line for couples: the model is not just under-fitting at the
extensive margin — it is producing economically implausible
predictions on every margin (wages 8× observed, hours 1.5× observed,
participation 1.0 vs 0.97, mass on extreme bins). The pre-patch
participation = 1.0000 was the visible tip of a much larger
specification failure.

---

## 6. Why the couples issue is structural

The structural V decomposition (Section 4 of the participation
diagnostic) pinpoints the cause. For couples, on the median household:

```
V_work − V_nonwork = U_gap + O_gap + (−log_prior_gap)
                   = +91.4 + (−17.4) + 8.4
                   = +82.4 nats (per partner)
```

The dominant term is `U` (consumption + leisure utility), not the
opportunity layer or the prior correction. The model has decided
that working maximizes household utility by an enormous margin, and
the opportunity layer is too weak to overcome that.

Three contributing specification choices, in order of likely
importance:

(a) **`θ_c (couples) = +0.319`**. This makes the couples consumption
Box-Cox `BC(C, 0.32) = (C^0.32 − 1) / 0.32` nearly linear in C over
the empirical range. With `β_c (couples) = 6.15` (large) and a
near-linear transform, a household's consumption-utility difference
between working (C ≈ 6000) and non-working (C ≈ 3000) becomes very
large. Compare to singles: `θ_c_singles = −0.836`, which makes the
singles BC strongly concave; a doubling of singles consumption
contributes a much smaller utility gain.

(b) **No leisure-leisure interaction `β_{l_m, l_f}`**. Capéau et
al. (2015/16) report a positive significant `β_{h1,h2} = 0.206`
(t = 2.7) for Belgium, meaning partner leisures are complements:
when one partner does not work, the household values the other
partner's leisure more. Without this term, the M0a-clean
specification adds male and female leisure utilities independently,
and there is no offsetting mechanism when both partners reduce
hours together. The v4 model contract lists this as M5.

(c) **No partner-status interactions on the leisure shifters**.
`β_l_nkids` is female-only and unmodified by male working status.
In couples with children, female leisure might plausibly be much
more valuable when the male partner is also at home (joint
childcare) versus when the male is working full-time. Capéau et
al. carry per-partner child-age-band shifters on each spouse's
leisure (their `ch03`, `ch36`, `ch69`). Yours has a single
`n_children` term on female leisure only.

The combination of (a) and (b) is sufficient to produce the
+91 utility gap. (a) inflates the consumption channel; (b)
removes the natural offset.

Two secondary contributors that are not the proximate cause but
amplify the problem:

(d) **The proposal samples a wide wage range (5–170 EUR/h)
uniformly within the lognormal envelope**. Combined with `θ_c`
near-linearity, alternatives in which both partners work at high
wages produce extreme household income, which produces extreme
consumption utility, which the model picks deterministically.
This is why predicted couples wages reach 140 EUR/h: not because
the model believes wages are that high, but because among the
sampled alternatives those are the ones that maximize V given the
estimated parameters.

(e) **The wage-block σ correlates with the singles consumption
block at >1**. This says σ is doing some of the work that the
singles consumption block should be doing — the data identifies a
linear combination of `(β_c_sf, β_c_sm, σ)` rather than each
separately. This is an identification residual, not a couples
problem, but it confirms that the consumption block is not in
good shape.

These are economic specification issues, not coding bugs. The
estimator and the patched reporter are doing the right thing on the
spec as written; the spec is incomplete in a way the literature has
already identified.

---

## 7. Preference-estimation credibility

Mixed and clearly weaker than the pre-patch summary suggested.

(a) **Singles consumption block is no longer credibly identified**.
`β_c_sm = 0.748` (NA SE), `β_c_sf = 0.677` (NA SE), `θ_c_singles =
−0.836` (NA SE). Three NA SEs in the consumption block after the
proper rename. The pre-patch summary reported finite SEs for these
parameters; that was an artefact of the equality-constraint
suppressing the post-estimation Hessian computation along the
constrained direction. With the proper rename, the diagnostic
honestly reports that the singles consumption block is jointly
unidentified at the current θ̂, even though three separately
significant point estimates are reported.

(b) **Multiple non-PSD correlation pairs** in the consumption-σ
block. Listed in §3. Ten pairs with `|corr| > 1`, all touching
either `β_c`, `θ_c`, `β_c_sm`, `β_c_sf`, `θ_c_singles`, or `σ`.
The covariance matrix is not positive semi-definite, which means
the parameters span an identification-flat subspace and reported
standard errors elsewhere should be read with caution too.

(c) **Couples preferences look identified in isolation**: `β_c =
6.15` (SE 0.50), `θ_c = +0.32` (SE 0.08), `β_l0_f = 4.84` (SE
0.70), `β_l0_m = 2.33` (SE 0.35), `θ_l_f = −0.70` (SE 0.09), `θ_l_m
= −0.74` (SE 0.12). All highly significant. But the couples
parameters are precisely the ones driving the couples-fit
pathology, so individual significance does not imply correctness.

(d) **Leisure shifters are mostly insignificant**: `β_l_age` (4
versions, 1 significant), `β_l_age2` (4 versions, 0 significant),
`β_l_nkids` (2 versions, 0 significant). 7 of 47 parameters have
|t| < 1. These are individually defensible as small-effect
parameters but their imprecision in this run is not surprising
given the overall identification issues.

(e) **MUC and MUL diagnostics clean**: zero negative marginal
utility of consumption or leisure across all groups; both MUC and
MUL are positive and diminishing on chosen alternatives. This is
the one preference diagnostic that is genuinely clean.

Bottom line for preferences: couples preferences look estimated but
are over-fitting the participation margin; singles preferences are
near-credible at point estimates but unidentified at the covariance
level. Neither block is ready for welfare or decomposition use.

---

## 8. Opportunity-estimation credibility

Heterogeneous across blocks.

(a) **Hours / employment opportunity** (`O^E + O^H`): all four
coefficients individually significant with sensible signs.
`β_E = −2.76` (t = −9.3), `β_h_ft = 1.45` (t = 29.1), `β_h_pt2 =
0.38` (t = 3.4), `β_h_pt1 = −0.50` (t = −4.6). Hierarchy
FT > PT2 > 0 > PT1 is correct. But the predicted hours distribution
collapses onto 51–60+ for couples (see §5), which suggests the
focal-point parameters are interacting badly with the rest of the
model rather than being individually wrong.

(b) **Market opportunity** (`β_E_gsur`, `β_E_educH`): both
significant, both signed correctly (negative for unemployment,
positive for education).

(c) **Wage opportunity** (`O^W`): the cleanest block. Mincer
coefficients all highly significant with correct signs.
`β_w_educH = 0.30` (t = 20.8), `β_w_pexp = 0.017` (t = 7.7),
`β_w_pexp² = −1.95e−4` (t = −4.1), `σ = 0.42` (t = 128). Implied
log-wage σ at 0.42 matches observed log-wage σ of 0.43–0.45 across
groups within rounding. The wage block is the only opportunity
component that could plausibly be reported as a preliminary
result.

The caveat for the wage block: `σ` shows up in the non-PSD
correlation panel with `|corr|` exceeding 1 against three
consumption parameters. The point estimate of σ is plausible and
individually significant, but its identification is intertwined
with the consumption block.

(d) **Occupation opportunity** (`O^Occ`): 8 of 12 significant at
p < 0.05, 10 at p < 0.10. Signs interpretable. Nonroutine-
cognitive (loc4 = 4) is the high-opportunity category for all four
groups. Routine-manual reference dominance for males. The
gendered male-female contrast in routine-cognitive vs nonroutine-
cognitive is consistent with the literature on French labour
market segmentation. Two non-significant coefficients
(`β_occ_2_sf`, `β_occ_4_sm`) — these are noise at small
samples.

The caveat for occupation: predicted occupation shares for
couples include `loc4 = −2` predicted at 1e−64, meaning the model
mechanically excludes the unknown-occupation sentinel for couples
even though 1.2% of couples-male chosen alternatives have it. This
is a model-vs-data mismatch, not an estimation issue.

Bottom line for opportunity: wage block is publishable-ready in
isolation. Occupation block is acceptable as a JMP contribution.
Hours/employment block is identified but the predictions are bad
for couples. The full opportunity layer cannot be cleanly
interpreted while the preference block is unidentified.

---

## 9. Whether M0a-clean can be used for welfare computation

**No. Not even as a toy.**

Three blocking issues:

(a) **The consumption block is non-PSD identified**. Money-metric
well-being is `CV(C, L, j) = U^{−1}(U(C*, L*, j*) − V_actual)` for
counterfactual packages. The inverse utility depends on
`(β_c, θ_c)` jointly; with `|corr(β_c, θ_c)| = 1.01` and three NA
SEs in the singles consumption block, the welfare number depends
on which interior point of an identification flat is chosen. Two
researchers running the same code on the same data could get
materially different welfare numbers because the optimizer can
land anywhere on the flat.

(b) **Couples predictions are not economically interpretable**.
A welfare computation off this θ̂ would say that opportunity
constraints have essentially zero welfare cost for couples,
because the model predicts couples almost always work regardless
of their opportunity set. This is not a finding; it is the
artefact of a missing leisure-leisure interaction and a
near-linear couples consumption Box-Cox.

(c) **Hessian is locally indefinite**. 1 negative eigenvalue, min
= −4.47. The θ̂ is not a local maximum of the likelihood. Any
sensitivity analysis around it (the standard welfare-robustness
exercise) would move in directions that decrease the likelihood,
which is not a meaningful sensitivity.

The standard advice for the welfare layer at this stage of the
project is to develop the welfare scaffolding code (CV, EV,
opportunity-conditioned utility) against a known synthetic θ̂ — for
example, the output of a recovery test on a simulated dataset —
so that the welfare code is ready to plug in once a credible θ̂
becomes available. Do not run the welfare code on M0a-clean's
estimate.

---

## 10. Whether M0a-clean can be used for decomposition

**No. The decomposition cannot be evaluated until the couples-fit
issue is resolved.**

The JMP question is: how much of observed inequality in money-metric
well-being is attributable to unequal job opportunities, and how
much to heterogeneous preferences, once labour supply is modeled as
choice among latent jobs?

For this question to be answered credibly, two things must hold:

(i) The model must reproduce the joint distribution of `(C, H, w,
Occ)` for the population. M0a-clean does this for singles and
fails badly for couples.

(ii) Preferences and opportunities must be separately identified.
M0a-clean fails this at the consumption block.

A decomposition produced on M0a-clean would attribute essentially
zero couples inequality to opportunity differences (because the
model says all couples almost always work, regardless of their
opportunity set), and would attribute essentially all couples
inequality to wage and consumption-preference variation. This is
not a finding about France 2016. It is an artefact of the missing
β_ll and the near-linear couples Box-Cox.

The singles-side decomposition, in isolation, might be informative
once the consumption-block identification is restored. But you
cannot publish a France-2016 inequality-decomposition paper that
reports only singles results — couples are 60% of the working-age
population, and the JMP's normative claim requires the population
to be in scope.

---

## 11. Whether to move to M1 region opportunity now

**No. M1 should wait for couples-preference repair.**

The v4 contract roadmap places M1 (add region dummies on `O^E +
O^H`) immediately after M0a-clean. The intuition is that location-
driven opportunity heterogeneity is the next economic story to add.
The current state changes that priority for two reasons:

(a) **M1 changes opportunity, not preferences**. The couples-fit
pathology is a preferences problem (consumption block near-linear
plus missing leisure interaction). Adding region dummies to
opportunity will not improve couples participation or hours
predictions. It will just spread the existing fit failure across
more parameters.

(b) **M1 would inherit M0a-clean's identification problems**.
Adding region × opportunity interactions to a spec whose
consumption block is non-PSD identified will produce a model with
the same non-PSD signature, plus more parameters, plus a likely
new collinearity between region and `β_E_gsur` (since gsur varies
by region). The Hessian will be worse, not better.

The correct ordering is: fix couples preferences (M0b), confirm
identification is restored, then add region (M1). This is also the
ordering that the literature standardly follows — Capéau et al.
identified the leisure-leisure interaction first, then added region
shifters later.

---

## 12. Recommended next model

**`M0b_couples_preference_repair`**: minimal spec change targeted at
the couples-fit pathology. Two YAML additions, no deletions:

(a) **Add leisure-leisure interaction**. In the YAML, add a new
`couples` subsection:

```yaml
couples:
  leisure_interaction:
    coefficient: "beta_ll"
    initial_value: 0.2          # anchored on Capéau et al. = 0.206
    bounds: [-2.0, 2.0]
```

This adds one parameter. Requires a small parser change to
recognize the new block and a small engine change to add
`β_ll · BC(L_m, θ_l_m) · BC(L_f, θ_l_f)` to the couples utility.

(b) **Constrain `θ_c (couples)` to be closer to `θ_c_singles`**.
Two options of increasing aggressiveness:

(b1) **Tighten the upper bound on `θ_c (couples)`** in the
`bounds` section, e.g. from `[−8.0, 0.95]` to `[−8.0, 0.0]`.
This forces couples consumption to be at most logarithmic, not
near-linear. Adds no parameters.

(b2) **Pool `θ_c` globally** across singles and couples. Replace
the singles `theta_c_singles` and couples `theta_c` with a single
shared `theta_c`. Removes one parameter.

Start with (b1) plus (a). If after estimation the couples
predictions are still extreme, escalate to (b2) plus (a).

This is identification repair on top of the existing M0a-clean
identification repair. Total parameter count after M0b: 47 − 0 + 1 =
48 (if just (a) and (b1)), or 47 − 1 + 1 = 47 (if (b2)).

Pre-conditions for M0b:

- Parser modification to accept the new `couples.leisure_interaction`
  block.
- Engine modification to add the interaction term to couples V.
- Smoke test (likelihood evaluation at initial values) to confirm
  the new term is finite and the gradient is well-defined.

Expected outcomes if M0b is right:

- Couples predicted participation drops from 1.0000 to 0.96–0.98
  (close to observed).
- Couples predicted mean hours drops from 60 to 40–45.
- Couples predicted mean wage drops from 140 to 18–25 EUR/h.
- L1 hours-bin distance for couples drops from 1.7 to under 1.0.
- `β_ll` is significantly positive (leisure complements).
- Couples `θ_c` settles between −0.5 and 0, much closer to singles.
- Hessian negative eigenvalue count drops from 1 to 0, restoring
  Gate B2.
- The consumption-block correlations all fall below 1 in absolute
  value, restoring Gate B3.

If M0b achieves all six, it becomes a credible baseline and the
ladder continues to M1 (region opportunity), then M3 (occupation-
conditional wage), then welfare.

If M0b achieves the couples-fit improvements but the consumption-
block correlations remain >1, the identification problem is
deeper than the leisure-leisure interaction can fix and a more
substantial spec rethink is needed — most likely separate consumption
scaling for singles and couples by household composition (singles
adult-equivalence scale of 1.0, couples scale of about 1.5–1.7).

---

## 13. What not to claim yet

Strictly out of bounds until M0b or its successor clears Gate B:

- Any couples-side participation, hours, or wage moment.
- Any couples-side elasticity (Capéau-style or otherwise).
- Any welfare number, in any form, for any subgroup.
- Any inequality-decomposition number.
- Any preference parameter from the singles consumption block
  (`β_c_sm`, `β_c_sf`, `θ_c_singles`) reported with a standard
  error.
- Any claim that the model identifies preferences separately from
  opportunities — Gate B3 is failed.
- Any comparison to Capéau et al.'s Belgian elasticities — their
  model has the interaction; yours does not.
- Any ρ² number as a summary of fit quality. The aggregate ρ² =
  0.708 pools singles (where it's meaningful) and couples (where it
  hides 1e−109 minimum chosen probabilities).
- Any sentence using "the model fits the joint distribution of...".
- Any region-driven opportunity claim — M1 not run.
- Any claim about the magnitude of `β_E` as a structural
  participation log-odds, until the couples participation
  pathology is resolved.

Statements that are defensible in internal drafts and supervisor
memos:

- The RURO occupation-opportunity pipeline runs end-to-end on
  France 2016 with rebuilt MNL files.
- Data preconditions hold (MNL validation 8/8 PASS, proposal
  adequacy FLAG-but-OK at M0).
- The post-estimation reporter is now verified faithful to the
  structural choice index to 1e−14 precision.
- Singles-side fit moments are reasonable for prototype use.
- The wage-opportunity block (Mincer mean and shared σ) produces
  estimates consistent with observed log-wage moments.
- Occupation-opportunity coefficients have sensible signs for
  singles and show the expected gendered task-content gradients.
- The current specification under-identifies the singles
  consumption block and over-fits couples participation due to a
  near-linear couples consumption Box-Cox plus the absence of a
  leisure-leisure interaction term standardly used in the
  literature.

---

## 14. Immediate next task

In priority order, with tool and saved filename for each.

**Step 1 — Decide between M0b options (this Claude project chat).**

The decision between (b1) and (b2) for the consumption-curvature
constraint is partly a modelling judgment call. Singles `θ_c =
−0.84` and couples `θ_c = +0.32` is a remarkable difference; if
the data really wants them different, pooling them at M0b would
be over-restrictive. But if the +0.32 is partly an artefact of the
missing β_ll absorbing curvature, pooling might let the data
relax to a sensible shared value. Recommendation: start with
(b1) — tighten the upper bound to 0.0 but do not pool — since this
is the more conservative move and leaves the option for (b2) at
M0c if needed.

Save the M0b design decision as
`docs/RURO_occ_M0b_design_memo_v1.md` before any code change.

**Step 2 — Implement M0b YAML, parser change, engine change (Claude
Code).**

Three small changes across:

- `scripts/enhanced/estimation_spec_ruro_occ_M0b.yaml` — new file
  copied from M0a-clean YAML with the two changes from §12.
- `scripts/enhanced/estimation_spec_parser.py` — add recognition of
  the new `couples.leisure_interaction` block.
- `scripts/enhanced/gamspy_estimation_vectorized.py` and
  `scripts/enhanced/estimation_engine.py` — add the
  `β_ll · BC(L_m) · BC(L_f)` term to couples V.

Save the patch report as
`docs/RURO_occ_M0b_implementation_report_v1.md`.

**Step 3 — Smoke test (Claude Code).**

Evaluate the likelihood at initial values; confirm `joint_ll` is
finite and the gradient norm is reasonable. Confirm parser
produces `n_estimated_params = 48` (or 47 if pooling). No
estimation yet.

Save smoke-test output as
`Results/_M0b_smoke_test.json`.

**Step 4 — Estimate M0b (Claude Code → `enh_RURO_estimate_FR.py`).**

Run with `--warm-start none`, at least three start points (spec
defaults, perturbed defaults, random within bounds). Save the run
folder. Re-run post-estimation with the patched reporter.

**Step 5 — Triage M0b (this Claude project chat).**

Same triage structure as this verdict memo: gate scorecard, fit
moments, identification panel, comparison to M0a-clean baseline.
Save as `docs/RURO_occ_M0b_triage_memo_v1.md`.

**Step 6 — Decide next move based on M0b.**

If M0b clears Gate B and the couples fit moments improve:
proceed to M1 (region opportunity) with the standard cadence.

If M0b clears Gate B but couples fit still wrong: try M0c
(global `θ_c` pool, option (b2)).

If M0b fails Gate B: this is a deeper specification issue and a
substantial spec rethink is needed — escalate to supervisor.

**Postponed** (do not touch until M0b passes Gate B):

- M1 region opportunity.
- M2 fine-grained occupation (`loc` instead of `loc4`).
- M3 occupation-conditional wage.
- M4 occupation-conditional hours.
- Welfare computation in any form.
- Recovery test.
- Seed-stability.
- Cross-engine consistency check (worth running independently of
  M0b, but not gating).
- Slides, supervisor figures, abstract numbers touching couples or
  the decomposition.

---

## Evidence trail (current canonical files)

| Purpose | File |
|---|---|
| Verdict (this memo) | `docs/RURO_occ_M0a_clean_verdict_v1.md` |
| Reporting patch | `docs/RURO_occ_M0a_clean_post_estimation_patch_report_v1.md` |
| Structural V diagnostic | `Results/RURO_ruro_occ_M0a_clean_participation_diag_v1.md` |
| Structural V diagnostic data | `Results/_participation_diag_ruro_occ_M0a_clean.json` |
| Patched-reporter fit check | `Results/_M0a_clean_post_est_fit_check.json` |
| Post-patch LLM summary | `reports/fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260514_102334.md` |
| Pre-patch LLM summary (provenance) | `reports/fr_2016_ruro_occ_gamspy_M0a_clean_llm_summary_20260513_193536.md` |
| MNL variable dictionary | `docs/RURO_CONTINUOUS_MNL_VARIABLE_DICTIONARY_v1.md` |
| Active YAML | `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` |
| Canonical estimation | `outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a_clean/run_2026-05-13_19-24-38/estimation_results.json` |

---

## Verdict label

**PROTOTYPE-USABLE FOR SINGLES ONLY. NOT A JMP BASELINE. WELFARE BLOCKED.**

`ruro_occ_M0a_clean` is a clean diagnostic milestone: the reporting
pipeline is now honest, the singles-side fit is defensible, the
wage and occupation blocks produce sensible point estimates, and the
data side of the pipeline is in good shape. It is also a clean
documentation milestone: the underlying couples specification
limitation is now visible rather than hidden behind a reporting bug.
The model is the right kind of object to be the JMP baseline; it
is not yet the right *instance* of that object. The minimum next
step is M0b — leisure-leisure interaction plus couples Box-Cox bound
tightening — before any robustness work, welfare work, or paper-
facing claim that touches couples or the joint decomposition.

---

## Suggested filename

Save this memo as: `RURO_occ_M0a_clean_verdict_v1.md`
(category: technical memo / verdict).
