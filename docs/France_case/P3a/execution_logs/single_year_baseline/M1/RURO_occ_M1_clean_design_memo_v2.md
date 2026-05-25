# RURO occ M1-clean — Design Memo v2

Date: 2026-05-18

Revision history: v2 supersedes v1. Five revisions are applied: (i)
path references updated to the `scripts/enhanced/specifications/`
canonical location for YAML files and the actual location of the
framework memo; (ii) the region-dummy column-name commitment is
relaxed in favour of an implementation-audit-driven choice;
(iii) the sample-size argument for the seven-dummy design is
softened from "identification requires" to "support is sufficient
to attempt"; (iv) the M1-naive description is reconciled with the
relaxed column commitment; (v) the SA1 acceptance thresholds are
explicitly labelled as *proposed* M1-clean criteria selected for
this memo, not inherited rules. All substantive content from v1 is
preserved.

Specification class: structural design memo for the next RURO
baseline iteration following `ruro_occ_M0c_b2_GSURv2`. The memo
specifies the intended changes, parameter accounting, identification
rationale, and acceptance criteria for `ruro_occ_M1_clean`. It does
not authorise estimation, code modification, welfare computation,
or canonical parquet promotion.

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the accepted working
  baseline)
- `Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md`
- `Results/P3a/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md`
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  conceptual framework; its regional design is superseded by this
  memo)
- `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md` §16 (the frozen
  blocks that M1-clean preserves)
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
  (the working YAML; the M1-clean YAML is derived from this file)

Scope of this memo: a specification design for a single, well-defined
structural step. The memo respects the boundary between the empirical
RURO JMP and the separate François Maniquet theory paper on jobs and
well-being; references to the theoretical framework are limited to
the conceptual machinery already operationalised in the framework
memo.

---

## 1. Purpose of M1-clean

M1-clean is the specification through which the JMP's normative
partition — distinguishing *opportunity*, *ability*, and *preferences*
in the determination of money-metric well-being — becomes operative
in the structural estimation. Where `ruro_occ_M0c_b2_GSURv2` is a
data-corrected baseline that retains the legacy M0c family's
parameterisation of the market-opportunity block, M1-clean is the
first specification in which the market-opportunity block is
conceptually aligned with the JMP's welfare apparatus.

Concretely, M1-clean implements two structural amendments to the
market-opportunity block of M0c_b2_GSURv2. It excludes individual
education from the opportunity-side index, on the grounds that
education attainment is informationally treated under the JMP's weak
Dworkinian welfare criterion as an ability dimension rather than a
circumstance for which individuals are entitled to compensation. It
introduces region of residence as an explicit shifter of the
employment-opportunity index, on the grounds that the regional
labour market — over and above the demographic-conditional regional
unemployment rate captured by the corrected GSUR variable — is a
circumstance for which individuals are not normatively responsible.

The estimated coefficients of M1-clean are not in themselves the
JMP's welfare results. They are the inputs from which the
opportunity-driven and preference-driven components of money-metric
well-being inequality will be constructed in a subsequent welfare-
scaffolding stage. M1-clean's purpose is therefore primarily to
furnish a structural baseline whose decomposition has interpretable
welfare meaning.

---

## 2. Why M1-clean is needed after M0c_b2_GSURv2

The GSURv2 correction resolved the regional misalignment, sex
stratification, and education stratification problems in the
canonical GSUR variable. It did not, however, reclassify the
parameters that absorb education and region effects. In particular,
under M0c_b2_GSURv2 the parameter `beta_E_educH` continues to enter
the market-opportunity block, where it captures a residual
education-on-opportunity effect of estimated magnitude +0.439 with
standard error 0.226 and p-value 0.052.

Three considerations make this configuration untenable as the JMP's
preferred specification.

First, the conceptual difficulty: under the ability/opportunity
partition documented in the framework memo, education attainment is
the canonical example of an ability dimension. Allowing education
to enter the opportunity-side index produces a structural model in
which the *same* education variable simultaneously affects the
wage-opportunity block (correctly, as a market price signal) and the
employment-opportunity block (problematically, as if education
attainment were a circumstance for which agents are not responsible).
Welfare decompositions built on top of M0c_b2_GSURv2 would inherit
this conceptual ambiguity.

Second, the empirical signal: the corrected GSUR variable is itself
education-stratified. The decline of `beta_E_educH` from +0.613
(p < 0.01) in M0c_b2 to +0.439 (p = 0.052) in M0c_b2_GSURv2 is
prima facie evidence that the v1 estimate was partially absorbing
the education-region correlation that the corrected GSUR now resolves.
The remaining +0.439 coefficient is plausibly a residual
education-on-opportunity effect that should either be reattributed
to ability or, if it survives a region-controlled specification,
preserved as a marginal opportunity effect for robustness purposes.
This question cannot be answered without an explicit specification
in which education is excluded from opportunity and region is
explicitly included; M1-clean is that specification.

Third, the symmetry of treatment: if region is an opportunity-side
circumstance — a proposition the JMP framework treats as
self-evident under any plausible welfare criterion — then region
should appear in the opportunity block. Under M0c_b2_GSURv2,
region enters only through GSUR, which is a demographically
conditional unemployment rate aggregated to the eight metropolitan
EUROMOD groupings. M0c_b2_GSURv2 therefore identifies the
opportunity effect of region only insofar as it operates through
the demographically conditional unemployment rate. M1-clean
generalises this by adding explicit region indicators, which absorb
region-specific employment-opportunity heterogeneity orthogonal to
the GSUR signal.

---

## 3. What M1-clean inherits unchanged

M1-clean preserves the structural content of M0c_b2_GSURv2 in every
block except the market-opportunity block. The preserved content
includes the following.

The utility specification is preserved entirely. This comprises the
Box-Cox functional form, the singles consumption sub-block with the
shared exponent `theta_c_singles` and group-specific scales
`beta_c_sm` and `beta_c_sf`, the couples consumption sub-block with
`beta_c` and `theta_c` fixed at zero (log-utility on couples
consumption per finding R5.2), the leisure intercepts and Box-Cox
exponents for each of the four demographic groups (sm, sf, m, f),
and the leisure shifters (age-normalised, age-normalised squared,
and number of children for female partners). The household leisure-
leisure interaction `beta_ll` carrying finding R5.1 is preserved.

The wage-opportunity block is preserved entirely: the log-normal
specification, the Mincer mean shifters (`beta_w0`, `beta_w_educL`,
`beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`) carrying finding
R5.4, and the wage-offer dispersion parameter `sigma` carrying
finding R5.3. Education continues to enter the wage block; the
M1-clean reclassification of education concerns only the
opportunity-side index, not the wage-determination process.

