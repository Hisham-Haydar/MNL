# JMP Welfare-Scaffolding Design Memo v1

Date: 2026-05-19

Specification class: code-architecture design memo. The memo
translates the welfare-measurement decisions of
`docs/JMP_welfare_measurement_decisions_memo_v1.md` into a concrete
module architecture, an input-boundary contract, a configuration
schema, and a deliverables list. It does not authorise welfare
computation; it specifies the scaffolding that, once authorised,
will perform welfare computation.

Reference documents:
- `docs/JMP_welfare_measurement_decisions_memo_v1.md` (the locked
  welfare-measurement decisions)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the current preferred
  structural baseline, SA1-STANDS)
- `docs/RURO_occ_M1_naive_robustness_verdict_v1.md` (the M1-naive
  robustness exposure)
- `docs/RURO_occ_M1_clean_design_memo_v2.md` (the structural design
  of M1-clean)
- `docs/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the prior baseline
  documenting the singles consumption identification limitation)
- `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the pooled-estimation roadmap and SA2 verdict architecture)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  ability/opportunity partition and the framework memo's C1–C9 code
  contract)
- `docs/JMP_literature_positioning_memo_v2.md` (contribution claim
  and closest-paper positioning)

Scope: empirical JMP scaffolding only. The memo respects the
boundary between the empirical JMP and the separate François
Maniquet pure-theory paper on jobs and well-being. The scaffolding
operationalises the equivalent-income welfare object that the
theory paper articulates; it does not implement the theory paper.

---

## 1. Purpose of the welfare scaffolding

The welfare scaffolding is the code layer that, given a structural
parameter vector $\hat{\theta}$ from an operational RURO baseline,
constructs the household equivalent-income welfare distribution
and the opportunity / ability / preference decomposition of welfare
inequality across that distribution. It is the "JMP-paper layer"
of the codebase, distinct from the estimation layer.

The scaffolding's purpose is twofold. First, it produces the
JMP's headline scientific output: a decomposition of money-metric
well-being inequality into opportunity, ability, and preference
components, with bootstrap confidence intervals, under multiple
attribution rules and reference choices. Second, it produces the
robustness machinery that the JMP's credibility rests on: the
M1-naive sensitivity exposure, the reference-set sensitivity, the
inequality-index sensitivity, and the welfare-measure sensitivity.

The scaffolding is methodologically constrained by the welfare-
measurement decisions memo. The decisions memo locks the welfare
object (household equivalent income), the reference choices
(median by household type, full-time employment at median wage),
the inequality index (Gini primary, with secondary indices), the
decomposition rule (Shapley primary, ordered-removal secondary),
and the inference procedure (bootstrap re-estimation). The
scaffolding implements these decisions; it does not re-litigate
them.

The scaffolding is operationally constrained by the structural
baseline. The current preferred baseline is `ruro_occ_M1_clean`,
and the scaffolding's primary deliverable runs on the M1-clean
parameter vector. A future pooled SA2-promoted baseline would
replace M1-clean as the primary input; the scaffolding must
accommodate both regimes without architectural rewriting.

The scaffolding does *not* re-estimate the structural model. It
operates on $\hat{\theta}$ as a fixed input. The bootstrap
re-estimation that produces inference is orchestrated externally
to the scaffolding; the scaffolding is invoked once per bootstrap
replicate.

---

## 2. What this memo authorises and does not authorise

*Authorised by this memo*: the design of the welfare scaffolding
code architecture. The module boundaries, the input-boundary
contract, the configuration-file schema, the function signatures,
the diagnostic outputs, and the deliverables list are all locked
here, in the same sense that the M1-clean design memo locked the
structural specification before estimation was authorised.

*Not authorised by this memo*: welfare scaffolding *implementation*
in code; welfare-decomposition *computation* on any structural
baseline; canonical MNL promotion (the O10 decision); Stage B
age-specific GSUR work (the O6 decision); modification of any
frozen-block element of M1-clean or M1-naive; pooled multi-year
estimation in any configuration. These remain explicitly deferred.

The authorisation cascade is therefore:
- *Locked*: welfare-measurement decisions (memo v1, dated
  2026-05-19); welfare scaffolding design (this memo).
- *Pending*: welfare scaffolding implementation, gated on a
  separate implementation prompt that takes this memo as input
  and produces the welfare-scaffolding code; welfare-decomposition
  computation, gated on a welfare-scaffolding verdict that audits
  the implemented code against this design.

The scaffolding implementation prompt is a separate deliverable
in a separate Claude Code Sonnet chat. This memo is the
specification it consumes.

A specific consequence of this gating: nothing in this memo
constitutes a welfare result. The memo specifies the code that
*will* produce welfare results once welfare-decomposition
computation is authorised. The distinction is the same as the
distinction between the M1-clean design memo and the M1-clean
estimation report.

---

## 3. Current structural baseline

The current preferred structural baseline is `ruro_occ_M1_clean`,
classified SA1-STANDS per `docs/RURO_occ_M1_clean_verdict_v1.md`.
The baseline parameter vector is the converged point of three
independent starts at log-likelihood $-6487.5522$, with the
GSURv2 MNL parquets as the operative data source.

The M1-clean baseline contains 53 free parameters partitioned as:
preference block (consumption and leisure Box-Cox curvature, age
and children leisure shifters, leisure-leisure interaction);
wage block (education, potential experience, gender, dispersion);
market-opportunity block (corrected GSUR, seven EUROMOD `drgn1`
region indicators / old-region aggregation indicators
(`reg2`–`reg8`, with `reg1` as the reference category), gender-on-
arrival, intercept); hours block (gender-
specific focal-point parameters); occupation block (task-content
by group); and the proposal correction (a likelihood-correction
artifact, not in opportunity / ability / preference).

The M1-naive baseline (`ruro_occ_M1_naive`) is a robustness
exposure, not a candidate primary specification. M1-naive differs
from M1-clean by retaining $\beta_{E\,\text{educH}}$ in the
market-opportunity block (54 free parameters; LL = $-6485.5287$).
The M1-naive verdict (`docs/RURO_occ_M1_naive_robustness_verdict_v1.md`)
concludes that the borderline statistical evidence for retaining
$\beta_{E\,\text{educH}}$ is insufficient to overturn the M1-clean
welfare-partition design. The scaffolding's *primary run* operates
on M1-clean; the *robustness run* operates on M1-naive (§§22–23).

The singles consumption joint-identification limitation
(three pseudoinverse-based standard errors on $\beta_{c,sm}$,
$\beta_{c,sf}$, $\theta_{c,\text{singles}}$, documented in the
M0c_b2_GSURv2 verdict §8 and preserved through M1-clean) is a
known structural data limitation that the scaffolding accommodates
operationally (§15).

A pooled multi-year specification may eventually replace M1-clean
as the primary baseline under an SA2-STANDS verdict. The
scaffolding's design must be compatible with such a replacement
without architectural rewriting; the compatibility is the subject
of §§4 and 24.

---

## 4. How the scaffolding remains baseline-agnostic

The scaffolding accepts the structural baseline as an input rather
than embedding the baseline in its code. The mechanism is the
following.

First, the *parameter vector* $\hat{\theta}$ is read from a parquet
file at a path supplied in the welfare configuration (§7). The
scaffolding does not hard-code the parameter vector or the
baseline's run directory. Under M1-clean, the parameter file is
the converged-estimates parquet at the M1-clean run directory;
under a future SA2-promoted pooled baseline, the parameter file is
the converged-estimates parquet at the pooled run directory.
Switching baselines is a single configuration change.

Second, the *opportunity-block and ability-block covariate lists*
are read from the YAML specification of the baseline rather than
hard-coded. The M1-clean YAML
(`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`)
declares the opportunity-block covariates as: corrected GSUR, seven
EUROMOD `drgn1` region indicators / old-region aggregation
indicators (`reg2`–`reg8`, with `reg1` as the reference category),
gender-on-arrival, intercept. The
scaffolding reads this declaration and uses it to construct the
opportunity-equalisation counterfactual. Under M1-naive, the YAML
additionally declares $\beta_{E\,\text{educH}}$ as an opportunity-
block covariate; the scaffolding picks it up automatically.

Third, the *MNL alternative-set data* (§6) are read from a data
path supplied in the welfare configuration. Under M1-clean, the
data are the GSURv2 MNL parquets for FR 2016; under a future
pooled baseline, the data are the stacked multi-year MNL parquets.
The data schema is invariant across baselines; the scaffolding
operates on the schema.

Fourth, the *bootstrap orchestration* is external to the
scaffolding. Under the single-year regime, the bootstrap is
standard; under the pooled regime, the bootstrap is cluster-robust
at the household level. The scaffolding does not orchestrate the
bootstrap; it is invoked once per replicate by an external
orchestration script that knows which regime is active.

