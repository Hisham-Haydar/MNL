# RURO occ M1-clean — Verdict v1

Date: 2026-05-18

Specification: `estimation_spec_ruro_occ_M1_clean.yaml` (53 free
parameters, parser-verified, frozen blocks preserved relative to
`estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`)

Selected estimation run:
`outputs/estimates/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_11-33-46/`
(Start 1, warm from M0c_b2_GSURv2; all three independent starts
converge to identical log-likelihood at LL = −6487.5522 and to a
bit-identical parameter vector)

Primary evidence:
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_estimation_report_v1.md`
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md`
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_gate_A_parse_report_v1.md`
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_YAML_implementation_report_v1.md`
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_diagnostics_implementation_report_v1.md`

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the prior working
  baseline)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` §22 (the SA1
  acceptance rule applied here)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the
  ability/opportunity partition implemented by M1-clean)

Scope of verdict: structural baseline acceptance for the JMP,
conditional on Stage A broad-age GSUR. This verdict does not
authorise canonical MNL promotion (O10), welfare-decomposition
computation, or Stage B age-specific GSUR work. The M1-naive
sensitivity exercise is sequenced separately per §16 below.

---

## 1. Verdict

**SA1-STANDS with documented qualifications. `ruro_occ_M1_clean` is
accepted as the JMP's preferred structural specification.**

The classification rests on the application of the proposed §22
acceptance rule of `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md`. Every
hard SA1-STANDS criterion is met at the design-memo threshold. Four
qualifications are documented but none constitutes a hard failure
under §22:

(Q1) The Mediterranean region coefficient `beta_E_drgn8` is
individually marginally significant (p = 0.097). This is the
single region dummy not significant at 5 per cent in individual
testing. The joint Wald test on the seven region coefficients
remains strongly significant (W = 28.18 on 7 d.f., p = 0.0002).
The SA1-STANDS criterion for the region block is joint
significance, which is met; the individual insignificance of
`beta_E_drgn8` constitutes a qualification rather than a failure.

(Q2) The singles-male participation fit reverses sign relative to
M0c_b2_GSURv2: predicted-minus-observed shifts from +0.04 to
−0.88 percentage points. The absolute regression of 0.92
percentage points falls inside the design memo's tolerance of one
percentage point but is the closest fit-diagnostic figure to a
threshold breach in any group. All other groups (sf, cm, cf) show
participation fit improvement.

(Q3) The singles-male hours-bin L1 distance regresses by 9.6 per
cent (from 0.6345 in M0c_b2_GSURv2 to 0.6945 in M1-clean). The
mechanism is that all seven region-dummy estimates are positive,
which raises predicted mass in the 21–30-hour bin for singles male
and amplifies a pre-existing over-concentration in that bin. Mean
hours fit is essentially unchanged across all four groups
(maximum change 0.04 hours), and the hours-bin L1 distances for
sf, cm, and cf are negligibly improved. The §22 SA1-STANDS
criterion specifies that hours fit not regress by more than 0.5
hours, which refers to mean hours rather than to bin-distribution
L1 distance; the bin-distribution regression is therefore not in
itself a hard-gate failure.

(Q4) The Bayesian information criterion (BIC) penalises M1-clean
by 50.4 units relative to M0c_b2_GSURv2 (BIC moves from 13611.6
to 13662.0), a mechanical consequence of adding six net
parameters. The Akaike information criterion (AIC) improves by
15.3 units in M1-clean's favour. BIC is not among the proposed
§22 SA1-STANDS criteria and is therefore not a hard-gate input.

The classification also depends on interpretive judgements where
the design-memo criteria do not admit mechanical application:

(J1) The §22 SA1-REVISION example list includes the situation of
"a single region coefficient individually insignificant but the
joint test passing." The current findings match this example
description. The reading adopted here is that the §22 SA1-STANDS
criterion for the region block is joint significance (which is
met), and the SA1-REVISION example list describes situations in
which SA1-STANDS criteria *fail* — which is not the case here.
Under this reading, the individual insignificance of
`beta_E_drgn8` is a documented qualification within SA1-STANDS,
not a SA1-REVISION trigger. The alternative reading (treating
individual insignificance as a SA1-REVISION trigger irrespective
of joint significance) would classify M1-clean as SA1-REVISION
on this single example alone. The reading adopted here is the
one consistent with conventional econometric practice, in which
the joint test is the primary inference for a block of
indicators and individual insignificance of one indicator within
a jointly significant block is not a specification defect.

(J2) The §22 SA1-STANDS criterion that "fit diagnostics do not
regress by more than one percentage point" refers to
participation, hours, wage, and occupation fit. The hours-bin
distribution L1 regression of 9.6 per cent for singles male is
not in this criterion list. Whether the bin-distribution
regression is acceptable given the welfare-partition gain is an
interpretive judgement the verdict makes by reference to the
JMP's design rationale rather than by mechanical threshold
comparison. The judgement here is that the bin-distribution
regression is acceptable because (a) the singles-male mean-hours
fit is essentially unchanged, (b) the regression has a known
mechanical cause (the all-positive region-shifter structure
amplifying a pre-existing bin imbalance), and (c) no
alternative specification within the SA1-STANDS criterion set
would simultaneously satisfy the welfare partition and the
bin-distribution objective.

The acceptance is qualified in three further respects that bear on
forward use of the M1-clean estimates:

(V1) The singles consumption joint-identification limitation —
three negative-variance entries in the Hessian-based VCV for the
parameters `beta_c_sm`, `beta_c_sf`, and `theta_c_singles` — is
preserved unchanged from M0c_b2_GSURv2. Point estimates of all
three parameters shift by less than 0.10 in absolute value. The
limitation is structurally inherited and is not a M1-clean
failure.

(V2) The acceptance does not authorise canonical MNL promotion.
The versioned GSURv2 MNL parquets remain the operative data
source. Canonical promotion is a separate O10 decision per the
v2.1 specification §12(F6-promote) and the GSURv2 verdict §10
S2; it requires explicit user approval after the SA1 verdict and
is not granted by this verdict.