The occupation-opportunity block is preserved entirely: the
twelve group-specific occupation shifters (three each for sm, sf,
cm, cf) carrying finding R5.5.

The hours-opportunity block is preserved entirely: the baseline
employment intercept `beta_E` and the hours-band shifters
`beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`.

The prior/proposal correction and the choice-set-centring
configuration are preserved: `center_within_choice_set: true` and
`center_weights: proposal`. The expression constraints
(`mul_cou_m_positive` and `mul_cou_f_positive`) are preserved.

The optimisation configuration is preserved: solver, method,
tolerances, parameter bounds, and the relaxed `beta_l0_m` lower
bound at 1e-6 established in M0c_b2.

---

## 4. What M1-clean changes

The change set is restricted to the `market_opportunity` block of
the YAML specification. Two amendments are applied.

The first amendment removes the education shifter:
`beta_E_educH` (the working-interacted coefficient on `educH`) is
dropped from the market-opportunity block.

The second amendment adds region-of-residence shifters: seven
indicators corresponding to EUROMOD `drgn1` groups 2 through 8,
each interacted with the employment indicator `working`. The
reference category is `drgn1 = 1` (Île-de-France). The coefficients
are named `beta_E_drgn2`, `beta_E_drgn3`, `beta_E_drgn4`,
`beta_E_drgn5`, `beta_E_drgn6`, `beta_E_drgn7`, `beta_E_drgn8`.
The *physical* data-column representation of these indicators is
deliberately left to the implementation audit, per §10 and §19.

No other block of the YAML is modified. The corrected broad-age
GSUR variable continues to enter the market-opportunity block
through `beta_E_gsur`, with its scaling and centring configuration
unchanged from M0c_b2_GSURv2.

---

## 5. Reconciliation with the older three-region-dummy plan

The framework memo at `Prompts/JMP_ability_vs_opportunity_framework_v1.md`
was drafted before the GSURv2 implementation work clarified the
regional structure of the EUROMOD France 2016 sample. Its provisional
regional design proposed three region dummies attached to a
NUTS-1-like aggregation, yielding an expected parameter count of
approximately forty-nine. This memo supersedes that regional design
in two ways.

First, the appropriate regional grouping for this sample is not the
modern thirteen-region NUTS-1 partition but the EUROMOD `drgn1`
ten-category coding. Categories 1 through 8 are observed in the
France 2016 metropolitan sample; categories 9 (DOM) and 10
(extra-regio) are absent by the sample-perimeter decision recorded
in the GSURv2 verdict memo §10. The natural partition is therefore
eight EUROMOD groups: Île-de-France, Bassin Parisien, Nord-Pas-de-
Calais, Est, Ouest, Sud-Ouest, Rhône-Alpes/Auvergne, and
Méditerranée. These are *old-region aggregations* implemented
through the EUROMOD coding, not modern NUTS-1 régions. The
distinction matters operationally because the modern Grand Est
NUTS-1 region cuts across old Champagne-Ardenne (in EUROMOD
`drgn1 = 2`) and old Lorraine + Alsace (in EUROMOD `drgn1 = 4`),
and the GSURv2 lookup was constructed precisely to respect the
EUROMOD definition.

Second, with `drgn1 = 1` (Île-de-France) as the reference category,
the natural saturated design comprises seven region dummies for
`drgn1 ∈ {2, 3, 4, 5, 6, 7, 8}`, not three. The earlier plan's
three-dummy aggregation was provisional and would have required an
explicit pooling rule that the framework memo did not specify. The
sample-size evidence in §17 below indicates that the observed cell
counts are sufficient to attempt the seven-dummy design; whether
pooling proves necessary remains an empirical identification
question to be settled by the M1-clean estimation diagnostics.

M1-clean adopts the saturated seven-dummy specification as the
default. Pooling is contemplated as a diagnostic response to
identification difficulty (per §17) and would, if triggered, require
a separate design memo specifying the pooling rule and its rationale.

---

## 6. Ability versus opportunity interpretation

The conceptual partition that M1-clean implements is the one
articulated in the framework memo §2 and §3, restated here in the
form in which it is operationalised by the YAML.

Variables classified as *opportunity* enter the market-opportunity
index and are interpreted under the welfare criterion as
circumstances for which individuals are not normatively responsible.
Under M1-clean, the opportunity dimensions are: region of residence
(captured by the seven `drgn1`-derived dummies for
`drgn1 ∈ {2, ..., 8}`, with `drgn1 = 1` as the reference category),
the regional demographically conditional unemployment rate (captured
by the corrected `gsur` variable through `beta_E_gsur`), and the
baseline employment shifter (`beta_E`). Region is treated as
opportunity under any plausible welfare criterion; GSUR is treated as
opportunity by construction, as the regional labour-market state to
which an individual is exposed; the baseline `beta_E` captures the
mean disutility of employment net of other opportunity components.

Variables classified as *ability* are those that enter the
wage-opportunity block and the labour-supply utility function but
not the market-opportunity block. Under M1-clean, the ability
dimensions are education attainment (captured by `beta_w_educL` and
`beta_w_educH` in the wage block) and potential labour-market
experience (captured by `beta_w_pexp` and `beta_w_pexp2` in the
wage block). Education thus enters the model through the wage
process but no longer through the opportunity-side index.

Variables classified as *preferences* are the parameters of the
utility function: leisure intercepts, Box-Cox exponents, leisure
shifters, consumption parameters, and the household leisure-leisure
interaction. These are treated under the welfare criterion as
responsibility-relevant in a manner that depends on the specific
welfare measure adopted; the framework memo's reference case is
the Fleurbaey-style equivalent-income measure, but the decomposition
will be reported under alternative welfare measures as a robustness
exercise.

The treatment of gender is deferred to the welfare-scaffolding stage
and is not implemented through M1-clean. The framework memo's gender
attribution rule (A1 ability, A2 opportunity, A3 a Blau-Kahn-anchored
40/60 mix as the main result) operates at the welfare-decomposition
stage, not at the estimation stage. M1-clean retains the same
gender-specific structural parameters as M0c_b2_GSURv2.

---

## 7. Treatment of education

Under M1-clean, education attainment enters the model in two places:
the wage-opportunity block (through `beta_w_educL` and `beta_w_educH`)
and, indirectly, the market-opportunity block (through the corrected
GSUR, which is education-stratified). Education does not enter the
opportunity-side index directly; the parameter `beta_E_educH` is
removed.

