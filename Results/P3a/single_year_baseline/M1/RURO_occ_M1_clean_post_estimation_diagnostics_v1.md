# RURO occ M1-clean Post-Estimation Diagnostics v1

Date: 2026-05-18  
Specification: `ruro_occ_M1_clean` (53 parameters)  
Comparison baseline: `ruro_occ_M0c_b2_GSURv2` (47 parameters)

Primary sources:
- `Results/RURO_occ_M1_clean_standard_post_estimation_diagnostics_v1.md`
- `Results/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`

Comparison sources:
- `Results/RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md`
- `Results/RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md`
- `docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md`

---

## 1. Purpose

This report consolidates all post-estimation evidence for `ruro_occ_M1_clean`
into a single document suitable for the M1-clean verdict. It draws on the
standard post-estimation report (fit, parameter, and Hessian diagnostics from
`RURO_post_estimation_styled.py`) and the M1-specific supplementary diagnostics
report (joint Wald test, region VCV block, GSUR+region Hessian sub-block from
`scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`).

**Scope**: consolidation and classification of evidence only. This report does
not make the final keep/pool/revise verdict, does not authorise welfare
computation, and does not run or recommend any new estimation. M1-naive is
noted only where it bears on the interpretation of specific findings; the
decision to estimate M1-naive is a verdict-level question, not a diagnostic
finding.

---

## 2. Data and selected run

**Estimation run selected**: `run_2026-05-18_11-33-46` (Start 1, warm from
M0c_b2_GSURv2). Selected on fewest solver iterations (12) and fastest
walltime (320.9 s). All three M1-clean starts converge to an identical
parameter vector and LL = −6487.5522 (verified by comparing
`estimation_results.json` parameter dictionaries across runs).