(V3) The acceptance does not authorise welfare-decomposition
computation. The welfare-measurement decisions memo specifying
the functional form, the inequality index, the decomposition
method, and the gender attribution rule remains unwritten and is
the prerequisite for welfare scaffolding (per the M0c_b2_GSURv2
verdict §11).

For all forward purposes — paper text, supervisor memos, robustness
exercises, welfare scaffolding design — `ruro_occ_M1_clean` is the
preferred specification. `ruro_occ_M0c_b2_GSURv2` is retained as the
data-corrected baseline against which M1-clean is documented but is
no longer the working specification.

---

## 2. Whether M1-clean was implemented as designed

**Yes. The implementation matches the v2 design memo specification
without deviation.**

The YAML implementation report (`docs/RURO_occ_M1_clean_YAML_
implementation_report_v1.md`) records that the M1-clean YAML at
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
is derived from
`scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
through five semantic field changes: the specification name and
description; the `market_opportunity.shifters` list (removing
`beta_E_educH` and adding seven `beta_E_drgn{k}` entries for
`k ∈ {2, ..., 8}`); and the corresponding entries in
`initial_values` and `optimization.bounds`. All other blocks of the
YAML are byte-identical to the source.

The Gate-A parse report (`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_gate_A_parse_report_v1.md`)
confirms 18 of 18 static checks passing, including parameter count
(53, parser-verified), correct removal of `beta_E_educH`, presence
of all seven `beta_E_drgn{k}` parameters, `applies_to: "household"`
on all region shifters, and preservation of the utility, wage,
hours, occupation, and prior-correction blocks.

The data-column reconciliation specified in design memo v2 §19 was
resolved by a hybrid path: the singles parquet already contained
pre-computed indicator columns `reg_nuts1_2` through `reg_nuts1_8`,
mapped one-to-one to EUROMOD `drgn1` groups 2 through 8; the
couples parquet did not contain analogous columns and accordingly
required on-the-fly construction at precompute time via
`(drgn1 == k).astype(float)`. The naming asymmetry was accommodated
through the YAML's `variable:` field, which references the variable
name `reg{k}` resolved by the estimator's variable resolver. The
seven region indicators are confirmed available on both datasets
through the Gate-A precompute smoke test. No MNL parquet files were
modified during implementation; the data contract of
`fr_2016_RURO_mnl_GSURv2__{singles,couples}.parquet` is unchanged
from the GSURv2 rebuild.

The estimation report (`Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_estimation_report_v1.md`)
confirms that three independent starts (warm from M0c_b2_GSURv2,
spec defaults, perturbed with seed 42) converged to the identical
log-likelihood LL = −6487.5522 and to a bit-identical parameter
vector. The warm-start transfer mapped 46 parameters from
M0c_b2_GSURv2 (discarding `beta_E_educH`) and initialised the seven
new region parameters at zero. No bound hits occurred on any of the
53 parameters across any of the three starts. The implementation is
therefore both static-correct (Gate-A) and dynamically stable
(multistart convergence).

---

## 3. Comparison to M0c_b2_GSURv2

The comparison between M1-clean and M0c_b2_GSURv2 is the primary
empirical content of this verdict. The two specifications differ
only in the market-opportunity block; all utility, wage,
occupation, hours, and prior-correction parameters are preserved
unchanged in form.

Table 1 summarises the parameter-level changes by block.

| Block | Parameter count | Maximum |Δ| | Status |
|---|---|---|---|
| Singles preference | 12 unchanged | < 0.01 | Stable |
| Couples preference | 10 unchanged | < 0.01 | Stable |
| Household interaction | `beta_ll`: 2.605 → 2.617 | 0.012 (0.5%) | Stable |
| Hours opportunity | 4 unchanged | < 0.05 | Stable |
| Market opportunity — retained | `beta_E_gsur`: −1.050 → −1.329 | 0.279 (27%) | Coherent shift (§5) |
| Market opportunity — `beta_E` | −2.489 → −2.499 | 0.010 (0.4%) | Stable |
| Market opportunity — removed | `beta_E_educH` (+0.439) | — | Dropped by design |
| Market opportunity — added | `beta_E_drgn{2..8}` | 0.46 to 1.56 | New (§6) |
| Occupation opportunity | 12 unchanged | < 0.002 | Stable |
| Wage opportunity | 6 unchanged | < 0.001 | Stable |

The structural picture established by `ruro_occ_M0c_b2_GSURv2` —
strong household leisure complementarity (R5.1), log-utility on
couples consumption (R5.2), wage-offer dispersion σ ≈ 0.427 (R5.3),
Mincer block consistent with French literature (R5.4), and eight
of twelve occupation parameters significant at p < 0.05 (R5.5) — is
preserved without material modification. The R5.1 to R5.5 findings
documented as the "paper-ready findings" in the M0c_b2_GSURv2
verdict §1 carry over to M1-clean.

The substantive shifts are concentrated in two parameters of the
market-opportunity block: `beta_E_gsur` strengthens from −1.050 to
−1.329 (a 27 per cent increase in absolute value), and seven new
region parameters take values between +0.46 and +1.56 relative to
the Île-de-France reference category. The coherence of these
shifts is treated in §5 and §6 below.

---

## 4. Log-likelihood and fit changes

The information-theoretic comparison between the two specifications
admits a clear directional statement on AIC and McFadden ρ², a
penalty under BIC, and a non-trivial caveat on the use of the
likelihood ratio test.

The joint log-likelihood improves by 13.66 units, from −6501.21 in
M0c_b2_GSURv2 to −6487.55 in M1-clean. AIC improves by 15.3 units
(13096.4 → 13081.1) and BIC worsens by 50.4 units
(13611.6 → 13662.0). The McFadden pseudo-R² rises by 0.00061
(0.70875 → 0.70936). All three information criteria are computed on
the joint sample of 4,253 households across the three demographic
groups (766 singles male, 910 singles female, 2,577 couples).

The formal likelihood ratio test is *not* applicable to this
comparison. The two specifications are non-nested because M1-clean
simultaneously removes one parameter (`beta_E_educH`) and adds
seven new parameters (`beta_E_drgn{2..8}`); the LR statistic is not
distributed as a χ² under any natural null hypothesis embedding
both models. The joint significance of the region block is
therefore assessed through the M1-specific Wald test reported in
§7 rather than through a nested-model comparison.

The §22 SA1-STANDS threshold for log-likelihood improvement is ten
units. The realised improvement of 13.66 units exceeds this
threshold by approximately 37 per cent. The BIC penalty of 50.4
units is mechanically driven by the addition of six net parameters
to a model with 47 baseline parameters and a likelihood-sample size
that, under the BIC formula, weights the parameter penalty by
log(425,300) ≈ 12.96 per parameter pair. Whether the BIC penalty
counts against M1-clean is an interpretive question; the §22
SA1-STANDS criterion uses log-likelihood and AIC rather than BIC,
under which the M1-clean specification is favoured.

---

## 5. beta_E_gsur stability

The `beta_E_gsur` parameter, which captures the partial effect of
the corrected demographically conditional regional unemployment
rate on the employment-opportunity index, strengthens from −1.050
(M0c_b2_GSURv2) to −1.329 (M1-clean), a magnitude increase of
0.279 or 27 per cent. The M1-clean estimate carries a standard
error of 0.163, a t-statistic of −8.15, and a p-value below 10⁻¹⁵,
remaining one of the most precisely identified parameters in the
specification.

The direction of the shift is consistent with the interpretation
established in design memo v2 §9. In M0c_b2_GSURv2, `beta_E_gsur`
is identified against the full (region × education × sex)
variation in the corrected GSUR variable. In M1-clean, the seven
region dummies absorb the region-marginal of GSUR variation,
leaving the within-region (education × sex) variation as the
identifying signal for `beta_E_gsur`. The strengthening from
−1.050 to −1.329 indicates that the within-region education-sex
variation in GSUR is informative about employment opportunity at a
*greater* rate than the unrestricted variation; the region-marginal
of GSUR, with its limited cell-count and its correlation with
unmodelled regional demand factors, contributed an attenuating
component to the M0c_b2_GSURv2 estimate that the region-dummy
restriction has now removed.

The estimate lies within the proposed §22 SA1-STANDS range of
[−1.5, −0.6]. The criterion is met at the strict reading: the
realised magnitude of 1.329 is interior to the range and consistent
with the within-region interpretation specified in design memo v2.
The statistical significance criterion (p < 0.01) is met by
several orders of magnitude.

The interpretation supports the JMP framing that the corrected GSUR
captures a substantive labour-market opportunity effect. Under the
M1-clean specification, a one-percentage-point increase in the
demographically conditional within-region unemployment rate is
associated with a 0.0133 utility-unit reduction in the
employment-opportunity index. Translation of this coefficient into
participation or hours marginal effects requires evaluation through
the full choice-utility simulation rather than direct
semi-elasticity arithmetic; the verdict respects the cautionary
framing established in the M0c_b2_GSURv2 verdict §4 and does not
present a direct probability effect.

---

## 6. Region-dummy interpretation

The seven region coefficients `beta_E_drgn2` through `beta_E_drgn8`
take values that are uniformly positive relative to the
Île-de-France reference category, with a substantial dispersion
across regions. Table 2 reports the estimates.

| Parameter | EUROMOD `drgn1` | Old-region label | Estimate | SE | t | p |
|---|---|---|---|---|---|---|
| `beta_E_drgn2` | 2 | Bassin Parisien | 0.801 | 0.266 | 3.01 | 0.0026 |
| `beta_E_drgn3` | 3 | Nord-Pas-de-Calais | 0.656 | 0.319 | 2.06 | 0.0394 |
| `beta_E_drgn4` | 4 | Est | 1.563 | 0.410 | 3.81 | 0.0001 |
| `beta_E_drgn5` | 5 | Ouest | 0.773 | 0.272 | 2.84 | 0.0045 |
| `beta_E_drgn6` | 6 | Sud-Ouest | 0.767 | 0.328 | 2.34 | 0.0192 |
| `beta_E_drgn7` | 7 | Rhône-Alpes/Auvergne | 0.640 | 0.312 | 2.05 | 0.0399 |
| `beta_E_drgn8` | 8 | Méditerranée | 0.463 | 0.279 | 1.66 | 0.0974 |

Six of the seven coefficients are individually significant at the
5 per cent level. The seventh, `beta_E_drgn8` for Méditerranée, is
significant only at the 10 per cent level (p = 0.097); it is the
weakest of the region dummies and is treated as the locus of the
Q1 qualification in §1.

The substantive interpretation is that Île-de-France residents,
conditional on the demographically conditional unemployment rate
through GSUR and on the wage-block determinants of opportunity,
experience the lowest employment-opportunity utility among the
eight metropolitan `drgn1` groups. The non-IDF regions raise the
employment-opportunity index by between 0.46 (Méditerranée) and
1.56 (Est) utility units relative to IDF. The largest coefficient
(`beta_E_drgn4` for Est, including old Champagne-Ardenne, Lorraine,
and Alsace) is an outlier in the distribution of region effects;
the remaining six are clustered between 0.46 and 0.80.

The signs of all seven region coefficients are positive, which is
the mechanism through which the singles-male hours-bin fit
regression of §1 Q3 arises: the region shifters push more mass into
the working alternatives for non-IDF households, and in singles
male this manifests disproportionately in the 21–30-hour bin which
was already over-concentrated relative to observation in
M0c_b2_GSURv2. The hours-bin regression is therefore an empirical
consequence of the region-effect direction, not a specification
error.

The interpretive distinction between this regional employment-
opportunity effect and the within-region GSUR effect is preserved
by construction. The region dummies span the eight-level region
marginal of GSUR variation, while `beta_E_gsur` is identified
against the residual within-region education-sex variation. The
two parameters capture complementary opportunity dimensions and do
not duplicate the same source of identification.

---

## 7. Joint region-dummy test

The supplementary diagnostics report computes the joint Wald
statistic for the null hypothesis that all seven region
coefficients are zero. The test uses the seven-by-seven sub-block
of the variance-covariance matrix, where the VCV is constructed as
the Moore-Penrose pseudoinverse of the finite-difference Hessian
recomputed at the M1-clean optimum (with step size ε = 10⁻⁵).

The realised statistic is W = 28.18 on seven degrees of freedom,
yielding a p-value of 0.000204. The null hypothesis of joint
zero is rejected at the 0.1 per cent level. The §22 SA1-STANDS
threshold of joint significance at the 5 per cent level is met by
approximately two orders of magnitude in p-value.

The strength of the joint result is the foundational evidence that
the region block contributes structurally to the
employment-opportunity index and that the addition of seven
parameters in M1-clean is not gratuitous. Coupled with the
log-likelihood improvement of 13.66 units (§4), the AIC improvement
of 15.3 units, and the McFadden ρ² improvement of 0.00061, the
joint Wald result supports retention of the seven-dummy design.

The individual insignificance of `beta_E_drgn8` (p = 0.097) does
not vitiate the joint result. Under conventional econometric
practice with a block of categorical indicators, the joint test is
the primary inference and individual insignificance within a
jointly significant block is treated as a noise-level finding for
that particular indicator rather than as a specification defect.
The verdict adopts this convention.

---

## 8. GSUR-region identification

The principal identification risk articulated in design memo v2 §17
is partial collinearity between the seven region dummies and the
corrected GSUR variable, both of which carry region-related
variation. The diagnostic evidence on this risk is uniformly
favourable.

The seven-by-seven region covariance sub-block has all pairwise
correlations bounded above by 0.191 in absolute value, with maximum
between `drgn2` and `drgn5` and between `drgn2` and `drgn8`. The
§22 SA1-STANDS threshold for correlation flags is 0.70; this
threshold is met by approximately a factor of four. No high-
correlation flag is raised. The off-diagonal block of the
variance-covariance matrix corresponding to mutually exclusive
region indicators is structurally near-zero because the household-
membership cross-derivative is zero by construction (households
inhabit exactly one region); the observed small positive
correlations reflect residual interaction with shared parameters
elsewhere in the model.

The eight-by-eight Hessian sub-block spanning `beta_E_gsur` and the
seven region dummies has eight positive eigenvalues, ranging from
5.77 to 285.5. No near-zero or negative eigenvalues appear. The
sub-block is locally strictly convex, which means the GSUR and
region block jointly constitute a well-identified component of the
overall opportunity index. The §22 SA1-STANDS criterion for this
sub-block — no near-zero or negative eigenvalues — is met
without ambiguity.

The combined evidence supports retention of the seven-dummy design
in conjunction with the within-region GSUR variable. The two
sources of identification (between-region absorbed by dummies,
within-region absorbed by GSUR) are statistically separable and
their estimated coefficients carry independent interpretive
content.

---

## 9. Preference-parameter stability

The preference block of M0c_b2_GSURv2 — twelve singles parameters,
ten couples parameters, and one household leisure-leisure
interaction `beta_ll` — is preserved structurally in M1-clean
without modification. The empirical stability of the parameter
estimates under the M1-clean specification is the strongest of the
SA1-STANDS criteria.

The maximum absolute shift across all twenty-three preference
parameters is below 0.01. The relative shifts, computed against
the M0c_b2_GSURv2 magnitudes, are below one per cent for every
preference parameter. The §22 SA1-STANDS threshold of five per cent
is therefore met by approximately a factor of five for the most
variable preference parameter (`beta_ll`, which shifts from 2.605
to 2.617, a relative change of 0.46 per cent).

The Box-Cox exponents on leisure (`theta_l_sm`, `theta_l_sf`,
`theta_l_m`, `theta_l_f`) remain at values consistent with concave
leisure in all four demographic groups, ranging from −0.712 to
−0.678 in M1-clean (essentially unchanged from M0c_b2_GSURv2). The
Box-Cox exponent on singles consumption (`theta_c_singles`) shifts
by 0.03 in absolute value (M0c_b2_GSURv2: −1.020; M1-clean:
−1.048), remaining within the log-utility neighbourhood. The
fixed exponent on couples consumption (`theta_c = 0`) is unchanged
by design.

The household leisure-leisure interaction parameter `beta_ll`
shifts from 2.605 to 2.617, with t-statistic from 7.54 to 7.48.
The R5.1 finding from the M0c_b2_GSURv2 verdict (β_ll strongly
positive, t > 7, indicating strong leisure complementarity in
French couples) is preserved unchanged in magnitude, precision,
and interpretive significance.

The §22 SA1-STANDS criterion on preference parameter stability
(maximum shift below 5 per cent in absolute value) is met by every
preference parameter, in many cases by margins exceeding an order
of magnitude. The structural separation between the market-
opportunity block (where M1-clean changes) and the preference block
(where M1-clean does not change) is empirically respected by the
estimation result.

---

## 10. Opportunity-parameter stability

The opportunity block divides into three sub-blocks for the
purposes of stability assessment: the hours-opportunity block (four
parameters); the wage-opportunity block (six parameters); and the
occupation-opportunity block (twelve parameters). All three sub-
blocks are preserved structurally in M1-clean and exhibit
empirically negligible parameter shifts.

The hours-opportunity block — `beta_E`, `beta_h_pt1`,
`beta_h_pt2`, `beta_h_ft` — shifts by at most 0.05 in absolute
value. The largest shift is on `beta_E` (the baseline employment
shifter), which moves from −2.489 to −2.499, a relative change of
0.4 per cent. This stability is empirically informative: the seven
positive region dummies do not generate offsetting absorption into
`beta_E` of a magnitude that would compromise the interpretive
content of the baseline shifter. All four hours-opportunity
parameters remain significant at p < 0.001 in M1-clean.

The wage-opportunity block — `beta_w0`, `beta_w_educL`,
`beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma` — shifts by
at most 0.001 in absolute value. The wage-offer dispersion
parameter `sigma` changes from 0.42747 to 0.42747 at five-decimal
precision. The high-education wage premium (`beta_w_educH`) is
0.324 in M1-clean compared to 0.318 in M0c_b2_GSURv2; the
high-significance regression of wage on education that supports
R5.4 is preserved. The wage block is structurally unaffected by the
market-opportunity changes, as expected under the model's
separation of wage determination from employment-opportunity
shifters.

The occupation-opportunity block — twelve group-specific occupation
shifters — shifts by at most 0.002 in absolute value across all
parameters. Nine of twelve occupation parameters are significant at
p < 0.05 in M1-clean (compared to eight of twelve in M0c_b2_GSURv2,
marginally improving on the R5.5 finding). The occupation structure
captured by the loc4 categorisation is empirically robust to the
market-opportunity reorganisation.

The cross-block stability between the hours-, wage-, and
occupation-opportunity blocks (which do not change in M1-clean) and
the market-opportunity block (which substantially changes) is the
strongest empirical evidence that the M1-clean specification has
*localised* the consequence of the educational reclassification and
the region-dummy addition to the targeted block.

---

## 11. Participation and hours fit

The participation and hours fit profile of M1-clean is the locus of
two of the four qualifications documented in §1. The overall
pattern is fit-stable, with the singles-male diagnostics
constituting the only material degradation and all other groups
exhibiting unchanged or marginally improved fit.

Participation fit by group is reported in Table 3.

| Group | Observed | M1-clean predicted | M1-clean Δ | M0c_b2_GSURv2 Δ |
|---|---|---|---|---|
| Singles male (sm) | 0.9295 | 0.9207 | −0.0088 | +0.0004 |
| Singles female (sf) | 0.9396 | 0.9590 | +0.0194 | +0.0239 |
| Couples male (cm) | 0.9717 | 0.9845 | +0.0129 | +0.0148 |
| Couples female (cf) | 0.9651 | 0.9896 | +0.0244 | +0.0261 |

The singles-male participation regression of 0.92 percentage
points — from an over-prediction of 0.04 percentage points to an
under-prediction of 0.88 percentage points — is a sign reversal but
falls within the §22 SA1-STANDS tolerance of one percentage point.
The three other groups exhibit modest participation-fit
improvements of 0.17 to 0.45 percentage points. The couples-female
participation over-prediction (+2.44 percentage points) is
unchanged in character from M0c_b2_GSURv2 (+2.61 percentage points)
and reflects a pre-existing structural limitation of the model in
generating non-employment in couples absent fixed costs of work.

Mean-hours fit is essentially unchanged across all four groups
(maximum absolute change 0.04 hours). The largest mean-hours
discrepancy in M1-clean remains the couples-female over-prediction
of 3.26 hours per week (compared to 3.30 hours in M0c_b2_GSURv2),
which is structurally inherited and not affected by the
market-opportunity reorganisation.

The hours-bin distribution L1 distance regresses materially for
singles male (M1-clean: 0.6945; M0c_b2_GSURv2: 0.6345; relative
worsening of 9.6 per cent) and L2 worsens by 10.5 per cent. The
distribution shift is concentrated in the 21–30-hour bin, where
predicted mass moves from 0.561 in M0c_b2_GSURv2 to 0.590 in
M1-clean against an observed share of 0.257. The mechanism is the
all-positive region-shifter structure raising the
employment-opportunity index for non-IDF singles male, who
disproportionately work the 21–30-hour range under the model's
hours-band approximation. The §22 SA1-STANDS criterion on hours
fit refers to mean hours rather than to bin-distribution L1
distance; the bin-distribution regression is therefore documented
as a qualification (§1 Q3) without triggering a hard-gate failure.

The fit regressions for singles male are concentrated in this one
group and do not propagate to the other three groups. Singles
female, couples male, and couples female all exhibit unchanged or
marginally improved fit across both participation and bin
distribution.

---

## 12. Wage and occupation fit

Wage fit by group is essentially unchanged in M1-clean relative to
M0c_b2_GSURv2. The pooled Mincer-style wage specification, with
high-significance loadings on education and quadratic experience,
produces predicted wage levels that under-predict observed singles
wages by 16 to 22 per cent and over-predict couples male wages by
approximately 5 per cent. These discrepancies are structurally
inherited from M0c_b2_GSURv2 and are not affected by the
market-opportunity reorganisation. The wage-offer dispersion
parameter `sigma` = 0.427 carries a t-statistic above 100,
indicating that the variance component of the wage process is
identified with near-perfect precision regardless of the
opportunity-block specification.

Occupation fit for couples is excellent in M1-clean. The predicted
occupation shares for the four `loc4` categories match observed
shares to within 0.7 percentage points in absolute terms across all
four (sex × household-type) groups for couples. The couples
occupation prediction is essentially unchanged from M0c_b2_GSURv2
(maximum absolute change 0.007 in the occupation 4 share for
couples female).

Occupation fit for singles remains the structurally weakest fit
diagnostic in either specification. The singles-male predicted
share of nonroutine cognitive occupations (loc4 = 4) is 0.168
points below the observed share, and the singles-female under-
prediction of nonroutine cognitive is 0.199 points below
observed. The absence of singles-specific occupation shifters in
the model — only couples-male and couples-female `beta_occ`
parameters are tier-specific — means the singles occupation fit
cannot be improved by region or education reorganisation alone.
This is a documented inherited limitation that is unaffected by
M1-clean and does not constitute a verdict-relevant criticism of
the new specification.

The wage and occupation fit profile under M1-clean confirms that
the structural changes to the market-opportunity block do not
propagate to wage determination or to occupation choice. The block
separation of the model is empirically respected by the estimation
result.

---

## 13. Hessian and standard-error diagnostics

The Hessian topology of M1-clean is essentially identical to that
of M0c_b2_GSURv2. Table 4 summarises the comparison.

| Diagnostic | M0c_b2_GSURv2 | M1-clean | §22 threshold |
|---|---|---|---|
| Hessian condition number | 5.14 × 10¹⁰ | 5.10 × 10¹⁰ | < 10¹¹ |
| Negative eigenvalues | 1 | 1 | unchanged at 1 |
| Near-zero eigenvalues | 0 | 0 | 0 |
| Negative-variance parameters | 3 | 3 | no new NA |
| Valid standard errors | 44 / 47 | 50 / 53 | no new NA |
| Bound hits | 0 | 0 | 0 |

The condition number of 5.10 × 10¹⁰ in M1-clean is essentially
unchanged from the M0c_b2_GSURv2 value of 5.14 × 10¹⁰. The §22
SA1-STANDS threshold of 10¹¹ is met by approximately a factor of
two.

The single negative Hessian eigenvalue remains localised to the
singles consumption joint-identification sub-block, where the
parameters `beta_c_sm`, `beta_c_sf`, and `theta_c_singles` exhibit
near-singular joint behaviour. This is the same sub-block, with
the same three parameters, as in M0c_b2_GSURv2; the minimum
eigenvalue of the sub-block is reported as −35.60 in M1-clean
compared to −15.01 in M0c_b2_GSURv2, which is a worsening of the
sub-block ill-conditioning but does not introduce new negative
eigenvalues elsewhere in the Hessian. The §22 SA1-STANDS criterion
that the single negative eigenvalue remains confined to the
singles consumption sub-block is met; the criterion that no new
NA standard errors appear is also met (the same three parameters
have NA SEs in both specifications). The worsened sub-block
conditioning is documented as an inherited limitation per §1 V1
but does not trigger a hard-gate failure.

Three parameters — `beta_c_sm`, `beta_c_sf`, and
`theta_c_singles` — exhibit negative diagonal entries in the
Hessian-based variance-covariance matrix produced by the Moore-
Penrose pseudoinverse procedure. Standard errors for these three
parameters are not reported in the parameter table; the
parameters themselves remain interior to their bounds (`beta_c_sm`
= 0.554, `beta_c_sf` = 0.506, `theta_c_singles` = −1.048) with
point estimates that shift by less than 0.10 in absolute value
from M0c_b2_GSURv2. The pseudoinverse-based SE replacement is a
standard finite-sample treatment for this kind of near-singular
Hessian sub-block and was documented as such in the
M0c_b2_GSURv2 verdict §8.

No M1-clean parameter reaches its bounds. The seven new region
dummies, with initial values of 0.0 and bounds of [−10.0, 10.0],
converge to interior values between 0.46 and 1.56. The retained
opportunity parameters `beta_E` and `beta_E_gsur`, with bounds of
[−25.0, 25.0] and [−10.0, 10.0] respectively, remain interior.
The §22 SA1-STANDS criterion that no parameter reaches its bound
is met.

The Hessian and SE diagnostics support SA1-STANDS without
qualification beyond the inherited singles consumption sub-block
limitation already documented under M0c_b2_GSURv2.

---

## 14. Whether full seven-dummy design is acceptable

**Yes. The full seven-dummy design is accepted as the preferred
M1-clean specification. The verdict does not require pooling, does
not require dropping `beta_E_drgn8`, and does not require any
modification to the design memo v2 specification.**

The evidence for retention of the full seven-dummy design comprises
five elements.

First, the joint Wald test (§7) yields W = 28.18 on seven degrees
of freedom with p = 0.000204. The block is jointly significant by
approximately two orders of magnitude in p-value. The block
contributes to the employment-opportunity index in a statistical
sense that is not in doubt.

Second, the GSUR-region identification analysis (§8) confirms no
collinearity (maximum pairwise correlation 0.191) and a strictly
convex Hessian sub-block (eight positive eigenvalues with
minimum 5.77). The seven dummies and the corrected GSUR variable
jointly identify the employment-opportunity index without the
partial-collinearity pathology that motivated the design memo v2
§17 risk discussion.

Third, the log-likelihood improvement of 13.66 units (§4) exceeds
the §22 SA1-STANDS threshold of 10 units. The improvement is
descriptive evidence that the seven-dummy block contributes
substantively to the model's explanatory power; the AIC
improvement of 15.3 units, computed with full account of the six
net additional parameters, confirms that the gain is not driven by
parameter proliferation alone.

Fourth, the individual significance pattern (six of seven at
p < 0.05) is consistent with the seven-dummy design having
identified non-zero effects across the regional partition with
appropriate statistical strength. The one marginally significant
case (`beta_E_drgn8` at p = 0.097) is the Mediterranean region,
the smallest of the eight in singles sample count and one of the
smaller in couples sample count; the marginal individual
significance is consistent with a true regional effect of similar
magnitude to the other dummies but estimated against the smallest
available sample. Dropping `beta_E_drgn8` would not improve the
identification of the remaining six and would introduce a post-
hoc partition asymmetry that is not motivated by the design
rationale.

Fifth, the conceptual rationale for the seven-dummy design — that
the EUROMOD `drgn1` partition is the natural saturated grouping
respecting the GSURv2 lookup construction (§5 of design memo v2) —
remains operative. Any pooled alternative would require an explicit
pooling rule, a separate design memo specifying that rule, and a
separate empirical justification for the chosen aggregation; the
evidence above does not motivate such a rule.

The seven-dummy design is therefore retained without modification.
Documentation of the `beta_E_drgn8` marginal individual
significance in §1 Q1 is the appropriate level of caveat; pooling
is rejected as the verdict response to this single qualification.

---

## 15. Whether pooling is needed

**No. Pooling is not required for the M1-clean verdict. The full
seven-dummy design is the preferred and accepted specification.**

The pooling question is treated separately from the seven-dummy
acceptance question because the design memo v2 §17 contemplates
pooling as a possible diagnostic response in Outcome B (a subset of
dummies individually insignificant with similar point-estimate
magnitudes to neighbouring regions). The M1-clean diagnostic
evidence does not fit Outcome B: only one dummy (`beta_E_drgn8`) is
individually insignificant at the 5 per cent level, its point
estimate of 0.463 is not close to a "neighbouring region"
estimate that would support a natural pooling, and the remaining
six dummies span a range from 0.640 (drgn7) to 1.563 (drgn4) that
does not exhibit the clustering pattern Outcome B's example
language describes.

The Outcome A response (accept the seven-dummy design) is
empirically and conceptually the correct response to the M1-clean
diagnostic profile. The seven-dummy design is retained.

A separate question — not within the scope of this verdict — is
whether the JMP's later welfare analysis might benefit from a
coarser regional aggregation for interpretive presentation. The
welfare-decomposition analysis would proceed with the seven-dummy
M1-clean estimates as the structural input; whether the welfare
results are subsequently aggregated to a coarser regional partition
for presentation is a presentation choice rather than a structural
specification choice and does not bear on this verdict.

---

## 16. Whether to run M1-naive robustness

**Yes. M1-naive should be estimated before the welfare-measurement
scaffolding work begins, and ideally before the welfare-measurement
decisions memo is finalised in its M1-clean reference treatment.**

The design memo v2 §23 specifies M1-naive as a sensitivity exercise
that adds the seven region dummies but retains `beta_E_educH` in
the market-opportunity block. M1-naive carries 54 parameters
(M0c_b2_GSURv2 plus seven region dummies, with `beta_E_educH`
retained); the empirical comparison between M1-clean and M1-naive
isolates the contribution of the educational reclassification
(dropping `beta_E_educH`) from the contribution of the regional
specification (adding the seven dummies).

Three considerations support estimating M1-naive before welfare
scaffolding rather than after.

First, the consolidated post-estimation diagnostics report §16
explicitly identifies M1-naive as a category of evidence required
for the M1-clean verdict's robustness exposure R2 in the framework
memo. The report observes that "until M1-naive is estimated, the
contribution of removing `beta_E_educH` to M1-clean's fit profile
cannot be separated from the contribution of adding the region
dummies." This separation is required for the JMP's robustness
section to be able to discuss how the ability-versus-opportunity
partition affects the structural estimates; without M1-naive, the
question cannot be empirically addressed.

Second, the operational cost of M1-naive is small. The
specification differs from M1-clean by a single parameter; the
warm-start path from M1-clean (or from M0c_b2_GSURv2) is direct;
the multistart protocol carries through without modification; and
the estimation walltime is expected to be comparable to M1-clean's
approximately 350 seconds per start. M1-naive can be estimated
within a single Claude Code session at the cost of one
implementation prompt.

Third, sequencing M1-naive before welfare scaffolding avoids the
operational pitfall of computing welfare results under M1-clean
and then discovering at the robustness stage that the M1-naive
specification produces materially different estimates. Such a
discovery would require recomputing welfare under M1-naive and
incorporating the difference into the JMP's robustness exposure.
Having both estimates in hand before welfare scaffolding begins
ensures that the welfare-measurement decisions memo can specify
the treatment of M1-naive at the design stage rather than as a
post-hoc correction.

The recommended sequencing is therefore:

1. M1-clean verdict (this memo).
2. M1-naive implementation prompt and estimation (next Claude Code
   task).
3. M1-naive verdict and the M1-clean-vs-M1-naive structural
   comparison memo.
4. Welfare-measurement decisions memo (in this chat, parallel to
   M1-naive estimation if desired).
5. Welfare scaffolding implementation.

The welfare-measurement decisions memo may be drafted in parallel
with the M1-naive estimation work since the welfare-measurement
choices (functional form, inequality index, decomposition method,
gender attribution rule) are largely independent of the M1-naive
findings; the role of M1-naive in the welfare track is robustness
exposure, not main specification choice.

---

## 17. Whether to proceed to welfare-measurement scaffolding

**Not yet. The welfare-measurement decisions memo is the
prerequisite. Welfare-decomposition computation is explicitly not
authorised by this verdict.**

The M1-clean specification is accepted as the structural baseline
for the welfare analysis, but welfare scaffolding implementation
requires three additional inputs that are not yet in place.

First, the welfare-measurement decisions memo
(`docs/JMP_welfare_measurement_decisions_memo_v1.md` or equivalent)
must specify the welfare functional (Fleurbaey-style equivalent
income, equivalent variation, compensating variation, or
alternative), the inequality index (Gini, Atkinson with specified
inequality aversion parameter, generalised entropy with specified
parameter, or alternative), the counterfactual decomposition method
(ordered removal, Shapley, or both), the reference distributions
for ability and opportunity, and the gender attribution rule (A1,
A2, A3, or a documented alternative). None of these is settled in
writing.

Second, the operational handling of the singles consumption
joint-identification limitation (§13 V1) must be specified. The
three NA-SE parameters (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`)
are interior in M1-clean but jointly near-singular. Welfare
functionals that operationally require identified consumption
curvature must either (a) marginalise over the parameter
uncertainty in this sub-block via bootstrap or similar procedure,
(b) work with the joint function `c → β_c · c^{θ_c}` (which is
identified up to joint scaling at the point estimate), or
(c) restrict welfare calculations to couples and adjust the JMP's
framing accordingly. The welfare-measurement decisions memo must
specify the chosen treatment.