The wage-block role of education is preserved unchanged. Education
remains a determinant of wage offers, as is conventional in
labour-supply estimation, and the M0c_b2_GSURv2 estimates of
`beta_w_educL` (−0.046, p = 0.031) and `beta_w_educH` (+0.318,
p < 10⁻¹⁵) are expected to carry over to M1-clean with minimal
change.

The indirect opportunity-block role of education is also preserved
through GSUR. Because the corrected GSUR is education-stratified at
NUTS-2 level and aggregated to `drgn1`, education-specific regional
unemployment differentials continue to affect the
employment-opportunity index. What changes is the *interpretation*:
this education-related variation is no longer a residual
education-on-opportunity effect interpreted as if education were a
circumstance; it is the education-specific component of the
regional unemployment rate to which the individual is exposed.

The conceptual move is therefore not the elimination of education
from the model. It is the reclassification of education's
opportunity-block effect from a direct shifter (`beta_E_educH`) into
the demographically conditional regional unemployment measure (`gsur`).

---

## 8. Treatment of region

Under M1-clean, region of residence enters the market-opportunity
block through indicators for EUROMOD `drgn1` groups
`drgn1 ∈ {2, ..., 8}`, each interacted with the employment indicator
`working`, and through the corrected `gsur` variable, which is a
function of `drgn1`, `educ3`, and `sex`. Region of residence does not
enter the utility function (no preference-for-location is
parameterised) and does not enter the wage-opportunity block (no
regional wage premium is parameterised at this stage).

The EUROMOD `drgn1` coding is the appropriate regional partition
because the GSURv2 lookup was constructed against precisely this
partition, the sample is restricted to `drgn1 ∈ {1, ..., 8}`, and
the partition respects the pre-2016 NUTS-2 boundaries from which
the EUROMOD `drgn2` variable was derived. The use of modern NUTS-1
groupings would introduce a vintage mismatch with the GSURv2 lookup
and reintroduce the kind of cross-vintage problem the GSURv2 rebuild
was designed to eliminate.

The reference category `drgn1 = 1` is Île-de-France. This choice is
operationally convenient because Île-de-France is also the only
unambiguous case in the GSURv2 crosswalk, mapping one-to-one to
post-2016 NUTS-2 code FR10, and is the parity-check region in the
lookup validation. Coefficients on the seven added dummies are
therefore interpretable as the employment-opportunity effect of
residing in `drgn1 = k` (for `k ∈ {2, ..., 8}`) relative to
Île-de-France, holding GSUR, education-through-wage, and all other
parameters fixed.

The role of region as opportunity in the welfare interpretation is
unambiguous: region of residence at the time of labour-market
participation is, for the prime working-age sample under study, a
circumstance to which individuals are exposed rather than a choice
for which they are normatively responsible. The framework memo
treats region as opportunity under any reasonable interpretation of
the weak Dworkinian welfare criterion. M1-clean implements that
treatment.

---

## 9. Treatment of corrected GSUR