A specific design consequence: the scaffolding source code contains
*zero* references to "M1-clean" or "M1-naive" or "pooled" as
hard-coded strings. Specification-identifying strings live only in
the configuration file. This is the test for whether the
scaffolding is genuinely baseline-agnostic at the implementation
level.

---

## 5. Required structural inputs

The scaffolding's structural inputs are the following objects, all
produced by the estimation layer and consumed by the scaffolding
without modification.

(S1) *Converged parameter vector* $\hat{\theta}$ as a parquet
file with one row per parameter, columns: `parameter_name`,
`estimate`, `se_pseudoinverse_flag`. The pseudoinverse flag is
True for the three singles consumption parameters under M1-clean
and is False for all other parameters; the flag controls the
bootstrap treatment of boundary parameters (framework memo §10
C8).

(S2) *Parameter VCV matrix* as a parquet file with parameter
names as both row and column indices, entries as the Hessian-based
or pseudoinverse-based variance-covariance estimate. The
scaffolding consumes the VCV only for diagnostic purposes (§27);
the bootstrap inference does not use the VCV.

(S3) *Estimation specification YAML* at the path declared in the
configuration. The scaffolding parses the YAML to extract the
opportunity-block covariate list, the ability-block covariate list,
the preference-block parameter list, the wage-block parameter
list, the hours-block parameter list, the occupation-block
parameter list, and the proposal-correction parameter list. The
extraction is read-only; the scaffolding does not modify the YAML.

(S4) *Run-directory metadata* declaring the baseline identifier,
the data-source MNL parquet paths, the EUROMOD system version
(currently `FR_2016_a3` under M1-clean; `FR_2015_a2`, `FR_2016_a3`,
`FR_2017_a2` under any pooled baseline), and the run-acceptance
verdict path (currently `docs/RURO_occ_M1_clean_verdict_v1.md`
under M1-clean). The metadata enables the scaffolding to record
which baseline produced any given welfare output.

The structural inputs are *read-only* to the scaffolding. The
scaffolding does not re-fit, re-estimate, re-derive, or modify
any structural object. A bootstrap re-estimation produces new
$\hat{\theta}$ vectors which the scaffolding consumes, but the
re-estimation itself is performed by the estimation layer, not by
the scaffolding.

---

## 6. Required MNL / alternative-set inputs

The scaffolding's MNL / alternative-set inputs are the data
objects that, together with $\hat{\theta}$, define each household's
feasible job set and the consumption–leisure point at each
alternative. These objects are produced by the MNL data-prep
pipeline (currently the GSURv2 versioned MNL parquets) and consumed
by the scaffolding without modification.

(M1) *Alternative-set parquet* with one row per (household,
alternative) pair, columns including: `household_id`,
`alternative_index`, `hours_male`, `hours_female`, `wage_male`,
`wage_female`, `gross_income`, `disposable_income` (EUROMOD-
processed), `consumption` (the consumption argument of utility),
`leisure_male`, `leisure_female`, `occupation_male`,
`occupation_female`, `is_chosen`, `prior_weight`, and the
ability-block and opportunity-block covariates evaluated for that
alternative.

(M2) *Household-level covariate parquet* with one row per
household, columns including: `household_id`, `household_type`
(singles male / singles female / couples), `age_male`, `age_female`,
`nkids_male`, `nkids_female`, `education_male`, `education_female`,
`pexp_male`, `pexp_female`, `drgn1` (the EUROMOD old-region
aggregation indicator; the legacy physical column name in the
existing parquets may read `region_nuts1`, but the conceptual
identifier is `drgn1` and the seven non-reference indicators are
`reg2`–`reg8`), `gsur_male`, `gsur_female`,
and any other household-level covariates entering preference,
ability, or opportunity blocks.

(M3) *Reference-distribution parquet*, produced once at
configuration-load time and cached, containing the median values
of each opportunity-block and ability-block covariate by household
type and gender. The scaffolding constructs this parquet on first
invocation from (M2) and writes it to the configuration's reference
cache; subsequent invocations read from cache.

(M4) *EUROMOD output-variable index* at the path declared in the
configuration (currently `euromod_fr_2015_2017_output_variable_index.csv`).
The scaffolding uses this index to confirm that the
`disposable_income` column in (M1) is the EUROMOD-processed
disposable income for the relevant system version, not a different
income concept. The check is a configuration-validation diagnostic,
not a data-modification operation.

The MNL alternative-set inputs are *read-only* to the scaffolding.
The scaffolding does not re-construct alternative sets, re-process
EUROMOD outputs, or re-derive any data object. Under the
opportunity-equalised counterfactual (§12), the scaffolding
modifies the *covariate values* used to evaluate the opportunity
density, but it does not modify the underlying parquet.

---

## 7. Required welfare configuration file

The scaffolding consumes a single YAML configuration file at the
path supplied as a command-line argument. The configuration's
schema is fixed by this design memo; the scaffolding rejects any
configuration that does not validate against the schema.

The configuration file declares the following sections, with
fixed key names:

```yaml
baseline:
  identifier: "ruro_occ_M1_clean"        # or "ruro_occ_M1_naive", or future pooled
  regime: "single_year"                  # or "pooled"
  parameter_parquet_path: "..."          # path to (S1)
  vcv_parquet_path: "..."                # path to (S2)
  estimation_spec_yaml_path: "..."       # path to (S3)
  acceptance_verdict_path: "..."         # path to the SA1 or SA2 verdict
  mnl_alternative_set_path: "..."        # path to (M1)
  mnl_household_covariate_path: "..."    # path to (M2)
  euromod_output_index_path: "..."       # path to (M4)
  euromod_system_version:
    - "FR_2016_a3"                       # one entry per system under pooling
welfare_object:
  primary: "equivalent_income"
  secondary:
    - "compensating_variation"
    - "equivalent_variation"
    - "atkinson_equivalent_epsilon_1"
    - "atkinson_equivalent_epsilon_2"
reference:
  bundle:
    consumption: "type_conditional_median"
    leisure: "type_conditional_median"
    sensitivity:
      - "type_conditional_mean"
      - "best_available"
      - "type_pooled_median"
  job:
    primary: "full_time_median_wage"
    sensitivity:
      - "household_actual"
      - "part_time_median_wage"
      - "gender_specific_occupation"
  opportunity_set:
    primary: "type_conditional_median_opportunity_covariates"
    sensitivity:
      - "best_available_opportunity_covariates"
attribution:
  primary_rule: "A3"                     # the 40/60 Blau-Kahn split
  reported_rules:
    - "A1"
    - "A2"
    - "A3"
  responsibility_position:
    primary: "weak_dworkin"
    secondary: "strong_roemer"
inequality_index:
  primary: "gini"
  secondary:
    - "cv_squared"
    - "theil_l"
    - "atkinson_epsilon_1"
    - "atkinson_epsilon_2"
decomposition:
  primary_rule: "shapley_shorrocks"
  secondary_rule: "ordered_removal"
  three_way: true                        # opp / abil / pref
  report_two_way_collapses: true
inference:
  procedure: "bootstrap_reestimation"
  n_replicates: 200
  cluster_unit: "household_id"           # required under "pooled" regime
  confidence_level: 0.95
  boundary_parameter_handling: "boundary_pinned"
singles_consumption:
  handling: "joint_function"             # operates on beta_c * c^theta_c
  restricted_sensitivity:
    enabled: true
    theta_c_singles_fixed_value: 0.0     # log-utility restriction
baseline_distribution:
  single_year:
    evaluation_year: "2016"
  pooled:
    primary: "single_year_2016"          # per decisions memo §13
    sensitivity:
      - "pooled_cross_section"
      - "reweighted_2016"
output:
  table_directory: "outputs/welfare/tables/"
  figure_directory: "outputs/welfare/figures/"
  diagnostic_directory: "outputs/welfare/diagnostics/"
  bootstrap_directory: "outputs/welfare/bootstrap/"
```

The schema fixes the configuration; the *values* fix the
specific scaffolding run. Switching the M1-clean primary run to
the M1-naive robustness run is a single change to the
`baseline.identifier` and the parameter / spec paths. Switching
to a hypothetical SA2-promoted pooled baseline is a change to
`baseline.regime`, the parameter / spec paths, and the
`inference.cluster_unit`. No other changes to the configuration
or the scaffolding code are required.

The scaffolding writes a copy of the resolved configuration into
each output directory as a provenance record. Re-running the
scaffolding on the same configuration produces the same output;
the output directory is timestamped and configuration-hashed.

---

## 8. Primary welfare object

The primary welfare object is *household equivalent income*
$\Omega_i$, computed as specified in the decisions memo §3 and §4.