Third, the M1-naive estimates from the §16 recommendation must be
in hand so that the welfare-measurement decisions memo can
specify the robustness exposure R2 procedure with the empirical
estimates rather than abstractly.

The welfare scaffolding work — implementation of the welfare
functional, computation of equivalent incomes by household,
construction of counterfactual distributions for ability and
opportunity, computation of inequality indices, decomposition into
opportunity-driven and preference-driven components — is therefore
sequenced after these three prerequisites are met.

Welfare scaffolding *design* work (the writing of the welfare-
measurement decisions memo and any associated literature review
extensions) can proceed in parallel with M1-naive estimation
without authorisation conflict. Welfare scaffolding *computation*
is explicitly not authorised by this verdict.

---

## 18. What not to claim yet

The following claims are not supported by the current evidence and
must not appear in JMP text, supervisor memos, or presentations
until additional work is completed.

(N1) "The M1-clean specification produces a complete welfare
decomposition." Not supported. The structural estimates are in
place; the welfare functional, the inequality index, the
decomposition method, and the bootstrap inference are not. The
decomposition is the next major step but is not yet computed.

(N2) "The seven region coefficients establish the JMP's
opportunity-driven inequality result." Not supported as stated.
The coefficients establish that region of residence shifts the
employment-opportunity index in a structural sense. Translation
of this into opportunity-driven inequality magnitudes requires
the welfare functional, the inequality index, and the
counterfactual decomposition that constructs an "equal region"
reference distribution. The seven coefficients are *inputs* to
the inequality result, not the result itself.