Under M1-clean, the corrected broad-age GSUR variable continues to
enter the market-opportunity block through `beta_E_gsur`, with the
same scaling (proportion units, the spec's `variable_scales.gsur =
10.0` scaling factor preserved) and the same centring (within choice
set, with proposal weights) as in M0c_b2_GSURv2. The Stage A
broad-age lookup is the GSUR source; Stage B age-specific GSUR
remains deferred per O6 of the GSUR rebuild specification.

The interpretation of `beta_E_gsur` shifts subtly when the region
dummies are added. In M0c_b2_GSURv2, `beta_E_gsur` is identified
against the full (region × education × sex) variation in the
corrected GSUR. In M1-clean, with the seven `drgn1` dummies absorbing
the region-marginal of GSUR, `beta_E_gsur` is identified against the
*within-region* (education × sex) variation in the corrected GSUR.
The expected magnitude of `beta_E_gsur` in M1-clean is therefore
smaller than the M0c_b2_GSURv2 estimate of −1.05 if and only if the
region-marginal of GSUR carried a substantial share of the GSUR
effect; if the within-region education-sex variation alone is
sufficient to identify the same effect size, the M1-clean estimate
will be close to the M0c_b2_GSURv2 estimate.

This is not a regression toward the M0c_b2 (pre-correction) estimate
of −0.74. The M0c_b2 attenuation arose from measurement error in
the misaligned regional crosswalk; the M1-clean redefinition arises
from partitioning the corrected variable into a region marginal
(absorbed by dummies) and a within-region residual (the identifying
variation for `beta_E_gsur`). The two effects are conceptually
distinct and may produce M1-clean estimates of `beta_E_gsur`
anywhere in the interval bounded by −0.74 and −1.05, or potentially
outside it, depending on the within-region structure of GSUR.

---

## 10. Exact M1-clean specification

The M1-clean specification is identical to M0c_b2_GSURv2 in all
blocks except the market-opportunity block, where the following
change occurs.

The `market_opportunity.shifters` list under M0c_b2_GSURv2 reads:

```
shifters:
  - variable: "gsur"
    coefficient: "beta_E_gsur"
    interaction: ["working"]
  - variable: "educH"
    coefficient: "beta_E_educH"
    interaction: ["working"]
```

Under M1-clean it becomes (variable-name placeholders to be resolved
by the implementation audit per §19; coefficient names are
authoritative):

```
shifters:
  - variable: "gsur"
    coefficient: "beta_E_gsur"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 2>
    coefficient: "beta_E_drgn2"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 3>
    coefficient: "beta_E_drgn3"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 4>
    coefficient: "beta_E_drgn4"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 5>
    coefficient: "beta_E_drgn5"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 6>
    coefficient: "beta_E_drgn6"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 7>
    coefficient: "beta_E_drgn7"
    interaction: ["working"]
  - variable: <indicator for drgn1 == 8>
    coefficient: "beta_E_drgn8"
    interaction: ["working"]
```

The `educH` shifter and its coefficient `beta_E_educH` are removed.
Seven indicator shifters with coefficients `beta_E_drgn{k}` for
`k ∈ {2, ..., 8}` are added. All other blocks of the YAML are
copied without modification from the M0c_b2_GSURv2 specification.

The provenance label changes:
`specification.name: "ruro_occ_M0c_b2_GSURv2"` becomes
`specification.name: "ruro_occ_M1_clean"`.

The placeholder `<indicator for drgn1 == k>` is intentional. The
final variable names (whether `drgn{k}`, `reg_nuts1_{k}`, or another
convention) are determined by the implementation audit per §19 and
the data-column inspection it requires. The coefficient names
`beta_E_drgn{k}` are stable across all naming conventions and serve
as the canonical parameter labels for the model.

---

## 11. Region-dummy design

The seven region dummies are conceptually defined as binary
indicators of `drgn1 == k` for `k ∈ {2, 3, 4, 5, 6, 7, 8}`. Each
indicator enters the market-opportunity block interacted with the
employment indicator `working`, so that the coefficient
`beta_E_drgn{k}` captures the employment-opportunity utility shift
of residence in `drgn1 = k` relative to `drgn1 = 1`, conditional on
working. The dummies are not interacted with sex, age, or education
at this stage; richer interactions are a possible extension if
M1-clean acceptance reveals systematic gender-by-region or
education-by-region heterogeneity, but the baseline M1-clean design
is parsimonious.

The dummies enter the market-opportunity block and do not appear in
the utility function or in the wage block. This placement enforces
the conceptual interpretation that regional differences are
employment-opportunity differences rather than preference or
productivity differences. Should evidence later support a regional
wage premium, that extension would be a separate specification
beyond M1-clean.

The household-level constancy property verified in the Stage A MNL
rebuild report §16 (M12-diag) establishes that `drgn1` is constant
within each household (within `idhh`); the conceptual indicators
inherit this constancy. Their entry into the choice-utility index
through `working`-interaction means they enter only the working
alternatives of each household's choice set, leaving the
non-working alternatives unaffected by the regional shifters. This
is the same structural placement as `beta_E_gsur` and
`beta_E_educH` in the M0c_b2_GSURv2 specification.

The physical column names through which the conceptual indicators
are realised in the MNL parquets are addressed by the implementation
audit in §19.

---

## 12. Parameters to remove

One parameter is removed from M0c_b2_GSURv2:

`beta_E_educH` — the working-interacted coefficient on `educH` in
the market-opportunity block. M0c_b2_GSURv2 estimate: +0.4386,
standard error 0.2257, t-statistic 1.943, p-value 0.052.

The removal reflects the reclassification of education from
opportunity to ability per §6 and §7. The parameter does not
reappear in any other block of the M1-clean YAML.

---

## 13. Parameters to add

Seven parameters are added to M0c_b2_GSURv2:

| Parameter | Conceptual variable | Interaction | Interpretation |
|---|---|---|---|
| `beta_E_drgn2` | indicator `drgn1 == 2` | `working` | Employment-opportunity effect of `drgn1 = 2` (Bassin Parisien) relative to `drgn1 = 1` (Île-de-France) |
| `beta_E_drgn3` | indicator `drgn1 == 3` | `working` | Same for `drgn1 = 3` (Nord-Pas-de-Calais) |
| `beta_E_drgn4` | indicator `drgn1 == 4` | `working` | Same for `drgn1 = 4` (Est) |
| `beta_E_drgn5` | indicator `drgn1 == 5` | `working` | Same for `drgn1 = 5` (Ouest) |
| `beta_E_drgn6` | indicator `drgn1 == 6` | `working` | Same for `drgn1 = 6` (Sud-Ouest) |
| `beta_E_drgn7` | indicator `drgn1 == 7` | `working` | Same for `drgn1 = 7` (Rhône-Alpes/Auvergne) |
| `beta_E_drgn8` | indicator `drgn1 == 8` | `working` | Same for `drgn1 = 8` (Méditerranée) |

Each parameter receives an initial value of 0.0 in the YAML
`initial_values` block and a bounds specification of `[-10.0, 10.0]`
in the YAML `optimization.bounds` block (matching the convention
used for other shifters of comparable magnitude such as
`beta_E_educH` in the M0c_b2_GSURv2 spec).

---

## 14. Expected parameter count

M0c_b2_GSURv2 has forty-seven free parameters. M1-clean removes one
parameter (`beta_E_educH`) and adds seven (`beta_E_drgn2` through
`beta_E_drgn8`). The expected M1-clean parameter count is therefore:

47 − 1 + 7 = 53

The expected M1-naive parameter count (per §23 below) is
forty-seven plus seven added region dummies with no removal:

47 + 7 = 54

These counts assume that the YAML parser interprets each entry in
the `market_opportunity.shifters` list as a single free parameter,
which is the parser behaviour observed in all M0c family
specifications to date. The parameter count must be verified against
the parser's reported count in the M1-clean estimation log; should
the parser report a count other than fifty-three for M1-clean or
fifty-four for M1-naive, this is a flag that requires investigation
before the run is accepted.

---

## 15. Parameters to leave unchanged

All forty-six parameters of M0c_b2_GSURv2 other than `beta_E_educH`
are preserved unchanged in M1-clean. Specifically:

The singles preference block (twelve parameters): `beta_l0_sm`,
`beta_l_age_sm`, `beta_l_age2_sm`, `beta_c_sm`, `theta_l_sm`,
`beta_l0_sf`, `beta_l_age_sf`, `beta_l_age2_sf`, `beta_l_nkids_sf`,
`beta_c_sf`, `theta_l_sf`, `theta_c_singles`.

The couples preference block (ten parameters): `beta_l0_m`,
`beta_l_age_m`, `beta_l_age2_m`, `theta_l_m`, `beta_l0_f`,
`beta_l_age_f`, `beta_l_age2_f`, `beta_l_nkids_f`, `theta_l_f`,
`beta_c`.

The household interaction parameter: `beta_ll` (one parameter).

The hours-opportunity block (four parameters): `beta_E`,
`beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`.

The retained market-opportunity parameter: `beta_E_gsur` (one
parameter).

The occupation-opportunity block (twelve parameters):
`beta_occ_2_sm`, `beta_occ_3_sm`, `beta_occ_4_sm`, `beta_occ_2_sf`,
`beta_occ_3_sf`, `beta_occ_4_sf`, `beta_occ_2_cm`, `beta_occ_3_cm`,
`beta_occ_4_cm`, `beta_occ_2_cf`, `beta_occ_3_cf`, `beta_occ_4_cf`.

The wage-opportunity block (six parameters): `beta_w0`,
`beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`,
`sigma`.

Total preserved: 12 + 10 + 1 + 4 + 1 + 12 + 6 = 46 parameters.

The initial values, parameter bounds, and expression constraints
of all forty-six preserved parameters are copied from
M0c_b2_GSURv2 without modification.

---

## 16. Expected parameter shifts

The substantive shifts expected in M1-clean relative to
M0c_b2_GSURv2 are concentrated in the market-opportunity block.

The coefficient `beta_E_gsur`, currently estimated at −1.050 under
M0c_b2_GSURv2, is expected to shift to a value of comparable
magnitude (within plus or minus thirty per cent). The direction of
shift is ambiguous: if the within-region education-sex variation in
GSUR is sufficient to identify the M0c_b2_GSURv2 effect size, the
M1-clean estimate will be close to −1.05; if the region-marginal
of GSUR carried part of the previously estimated effect, the
M1-clean estimate will move toward zero in magnitude.

The seven added region coefficients `beta_E_drgn{k}` are expected
to be jointly significant and individually heterogeneous in sign.
The corrected GSUR aggregates documented in the Stage A MNL rebuild
report §15 indicate that the M11-diagnostic average GSUR by `drgn1`
ranges from approximately 5.6 percent (in `drgn1 = 1`, IDF) to
approximately 11.0 percent (in `drgn1 = 3`, Nord-Pas-de-Calais);
the residual employment-opportunity differential captured by the
region dummies may therefore plausibly be in the range of plus or
minus 0.5 to 1.5 utility-units relative to IDF, with Île-de-France
serving as the high-employment-opportunity reference.

The coefficient `beta_E`, currently −2.489 under M0c_b2_GSURv2, is
expected to shift to accommodate the added region dummies' implicit
absorption of the IDF-relative baseline. If the dummies are
positively signed (indicating other regions have higher
employment-opportunity utility than IDF), `beta_E` will shift
downward (more negative). If the dummies are negatively signed
(IDF has highest employment opportunity), `beta_E` will shift
upward (less negative). The expected shift magnitude is on the
order of plus or minus 0.5 utility-units.

The preference block parameters are expected to be stable. The
M0c_b2_GSURv2 evidence demonstrates that adding region structure
to the opportunity block does not propagate substantially into the
preference parameters; the same property is expected to hold for
M1-clean, where the change is again confined to the
market-opportunity block.

The wage-block parameters, including `beta_w_educL` and
`beta_w_educH`, are expected to be stable to within rounding error.
The wage equation has no structural link to the market-opportunity
block in the current specification.

The occupation-opportunity block is expected to be stable: all
twelve coefficients are expected to shift by less than 0.01 in
absolute value. Multistart confirmation is required to verify this.

The household leisure-leisure interaction `beta_ll` (finding R5.1)
is expected to be stable to within one per cent.

The log-likelihood is expected to improve relative to
M0c_b2_GSURv2. A point estimate of the expected improvement is
not specified here; an improvement of fewer than ten log-likelihood
units would indicate that the region dummies add limited
information beyond GSUR; an improvement larger than fifty
log-likelihood units would suggest substantial regional residual
heterogeneity that the GSUR variable did not capture.

---

## 17. Identification risks from GSUR and region dummies

The principal identification risk in M1-clean is partial collinearity
between the seven region dummies and the corrected GSUR variable.
The GSUR variable is education-sex-region-stratified at NUTS-2 level
and aggregated to `drgn1`, taking at most 48 distinct values across
households (8 `drgn1` × 3 `educ3` × 2 `sex`). The seven region
dummies span the 8-level region marginal of this variation. Within
the linear-in-index structure of the choice-utility specification,
the region dummies and the region-marginal of GSUR are perfectly
collinear; what identifies `beta_E_gsur` separately from the dummies
is the within-region (education × sex) variation in GSUR.

This is not a singular collinearity but a partial one. The Stage A
M11-diagnostic table (rebuild report §15) records the within-region
GSUR variation: at `drgn1 = 1` (where the region marginal does no
work), the GSUR varies from 5.6 percent (high-education males) to
16.4 percent (low-education males); within `drgn1 = 3`, GSUR varies
from 6.7 percent to 23.4 percent. The education-sex variation
within each region is substantial relative to the between-region
variation, and is therefore expected to identify `beta_E_gsur` even
when the region dummies absorb the region-marginal.

The observed-support evidence supports attempting the seven-dummy
design. The smallest singles cell occurs at `drgn1 = 3`
(Nord-Pas-de-Calais), with approximately 126 households and 12,600
alternative-row observations across the six (`educ3` × `dgn`)
sub-cells. The smallest couples cell occurs at the same `drgn1`
with approximately 191 households. These counts are decent for
estimating individual binary coefficients but do not, by themselves,
guarantee identification in the presence of a strongly related GSUR
variable. Whether pooling proves necessary remains an empirical
identification question to be settled by the diagnostics in §21 and
the SA1 verdict process in §22.

Four diagnostic outcomes and their corresponding design responses
are specified below.

*Outcome A — All region dummies individually significant at
p < 0.05; `beta_E_gsur` retains within-region interpretation at
magnitude in [−0.6, −1.5]; Hessian condition number stable within
factor of two; standard errors of the seven region coefficients
each less than 0.5.* Response: accept the seven-dummy design.
M1-clean stands as specified.

*Outcome B — A subset of region dummies individually
insignificant at p ≥ 0.20 with similar point-estimate magnitudes
to neighbouring regions; remaining diagnostics within Outcome-A
ranges.* Response: consider pooling the affected dummies into a
coarser partition (for instance, pooling Nord-Pas-de-Calais and
Méditerranée if both show large negative coefficients, or pooling
Ouest, Sud-Ouest, and Rhône-Alpes if all three show small positive
coefficients). Pooling requires a separate design memo specifying
the pooled categories and their normative justification; it is
not implemented in M1-clean directly.

*Outcome C — Region dummies all jointly insignificant in a Wald
test (p ≥ 0.10); log-likelihood improvement under five units
relative to M0c_b2_GSURv2; `beta_E_gsur` essentially unchanged.*
Response: drop the region dummies and revert to a specification
that retains corrected GSUR as the sole region-related variable
in the market-opportunity block. This would correspond to
adopting M0c_b2_GSURv2 (with `beta_E_educH` removed) as the
JMP's preferred specification. Document the finding as evidence
that GSUR's regional content is sufficient for the
opportunity-side index.

*Outcome D — Hessian condition number exceeds 10¹² (an order of
magnitude worse than the M0c_b2_GSURv2 condition number of
5.14 × 10¹⁰); new negative eigenvalues appear in the
market-opportunity block; one or more region coefficients reach
their bounds; standard errors exceed unity for multiple region
coefficients.* Response: M1-clean is overparameterised. The
specification is rejected; the JMP defaults to M0c_b2_GSURv2 with
`beta_E_educH` removed (a 46-parameter specification) as a
fallback preferred specification. The seven-dummy design is
documented as having failed identification.

The decision rule among Outcomes A, B, C, and D is specified in the
SA1 acceptance rule in §22.

---

## 18. Required YAML changes

The M1-clean YAML is produced by deriving from
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
and applying the following edits.

The `specification.name` field is changed from
`"ruro_occ_M0c_b2_GSURv2"` to `"ruro_occ_M1_clean"`. The
`specification.description` field is updated to reflect M1-clean's
purpose and to identify the parent specification.

In the `market_opportunity.shifters` list, the entry for `educH`
with coefficient `beta_E_educH` is removed. Seven entries are
appended, one for each conceptual indicator of `drgn1 == k` for
`k ∈ {2, ..., 8}`, with coefficients `beta_E_drgn2` through
`beta_E_drgn8` respectively and interaction `["working"]`. The
`variable` field of each appended entry is filled in by the
implementation audit according to the chosen column convention
(see §19).

In the `initial_values` block, the entry for `beta_E_educH` is
removed. Seven entries are added, one for each of the new
coefficients, each initialised at 0.0.

In the `optimization.bounds` block, the entry for `beta_E_educH`
is removed. Seven entries are added, one for each of the new
coefficients, each bounded `[-10.0, 10.0]`.

No other block of the YAML is modified. The
`variable_scales.gsur` field, the `center_within_choice_set`
field, the `center_weights` field, the `couples.leisure_interaction`
block, the `expression_constraints` block, the `gradient_verification`
block, and all other configuration elements are preserved
unchanged.

The M1-clean YAML is saved as
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
in the canonical `specifications/` subdirectory parallel to the
M0c_b2_GSURv2 YAML. The M0c_b2_GSURv2 YAML is retained without
modification for provenance and reproducibility.

---

## 19. Required data columns

The seven region indicators required by M1-clean are conceptually
defined as binary functions of `drgn1`. The implementation audit
must establish how these conceptual indicators are realised in the
live data contract of the versioned GSURv2 MNL parquets. The audit
discovers three live-data conditions that must be reconciled.

First, the GSURv2 singles parquet currently contains pre-computed
indicator columns `reg_nuts1_1` through `reg_nuts1_8`, one per
EUROMOD `drgn1` group. The naming convention reflects an earlier
NUTS-1-style framing; these columns are nonetheless the appropriate
indicators of `drgn1 == k` for the singles data.

Second, the GSURv2 couples parquet does not currently contain
analogous pre-computed indicator columns. The couples parquet
carries the `drgn1` column at the alternative-row level (verified
by the Stage A MNL rebuild report's M12-diagnostic of household-
level constancy), but no `reg_*` or `drgn{k}` indicator columns
are present.

Third, the estimator's variable resolver may or may not support
on-the-fly construction of binary indicators from a categorical
column such as `drgn1`. Whether it does is a property of the
estimator's parser implementation and must be established by
inspection.

The implementation audit must reconcile these three conditions and
recommend one of three implementation paths.

*Path A — Reuse the existing singles indicators and create matching
couples indicators.* This path requires adding `reg_nuts1_2` through
`reg_nuts1_8` (or equivalently named indicators) to the couples
parquet via a small MNL rebuild step. The advantage is symmetry with
the existing singles convention; the disadvantage is that the
`reg_nuts1_*` naming is a misnomer (the indicators map `drgn1`
groups, not modern NUTS-1 régions), which may cause downstream
confusion.

*Path B — Derive indicators from `drgn1` at load time.* This path
relies on the estimator's variable resolver to construct binary
indicators on demand from the existing `drgn1` column in both
parquets. The advantage is that no MNL rebuild is required and the
data contract is unchanged. The disadvantage is that the resolver's
behaviour must be verified to support indicator construction with
the YAML variable references used in §10 and §18.

*Path C — Create harmonized `drgn{k}` indicator columns in both
parquets.* This path requires an MNL rebuild step that adds
`drgn2` through `drgn8` to both singles and couples parquets,
deprecating the existing `reg_nuts1_*` columns in singles or
retaining them in parallel for backwards compatibility. The
advantage is naming clarity and physical symmetry; the disadvantage
is the cost of the rebuild and the proliferation of indicator
columns.

The choice among Path A, Path B, and Path C is made by the
implementation audit on the basis of (a) the estimator's resolver
capability, (b) the cost of any required MNL rebuild, and (c) the
operational preference for naming clarity. The choice does not
affect the conceptual content of M1-clean; the coefficient names
`beta_E_drgn{k}` are stable across all three paths.

Whichever path is chosen, the implementation must respect the
versioned-path discipline established in v2.1 §12 and the GSURv2
verdict §9. Any new MNL rebuild writes to further-versioned paths
(e.g., `fr_2016_RURO_mnl_GSURv2_drgn_M1__{singles,couples}.parquet`)
and does not touch the canonical files. Promotion of any
M1-related rebuild to canonical paths is not authorised by this
memo.

---

## 20. Required estimation protocol

M1-clean estimation follows the same protocol as the M0c_b2_GSURv2
re-estimation, with one adjustment for the new parameters.

The multistart configuration uses three independent starts. Start
one warm-starts from the M0c_b2_GSURv2 accepted parameter vector
(specifically from
`outputs/estimates/fr/spec/ruro_occ_GSURv2/gamspy/estimation_spec_ruro_occ_M0c_b2_GSURv2/run_2026-05-17_23-55-09/estimation_results.json`),
with the seven new `beta_E_drgn{k}` parameters initialised at zero
and the dropped `beta_E_educH` parameter omitted. Start two uses
the YAML defaults (all preference and opportunity parameters at
their `initial_values` settings). Start three uses a perturbed
initial vector with seed 42 and a five-per-cent-of-bounds-range
perturbation, matching the M0c_b2_GSURv2 multistart protocol.

The solver is CONOPT via GAMSPy vectorised. The `--mnl-base` stem
points to the versioned GSURv2 paths (or, if Path A or Path C of
§19 is selected, to the further-versioned drgn-augmented paths).
The output directory is
`outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/`.

Acceptance of the M1-clean estimation result requires (a)
convergence of all three starts to a status of `OptimalLocal` with
solver status `NormalCompletion`, (b) identical log-likelihood
across the three starts to within machine precision, and (c)
identical parameter vector across the three starts to within
machine precision. Failure of any of these conditions triggers a
diagnostic investigation before the M1-clean verdict can be
written.

The M1-clean estimation does not modify the wage draws, hours
draws, occupation draws, alternative sets, prior corrections, or
any other element of the pre-estimation pipeline. These are
preserved from the M0c_b2_GSURv2 run.

---

## 21. Required post-estimation diagnostics

The M1-clean post-estimation diagnostics replicate the M0c_b2_GSURv2
post-estimation diagnostics with three additions.

The standard diagnostics — parameter estimates with standard errors,
t-statistics, and p-values; observed-versus-predicted participation
rates by group; observed-versus-predicted mean hours by group; hours
distributions, wage distributions, and occupation shares; Hessian
condition number and eigenvalue inventory; standard-error
inventory by validity — are reported for M1-clean in the same form
as for M0c_b2_GSURv2, using the same post-estimation script and the
same output structure.

In addition, the following M1-specific diagnostics are reported.

First, a *joint Wald test* of the null hypothesis
`beta_E_drgn2 = beta_E_drgn3 = ... = beta_E_drgn8 = 0`. The
resulting chi-squared statistic, its degrees of freedom (seven),
and its p-value identify whether the region dummies are jointly
significant. The test is essential for distinguishing Outcome A or
B from Outcome C in §17.

Second, a *region-specific covariance inspection*: the seven-by-seven
sub-block of the variance-covariance matrix corresponding to the
region coefficients, together with the correlation matrix
derived from it. Correlations exceeding 0.9 between any pair of
region coefficients are reported as a flag; correlations exceeding
0.95 indicate identification weakness that must be addressed
before the M1-clean verdict is written.

Third, a *region-conditional GSUR identification check*: the
sub-matrix of the Hessian restricted to `(beta_E_gsur, beta_E_drgn2,
..., beta_E_drgn8)`, with its eigenvalues reported. Near-zero or
negative eigenvalues in this sub-block flag the partial collinearity
risk discussed in §17.

The post-estimation script is run against the M1-clean estimation
results with the same `--mnl-base` setting used at estimation time.
A new post-estimation report
`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md` is
produced parallel to the M0c_b2_GSURv2 post-estimation report.

---

## 22. Acceptance rule for M1-clean

The acceptance of M1-clean is judged against three SA1 verdicts,
analogous in form to the SA-STANDS / SA-REVISION / SA-OVERTURNED
rule of the GSUR rebuild specification §9.3 but adapted to the
M1-clean context. The numerical thresholds below are *proposed
M1-clean acceptance thresholds* selected for this design memo;
they are not inherited from any earlier governing document. The
thresholds may be revised in a successor memo if the M1-clean
estimation evidence indicates that the proposed levels are
operationally too strict or too lax.

*SA1-STANDS — M1-clean accepted as the preferred specification.*
The proposed criteria are: all preference parameters shift by less
than five per cent in absolute value relative to M0c_b2_GSURv2;
`beta_E_gsur` remains negative and statistically significant at
p < 0.01 with magnitude in [−0.6, −1.5]; the seven region
coefficients are jointly significant at p < 0.05 by the Wald test
of §21; the log-likelihood improvement relative to M0c_b2_GSURv2
exceeds ten units; the Hessian condition number remains below
10¹¹; the number of negative Hessian eigenvalues remains at one and
is confined to the singles consumption sub-block; no new NA
standard errors appear; all key M0c_b2_GSURv2 findings (R5.1
through R5.5) are preserved within M0c_b2_GSURv2-comparable
confidence bands; participation, hours, wage, and occupation fit
diagnostics do not regress by more than one percentage point or
0.5 hours relative to M0c_b2_GSURv2.

*SA1-REVISION — M1-clean accepted with documented qualifications.*
This verdict applies when one or more SA1-STANDS criteria fail by
small margins. For instance: log-likelihood improvement of fewer
than ten but more than three units; a single region coefficient
individually insignificant but the joint test passing; preference-
parameter shifts up to ten per cent; a fit diagnostic regressing
by between one and two percentage points. Under SA1-REVISION,
M1-clean is documented as the working specification with a verdict
memo recording the specific qualifications; pooling of one or more
region dummies into a coarser partition is contemplated and may
be implemented in a successor specification.

*SA1-OVERTURNED — M1-clean rejected.* This verdict applies when one
or more of the following conditions hold: a preference parameter
shifts by more than ten per cent in absolute value; the Hessian
condition number exceeds 10¹² or new negative eigenvalues appear
outside the singles consumption sub-block; multiple region
coefficients reach their bounds; multistart fails to converge to a
single attractor; the joint Wald test of region dummies returns
p > 0.20 *and* the log-likelihood improvement is less than three
units. Under SA1-OVERTURNED, M1-clean is rejected. The JMP defaults
to a fallback specification consisting of M0c_b2_GSURv2 with
`beta_E_educH` removed (forty-six parameters), which retains the
educational reclassification but does not add region dummies.

The selection among SA1-STANDS, SA1-REVISION, and SA1-OVERTURNED
is made on the basis of the M1-clean estimation report and
post-estimation diagnostics; a separate verdict memo
`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` is written to record the
verdict and its justification, following the same template as the
M0c_b2_GSURv2 verdict memo.

The thresholds proposed above are deliberately strict on the
preference-parameter dimension (five per cent for SA1-STANDS) and
moderate on the log-likelihood dimension (ten units for STANDS, a
quantity comparable to the seven-unit improvement of GSURv2 over
M0c_b2). Their precommitment serves two purposes: it disciplines
the verdict process by removing post-hoc threshold setting, and it
makes explicit the conceptual hierarchy of the JMP — preference
stability dominates fit improvement in the acceptance criterion.

---

## 23. M1-naive robustness specification

M1-naive is a sensitivity specification, not a preferred
specification. Its purpose is to quantify the dependence of the
M1-clean welfare decomposition on the educational reclassification.

The M1-naive specification adds the same seven region dummies to
M0c_b2_GSURv2 but retains `beta_E_educH` in the
market-opportunity block. The expected parameter count is
forty-seven plus seven, equal to fifty-four. All other elements of
M1-naive are identical to M1-clean and to M0c_b2_GSURv2; the same
data-column reconciliation per §19 applies to M1-naive.

M1-naive is estimated under the same protocol as M1-clean (§20)
and its diagnostics are reported in the same form (§21). M1-naive
does not have its own SA1 verdict; instead, M1-naive is documented
as a robustness check whose findings feed the welfare-decomposition
robustness exposure R2 in the framework memo. The R2 exposure
asks how the ability-versus-opportunity partition affects the
inequality decomposition; the comparison between M1-clean and
M1-naive answers precisely this question on the structural side,
before any welfare measurement is applied.

M1-naive is not the JMP's preferred specification. If M1-naive
produces estimates that materially differ from M1-clean, the JMP
text reports this as a robustness finding. The preferred
specification remains M1-clean (subject to its SA1 verdict), and
the JMP's main welfare results are computed from M1-clean
estimates.

The M1-naive YAML is saved as
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml`
in the same `specifications/` subdirectory as the M1-clean YAML.

---

## 24. What remains postponed

The following items remain outside the scope of M1-clean and are
not authorised by this design memo.

*Stage B age-specific GSUR.* The narrow age bands Y15-24, Y25-34,
Y35-44, Y45-54, and Y55-64 from the corrected GSUR lookup are not
activated in M1-clean. The age-specific GSUR question is deferred
to a post-M1-clean review per O6 of the GSUR rebuild specification.

*Canonical promotion of GSURv2 MNL parquets.* The versioned GSURv2
parquets remain the working data source; the canonical paths
retain v1 content. Promotion to canonical paths is a separate O10
decision requiring explicit user approval after a successful Stage
A verdict. The current Stage A verdict is positive (SA-STANDS) per
the M0c_b2_GSURv2 verdict memo §1, but promotion has not been
authorised.

*Welfare scaffolding implementation.* The welfare-measurement
decisions memo (specifying functional choice, inequality index,
decomposition method, and gender attribution rule) is the
prerequisite for welfare scaffolding implementation. This memo
remains unwritten and is the recommended parallel task to M1-clean
implementation.

*Gender attribution rule implementation.* The framework memo's
gender attribution rules A1, A2, and A3 operate at the welfare-
decomposition stage, not at the M1-clean estimation stage. M1-clean
preserves the M0c_b2_GSURv2 gender-specific structural parameters
unchanged.

*Multi-country and multi-year extensions.* M1-clean is estimated on
France 2016 only. Extensions to France 2021, Germany, or other
country-year combinations are deferred to post-JMP-baseline work.

*The François Maniquet pure-theory paper.* This memo's empirical
specification work is intellectually adjacent to but operationally
distinct from the separate theory paper on jobs and well-being.
The JMP must remain a distinct empirical contribution and must not
be framed as an implementation of the theory paper.

---

## 25. What this allows me to write in the JMP

The acceptance of M1-clean — conditional on the SA1 verdict process
in §22 — supports the following additions to the JMP draft.

A *methods section* paragraph documenting the ability-versus-
opportunity partition and its operational implementation in the
structural model. This paragraph cites the framework memo, the
GSURv2 verdict, and this design memo as the chain of design
decisions leading to M1-clean.

A *specification table* listing the parameters of M0c_b2_GSURv2 and
M1-clean side by side, identifying the dropped parameter
`beta_E_educH` and the seven added region parameters. The table
serves as the conceptual anchor for the JMP's structural section
and is the necessary reference for any later interpretation of the
decomposition results.

A *baseline-versus-preferred-specification discussion* in which
M0c_b2_GSURv2 is identified as the data-corrected baseline and
M1-clean as the JMP's preferred specification, with the
ability-versus-opportunity partition as the principled
justification for the move. This discussion ties together the GSUR
correction, the educational reclassification, and the regional
specification.

A *robustness section paragraph* documenting the M1-naive
sensitivity exercise and its implications for the welfare
decomposition. The R2 exposure in the framework memo is
operationally answered by the M1-clean-versus-M1-naive comparison
on the structural side; the welfare-side consequences will be
reported when welfare scaffolding is implemented.

A *limitations paragraph* documenting the singles consumption
joint-identification issue (unchanged from M0c_b2 and
M0c_b2_GSURv2), the Stage A versus Stage B GSUR distinction, and
the metropolitan-France sample restriction. These are honest
qualifications that strengthen the JMP rather than weaken it.

This memo does not, however, license claims about welfare
decompositions, opportunity-driven inequality magnitudes, or
preference-driven inequality magnitudes. Those claims require
estimated welfare results, which in turn require the
welfare-measurement decisions memo to be written and a welfare
scaffold to be implemented. Until both prerequisites are met, the
JMP draft can include only the structural specification work and
not the decomposition work.

---

## 26. Immediate next coding task

The immediate next coding task is the M1-clean implementation
prompt, to be executed by Claude Code Sonnet against the local
RURO/MNL codebase. The prompt is *not* this memo; this memo is the
design specification, and a separate implementation prompt
operationalises it.

The implementation prompt should include the following content.

A directive to read this memo, the M0c_b2_GSURv2 verdict, the
M0c_b2_GSURv2 YAML at
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`,
the GSUR rebuild specification §16 and §12 (F6, F6-promote), and
the Stage A MNL rebuild report (for the data-column constancy
properties).

A *data-column reconciliation audit* (per §19) that establishes
which of Path A, Path B, or Path C is operative. The audit
inspects the live GSURv2 parquets (both singles and couples),
identifies the existing `reg_nuts1_*` columns in singles, confirms
the absence of analogous columns in couples, and tests the
estimator's variable resolver for on-the-fly indicator construction.
The audit's recommendation is recorded in the implementation report
before any YAML construction or MNL rebuild proceeds.

A *YAML construction step* for the M1-clean YAML at
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`,
derived from the M0c_b2_GSURv2 YAML with the §18 edits applied. The
`variable` field of each region shifter is filled in according to
the column convention chosen by the data-column audit.

An *MNL rebuild step* (conditional on Path A or Path C of §19),
adding the required region indicator columns to one or both
parquets at further-versioned paths. The rebuild is skipped under
Path B.

A *multistart estimation step* following §20, with three independent
starts and the M0c_b2_GSURv2 warm-start path as the first start.

A *post-estimation step* following §21, with the joint Wald test,
the region covariance inspection, and the region-conditional
Hessian sub-matrix eigenvalue inventory as the M1-specific
additions to the standard diagnostics.

A *reporting step* producing the M1-clean estimation report and
post-estimation diagnostics in
`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_estimation_report_v1.md` and
`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md`.

The implementation prompt does not authorise the M1-clean verdict;
the verdict is written separately in this chat after the
implementation report and post-estimation diagnostics are
delivered. The implementation prompt also does not authorise
welfare computation, canonical promotion, or any Stage B work.

The recommended parallel task to the M1-clean implementation prompt
is the *welfare-measurement decisions memo*, which can be drafted
in this chat while Claude Code executes M1-clean. The welfare memo
does not block M1-clean; it can proceed in parallel and is the
methodological prerequisite for the subsequent welfare scaffolding
work.

---

## Operational note (v2)

The v1 of this memo (`docs/RURO_occ_M1_clean_design_memo_v1.md`)
is superseded by v2 in full and may be archived or retained for
provenance at the project owner's discretion. The substantive
content of v1 is preserved in v2 with the five revisions described
in the revision history at the top of this memo. v2 should be
added to version control (`git add docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md`)
before any implementation work proceeds, so that the design contract
binding the next coding task is checked in.