The scaffolding constructs $\Omega_i$ as follows. For each
household $i$, the structural model implies an expected-maximum
utility over the household's sampled feasible job set, computed as
the log-sum-exp of utilities over alternatives weighted by the
opportunity density $q(x_{\text{opp}})$, the wage density
$g_1(w; x_w)$, the hours density $g_2(h)$, the occupation
mechanism $O^{\text{Occ}}$, and the prior correction. This
expected-maximum utility is the household's attained utility.

The equivalent income $\Omega_i$ is the disposable-income level
$y^*$ that, at the reference job (§10) and the reference
opportunity set (§11), would deliver attained utility equal to
the household's actual attained utility under the household's own
preferences. The scaffolding solves for $y^*$ by inverting the
attained-utility map at the reference job; the inversion is
one-dimensional and is performed numerically via a bracketing root
solver on the household's own utility function.

A specific operational note: the inversion operates on disposable
income evaluated at the reference job's tax-benefit treatment. The
scaffolding does *not* re-run EUROMOD inside the inversion; the
tax-benefit function at the reference job is pre-computed from the
EUROMOD outputs in (M1) and is interpolated where the reference
job's hours and wage fall between alternative-set values. The
interpolation uses a linear-piecewise scheme on the
hours-disposable-income relationship for each household, which is
adequate for the smooth EUROMOD tax-benefit schedule.

The primary welfare object is computed once per household per
baseline. The output is a parquet file with one row per household,
columns: `household_id`, `omega_actual`, and diagnostic columns
documenting the attained-utility value and the convergence status
of the inversion.

---

## 9. Secondary welfare objects

The secondary welfare objects are *compensating variation* (CV),
*equivalent variation* (EV), and the *Atkinson-equivalent income*
at $\varepsilon = 1$ and $\varepsilon = 2$. Each is computed by
the scaffolding as a configuration-switchable alternative to the
primary equivalent income.

(W1) *Compensating variation*. For each household $i$, CV is the
income transfer that would make the household indifferent between
its actual opportunity environment and the reference opportunity
environment, under the household's own preferences. The
scaffolding computes CV by the de Palma–Kilani log-sum-exp
adjustment over the household's feasible job sets in the two
environments.

(W2) *Equivalent variation*. EV is the income transfer that would
make the household indifferent between the reference opportunity
environment and its actual environment. EV and CV differ when the
reference state is genuinely counterfactual.

(W3) *Atkinson-equivalent income at $\varepsilon$*. For each
household, this is the income level that produces an Atkinson-
weighted utility equal to the household's attained utility, under
the household's own preferences. The scaffolding computes it by
the same inversion machinery as the primary $\Omega_i$, with the
Atkinson utility transformation applied at the inversion step.

The secondary welfare objects are computed *on the same
counterfactual covariate inputs* as the primary equivalent income.
The decomposition is performed on each welfare object separately
under configuration control, and the JMP reports the headline
results on the primary object and the sensitivity results on the
secondary objects.

Switching welfare objects is a single configuration change in the
`welfare_object` section. The scaffolding produces the secondary
objects only when they are listed in the configuration's
`secondary` field; this avoids unnecessary computation on the
primary M1-clean run.

---

## 10. Reference bundle and reference job

The reference bundle and reference job are jointly specified by
the configuration's `reference.bundle` and `reference.job`
sections. The scaffolding constructs them as follows.

The *reference bundle* $(c^*, \ell^*)$ is the consumption–leisure
point at which equivalent income is evaluated. Under the primary
choice, $c^*$ is the median consumption and $\ell^*$ is the
median leisure of the working-age sample, computed separately by
household type. The scaffolding constructs the type-conditional
medians from (M2) on first invocation and caches them in the
reference-distribution parquet (M3); subsequent invocations read
from cache.

The *reference job* is full-time employment at the median full-
time wage, computed by household type and gender. The
scaffolding constructs the reference job by selecting, from the
chosen-alternative subset of (M1) where the household member's
hours fall in the full-time range, the median hours and median
wage. The selection is type-conditional and gender-conditional.

The reference bundle and reference job are *mutually consistent*
in the following sense: the reference job's hours and wage,
combined with the reference opportunity set's tax-benefit
treatment, must produce a consumption–leisure point close to
$(c^*, \ell^*)$. If the produced point differs materially, the
scaffolding emits a diagnostic warning at construction time; this
diagnostic is part of the §27 required diagnostics.

Switching reference choices is a single configuration change. The
sensitivity references (`type_conditional_mean`, `best_available`,
`type_pooled_median`) are constructed by the same scaffolding code
under different configuration settings; the construction logic is
shared.

A specific operational note: the reference bundle and reference
job are normative choices in the strict sense of the decisions
memo §6–7. The scaffolding does not select among them; it
operationalises the choices declared in the configuration. The
choice itself is the analyst's normative responsibility and is
documented in the configuration file's provenance record.

---

## 11. Reference opportunity set

The reference opportunity set is the feasible job set under which
the counterfactual welfare objects are computed. The scaffolding
constructs it from the opportunity-block covariate list extracted
from the estimation specification YAML (§5 S3).

Under M1-clean, the reference opportunity set is defined by the
following covariate values: corrected GSUR at the type-conditional
median, all seven EUROMOD `drgn1` region indicators / old-region
aggregation indicators (`reg2`–`reg8`) at the reference category
(`reg1`, the modal region across the sample), gender-on-arrival
held or
equalised per the gender attribution rule (§17), and the
opportunity-block intercept at its estimated value (intercepts are
not equalised; only shifter covariates are).

Under M1-naive, the reference opportunity set additionally sets
$\beta_{E\,\text{educH}}$'s associated education covariate to the
type-conditional median. The scaffolding picks this up
automatically because the M1-naive YAML declares the education
covariate as an opportunity-block shifter, and the scaffolding
reads the opportunity-block list from the YAML.

Under a future pooled SA2-promoted baseline, the reference
opportunity set additionally includes year fixed effects, set to
the reference year (2016 under the decisions memo §13 primary
baseline-distribution choice). The scaffolding constructs the
year-equalised reference automatically when the
`baseline.regime` field is `"pooled"`.

The reference opportunity set is the *core operational object* of
the JMP's opportunity-driven inequality measurement. The
scaffolding produces it once per baseline-configuration pair and
caches it in the reference-distribution parquet (M3).

Switching reference opportunity sets between primary and sensitivity
(best-available opportunity covariates) is a single configuration
change; the scaffolding constructs each sensitivity reference
under the same machinery.

---

## 12. Opportunity-equalised counterfactual

The opportunity-equalised counterfactual welfare distribution
$\{\Omega_i^{\text{opp-eq}}\}_i$ is constructed by the scaffolding
as follows.

For each household $i$, the scaffolding replaces the opportunity-
block covariates in the household's alternative set with the
reference opportunity set's values (§11). The structural parameter
vector $\hat{\theta}$ is unchanged; the ability covariates are
unchanged; the preference parameters are unchanged; the random
preference shock is unchanged (i.e., the same alternative-set rows
are used, with only the opportunity covariates modified).

The scaffolding then recomputes the attained utility under the
modified opportunity covariates and inverts to obtain the
counterfactual equivalent income $\Omega_i^{\text{opp-eq}}$. The
inversion machinery is the same as for $\Omega_i^{\text{actual}}$
(§8); the only change is the opportunity-covariate input.

A specific design consequence: the opportunity-equalisation
operation is *covariate-side*, not parameter-side. The opportunity
parameters are not zeroed out; they are evaluated at the
counterfactual covariates. This preserves the parameter vector's
internal consistency (e.g., the intercept, which encodes the
average level of opportunity, is retained) while equalising the
covariate-driven heterogeneity (e.g., the regional differences,
which encode opportunity heterogeneity).

The opportunity-equalised distribution is the central
counterfactual of the JMP. The inequality of
$\Omega_i^{\text{opp-eq}}$ is the welfare inequality that would
remain if the opportunity dimension were eliminated, holding
ability, preferences, and shocks at their actual realisations.

The output is a parquet file with one row per household, columns:
`household_id`, `omega_opp_eq_actual_opportunity`,
`omega_opp_eq_reference_opportunity`, and diagnostic columns. The
file is named with the baseline identifier and the reference-set
identifier so that the M1-clean primary and the M1-naive
robustness runs do not collide on disk.

---

## 13. Ability-equalised counterfactual

The ability-equalised counterfactual welfare distribution
$\{\Omega_i^{\text{abil-eq}}\}_i$ is constructed by the
scaffolding as a structural analogue of the opportunity-equalised
counterfactual.

For each household $i$, the scaffolding replaces the ability-
block covariates (education, potential experience, gender-on-wage)
in the household's alternative set with the reference values
(§10). The opportunity covariates are unchanged; the preference
parameters are unchanged; the random preference shock is
unchanged. The scaffolding then recomputes the attained utility
under the modified ability covariates and inverts to obtain
$\Omega_i^{\text{abil-eq}}$.

