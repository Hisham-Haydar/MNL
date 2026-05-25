# JMP Multi-Year Data Strategy: Pooling, Cross-Year Replication, and Cross-Validation — Strategy Memo v1

Date: 2026-05-18

Specification class: strategy memo. The memo evaluates three distinct
proposals that would extend the JMP's empirical basis beyond the
current France 2016 cross-section. It recommends one of the three for
implementation as a JMP robustness exposure, defers the second, and
dismisses the third. The memo does not authorise implementation
work; its outputs are a recommendation for sequencing and a sketch of
the operational design that any subsequent implementation prompt
would build upon.

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the accepted structural
  baseline against which any multi-year extension is judged)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` (the structural design
  document defining the preferred specification)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the data-corrected
  baseline)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the welfare
  framework whose robustness exposures the proposals would
  supplement)
- `euromod_fr_2015_2017_standard_income_concepts.csv`,
  `euromod_fr_2015_2017_output_variable_index.csv` (provisional
  evidence that EUROMOD FR data is available for 2015 and 2017)

Scope: a methodological evaluation conditional on the M1-clean
SA1-STANDS verdict. The memo respects the project's existing
sequencing — M1-naive estimation, welfare-measurement decisions
memo, welfare scaffolding — and locates any multi-year work within
that sequence.

---

## 1. The two proposals are distinct

The user's framing combines two methodological additions under the
casual label "use more data than 2016." The two additions differ in
their model-design implications, in their operational cost, and in
their evidentiary returns. They must be evaluated separately before
either can be incorporated into the JMP's robustness architecture.

The first proposal — out-of-sample validation through cross-
validation — is a *predictive-accuracy* exercise. It asks whether
the structural model, estimated on a training subset of the data,
predicts well on a held-out subset. The natural held-out subset
might be a random sample of households, a held-out year, or a
held-out subgroup. The criterion is predictive fit (typically
measured by log-likelihood, classification accuracy, or marginal-
distribution fit) on the held-out subset.

The second proposal — pooling 2015, 2016, and 2017 EUROMOD France
data before estimation — is a *sample-size and time-variation*
exercise. It asks whether estimating the structural model on a
larger pooled sample produces tighter standard errors and improved
identification of weakly identified parameters. The criterion is
parameter precision and the resolution of identification weaknesses
documented in the current 2016 baseline.

These exercises target different inferential objects. Cross-
validation targets the model's *generalisation* property — its
ability to predict outcomes not used in estimation. Pooling targets
the *identification* property — the precision and stability of the
structural parameters used for welfare inference. A method that
improves one need not improve the other; pooling, for instance,
might leave the model's out-of-sample predictive accuracy
essentially unchanged while substantially improving structural
parameter identification, and conversely a model that survives
cross-validation might still have weakly identified parameters in
the welfare-relevant blocks.

The remainder of this memo evaluates four distinct operational
realisations of these two ideas, recommends one for incorporation
as a JMP robustness exposure, defers two as either too costly or
too marginal at the current project stage, and dismisses one as
methodologically uninformative.

---

## 2. The four operational variants

Four distinct operational realisations span the proposal space.

*Variant A — Multi-year pooled estimation.* The 2015, 2016, and
2017 EUROMOD France samples are stacked into a single dataset.
The M1-clean specification is augmented with year fixed effects
in the opportunity block (potentially also in the wage block,
depending on identification strategy), with preferences assumed
time-invariant. Estimation proceeds on the pooled sample of
approximately 12,000–13,000 households. The result is a single
set of structural parameters estimated against three years of
observed labour-supply behaviour.

*Variant B — Cross-year structural replication.* The M1-clean
specification is estimated separately on each of the 2015, 2016,
and 2017 cross-sections, producing three independent parameter
vectors. The cross-year comparison serves as a robustness check
on the temporal stability of the structural parameters. No
pooling is performed; the M1-clean welfare baseline remains the
2016 estimates.

*Variant C — Year-out out-of-sample prediction.* The M1-clean
specification is estimated on a training subsample (for instance,
2015 + 2016) and used to predict labour-supply outcomes in a
held-out year (2017). The criterion is whether the predicted
participation, hours, and occupation distributions match the
observed 2017 distributions to a tolerance comparable to the
2016 in-sample fit.

*Variant D — Within-year K-fold cross-validation.* The 2016
households are randomly partitioned into K folds (typically
K = 5 or K = 10). The M1-clean specification is estimated on
K − 1 folds and evaluated on the held-out fold. The procedure is
repeated K times, with summary statistics on parameter stability
across folds and on out-of-fold predictive fit.

Variants A and C represent the most ambitious operational
realisations of the two proposals; Variant B is a more modest
robustness check that draws on additional years without pooling;
Variant D is the conventional machine-learning cross-validation
applied to the existing 2016 sample. The four variants impose
substantially different operational costs and offer substantially
different evidentiary returns, summarised in Table 1.

| Variant | Operational cost | Evidentiary return |
|---|---|---|
| A — Pooled multi-year | High | Improved identification; new methodological territory |
| B — Cross-year replication | Medium | Robustness check on parameter stability |
| C — Year-out prediction | Medium-high | Out-of-sample generalisation evidence |
| D — Within-year CV | Medium | Marginal — does not exploit additional data |

The high-cost variants (A and C) impose construction of MNL
parquets for one or more additional years, which involves
replicating the GSURv2 rebuild work for each new year, replicating
the occupation coding (loc4), replicating the wage construction
and discretisation, and replicating the alternative-set
construction. The walltime of this preparation is substantial: the
original GSUR rebuild for 2016 required several days of design and
implementation work, much of which would carry through to 2015 and
2017 but not without adjustment for year-specific tax-benefit
parameters and data column availability. The estimation walltime
is comparatively small (approximately 350 seconds per start on
2016; multi-year pooled estimation may be one and a half to two
times this).

---

## 3. Variant A — Multi-year pooled estimation

Variant A is methodologically appealing and operationally
expensive. The appeal arises from the substantial increase in
sample size — approximately 12,000–13,000 households when 2015,
2016, and 2017 are pooled — and from the introduction of time
variation that may identify additional parameters or sharpen the
identification of currently weakly identified parameters.

The principal candidate for improved identification under Variant A
is the singles consumption joint-identification limitation
documented in the M0c_b2_GSURv2 verdict §1 V3 and preserved in
the M1-clean verdict §1 V1. The three parameters `beta_c_sm`,
`beta_c_sf`, and `theta_c_singles` exhibit negative-variance
entries in the Hessian-based VCV under the 2016 sample; the
near-singular sub-block reflects insufficient variation in the
singles consumption-leisure tradeoff to identify both the scale
parameters and the Box-Cox curvature parameter simultaneously. A
three-fold increase in singles sample size would not necessarily
resolve this limitation if the underlying identification problem
is structural rather than sample-size-driven, but it would
materially shift the burden of proof: under a 12,000-household
pooled sample, the persistence of the negative-variance pathology
would constitute stronger evidence that the limitation is
structural (i.e., that the model's functional form is
under-identified) rather than sample-size-related.

Against this appeal, Variant A imposes five substantial costs.

First, the replication of the data pipeline for 2015 and 2017
requires re-doing the GSURv2 work for those years. The EUROMOD
FR_2015 and FR_2017 systems differ from FR_2016 in tax-benefit
parameters, in the available labour-market variables, and in
the underlying EU-SILC sample. The GSUR Stage A lookup must be
constructed for each year against year-specific Eurostat data
(`lfst_r_lfu3rt` and `lfst_r_lfsd2pop`), respecting the same NUTS-2
crosswalk and EUROMOD `drgn1` aggregation. The occupation coding
(loc4) must be reconstructed for each year against the EU-SILC
PL051 (ISCO-08 1-digit) and the project-specific 4-category
aggregation. The wage construction and the hours discretisation
must be replicated. Each of these steps was substantial work in
2016 and would consume comparable effort for each additional year.

Second, the pooled-estimation specification requires year fixed
effects in the opportunity block. The natural placement is in the
market-opportunity block, supplementing the seven `drgn1` dummies
with two year dummies (taking 2016 as the reference and adding
indicators for 2015 and 2017). This adds two parameters in the
M1-clean specification, bringing the count to 55. Whether the
year fixed effects belong in the opportunity block alone is itself
a design question. If the wage process exhibits time variation
(real wages grew approximately 0.5 per cent annually over
2015–2017 in France), the wage block requires year-specific
intercepts or a deflation procedure. Three operational choices
present themselves: include year fixed effects in the wage
block (introducing two further parameters), deflate wages to a
common base year (requiring a price index choice), or restrict
attention to within-year wage variation while assuming structural
parameters are time-invariant. None of these choices is innocuous,
and each affects the interpretation of the estimated parameters.

Third, the EU-SILC sample structure across years is partially
overlapping. The EU-SILC longitudinal component operates as a
four-year rotating panel: a household sampled in year *t* may
re-appear in *t* + 1, *t* + 2, and *t* + 3, with annual
sample-rotation cycling new households into the panel. The
2015 + 2016 + 2017 sample therefore contains a non-trivial
proportion of households appearing in two or three of the years.
Treating the pooled sample as if households were independent
across years over-counts identifying information and produces
under-estimated standard errors. The correct treatment is to
cluster standard errors at the household level (which the GAMSPy
solver does not natively support) or to use the cross-sectional
EU-SILC component only (which excludes panel households and
substantially reduces effective sample size). Neither operational
correction is straightforward to implement in the existing
pipeline, and neither has been designed for the M0c family of
specifications.

Fourth, the welfare interpretation of the pooled estimates is
non-obvious. Under the M1-clean welfare framework, the JMP
computes opportunity-driven and preference-driven components of
inequality against a specified reference distribution. With three
years of data, the natural reference distributions include each
year's distribution separately, the pooled distribution, and
constructed counterfactual distributions. The choice among these
options is a substantive welfare-measurement decision that the
project's current welfare-measurement decisions memo (yet
unwritten) would need to address explicitly. The welfare results
under pooled estimation are not simply the average of the three
single-year welfare results; the structural parameters under
pooling are different objects than the single-year parameters,
and the resulting welfare decompositions correspondingly differ.

Fifth, the timing of Variant A relative to the JMP's project
sequence is poor. The M1-clean baseline has only just been
accepted; the M1-naive sensitivity is not yet estimated; the
welfare-measurement decisions memo is not yet written; the
welfare scaffolding is not yet implemented. Inserting a major
pipeline rebuild at this point would delay the welfare track by
approximately the same time as the rebuild itself (six to eight
weeks of additional work) without delivering welfare results
during the rebuild. If multi-year work is ultimately required, it
is more sensibly placed after the welfare scaffolding is in place
and a single-year welfare result has been computed; the multi-year
extension then has a benchmark against which to compare and a
welfare framework against which to be designed.

The recommendation on Variant A is *defer*. The work is
methodologically valuable but is best implemented after the
single-year welfare track is complete, at which point a multi-year
extension would constitute either a JMP extension chapter or a
follow-up paper. Implementation at the current project stage would
displace the welfare track without compensating benefit.

---

## 4. Variant B — Cross-year structural replication

Variant B is the more modest of the two multi-year proposals and
is, in my view, the appropriate operational realisation for the
JMP's robustness architecture. Under Variant B, the M1-clean
specification is estimated separately on the 2015 and 2017
cross-sections, producing two additional parameter vectors that
are compared to the 2016 baseline. No pooling is performed; no
year fixed effects are introduced; no panel-correlation correction
is required; no model redesign is necessary.

The evidentiary content of Variant B is substantial. Cross-year
replication tests whether the structural parameters of the
M1-clean specification are stable across years, which is the
relevant temporal-robustness exposure for a paper whose central
empirical exercise is conducted on a single year. The comparison
yields three independent estimates of each structural parameter,
and the across-year dispersion of these estimates provides a
diagnostic on the empirical credibility of the M1-clean
identification.

Three structural parameters warrant particular attention under
Variant B.

The household leisure-leisure interaction parameter `beta_ll`
(finding R5.1 in the M0c_b2_GSURv2 verdict) carries the JMP's
substantive claim that French couples exhibit strong leisure
complementarity. If `beta_ll` is estimated at approximately 2.6
in 2015, 2016, and 2017, the finding is credibly time-invariant
and supports the JMP's interpretive framing. If `beta_ll` shifts
materially across years, the finding requires re-interpretation
as a year-specific result, with consequences for the JMP's
generalisability claims.

The corrected GSUR coefficient `beta_E_gsur` (M1-clean estimate
−1.329 in 2016) carries the JMP's claim that the demographically
conditional within-region unemployment rate is a substantively
important opportunity shifter. Cross-year replication tests
whether the coefficient is consistent across the three years'
different unemployment environments. The French regional
unemployment rate rose marginally between 2015 (9.4 per cent) and
2016 (9.7 per cent) before declining to 9.0 per cent in 2017,
providing some — modest — temporal variation against which the
parameter's stability can be assessed.

The seven region coefficients `beta_E_drgn2` through
`beta_E_drgn8` test whether the regional employment-opportunity
structure is stable across years. The Île-de-France high-opportunity
finding in 2016 is the substantive content; cross-year replication
tests whether the same finding emerges from 2015 and 2017 data.

The operational cost of Variant B is moderate. The principal
operational task is the construction of MNL parquets for 2015 and
2017, which involves:

(a) Replicating the GSURv2 Stage A lookup construction for each
year. The Eurostat data sources (`lfst_r_lfu3rt`,
`lfst_r_lfsd2pop`, INSEE benchmark) are time-varying and must be
re-extracted for 2015 and 2017. The NUTS-2 crosswalk to EUROMOD
`drgn1` is invariant across years. The validation procedures
(L1–L11 of the GSURv2 v2.1 specification) can be re-applied
without substantial modification.

(b) Replicating the occupation coding for each year. The EU-SILC
occupation variable PL051 is comparable across years; the
project-specific four-category aggregation (loc4) can be applied
identically. Minor revisions may be required if PL051 coding
conventions changed between years.

(c) Replicating the wage construction and hours discretisation.
The wage variables PY010G (employee cash income) and PY010N
(employee gross income) are comparable across years. Wage
deflation is not required under Variant B because each year is
estimated separately. The hours discretisation procedure can be
applied identically.

(d) Re-estimating the M1-clean specification separately on each
year. The estimation walltime is approximately 350 seconds per
start; three starts per year; two additional years (2015 and 2017).
Total estimation walltime is approximately 35 minutes for the
additional years combined. Multistart convergence and
post-estimation diagnostic protocols are unchanged from the 2016
M1-clean run.

(e) Constructing a cross-year comparison report that documents
the parameter-by-parameter comparison across the three years,
flags structural shifts of interest, and provides a robustness
exposure for the JMP's robustness section.

The cost of (a) through (c) is the substantive cost of Variant B.
It is approximately one-third to one-half of the cost that
Variant A would impose, because the model design work is not
required and the pooled-estimation infrastructure (year fixed
effects, panel correction) is not required. The work fits within
an estimated four to six weeks of focused effort, which can be
parallelised with the welfare-measurement decisions memo and the
welfare scaffolding design.

The recommendation on Variant B is *accept, with sequencing
placement after M1-naive verdict and before welfare scaffolding
implementation*. The exposure becomes the JMP's robustness
exposure R10 (cross-year structural replication), supplementing
R2 (M1-clean versus M1-naive, ability-versus-opportunity
partition) as a structural-side robustness exposure. The R10
exposure provides credibility for the M1-clean welfare results
that would be substantially harder to establish on a single-year
basis alone.

---

## 5. Variant C — Year-out out-of-sample prediction

Variant C is methodologically valid but offers less evidentiary
return per unit cost than Variant B. The procedure estimates the
M1-clean specification on a training subsample (for instance, 2015
or 2015 + 2016) and uses the estimated parameters to predict the
labour-supply outcomes in a held-out year (2017). The criterion
is the closeness of the predicted distributions to the observed
distributions in the held-out year.

Two methodological observations bear on the value of Variant C in
the JMP context.

First, the out-of-sample prediction exercise tests the model's
*predictive* generalisation rather than its *welfare-identifying*
generalisation. A model that predicts 2017 labour-supply
outcomes well from 2016-trained parameters demonstrates that the
2016 structural relations transport to 2017; it does not
directly demonstrate that the welfare decomposition computed under
the 2016 estimates would be similar to the welfare decomposition
computed under 2017 estimates. The two questions are related but
not identical. Variant B directly addresses the second question
through cross-year parameter replication; Variant C addresses the
first question through predictive accuracy comparison.

Second, the operational cost of Variant C is essentially the same
as Variant B in terms of data preparation (constructing MNL
parquets for 2015 or 2017) but adds the prediction-comparison
infrastructure. The latter is non-trivial: predicting labour-supply
choices in a year not used for estimation requires applying the
estimated structural parameters to the year-specific alternative
sets, computing predicted choice probabilities, and comparing the
resulting marginal distributions to the observed distributions
using a metric that controls for year-specific compositional
differences in the sample.

A pragmatic compromise is to incorporate a single out-of-sample
prediction exercise within Variant B's cross-year replication
framework. Under this compromise, the structural parameters
estimated in 2016 are used to predict 2017 outcomes; the
comparison provides a single, focused out-of-sample diagnostic
without requiring the full cross-year replication infrastructure.
This is a one-page exercise that can be added to the JMP's
robustness section without substantial additional cost.

The recommendation on Variant C is *partially incorporate within
Variant B*. The full Variant C exercise (separate training and
prediction sets) is not justified by its incremental evidentiary
return; the partial exercise (single-year prediction within the
cross-year replication framework) is a low-cost supplement that
can be added at the same time as Variant B.

---

## 6. Variant D — Within-year K-fold cross-validation

Variant D applies the standard machine-learning cross-validation
procedure to the 2016 sample alone. The procedure partitions the
4,253 households into K folds, estimates the M1-clean
specification on K − 1 folds, and evaluates predictive fit on the
held-out fold. The procedure repeats K times.

Variant D is methodologically uninformative for the JMP's
purposes for two reasons.

First, the 2016 cross-section is small (4,253 households). With
K = 5, each fold contains approximately 850 households, of which
approximately 150 are singles male and 320 are couples. The
single-fold sample size approaches the threshold below which
multistart convergence to a unique optimum cannot be reliably
expected for a 53-parameter specification. The identification
problems documented in the singles consumption sub-block (three
NA standard errors in the 2016 full sample) would be exacerbated
in single-fold estimation; multiple folds might fail to converge
or might converge to parameter vectors with materially different
structure than the full-sample estimates. The K-fold standard-
error inflation would mask rather than illuminate the
underlying identification problems.

Second, the structural-econometric interpretation of K-fold cross-
validation is unclear. In conventional ML applications, cross-
validation provides an unbiased estimator of out-of-sample
predictive risk. In structural applications, where the criterion
is identification of welfare-relevant parameters rather than
predictive accuracy on held-out subsamples, the cross-validation
statistic does not directly map to a JMP-relevant quantity. The
JMP's reader is not asking "does the model predict held-out
households well?" but "are the structural parameters credibly
identified for welfare purposes?" The latter question is better
addressed by Hessian-based identification diagnostics, multistart
convergence checks, joint Wald tests, and cross-year replication
than by within-year K-fold CV.

The recommendation on Variant D is *reject*. The procedure is
operationally expensive (K full estimation runs), methodologically
informative for a question the JMP is not asking, and creates a
real risk of fold-level convergence failures that would generate
noise rather than signal. Within-year robustness is already
adequately addressed by the M1-clean multistart protocol and by
the M1-naive sensitivity exercise; no further within-year cross-
validation is required.

---

## 7. The recommended robustness exposure R10

Variant B — cross-year structural replication — is the recommended
multi-year addition to the JMP. The exposure becomes the
robustness exposure R10 (cross-year structural replication) in
the framework memo's robustness architecture, supplementing the
existing exposures R1 through R9.

The R10 exposure is defined as follows.

*Specification.* M1-clean as accepted in the verdict memo, with
no modification to the structural specification, the parameter
count, or the frozen blocks. Estimated separately on 2015, 2016,
and 2017 cross-sections.

*Sample.* For each year, the equivalent metropolitan France
sample to the 2016 baseline: singles (separated by sex, ages 25
through 65 inclusive, dependent on the year-specific availability)
and couples (same age range). Sample-perimeter decisions
(metropolitan France only via `drgn1 ∈ {1, …, 8}`; exclusion of
the DOM) are preserved across years.

*Data construction.* MNL parquets are constructed for 2015 and
2017 following the GSURv2 v2.1 specification. The GSUR Stage A
lookup is constructed against year-specific Eurostat
`lfst_r_lfu3rt` and `lfst_r_lfsd2pop` data and validated against
the year-specific INSEE national-rate benchmark. The occupation
coding (loc4), wage construction, and hours discretisation are
replicated from the 2016 pipeline with minimal adjustment.

*Estimation protocol.* Three independent starts per year, with
warm-start from the M1-clean 2016 parameter vector; convergence
criterion identical to the 2016 protocol; post-estimation
diagnostics replicated from the M1-clean 2016 deliverables.

*Comparison report.* A cross-year comparison memo reports the
parameter-by-parameter comparison across the three years, with
specific attention to the preferences block (R5.1, R5.2, R5.3,
R5.4, R5.5 findings), the corrected GSUR coefficient (substantively
the within-region unemployment-rate effect), and the seven region
coefficients. Parameter shifts exceeding fifteen per cent in
absolute value between any two years are flagged for substantive
interpretation; shifts within ten per cent are documented as
robustness evidence; shifts between ten and fifteen per cent are
documented with brief commentary.

*Welfare implications.* The cross-year replication does not, in
itself, change the JMP's welfare decomposition. The 2016 M1-clean
estimates remain the welfare baseline; the 2015 and 2017 estimates
provide robustness evidence for the JMP's robustness section. If
the cross-year evidence reveals systematic temporal shifts (e.g.,
`beta_ll` declining over time, or `beta_E_gsur` losing precision
in 2017), these are documented as qualifications to the JMP's
substantive claims but do not require re-doing the main welfare
results.

The R10 exposure is methodologically conservative. It accepts
M1-clean as the working specification, treats the 2016 estimates
as the welfare baseline, and uses 2015 and 2017 data only to
provide robustness evidence on parameter stability. It does not
introduce model redesign, does not require panel-correlation
corrections, and does not alter the welfare interpretation of the
2016 estimates. Its evidentiary content is the cross-year
parameter comparison itself, which is a credibility-strengthening
result for the JMP's main empirical claims.

---

## 8. Sequencing within the project

The R10 exposure is sequenced as follows within the JMP's
project timeline.

1. *M1-clean verdict* — completed (`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md`).

2. *M1-naive implementation* — Claude Code Sonnet task, derived
   from the M1-clean YAML by re-adding `beta_E_educH`. Produces
   the M1-naive estimation report, post-estimation diagnostics,
   and supplementary diagnostics on the 2016 sample. Walltime
   approximately one focused session.

3. *M1-naive verdict* — Claude Project chat task. Documents the
   M1-clean-versus-M1-naive comparison for the JMP's robustness
   exposure R2.

4. *Welfare-measurement decisions memo* — Claude Project chat
   task. Locks the welfare functional, inequality index,
   decomposition method, reference distributions, and gender
   attribution rule. This memo is *methodologically independent
   of R10* and can proceed in parallel with R10 implementation.

5. *R10 implementation, Stage 1 — GSURv2 rebuild for 2015 and
   2017.* Claude Code Sonnet task. Replicates the GSURv2 Stage A
   lookup construction for the two additional years. Estimated
   walltime: one focused session per year, with parallelism
   possible across years.

6. *R10 implementation, Stage 2 — MNL parquet construction for
   2015 and 2017.* Claude Code Sonnet task. Replicates the MNL
   data preparation pipeline (occupation coding, wage
   construction, hours discretisation) for the two additional
   years. Estimated walltime: one to two focused sessions per
   year.

7. *R10 implementation, Stage 3 — M1-clean estimation on 2015 and
   2017.* Claude Code Sonnet task. Re-estimates M1-clean
   separately on each year using the warm-start protocol.
   Estimated walltime: approximately one hour per year.

8. *R10 cross-year comparison memo* — Claude Project chat task.
   Documents the cross-year parameter comparison and the JMP's
   robustness exposure R10.

9. *Welfare scaffolding implementation* — sequenced after items
   3, 4, and 8 are complete. The scaffolding uses M1-clean 2016
   estimates as the welfare baseline and incorporates R2 (from
   item 3) and R10 (from item 8) as robustness exposures.

10. *Welfare-decomposition computation, robustness exposures,
    paper drafting.*

Items 5 through 7 (the R10 implementation stages) can be
parallelised with items 3 and 4 (the M1-naive and welfare-
measurement work) so that the welfare-scaffolding implementation
(item 9) finds all robustness exposures in place. Total
incremental walltime for the R10 exposure is approximately five
to seven weeks of focused work, depending on parallelism with
other tasks.

The sequencing places R10 before welfare scaffolding because the
JMP's robustness section requires R10 evidence to be in hand
before welfare results are presented; placing R10 after welfare
scaffolding would require re-doing welfare computation if the
R10 results revealed material temporal instability. The sequencing
does not place R10 before the welfare-measurement decisions memo
because the decisions memo's methodological content (functional
form, inequality index, decomposition method) is independent of
the cross-year evidence.

---

## 9. What R10 adds to the JMP

The R10 exposure adds three distinct contributions to the JMP's
empirical content.

First, it adds a *temporal-robustness* exposure to the existing
robustness architecture. The current robustness exposures address
gender attribution (R1), ability-versus-opportunity partition
(R2), reference-distribution choice (R3), welfare-measure choice
(R4), inequality-index choice (R5), decomposition-method choice
(R6), subsample (R7), bootstrap (R8), and strong-Roemer
interpretation (R9). None of these directly addresses the
question of whether the JMP's central empirical findings are
temporally stable. R10 fills this gap.

Second, it provides *parameter-stability evidence* that
strengthens the credibility of the welfare results. A welfare
decomposition computed from structural parameters that replicate
across three years carries more empirical weight than one computed
from a single-year estimation. The JMP's reader has a natural
question — "would this result have been different in 2015 or
2017?" — that R10 directly addresses.

Third, it provides a *foundation for future multi-year extensions*
without committing the JMP to multi-year estimation. If the R10
results are favourable (parameter stability across years), the
JMP can credibly claim that its 2016 results are representative
of the broader 2015–2017 period without engaging the pooled-
estimation complications of Variant A. If the R10 results reveal
substantial temporal instability, the JMP can transparently
document this as a qualification and identify multi-year
estimation as a future extension. Either outcome strengthens the
JMP's empirical contribution.

The R10 exposure also positions the project for a possible
follow-up paper. The data infrastructure built for R10 (MNL
parquets for 2015 and 2017, GSURv2 Stage A lookups for those
years) is the precise infrastructure required for any subsequent
multi-year pooled estimation or for an explicit policy-evaluation
exercise across the 2015–2017 period. The investment is
defensible on JMP grounds alone but also generates option value
for future work.

---

## 10. What R10 does not do

The R10 exposure is intentionally limited in three respects.

First, R10 does not perform pooled estimation. The three years
remain separate estimation samples; the 2016 estimates remain the
JMP's welfare baseline. Pooling is methodologically more
demanding (year fixed effects, panel correlation, welfare-
interpretation choices) and is deferred to a possible follow-up
paper or to a later extension chapter.

Second, R10 does not provide formal predictive cross-validation.
A single-year out-of-sample prediction exercise can be added at
low cost (per §5 above), but the full Variant C procedure is not
implemented. Predictive validation is methodologically valid but
addresses a question slightly different from the JMP's primary
welfare-identification question; the marginal evidentiary return
does not justify the additional infrastructure.

Third, R10 does not modify the M1-clean specification. The
specification is locked at the M1-clean SA1-STANDS verdict; R10
applies the same specification to additional years. If the
cross-year evidence reveals that a different specification is
required for 2015 or 2017 — for instance, if the regional
structure of unemployment is substantially different in 2015 — the
finding is documented as a robustness qualification but does not
trigger a re-design of the M1-clean specification.

---

## 11. Immediate next task

The immediate next task is *not* R10. The R10 implementation is
sequenced after the M1-naive verdict and in parallel with the
welfare-measurement decisions memo, per §8. Inserting R10 before
M1-naive would compete with the JMP's ability-versus-opportunity
robustness exposure R2 (per the M1-clean verdict §16) without
materially improving its evidentiary content.

The immediate next task remains the M1-naive implementation
prompt for Claude Code Sonnet, as recommended in the M1-clean
verdict §19. The R10 exposure is added to the project's task
list as a sequenced item to be implemented after the M1-naive
verdict is in place.

Once the M1-naive verdict is complete, the appropriate next chat
task is the welfare-measurement decisions memo, which can be
drafted in parallel with the first Stage of R10 implementation
(the GSURv2 rebuild for 2015 and 2017). The two tasks are
operationally independent.

---

## 12. Operational note

The R10 implementation requires the data infrastructure for 2015
and 2017 to be available. The project memory indicates that the
EUROMOD FR data for 2015 and 2017 is available
(`euromod_fr_2015_2017_standard_income_concepts.csv` and the
related output variable index), but the full MNL pipeline has
not been run for those years. A pre-implementation feasibility
audit is recommended before the R10 implementation prompt is
written: the audit confirms (a) availability of EUROMOD FR_2015
and FR_2017 systems in the project's EUROMOD installation, (b)
availability of EU-SILC microdata for 2015 and 2017 (subject to
licensing constraints), and (c) availability of the Eurostat
denominator and unemployment-rate sources for those years. This
audit can be performed in Claude Code Sonnet as a brief
preparatory step before the full R10 implementation begins.

The audit's findings determine the operational scope of R10. If
the data is available, R10 proceeds as specified above. If
2015 or 2017 data is missing in some respect, R10's scope is
adjusted accordingly — for instance, a two-year (2016 + 2017)
replication may be the operative version if 2015 EU-SILC is
unavailable.

The audit is a low-cost preparatory step and is not itself the
R10 implementation. It is recommended that the audit be performed
before the M1-naive verdict so that R10's scope is known when
the welfare-measurement decisions memo is drafted; the welfare-
measurement decisions memo's treatment of robustness exposures
will benefit from knowing whether R10 is two-year or three-year.