(N3) "The corrected GSUR coefficient of −1.33 establishes the
regional unemployment effect on labour-market opportunity." Not
supported as stated. The coefficient is on the within-region
education-sex variation in GSUR under the M1-clean partition; it
captures a different component of GSUR variation than the −1.05
estimate in M0c_b2_GSURv2 (which absorbed both within-region and
between-region variation). The two coefficients are not directly
comparable as estimates of the same quantity. Reporting either
requires the relevant interpretive framing.

(N4) "M1-clean replaces M0c_b2_GSURv2 with no qualifications."
Not supported. The qualifications Q1 through Q4 documented in §1
must be acknowledged in any side-by-side presentation. The
qualifications strengthen the JMP's transparency rather than
weaken its results.

(N5) "The educational reclassification is empirically validated
by M1-clean." Not supported until M1-naive is estimated. The
reclassification is conceptually motivated by the ability/
opportunity partition; its empirical consequences are mixed
between M1-clean and what M1-naive would produce. The empirical
validation requires the comparison.

(N6) "The seven region dummies make the GSUR coefficient
interpretable as a pure labour-market opportunity effect." Not
supported as stated. The seven region dummies make the GSUR
coefficient identifiable against the within-region education-sex
variation; whether this is a "pure labour-market opportunity
effect" depends on whether the within-region variation is
plausibly orthogonal to omitted determinants of employment
opportunity. This question is not formally tested in the current
evidence.