**MNL base**: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`

| Dataset | Rows | Columns |
|---|---|---|
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | 167,600 | 81 |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | 257,700 | 105 |

Sidecar `fr_2016_RURO_mnl_GSURv2__mnlmeta.json`: **present** (confirmed before
post-estimation run; no sidecar-related errors in any run).

**Post-estimation run folder**:
`outputs/post_estimation/fr/spec/ruro_occ_M1_clean/gamspy/estimation_spec_ruro_occ_M1_clean/run_2026-05-18_12-56-41/`
26 output files written. Script exited without errors.

**Supplementary diagnostics run**: `scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`
at eps = 1e-5 on the same parameter vector. Full 53×53 Hessian recomputed via
central-difference finite differences. Outputs: `Results/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`,
`Results/RURO_occ_M1_clean_vcv_region_block_20260518_125924.csv`,
`Results/RURO_occ_M1_clean_hessian_region_block_20260518_125924.csv`.

---

## 3. Standard fit diagnostics

**Log-likelihood and information criteria**

| Metric | M0c_b2_GSURv2 | M1-clean | Change |
|---|---|---|---|
| Joint LL | −6501.2082 | −6487.5522 | +13.656 |
| AIC | 13096.4 | 13081.1 | −15.3 (M1-clean better) |
| BIC | 13611.6 | 13662.0 | +50.4 (M1-clean penalised) |
| McFadden ρ² | 0.70875 | 0.70936 | +0.00061 |
| Parameters | 47 | 53 | +6 net |

ΔLL = +13.656 is descriptive evidence of improved fit. A formal LR test is not
valid — M1-clean simultaneously removes `beta_E_educH` and adds
`beta_E_drgn2`–`beta_E_drgn8`, making the two models non-nested. AIC favours
M1-clean; BIC penalises the six net additional parameters. The formal joint-
significance test for the new region block is D1 in §9.

**Parameter significance summary (M1-clean, 50 estimable parameters)**

| Block | n | p < 0.001 | p < 0.01 | p < 0.05 | p ≥ 0.05 |
|---|---|---|---|---|---|
| Preference | 23 | 9 | 10 | 10 | 13 |
| Employment/hours opportunity | 4 | 4 | 4 | 4 | 0 |
| Market residual opportunity | 8 | 2 | 4 | 7 | 1 |
| Wage opportunity | 6 | 5 | 5 | 5 | 1 |
| Occupation opportunity | 12 | 8 | 8 | 9 | 3 |
| **Total (estimable)** | **50** | — | — | **35** | **15** |

35 of 50 estimable parameters significant at 5% (66%). Three additional
parameters have NA SEs (singles consumption block; see §7). The sole non-
significant parameter in the market opportunity block is `beta_E_drgn8`
(Mediterranean; p = 0.097), which is the weakest of the seven region dummies
but is retained under the joint test result.

---

## 4. Participation and hours fit

### Participation fit

| Group | Observed | M1-clean pred | M1-clean Δ | M0c_b2_GSURv2 Δ | Change |
|---|---|---|---|---|---|
| Singles male (sm) | 0.9295 | 0.9207 | **−0.88 ppt** | +0.04 ppt | reverses sign |
| Singles female (sf) | 0.9396 | 0.9590 | +1.94 ppt | +2.39 ppt | improved |
| Couples male (cm) | 0.9717 | 0.9845 | +1.29 ppt | +1.48 ppt | improved |
| Couples female (cf) | 0.9651 | 0.9896 | +2.44 ppt | +2.61 ppt | improved |

The sm participation fit reverses sign: M0c_b2_GSURv2 overpredicted by +0.04
ppt; M1-clean underpredicts by −0.88 ppt. The region shifters — all positive —
increase the employment-opportunity index for non-IDF households, which raises
predicted participation enough to produce a slight aggregate underprediction
relative to the IDF-weighted observed rate. The absolute gap (0.88 ppt) is
small but is a structural reversal.

For sf, cm, and cf, participation fit improves modestly (by 0.17–0.45 ppt)
relative to M0c_b2_GSURv2. The cf participation overprediction (0.9896 vs
observed 0.9651) remains the largest unresolved structural gap in the model;
it is an unchanged limitation from M0c_b2_GSURv2 (previously 0.9911 vs 0.9651)
reflecting the model's structural difficulty generating non-employment in
couples without fixed costs of work.

### Mean hours fit

| Group | Observed | M1-clean pred | M1-clean Δ | M0c_b2_GSURv2 Δ | Change |
|---|---|---|---|---|---|
| Singles male (sm) | 39.30 h | 35.75 h | −3.55 h | −3.58 h | negligible |
| Singles female (sf) | 36.30 h | 35.09 h | −1.20 h | −1.22 h | negligible |
| Couples male (cm) | 41.61 h | 42.72 h | +1.11 h | +1.15 h | negligible |
| Couples female (cf) | 35.65 h | 38.91 h | +3.26 h | +3.30 h | negligible |

Mean-hours fit is essentially unchanged from M0c_b2_GSURv2 across all four
groups (maximum change 0.04 h). The region dummies do not materially alter
the hours-distribution first moment.

### Hours-bin fit (L1 and L2 distance)

| Group | M1-clean L1 | M0c_b2_GSURv2 L1 | Δ L1 | Direction |
|---|---|---|---|---|
| Singles male | **0.6945** | **0.6345** | **+0.060** | **M1-clean worse (+9.6%)** |
| Singles female | 0.4176 | 0.4220 | −0.005 | ≈same |
| Couples male | 0.3446 | 0.3500 | −0.005 | negligible improvement |
| Couples female | 0.4998 | 0.5050 | −0.005 | negligible improvement |

The hours-bin L1 distance for singles male worsens by +9.6% (L2: +10.5%)
relative to M0c_b2_GSURv2. The cause is mechanical: all seven region dummy
estimates are positive, increasing the employment-opportunity index for working
in non-IDF regions. This shifts more singles-male mass into the 21–30 h bin
(M1-clean 0.590 vs M0c_b2_GSURv2 0.561, against observed 0.257). The 21–30 h
bin was already over-concentrated in M0c_b2_GSURv2; M1-clean amplifies this.

This is a fit tradeoff: the region dummies improve the welfare-partition
structure of the model but worsen the hours-distribution shape for singles male.
No group other than singles male shows a material change.

---

## 5. Wage and occupation fit

### Wage fit

| Group | Obs mean €/h | M1-clean pred €/h | Δ % | Obs σ(log w) | Pred σ |
|---|---|---|---|---|---|
| Singles male | 16.21 | 12.59 | −22% | 0.4502 | 0.4275 |
| Singles female | 15.11 | 12.73 | −16% | 0.4360 | 0.4275 |
| Couples male | 17.66 | 17.11 | −3% | 0.4402 | 0.4275 |
| Couples female | 15.17 | 15.93 | +5% | 0.4360 | 0.4275 |

Wage fit is **unchanged from M0c_b2_GSURv2** in all dimensions. The Mincer
block (`beta_w0`, `beta_w_educL`, `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`)
and `sigma` shift by ≤ 0.001 in absolute value. The singles wage underprediction
(~22%) and couples-female slight overprediction are pre-existing structural
limitations of the pooled Mincer specification, not introduced by M1-clean.
Quantile fit: couples q10/q50/q90 within 8%; singles systematically
underpredict at all quantiles (inherited limitation). Implied `sigma` = 0.4275
vs observed σ(log w) of 0.436–0.450 — a 2–3% dispersion gap, unchanged.

### Occupation fit

| Group | Max |Δ| observed | Status | vs M0c_b2_GSURv2 |
|---|---|---|---|
| Singles male | 0.168 | Poor | Unchanged |
| Singles female | 0.199 | Poor | Unchanged |
| Couples male | 0.004 | Excellent | Unchanged |
| Couples female | 0.007 | Excellent | Unchanged |

Occupation fit is **unchanged from M0c_b2_GSURv2**. Couples shares are
excellent (max |Δ| ≤ 0.007). Singles shares remain poor: the model
over-predicts routine cognitive (cat 3) for sm by 15.8 ppt and under-predicts
nonroutine cognitive (cat 4) for sf by 19.9 ppt. These limitations are
inherited from M0c_b2_GSURv2 and reflect the absence of group-specific
occupation opportunity shifters for singles at this model tier (all
group-specific occupation coefficients `beta_occ_{2,3,4}_{sm,sf}` are
present but insufficient to recover the full marginal occupational
self-selection).

---

## 6. Probability diagnostics

### Chosen probability distribution

| Metric | M1-clean | M0c_b2_GSURv2 |
|---|---|---|
| p_chosen_min | 1.161×10⁻⁹ | 1.09×10⁻⁹ |
| p_chosen_q10 | 0.01528 | 0.0150 |
| p_chosen_q25 | 0.06649 | 0.0671 |
| p_chosen_mean | 0.38982 | 0.3902 |
| p_chosen_median | 0.27221 | 0.2730 |
| p_chosen_q75 | 0.72569 | 0.7267 |
| p_chosen_q90 | 0.92252 | 0.9228 |
| p_chosen_max | 0.99934 | 0.9993 |

The chosen-probability distribution is essentially identical to M0c_b2_GSURv2
across the full range of quantiles. Probability normalisation errors at machine
precision (max = 7.77×10⁻¹⁶, mean = 1.31×10⁻¹⁶), confirming correct
normalisation across all 4,253 choice sets.

One flag: `very_small_p_chosen_min` (1.161×10⁻⁹ < 1×10⁻⁸ threshold). Same
household as M0c_b2_GSURv2 (idhh = 4012700, singles male group). Not newly
introduced by M1-clean.

### Non-work probability

| Group | Obs non-work | Pred non-work | Δ |
|---|---|---|---|
| Singles male | 0.0705 | 0.0793 | +0.88 ppt |
| Singles female | 0.0604 | 0.0410 | −1.94 ppt |
| Couples male | 0.0283 | 0.0155 | −1.28 ppt |
| Couples female | 0.0349 | 0.0104 | −2.44 ppt |

Non-work probabilities are the mirror of participation fit. Couples-female
non-work predicted at 1.04% vs observed 3.49% (factor ~3.4× underprediction).
Unchanged structural limitation from M0c_b2_GSURv2.

### Worst-fit households

The same 10 households appear at the top of the worst-fit list in both M1-clean
and M0c_b2_GSURv2 (same `idhh`, same groups). The region shifters do not
alter which households are hardest to fit.

### Marginal utilities

All positive and well-behaved across all 4,253 households (0 negative MUC,
0 negative MUL for all four groups). Unchanged from M0c_b2_GSURv2.

---

## 7. Hessian and standard-error diagnostics

### Full-model Hessian

| Metric | M1-clean | M0c_b2_GSURv2 | Change |
|---|---|---|---|
| Condition number κ | 5.096×10¹⁰ | 5.138×10¹⁰ | −0.8% |
| Classification | Ill-conditioned (κ ≥ 10¹⁰) | Ill-conditioned | unchanged |
| Negative eigenvalues | 1 | 1 | unchanged |
| Near-zero eigenvalues | 0 | 0 | unchanged |
| Bound hits | 0 / 53 | 0 / 47 | unchanged |
| Valid SEs | 50 / 53 | 44 / 47 | same fraction |
| NA SEs | 3 / 53 | 3 / 47 | same three parameters |

The global Hessian topology is essentially unchanged. The condition number
decreases by 0.8% (not meaningful). The single negative eigenvalue is localised
in the singles consumption block (`beta_c_sm` / `beta_c_sf` / `theta_c_singles`)
as in M0c_b2_GSURv2. The minimum eigenvalue is more negative in M1-clean
(−35.60 vs −15.01 in M0c_b2_GSURv2), consistent with the addition of seven
parameters that interact with the existing collinear block through the shared
opportunity index. CONOPT reaches `NormalCompletion / OptimalLocal` regardless.

### NA standard errors

The three parameters with NA SEs are identical to M0c_b2_GSURv2:

| Parameter | Estimate | SE | Cause |
|---|---|---|---|
| `beta_c_sm` | 0.553672 | NA | Singles consumption joint-identification ridge |
| `beta_c_sf` | 0.505586 | NA | Singles consumption joint-identification ridge |
| `theta_c_singles` | −1.048483 | NA | Singles consumption joint-identification ridge |

The pseudoinverse produces negative diagonal entries for these three, reported
as NA. This is a data limitation (insufficient singles consumption variation to
separately identify two scale parameters and their shared exponent), inherited
from M0c_b2_GSURv2, and unaffected by M1-clean's changes to the
market-opportunity block. All seven new region parameters have valid SEs.

Top cross-parameter correlations (pseudoinverse artefacts in the collinear
block, values > 1 are expected):

| Pair | Correlation |
|---|---|
| `beta_c_sm` ↔ `beta_c_sf` | −1.108 |
| `beta_c_sf` ↔ `theta_c_singles` | −1.086 |
| `beta_c_sm` ↔ `theta_c_singles` | −1.067 |
| `beta_w_pexp` ↔ `beta_w_pexp2` | −0.960 |

All pairs outside the collinear block have correlations within [−1, +1].

### Parameters near bounds

No parameters at strict bounds. Four parameters near lower bounds (within 5%
of bound width): `beta_c_sm` (0.554 vs lb = 0.05), `beta_c_sf` (0.506 vs
lb = 0.05), `beta_l0_m` (0.012 vs lb = 1×10⁻⁶), `sigma` (0.428 vs lb = 0.10).
Same four parameters as M0c_b2_GSURv2. No region parameters are near any bound.

---

## 8. M1-specific region diagnostics — overview

Three diagnostics specific to the region block were computed by
`scripts/diagnostics/RURO_post_estimation_M1_diagnostics.py`. The full 53×53
Hessian was recomputed via central-difference finite differences
(eps = 1×10⁻⁵) on the joint gradient, using the same parameter vector and data
as the estimation run. VCV computed as Moore-Penrose pseudo-inverse
(rcond = 1×10⁻¹⁰), consistent with the SE computation method.

Full-Hessian condition number (recomputed): 5.0957×10¹⁰ — consistent with
the estimation-time value (5.096×10¹⁰), confirming the recomputation is
accurate.

---

## 9. Joint region-dummy test

**Wald test: H₀: β_E_drgn2 = β_E_drgn3 = … = β_E_drgn8 = 0**

Uses the 7×7 sub-block of the recomputed VCV. The LR test is not available
because M1-clean and M0c_b2_GSURv2 are non-nested.

| Statistic | Value |
|---|---|
| W (Wald statistic) | 28.18 |
| Degrees of freedom | 7 |
| p-value | 0.000204 |
| Classification | Highly significant (p < 0.001) |

The seven region dummies jointly improve the employment-opportunity index fit
beyond what `beta_E_gsur` alone provides.

**Individual parameter table** (SEs and p-values from original estimation):

| Parameter | Region | Estimate | SE | z | p | Sig |
|---|---|---|---|---|---|---|
| `beta_E_drgn2` | Paris Basin | 0.8013 | 0.2664 | 3.008 | 0.0026 | ** |
| `beta_E_drgn3` | North | 0.6564 | 0.3186 | 2.060 | 0.0394 | * |
| `beta_E_drgn4` | East | 1.5626 | 0.4100 | 3.811 | 0.0001 | *** |
| `beta_E_drgn5` | West | 0.7725 | 0.2722 | 2.838 | 0.0045 | ** |
| `beta_E_drgn6` | South-West | 0.7665 | 0.3275 | 2.341 | 0.0192 | * |
| `beta_E_drgn7` | Centre-East | 0.6405 | 0.3118 | 2.054 | 0.0399 | * |
| `beta_E_drgn8` | Mediterranean | 0.4631 | 0.2794 | 1.658 | 0.0974 | — |

Six of seven region dummies are individually significant at 5%. `beta_E_drgn8`
(Mediterranean, drgn1 = 8) is not significant at 5% (p = 0.097) but is retained
under the joint test result: the Wald statistic reflects the joint information
in all seven parameters and their cross-covariance; dropping a marginally
insignificant individual dummy on the basis of its marginal p-value alone is
not supported when the joint test is highly significant.

All seven estimates are positive, indicating that all non-IDF regions show
higher employment opportunity than IDF (Île-de-France) after conditioning on
`beta_E_gsur`. East France (drgn4) shows the strongest effect (1.5626), more
than twice the next-largest (drgn2, drgn5, drgn6 at 0.77–0.80).

---

## 10. Region covariance and correlation diagnostics

**7×7 region VCV standard errors** (from the recomputed Hessian VCV):

| Parameter | SE |
|---|---|
| `beta_E_drgn2` | 0.2664 |
| `beta_E_drgn3` | 0.3186 |
| `beta_E_drgn4` | 0.4100 |
| `beta_E_drgn5` | 0.2722 |
| `beta_E_drgn6` | 0.3275 |
| `beta_E_drgn7` | 0.3118 |
| `beta_E_drgn8` | 0.2794 |

These are consistent with the original estimation SEs to four decimal places,
confirming that the Hessian recomputation is accurate.

**Correlation matrix (7×7)**

|  | drgn2 | drgn3 | drgn4 | drgn5 | drgn6 | drgn7 | drgn8 |
|---|---|---|---|---|---|---|---|
| drgn2 | 1.000 | 0.174 | 0.131 | 0.191 | 0.160 | 0.165 | 0.191 |
| drgn3 | 0.174 | 1.000 | 0.124 | 0.151 | 0.123 | 0.115 | 0.176 |
| drgn4 | 0.131 | 0.124 | 1.000 | 0.124 | 0.103 | 0.104 | 0.129 |
| drgn5 | 0.191 | 0.151 | 0.124 | 1.000 | 0.163 | 0.172 | 0.183 |
| drgn6 | 0.160 | 0.123 | 0.103 | 0.163 | 1.000 | 0.146 | 0.152 |
| drgn7 | 0.165 | 0.115 | 0.104 | 0.172 | 0.146 | 1.000 | 0.155 |
| drgn8 | 0.191 | 0.176 | 0.129 | 0.183 | 0.152 | 0.155 | 1.000 |

**No high-correlation flags** (all |corr| ≤ 0.70; maximum observed: 0.191).

The low off-diagonal correlations are structurally expected: households belong
to exactly one EUROMOD region, so the cross-second-derivatives of the log-
likelihood with respect to two distinct region dummies are zero by construction
(a household cannot simultaneously activate drgn2 and drgn3). The non-zero
off-diagonal elements in the VCV arise through the shared dependence on
other parameters; they remain small. No evidence of multicollinearity in the
region dummy block.

---

## 11. GSUR-region identification diagnostics

**8×8 GSUR+region Hessian sub-block eigenvalues**

Sub-block spans {β_E_gsur, β_E_drgn2, …, β_E_drgn8}, extracted from the full
recomputed Hessian.

| # | Eigenvalue | Sign |
|---|---|---|
| 1 | 5.768×10⁰ | positive |
| 2 | 8.570×10⁰ | positive |
| 3 | 1.116×10¹ | positive |
| 4 | 1.228×10¹ | positive |
| 5 | 1.447×10¹ | positive |
| 6 | 1.638×10¹ | positive |
| 7 | 1.726×10¹ | positive |
| 8 | 2.855×10² | positive |

**All 8 eigenvalues are positive.** Minimum eigenvalue: 5.768. Maximum: 285.5.
The 8×8 GSUR+region sub-block is locally convex at the solution. No saddle-
point direction in the region opportunity block. The large gap between
eigenvalue 7 (17.26) and eigenvalue 8 (285.5) reflects the dominance of
`beta_E_gsur` (the single continuous variable) relative to the seven binary
region indicators in the local curvature.

---

## 12. beta_E_gsur stability

`beta_E_gsur` shifts from −1.0502 (M0c_b2_GSURv2) to −1.3289 (M1-clean), a
change of −0.279 (Δ = −26.6% in absolute magnitude).

| Specification | `beta_E_gsur` | SE | t | p |
|---|---|---|---|---|
| M0c_b2 (pre-GSURv2) | −0.7438 | 0.2130 | −3.49 | 0.0005 |
| M0c_b2_GSURv2 | −1.0502 | 0.2002 | −5.25 | 1.55×10⁻⁷ |
| M1-clean | −1.3289 | 0.1631 | −8.15 | 4.44×10⁻¹⁶ |

The M1-clean shift is coherent: the seven region dummies absorb region-specific
opportunity variation that was previously loaded onto the GSUR coefficient.
After conditioning on the explicit region indicators, the residual GSUR
coefficient strengthens further (from −1.05 to −1.33), indicating that the
GSUR variable and the region dummies capture complementary, not redundant,
variation. The SE on `beta_E_gsur` narrows from 0.200 to 0.163 across the
three specifications (improvement in precision). The strengthening direction is
consistent across M0c_b2 → M0c_b2_GSURv2 → M1-clean as the regional
labour-market signal is progressively purified.

The M0c_b2_GSURv2 verdict §4 documents that `beta_E_gsur` is identified on
the centred, proportion-units GSUR variable and does not have a direct
probability semi-elasticity interpretation; this caveat carries forward to
M1-clean. The structural interpretability established in the baseline verdict
is preserved.

---

## 13. Comparison to M0c_b2_GSURv2

### Summary comparison table

| Diagnostic | M0c_b2_GSURv2 | M1-clean | Direction |
|---|---|---|---|
| Log-likelihood | −6501.21 | −6487.55 | +13.66 M1-clean |
| AIC | 13096.4 | 13081.1 | −15.3 M1-clean |
| BIC | 13611.6 | 13662.0 | +50.4 M0c_b2_GSURv2 |
| McFadden ρ² | 0.70875 | 0.70936 | +0.00061 M1-clean |
| Parameters | 47 | 53 | +6 net |
| Valid SEs | 44/47 | 50/53 | same fraction |
| NA SEs | 3 | 3 | same block |
| p < 0.05 (estimable) | 29/44 | 35/50 | +6 |
| Participation Δ (sm) | +0.04 ppt | −0.88 ppt | sign reversal |
| Participation Δ (sf) | +2.39 ppt | +1.94 ppt | improved |
| Participation Δ (cm) | +1.48 ppt | +1.29 ppt | improved |
| Participation Δ (cf) | +2.61 ppt | +2.44 ppt | improved |
| Hours-bin L1 (sm) | 0.634 | **0.695** | **M1-clean worse +9.6%** |
| Hours-bin L1 (sf) | 0.422 | 0.418 | ≈same |
| Hours-bin L1 (cm) | 0.350 | 0.345 | ≈same |
| Hours-bin L1 (cf) | 0.505 | 0.500 | ≈same |
| Occupation fit (cm/cf) | max |Δ| ≤ 0.007 | max |Δ| ≤ 0.007 | unchanged |
| Wage fit | unchanged | unchanged | — |
| Hessian κ | 5.14×10¹⁰ | 5.10×10¹⁰ | −0.8% |
| Negative eigenvalues | 1 | 1 | unchanged |
| `beta_E_gsur` | −1.0502 | −1.3289 | strengthened |
| Region block (new) | — | W = 28.18, p = 0.0002 | highly significant |
| Region collinearity | — | max corr = 0.191 | no collinearity |
| GSUR+region eigenvalues | — | all positive | locally convex |

### Key structural changes introduced by M1-clean

1. `beta_E_educH` removed (reclassified as ability under JMP partition; was
   +0.439, p = 0.052 in M0c_b2_GSURv2 — the marginal significance made
   reclassification clean).

2. Seven region dummies added, jointly significant (W = 28.18, p < 0.001),
   six individually significant at 5%. All positive: all non-IDF regions show
   higher employment opportunity than IDF after GSUR conditioning.

3. `beta_E_gsur` strengthens by −0.279 (−26.6% in absolute value), coherent
   with the region dummies absorbing region-specific variation from the GSUR
   coefficient.

4. Preference, wage, occupation, and hours-opportunity blocks unchanged (all
   parameter shifts < 0.01 in absolute value for the frozen blocks).

---

## 14. Diagnostics that passed

The following diagnostics pass without qualification:

**Estimation quality**
- Convergence: three independent starts all reach LL = −6487.5522 (identical
  parameter vector verified); unique attractor confirmed.
- CONOPT status: `NormalCompletion / OptimalLocal` on all three starts.
- No bound hits on any of the 53 parameters.

**Parameter identification (global)**
- 50 of 53 parameters have valid SEs.
- 35 of 50 estimable parameters significant at p < 0.05.
- The preference, wage, occupation, and hours-opportunity blocks are all
  identified with the same structure as M0c_b2_GSURv2.
- No new NA SEs introduced by M1-clean (the three NA SEs are the same
  singles consumption block as M0c_b2_GSURv2).

**Region block identification (M1-specific)**
- Joint Wald test: W = 28.18 (7 d.f.), p = 0.000204 — highly significant.
- No region-pair correlation exceeds 0.20 (maximum 0.191).
- All 8 eigenvalues of the GSUR+region Hessian sub-block are positive
  (min = 5.77); the sub-block is locally convex.
- `beta_E_gsur` strengthens coherently (−1.05 → −1.33); GSUR and region
  dummies capture complementary variation.

**Fit diagnostics**
- Participation fit improves for sf, cm, cf relative to M0c_b2_GSURv2.
- Hours-bin fit for sf, cm, cf: unchanged or marginally improved.
- Mean hours fit: unchanged across all four groups (max Δ = 0.04 h).
- Wage fit: unchanged.
- Occupation fit (couples): unchanged, remains excellent (max |Δ| ≤ 0.007).
- Probability normalisation: machine precision (max error 7.77×10⁻¹⁶).
- Marginal utilities: all positive across all 4,253 households.
- Chosen-probability distribution: identical to M0c_b2_GSURv2 across all
  quantiles.

**Parameter stability (frozen blocks)**
- Preference parameters: maximum shift < 0.01 in absolute value.
- Wage parameters: shift ≤ 0.001 in absolute value.
- Occupation parameters: shift ≤ 0.002 in absolute value.
- `beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`: shifts ≤ 0.05, remaining
  highly significant (all p < 0.001).

---

## 15. Diagnostics that failed or remain weak

The following diagnostics are explicitly failed or remain structurally weak.
They are listed without verdict recommendation.

**Failed: Hours-bin fit for singles male**
M1-clean L1 = 0.695 vs M0c_b2_GSURv2 L1 = 0.634 (+9.6%). L2 also worsens
(+10.5%). The root cause is the all-positive region dummy structure: every
non-IDF region receives a positive employment-opportunity shift, increasing
predicted mass in the 21–30 h bin for singles male. The observed singles-male
hours distribution is concentrated in the 31–40 h bin (observed 0.480), but
the model already over-predicted the 21–30 h bin in M0c_b2_GSURv2 (0.561 vs
observed 0.257); M1-clean amplifies this to 0.590. This is a regression, not
a new failure — the bin-distribution limitation pre-existed, but M1-clean
makes it measurably worse for this group.

**Structurally weak (inherited): Singles consumption joint-identification**
Three NA SEs on `beta_c_sm`, `beta_c_sf`, `theta_c_singles`. Unchanged from
M0c_b2_GSURv2. The pseudoinverse produces negative diagonal entries in this
sub-block; SEs are not available. The minimum Hessian eigenvalue worsens
(−35.60 vs −15.01 in M0c_b2_GSURv2), reflecting the interaction between the
new region parameters and the collinear block through the shared opportunity
index. Point estimates of all three parameters are stable (all shifts < 0.10
in absolute value from M0c_b2_GSURv2). This is a data limitation, not an
M1-clean failure, but any welfare decomposition that requires identified singles
consumption curvature operates under this constraint.

**Structurally weak (inherited): Couples-female participation overprediction**
Predicted 0.9896 vs observed 0.9651 (+2.44 ppt). Slightly improved from
M0c_b2_GSURv2 (+2.61 ppt) but structurally unchanged. The model produces
near-universal employment in couples female because there are no fixed costs
of work or formal rationing. This affects the welfare-partition interpretation
for couples female (the model attributes near-zero non-employment probability
to circumstance, which may overstate the scope for opportunity-driven welfare
improvement).

**Structurally weak (inherited): Singles wage underprediction**
Predicted wage 12.59 €/h vs observed 16.21 €/h for singles male (−22%),
12.73 €/h vs 15.11 €/h for singles female (−16%). The pooled Mincer
specification does not recover singles-specific wage levels. Unchanged from
M0c_b2_GSURv2; reflected in the quantile underprediction at all percentiles
for singles.

**Structurally weak (inherited): Singles occupation fit**
Max |Δ| = 0.168 (sm) and 0.199 (sf). The model over-predicts routine cognitive
and under-predicts nonroutine cognitive for both singles groups. Unchanged
from M0c_b2_GSURv2; absent group-specific occupation shifters at the singles
tier cannot be corrected by region dummies.

**BIC increase**
BIC increases by +50.4 (M1-clean worse). This is a mechanical consequence of
adding 6 net parameters to a model that already has 47. Whether the BIC
penalty is an informative model-comparison signal or simply a penalty for
theoretically motivated parameters is an interpretive question for the verdict,
not a hard diagnostic failure.

**`beta_E_drgn8` individual non-significance**
Mediterranean region (drgn1 = 8): p = 0.097. Not significant at 5%
individually. The joint Wald test remains highly significant; individual
non-significance of `drgn8` alone is not sufficient to drop the whole region
block. Whether to pool drgn8 with another region or retain it in the
seven-dummy design is a verdict-level question.

---

## 16. Evidence needed for the M1-clean verdict

The following categories of evidence are not provided by this report and must
be resolved at the verdict stage:

**Still interpretive (not hard-gated)**

1. **BIC penalty**: AIC favours M1-clean (−15.3); BIC penalises it (+50.4).
   Whether the six net additional parameters are justified by the JMP's
   normative welfare-partition requirement is a theoretical judgement, not a
   statistical one. The verdict must weigh AIC improvement against BIC penalty
   in the context of the design memo's rationale (§4 of
   `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md`).

2. **Singles-male hours regression**: the +9.6% worsening in L1 for singles
   male is a real cost of the region dummy structure. The verdict must decide
   whether this fit tradeoff is acceptable given the gain in welfare-partition
   alignment. The standard post-estimation report confirms the mechanistic
   cause (all-positive region shifters), which is correct given the empirical
   estimates; there is no specification error.

3. **`beta_E_drgn8` pooling decision**: Mediterranean is the one individually
   insignificant region dummy. The verdict may accept it on the basis of the
   joint test, pool it with a neighbouring region, or require M1-naive
   sensitivity. This is an active design question, not a diagnostic failure.

4. **Welfare-partition completeness**: removing `beta_E_educH` and adding
   region dummies brings the opportunity block one step closer to the JMP's
   normative partition, but the verdict should confirm that no other
   opportunity-classified variables remain misassigned under the ability/
   opportunity criterion before accepting M1-clean as the welfare baseline.

**Not yet estimated (required for robustness, per design memo §6 / M0c_b2_GSURv2 verdict §10 S2)**

5. **M1-naive sensitivity** (`beta_E_educH` retained, region dummies added):
   the design memo requires this as robustness exposure R2. Until M1-naive
   is estimated, the contribution of removing `beta_E_educH` to M1-clean's
   fit profile cannot be separated from the contribution of adding the region
   dummies. The M1-specific diagnostics in this report address the region
   block only. Whether M1-naive is required before the verdict or can follow
   it is a verdict-level decision; the diagnostic evidence does not compel
   either sequencing.

**Hard gates (already satisfied)**

The following gates were previously hard requirements under the M0c_b2_GSURv2
verdict and the M1-clean design memo. They are satisfied:

| Gate | Status |
|---|---|
| Convergence to identical LL across ≥ 3 independent starts | **Passed** (3/3 starts, LL = −6487.5522) |
| No bound hits | **Passed** (0/53 parameters) |
| Preference block stability (all shifts < 5%) | **Passed** (max shift < 0.01) |
| Wage and occupation block stability | **Passed** (max shift ≤ 0.002) |
| Region block jointly significant | **Passed** (W = 28.18, p = 0.0002) |
| No region collinearity (max |corr| ≤ 0.70) | **Passed** (max = 0.191) |
| GSUR+region sub-block locally convex | **Passed** (all 8 eigenvalues positive) |
| `beta_E_gsur` coherent shift direction | **Passed** (strengthens from −1.05 to −1.33) |
| Standard post-estimation completed without errors | **Passed** (26 files, no exceptions) |
| Marginal utilities all positive | **Passed** (0 negative MUC/MUL) |

---

*Sources: `Results/RURO_occ_M1_clean_standard_post_estimation_diagnostics_v1.md`,
`Results/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`,
`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_diagnostics_implementation_report_v1.md`,
`Results/RURO_occ_M1_clean_estimation_report_v1.md`,
`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_design_memo_v2.md`,
`Results/RURO_occ_M0c_b2_GSURv2_estimation_report_v1.md`,
`Results/RURO_occ_M0c_b2_GSURv2_post_estimation_diagnostics_v1.md`,
`docs/France_case/P3a/execution_logs/single_year_baseline/M0c/RURO_occ_M0c_b2_GSURv2_verdict_v1.md`*