# RURO occ M0c_b2 GSURv2 — Baseline Verdict v1

Date: 2026-05-18

Specification: `estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
(economic content byte-identical to `estimation_spec_ruro_occ_M0c_b2.
yaml`; differs only in `specification.name` for output-folder
provenance)

Selected run:
`outputs/estimates/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_
ruro_occ_M0c_b2_GSURv2/run_2026-05-17_23-55-09/`

Primary evidence:
- `RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md`
- `RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md`
- `Results/P3a/gsurv2/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md`
- `Results/P3a/gsurv2/RURO_GSUR_v2_stageA_lookup_validation_report_v1.md`

Comparison baseline:
- `RURO_occ_M0c_b2_verdict_v1.md` (the frozen pre-GSURv2 baseline)

Scope of verdict: structural baseline acceptance for the current
project, conditional on Stage A broad-age GSUR resolution. This
verdict does NOT authorise canonical MNL promotion (O10),
welfare-decomposition computation, or Stage B age-specific GSUR
work; those remain separately gated.

---

## 1. Verdict

**`ruro_occ_M0c_b2_GSURv2` is accepted as the new working
structural baseline, conditional on Stage A broad-age GSUR.**

The pre-GSURv2 verdict on `ruro_occ_M0c_b2` was provisional pending
re-estimation against the region-corrected GSUR variable. The
re-estimation has now been completed, validated, and post-estimated,
and the result satisfies the SA-STANDS criterion in the v2.1
specification §9.3.

The acceptance is qualified in five respects:

(V1) The acceptance is conditional on **Stage A broad-age GSUR
only**. The lookup uses Y20-64 broad-age values weighted to EUROMOD
`drgn1` from corrected NUTS-2 components. Stage B age-specific GSUR
(narrow age bands) has not been implemented and is not authorised by
this verdict.

(V2) The acceptance does NOT promote the versioned GSURv2 MNL
parquets to canonical paths. Canonical promotion is an O10 decision
that requires a separate explicit user approval message after the
Stage A verdict, per the v2.1 spec §12(F6-promote) and §15(R2).
This verdict is SA-STANDS, which makes promotion *eligible* under
the v2.1 §9.3 decision rule, but does not by itself authorise the
promotion.

(V3) The singles consumption joint-identification limitation (3 NA
SEs on `beta_c_sm`, `beta_c_sf`, `theta_c_singles`) is unchanged
from M0c_b2 and remains a known structural data limitation. The
GSUR correction does not resolve or worsen it. Any welfare
decomposition that operationally requires identified singles
consumption curvature must be designed with this limitation in
mind.

(V4) `beta_E_educH` falls from p = 0.0094 in M0c_b2 to p = 0.0518
in M0c_b2_GSURv2. The estimate shrinks from +0.613 to +0.439
(−28%) while the standard error contracts slightly. The
interpretation given in §3 below is that the corrected GSUR
disentangles education-region correlation that was previously
absorbed by the education-on-opportunity coefficient. The shift is
substantively informative; it must not be presented as a model
defect.

(V5) Welfare decomposition is NOT authorised. The model passes the
estimation and fit-stability gates required for baseline
acceptance; it does not yet pass the additional welfare-readiness
gates that depend on identified consumption curvature and a
documented welfare-measurement framework. See §11.

The verdict for M0c_b2 (the previous baseline) is hereby
superseded by this memo for all forward purposes. M0c_b2 remains
documented for provenance and reproducibility but is no longer the
working baseline.

---

## 2. What changed in GSURv2

The change is restricted to the data variable `gsur` (and its
partner-specific variants in couples). No economic model element
changes; no model parameter is added or removed; no constraint or
bound is modified; no draws, alternatives, or prior corrections are
revised. The change is a data correction.

Substantively, the GSURv2 `gsur` column differs from the GSURv1
`gsur` column along four dimensions, all of which are corrections:

(C1) **Regional crosswalk corrected.** The GSURv1 variable was
assembled under a misaligned crosswalk that confused pre-2016 and
post-2016 NUTS vintages and that aggregated at NUTS-1 rather than
NUTS-2. GSURv2 uses a `drgn1` → old NUTS-2 → new NUTS-2 chain
verified against the official Eurostat `NUTS2013-NUTS2016.xlsx`
correspondence.

(C2) **Sex stratification activated.** The GSURv1 variable used
TOTAL-sex rates; the GSURv2 variable joins on sex (M, F) so that
within a couple the male and female partners receive their own
regional sex-specific unemployment rates.

(C3) **Education stratification activated.** The GSURv1 variable
used TOTAL-education rates; the GSURv2 variable joins on
ISCED-aligned `educ3` (ED0-2, ED3-4, ED5-8).

(C4) **Denominator correctly weighted.** Where a `drgn1` group spans
multiple post-2016 NUTS-2 components, the aggregation is now
population-weighted (Eurostat `lfst_r_lfsd2pop`, the D2 operational
denominator per the O2 binding decision). GSURv1 used an unweighted
mean.

The magnitude of these corrections at the MNL-cell level is
substantial: the singles-level mean absolute v1→v2 difference is
1.66 percentage points and the maximum is 10.60 percentage points
(at drgn1 = 3, dgn = 0, educ3 = 0 — Nord-Pas-de-Calais low-education
females). The sign of the correction reverses across regions in a
pattern consistent with the v1 misalignment having been
systematically biased in opposite directions across EUROMOD
groupings. Île-de-France (drgn1 = 1, the single-component case)
shows zero correction at all six (educ3, sex) cells, confirming
that the v1 misalignment was concentrated in multi-component
groupings.

Operationally, the parquet rebuild verified all v2.1 §14 gates
M1-M10 plus M12-diag at the strictest interpretation (the rebuild
report records 9/9 hard gates passing). The merge preserved the v1
audit trail (`gsur_legacy_misaligned`), respected the household-
level constancy property, and did not touch canonical files.

---

## 3. Whether the GSUR issue is resolved

**The GSUR issue is resolved for the current Stage A structural
baseline. It is not resolved for Stage B age-specific work, which
remains scope-deferred under O6.**

The GSUR issue identified in the M0c_b2 verdict §6 had three
components, of which this verdict addresses two and defers the
third.

(R1) **Regional misalignment (resolved).** The GSURv2 lookup
correctly maps EUROMOD `drgn1` to the corresponding pre-2016
NUTS-2 components and uses 2016-vintage NUTS-2 Eurostat data with
the proper renaming. The Île-de-France parity check at the MNL
level produces zero numerical error at machine precision (M4 in
the rebuild report). The crosswalk has been signed off (O7) and the
lookup validation reports all nine pass/fail checks passing,
including the national-benchmark consistency check against INSEE
BDM `001688526` (9.82% computed vs 9.725% benchmark, Δ = 0.10
percentage points within the ±1.0 percentage-point tolerance).

(R2) **Sex/education stratification (resolved).** The GSURv2 lookup
is fully stratified by sex × ISCED-`educ3` × NUTS-2 region. The
post-estimation diagnostics confirm partner-specific GSUR variation
in couples (the M6 fraction of `gsur_male = gsur_female` is 0.0%,
indicating sex-stratified rates are operative throughout). The
`beta_E_gsur` coefficient is now identified against a regionally,
educationally, and sex-stratified labour-market indicator, where
M0c_b2 estimated it against an unstratified one.

(R3) **Age stratification (deferred).** Stage A uses the Y20-64
broad-age value for all working-age individuals (with the O3 fallback
for the 200 singles age-65 rows = 2 households flagged as
`Y20-64_fallback_age65`). The narrow age bands (Y15-24, Y25-34,
Y35-44, Y45-54, Y55-64) are not used in this Stage A run, and Stage
B has not been authorised. The age-stratification component of the
broader GSUR issue is therefore explicitly outside the scope of the
current baseline.

The pre-GSURv2 baseline could not separate true regional
labour-market effects from measurement-induced attenuation in the
GSUR coefficient. The post-GSURv2 baseline can. This is sufficient
to declare the GSUR issue resolved *for the current structural
baseline*. Stage B is a separate later question.

---

## 4. Whether beta_E_gsur is now interpretable

**Yes, `beta_E_gsur` is now interpretable in the structural sense
required by the latent-jobs RURO framework. Direct probability
interpretations require correct construction at the GSUR scaling
used in the specification.**

Under M0c_b2 (pre-GSURv2) the `beta_E_gsur` estimate was −0.7438
with standard error 0.213 (t = −3.49, p = 0.0005). Its sign was
correct (higher regional unemployment reduces employment opportunity)
but the interpretation was compromised by GSUR-measurement error:
the regression of the latent opportunity index on a misaligned
regional unemployment variable produced an attenuated coefficient
whose magnitude was not interpretable as the partial response to a
true regional labour-market shock.

Under M0c_b2_GSURv2 the estimate is −1.0502 with standard error
0.2002 (t = −5.246, p = 1.55 × 10⁻⁷). The 41% increase in magnitude
(in absolute value) is in the direction expected under classical
measurement-error attenuation: the correction tightens the regression
of the opportunity index onto the corrected regional UR, recovering
a stronger response. The smaller standard error (0.213 → 0.200)
indicates that the corrected variable improves precision modestly,
consistent with measurement error having inflated residual variance
in the M0c_b2 estimation.

The economic interpretation must respect the GSUR variable's scaling
in the specification. The estimator enters `gsur` in proportion units
(0.04 = 4%) and centred within the choice set with proposal weights
per the spec's `market_opportunity` block. Consequently:

(I1) The reported `beta_E_gsur = −1.0502` is the coefficient on
the centred, proportion-units GSUR variable inside the
choice-utility specification. It is NOT the marginal effect on the
unconditional probability of employment.

(I2) A direct probability semi-elasticity requires computation
through the model's full opportunity block: changes in `gsur` enter
the choice-utility index, are scaled by `beta_E_gsur`, interact
with other opportunity components (`beta_E`, `beta_E_educH`, the
proposal correction), and pass through the softmax over the
alternative set. Pointwise marginal effects are well-defined only
when computed under the full alternative-by-alternative simulation,
not by direct semi-elasticity arithmetic on `beta_E_gsur`.

(I3) For order-of-magnitude framing only (not for citation): a
unit increase in `gsur` (i.e. 1.0 absolute, or 100 percentage
points) shifts the centred choice-utility index by approximately
−1.05 utility units per alternative. A 1-percentage-point increase
in regional unemployment (Δgsur = 0.01) shifts the index by
approximately −0.0105 utility units per alternative. These figures
are illustrative; they should not be used as the basis for welfare
or policy calculations without being recomputed through the model
in a participation- or hours-equivalent metric.

For paper-writing purposes, `beta_E_gsur` is now a structurally
interpretable parameter and the GSURv2 estimate is the figure that
should be reported as the baseline. The 41% strengthening relative
to M0c_b2 should be discussed in the text as the measurement
correction, not framed as a behavioural change.

---

## 5. Parameter stability relative to old M0c_b2

**Preference parameters are stable. Wage parameters are stable.
Occupation parameters are stable. The market-opportunity sub-block
(`beta_E`, `beta_E_gsur`, `beta_E_educH`) shifts coherently in
response to the GSUR correction.**

The full 47-parameter comparison is in §15 of the estimation report
and the appendix of that report. Summarising:

(S1) **Singles preferences (12 parameters)**. Maximum absolute
change is 0.032 on `beta_l0_f` (a couples-female leisure intercept;
this row is mistakenly grouped under singles in the comparison
table — the parameter belongs to the couples block). Among the
true singles preference parameters, the maximum change is 0.016 on
`beta_l0_sm` and 0.009 on `beta_c_sm`. The Box-Cox exponents
(`theta_l_sm`, `theta_l_sf`, `theta_c_singles`) change by less
than 0.009 in absolute value. The leisure shifters by age and by
number of children change by less than 0.008.

(S2) **Couples preferences (5 parameters)**. The leisure intercept
`beta_l0_f` changes by +0.032 (the largest shift in any preference
parameter, but 1.2% in relative terms and well within the SE of
0.432). `beta_l0_m`, `theta_l_m`, `theta_l_f`, `beta_l_age_f`, and
`beta_l_nkids_f` are all stable to within 0.008.

(S3) **Couples consumption + interaction (2 parameters)**.
`beta_c` changes by 0.006 (0.15% relative). The central
household-complementarity parameter `beta_ll` changes from 2.624
to 2.605, a relative change of 0.7% and well within its standard
error of 0.346. The substantive paper-ready finding R5.1 (β_ll
strongly positive, t > 7) is preserved unchanged: t(M0c_b2) = 7.58
versus t(M0c_b2_GSURv2) = 7.54. The finding R5.2 (log-utility
preferred on couples consumption, `theta_c` fixed at 0) remains
the spec choice and is unaffected.

(S4) **Wage block (6 parameters)**. All wage parameters change by
less than 0.005 in absolute value. The wage-offer dispersion
`sigma` changes from 0.42676 to 0.42680 (0.01% relative). The
Mincer block (`beta_w0`, `beta_w_educL`, `beta_w_educH`,
`beta_w_pexp`, `beta_w_pexp2`) is unchanged to the third decimal
place. The finding R5.3 (σ = 0.427) and R5.4 (Mincer consistent
with French literature) carry over unchanged.

(S5) **Occupation block (12 parameters)**. All occupation
shifters change by less than 0.002 in absolute value. The
occupation gradient is fully stable; 8 of 12 occupation parameters
remain significant at p < 0.05 (matching the R5.5 finding).

(S6) **Market-opportunity block (3 parameters, the substantive
shift)**. `beta_E`: −2.8423 → −2.4895 (Δ = +0.353, 12% relative
shift). `beta_E_gsur`: −0.7438 → −1.0502 (Δ = −0.306, 41%
magnitude increase). `beta_E_educH`: +0.613 → +0.439 (Δ = −0.175,
28% magnitude decrease). The three shifts are coherent: the
baseline employment disutility `beta_E` partially offsets the
strengthened GSUR effect, and the education-on-opportunity term
narrows because the corrected GSUR absorbs education-region
correlation previously left in `beta_E_educH`.

By v2.1 §9.3 decision rules:
- All preference parameters shift by less than 5% (the SA-STANDS
  threshold for preference stability).
- `beta_E_gsur` shifts by 41% (above the 50% SA-REVISION trigger
  by a comfortable margin; below the 50% threshold by ~10
  percentage points and not at the threshold).
- Other opportunity-block parameters (`beta_E`, `beta_E_educH`)
  shift by 12% and 28% respectively (these are within the SA-STANDS
  envelope when interpreted as expected co-movements with the
  corrected GSUR; they are not independent shifts of unrelated
  parameters).

The verdict is **SA-STANDS** under v2.1 §9.3, not SA-REVISION. The
M0c_b2 verdict findings R5.1-R5.5 carry over essentially unchanged
to GSURv2, conditional on the four updates noted in §12 below.

---

## 6. Fit stability relative to old M0c_b2

**Fit improves overall by all three information criteria. Local
fit changes are mixed but small.**

Information criteria:
- Joint log-likelihood: −6509.16 → **−6501.21** (Δ = +7.95 units
  for zero additional parameters).
- AIC: 13112.3 → **13096.4** (Δ = −15.9).
- BIC: 13627.5 → **13611.6** (Δ = −15.9).
- McFadden ρ²: 0.70839 → **0.70875** (Δ = +0.00036).

The +7.95-unit log-likelihood improvement is substantively
meaningful for a zero-parameter data correction. It is the strongest
evidence that the GSUR correction is doing real work, not just
shifting parameter values cosmetically.

Participation fit by group:

| Group | M0c_b2 Δ | M0c_b2_GSURv2 Δ | Change |
|---|---|---|---|
| Singles male | +0.000 | +0.0004 | ≈ 0 |
| Singles female | +0.012 | +0.024 | +1.1 ppt worse |
| Couples male | +0.011 | +0.015 | +0.4 ppt worse |
| Couples female | +0.024 | +0.026 | +0.3 ppt worse |

The participation-rate fit for non-SM groups worsens by 0.3-1.1
percentage points. The post-estimation diagnostics flag the
couples-female predicted rate (0.9911) as "very high". This pattern
existed in M0c_b2 and is amplified marginally in GSURv2; it
reflects the model's structural difficulty generating non-employment
in couples and in females in a specification without fixed costs
of work or formal rationing. The worsening is small relative to the
underlying pattern and does not invalidate the structural baseline.

Hours fit by group:

| Group | M0c_b2 mean Δ | M0c_b2_GSURv2 mean Δ | L1 distance change |
|---|---|---|---|
| Singles male | −3.59 h | −3.58 h | −12.7% (improved) |
| Singles female | −1.21 h | −1.22 h | +4.5% (slight regression) |
| Couples male | +1.17 h | +1.15 h | +2.3% (negligible) |
| Couples female | +3.33 h | +3.30 h | +0.8% (negligible) |

Hours mean fit is unchanged at the first decimal place for all four
groups. The singles male hours-distribution L1 distance improves
materially (−12.7%); the other groups change negligibly. The
couples-female mean-hours overprediction of +3.3 hours per week
persists; this is a known limitation of the M0c_b2 baseline
unaffected by the GSUR correction.

Wage fit: unchanged. The Mincer block and `sigma` are unchanged to
three decimal places; observed-vs-predicted wage quantiles are
identical to M0c_b2.

Occupation fit: unchanged. Couples occupation shares match to within
1 percentage point in both models; the singles occupation fit
limitation (no group-specific occupation shifters at M0c_b2) is
unchanged.

The verdict is **fit-stable with positive evidence on information
criteria and one positive local improvement (singles-male hours)**.
The slight participation-fit regressions for non-SM groups are
within the tolerance expected for a data correction that shifts
opportunity-block parameters and do not undermine the SA-STANDS
finding.

---

## 7. Identification diagnostics

**The Hessian topology is identical to M0c_b2. The condition number,
the number of negative eigenvalues, the number of NA standard
errors, and the structure of the negative-variance block are
unchanged.**

| Diagnostic | M0c_b2 | M0c_b2_GSURv2 |
|---|---|---|
| Hessian condition number | 5.06 × 10¹⁰ | 5.14 × 10¹⁰ |
| Negative eigenvalues | 1 | 1 |
| Near-zero eigenvalues (|λ| ≤ 10⁻⁸) | 0 | 0 |
| Bound hits | 0 / 47 | 0 / 47 |
| Valid standard errors | 44 / 47 | 44 / 47 |
| NA standard errors | 3 / 47 | 3 / 47 |
| Affected NA-SE parameters | `beta_c_sm`, `beta_c_sf`, `theta_c_singles` | same three |

Multistart confirmation: three independent starts (warm from
M0c_b2, spec defaults, ±5% perturbed with seed 42) converge to
identical log-likelihood −6501.2082 and identical parameter vector
at machine precision. The GSURv2 solution is the unique attractor
among the tested starts; this is the strongest possible
finite-sample identification evidence for the parameter vector.

The single negative Hessian eigenvalue and three NA standard errors
are localised in the singles consumption sub-block, as in M0c_b2.
This is the structural data limitation discussed in §8 below. It is
not a model defect, not an estimation failure, and not affected by
the GSUR correction.

Among the 44 parameters with valid SEs:
- 29 are significant at p < 0.05 (vs 30 in M0c_b2; the one parameter
  that lost significance is `beta_E_educH`, p = 0.0094 → 0.0518,
  discussed in §1 V4 above).
- 28 are significant at p < 0.01.
- All 12 occupation shifters except `beta_occ_4_sm` (p = 0.787)
  and `beta_occ_2_sf` (p = 0.921) are significant at p < 0.10;
  8 of 12 are significant at p < 0.05 (preserving the R5.5
  finding).
- The wage block has all 6 parameters significant at p < 0.05;
  `sigma` is significant at p < 10⁻¹⁵.
- The household leisure interaction `beta_ll` is significant at
  p = 4.86 × 10⁻¹⁴ (t = 7.535), preserving R5.1.

The identification diagnostics confirm SA-STANDS at the strictest
interpretation: no degradation in identification, no parameter on
a boundary, no new singular eigendirection, no instability across
starts.

---

## 8. Remaining singles consumption limitation

**The singles consumption joint-identification limitation is
unchanged and remains a known structural data limitation.**

The three parameters `beta_c_sm`, `beta_c_sf`, and
`theta_c_singles` enter the singles utility specification as

U_sm(c, l) = beta_c_sm · c^{theta_c_singles} + (leisure block)
U_sf(c, l) = beta_c_sf · c^{theta_c_singles} + (leisure block)

with the Box-Cox exponent `theta_c_singles` shared between male and
female singles. The likelihood surface in the (`beta_c_sm`,
`beta_c_sf`, `theta_c_singles`) subspace is near-flat: the consumption
variation in the French 2016 singles sample is insufficient to
separately identify the two scale parameters and the shared exponent.
The Hessian's negative eigenvalue and the pseudoinverse-produced
negative diagonal entries (reported as NA SEs) sit in this
sub-block.

The condition is documented in the M0c_b2 verdict §4 as a data
limitation. GSURv2 does not affect singles consumption variation
(the GSUR variable enters the market opportunity block, not the
utility block), so the limitation is fully preserved. The point
estimates of all three parameters shift by less than 0.01 in
absolute value between M0c_b2 and M0c_b2_GSURv2; the limitation
is therefore stable in its location and magnitude.

Implications for the JMP welfare scaffold:

(L1) Welfare functionals that operationally require identified
singles consumption curvature must either (a) marginalise over the
parameter uncertainty in this sub-block, (b) work with the joint
function `c → beta_c · c^{theta_c}` (which is identified up to
joint scaling at the point estimate, even if its individual
components are not), or (c) restrict welfare calculations to
couples and adjust the JMP's framing accordingly.

(L2) The pseudoinverse-based SE replacement is a standard finite-
sample treatment for this kind of near-singular Hessian. It is
acceptable for the baseline verdict but should be flagged in the
JMP paper text as a known robustness item.

(L3) Stage B age-specific GSUR, M1-clean region dummies, and the
welfare decomposition all operate in the presence of this
limitation. None of them depend on identified singles consumption
curvature for their core estimation step; welfare is the place
where this matters operationally, and the framing in §11 below
respects that.

The limitation is documented and not a new finding. It does not
block baseline acceptance.

---

## 9. Whether this is the working structural baseline

**Yes. `ruro_occ_M0c_b2_GSURv2` is the working structural baseline
for the JMP, conditional on the qualifications in §1.**

The previous baseline (`ruro_occ_M0c_b2`) was provisional pending
GSUR correction. The correction has now been applied, validated,
and re-estimated. The result is SA-STANDS under v2.1 §9.3 with a
+7.95 log-likelihood improvement, fully stable preference and wage
blocks, a coherent shift in the market-opportunity block, and
unchanged identification topology.

For all forward purposes — paper text, supervisor memos, robustness
exercises, M1-clean design — `ruro_occ_M0c_b2_GSURv2` is the
reference. M0c_b2 is documented for provenance but is not the
working baseline.

Canonical promotion (the F6-promote step of v2.1 §12) is NOT
authorised by this verdict. It requires a separate explicit user
approval message per O10. Until that approval is granted, all
estimation that consumes corrected GSUR must use the `--mnl-base
".../fr_2016_RURO_mnl_GSURv2"` stem rather than the canonical
stem. The canonical files at the canonical paths retain v1 content
and are untouched.

Recommended next step on the promotion question: defer the O10
canonical-promotion decision until after the M1-clean design memo
is written (so that the M1-clean implementation can be designed
against the versioned GSURv2 parquets without an intervening
canonical overwrite). The promotion is reversible in practice (v1
canonical files would be archived as `_GSURv1` per the v2.1
F6-promote procedure), so deferring it has no operational cost
and preserves optionality.

---

## 10. Whether to proceed to M1-clean

**Yes. M1-clean design and implementation are authorised against the
GSURv2 baseline.**

M1-clean is the next planned step on the JMP roadmap. Per the JMP
ability-vs-opportunity framework memo, M1-clean implements two
structural changes relative to M0c_b2:

(M1a) **Drop `beta_E_educH` from the market-opportunity block.**
Education is reclassified as ability (under the weak Dworkinian
welfare criterion) rather than opportunity. The market-opportunity
block in M1-clean retains `beta_E`, `beta_E_gsur`, and the
occupation shifters but drops `beta_E_educH`.

(M1b) **Add NUTS-1 region dummies × working** to the
market-opportunity block. These capture region-level demand
variation orthogonal to the (now stratified) GSUR signal.

Both changes are well-defined against the GSURv2 baseline because:

(W1) The GSURv2 stratification means that `beta_E_educH` is no
longer absorbing education-region correlation (per the §3 R1-R2
discussion); its drop from M1-clean is therefore semantically
cleaner than it would have been against M0c_b2. The GSURv2
estimate of `beta_E_educH` (+0.439, p = 0.052) is the boundary
case that signals exactly this: under the corrected GSUR, the
education-on-opportunity effect is small enough to be reclassified
without losing substantial fit.

(W2) The corrected GSUR provides the region-stratified variation
that the M1-clean region dummies will then orthogonalise. The
M1-clean partition is the eight metropolitan `drgn1` regions
(drgn1 ∈ {1, ..., 8} per the §10 sample-perimeter decision), not
the thirteen modern NUTS-1 régions.

(W3) The Hessian topology of M0c_b2_GSURv2 is stable and the
multistart attractor is unique. M1-clean is a small structural
perturbation around this fixed point and is expected to remain
well-identified.

Sequencing recommendation:

(S1) **M1-clean design memo first.** Document the precise YAML
specification change, the expected parameter shifts, the new
identification diagnostics to run, and the SA-style decision rule
for accepting M1-clean. Treat this as `RURO_occ_M1_clean_design_
memo_v1.md` (parallel to the M0a, M0b, M0c design memos).

(S2) **M1-naive sensitivity in parallel.** Per the JMP framework
memo, the robustness exposure R2 requires estimating both
M1-clean (region dummies, no `beta_E_educH`) and M1-naive (region
dummies, keep `beta_E_educH`) so that the framework can show how
the ability-vs-opportunity decomposition responds to whether
education enters the opportunity block.

(S3) **M1-clean implementation prompt** for Claude Code, against
the versioned GSURv2 parquets. Same `--mnl-base` stem as the
GSURv2 estimation; new YAML spec.

(S4) **M1-clean verdict** following the same template as this
memo.

M1-clean should NOT be sequenced before O10 canonical promotion if
canonical promotion is desired before M1-clean estimation. Per §9
the recommendation is to defer canonical promotion until after
M1-clean implementation, which means M1-clean operates against the
versioned paths.

---

## 11. Whether to proceed to welfare scaffolding

**Welfare-decomposition computation is NOT authorised by this
verdict. Welfare-scaffolding design work can proceed as a parallel
track that does not depend on the GSURv2 estimates.**

The JMP's central deliverable is a decomposition of money-metric
well-being inequality into opportunity, ability, and preference
components, per the framework memo and the v2 of the concept note.
This requires:

(W1) A specific money-metric well-being functional (Fleurbaey-style
equivalent income or equivalent variation), chosen and documented.

(W2) A specific counterfactual decomposition method (ordered removal,
Shapley, or both), with reference distributions for ability and
opportunity defined.

(W3) A specific inequality index (Gini, Atkinson, generalised entropy)
or family of indices.

(W4) Bootstrap inference compatible with the parameter-vector
constraints (the three NA-SE singles consumption parameters require
care).

(W5) Operational handling of the singles consumption identification
limitation discussed in §8.

None of these are settled in writing. The JMP framework memo
identifies the questions but does not lock the answers. The
literature is largely sufficient (Bargain et al. 2013, Capéau et
al. 2021, Fleurbaey-Maniquet 2018-2019, Aaberge-Colombino tradition
on rank-dependent SWFs, Shorrocks 2013 on Shapley decomposition,
Bhattacharya 2015 on EV/CV identification for discrete choice).
The decision is methodological selection from this literature, not
literature acquisition.

Recommendation:

(R1) **Write a welfare-measurement decisions memo** as the next
conceptual lock-in step (`JMP_welfare_measurement_decisions_memo_
v1.md`). This memo should resolve W1-W4 by reference to the
literature already in the project and should specify how W5 will
be handled. The memo can be written in parallel with the M1-clean
design work; it does not depend on M1-clean being completed first,
and it does not require running any welfare computation.

(R2) **Defer welfare scaffolding implementation** until the
decisions memo is locked. Implementation requires (a) the M1-clean
estimates (because M1-clean is the JMP's preferred specification
for welfare; M0c_b2_GSURv2 is the baseline against which M1-clean
is compared), (b) the welfare-measurement decisions memo, and (c)
either the canonical-promoted GSURv2 parquets or a consistent
choice of the versioned parquets.

(R3) **Do not run welfare computation** as part of any current
prompt. The post-estimation diagnostics report §19 conclusion is
explicit: "welfare decomposition remains separately gated and is
not authorised by this report."

The welfare track is the next major conceptual step but is not
sequenced immediately after this verdict. The immediate next task
is in §13.

---

## 12. What not to claim yet

The following claims are NOT supported by the current evidence and
should not appear in the JMP text, supervisor memos, or
presentations until additional work is completed.

(N1) **"The GSUR issue is fully resolved."** Not supported. Stage A
broad-age GSUR is resolved. Stage B age-specific GSUR is deferred
(O6) and may either (a) prove unnecessary on inspection or (b)
require a separate spec, lookup, and estimation cycle. Use "the
Stage A broad-age GSUR issue is resolved" or "the regional and
demographic GSUR misalignment is resolved" as the supported
phrasing.

(N2) **"The corrected GSUR coefficient β_E_gsur = −1.05 means a 1
percentage point higher regional unemployment reduces employment
probability by X percent."** Not supported as stated. The
coefficient is on the centred, proportion-units GSUR variable in
the choice-utility index, not on an outcome probability. Direct
probability marginal effects must be computed through the model.
See §4 for the correct interpretive framing.

(N3) **"The 41% strengthening of β_E_gsur is a substantive
finding about French regional labour markets."** Not supported. It
is a measurement correction. The substantive finding is that the
v1 misalignment produced classical attenuation bias and that the
corrected variable recovers a stronger relationship. The 41% is
the magnitude of the attenuation correction, not the magnitude of
a behavioural response.

(N4) **"The M0c_b2_GSURv2 baseline is the final structural
specification for the JMP."** Not supported. It is the working
baseline. M1-clean is the planned next specification and is
expected to be the JMP's reported preferred specification, with
M0c_b2_GSURv2 as the comparison baseline.

(N5) **"The singles consumption identification issue is resolved."**
Not supported. It is unchanged. The three NA SEs remain in the same
sub-block. Documentation as a known limitation is acceptable;
treating it as resolved is not.

(N6) **"The corrected baseline justifies welfare decomposition."**
Not supported in the absence of (a) M1-clean estimates and (b) a
welfare-measurement decisions memo. The baseline is suitable for
welfare scaffolding *design* work, not for welfare computation
output.

(N7) **"β_E_educH lost significance because the GSUR correction
broke the education effect."** Not the correct interpretation.
β_E_educH lost significance because the corrected GSUR absorbed
education-region correlation that was previously left in the
education-on-opportunity coefficient. The education-on-wage
coefficients (`beta_w_educL`, `beta_w_educH`) are unchanged and
remain highly significant: the education effect on wages is fully
preserved; only its absorption into the opportunity block is
narrowed.

(N8) **"GSURv2 results can replace M0c_b2 results in the paper
without comment."** Not supported. The replacement should be made
with a clear footnote or methods-section paragraph documenting
the GSUR correction, its motivation, and its quantitative effect.
The reader needs the audit trail.

(N9) **"Canonical promotion is approved."** Not supported. O10
canonical promotion is a separate decision per §9.

(N10) **"M1-clean has been started."** Not supported as of the
date of this verdict. M1-clean design memo is the recommended
next step; implementation is two steps further.

---

## 13. Immediate next task

**The immediate next task is to write the M1-clean design memo.**

Tool path: Claude Project chat (conceptual synthesis / design memo
work), not Claude Code.

Inputs to consult:
- `JMP_ability_vs_opportunity_framework_v1.md` (the M1-clean
  motivation and the partition of variables across opportunity,
  ability, and preferences)
- `RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (this memo, the baseline
  the M1-clean spec sits on)