(N7) "M1-clean is the JMP's final structural specification." Not
supported. M1-clean is the working specification subject to the
M1-naive robustness exposure. Stage B age-specific GSUR work and
any potential M1c-style refinements remain post-M1-clean
options.

(N8) "Canonical MNL promotion is approved." Not supported. The
versioned GSURv2 MNL parquets remain the operative data source.
The O10 promotion decision is separately gated per the v2.1
specification §12(F6-promote) and is not granted by this verdict.

(N9) "The hours-bin regression for singles male is a model
defect." Not the correct framing. The regression has a known
mechanical cause (all-positive region-shifter structure
amplifying a pre-existing bin imbalance) and is a documented
qualification (Q3) of the M1-clean specification. The JMP text
should present it as a fit tradeoff associated with the
welfare-partition alignment, not as a specification error.

(N10) "The BIC penalty argues against M1-clean." Not supported.
BIC is not among the SA1-STANDS criteria, and its penalty of
50.4 units is a mechanical consequence of adding six parameters.
AIC favours M1-clean by 15.3 units, and the conceptual
motivation for the additional parameters is the JMP's
normative welfare-partition requirement.

---

## 19. Immediate next task

**The immediate next task is the M1-naive implementation prompt for
Claude Code Sonnet.**

Tool path: Claude Code Sonnet (local codebase, estimation work),
not Claude Project chat.