The ability-equalisation interacts with the gender attribution rule
(§17). Under A1 (gender-on-wage as ability), the gender-on-wage
coefficient's covariate is equalised in the ability-equalisation
operation. Under A2 (gender-on-wage as opportunity), it is *not*
equalised here; it is equalised in the opportunity operation.
Under A3 (split 40/60), the ability-equalisation equalises 40 per
cent of the gender-on-wage covariate. The scaffolding enforces
this joint dependence via the attribution-rule configuration.

The ability-equalised counterfactual is informational under the
weak-Dworkin primary attribution: the ability-driven inequality
is not compensation-relevant under that position. Under the
strong-Roemer alternative, the ability-equalised counterfactual is
co-equal with the opportunity-equalised counterfactual in defining
the compensation-relevant welfare cut.

The output is a parquet file analogous to the opportunity-
equalised output. The diagnostic columns flag any case where the
ability-equalisation operation produces an unbounded or undefined
welfare value; this is part of the §27 required diagnostics.

---

## 14. Preference-neutralised counterfactual

The preference-neutralised counterfactual welfare distribution
$\{\Omega_i^{\text{both-eq}}\}_i$ is constructed by the scaffolding
as the welfare distribution under simultaneous opportunity and
ability equalisation. For each household, the scaffolding replaces
both the opportunity covariates and the ability covariates with
their reference values, leaving only the preference parameters and
the random preference shock at their actual realisations.

The preference-neutralised counterfactual is the *residual after
both opportunity and ability equalisation*. The inequality of
$\Omega_i^{\text{both-eq}}$ is the welfare inequality attributable
to preference heterogeneity, under the structural mapping of
preferences to the consumption/leisure curvature, the leisure
shifters, the leisure-leisure interaction, gender-on-utility, and
the random Fréchet shock.

A specific design clarification: the preference-neutralised
counterfactual does *not* equalise preferences. Equalising
preferences would require collapsing the heterogeneous preference
parameters to a common value, which is a common-utility operation
alien to the JMP's preference-respecting design. The scaffolding
does not implement that operation. The "neutralisation" instead
refers to residualisation: opportunity and ability are equalised,
and what remains in the welfare distribution is the preference
contribution.

The output is a parquet file analogous to the opportunity- and
ability-equalised outputs.

---

## 15. Treatment of singles

The scaffolding handles the singles male and singles female sub-
samples separately from the couples sub-sample, for two reasons.

First, the structural model has different functional forms across
household types. Singles utility depends on one person's hours,
wage, and demographics; couples utility depends on both spouses'
hours, wages, demographics, and the leisure-leisure interaction.
The reference bundle, reference job, and reference opportunity
set are therefore type-conditional. The scaffolding processes
singles male, singles female, and couples separately and reports
welfare distributions and decompositions by type.

Second, the singles consumption joint-identification limitation
(§3 and decisions memo §22) affects only the singles sub-sample.
The scaffolding's treatment is:

(T1) *Joint-function handling*. The scaffolding's primary mode
operates on the function
$c \mapsto \beta_{c,g} \cdot c^{\theta_{c,\text{singles}}}$ rather
than on the individual parameters. The function is identified up
to joint scaling at the point estimate; the welfare object is
well-defined despite the parameter-level indeterminacy.

(T2) *Restricted-curvature sensitivity*. Under the configuration's
`singles_consumption.restricted_sensitivity.enabled` flag, the
scaffolding additionally computes the welfare decomposition with
$\theta_{c,\text{singles}}$ fixed at its restricted value (zero
under the default, corresponding to log-utility). Under the
restriction, the singles consumption parameters are identified
and the welfare calculation is precise. The JMP reports the
unrestricted and restricted welfare decompositions side by side
for singles, per decisions memo §22.

(T3) *Separate bootstrap inference*. The bootstrap distribution
for the singles welfare decomposition is computed separately from
the bootstrap distribution for the couples welfare decomposition.
The reason is that the singles bootstrap exhibits higher variance
in the $(\beta_{c,sm}, \beta_{c,sf}, \theta_{c,\text{singles}})$
subspace than the couples bootstrap exhibits in its corresponding
subspace; joint reporting without flagging would conceal the
heterogeneity in precision.

(T4) *Documented qualification in output tables*. The scaffolding's
output tables (§25) report the singles welfare decomposition with
a footnote referencing the singles consumption limitation, per
decisions memo §22 and framework memo §10 C9. The footnote text
is templated by the scaffolding.

---

## 16. Treatment of couples

The couples sub-sample is the scaffolding's *strongest welfare
claim*. The couples utility specification is fully identified at
the M1-clean point estimate (no negative-variance entries in the
couples consumption sub-block), the couples sub-sample is the
larger sub-sample, and the couples welfare decomposition is the
JMP's headline result in the literature-positioning memo's France
2016 couples prototype framing.

The scaffolding processes couples as follows.

(T5) *Joint household welfare*. Couples welfare is a household-
level object, not a pair of individual-level objects. The
equivalent income $\Omega_i$ for a couple is the disposable-
income level that, at the reference job for both spouses,
delivers attained household utility equal to the couple's actual
attained utility under the couple's own preferences. The reference
job for couples is full-time employment for both spouses at the
median full-time wage by gender.

(T6) *Leisure-leisure interaction*. The leisure-leisure interaction
parameter $\beta_{ll}$ is part of the preference block under the
framework memo §2 classification. The scaffolding preserves
$\beta_{ll}$ at its estimated value across all counterfactual
operations; the preference-neutralised counterfactual leaves it
unchanged.

(T7) *Decomposition by gender within couples*. The decomposition
reports opportunity and ability contributions for the male spouse
and the female spouse separately, in addition to the joint
household decomposition. The gender-separated reporting is
informative for understanding within-couple inequality and is
part of the §25 output tables.

(T8) *Pooled household-type decomposition*. The scaffolding
additionally reports the decomposition on the pooled sample of all
households (singles male, singles female, couples) with appropriate
type-conditional reference values. The pooled decomposition is the
JMP's broadest welfare statement.

The couples sub-sample carries no special structural-identification
caveat. The scaffolding's couples decomposition is the welfare
result that the JMP claims most strongly.

---

## 17. Gender attribution rules A1, A2, A3

The gender attribution rules govern how gender effects in the
structural model are classified for the welfare decomposition.
The decisions memo §10 and the framework memo §4 commit the JMP
to reporting all three rules; the scaffolding implements the
parameterisation.

(A1) *Gender as ability*. Both gender-on-wage and gender-on-
arrival are classified as ability. The scaffolding equalises both
in the ability-equalisation operation; neither is equalised in the
opportunity-equalisation operation. A1 produces the smallest
opportunity contribution.

(A2) *Gender as opportunity*. Both gender-on-wage and gender-on-
arrival are classified as opportunity. The scaffolding equalises
both in the opportunity-equalisation operation; neither is
equalised in the ability-equalisation operation. A2 produces the
largest opportunity contribution.

(A3) *Split (Blau–Kahn anchor)*. Gender-on-wage counts as 40 per
cent ability and 60 per cent opportunity; gender-on-arrival counts
as 100 per cent opportunity (framework memo §4 commit). The
scaffolding implements the split by computing the equalised
covariate value as a weighted average: under A3, the ability-
equalisation sets the gender-on-wage covariate to 40 per cent of
the (full-equalisation value) + 60 per cent of (actual value), and
the opportunity-equalisation sets the gender-on-wage covariate to
60 per cent of (full-equalisation value) + 40 per cent of (actual
value). The same household receives both partial equalisations in
the preference-neutralised counterfactual.

The scaffolding accepts the attribution rule via the configuration's
`attribution.primary_rule` field. The reporting rules
(`attribution.reported_rules`) list which attribution-rule runs
are produced; the JMP's primary table reports A3 in the main
column and A1, A2 as bounds in additional columns.

A specific design consequence: the attribution rule does not
change the structural estimates. The same $\hat{\theta}$ is used
across A1, A2, A3; only the equalisation operations differ. The
attribution-rule sensitivity is therefore computationally cheap:
the scaffolding produces the three attribution-rule decompositions
on the same M1-clean run without re-estimation.

---

## 18. Inequality index module

The inequality index module computes the inequality of any welfare
distribution under a configurable index. The primary index is
Gini; the secondary indices are $CV^2$, the mean log deviation
(Theil L), and the Atkinson index at $\varepsilon = 1$ and
$\varepsilon = 2$ (decisions memo §17).

The module's interface is:

```python
def compute_inequality(
    welfare_values: np.ndarray,           # shape (n_households,)
    household_weights: np.ndarray,        # shape (n_households,)
    index: str,                            # "gini", "cv_squared", etc.
) -> float
```

The household weights are the EU-SILC survey weights, applied at
the inequality-index computation rather than at the welfare-object
computation. Survey-weighted inequality indices are the standard
in the EU-SILC tradition.