- `RURO_GSUR_rebuild_specification_v2_1.md` §16 (what must not be
  changed in the spec; M1-clean is allowed to change the
  market-opportunity block but not the wage, occupation, or
  preference blocks)
- `scripts/enhanced/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
  (the working YAML; M1-clean YAML is derived from this)
- The frozen identification findings R5.1-R5.5 in the M0c_b2
  verdict §5 (carry over to M0c_b2_GSURv2; M1-clean should preserve
  R5.1 β_ll, R5.2 log-utility on couples consumption, R5.3 σ, R5.4
  Mincer block as identified)

Deliverable: `docs/RURO_occ_M1_clean_design_memo_v1.md`. Structure
should parallel the M0a/M0b/M0c design memos in the project,
covering:

(D1) Motivation (why drop `beta_E_educH` and add region dummies,
referencing the framework memo).

(D2) The exact YAML edits relative to
`estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`.

(D3) The expected parameter shifts and the SA-style decision rule
for accepting M1-clean (SA1-STANDS, SA1-REVISION, SA1-OVERTURNED
analogues).

(D4) The identification diagnostics to run on M1-clean and the
expected pre-/post-comparison structure.

(D5) The M1-naive parallel specification (region dummies but
keeping `beta_E_educH`), for the framework memo's R2 robustness
exposure.

(D6) The sequencing: M1-clean design memo → M1-clean implementation
prompt → M1-clean estimation → M1-clean verdict → M1-naive
sensitivity → welfare-measurement decisions memo → welfare
scaffold.

(D7) An explicit non-authorisation statement: the design memo does
not authorise estimation; implementation requires a separate
implementation prompt for Claude Code Sonnet.

Optional parallel deliverable: `docs/JMP_welfare_measurement_
decisions_memo_v1.md`. This memo is not blocked by M1-clean and
can be drafted in parallel by either Claude Project chat or
ChatGPT thinking chat. Writing it earlier rather than later is
recommended because the welfare functional choice (equivalent
income vs EV/CV vs equivalent variation, choice of inequality
index, choice of decomposition method) affects how the M1-clean
results will be presented in the JMP. Resolving the welfare
choices in writing now means M1-clean estimation can be sequenced
straight into welfare scaffolding without a methodological
hiatus.

Things NOT to do in the next task:
- Do not run any estimation.
- Do not write any code.
- Do not run welfare computation.
- Do not promote the GSURv2 parquets to canonical paths.
- Do not commit to a Stage B GSUR implementation; that decision is
  deferred to post-M1-clean review (O6).
- Do not modify `estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`. The
  M1-clean YAML is a separate file derived from it.
