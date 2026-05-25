# RURO occ M1-naive — Robustness Verdict v1

Date: 2026-05-18

Specification: `estimation_spec_ruro_occ_M1_naive.yaml` (54 free
parameters, parser-verified, frozen blocks preserved relative to
`estimation_spec_ruro_occ_M1_clean.yaml`)

Selected estimation run:
`outputs/estimates/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_17-50-20/`
(Start 1, warm from M1-clean with `beta_E_educH = 0.4386`; all
three independent starts converge to LL = −6485.5287 and to a
bit-identical parameter vector)

Primary evidence:
- `Results/RURO_occ_M1_naive_estimation_report_v1.md`
- `Results/RURO_occ_M1_naive_post_estimation_diagnostics_v1.md`
- `Results/RURO_occ_M1_naive_supplementary_diagnostics_v1.md`
- `Results/RURO_occ_M1_naive_gate_A_parse_report_v1.md`
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_naive_YAML_implementation_report_v1.md`

Reference documents:
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the preferred structural
  baseline against which M1-naive is compared)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` §22 (the SA1
  acceptance rule that M1-clean satisfied)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md` §23 (the M1-naive
  specification design as a robustness exposure, not a candidate
  primary baseline)
- `docs/jmp_methodology/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md`
  (the multi-year strategy, used here for sequencing implications
  only)
- `Results/RURO_occ_M1_clean_post_estimation_diagnostics_v1.md`
  (the M1-clean diagnostic comparison reference)
- `Prompts/JMP_ability_vs_opportunity_framework_v1.md` (the welfare
  framework whose ability/opportunity partition M1-naive
  intentionally suspends for robustness purposes)

Scope of verdict: structural robustness assessment of M1-naive
relative to the M1-clean preferred baseline. The verdict
adjudicates whether the borderline statistical evidence for
retaining `beta_E_educH` in the market-opportunity block is
sufficient to overturn the M1-clean welfare-partition design. It
does not authorise canonical MNL promotion (O10), welfare-
decomposition computation, Stage B age-specific GSUR work, or
pooled multi-year estimation; those decisions are separately
gated in their respective verdict pathways.

---

## 1. Verdict

**M1-naive is a robustness check, not a replacement.
`ruro_occ_M1_clean` remains the preferred structural baseline.**

The verdict rests on the strict adjudication of two distinct
inferential questions. The first question — whether the
empirical evidence is consistent with `beta_E_educH` carrying a
non-zero coefficient in the market-opportunity block — is
borderline at conventional thresholds: the nested likelihood-
ratio test against M1-clean yields $\chi^2(1) = 4.047$ with
$p \approx 0.044$, and the parameter-level Wald test yields $t =
1.938$ with $p \approx 0.053$. The two inferential routes
straddle the 5 per cent threshold. Neither route delivers
decisive evidence at the conventional significance level
typically required to overturn a precommitted specification.

The second question — whether `beta_E_educH` belongs
conceptually in the market-opportunity block under the JMP's
welfare partition — is settled by the partition itself, not by
the empirical evidence. The M1-clean design memo §6 articulates
the ability/opportunity partition under which education is
classified as an ability dimension carrying responsibility-
relevant content through the wage process, not as a circumstance
carrying compensation-relevant content through the employment-
opportunity index. Under this partition, `beta_E_educH` should
not enter the market-opportunity block irrespective of whether
the empirical evidence is decisive, marginal, or null. The
M1-naive specification is therefore conceptually inconsistent
with the JMP's welfare framework by design; its only legitimate
role is as a sensitivity exposure quantifying the empirical
consequences of suspending the partition.

The empirical evidence reinforces, rather than overturns, this
conclusion. M1-naive imposes three measurable costs against the
2.02-unit log-likelihood gain. First, the Bayesian information
criterion penalises M1-naive by 8.9 units relative to M1-clean
(BIC moves from 13662.0 to 13670.9), a mechanical consequence of
adding one parameter to a model whose sample is large. Second,
the singles-male participation fit regresses from a 0.88
percentage-point underprediction in M1-clean to a 2.92
percentage-point underprediction in M1-naive, exceeding the
M1-clean SA1 one-percentage-point tolerance by approximately a
factor of two. Third, the singles-male hours-bin L1 distance
worsens from 0.6945 to 0.7781, a 12.1 per cent relative
regression that compounds the 9.6 per cent regression already
incurred in the M1-clean transition from M0c_b2_GSURv2.

The supplementary diagnostics provide a structural interpretation
of the borderline evidence that further weakens the case for
M1-naive replacement. The `beta_E_educH` ↔ `beta_E_gsur`
correlation in the recomputed Hessian-based VCV is 0.640, below
the 0.70 collinearity flag threshold but materially above the
correlation magnitudes observed elsewhere in the opportunity
block. The corresponding mechanical response in the parameter
estimates — `beta_E_gsur` reverting from −1.329 in M1-clean to
−1.048 in M1-naive, almost exactly recovering the M0c_b2_GSURv2
value of −1.050 — demonstrates that the `beta_E_educH`
coefficient operates predominantly through reallocation of
explanatory weight from GSUR rather than through the
identification of an independent education-on-opportunity
channel. The reallocation is not complete: GSUR retains a
$t$-statistic of −4.77 in M1-naive ($p < 10^{-6}$), confirming
that the within-region education-sex variation in GSUR remains a
substantive opportunity shifter. But the educH contribution is
partially redundant with GSUR by construction, weakening the
argument that M1-naive identifies a genuinely new opportunity
channel that the M1-clean specification has wrongly omitted.

The verdict acknowledges that the LR test ($p \approx 0.044$) is
nominally significant at 5 per cent and that this would, in a
purely data-driven specification choice, constitute marginal
support for retaining `beta_E_educH`. The verdict's conclusion
that M1-clean nonetheless remains preferred reflects the
combination of three considerations: the Wald test fails to
confirm the LR signal at the same threshold; the fit costs are
disproportionate to the borderline statistical gain; and the
welfare partition that governs the JMP's substantive contribution
classifies education as ability irrespective of marginal
empirical fluctuations. The verdict therefore treats M1-naive as
its design memo §23 intended — as a sensitivity exposure
documenting the consequences of suspending the partition, not as
a candidate primary specification.

For all forward purposes — paper text, supervisor memos,
sequencing of subsequent empirical work, welfare scaffolding
design — `ruro_occ_M1_clean` remains the JMP's preferred
structural specification, subject only to the future possibility
of replacement by a pooled multi-year specification under a SA2-
style verdict per the v3.1 multi-year strategy memo. M1-naive is
retained on the project record as a robustness exposure
addressing the R2 robustness question in the framework memo and
will be reported as such in the JMP's robustness section. The
sequencing implication is that the multi-year feasibility audit
becomes the immediate next operational step, with the welfare-
measurement decisions memo proceeding in parallel.

---

## 2. Why M1-naive was run

The M1-naive specification was designed in the M1-clean design
memo §23 as the sensitivity exposure for the ability-versus-
opportunity partition. The framework memo's R2 robustness
exposure asks how the JMP's welfare decomposition is affected by
the partition decision; on the structural side, the question is
answered empirically by the M1-clean-versus-M1-naive comparison.

Three motivations support running the sensitivity.

First, the M0c_b2_GSURv2 estimate of `beta_E_educH` (+0.439 with
$p = 0.052$) was itself marginal. The M1-clean design memo §2
identified this borderline significance as evidence that the
M0c_b2_GSURv2 specification was partially absorbing the
education-region correlation that the corrected GSUR variable
should resolve. The M1-naive estimation tests this conjecture
directly: if `beta_E_educH` becomes substantively insignificant
under the M1-clean specification's region-controlled framework,
the JMP's reclassification of education as ability gains
empirical support. If `beta_E_educH` retains or strengthens its
borderline significance, the reclassification rests on the
conceptual partition alone, without empirical reinforcement.

Second, the structural shift of `beta_E_gsur` from −1.050 in
M0c_b2_GSURv2 to −1.329 in M1-clean — a 27 per cent
strengthening — was not anticipated by the design memo's pre-
estimation predictions. The M1-clean verdict §5 documented the
shift as consistent with the within-region interpretation of the
GSUR variable, but the structural cause of the magnitude was
left for subsequent investigation. The M1-naive estimation
provides the diagnostic: if removing `beta_E_educH` (the M1-clean
treatment) shifts `beta_E_gsur` by approximately the magnitude
of the M0c-to-M1-clean change, the structural role of
`beta_E_educH` in M1-clean's GSUR coefficient is empirically
verified.

Third, the JMP's robustness section requires the comparison as
evidence that the welfare results are robust to the partition
decision. The framework memo's R2 exposure is one of nine
robustness exposures (R1 through R9) that the JMP commits to in
its empirical section. M1-naive is the structural-side input to
R2; the welfare-side complement is the welfare-decomposition
comparison under the two specifications, which will be computed
when welfare scaffolding is implemented.

The M1-naive estimation was therefore neither a discretionary
addition nor a candidate primary specification. It was a
precommitted sensitivity exposure whose role is to inform the
JMP's robustness section. The interpretation of its findings is
governed by this role rather than by a default rule that the
better-fitting specification wins.

---

## 3. Whether M1-naive was implemented as designed

**Yes. The implementation conforms to the design memo §23
specification without deviation.**

The YAML implementation report records that the M1-naive YAML
differs from the M1-clean YAML by exactly five fields: the
`specification.name`, the `specification.description`, one entry
in `market_opportunity.shifters` (the `beta_E_educH` line copied
from M0c_b2_GSURv2), one entry in `initial_values`
(`beta_E_educH: 0.0`), and one entry in `optimization.bounds`
(`beta_E_educH: [-10.0, 10.0]`). All other blocks of the YAML —
utility, wage, occupation, hours, prior-correction, expression
constraints, solver configuration — are byte-identical to
M1-clean.

The Gate-A parse report records that all 23 static checks pass.
The parameter count of 54 is parser-verified and corresponds
exactly to the M1-clean count of 53 plus the re-added
`beta_E_educH`. The frozen blocks are preserved as byte-identical
to M1-clean. The `educH` data column is pre-existing in both the
singles and couples MNL parquets (it was already in use under
M0c_b2_GSURv2) and required no parquet modification. The seven
region indicators required by the M1-clean inheritance are
resolved at precompute time through the same mechanism as in
M1-clean: pre-existing `reg_nuts1_*` columns in singles, on-the-
fly construction from `drgn1` in couples.

The estimation report confirms that three independent multistart
runs converged to the identical log-likelihood
LL = −6485.5287 and to a bit-identical parameter vector. The
warm-start run from M1-clean (with `beta_E_educH` initialised at
the M0c_b2_GSURv2 estimate of 0.4386) converged in 10
iterations; the spec-defaults run (with `beta_E_educH = 0.0`)
converged in 1 iteration, indicating that the M0c attractor is
near the gradient direction from zero initialisation; the
perturbed run (with seed 42 and a 5 per cent perturbation)
required 94 iterations and recovered the same attractor. No
bound hits occurred on any of the 54 parameters across any of
the three starts.

The M1-naive estimation is therefore both static-correct (Gate-A
PASS) and dynamically stable (multistart convergence to a unique
attractor). The implementation provides a clean empirical
platform for the structural comparison with M1-clean.

---

## 4. Comparison to M1-clean

The comparison between M1-naive and M1-clean is the principal
empirical content of this verdict. The two specifications differ
only in the market-opportunity block: M1-naive includes one
additional parameter (`beta_E_educH`) and is otherwise byte-
identical to M1-clean. Table 1 summarises the parameter-level
changes by block.

| Block | Parameter count | Maximum $|\Delta|$ | Status |
|---|---|---|---|
| Singles preference | 12 unchanged | < 0.006 | Stable |
| Couples preference | 10 unchanged | < 0.012 | Stable |
| Household interaction | `beta_ll`: 2.617 → 2.619 | 0.0012 (0.05%) | Stable |
| Hours opportunity (`beta_h`) | 3 unchanged | < 0.002 | Stable |
| Hours-opportunity intercept | `beta_E`: −2.499 → −2.914 | 0.415 (16.6%) | Substantial shift |
| Market opportunity — retained | `beta_E_gsur`: −1.329 → −1.048 | 0.281 (21.1%) | Substantial shift |
| Market opportunity — restored | `beta_E_educH` (+0.450) | — | Re-introduced (§6) |
| Market opportunity — region | 7 unchanged | < 0.100 | Mostly stable (§8) |
| Occupation opportunity | 12 unchanged | < 0.002 | Stable |
| Wage opportunity | 6 unchanged | < 0.001 | Stable |

The structural pattern is that the M1-naive intervention is
empirically localised within the market-opportunity block but
within that block produces three coordinated shifts: the
`beta_E_educH` parameter takes a value (+0.450) close to its
M0c_b2_GSURv2 estimate (+0.439), the `beta_E_gsur` parameter
reverts to its M0c_b2_GSURv2 level (−1.048 vs M0c_b2_GSURv2's
−1.050), and the `beta_E` intercept compensates by shifting
downward by 0.415 utility units. The preference, wage, and
occupation blocks are essentially unchanged across the two
specifications.

The findings R5.1 through R5.5 from the M0c_b2_GSURv2 verdict
are preserved in M1-naive as in M1-clean. The household leisure-
leisure interaction `beta_ll` shifts from 2.617 in M1-clean to
2.619 in M1-naive (0.05 per cent relative change); the wage-
offer dispersion `sigma` shifts by less than 0.0001; the Mincer
block is byte-stable; the twelve occupation shifters move by less
than 0.002 each. The preference-block stability across both
specifications confirms that the M1-naive intervention does not
propagate into the welfare-critical parameters outside the
opportunity-block locus of the change.

---

## 5. Log-likelihood and information criteria

The information-theoretic comparison between the two
specifications admits a clear nested-model interpretation. M1-
clean is nested inside M1-naive: the former is obtained from the
latter by restricting `beta_E_educH = 0`. The likelihood-ratio
test is therefore valid.

| Metric | M1-clean | M1-naive | Δ |
|---|---|---|---|
| Joint log-likelihood | −6487.5522 | −6485.5287 | +2.0235 |
| Parameters | 53 | 54 | +1 |
| AIC | 13081.1 | 13079.1 | −2.0 (M1-naive better) |
| BIC | 13662.0 | 13670.9 | +8.9 (M1-naive worse) |
| McFadden $\rho^2$ | 0.70936 | 0.70945 | +0.00009 |
| LR statistic $\chi^2(1) = 2 \cdot \Delta\mathrm{LL}$ | — | — | 4.047 |
| LR test $p$-value | — | — | $\approx 0.044$ |

The LR statistic of 4.047 on one degree of freedom corresponds
to a $p$-value of approximately 0.044, marginally significant at
the 5 per cent threshold. The AIC favours M1-naive by 2.0 units;
the BIC penalises M1-naive by 8.9 units, a mechanical
consequence of the BIC's parameter-count penalty
$\ln(N_{\mathrm{obs}}) \approx \ln(425{,}300) \approx 12.96$
applied to the single added parameter. The McFadden $\rho^2$
improvement of 0.00009 is statistically present but practically
negligible.

The information criteria therefore divide. AIC and the
proportional-likelihood improvement favour M1-naive; BIC
penalises it. Under the conventional interpretation in which BIC
is appropriate for selecting between models intended to identify
a parsimonious data-generating process and AIC is appropriate
for selecting between models intended to maximise predictive
fit, the JMP's structural-modelling purpose aligns more closely
with the BIC framing: the structural model is intended to
identify welfare-relevant parameters rather than to maximise
in-sample fit. The BIC penalty therefore carries more weight in
this context than its absolute magnitude would suggest in a
purely predictive setting.

The LR test's $p \approx 0.044$ result is nominally significant
at the 5 per cent threshold but is not robust to small variation
in the test specification. The Wald test on `beta_E_educH`
itself (§6) yields $p \approx 0.053$, just above the same
threshold. The discrepancy between the LR and Wald $p$-values
reflects the small magnitude of the LR statistic (4.047 is
slightly above the 5 per cent critical value of 3.84 but below
the 1 per cent critical value of 6.63) and is within the normal
range of small-sample disagreement between the two tests. The
combined inferential picture — both routes within 0.01 of the
5 per cent threshold, on opposite sides — is appropriately
characterised as *borderline*: the evidence is consistent with
either rejecting or failing to reject the null hypothesis that
`beta_E_educH = 0`, depending on which test is privileged and
which conventional threshold is applied.

---

## 6. beta_E_educH interpretation

The M1-naive estimate of `beta_E_educH` is +0.4503 with standard
error 0.2323, $t$-statistic 1.938, and two-sided $p$-value
$\approx 0.0526$. The point estimate is closely consistent with
the M0c_b2_GSURv2 estimate of +0.4386 (the value the parameter
took before M1-clean removed it), with a difference of 0.012
utility units that is well within sampling variation.

The parameter is interpretable as the additional employment-
opportunity utility associated with high-education status,
conditional on the demographically conditional within-region
unemployment rate (`beta_E_gsur`), the seven region effects
(`beta_E_drgn2` through `beta_E_drgn8`), and the baseline
employment shifter (`beta_E`). A positive coefficient implies
that high-education individuals face better employment
opportunities than the omitted education categories, even after
absorbing the regional unemployment-rate variation that the
corrected GSUR variable captures.

The Wald $p$-value of $\approx 0.053$ is borderline at the 5 per
cent significance threshold. Under the conventional reporting
convention, the parameter is "not significant at the 5 per cent
level" by the Wald test but is "significant at the 10 per cent
level". Under the corresponding likelihood-ratio test against
M1-clean (§5), the parameter is "significant at the 5 per cent
level". The two routes disagree, and the disagreement is
genuine: the LR and Wald tests are asymptotically equivalent
under the null hypothesis but can differ in finite samples,
particularly when the test statistic is close to the critical
value.

The strict adjudication does not resolve the disagreement by
choosing the more favourable test. Conventional econometric
practice treats joint significance evidence symmetrically:
borderline evidence under multiple tests reflects genuine
inferential uncertainty about whether the parameter is non-zero,
not an opportunity to select the test that produces the desired
conclusion. The verdict therefore treats the `beta_E_educH`
evidence as *borderline*: empirically present, statistically
marginal, and not strong enough by either route to overturn a
precommitted specification on data-driven grounds alone.

The structural interpretation of the borderline evidence is
informed by the supplementary diagnostic D4. The covariance
analysis records that `beta_E_educH` correlates with
`beta_E_gsur` at 0.640 in the recomputed Hessian-based VCV.
This correlation is below the 0.70 collinearity flag threshold
established in the M1-clean diagnostic protocol but is materially
above the correlation magnitudes observed among other
opportunity-block parameter pairs (the highest region-dummy
pairwise correlation in M1-clean was 0.191; the highest in
M1-naive is 0.193). The 0.640 correlation indicates that
`beta_E_educH` and `beta_E_gsur` share a substantial fraction of
their identifying variance: GSUR is education-sex-region-
stratified by construction, and adding `educH` as a separate
shifter partially duplicates the within-region education-related
content of GSUR.

The consequence is that the `beta_E_educH` coefficient should
*not* be interpreted as the identification of a fully
independent education-on-opportunity channel that M1-clean has
wrongly omitted. The coefficient operates predominantly by
reallocating explanatory weight between `beta_E_educH` and
`beta_E_gsur`. The structural evidence of this reallocation is
the `beta_E_gsur` reversion documented in §7: the GSUR
coefficient changes from −1.329 in M1-clean to −1.048 in
M1-naive, almost exactly recovering the M0c_b2_GSURv2 estimate
of −1.050 that obtained before M1-clean removed `beta_E_educH`.
The mechanical equivalence between adding `beta_E_educH` and
weakening `beta_E_gsur` by the same magnitude (in absolute
value) is consistent with the partial collinearity interpretation
and weakens the case that `beta_E_educH` carries information
distinct from what GSUR already conveys.

The supplementary diagnostic also records a secondary
reallocation channel: the `beta_E_educH` ↔ `beta_E_drgn3`
correlation is −0.156, the largest among the region pairs. The
mechanical correlate is the weakening of `beta_E_drgn3` from
0.6564 in M1-clean to 0.5563 in M1-naive, consistent with
`beta_E_educH` absorbing part of the above-average education
composition of the Nord-Pas-de-Calais region. The shift is small
(0.100 utility units), the standard error is unchanged (0.319
vs 0.322), and the joint Wald test on the region block is
preserved (§8). The drgn3 reallocation does not materially
affect the region-block interpretation.

The combined evidence on `beta_E_educH` is therefore: the
parameter is empirically present at the M0c_b2_GSURv2 magnitude,
its statistical significance is borderline by both LR and Wald
tests, and its identifying variation is materially shared with
`beta_E_gsur` and minimally with `beta_E_drgn3`. The coefficient
carries some genuinely distinct information (the eigenvalue
analysis in D3 of the supplementary diagnostics confirms the
9×9 GSUR + educH + region sub-block is locally convex with all
eigenvalues positive) but not enough to constitute the
identification of a fully independent opportunity channel.

---

## 7. beta_E_gsur stability

The `beta_E_gsur` parameter exhibits the largest single-parameter
shift in the M1-clean-to-M1-naive transition. Table 2
reports the comparison across the three relevant specifications.

| Specification | `beta_E_gsur` | SE | $t$-statistic | $p$-value |
|---|---|---|---|---|
| M0c_b2_GSURv2 | −1.0502 | 0.2002 | −5.25 | $1.6 \times 10^{-7}$ |
| M1-clean | −1.3289 | 0.1631 | −8.15 | $4.4 \times 10^{-16}$ |
| M1-naive | −1.0479 | 0.2197 | −4.770 | $1.8 \times 10^{-6}$ |

The M1-clean specification produced a strengthened GSUR
coefficient (−1.329) that the M1-clean verdict §5 interpreted as
the within-region education-sex identification of the
opportunity-block coefficient. The M1-naive specification
produces a reverted GSUR coefficient (−1.048) that essentially
recovers the M0c_b2_GSURv2 value of −1.050 to within 0.002
utility units.

The reversion is empirically informative. Under the
identification framework articulated in the M1-clean design memo
§9, removing `beta_E_educH` (the M1-clean treatment) forces the
GSUR coefficient to absorb the education-on-opportunity signal
that is correlated with the regional unemployment rate. The
0.279-unit strengthening of `beta_E_gsur` in M1-clean from −1.050
to −1.329 was therefore predicted to operate through precisely
this absorption mechanism. The M1-naive estimation provides
direct empirical confirmation: restoring `beta_E_educH` releases
the GSUR coefficient back to its M0c_b2_GSURv2 level, with the
recovered magnitude matching the M0c_b2_GSURv2 estimate to four
significant figures.

The structural confirmation has two implications. First, the
M1-clean GSUR coefficient of −1.329 represents the joint effect
of the within-region unemployment-rate variation *and* the
within-region education-related variation that `beta_E_educH`
would otherwise absorb. The M1-naive GSUR coefficient of −1.048
represents the within-region unemployment-rate variation *net of*
the education-related component. The two coefficients are
estimates of different conditional quantities, not of the same
quantity under different specifications. Second, the empirical
magnitude of the absorption (0.279 utility units) is a
quantitative measure of the education-on-opportunity content
that the corrected GSUR variable carries. This is a direct
empirical answer to a question the M1-clean design memo §9 left
open: whether the within-region GSUR variation is sufficient to
identify the opportunity-block coefficient without an explicit
education shifter.

The M1-naive GSUR coefficient remains highly statistically
significant ($t = -4.77$, $p < 10^{-6}$) despite the reversion.
The structural role of GSUR as a substantive opportunity shifter
is preserved in M1-naive; the reversion concerns the *magnitude*
of the coefficient, not its presence or significance. The
standard error of `beta_E_gsur` widens from 0.163 in M1-clean to
0.220 in M1-naive, a 34 per cent increase consistent with the
partition of identifying variance between two partially
correlated predictors (`beta_E_gsur` and `beta_E_educH`). The
widened standard error is the direct numerical correlate of the
0.640 correlation reported in D4.

The implication for the M1-clean verdict §1 V3 caveat (that the
−1.329 estimate captures the within-region rather than total
GSUR effect) is reinforced by the M1-naive evidence: the within-
region GSUR effect can be decomposed empirically into a pure
within-region unemployment-rate component (−1.048, matching the
M0c_b2_GSURv2 estimate) and a within-region education-related
component (which `beta_E_educH = +0.450` captures, after
accounting for the relative scaling). The decomposition is now
on the project record.

---

## 8. Region-dummy stability

The seven region dummies `beta_E_drgn2` through `beta_E_drgn8`
are stable across the M1-clean-to-M1-naive transition. Table 3
reports the parameter-by-parameter comparison.

| Parameter | M1-clean | M1-clean $p$ | M1-naive | M1-naive $p$ | $\Delta$ |
|---|---|---|---|---|---|
| `beta_E_drgn2` (Bassin Parisien) | 0.801 | 0.0026 | 0.822 | 0.0021 | +0.020 |
| `beta_E_drgn3` (Nord) | 0.656 | 0.0394 | 0.556 | 0.0842 | −0.100 |
| `beta_E_drgn4` (Est) | 1.563 | 0.0001 | 1.542 | 0.0002 | −0.020 |
| `beta_E_drgn5` (Ouest) | 0.773 | 0.0045 | 0.806 | 0.0032 | +0.034 |
| `beta_E_drgn6` (Sud-Ouest) | 0.767 | 0.0192 | 0.778 | 0.0178 | +0.012 |
| `beta_E_drgn7` (Rhône-Alpes/Auvergne) | 0.641 | 0.0399 | 0.659 | 0.0343 | +0.019 |
| `beta_E_drgn8` (Méditerranée) | 0.463 | 0.0974 | 0.438 | 0.1188 | −0.026 |

All seven region dummies shift by less than 0.10 utility units
in absolute value. Six of the seven coefficient shifts are below
0.04 in absolute value; the seventh (`beta_E_drgn3`) shifts by
0.100. The signs are preserved on every dummy. The regional
ordering is preserved: drgn4 > drgn2 ≈ drgn5 ≈ drgn6 > drgn3 ≈
drgn7 > drgn8 in both specifications. No region dummy approaches
its bound of ±10 utility units. The standard errors are
essentially unchanged across the two specifications (maximum SE
change 0.004 across all seven region dummies).

The individual-significance pattern shifts modestly. In M1-clean,
six of seven region dummies were individually significant at the
5 per cent level (only `beta_E_drgn8` failed at $p = 0.097$). In
M1-naive, five of seven are individually significant at the 5 per
cent level: `beta_E_drgn3` (Nord) weakens from $p = 0.039$ to
$p = 0.084$, crossing the threshold. `beta_E_drgn8` (Méditerranée)
remains marginal at $p = 0.119$, slightly weaker than its M1-
clean value of $p = 0.097$.

The drgn3 weakening is mechanically traceable to the
`beta_E_educH` ↔ `beta_E_drgn3` correlation of −0.156 reported
in supplementary diagnostic D4. The North region of France has
above-average educational composition; adding `beta_E_educH` to
the specification produces a partial reallocation of the North
region's opportunity signal from the region dummy to the
education shifter. The reallocation is small (the drgn3 point
estimate shifts by 0.100 utility units, less than half a standard
deviation), but it crosses the 5 per cent significance threshold
in the individual Wald test.

The joint Wald test on the region block is the relevant
inferential statistic, not the individual tests. Supplementary
diagnostic D1 records the joint statistic for both
specifications:

| Specification | Wald $W$ | d.f. | $p$-value |
|---|---|---|---|
| M1-clean | 28.18 | 7 | 0.000204 |
| M1-naive | 28.20 | 7 | 0.000202 |

The joint significance is essentially unchanged across the two
specifications. The region block contributes statistically to
the employment-opportunity index in M1-naive as decisively as in
M1-clean, with the Wald statistic essentially identical between
the two specifications. The individual drgn3 weakening
constitutes a minor realignment, not a structural failure of the
region block.

The substantive interpretation of the region block is preserved
in M1-naive. The Île-de-France region remains the lowest-
opportunity reference category; the seven non-IDF regions retain
their positive coefficients; the regional ordering is unchanged;
the largest coefficient (Est, +1.54) remains the regional outlier.
The conclusion of M1-clean verdict §6 — that residence outside
Île-de-France carries a substantive employment-opportunity
premium relative to IDF — is reinforced by the M1-naive
evidence and does not depend on the inclusion of `beta_E_educH`.

The supplementary diagnostic D2 confirms that no new collinearity
is introduced among the region dummies under M1-naive. The
maximum pairwise correlation in the seven-by-seven region
covariance sub-block is 0.193 (between `beta_E_drgn2` and
`beta_E_drgn5`), essentially unchanged from M1-clean's maximum
of 0.191. The off-diagonal structure of the region block is
preserved with negligible perturbation.

---

## 9. Preference-parameter stability

The preference block is structurally separated from the
market-opportunity block under both M1-clean and M1-naive. The
empirical stability of the preference parameters across the
M1-clean-to-M1-naive transition is correspondingly strong.

The maximum absolute shift across all twenty-three preference
parameters is below 0.006 utility units. Among the parameters
of substantive interest:

The household leisure-leisure interaction `beta_ll` shifts from
2.6175 in M1-clean to 2.6187 in M1-naive (relative change of
0.05 per cent), with $t$-statistic moving from 7.48 to 7.49.
The R5.1 finding from the M0c_b2_GSURv2 verdict (strong leisure
complementarity in French couples) is preserved unchanged in
magnitude, precision, and interpretive significance.

The Box-Cox exponents on leisure (`theta_l_sm`, `theta_l_sf`,
`theta_l_m`, `theta_l_f`) shift by less than 0.001 each. Concave
leisure utility is preserved in all four demographic groups.

The shared singles consumption Box-Cox exponent
`theta_c_singles` shifts from −1.0485 in M1-clean to −1.0518 in
M1-naive (relative change of 0.3 per cent). The fixed couples
consumption Box-Cox exponent ($\theta_c = 0$, log-utility) is
preserved by design.

The leisure intercepts (`beta_l0_sm`, `beta_l0_sf`, `beta_l0_m`,
`beta_l0_f`) shift by less than 0.020 each. The leisure shifters
(`beta_l_age`, `beta_l_age2`, `beta_l_nkids`) shift by less than
0.006 each.

The §22 SA1-STANDS criterion on preference parameter stability
(maximum shift below 5 per cent in absolute value) is met by
every preference parameter at margins exceeding two orders of
magnitude. The structural separation between the market-
opportunity block (where M1-naive intervenes) and the preference
block (where M1-naive does not intervene) is empirically
respected by the estimation result. The M1-naive intervention
does not propagate into the welfare-critical preference
parameters.

---

## 10. Fit stability

The fit profile of M1-naive degrades materially relative to
M1-clean in the singles-male group while exhibiting modest fit
improvements in the other three groups. The net fit picture is
mixed and is the principal empirical cost weighing against the
borderline statistical gain documented in §5 and §6.

*Participation fit.* Table 4 reports the predicted-minus-
observed participation rate by group across the three relevant
specifications.

| Group | M0c_b2_GSURv2 $\Delta$ | M1-clean $\Delta$ | M1-naive $\Delta$ |
|---|---|---|---|
| Singles male (sm) | +0.04 ppt | −0.88 ppt | **−2.92 ppt** |
| Singles female (sf) | +2.39 ppt | +1.94 ppt | +0.87 ppt |
| Couples male (cm) | +1.48 ppt | +1.29 ppt | +0.93 ppt |
| Couples female (cf) | +2.61 ppt | +2.44 ppt | +2.19 ppt |

The singles-male participation fit progressively regresses across
the three specifications. The progression from +0.04 to −0.88 to
−2.92 ppt indicates that each successive opportunity-block
elaboration (corrected GSUR in M0c_b2_GSURv2 → region dummies in
M1-clean → education shifter in M1-naive) adds positive shifts to
the employment-opportunity index that push predicted participation
upward in the singles-male group, where the observed
participation rate (0.9295) is below the other three groups'
observed rates (0.94 to 0.97).

The M1-clean SA1-STANDS criterion specified that fit diagnostics
should not regress by more than one percentage point in any group.
The M1-naive singles-male participation regression of 2.92
percentage points (relative to observed) corresponds to an
absolute worsening of 2.04 ppt relative to M1-clean, exceeding the
SA1 one-percentage-point tolerance by approximately a factor of
two. The other three groups exhibit fit *improvements* in
M1-naive relative to M1-clean (singles female improves by 1.07
ppt; couples male by 0.36 ppt; couples female by 0.25 ppt), but
the singles-male regression is not offset by these improvements
in any composite metric that the SA1 criterion would credit.

*Mean hours fit.* Mean hours fit is essentially unchanged across
the M1-clean-to-M1-naive transition (maximum absolute change
0.02 hours per week across all four groups). The first-moment of
the hours distribution is not materially affected by the
M1-naive intervention.

*Hours-bin distribution fit.* Table 5 reports the L1 distance
between observed and predicted hours-bin distributions by group.

| Group | M0c_b2_GSURv2 L1 | M1-clean L1 | M1-naive L1 | Δ(naive − clean) |
|---|---|---|---|---|
| Singles male | 0.6345 | 0.6945 | **0.7781** | +0.084 |
| Singles female | 0.4220 | 0.4176 | 0.4132 | −0.004 |
| Couples male | 0.3500 | 0.3446 | 0.3329 | −0.012 |
| Couples female | 0.5050 | 0.4998 | 0.4959 | −0.004 |

The singles-male hours-bin L1 worsens by 12.1 per cent relative
to M1-clean (and 22.6 per cent relative to M0c_b2_GSURv2). The
mechanism is the same as in the M1-clean verdict's Q3
qualification, amplified by the added `beta_E_educH` term: the
all-positive opportunity-side shifters push predicted mass into
the 21–30-hour bin for singles male, where the observed
distribution is concentrated in the 31–40-hour bin. The predicted
share in the 21–30-hour bin under M1-naive is 0.619, against an
observed share of 0.257; the predicted share in the 31–40-hour
bin is 0.300, against an observed share of 0.480.

The other three groups exhibit small hours-bin L1 improvements
in M1-naive (changes between −0.012 and −0.004).

*Wage fit.* The wage block parameters are byte-stable across
M1-clean and M1-naive (maximum shift 0.001), and the wage fit is
correspondingly unchanged. The pooled Mincer-style specification
continues to under-predict singles wages by 16 to 22 per cent and
to slightly over-predict couples wages, as documented in the
M1-clean verdict §12. The structural limitations of the wage
block are unaffected by the M1-naive intervention.

*Occupation fit.* The occupation-block parameters are also byte-
stable (maximum shift 0.002), and the occupation fit is
correspondingly unchanged. The couples occupation fit remains
excellent (maximum absolute share error 0.007 across all four
demographic groups); the singles occupation fit remains the
structurally weakest fit diagnostic, with under-prediction of
non-routine cognitive occupations by 0.168 in singles male and
0.199 in singles female.

The composite fit picture is therefore: M1-naive imposes a real
fit cost in the singles-male group (participation regression of
2.04 ppt; hours-bin L1 regression of 12.1 per cent) while
producing modest fit improvements in the other three groups. The
singles-male regression exceeds the M1-clean SA1 one-percentage-
point tolerance by approximately a factor of two for participation
and is the largest hours-bin regression observed in any group-
specification pair across the M0c-to-M1-naive trajectory.

---

## 11. Identification diagnostics

The Hessian topology of M1-naive is essentially identical to that
of M1-clean. Table 6 summarises the comparison.

| Diagnostic | M1-clean | M1-naive | Change |
|---|---|---|---|
| Parameters (free) | 53 | 54 | +1 |
| Bound hits | 0 | 0 | 0 |
| Hessian condition number $\kappa$ | $5.10 \times 10^{10}$ | $5.15 \times 10^{10}$ | +1% |
| Negative eigenvalues | 1 | 1 | unchanged |
| Near-zero eigenvalues | 0 | 0 | unchanged |
| Negative variances (singles consumption block) | 3 | 3 | unchanged |
| Valid standard errors | 50/53 | 51/54 | +1 (the added `beta_E_educH` has valid SE) |

The condition number increase of 1 per cent is negligible. The
single negative eigenvalue remains localised in the singles
consumption joint-identification sub-block, where the same three
parameters (`beta_c_sm`, `beta_c_sf`, `theta_c_singles`) exhibit
near-singular joint behaviour under both M1-clean and M1-naive.
No new negative eigenvalues are introduced by the M1-naive
intervention.

Three parameters exhibit negative-diagonal variance in the
Moore-Penrose pseudoinverse VCV under both specifications; the
specific parameters are the same in both cases. The newly added
`beta_E_educH` parameter exhibits a valid standard error
(0.2323), confirming that the M1-naive intervention does not
extend the singles consumption identification failure into the
opportunity block.

The M1-specific supplementary diagnostics confirm local
identification of the extended opportunity block. The joint Wald
test on the region block (D1, §8 of this verdict) yields $W =
28.20$ with $p = 0.000202$. The seven-by-seven region covariance
sub-block (D2) exhibits a maximum pairwise correlation of 0.193,
below the 0.70 collinearity flag threshold. The nine-by-nine
GSUR + educH + region Hessian sub-block (D3) has all nine
eigenvalues positive, with minimum eigenvalue 5.559 and maximum
eigenvalue 286.3, yielding a sub-block condition number of 51.5.
The sub-block is locally strictly convex at the M1-naive
solution; the extended opportunity block is well-identified.

The supplementary diagnostic D4 records the cross-correlations
between `beta_E_educH` and the other opportunity-block
parameters. The `beta_E_educH` ↔ `beta_E_gsur` correlation is
0.640, below the 0.70 flag threshold but materially above the
correlations elsewhere in the block. The next-largest cross-
correlation is `beta_E_educH` ↔ `beta_E_drgn3` at −0.156. The
remaining six `beta_E_educH` ↔ region correlations are below
0.07 in absolute value. The covariance structure confirms the
interpretation in §6 and §7: `beta_E_educH` reallocates
explanatory weight primarily from `beta_E_gsur` and secondarily
from `beta_E_drgn3`, with no other parameter materially affected.

No new identification failure is introduced by the M1-naive
intervention. The borderline statistical significance of
`beta_E_educH` is not a consequence of identification failure
(the parameter has a valid standard error and the Hessian sub-
block containing it is well-conditioned); it is a consequence of
small-sample inferential uncertainty combined with the partial
overlap of identifying variance with `beta_E_gsur`.

---

## 12. Whether M1-naive challenges M1-clean

The strict adjudication of whether M1-naive constitutes a
substantive challenge to M1-clean as the preferred specification
requires weighing four distinct considerations.

*Consideration 1 — Statistical evidence.* The LR test against
M1-clean yields $\chi^2(1) = 4.047$ with $p \approx 0.044$,
nominally significant at 5 per cent. The Wald test on
`beta_E_educH` yields $t = 1.938$ with $p \approx 0.053$, not
significant at 5 per cent. The two routes straddle the
threshold; neither route delivers decisive evidence at the
significance level conventionally required to overturn a
precommitted specification. The combined statistical evidence is
*borderline*: empirically consistent with both rejection and
non-rejection of the null hypothesis $\beta_{E_{\mathrm{educH}}}
= 0$, depending on test choice and threshold.

*Consideration 2 — Fit costs.* The M1-naive specification
inflicts three measurable fit costs against the 2.02-unit log-
likelihood gain. The Bayesian information criterion penalises
M1-naive by 8.9 units (a mechanical penalty for the single added
parameter, with $\ln(N_{\mathrm{obs}}) \approx 12.96$). The
singles-male participation fit regresses from −0.88 ppt to
−2.92 ppt, a 2.04 ppt absolute worsening that exceeds the
M1-clean SA1 one-percentage-point tolerance by approximately a
factor of two. The singles-male hours-bin L1 distance worsens by
12.1 per cent (from 0.6945 to 0.7781), continuing and amplifying
the regression pattern documented in the M1-clean Q3
qualification. Together, the three costs constitute a non-
trivial fit deterioration that is not offset by the modest fit
improvements in the other three demographic groups.

*Consideration 3 — Structural reallocation evidence.* The
supplementary diagnostic D4 establishes that `beta_E_educH`
operates predominantly through reallocation of explanatory
weight rather than through the identification of a fully
independent opportunity channel. The 0.640 correlation between
`beta_E_educH` and `beta_E_gsur` in the recomputed VCV is below
the 0.70 collinearity flag but is materially elevated relative
to the rest of the opportunity block. The corresponding
mechanical response — `beta_E_gsur` reverting from −1.329 in
M1-clean to −1.048 in M1-naive, recovering the M0c_b2_GSURv2
value of −1.050 — confirms that the bulk of `beta_E_educH`'s
estimated content is shared with GSUR rather than orthogonal to
it. The M1-naive specification therefore does not identify a new
opportunity signal hitherto omitted from M1-clean; it
redistributes the within-region education-related component of
the GSUR effect into a separate education parameter while
preserving the total GSUR-plus-educH effect approximately
constant.

*Consideration 4 — Conceptual partition.* The JMP's welfare-
relevant ability/opportunity partition classifies education as
an ability dimension whose effect on welfare operates through the
wage process, not through the employment-opportunity index. The
partition is articulated in the framework memo and operationalised
in the M1-clean specification. The M1-naive specification suspends
the partition as a robustness exercise, but the suspension is
conceptually inconsistent with the JMP's welfare framework and
would yield a welfare decomposition with the same conceptual
ambiguity that the M1-clean design memo §2 identified as
untenable: education would simultaneously enter the wage block
(correctly, as an ability dimension) and the opportunity block
(problematically, as if it were a circumstance). This conceptual
inconsistency is not adjudicated by empirical evidence; it
follows from the welfare partition the JMP commits to.

The four considerations together favour M1-clean over M1-naive.
The borderline statistical evidence (Consideration 1) is
insufficient to overturn a precommitted specification on data-
driven grounds alone. The fit costs (Consideration 2) are
substantial and disproportionate to the log-likelihood gain. The
structural reallocation evidence (Consideration 3) demonstrates
that M1-naive's apparent improvement is largely a redistribution
of identifying variance rather than the identification of a new
opportunity channel. The conceptual partition (Consideration 4)
governs the JMP's substantive contribution and cannot be
overridden by marginal empirical fluctuations.

M1-naive does not challenge M1-clean in any decisive sense. The
two specifications produce statistically similar log-likelihood
values, but the structural interpretation, the fit costs, and
the conceptual classification all point in M1-clean's favour.
M1-naive functions as designed: as a sensitivity exposure
quantifying the empirical consequences of suspending the welfare
partition, not as a candidate primary specification.

---

## 13. Whether M1-clean remains preferred

**Yes. `ruro_occ_M1_clean` remains the JMP's preferred structural
baseline.**

The conclusion follows from the §12 adjudication. The four
considerations articulated there — borderline statistical
evidence, substantial fit costs, structural reallocation,
conceptual partition — collectively support the retention of
M1-clean as the working specification. The M1-naive specification
does not earn a SA1-style verdict and does not become the
preferred specification at any point in this verdict's analysis.

The retention of M1-clean as the preferred specification is
preserved subject only to the prospective replacement of the
single-year M1-clean baseline by a pooled multi-year specification
under the SA2-style verdict process articulated in the v3.1
multi-year strategy memo §11. The v3.1 memo §10 records the
default position that the M1-clean single-year SA1-STANDS verdict
governs until a pooled specification earns its own SA2 verdict.
The M1-naive robustness verdict reaffirms this default: M1-clean
remains primary; the pooled-specification path is the only route
through which the primary baseline may be replaced; and pooled
estimation has not yet been initiated, far less verdict-
adjudicated.

The robustness exposure R2 in the framework memo (M1-clean vs
M1-naive, ability-versus-opportunity partition) is now
operationally complete on the structural side. The empirical
finding is that the M1-clean specification's removal of
`beta_E_educH` produces a marginal log-likelihood loss
($\Delta\mathrm{LL} = -2.02$, $p \approx 0.044$) but secures a
substantive welfare-partition gain and avoids the fit costs of
the unrestricted specification. The robustness section of the
JMP will report this finding as evidence that the central
welfare results are not driven by the partition decision in any
quantitatively dramatic way: the structural parameters of
substantive interest (preferences, wages, occupations, region
dummies) are stable across the two specifications, and the
welfare decomposition computed under either specification will
likely yield similar substantive conclusions, modulo the
education-on-opportunity channel that the partition disagreement
captures.

The welfare-side complement of the R2 robustness exposure — the
comparison of welfare decompositions computed under M1-clean and
M1-naive estimates — remains a deferred deliverable. It will be
computed when welfare scaffolding is implemented, against the
JMP's primary baseline (M1-clean or pooled, whichever is
operative at that stage) and as a robustness exposure against
the secondary baseline (M1-naive, computed for documentation only).

---

## 14. Implications for ability versus opportunity interpretation

The M1-naive evidence does *not* change the preferred
ability/opportunity partition. The JMP's classification of
education as an ability dimension entering welfare through the
wage channel rather than through the opportunity index is a
normative decision grounded in the framework memo's articulation
of the weak Dworkinian welfare criterion. The decision is
informed by the empirical evidence but is not determined by it.

If the M1-naive Wald test had returned a $p$-value below 0.01
and the M1-naive specification had simultaneously improved the
fit across all four demographic groups, the conceptual case for
treating education as opportunity rather than ability would
remain unchanged: a positive `beta_E_educH` coefficient under
the unrestricted specification is consistent with at least three
underlying mechanisms — (a) genuine education-on-opportunity
discrimination by employers, (b) education-correlated unmodelled
ability or productivity differentials that the GSUR variable
fails to absorb, or (c) education-correlated regional and
sectoral employment composition. Of these three mechanisms, only
the first would unambiguously support reclassifying education
as a compensation-relevant circumstance. The framework memo's
welfare partition does not commit to any one of the three
mechanisms but reflects the broader judgement that, under the
weak Dworkinian criterion, education attainment is treated as
ability irrespective of which of (a) through (c) operates.

The M1-naive evidence is therefore informative about whether
`beta_E_educH` is non-zero in the unrestricted specification
(borderline) but is not informative about whether education
should be classified as ability or opportunity in the JMP's
welfare partition (a normative decision). The two questions are
distinct, and the strict adjudication of the M1-naive evidence
respects the distinction.

The empirical evidence does, however, inform the JMP's
robustness section. The R2 exposure quantifies the consequences
of the partition decision for the structural estimates: the
preference, wage, occupation, hours, and region-dummy
parameters are stable across the two specifications; the
substantive shifts are localised in the market-opportunity
intercept (`beta_E`), the within-region GSUR coefficient
(`beta_E_gsur`), and the re-introduced `beta_E_educH`. The
welfare decomposition under M1-naive will inherit these
structural shifts and will likely yield a similar substantive
decomposition with a quantitatively shifted partition of
welfare-relevant inequality between the opportunity-side and
preference-side components. The shift magnitude will be reported
when welfare scaffolding is implemented; the direction is
predictable from the structural-parameter shifts and will not
fundamentally alter the JMP's welfare conclusions.

The M1-naive evidence's classification of education is therefore
borderline empirically and unambiguous conceptually: the JMP's
welfare partition treats education as ability, and the M1-clean
specification is the structural realisation of this partition.

---

## 15. Whether welfare-measurement decisions work may proceed

**Yes for the welfare-measurement decisions memo. No for welfare
scaffolding implementation. No for welfare-decomposition
computation.**

The verdict distinguishes three distinct welfare-track activities,
each with its own gating criterion.

*The welfare-measurement decisions memo* (yet unwritten;
prospective filename `docs/JMP_welfare_measurement_decisions_memo_v1.md`)
specifies the methodological choices for the welfare-
decomposition: the welfare functional (Fleurbaey-style equivalent
income, equivalent variation, compensating variation, or
alternative), the inequality index (Gini, Atkinson with specified
inequality-aversion parameter, generalised entropy, or
alternative), the counterfactual decomposition method (ordered
removal, Shapley, or both), the reference distributions for
ability and opportunity, the gender attribution rule (A1, A2,
A3, or a documented alternative), and the operational handling of
the singles consumption joint-identification limitation. These
methodological choices are *independent* of whether the
structural baseline is M1-clean (currently preferred) or a future
pooled-specification (to be earned through SA2). The decisions
memo may therefore proceed in parallel with the multi-year track
without methodological conflict.

The decisions memo is also independent of the M1-naive evidence
in this verdict: the methodological choices apply equivalently
to the M1-clean estimates that constitute the JMP's preferred
baseline and to the M1-naive estimates that constitute the R2
robustness exposure. The decisions memo may articulate how the
welfare decomposition will be reported under both specifications
when welfare scaffolding is implemented.

*Welfare scaffolding implementation* is the computational
construction of the welfare functional, the inequality index, the
reference distributions, and the decomposition procedure. The
implementation operates on the structural estimates from the JMP's
preferred baseline (currently M1-clean; potentially a future
pooled specification). The implementation requires the welfare-
measurement decisions memo as its prerequisite and is *not*
authorised by this verdict. The scaffolding will be implemented
after the decisions memo is complete and after the multi-year
feasibility audit has been performed (the audit's findings may
inform the sequencing of scaffolding implementation against
M1-clean versus a future pooled specification).

*Welfare-decomposition computation* is the actual numerical
production of the JMP's welfare results: the opportunity-driven
and preference-driven components of money-metric inequality, the
counterfactual distributions, the robustness exposures (R1
through R9). The computation requires the welfare scaffolding to
be implemented, the structural baseline to be locked, and the
welfare-measurement decisions to be settled. The computation is
*not* authorised by this verdict. It will be authorised when the
prerequisite work is complete and the JMP's primary baseline has
been definitively established (either M1-clean as the current
preferred baseline, or a pooled specification under a future
SA2-STANDS verdict).

The sequencing implication is that the welfare-measurement
decisions memo is the immediate parallel chat task that may
proceed alongside the multi-year feasibility audit, while
welfare scaffolding implementation and welfare-decomposition
computation remain deferred to a later operational stage.

---

## 16. What not to claim yet

The following claims are not supported by the current evidence
and must not appear in JMP text, supervisor memos, or
presentations until the relevant prerequisites are in place.

(N1) *"M1-naive overturns M1-clean as the preferred
specification."* Not supported. The §12 strict adjudication
shows that the borderline statistical evidence is insufficient
to overturn the precommitted specification, the fit costs are
substantial, the structural shift is largely a reallocation
rather than a new identification, and the conceptual partition
governs the welfare classification irrespective of marginal
empirical fluctuations.

(N2) *"The borderline `beta_E_educH` significance proves that
education belongs in the opportunity block."* Not supported. §14
articulates the distinction between the empirical question
(whether `beta_E_educH` is non-zero in the unrestricted
specification) and the normative question (whether education
should be classified as ability or opportunity in the JMP's
welfare partition). The two questions are distinct; the
empirical evidence cannot determine the normative classification
because the welfare partition is informed by considerations
beyond the data.

(N3) *"The `beta_E_gsur` reversion in M1-naive shows that the
M1-clean GSUR coefficient was wrong."* Not supported. The
M1-clean and M1-naive GSUR coefficients are estimates of
different conditional quantities (within-region unemployment
effect under different conditioning sets), not of the same
quantity under different specifications. The reversion is a
structural consequence of the partition of variance between
correlated predictors, not evidence that one estimate is
"correct" and the other "wrong" in a substantive sense.

(N4) *"M1-naive identifies a distinct education-on-opportunity
channel that M1-clean omitted."* Not supported as stated. The
supplementary diagnostic D4 establishes that `beta_E_educH`
operates predominantly through reallocation from `beta_E_gsur`
(correlation 0.640), with secondary reallocation from
`beta_E_drgn3` (correlation −0.156). The coefficient carries
some genuinely distinct information (the 9×9 sub-block is
locally convex), but the dominant mechanism is reallocation, not
new identification.

(N5) *"The welfare results are robust to the ability-versus-
opportunity partition."* Not supported until welfare scaffolding
is implemented and the welfare decomposition is computed under
both M1-clean and M1-naive estimates. The structural-side
robustness (parameter stability) is established by this verdict;
the welfare-side robustness (decomposition stability) requires
the welfare computation, which is not authorised here.

(N6) *"Canonical MNL promotion is approved."* Not supported. The
versioned GSURv2 MNL parquets remain the operative data source.
The O10 promotion decision is separately gated and is not
granted by this verdict.

(N7) *"The single-year M1-clean baseline is the JMP's permanent
preferred specification."* Not supported as stated. M1-clean is
the current preferred specification subject to the prospective
replacement by a pooled multi-year specification under the v3.1
multi-year strategy memo's SA2 verdict pathway. The replacement
is not assured; it is the only route through which the primary
baseline may change.

(N8) *"Welfare scaffolding implementation is authorised."* Not
supported. The §15 distinction places welfare scaffolding behind
two prerequisites: the welfare-measurement decisions memo and
the establishment of the primary structural baseline (which
remains M1-clean pending the prospective pooled-specification
path).

(N9) *"M0/M1 model repair is required given the M1-naive
findings."* Not supported. The §11 identification diagnostics
confirm that the Hessian topology of M1-naive is essentially
identical to that of M1-clean; no new identification failure is
introduced. The borderline statistical significance of
`beta_E_educH` is a small-sample inferential phenomenon
combined with the partial overlap of identifying variance with
`beta_E_gsur`, not an identification failure of either M1-clean
or M1-naive. The M0c/M1 model specifications do not require
repair on the basis of the M1-naive evidence.

(N10) *"Age-specific GSUR (Stage B) is authorised."* Not
supported. Stage B remains deferred per the GSUR rebuild
specification §16 O6. The M1-naive evidence does not motivate
re-opening the Stage B question.

---

## 17. Immediate next task

**The immediate next task is the multi-year feasibility audit,
to be executed in Claude Code Sonnet per the v3.1 multi-year
strategy memo §13 Step 4.**

Tool path: Claude Code Sonnet (local codebase, data inspection
and feasibility verification), not Claude Project chat.

The feasibility audit is the operational initiator of the
multi-year track. Under the v3.1 strategy memo §4, the audit
covers six conditions: EUROMOD FR_2015 and FR_2017 system
installation (F1), EU-SILC microdata availability (F2), Eurostat
GSUR sources for 2015 and 2017 (F3), INSEE national-rate
benchmark for 2015 and 2017 (F4), INSEE CPI series for 2015,
2016, and 2017 (F5), and EUROMOD output variable comparability
across the three years (F6). The audit also records the maximum
identifier magnitudes required by the §6 numerical encoding
scheme (the operational default base $B = 10^{11}$ established
in v3.1 §6 Element I3) and confirms the canonical clustering key
(`idhh_raw` or `idorighh_raw`) per §6 Element I6.

The audit produces a feasibility report
(`Results/JMP_multi_year_feasibility_audit_v1.md` or equivalent)
that records the status of each condition and authorises the
subsequent pipeline implementation steps. The audit is
methodologically independent of the welfare-measurement decisions
memo and the M1-naive verdict; it can be executed at any point
after this verdict is complete.

The recommended parallel chat task is the *welfare-measurement
decisions memo*
(`docs/JMP_welfare_measurement_decisions_memo_v1.md`), which can
be drafted in this chat while the multi-year feasibility audit
proceeds in Claude Code Sonnet. The two tasks are operationally
independent and methodologically complementary: the audit
prepares the empirical infrastructure for any future pooled-
specification work, while the decisions memo articulates the
methodological choices for the welfare computation that will
operate on whichever structural baseline is operative at the
welfare-scaffolding stage.

Items explicitly not authorised by this verdict:

- Welfare-decomposition computation in any form.
- Welfare scaffolding implementation in any form (decisions memo
  may proceed; computation must wait).
- Canonical MNL promotion of any data product (the O10
  decision).
- Stage B age-specific GSUR work (the O6 decision).
- Modification of the M1-clean specification, the M1-naive
  specification, or any frozen blocks therein.
- Pooled multi-year estimation in any configuration (P1, P2, or
  P3): the implementation requires the feasibility audit, the
  CPI harmonisation utility, the ID stacking utility, and the
  GSURv2 lookups for 2015 and 2017 to be in place. The audit
  produces these prerequisites in due sequence; pooled estimation
  is sequenced after the audit completes successfully and the
  pipeline implementation stages M1, M2, M3 of v3.1 §13 are
  executed.
- The François Maniquet pure-theory paper. This memo's empirical
  work is intellectually adjacent to but operationally distinct
  from the theory paper. The JMP must remain a distinct empirical
  contribution.