The module is invariant under the welfare-object choice (§§8–9):
the same module computes the inequality of $\Omega_i^{\text{actual}}$,
$\Omega_i^{\text{opp-eq}}$, $\Omega_i^{\text{abil-eq}}$, and
$\Omega_i^{\text{both-eq}}$. The module is invariant under the
attribution-rule choice: the same module computes the inequality
under A1, A2, A3.

A specific design note: the Gini coefficient is computed by the
standard order-statistic formula; the Theil L coefficient is
computed in log space with appropriate handling of zero or
negative welfare values (which should not occur in the JMP's
welfare distribution but are guarded against as a defensive
diagnostic).

---

## 19. Shapley decomposition module

The Shapley decomposition module allocates the difference between
total welfare inequality $I(\Omega^{\text{actual}})$ and the
preference-contribution residual $I(\Omega^{\text{both-eq}})$
across the opportunity and ability factors, with the order-
independent Shapley-Shorrocks rule (decisions memo §18).

The module's interface is:

```python
def shapley_decomposition(
    inequality_actual: float,
    inequality_opp_eq: float,
    inequality_abil_eq: float,
    inequality_both_eq: float,
) -> dict
```

The return value is a dictionary with keys: `opportunity_share`,
`ability_share`, `preference_share`, `total_inequality`, and
`shapley_residual` (the diagnostic showing that the three shares
sum to the total inequality; if not, a numerical-precision
warning is emitted).

Under the three-way decomposition, the Shapley shares are computed
as averages over the $3! = 6$ orderings of factor removal. Under
the two-way collapse (opportunity-or-ability versus preference
under strong-Roemer, or opportunity versus ability-or-preference
under weak-Dworkin), the shares are computed over the relevant $2!
= 2$ orderings. The module supports both via a
`collapse_mode` keyword argument.

A specific design consequence: the Shapley decomposition requires
only the four inequality values, not the underlying welfare
distributions. The module is therefore lightweight and is invoked
many times per scaffolding run (once per inequality index, once
per attribution rule, once per bootstrap replicate). The
decomposition is robust to numerical noise in the underlying
inequality values, which the module documents in its diagnostic
output.

The module's correctness is verified by a unit test that the
Shapley shares sum to the total inequality reduction; this test is
part of the §28 module test suite.

---

## 20. Ordered-removal diagnostic module

The ordered-removal decomposition module is the secondary
decomposition rule (decisions memo §18). It computes the
opportunity, ability, and preference contributions under a
specific factor-removal ordering, and the interaction term as the
residual.

The module's interface is:

```python
def ordered_removal_decomposition(
    inequality_actual: float,
    inequality_opp_eq: float,
    inequality_abil_eq: float,
    inequality_both_eq: float,
    ordering: tuple,                       # ("opportunity", "ability") or ("ability", "opportunity")
) -> dict
```

The return value is a dictionary with keys: `opportunity_share`,
`ability_share`, `preference_share`, `interaction_term`, and
`total_inequality`. Under ordered removal, the four entries sum
exactly to the total inequality, with the interaction term as a
separate quantity rather than being dissolved.

The module reports the ordered-removal decomposition under both
orderings (opportunity-first and ability-first) so that the
ordering dependence is transparent. The framework memo §5 commits
to reporting the interaction term as a separate quantity under
this rule.

The module's primary role is *diagnostic*. The JMP's headline
results are the Shapley shares (§19); the ordered-removal
decomposition is reported alongside as a robustness check on the
ordering-independence claim of the Shapley method.

---

## 21. Bootstrap / uncertainty interface

The bootstrap orchestration is external to the scaffolding (§4),
but the scaffolding exposes a bootstrap interface that the
orchestration script invokes once per replicate.

The interface is:

```python
def compute_welfare_decomposition(
    config: WelfareConfig,                 # parsed from §7 YAML
    theta_hat: np.ndarray,                 # the (possibly bootstrap-replicate) parameter vector
    output_directory: str,                 # the timestamped output directory
) -> WelfareDecompositionResult
```

The function is the scaffolding's *single public entry point*. It
consumes the configuration, the parameter vector, and the output
directory, and produces a structured result containing the four
welfare distributions, the inequality indices, the Shapley and
ordered-removal decompositions, and the diagnostic flags.

The bootstrap orchestration script:

1. Loads the configuration.
2. Loads the point-estimate parameter vector from (S1).
3. Calls `compute_welfare_decomposition` with the point-estimate
   parameters and the primary output directory; this is the
   *headline* welfare decomposition.
4. For $b = 1, \ldots, B$ bootstrap replicates:
   a. Calls the estimation layer to re-fit the structural model
      on a household-cluster-resampled bootstrap sample,
      producing a replicate parameter vector
      $\hat{\theta}^{(b)}$;
   b. Calls `compute_welfare_decomposition` with
      $\hat{\theta}^{(b)}$ and a replicate output directory;
5. Aggregates the bootstrap replicates' decomposition results
   into bootstrap confidence intervals.

The bootstrap orchestration is computationally expensive
(re-estimation of the structural model on each replicate). The
scaffolding is therefore designed to be cleanly invocable as a
function-of-$\hat{\theta}$, so that the bootstrap orchestration
can parallelise across replicates without internal scaffolding
state being held across invocations.

Under the single-year M1-clean regime, the bootstrap resamples
households independently. Under the pooled regime, the bootstrap
resamples household *clusters* (the 8,796 repeat households of
2016–2017 are resampled as units), per the multi-year memo §2 P3.
The cluster unit is declared in the configuration's
`inference.cluster_unit` field.

The bootstrap output is a parquet file with one row per replicate,
columns for each decomposition component. The aggregation into
confidence intervals is performed by a post-processing script that
is part of the scaffolding but separable from the per-replicate
computation.

---

## 22. M1-clean primary run

The M1-clean primary run is the JMP's headline scaffolding
execution. The run consumes the M1-clean parameter vector at the
SA1-STANDS accepted point estimate, the M1-clean YAML, the GSURv2
MNL parquets, and the M1-clean welfare configuration. It produces
the headline opportunity / ability / preference decomposition under
the primary attribution rule (A3), the primary inequality index
(Gini), the primary decomposition rule (Shapley), and the primary
reference choices.

The M1-clean primary run is configured by:

```yaml
baseline:
  identifier: "ruro_occ_M1_clean"
  regime: "single_year"
  parameter_parquet_path:
    "outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/parameters.parquet"
  estimation_spec_yaml_path:
    "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml"
  acceptance_verdict_path:
    "docs/RURO_occ_M1_clean_verdict_v1.md"
  euromod_system_version:
    - "FR_2016_a3"
```

(The remaining configuration fields take their defaults per §7.)

The M1-clean primary run is the welfare decomposition that the
JMP's main results table reports. The first-prototype output set
(decisions memo §23) is produced from this run.

The M1-clean primary run is *not* authorised by this memo. It is
authorised by a subsequent welfare-decomposition computation
prompt that follows the welfare scaffolding implementation and the
welfare scaffolding verdict.

---

## 23. M1-naive robustness run

The M1-naive robustness run is the scaffolding's R2 sensitivity
exposure (framework memo §8 R2 and decisions memo §10). The run
consumes the M1-naive parameter vector at LL = $-6485.5287$, the
M1-naive YAML (with $\beta_{E\,\text{educH}}$ in the opportunity
block), the same GSURv2 MNL parquets, and an M1-naive welfare
configuration that differs from the M1-clean configuration only
in the `baseline` block:

```yaml
baseline:
  identifier: "ruro_occ_M1_naive"
  regime: "single_year"
  parameter_parquet_path:
    "outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/parameters.parquet"
  estimation_spec_yaml_path:
    "scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml"
  acceptance_verdict_path:
    "docs/RURO_occ_M1_naive_robustness_verdict_v1.md"
  euromod_system_version:
    - "FR_2016_a3"
```

The M1-naive run produces the same decomposition outputs as the
M1-clean run, but on the M1-naive parameter vector and with the
M1-naive opportunity-block covariate list (which additionally
includes the education covariate). The two runs differ in the
covariate-side equalisation operations: under M1-naive, the
opportunity equalisation includes education, and the ability
equalisation excludes education. Under M1-clean, the reverse.

The M1-naive robustness run is reported alongside the M1-clean
primary run in the JMP's robustness table (§25). The numerical
difference between the two decompositions is the "ability-mediated
opportunity" of the framework memo §3 — the inequality that the
older RURO literature attributes to opportunity but that the JMP
attributes to ability through the wage channel.

The M1-naive robustness run is *not* authorised by this memo. It
is authorised by the same subsequent welfare-decomposition
computation prompt that authorises the M1-clean primary run.

---

## 24. Pooled-specification compatibility if SA2-STANDS later occurs