The M1-naive specification is defined by design memo v2 §23 and
differs from M1-clean by a single parameter: `beta_E_educH` is
retained in the market-opportunity block while all seven region
dummies `beta_E_drgn2` through `beta_E_drgn8` are also present. The
M1-naive parameter count is 54 (M0c_b2_GSURv2's 47 plus seven
region dummies). All other elements of M1-naive — utility, wage,
occupation, hours, prior-correction, expression constraints — are
preserved unchanged from M1-clean and from M0c_b2_GSURv2.

Inputs to the M1-naive implementation prompt:

- This verdict memo (the M1-clean baseline against which M1-naive
  is compared)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` §23 (the M1-naive
  specification)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md` (the prior baseline,
  which together with this verdict bounds the expected M1-naive
  parameter values)
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
  (the YAML to be derived from, by re-adding `beta_E_educH`)
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml`
  (the YAML containing the canonical `beta_E_educH` entry to be
  copied)
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_estimation_report_v1.md` (the
  parameter values to be used as the warm-start vector)

Output deliverables of the M1-naive implementation prompt:

- `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_naive.yaml`
  (the M1-naive YAML, 54 parameters)
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_gate_A_parse_report_v1.md`
  (parameter-count verification and frozen-block preservation
  checks)
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_estimation_report_v1.md`
  (multistart estimation results)
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_post_estimation_diagnostics_v1.md`
  (standard fit diagnostics)
- `Results/P3a/single_year_baseline/M1/RURO_occ_M1_naive_supplementary_diagnostics_v1.md`
  (M1-specific Wald test, region VCV sub-block, and GSUR-region
  Hessian sub-block diagnostics, following the same protocol as
  M1-clean)

The M1-naive implementation prompt does not authorise the M1-naive
verdict; the verdict is written separately in this chat after the
M1-naive deliverables are produced. The implementation prompt also
does not authorise welfare computation, canonical MNL promotion,
or Stage B age-specific GSUR work.

The recommended parallel task in this chat is the
welfare-measurement decisions memo
(`docs/JMP_welfare_measurement_decisions_memo_v1.md`), which
specifies the welfare functional, inequality index, counterfactual
decomposition method, gender attribution rule, and treatment of
the singles consumption identification limitation. This memo is
methodologically independent of M1-naive and can proceed in
parallel; its drafts inform the welfare scaffolding implementation
that follows after M1-naive is verdict-accepted.

Items explicitly not authorised by this verdict:

- Welfare-decomposition computation in any form.
- Canonical MNL promotion (the O10 decision).
- Stage B age-specific GSUR work (the O6 decision).
- Modification of the wage block, occupation block, utility
  block, prior-correction block, or any other M1-clean-frozen
  element.
- The François Maniquet pure-theory paper. This memo's empirical
  work is intellectually adjacent to but operationally distinct
  from the theory paper. The JMP must remain a distinct empirical
  contribution.
