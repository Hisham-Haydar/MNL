# JMP Welfare-Measurement Decisions Memo v1

Date: 2026-05-19

Specification class: methodological-decisions memo. The memo
articulates the welfare-measurement design choices that govern the
JMP's eventual welfare scaffolding and welfare-decomposition
computation. It does not authorise welfare computation, welfare
scaffolding implementation, canonical MNL promotion, or any
modification of the structural specification.

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the current preferred
  structural baseline, classified SA1-STANDS)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_naive_robustness_verdict_v1.md` (the M1-naive
  robustness exposure)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` (the structural design
  of M1-clean)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the prior baseline
  documenting the singles consumption identification limitation)
- `docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the pooled-estimation roadmap and the SA2 verdict architecture)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  ability/opportunity partition driving the welfare cuts)
- `docs/JMP_literature_positioning_memo_v2.md` (contribution claim
  and closest-paper positioning)

Scope: empirical-JMP welfare-measurement decisions only. The memo
respects the boundary between the empirical JMP and the separate
François Maniquet pure-theory paper on jobs and well-being. The
empirical JMP draws on the conceptual machinery of the theory paper
only through the operationalisations already locked in the framework
memo and the literature-positioning memo; it does not implement
the theory paper, and it does not reproduce its axiomatic results.

---

## 1. Purpose of this memo

This memo locks the welfare-measurement decisions that the JMP's
welfare layer will implement when welfare scaffolding is later
authorised. The intent is to make every methodological choice that
governs the welfare object, the counterfactual construction, the
inequality index, and the decomposition rule explicit *before* code
is written, so that the welfare scaffolding implementation can be
audited against a written design contract rather than discovered
incrementally from code.

The memo is the welfare-side analogue of the M1-clean design memo:
it specifies what the welfare layer must do and on what principled
grounds, and it draws the line between methodological choices that
are normative, methodological choices that are structural, and
methodological choices that are empirical and therefore answerable
to data. The eventual `RURO_welfare_scaffold_design_contract_v1.md`
will translate this memo into a code contract; the eventual
`RURO_welfare_scaffold_verdict_v1.md` will audit implementation
against that contract. This memo precedes both.

The memo does not compute welfare numbers, does not propose
welfare numbers, and does not pre-empt the SA2 verdict on a future
pooled specification. Its scope is the design of the welfare
machinery, not its operation.

---

## 2. Why welfare-measurement decisions must be locked before coding

Three considerations make a written decisions memo a strict
prerequisite for welfare scaffolding implementation.

First, the welfare object is jointly determined by normative
choices and structural-model outputs. The same set of structural
estimates can support several welfare functionals — equivalent
income, equivalent variation, compensating variation, common
utility, type-conditional rank-dependent welfare — and the choice
among them is not pinned down by the structural estimation. Writing
the welfare code before settling these choices invites the code's
implementation defaults to become silent normative commitments. The
JMP's central claim is that the *choice* between opportunity-driven
and preference-driven attribution is informative; that claim is
incompatible with welfare defaults adopted casually inside the
implementation.

Second, the decomposition is the JMP's headline scientific object.
The literature-positioning memo states that the decomposition,
rather than estimation or ranking, is the paper's main contribution.
Decomposition is sensitive to the welfare functional, the inequality
index, the reference distribution, and the order of factor removal.
The welfare scaffolding must therefore be designed so that
alternative welfare functionals, alternative inequality indices, and
alternative attribution rules can be exercised on the *same*
structural estimates without rewriting the welfare layer. This kind
of modular design must be planned in writing; it does not emerge
from incremental coding.

Third, the structural baseline is currently single-year M1-clean
but may, under an SA2-STANDS verdict, be replaced by a pooled
specification in the future. The welfare layer must accommodate
both possibilities without architectural rewriting. Designing the
welfare layer to be specification-agnostic at the input boundary,
and decomposition-coherent at the output boundary, is a design
decision rather than an implementation detail.

For these reasons, welfare-measurement decisions work is authorised
now, while welfare scaffolding implementation and welfare-
decomposition computation both remain explicitly deferred.

---

## 3. Primary welfare object

The JMP's primary welfare object is *household equivalent income*,
denoted $\Omega_i$. Concretely, $\Omega_i$ is the level of household
disposable income that, evaluated under a fixed reference job and a
fixed reference opportunity set, would deliver to household $i$ the
same level of attained utility — under the household's *own*
preferences — that the household attains in its actual choice
problem. The object is money-metric, household-indexed, and
preference-respecting in the same sense as Decancq–Fleurbaey–
Schokkaert (2015) and Fleurbaey–Maniquet (2017).

Three features of this choice deserve emphasis.

First, $\Omega_i$ is computed at attained utility rather than at
maximum utility on a fixed budget constraint. In a latent-jobs
model, the appropriate concept of attained utility is the expected
maximum utility over the household's sampled feasible job set,
which in the RURO architecture is the log-sum-exp of utilities over
that feasible set. This object inherits the household's preferences,
the household's wages, the household's opportunity density, and the
household's tax-benefit environment.

Second, $\Omega_i$ is preference-respecting at the level of the
single household: increasing the income of a household that, under
its own preferences, is indifferent between actual and reference
situations changes $\Omega_i$ in the direction the household
itself would endorse. Preference-respecting does not mean
"preferences are responsibility-relevant"; the responsibility
classification is a separate normative step downstream of the
welfare measurement.

Third, $\Omega_i$ is conditional on the household's *actual*
opportunity environment unless the welfare calculation is
explicitly counterfactual. The conditioning is what permits
opportunity heterogeneity to leave a measurable trace in welfare
inequality; equalising opportunities is one of the counterfactual
operations the welfare layer is required to support.

The notation $\Omega_i$ is used throughout the memo for the
welfare object; the term "equivalent income" and the term
"money-metric well-being" are used interchangeably for the same
object except where literature-specific usage demands one or the
other.

---

## 4. Why equivalent income / money-metric well-being is preferred

Equivalent income is the natural primary welfare object for the JMP
for four reasons that, taken together, exclude the alternatives.

First, it respects individual preferences. The personal-preference
principle of Decancq–Fleurbaey–Schokkaert (2015) and the
preference-respecting tradition of Fleurbaey–Maniquet (2017) both
identify equivalent income as the welfare metric that uses each
household's own preferences for intra-personal comparisons while
permitting a transparent normative choice for interpersonal
comparability — namely, the reference job and reference opportunity
set. This is in contrast to common-utility welfare, which obtains
interpersonal comparability by imposing identical preferences and
absorbs heterogeneity into the comparability assumption rather than
making it visible.

Second, equivalent income is well-defined in a latent-jobs random-
utility model. The reference-job conditioning permits a single
income equivalent to be computed from the household's
choice-probability-implied utility level. This is the operational
sense in which equivalent income inherits the structural-model
output cleanly; equivalent variation and compensating variation
require defining the welfare object relative to a counterfactual
state of the world, and although they can be defined in this model,
they are derivative of equivalent income rather than primary to it.

Third, equivalent income carries opportunity information through the
reference opportunity set. The literature-positioning memo identifies
the weakness of Bargain et al. (2013) precisely as the absorption of
opportunity into the residual labelled "preferences"; equivalent
income, conditional on a reference opportunity set that is
explicitly chosen rather than implicitly absorbed, is the welfare
object that can isolate the opportunity component of welfare
inequality. This is the central conceptual reason for the choice.

Fourth, equivalent income is the welfare object that the closest
substantive competitor — Jacquet, Jia and Thoresen (2026) — uses
to construct the responsibility-sensitive cut on Norwegian data.
The JMP's primary welfare object is methodologically aligned with
the closest competitor for comparability, while the JMP's
decomposition object diverges from the competitor's two-way
welfare contrast and instead produces an order-independent
attribution.

The four reasons are jointly sufficient. Each one alone would not
exclude equivalent variation; together they identify equivalent
income as the primary object and equivalent variation as a
secondary sensitivity.

---

## 5. Why EV/CV are secondary here

Equivalent variation (EV) and compensating variation (CV) are
welfare-difference concepts. They measure the income transfer
required to compensate a household for a change between two states
of the world. The JMP's primary scientific object is not a policy
counterfactual but the inequality decomposition of the welfare
*level*; the appropriate welfare object for inequality of a level
is a level, not a difference.

EV and CV nonetheless retain a secondary role. First, EV/CV are
the standard objects in the structural-microsimulation literature
(Aaberge–Colombino–Strøm 1999; Aaberge–Dagsvik–Strøm 1995), and
the JMP's results should be intelligible to that audience. Second,
the de Palma–Kilani log-sum-exp adjustment for CV/EV in discrete-
choice models is the same machinery that produces the equivalent-
income level, so an EV/CV side-calculation is computationally
inexpensive once the equivalent-income calculation is in place.
Third, where the JMP examines the welfare consequences of an
opportunity-equalising counterfactual (§14), an EV/CV interpretation
of the counterfactual gain is a useful translation device.

The welfare scaffolding is therefore designed to compute equivalent
income as the primary output and to expose EV/CV as a secondary
output. The decomposition operates on equivalent income; the
EV/CV-based decomposition is a robustness exercise (R4 in the
framework memo). EV/CV is not the headline welfare object.

---

## 6. Reference bundle

The reference bundle is the consumption–leisure–job-attribute point
at which the household's equivalent income is evaluated. The JMP
locks the reference bundle as follows.

The reference job is a job with a representative consumption level
$c^*$ and a representative leisure level $\ell^*$. The values
$(c^*, \ell^*)$ are not pinned down by the structural model; they
are normative choices, made by the analyst, and reported transparently.

The JMP's *primary* reference bundle uses the median consumption
and the median leisure of the working-age sample, computed
separately by household type (singles male, singles female,
couples), within the operational structural baseline. The choice of
median rather than mean is consistent with the framework memo §6
and is preferred for robustness to outliers; the choice of
type-conditional rather than pooled median respects the differing
budget constraints faced by different household types.

The JMP's *secondary* reference bundles, exercised as sensitivities,
are: (i) mean rather than median consumption and leisure; (ii) the
"best-available" reference of high consumption and moderate leisure
(framework memo §6 sensitivity); and (iii) a single common
reference bundle pooled across household types, which collapses the
type-specific reference and is informative for understanding the
contribution of type-conditioning to the welfare ranking.

These reference choices are normative in the strict sense that no
data-driven argument selects among them. The decomposition magnitudes
will depend on the choice; the JMP reports the dependence rather
than concealing it. This is explicit normative bookkeeping.

---

## 7. Reference job

The reference job is the labour-supply state — hours, wage,
occupation, employment status — at which equivalent income is
evaluated. The reference job is logically separate from the
reference bundle: $(c^*, \ell^*)$ specifies the welfare-evaluation
point in consumption–leisure space; the reference job specifies
the labour-market state that produces that point.

The JMP's *primary* reference job is full-time employment at the
median full-time wage, computed by household type and gender within
the operational structural baseline. This choice is consistent with
the standard equivalent-income tradition (Decancq–Fleurbaey–
Schokkaert 2015), and it is interpretable as the labour-market
state of a "representative" worker against which other workers'
welfare levels are anchored.

The choice of full-time employment as the reference job is
normative: it commits the JMP to evaluating welfare at a labour-
market state where the household is unconstrained by employment
restrictions. This is the appropriate primary choice because the
opportunity component of welfare inequality is *defined* relative
to a reference state in which opportunities are not binding. The
alternative — taking a non-employment or part-time reference job —
would conflate the reference state with the opportunity-restricted
state and would obscure the decomposition.

The JMP's *secondary* reference jobs, exercised as sensitivities,
are: (i) the household's *actual* labour-supply state (which
collapses the reference and the actual job and produces an EV-style
object); (ii) a part-time reference job at the median part-time
wage; and (iii) the reference job under the household's gender-
specific occupation rather than under a uniform full-time
employment label.

The reference job and the reference bundle are *jointly* specified
in the welfare scaffolding code: $(c^*, \ell^*)$ determines where in
consumption–leisure space welfare is evaluated, and the reference
job determines the labour-market environment that produces that
point. The two must be mutually consistent; the welfare layer is
responsible for enforcing the consistency.

---

## 8. Reference opportunity set

The reference opportunity set is the feasible job set under which
the equivalent-income calculation is performed for the
counterfactual welfare objects. The reference opportunity set is
the central locus of the JMP's opportunity-equalisation operation;
it is where the opportunity-driven component of welfare inequality
is constructed.

The JMP's *primary* reference opportunity set is the feasible job
set that the household would face if it were endowed with the
median values of the opportunity-block covariates entering
$q(x_{\text{opp}})$ in the structural specification. Under the
M1-clean baseline, these covariates are: the corrected GSUR
(regional sex-specific education-conditional unemployment rate), the
seven NUTS-1 region dummies, and the gender-on-arrival coefficient
under the chosen gender-attribution rule. The "median" opportunity
covariates are: median GSUR, modal region (reference NUTS-1
category), and gender held at its actual value (under the M1-clean
default, which treats gender-on-arrival as opportunity under the
G4 A3 attribution rule).

This primary reference is a *level reference*. It is not the
unconstrained opportunity set; it is the median opportunity set. The
choice respects the framework memo §6 robustness preference for
medians and is interpretable as "the opportunity set faced by the
typical household." An alternative — a *maximal* reference
opportunity set, in which all opportunity covariates are set to
their best-available values — is exercised as a sensitivity and
corresponds to an upper bound on what opportunity equalisation
could achieve.

The reference opportunity set determines the magnitude of the
opportunity-driven component of welfare inequality. The reference is
therefore a substantive normative commitment, and the JMP must
report decomposition magnitudes under the primary reference and
under the sensitivity references in the same table.

The reference opportunity set under a future pooled SA2-promoted
baseline is described in §13 below; the year-pooling question
materially affects the construction of the reference and is
addressed explicitly.

---

## 9. Treatment of preferences

Preferences enter the structural model through (i) the Box-Cox
consumption and leisure curvature parameters, (ii) the age and
children shifters of leisure, (iii) the leisure-leisure interaction
parameter $\beta_{ll}$, (iv) the random Fréchet preference shock,
and (v) gender-on-utility coefficients where present. Under the
framework memo §2 mapping, all five components are classified as
preferences. M1-clean's structural amendment does not alter this
classification.

The welfare layer treats preferences as preference-respecting at
the household level and as responsibility-relevant for the
*primary* decomposition. This is the Dworkinian-weak position of
the framework memo §1: individuals are not held responsible for
opportunity differences, but they are held responsible for the
preferences with which they engage with their feasible jobs.

The welfare layer reports a *secondary* decomposition under the
strong-Roemer position, in which ability differences are also
classified as compensation-relevant (framework memo §1, R9). The
strong-Roemer alternative bears on the *ability* classification,
not the preference classification; preferences remain
responsibility-relevant under both positions. The JMP's robustness
exposure on this dimension is therefore an ability-classification
robustness, not a preference-classification robustness.

The welfare-decomposition output reports the preference contribution
to total welfare inequality as the residual after opportunity
equalisation and ability equalisation. Under the primary attribution
rules, this residual is the responsibility-relevant component of
welfare inequality. Under the strong-Roemer alternative, the
preference contribution is the *only* responsibility-relevant
component, and the opportunity + ability sum is the compensation-
relevant component. The welfare layer reports both attributions
side by side in the robustness table.

The classification of preferences is normative. The structural
model identifies preference parameters; it does not identify their
normative status. The welfare layer makes the normative status
explicit.

---

## 10. Treatment of opportunities

Opportunities enter the structural model through the market-
opportunity block $q(x_{\text{opp}})$ and through the hours block
$g_2(h)$. Under the M1-clean specification, the market-opportunity
block contains the corrected GSUR, the seven NUTS-1 region dummies,
gender-on-arrival, and an intercept; the hours block contains
gender-specific focal-point parameters. The occupation block
$O^{\text{Occ}}$ is also classified as opportunity in the framework
memo §2 (occupation availability conditional on an offer).

Under the framework memo's primary attribution rules, all of these
covariates contribute to the *opportunity* component of the
decomposition. Under the gender attribution rules A1, A2, A3, the
gender-on-arrival coefficient moves between the opportunity and
ability classifications; the welfare layer reports the decomposition
under all three rules so that the reader can adopt the position
they find most defensible.

The welfare-decomposition operation that constructs the
opportunity-equalised counterfactual welfare distribution
$\Omega_i^{\text{opp-eq}}$ sets all opportunity covariates to their
reference-opportunity-set values (§8) while holding ability
covariates, preference parameters, and the random preference shock
at their actual realisations. The difference between the inequality
of $\Omega_i^{\text{actual}}$ and the inequality of
$\Omega_i^{\text{opp-eq}}$ is the opportunity contribution to
welfare inequality under the ordered-removal decomposition. Under
the Shapley decomposition, the opportunity contribution is the
average over all permutations of factor-removal orderings.

The framework memo §2 already commits to (i) removing
$\beta_{E\,\text{educH}}$ from the opportunity block under M1-clean
(implemented in the current baseline) and (ii) reporting M1-naive
as a sensitivity that quantifies the cost of suspending the
partition. The M1-naive verdict confirms that the partition decision
is not overturned by the M1-naive evidence; M1-clean remains the
preferred baseline and M1-naive is reported as a robustness
exposure, not as a competing primary baseline.

The opportunity block under a future pooled SA2-promoted baseline
would additionally include year fixed effects (multi-year memo §7
baseline; §7 E4 sensitivity for wage-block year effects). The
welfare layer's opportunity-equalisation operation under that
configuration would set year fixed effects to their reference
value as well. The pooled-baseline case is addressed in §13 below.

The classification of opportunities is normative in the same sense
as the classification of preferences: the structural model
identifies the opportunity-block coefficients, but it does not
identify their normative status. The framework memo settles the
classification, and the welfare layer respects the settlement.

---

## 11. Treatment of ability

Ability enters the structural model through (i) education
($\beta_{w\,\text{educL}}$, $\beta_{w\,\text{educH}}$),
(ii) potential experience ($\beta_{w\,\text{pexp}}$,
$\beta_{w\,\text{pexp}^2}$), (iii) gender-on-wage (where present),
and (iv) the wage-dispersion parameter $\sigma$. All four enter the
wage block $g_1(w; x_w)$, where the framework memo §2 classifies
education and potential experience as ability, gender-on-wage as
ability under attribution rule A1 or as ability/opportunity-split
under A3, and $\sigma$ as shared.

The welfare layer treats ability as compensation-relevant under
the *strong-Roemer* alternative and as responsibility-relevant
under the *weak-Dworkin* primary attribution. The framework memo §1
commits to the weak position as the empirical default, with the
strong position reported as a robustness exposure.

The welfare-decomposition operation that constructs the ability-
equalised counterfactual welfare distribution
$\Omega_i^{\text{abil-eq}}$ sets all ability covariates to their
reference values while holding opportunity covariates, preference
parameters, and the random preference shock at their actual
realisations. The reference values for ability covariates are the
median values by household type and gender, consistent with the
framework memo §6.

The ability classification interacts with the gender attribution
rule. Under A1, gender-on-wage is ability and is equalised when
ability is equalised. Under A2, gender-on-wage is opportunity and
is equalised when opportunity is equalised. Under A3, the
ability-equalisation operation equalises the ability portion of
gender-on-wage (40 per cent of the coefficient under the Blau–Kahn
anchor), and the opportunity-equalisation operation equalises the
opportunity portion (60 per cent). The welfare layer enforces this
joint dependence; the welfare scaffolding code must accept the
attribution rule as an input parameter and adjust the equalisation
operations accordingly.

The ability classification, like the opportunity and preference
classifications, is normative. The framework memo settles it and
the welfare layer respects the settlement.

---

## 12. Mapping RURO estimates into welfare objects

The structural estimates from the operational baseline — currently
the M1-clean parameter vector at LL = $-6487.5522$, with the
GSURv2 MNL parquets as the operative data source — enter the
welfare layer as the parameter vector $\hat{\theta}$. The welfare
layer's input boundary accepts $\hat{\theta}$ together with the
opportunity covariates $x_{\text{opp},i}$, the ability covariates
$x_{w,i}$, and the preference shifters for household $i$, and
returns the equivalent-income welfare object $\Omega_i$.

The mapping is the standard log-sum-exp construction for discrete-
choice random-utility models. The household's choice-probability-
implied attained utility under the actual feasible job set is
computed from $\hat{\theta}$, the sampled feasible job set, the
opportunity density $q(x_{\text{opp},i})$, the wage density
$g_1(w; x_{w,i})$, the hours density $g_2(h)$, the occupation
mechanism $O^{\text{Occ}}$, the tax-benefit function (EUROMOD), and
the household's deterministic utility function. The equivalent
income $\Omega_i$ is the income level that, at the reference job
and reference opportunity set, produces the same attained utility
under the household's preferences.

The welfare-layer architecture is specification-agnostic at the
input boundary. The same architecture must accept (i) the single-
year M1-clean parameter vector and the GSURv2 MNL data, and (ii) a
future pooled-specification parameter vector and the multi-year
stacked data. The welfare layer's mapping from $\hat{\theta}$ to
$\Omega_i$ does not depend on which baseline is operative; the
only specification-dependent component is the opportunity-block
covariate list, which the welfare scaffolding reads from the YAML
specification of the baseline rather than hard-codes.

The pseudoinverse-based standard errors on the singles consumption
parameters ($\beta_{c,sm}$, $\beta_{c,sf}$, $\theta_{c,\text{singles}}$),
documented in the M0c_b2_GSURv2 verdict §8 as a known structural
limitation inherited unchanged by M1-clean, enter the welfare layer
as a known sensitivity exposure rather than as a hard constraint.
The welfare-layer treatment is specified in §22 below.

The welfare layer does *not* re-estimate the structural model. It
operates on $\hat{\theta}$ as a fixed input. Inference uncertainty
on $\hat{\theta}$ enters the welfare layer through the bootstrap
re-estimation procedure (§21); the welfare-layer code is invoked
once per bootstrap replicate, not internally re-fitted within a
single welfare calculation.

---

## 13. Baseline welfare distribution

The baseline welfare distribution is the cross-sectional
distribution of $\Omega_i^{\text{actual}}$ across households in the
operational structural baseline. Under the current preferred
baseline `ruro_occ_M1_clean`, the baseline welfare distribution is
the France 2016 distribution of household equivalent incomes
across the singles male, singles female, and couples sub-samples.

The baseline welfare distribution is the distribution against which
the counterfactual distributions (§§14–16) are compared in the
decomposition. Its construction is therefore the first operational
step of the welfare layer and must be specified before the
counterfactual operations can be defined.

The pooled-specification case raises a substantive open question
that the multi-year memo §14 O2 explicitly defers to this memo.
Under a hypothetical SA2-STANDS verdict promoting a pooled
specification to the primary baseline, the baseline welfare
distribution can be: (a) the pooled distribution across all
included years; (b) a single year's distribution (likely 2016 for
continuity with the M1-clean baseline); or (c) the 2016
distribution reweighted to reflect the pooled household composition.

The JMP's *primary* choice in the pooled case is (b): the baseline
welfare distribution is the 2016 distribution computed from the
pooled $\hat{\theta}$ but evaluated on the 2016 cross-section.
Three reasons support this choice. First, continuity with the
single-year M1-clean baseline is preserved; reported magnitudes
remain comparable across the SA1-STANDS and the hypothetical
SA2-STANDS regimes. Second, the 2016 cross-section is the year for
which the JMP's narrative empirical setting (the France 2016
couples and singles prototype of the literature-positioning memo
§7) is constructed. Third, the welfare-decomposition magnitudes
are dominated by cross-sectional variation in opportunities,
ability, and preferences rather than by temporal variation in
those quantities; evaluating on a single year focuses the
decomposition on the cross-sectional welfare question that the JMP
asks.

The *secondary* choices, exercised as sensitivities under the
pooled regime, are (a) and (c). Option (a) reports the
decomposition on the full pooled cross-section and is the natural
sensitivity for understanding how much temporal variation in
opportunities contributes to total welfare inequality. Option (c)
is reweighted-2016 and is the natural sensitivity for checking the
robustness of the cross-sectional decomposition to differences in
household composition between 2016 and the pooled sample.

Under the current single-year M1-clean baseline, the question of
choosing among (a), (b), and (c) does not arise: the baseline is
the 2016 cross-section directly. The welfare scaffolding code must
be designed to handle both regimes (single-year and pooled) at the
input boundary; the baseline-distribution choice under the pooled
regime is settled here in advance so that the implementation does
not need to make the choice in code.

---

## 14. Opportunity-equalized counterfactual

The opportunity-equalised counterfactual welfare distribution
$\{\Omega_i^{\text{opp-eq}}\}_i$ is the central counterfactual of
the JMP. It is the distribution of household equivalent incomes
that would obtain if every household faced the reference
opportunity set defined in §8, while retaining its actual ability
covariates, its actual preference parameters, and its actual
random preference shock.

Operationally, the opportunity-equalisation operation sets the
opportunity-block covariates in the welfare-layer input to the
reference values: median GSUR, modal NUTS-1 region (with all seven
region dummies set to the reference category), and — under the
gender attribution rule — gender-on-arrival held or equalised
according to the rule. The structural parameter vector
$\hat{\theta}$ is unchanged; only the covariate inputs are
modified. The welfare layer recomputes $\Omega_i^{\text{opp-eq}}$
for each household under these counterfactual covariates.

The inequality of $\Omega_i^{\text{opp-eq}}$ is the welfare
inequality that would remain if the opportunity dimension were
eliminated. The opportunity contribution to total welfare
inequality is the difference between $I(\Omega_i^{\text{actual}})$
and $I(\Omega_i^{\text{opp-eq}})$ under the ordered-removal
decomposition. Under the Shapley decomposition, it is the average
of analogous differences across all factor-removal orderings.

The opportunity-equalised counterfactual is the operationalisation
of the JMP's central research question: *how much of observed
inequality in money-metric well-being is attributable to unequal
job opportunities*. The magnitude of the opportunity contribution
is the headline number of the paper. The welfare layer must
therefore produce $\Omega_i^{\text{opp-eq}}$ as a primary output
and must support sensitivity recomputations under the alternative
reference opportunity sets specified in §8.

The opportunity-equalisation operation under a future pooled SA2-
promoted baseline includes the year fixed effects in the
opportunity covariate list (multi-year memo §7); the welfare layer
sets year fixed effects to their reference value (year 2016 under
the primary baseline-distribution choice of §13) when constructing
the opportunity-equalised counterfactual. This implementation
detail is settled here so that the welfare scaffolding does not
need to make the choice in code.

---

## 15. Ability-equalized counterfactual

The ability-equalised counterfactual welfare distribution
$\{\Omega_i^{\text{abil-eq}}\}_i$ is the distribution of household
equivalent incomes that would obtain if every household faced the
reference ability covariates (median education, median potential
experience, gender held or equalised under the gender attribution
rule), while retaining its actual opportunity covariates, its
actual preference parameters, and its actual random preference
shock.

The ability-equalisation operation is structurally analogous to the
opportunity-equalisation operation but operates on the ability-
block covariates that enter the wage density $g_1(w; x_w)$. The
welfare layer recomputes $\Omega_i^{\text{abil-eq}}$ for each
household under the counterfactual ability covariates.

The ability-equalised counterfactual carries a distinct normative
interpretation under the two attribution positions. Under the
weak-Dworkin primary attribution (framework memo §1), the
inequality difference $I(\Omega_i^{\text{actual}}) -
I(\Omega_i^{\text{abil-eq}})$ measures the ability-driven component
of welfare inequality, which is *not* compensation-relevant: it is
reported as informational but is not part of the JMP's primary
opportunity-driven inequality number. Under the strong-Roemer
alternative (R9), the ability component is added to the opportunity
component to produce the alternative compensation-relevant
inequality number. The JMP reports both under separate columns of
the decomposition table.

The ability-equalised counterfactual is also informative for the
sensitivity exposure provided by the M1-naive specification.
Because M1-naive places $\beta_{E\,\text{educH}}$ in the
opportunity block, education enters both the opportunity-
equalisation operation (through M1-naive's opportunity covariate
list) and the ability-equalisation operation (through both M1-clean's
and M1-naive's wage covariates). The M1-naive welfare decomposition
under the strong-Roemer alternative is therefore numerically close
to the M1-clean strong-Roemer decomposition, with the difference
indicating how the partition assignment of education redistributes
inequality between opportunity and ability components without
affecting the responsibility-sensitive sum.

---

## 16. Preference-neutralized counterfactual

The preference-neutralised counterfactual welfare distribution
$\{\Omega_i^{\text{both-eq}}\}_i$ is the distribution of household
equivalent incomes that would obtain if every household faced both
the reference opportunity set and the reference ability covariates,
while retaining only its actual preference parameters and its
actual random preference shock.

The preference-neutralised counterfactual is the residual after
both opportunity and ability equalisation. The inequality of
$\Omega_i^{\text{both-eq}}$ is the welfare inequality attributable
to preference heterogeneity alone, under the JMP's structural
mapping of preferences to the consumption and leisure curvature
parameters, the leisure shifters, the leisure-leisure interaction,
gender-on-utility, and the random Fréchet shock.

The preference-neutralised counterfactual is *not* a strong claim
that preferences are wholly responsibility-relevant. It is a
structural attribution: it isolates the welfare-inequality variance
that the structural model attaches to preference-block parameters
and shocks. The normative classification of this residual is
specified separately by the attribution position (weak-Dworkin or
strong-Roemer).

The preference contribution to total welfare inequality is
$I(\Omega_i^{\text{both-eq}})$ under the ordered-removal
decomposition with opportunity and ability removed first. Under
the Shapley decomposition, the preference contribution is the
average of analogous residuals across all factor-removal orderings.

The labelling "preference-neutralised" is *deliberately distinct*
from "preference-equalised". Equalising preferences would require
collapsing the heterogeneous preference parameters to a common
value, which would be a common-utility-function operation alien to
the JMP's preference-respecting design. The JMP does not perform
that operation. The "neutralisation" instead refers to the
residualisation of welfare inequality after the opportunity and
ability dimensions have been equalised; what remains is the
preference contribution.

This is the central conceptual reason the JMP's primary welfare
object is equivalent income rather than common-utility welfare:
the preference-respecting structure permits the preference
contribution to be reported as the residual after opportunity and
ability equalisation, without ever requiring preferences themselves
to be normalised across households.

---

## 17. Inequality index choice

The inequality index is the function that maps a welfare
distribution to a scalar inequality measure. The JMP's *primary*
inequality index is the Gini coefficient of the household
equivalent-income distribution. The Gini is chosen because (i) it
is the index that the literature most consistently uses for cross-
sectional welfare-inequality reporting (Aaberge–Colombino–Strøm
1999; Bargain et al. 2013); (ii) it is bounded between zero and one
and admits transparent interpretation; (iii) it is differentiable
in the welfare distribution at any non-degenerate point, which is
useful for bootstrap inference; and (iv) it is the index used in
the closest substantive competitor (Jacquet, Jia and Thoresen
2026), permitting like-for-like comparison of magnitudes.

The JMP's *secondary* inequality indices, exercised as
sensitivities, are: (i) the squared coefficient of variation
$CV^2$; (ii) the mean log deviation (Theil L); and (iii) the
Atkinson index at an inequality-aversion parameter $\varepsilon = 1$
and at $\varepsilon = 2$. The sensitivities are the framework memo
§8 R5 robustness exposure.

The choice of Gini as the primary index is normative. Different
indices weight different parts of the welfare distribution
differently; Gini is sensitive to the middle of the distribution,
$CV^2$ is sensitive to the upper tail, and the mean log deviation
is sensitive to the lower tail. The opportunity contribution to
welfare inequality may differ in magnitude across indices, and the
JMP reports the dependence. This is explicit normative bookkeeping
analogous to the reference-bundle bookkeeping of §6.

The inequality index is computed on each of the four welfare
distributions: $\Omega_i^{\text{actual}}$,
$\Omega_i^{\text{opp-eq}}$, $\Omega_i^{\text{abil-eq}}$, and
$\Omega_i^{\text{both-eq}}$. The differences among these four index
values, weighted by the decomposition rule (§18), produce the
factor contributions to welfare inequality.

A specific consequence of the Gini choice is that the Atkinson-
index sensitivities permit a transparent translation between the
JMP's responsibility-sensitive framing and the welfare-economics
tradition of inequality-averse welfare measurement. This
translation is informative but is not the JMP's primary mode of
reporting.

---

## 18. Decomposition rule

The decomposition rule allocates the difference between total
welfare inequality $I(\Omega^{\text{actual}})$ and the
preference-contribution residual $I(\Omega^{\text{both-eq}})$
across the opportunity and ability factors (under the three-way
decomposition of the framework memo) or across the opportunity and
non-opportunity factors (under the two-way collapse).

The JMP's *primary* decomposition rule is the Shapley-Shorrocks
rule (Shorrocks 2013). The rule averages the marginal contribution
of each factor across all orderings of factor removal, producing
an order-independent attribution. Three considerations support the
choice. First, the Shapley rule is the order-independent rule
canonically used in the inequality-decomposition literature
(Shorrocks 2013; Bourguignon–Ferreira–Menéndez 2007; Ferreira–
Gignoux 2011). Second, the literature-positioning memo identifies
the order-independent decomposition as the central methodological
contribution that distinguishes the JMP from the closest
substantive competitor. Third, the Shapley rule resolves the
interaction-term allocation problem that the framework memo §5
flags under the ordered-removal alternative.

The JMP's *secondary* decomposition rule, exercised as a
robustness exposure (framework memo §8 R6), is the ordered-removal
rule. Under ordered removal, the opportunity contribution is
$I(\Omega^{\text{actual}}) - I(\Omega^{\text{opp-eq}})$, the
ability contribution is $I(\Omega^{\text{opp-eq}}) -
I(\Omega^{\text{both-eq}})$, and the preference contribution is
$I(\Omega^{\text{both-eq}})$. The order matters: an alternative
ordered removal with ability first would produce different
contributions. The JMP reports the dependence on ordering as a
robustness check on the Shapley result.

The Shapley decomposition under the JMP's three-way attribution
(opportunity, ability, preference) requires averaging over $3! = 6$
orderings. Under the two-way attribution preferred by the weak-
Dworkin position (opportunity-or-ability versus preference), the
Shapley decomposition collapses to a two-factor average over $2! =
2$ orderings, which is equivalent to the ordered-removal rule. The
welfare layer is designed to compute both the three-way and the
two-way decompositions on the same welfare distributions.

The decomposition rule, like the inequality index, is normative.
The JMP reports the Shapley decomposition as the primary result and
the ordered-removal decomposition as a robustness exposure. The
two should produce qualitatively similar headline magnitudes if the
opportunity-ability interaction is small relative to the main
effects; the JMP will report whether this is so.

---

## 19. Treatment of interactions

Interactions among opportunity, ability, and preference factors are
generic in any structural-decomposition setting. The framework
memo §5 flags the opportunity-ability interaction as the principal
substantive interaction: educated workers may also tend to live in
high-employment regions, so equalising both factors removes more
inequality than the sum of equalising each separately.

The JMP's treatment of interactions is structural rather than
ad-hoc. The Shapley-Shorrocks decomposition (§18) allocates
interaction terms across factors by averaging marginal
contributions over all orderings; the interaction does not appear
as a separate column of the decomposition table under the Shapley
rule but is dissolved into the factor contributions.

Under the ordered-removal decomposition (the secondary rule), the
interaction term *does* appear as a separate quantity: it is the
difference between the sum of single-factor contributions and the
total inequality reduction. The framework memo §5 commits to
reporting this interaction term explicitly under the ordered-
removal rule rather than allocating it. The welfare layer must
output the interaction term as a separate quantity under the
ordered-removal decomposition; under the Shapley decomposition, the
interaction term is reported as $|I^{\text{Shapley}} -
I^{\text{ordered}}|$ for each factor as a diagnostic.

The interaction between gender attribution and the opportunity/
ability classification is a separate matter, handled by the gender
attribution rules (A1, A2, A3) of the framework memo §4. The
welfare layer reports the decomposition under each attribution
rule separately; gender interactions are not pooled across
attribution rules.

The interaction between the M1-clean and M1-naive opportunity-block
specifications produces a similar reporting requirement. The JMP
reports the Shapley decomposition under the M1-clean baseline as
the primary result; the M1-naive decomposition is reported as a
robustness exposure (framework memo §8 R2) under the same
attribution rules. The numerical difference between the two
decompositions is the "ability-mediated opportunity" of the
framework memo §3 — the inequality that the older RURO literature
attributes to opportunity but that the JMP attributes to ability
through the wage channel.

---

## 20. Sensitivity welfare measures

The framework memo §8 R4 specifies the welfare-measure sensitivity
as the EV/CV alternative to equivalent income. The JMP locks the
following sensitivity welfare measures.

First, *compensating variation* (CV). For each household, CV is the
income transfer required to make the household indifferent between
its actual opportunity environment and the reference opportunity
environment, computed under the household's own preferences. CV is
a welfare-difference object and is informative for the
opportunity-equalisation counterfactual specifically; it
complements the welfare-level (equivalent income) reporting.

Second, *equivalent variation* (EV). For each household, EV is the
income transfer required to make the household indifferent between
the reference opportunity environment and its actual environment.
EV and CV differ when the reference state is genuinely
counterfactual; the difference vanishes when the reference and
actual states coincide.

Third, an *atemporal-Atkinson* equivalent. For each household, the
Atkinson-equivalent income at $\varepsilon$ is the income level
that, under the household's own preferences, produces an Atkinson-
weighted utility equal to the household's actual utility. The
Atkinson-equivalent income is the welfare object that ties the
welfare measurement directly to the inequality index when the
inequality index is the Atkinson index at $\varepsilon$. The
welfare layer reports the Atkinson-equivalent income at
$\varepsilon = 1$ and $\varepsilon = 2$ as a sensitivity.

The three sensitivity welfare measures are computed on the same
counterfactual covariate inputs as the primary equivalent-income
measure. The welfare-layer architecture is designed so that
switching among welfare measures is a single configuration choice
rather than a structural rewrite.

---

## 21. Inference and uncertainty

The welfare decomposition is the JMP's headline result, and its
confidence bands are essential for scientific credibility. The
welfare layer's inference procedure is the *bootstrap re-estimation*
specified in the framework memo §10 C6 and §8 R8.

The bootstrap procedure is: (i) draw $B = 200$ bootstrap samples
from the operational structural-baseline dataset; (ii) re-estimate
$\hat{\theta}$ on each bootstrap sample, holding boundary
parameters at their boundary values (framework memo §10 C8 and
C9); (iii) recompute the welfare decomposition under each
bootstrap replicate's $\hat{\theta}$; (iv) report 95 per cent
confidence intervals as the 2.5th and 97.5th percentiles of the
bootstrap distribution of each decomposition component.

The bootstrap re-estimation is computationally expensive but
unavoidable. The framework memo §10 C6 and the M0c_b2_GSURv2
verdict §11 both flag the bootstrap as the inference method of
record; asymptotic standard errors are not valid for boundary
parameters and are not used for the headline decomposition
inference.

The pooled SA2-promoted baseline, if eventually adopted, requires
*cluster-robust* bootstrap inference at the household level, per
the multi-year memo §2 P3 commitment. The cluster-robust bootstrap
resamples households rather than household-year observations,
preserving the within-household correlation across years for the
8,796 households appearing in both 2016 and 2017. Under the
current single-year M1-clean baseline, the within-household
clustering issue does not arise, and the standard bootstrap is
appropriate.

The welfare layer's inference output is the bootstrap distribution
of each decomposition component under each attribution rule and
each robustness specification. The reported confidence bands are
specification-conditional; they reflect uncertainty in $\hat{\theta}$
given the chosen baseline, not uncertainty across alternative
specifications. Specification uncertainty is reported separately
through the M1-clean / M1-naive sensitivity and the SA1 / SA2
comparison.

A specific consequence of the bootstrap design is that the
welfare-layer code is invoked $B = 200$ times per attribution
rule per sensitivity specification. The walltime cost of the
welfare decomposition is therefore dominated by the bootstrap
re-estimation, not by the welfare layer itself. The bootstrap
re-estimation is a separate computational stage that the welfare
scaffolding orchestrates but does not internally perform; the
welfare-layer architecture is designed to be re-invocable under
external orchestration.

---

## 22. How to handle weak singles consumption identification

The singles consumption joint-identification limitation is a known
structural data limitation, documented in the M0c_b2_GSURv2 verdict
§8 and preserved unchanged through M0c_b2 → M0c_b2_GSURv2 → M1-clean.
The three parameters $\beta_{c,sm}$, $\beta_{c,sf}$, and
$\theta_{c,\text{singles}}$ enter the singles utility specification
as $\beta_{c,g} \cdot c^{\theta_{c,\text{singles}}}$, with a near-
flat likelihood surface in their joint subspace and pseudoinverse-
based standard errors. The limitation does not block structural
baseline acceptance but does affect welfare claims for singles.

The welfare layer treats the singles consumption limitation as
follows.

First, *the welfare layer operates on the joint function
$c \mapsto \beta_{c,g} \cdot c^{\theta_{c,\text{singles}}}$, not on
the individual parameters separately*. The function is identified
up to joint scaling at the point estimate, even when its
individual components are not (M0c_b2_GSURv2 verdict §8 L1). The
equivalent-income calculation depends on the function, not on the
parameter decomposition; the welfare object is therefore well-
defined despite the parameter-level indeterminacy.

Second, *the bootstrap inference for singles welfare claims is
required to be reported separately from the bootstrap inference
for couples welfare claims*. The reason is that the singles
bootstrap distribution will exhibit higher variance in the
$(\beta_{c,sm}, \beta_{c,sf}, \theta_{c,\text{singles}})$ subspace
than the couples bootstrap distribution will in its consumption-
curvature subspace. Reporting confidence bands jointly across
singles and couples without flagging the source of the
heterogeneity in precision would be misleading.

Third, *the sensitivity exposure of the singles welfare claims to
imposing alternative restrictions on the singles consumption
parameters is reported as a robustness exercise*. The framework
memo §11 leaves open the possibility of restricting
$\theta_{c,\text{singles}}$ to a fixed value (e.g., zero, log-
utility) for the welfare calculation; under this restriction, the
singles consumption parameters are identified and the welfare
calculation is precise. The JMP reports the headline decomposition
under the unrestricted singles consumption and the restricted
singles consumption as a robustness exposure.

Fourth, *the welfare claims for singles are qualified relative to
the welfare claims for couples in the paper text*. The JMP states
explicitly that the singles welfare decomposition rests on a
structural limitation, that the couples welfare decomposition does
not, and that the joint reporting respects the difference. This is
the explicit-bookkeeping treatment of the framework memo §10 C9.

The singles consumption limitation does not require any change to
the welfare-layer architecture; the architecture already operates
on the joint function rather than on the individual parameters. The
limitation is a documentation and reporting requirement, not a
code-design requirement.

---

## 23. What will be reported in the first prototype

The first welfare prototype, when welfare scaffolding implementation
is eventually authorised, reports the following objects on the
France 2016 M1-clean baseline.

First, a *baseline welfare distribution figure*. A single-panel
density plot of $\Omega_i^{\text{actual}}$ separately for singles
male, singles female, and couples. The plot is informational; it
is not a decomposition output.

Second, a *primary decomposition table*. A single table with rows
for (i) total welfare inequality measured by Gini on
$\Omega_i^{\text{actual}}$, (ii) the opportunity-contribution to
welfare inequality under the primary reference opportunity set
(§8) and under the Shapley decomposition (§18), (iii) the ability-
contribution under the same rule, (iv) the preference-contribution
as the residual, and (v) the opportunity-ability interaction
diagnostic. The table reports magnitudes for the singles male,
singles female, and couples sub-samples separately and for the
pooled household-type sample. Each entry has a bootstrap 95 per
cent confidence interval.

Third, a *gender-attribution-rule sensitivity table*. The same
decomposition under attribution rules A1, A2, and A3, as columns
of a single table.

Fourth, an *M1-clean / M1-naive sensitivity row*. The same primary
decomposition row computed under the M1-naive estimates (framework
memo §8 R2), reported as a single row to be appended to the
primary decomposition table.

Fifth, a *reference-set sensitivity table*. The decomposition under
the primary reference (§8 median), the best-available reference,
and the type-pooled reference, as rows of a single table.

Sixth, a *figure showing the opportunity-driven welfare cut*. A
single-panel plot of $\Omega_i^{\text{actual}}$ versus
$\Omega_i^{\text{opp-eq}}$ across households, with the diagonal
indicating no opportunity effect and the deviations from the
diagonal indicating the opportunity-driven welfare gap. The plot
is the visual representation of the JMP's central question.

These six objects together constitute the first prototype. They
are not the JMP's final reporting set; they are the minimum
sufficient output to establish that the welfare layer functions
correctly and produces the headline magnitude that the JMP
expects. The framework memo §8 R3, R5, R6, R7 robustness exposures
extend the prototype but are not part of the first deliverable.

The prototype is computed against `ruro_occ_M1_clean` as the
operational structural baseline. If the SA2 verdict eventually
promotes a pooled specification, the prototype is recomputed
against the pooled $\hat{\theta}$ under the §13 primary baseline-
distribution choice (single-year 2016 evaluation of pooled-
parameter equivalent incomes). The prototype's reporting structure
is unchanged in either regime.

---

## 24. What will not be claimed yet

The following claims are explicitly *not* supported by this memo
and must not appear in JMP text, supervisor memos, or
presentations until welfare-decomposition computation is authorised
and welfare results are produced.

(N1) *"The opportunity share of welfare inequality is X per
cent."* Not supported. No welfare numbers are computed in this
memo. The headline opportunity-share magnitude is produced by the
welfare decomposition once welfare scaffolding is implemented and
welfare-decomposition computation is authorised.

(N2) *"The welfare decomposition is independent of the inequality
index."* Not supported. §17 explicitly anticipates index
dependence; the JMP reports magnitudes under each index without
claiming index-independence.

(N3) *"The decomposition is independent of the reference
opportunity set."* Not supported. §8 explicitly anticipates
reference dependence; the JMP reports magnitudes under each
reference without claiming reference-independence.

(N4) *"Country ranking of welfare inequality is the JMP's
contribution."* Not supported. The JMP is not a country-ranking
exercise. The first prototype is France 2016 only; later
extensions to other years and other countries may produce ranking
information, but ranking is not the scientific object. The
literature-positioning memo §6 makes this explicit: rankings tell
the reader who is ahead under a metric; decomposition tells the
reader what mechanism produces inequality in that metric. The JMP
delivers the latter.

(N5) *"The welfare layer produces a tax-reform counterfactual."*
Not supported. The welfare layer constructs counterfactuals on
opportunity and ability covariates, not on tax-benefit policy
parameters. Tax-reform counterfactuals require operating on the
EUROMOD tax-benefit function and are out of scope for the first
prototype. They are a possible later extension but are not part of
the JMP's primary contribution.

(N6) *"Preferences are normatively responsibility-relevant."*
Partially supported and explicitly hedged. The JMP's primary
attribution treats preferences as responsibility-relevant under
the weak-Dworkin position; the strong-Roemer alternative treats
ability as compensation-relevant alongside opportunity. The
preference contribution is reported with a normative footnote in
both columns; the JMP does not impose the weak-Dworkin position
on the reader.

(N7) *"The pooled specification is the JMP's preferred baseline."*
Not supported. The current preferred baseline is M1-clean. A
future pooled specification may replace M1-clean only under an
SA2-STANDS verdict per the multi-year memo §11. The welfare-
measurement decisions in this memo accommodate both regimes
without prejudging the SA2 verdict.

(N8) *"The François Maniquet pure-theory paper is implemented in
the JMP welfare layer."* Not supported. The JMP welfare layer
operationalises the equivalent-income welfare object that the
theory paper articulates, but it does not reproduce or implement
the theory paper. The JMP remains a distinct empirical paper.

(N9) *"Welfare scaffolding implementation is authorised."* Not
supported. This memo authorises welfare-measurement decisions
work; welfare scaffolding implementation, welfare-decomposition
computation, canonical MNL promotion, and Stage B age-specific
GSUR work all remain deferred.

(N10) *"The welfare layer's inference is asymptotic."* Not
supported. The inference procedure is the bootstrap re-estimation
of §21. Asymptotic standard errors are not valid for boundary
parameters and are not used for the headline decomposition.

---

## 25. Implications for welfare-scaffolding code

When welfare scaffolding implementation is eventually authorised,
the welfare-scaffolding code must satisfy the following design
implications of this memo. These implications are the contract
under which the welfare-layer code will later be implemented and
audited.

(I1) *Specification-agnostic input boundary*. The welfare layer
accepts (i) a structural-parameter vector $\hat{\theta}$ from any
operational baseline (currently M1-clean, potentially a future
pooled specification), and (ii) the opportunity-block and ability-
block covariate lists from the YAML specification of that baseline.
The welfare layer does not hard-code the covariate lists; it reads
them from the YAML.

(I2) *Modular welfare-measure switching*. The primary equivalent-
income measure and the secondary EV/CV/Atkinson-equivalent measures
are produced by the same code with a configuration switch. Adding
a fourth welfare measure does not require structural rewriting.

(I3) *Modular counterfactual construction*. The opportunity-
equalised, ability-equalised, and preference-neutralised
counterfactuals are produced by the same code with a configuration
switch over which covariate block is held at reference. Adding a
fourth counterfactual (e.g., year-equalised under the pooled
regime) does not require structural rewriting.

(I4) *Joint singles consumption handling*. The welfare layer
operates on the joint function
$c \mapsto \beta_{c,g} \cdot c^{\theta_{c,\text{singles}}}$ rather
than on the individual parameters separately, per §22. The code
must not require the individual parameters to be separately
identified.

(I5) *Specification-conditional bootstrap orchestration*. The
welfare layer is invocable as a function of a single $\hat{\theta}$
input; it does not internally orchestrate the bootstrap. The
bootstrap orchestration is a separate stage that invokes the
welfare layer once per replicate. Under the pooled regime, the
bootstrap is cluster-robust at the household level; under the
single-year regime, the bootstrap is standard.

(I6) *Reference-set parameterisation*. The reference bundle, the
reference job, and the reference opportunity set are parameterised
in a single configuration file rather than hard-coded. Switching
between primary and sensitivity references is a configuration
change, not a code change.

(I7) *Three-way and two-way decomposition support*. The welfare
layer computes both the three-way decomposition (opportunity,
ability, preference) and the two-way collapses (opportunity-or-
ability versus preference under the strong-Roemer alternative;
opportunity versus ability-or-preference under the weak-Dworkin
primary). Both Shapley and ordered-removal rules are supported.

(I8) *Gender-attribution-rule parameterisation*. The three gender
attribution rules A1, A2, A3 are parameterised by a single
configuration value rather than hard-coded. The same welfare-layer
code produces the decomposition under each rule with a single
configuration change.

(I9) *Decomposition table as primary output*. The welfare layer's
primary output is a structured table containing the decomposition
components, their bootstrap confidence intervals, and their
attribution-rule and sensitivity-specification labels. The table
format is the same across single-year and pooled regimes.

(I10) *Singles–couples reporting separation*. The decomposition
table reports singles male, singles female, and couples sub-samples
separately and the pooled household-type sample, per §22 and §23.
The singles welfare claims carry a documented qualification
relative to the couples claims, encoded in the table's footnote
schema.

(I11) *No tax-benefit modification*. The welfare layer does not
modify the EUROMOD tax-benefit function. Tax-reform counterfactuals
are out of scope for the first prototype, per §24 N5.

(I12) *Output reproducibility*. The welfare layer's output is
deterministic given $\hat{\theta}$, the covariate inputs, and the
configuration. Bootstrap replicates introduce randomness through
the resampling, not through the welfare-layer computation.
Re-running the welfare layer on identical inputs produces identical
outputs.

These twelve implications constitute the design contract for the
welfare scaffolding. The eventual
`RURO_welfare_scaffold_design_contract_v1.md` will codify them
into a formal implementation specification; the eventual
`RURO_welfare_scaffold_verdict_v1.md` will audit the
implementation against the contract.

This memo does not authorise the implementation. It authorises the
design. The implementation is gated on a separate authorisation
that takes (this memo) and (the resolved primary structural
baseline path — currently M1-clean, possibly a future pooled
specification under SA2-STANDS) as joint inputs.

---

## Status and authorisation summary

*Authorised by this memo*: the welfare-measurement decisions are
locked. The welfare scaffolding design contract may now be drafted
on the basis of these decisions.

*Not authorised by this memo*: welfare scaffolding implementation;
welfare-decomposition computation; canonical MNL promotion (the
O10 decision); Stage B age-specific GSUR work (the O6 decision);
modification of the M1-clean, M1-naive, or any frozen-block
specification; pooled multi-year estimation in any configuration;
the François Maniquet pure-theory paper.

*Pending under separate verdicts*: the SA2 verdict on a potential
pooled-specification replacement of M1-clean; the welfare
scaffolding implementation, gated on this memo and on the resolved
primary structural baseline; the welfare-decomposition computation,
gated on the welfare scaffolding verdict.

*Status of M1-clean as preferred structural baseline*: unchanged.
M1-clean is SA1-STANDS per `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md`
and remains the JMP's preferred specification subject only to the
prospective SA2 verdict pathway.

*Status of M1-naive*: a robustness exposure, not a candidate
primary specification. M1-naive is reported in the welfare
decomposition as the R2 sensitivity exposure of the framework memo
§8 and is not the baseline against which the JMP's headline
welfare magnitudes are computed.

*Status of the JMP relative to the François Maniquet pure-theory
paper*: distinct. The JMP is an empirical paper; the theory paper
is intellectually adjacent but operationally separate. The JMP
implements the equivalent-income object that the theory paper
articulates, but does not reproduce the theory paper's axiomatic
results.