The scaffolding is designed so that a hypothetical SA2-STANDS
verdict promoting a pooled multi-year specification to the primary
baseline can be accommodated by a single configuration change. The
mechanism is the following.

(C1) The pooled parameter vector $\hat{\theta}_{\text{pooled}}$ is
read from the pooled run's converged-estimates parquet path,
declared in the configuration's `baseline.parameter_parquet_path`
field. No scaffolding code change is required.

(C2) The pooled YAML
(`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean_pooled.yaml`,
or the analogous pooled spec name) declares the opportunity-block
covariate list with year fixed effects included. The scaffolding
reads the YAML and constructs the reference opportunity set with
year fixed effects set to the reference year (decisions memo §13).
No scaffolding code change is required.

(C3) The pooled MNL alternative-set parquet is the stacked multi-
year MNL parquet at the path declared in the configuration's
`baseline.mnl_alternative_set_path` field. The schema is invariant
across single-year and pooled regimes; the scaffolding operates on
the schema.

(C4) The cluster-robust bootstrap is activated by setting the
configuration's `baseline.regime` field to `"pooled"`. The
scaffolding does not change; the bootstrap orchestration script
detects the regime and resamples household clusters rather than
household-year observations.

(C5) The baseline welfare distribution under the pooled regime is
the 2016 cross-section evaluated under the pooled parameter vector
(decisions memo §13 primary choice). The scaffolding extracts the
2016 sub-sample from the pooled MNL parquet via a year filter and
applies it to the welfare-object construction. The pooled-cross-
section sensitivity and the reweighted-2016 sensitivity are
exercised by alternative configuration values in the
`baseline_distribution.pooled.sensitivity` list.

(C6) The strong-Roemer interpretation under pooling, addressed by
the multi-year memo §14 O4, is handled by the same attribution-
rule machinery as the single-year regime. The within-circumstance
variation under pooled estimation includes within-household across-
year variation; the scaffolding does not need to distinguish this
from cross-household within-year variation because the
opportunity-equalisation operation equalises year fixed effects as
part of the opportunity covariate list, which absorbs the
across-year variation into the opportunity contribution rather
than the preference residual. This is the decisions memo §13
treatment of O4.

The pooled-specification compatibility is therefore *complete at
the scaffolding design level*. No code change is required to
switch from M1-clean to a future SA2-promoted pooled baseline.
The pooled run is not authorised by this memo or by any
subsequent prompt until the SA2 verdict produces SA2-STANDS.

---

## 25. Output tables

The scaffolding produces the following tables. All tables are
written to the configuration's `output.table_directory` as parquet
files with companion CSV exports for human inspection.

(T1) *Primary decomposition table*. Rows: total welfare inequality
on $\Omega_i^{\text{actual}}$, opportunity contribution, ability
contribution, preference contribution, opportunity-ability
interaction (under ordered-removal; Shapley residual diagnostic).
Columns: singles male, singles female, couples, pooled all
households. Sub-columns: point estimate, bootstrap 2.5th
percentile, bootstrap 97.5th percentile. Filename:
`table_primary_decomposition__{baseline_identifier}.parquet`.

(T2) *Gender-attribution-rule sensitivity table*. Rows as in T1.
Columns: A1, A2, A3. Single-sample (pooled all households). The
rule columns are *not* mutually exclusive sub-columns; they are
three full decompositions reported side by side. Filename:
`table_gender_attribution__{baseline_identifier}.parquet`.

(T3) *M1-clean / M1-naive sensitivity row*. A single row that
appends to T1, reporting the M1-naive equivalent decomposition.
Filename: `table_m1_naive_robustness.parquet` (produced only by
the M1-naive robustness run; the row is post-processed into T1 for
the JMP's main paper table).

(T4) *Reference-set sensitivity table*. Rows: opportunity
contribution, ability contribution, preference contribution.
Columns: primary reference, mean reference, best-available
reference, type-pooled reference. Filename:
`table_reference_set_sensitivity__{baseline_identifier}.parquet`.

(T5) *Inequality-index sensitivity table*. Rows as in T1.
Columns: Gini, $CV^2$, Theil L, Atkinson $\varepsilon = 1$,
Atkinson $\varepsilon = 2$. Filename:
`table_inequality_index_sensitivity__{baseline_identifier}.parquet`.

(T6) *Welfare-measure sensitivity table*. Rows as in T1. Columns:
equivalent income, CV, EV, Atkinson-equivalent at $\varepsilon = 1$,
Atkinson-equivalent at $\varepsilon = 2$. Filename:
`table_welfare_measure_sensitivity__{baseline_identifier}.parquet`.

(T7) *Decomposition-rule sensitivity table*. Rows as in T1.
Columns: Shapley three-way, Shapley two-way (weak-Dworkin), Shapley
two-way (strong-Roemer), ordered-removal opportunity-first,
ordered-removal ability-first. Filename:
`table_decomposition_rule_sensitivity__{baseline_identifier}.parquet`.

(T8) *Singles consumption restricted-sensitivity table*. The
singles sub-sample's decomposition under the unrestricted singles
consumption (the primary) and under the restricted singles
consumption ($\theta_{c,\text{singles}} = 0$, log-utility). Filename:
`table_singles_consumption_restricted__{baseline_identifier}.parquet`.

The first-prototype output (decisions memo §23) consists of T1,
T2, T3, and T4. Tables T5, T6, T7, T8 are produced by the same
scaffolding code under expanded configuration but are not part of
the first-prototype deliverable.

---

## 26. Output figures

The scaffolding produces the following figures, written to
`output.figure_directory` as PDF files with companion PNG exports.

(F1) *Baseline welfare distribution density*. Single panel; three
densities (singles male, singles female, couples) of
$\Omega_i^{\text{actual}}$. Filename:
`figure_baseline_welfare_density__{baseline_identifier}.pdf`.

(F2) *Opportunity-equalised welfare cut*. Single panel; scatter of
$\Omega_i^{\text{actual}}$ versus $\Omega_i^{\text{opp-eq}}$ across
households, with the 45-degree diagonal. Households below the
diagonal experience opportunity-driven welfare gain under
equalisation; households above the diagonal experience opportunity-
driven welfare loss. The cloud's vertical width measures the
opportunity contribution. Filename:
`figure_opportunity_equalisation_cut__{baseline_identifier}.pdf`.

(F3) *Decomposition bar chart*. Single panel; stacked bar chart
showing the three components (opportunity, ability, preference) as
fractions of total welfare inequality, by household type and under
each gender attribution rule. Filename:
`figure_decomposition_bar_chart__{baseline_identifier}.pdf`.

(F4) *Reference-set sensitivity bar chart*. Single panel; bar chart
showing the opportunity contribution under each reference-set
choice (primary, mean, best-available, type-pooled), with
bootstrap whiskers. Filename:
`figure_reference_set_sensitivity__{baseline_identifier}.pdf`.

(F5) *M1-clean vs M1-naive comparison*. Single panel; side-by-side
bar charts of the opportunity, ability, and preference
contributions under the two baselines. The numerical gap visualises
the "ability-mediated opportunity" diagnosis. Filename:
`figure_m1_clean_vs_m1_naive_comparison.pdf` (produced only after
both the M1-clean primary run and the M1-naive robustness run are
complete).

The first-prototype output (decisions memo §23) consists of F1,
F2, F3. Figures F4 and F5 are produced by the same scaffolding
code under expanded configuration but are not part of the first-
prototype deliverable.

---

## 27. Required diagnostics before interpreting results

The scaffolding produces a set of diagnostic outputs that must
pass before the welfare-decomposition results are interpretable.
The diagnostics are part of the welfare-scaffolding verdict that
will follow implementation; this memo specifies which diagnostics
are required.

(D1) *Inversion convergence*. For each household and each
counterfactual, the equivalent-income inversion must converge to
within a tolerance of $10^{-6}$ on the attained-utility match. The
scaffolding emits a diagnostic file
`diagnostics_inversion_convergence__{baseline_identifier}.parquet`
listing any household × counterfactual combination that failed to
converge. Failures must be zero in the headline run; non-zero
failures are a result-blocking finding.

(D2) *Bootstrap convergence*. For each bootstrap replicate, the
estimation layer's re-estimation must converge. The bootstrap
orchestration emits a convergence-status parquet; any replicate
that failed to converge is excluded from the confidence-interval
aggregation, with the exclusion rate reported as a diagnostic.
Exclusion rates above 5 per cent are a result-blocking finding.

(D3) *Reference-bundle consistency*. The reference job's hours
and wage, combined with the reference opportunity set's tax-
benefit treatment, must produce a consumption-leisure point within
a tolerance of 5 per cent of $(c^*, \ell^*)$. The scaffolding
emits a diagnostic file
`diagnostics_reference_consistency__{baseline_identifier}.parquet`.
Failures are a result-blocking finding.

(D4) *Singles consumption joint-function validity*. The singles
consumption function $c \mapsto \beta_{c,g} \cdot c^{\theta_{c,\text{singles}}}$
must be monotone increasing in $c$ across the welfare-relevant
consumption range. Negative or non-monotone values are a
diagnostic flag. The check is implemented in the singles welfare
module (§15) and emits
`diagnostics_singles_consumption_validity__{baseline_identifier}.parquet`.

(D5) *Shapley-residual diagnostic*. The Shapley shares' sum must
equal the total inequality reduction to within a tolerance of
$10^{-8}$. The decomposition module (§19) emits the diagnostic.
Failures are an implementation defect.

(D6) *Attribution-rule consistency*. Under attribution rule A3,
the sum of the gender-on-wage ability-share and the gender-on-wage
opportunity-share must equal the full gender-on-wage coefficient
contribution. The scaffolding emits the diagnostic.

(D7) *Specification-baseline traceability*. The output tables and
figures must record the baseline identifier, the parameter vector
hash, the configuration hash, and the welfare-scaffolding code
version. This is a provenance diagnostic; absence is a result-
blocking finding.

(D8) *Pooled-regime year-equalisation check*. Under the pooled
regime, the opportunity-equalisation operation must include year
fixed effects in the equalised covariate list. The scaffolding
emits the diagnostic
`diagnostics_pooled_year_equalisation__{baseline_identifier}.parquet`.
Absence under pooled regime is a result-blocking finding.

The required diagnostics are produced by the scaffolding as a
matter of course; they are not optional. The welfare-scaffolding
verdict will require all eight diagnostics to pass before the
welfare-decomposition results are interpretable.

---

## 28. Code modules to create

The scaffolding is organised into the following Python modules,
collectively forming a new top-level directory
`scripts/welfare/` parallel to `scripts/enhanced/`. The module
list is fixed by this memo; the implementation prompt creates each
module per this specification.

```
scripts/welfare/
├── __init__.py
├── config.py
│       Parses the §7 YAML configuration into a typed `WelfareConfig`
│       object. Validates schema. Computes configuration hash for
│       provenance. Resolves baseline-specific paths.
│
├── inputs.py
│       Loads the structural inputs (S1–S4 of §5) and the MNL
│       alternative-set inputs (M1–M4 of §6). Builds the reference
│       distribution parquet (M3) on first invocation. Read-only.
│
├── references.py
│       Constructs the reference bundle (§10), reference job (§10),
│       and reference opportunity set (§11) under the configured
│       primary and sensitivity choices.
│
├── welfare_object.py
│       Implements the equivalent-income inversion (§8) and the
│       secondary welfare objects (§9). Exposes a single function
│       `compute_omega(theta_hat, household_inputs, reference, welfare_object_type)`.
│
├── counterfactuals.py
│       Implements the three counterfactual operations (§§12–14).
│       Modifies covariate inputs to `welfare_object.compute_omega`
│       per the equalisation rule and the attribution rule.
│
├── attribution.py
│       Implements the A1, A2, A3 attribution rules (§17).
│       Determines which covariates are equalised under which
│       counterfactual.
│
├── singles.py
│       Implements the singles-specific treatment (§15). Operates
│       on the joint singles consumption function. Implements the
│       restricted-curvature sensitivity.
│
├── couples.py
│       Implements the couples-specific treatment (§16). Handles the
│       leisure-leisure interaction and the gender-separated
│       decomposition.
│
├── inequality.py
│       Implements the inequality-index module (§18). Five indices
│       under a uniform interface.
│
├── shapley.py
│       Implements the Shapley-Shorrocks decomposition module (§19).
│       Three-way and two-way collapse variants.
│
├── ordered_removal.py
│       Implements the ordered-removal decomposition module (§20).
│       Both orderings, with the interaction term as a separate
│       quantity.
│
├── diagnostics.py
│       Produces the eight required diagnostics (§27) at each
│       scaffolding invocation.
│
├── tables.py
│       Constructs the eight output tables (§25) from the scaffolding
│       results. Writes parquet and CSV.
│
├── figures.py
│       Constructs the five output figures (§26). Writes PDF and PNG.
│
├── bootstrap_interface.py
│       Defines the single public entry point
│       `compute_welfare_decomposition(config, theta_hat, output_directory)`
│       (§21). Invoked once per bootstrap replicate by the
│       orchestration script.
│
├── orchestration/
│   ├── __init__.py
│   ├── run_primary.py
│   │       Orchestrates the M1-clean primary run (§22).
│   ├── run_robustness_m1_naive.py
│   │       Orchestrates the M1-naive robustness run (§23).
│   ├── run_pooled.py
│   │       Orchestrates a pooled-specification run if SA2-STANDS later
│   │       occurs (§24). Not invoked under current authorisation.
│   └── bootstrap.py
│           Orchestrates the bootstrap re-estimation and the per-replicate
│           scaffolding invocation. Handles cluster-robust resampling under
│           pooled regime.
│
└── tests/
    ├── test_inequality.py
    ├── test_shapley.py
    ├── test_ordered_removal.py
    ├── test_counterfactuals.py
    ├── test_attribution.py
    ├── test_welfare_object.py
    └── test_diagnostics.py
```

The module layout enforces the design principles of this memo:
specification-agnostic input boundary (`config.py`, `inputs.py`),
modular counterfactual construction (`counterfactuals.py`),
modular decomposition rules (`shapley.py`, `ordered_removal.py`),
modular welfare-measure switching (`welfare_object.py`), and clean
separation of the scaffolding from the bootstrap orchestration
(`bootstrap_interface.py` versus `orchestration/bootstrap.py`).

The tests directory contains unit tests for the core modules. The
welfare-scaffolding verdict will require the tests to pass before
the welfare-decomposition computation is authorised.

---

## 29. File and folder outputs

The scaffolding's outputs are organised under
`outputs/welfare/` parallel to `outputs/estimates/`. The structure
is:

```
outputs/welfare/
├── runs/
│   └── {baseline_identifier}__{config_hash}__{timestamp}/
│       ├── config_resolved.yaml          # provenance copy of the configuration
│       ├── parameter_vector_hash.txt     # hash of the input theta_hat
│       ├── welfare_object_parquet.parquet
│       ├── counterfactual_omega_opp_eq.parquet
│       ├── counterfactual_omega_abil_eq.parquet
│       ├── counterfactual_omega_both_eq.parquet
│       ├── diagnostics/
│       │   ├── diagnostics_inversion_convergence.parquet
│       │   ├── diagnostics_reference_consistency.parquet
│       │   ├── diagnostics_singles_consumption_validity.parquet
│       │   ├── diagnostics_shapley_residual.parquet
│       │   ├── diagnostics_attribution_consistency.parquet
│       │   ├── diagnostics_specification_traceability.parquet
│       │   └── diagnostics_pooled_year_equalisation.parquet
│       └── tables/
│           └── (the §25 T1–T8 tables, scoped to this run's baseline)
├── bootstrap/
│   └── {baseline_identifier}__{config_hash}__{timestamp}/
│       ├── replicates/
│       │   └── replicate_{b:04d}/
│       │       └── (per-replicate scaffolding output)
│       ├── replicate_convergence_status.parquet
│       └── confidence_intervals.parquet
├── tables/
│   └── (the §25 tables aggregated across baselines, for the JMP paper)
├── figures/
│   └── (the §26 figures)
└── reports/
    └── (markdown welfare reports, produced after computation)
```

The `runs/` directory contains one sub-directory per scaffolding
invocation, with full provenance. The `bootstrap/` directory
contains the bootstrap orchestration's per-replicate outputs and
the aggregated confidence intervals. The `tables/` and `figures/`
directories contain the JMP paper deliverables, post-processed from
the runs and bootstrap outputs.

The output structure is provenance-complete. Any welfare result
in the JMP paper can be traced back to: the configuration that
produced it; the parameter vector hash; the scaffolding code
version; and the diagnostic status of the run. This is the
requirement of decisions memo §25 I12 (output reproducibility).

---

## 30. What remains blocked

The following items remain explicitly blocked by this memo and by
the authorisation cascade:

(B1) *Welfare-decomposition computation*. This memo authorises the
design of the scaffolding, not its operation. Computation on any
baseline (M1-clean primary or M1-naive robustness) requires a
separate welfare-decomposition computation prompt that postdates
the welfare-scaffolding verdict.

(B2) *Welfare-scaffolding implementation*. This memo authorises
the design; the implementation prompt that consumes this memo and
produces the `scripts/welfare/` code is a separate Claude Code
Sonnet task, with its own verdict.

(B3) *Canonical MNL promotion (the O10 decision)*. The versioned
GSURv2 MNL parquets remain the operative data source for both the
M1-clean primary and the M1-naive robustness runs. Promotion of any
data product to a canonical name is separately gated and is not
within this memo's scope.

(B4) *Stage B age-specific GSUR (the O6 decision)*. Age-specific
GSUR remains deferred. The scaffolding's market-opportunity
covariate handling treats the corrected GSUR as a single block;
under any future activation of age-specific GSUR, the YAML
declaration would change and the scaffolding would automatically
adapt.

(B5) *Modification of M1-clean, M1-naive, or any frozen-block
element*. The scaffolding operates on the M1-clean and M1-naive
estimates as fixed inputs. Any structural specification change
would require a separate design and verdict cascade.

(B6) *Pooled multi-year estimation*. Pooled estimation is gated on
the multi-year feasibility audit, the multi-year pipeline
implementation stages, the pooled-specification estimation, and the
SA2 verdict. The scaffolding's pooled-regime compatibility (§24)
enables a future pooled welfare decomposition but does not
authorise the estimation itself.

(B7) *The François Maniquet pure-theory paper*. The scaffolding
operationalises the equivalent-income welfare object that the
theory paper articulates; it does not implement the theory paper.
The JMP remains a distinct empirical paper.

The blocked items are not blocked by oversight. They are blocked
by the same gating philosophy that governed M0c → M0c_b →
M0c_b2 → M0c_b2_GSURv2 → M1-clean → M1-naive: each substantive
step has its own design memo, its own implementation prompt, its
own deliverables, and its own verdict. The welfare scaffolding
follows the same discipline.

---

## 31. Immediate coding task after this memo

The immediate task following this memo is *not* the welfare
scaffolding implementation. The welfare scaffolding design is now
locked, but its implementation is sequenced *after* the multi-year
feasibility audit clarifies whether the near-term structural-
baseline path remains single-year M1-clean or moves toward an SA2
pooled estimation. The §24 pooled-compatibility guarantees ensure
that the implementation will not need to be rewritten under either
outcome; what the audit settles is the *order* in which the
welfare layer should be implemented and exercised.

The immediate task is therefore the *multi-year feasibility
audit*, to be executed in Claude Code Sonnet (local codebase, data
inspection and feasibility verification) per the v3.1 multi-year
strategy memo §13 Step 4 and the M1-naive robustness verdict §17.

Tool: Claude Code Sonnet.

Inputs to the feasibility audit prompt:
- `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the multi-year strategy; the audit operationalises §4
  feasibility conditions F1–F6 and §6 identifier encoding
  elements I3 and I6).
- `docs/RURO_occ_M1_naive_robustness_verdict_v1.md` §17 (the
  authorising verdict for the audit).
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the SA1-STANDS reference
  baseline against which any future pooled specification will be
  compared at the SA2 verdict).
- `euromod_fr_2015_2017_output_variable_index.csv` (the EUROMOD FR
  output-variable inventory used in F6 comparability).
- The local raw inventory at `U:\EUROMOD-STORAGE\Data\FR` for the
  FR_2015, FR_2016, and FR_2017 cross-sections.

Output deliverable of the feasibility audit:
- `Results/JMP_multi_year_feasibility_audit_v1.md`, recording the
  status of each F1–F6 condition, the maximum identifier
  magnitudes required by the §6 I3 numerical encoding (operational
  default base $B = 10^{11}$), the canonical clustering key
  (`idhh_raw` or `idorighh_raw`) per §6 Element I6, and an
  authorisation recommendation for the subsequent multi-year
  pipeline implementation stages.

The audit does not authorise pooled estimation, welfare
scaffolding implementation, welfare-decomposition computation,
canonical MNL promotion, or Stage B age-specific GSUR. Its
deliverable is a feasibility report; the substantive
authorisations follow from subsequent verdicts.

The welfare scaffolding implementation is sequenced *after* the
audit, at a point determined by the audit's findings. Two
sequencing paths are possible.

*Path A — single-year M1-clean remains the operational baseline.*
If the audit concludes that pooled-estimation feasibility is
non-trivial (one or more of F1–F6 fails or requires substantial
additional infrastructure) or that the pooled pipeline cannot be
delivered within the JMP's near-term horizon, the welfare
scaffolding is implemented next, against M1-clean as the primary
input. The implementation prompt (described below) is then the
immediate post-audit task.

*Path B — pooled-estimation path advances.* If the audit
concludes that pooled estimation is feasible and the pooled
pipeline implementation is sequenced next, the welfare scaffolding
implementation is deferred until the SA2 verdict resolves the
primary structural baseline. The implementation prompt is then
sequenced after the SA2 verdict, with the same design but with
the configuration `baseline.regime` set to `"pooled"` per §24. The
scaffolding code is the same; only the configuration changes.

Under both paths the scaffolding *design* in this memo is
unchanged. The design is locked now; the implementation is
sequenced later.

For provenance, the welfare-scaffolding implementation prompt —
when it is eventually authorised — will consume the following
inputs and produce the following deliverables.

Inputs to the (later) implementation prompt:
- This memo (the design specification).
- `docs/JMP_welfare_measurement_decisions_memo_v1.md` (the locked
  welfare-measurement decisions).
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the SA1-STANDS baseline)
  and, under Path B, the SA2-verdict document for the promoted
  pooled specification.
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  framework memo's C1–C9 code contract).
- The operative-baseline YAML
  (`estimation_spec_ruro_occ_M1_clean.yaml` under Path A; the
  pooled-spec YAML under Path B) plus
  `estimation_spec_ruro_occ_M1_naive.yaml` for the R2 robustness
  exposure.
- `Results/JMP_multi_year_feasibility_audit_v1.md` (the audit
  output), which records the regime under which the scaffolding
  will operate.

Output deliverables of the (later) implementation prompt:
- The `scripts/welfare/` module tree per §28.
- The unit tests under `scripts/welfare/tests/` per §28.
- Reference welfare configuration files
  `scripts/welfare/configs/welfare_config_primary.yaml` and
  `scripts/welfare/configs/welfare_config_robustness.yaml`
  pointing to the operative-baseline parameter parquets.
- `Results/RURO_welfare_scaffold_implementation_report_v1.md`
  documenting modules created, tests passing, dry-run diagnostics,
  and any deviation from this design.

The implementation prompt will produce the scaffolding code and
verify by unit tests and dry-run invocation that the scaffolding
meets the design. It will not run the welfare decomposition; that
authorisation is a further-downstream prompt that postdates the
welfare-scaffolding verdict.

In parallel with the implementation, a *welfare-scaffolding audit
specification* may be drafted in Claude Project chat (analogous to
the M1-clean design memo §22 SA1 acceptance rule). The audit
specification articulates the verdict criteria the implementation
will be evaluated against. It can be drafted at any point after
this memo is locked, including in parallel with the multi-year
feasibility audit.

Items explicitly not authorised by this memo or by the immediate
audit prompt:
- Welfare-scaffolding implementation in code (deferred per path
  selection above).
- Welfare-decomposition computation on M1-clean or M1-naive.
- Any modification of the M1-clean, M1-naive, or M0c_b2_GSURv2
  estimates.
- Canonical MNL promotion of any data product (the O10 decision).
- Stage B age-specific GSUR work (the O6 decision).
- Pooled multi-year estimation (sequenced post-audit per the v3.1
  multi-year strategy memo).
- The François Maniquet pure-theory paper.

---

**Status and authorisation summary.**

**Authorised by this memo**: the welfare-scaffolding code
architecture design. The module structure of §28, the configuration
schema of §7, the input-boundary contract of §§5–6, the output
structure of §§25–26, the diagnostic requirements of §27, and the
M1-clean primary and M1-naive robustness run configurations of
§§22–23 are all locked.

**Not authorised by this memo**: welfare-scaffolding implementation
(in code); welfare-decomposition computation (on any baseline);
canonical MNL promotion (O10); Stage B age-specific GSUR (O6);
modification of the M1-clean, M1-naive, or any frozen-block
specification; pooled multi-year estimation; the François Maniquet
pure-theory paper.

**Pending under separate verdicts**: the multi-year feasibility
audit and its findings, which determine the sequencing of
welfare-scaffolding implementation under Path A or Path B; the
welfare-scaffolding implementation prompt and its verdict, gated
on this memo and on the audit's path selection; the welfare-
decomposition computation, gated on the welfare-scaffolding
verdict; the SA2 verdict on a potential pooled-specification
replacement of M1-clean, gated on the multi-year pipeline.

**Status of M1-clean as preferred structural baseline**: unchanged.
M1-clean is SA1-STANDS and is the scaffolding's primary input
under Path A and the comparison reference under Path B.

**Status of M1-naive**: a robustness exposure, processed by the
scaffolding under §23 as the R2 sensitivity. M1-naive is not the
primary baseline.

**Status of the JMP relative to the François Maniquet pure-theory
paper**: distinct. The scaffolding operationalises the equivalent-
income welfare object; it does not implement the theory paper. The
JMP remains a distinct empirical contribution.
