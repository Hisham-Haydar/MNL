# RURO occ M1-naive Supplementary Diagnostics v1

Date: 2026-05-18
Spec: `ruro_occ_M1_naive` (54 parameters)
Estimation run: `run_2026-05-18_17-50-20`
Parameters source: `outputs/post_estimation/fr/spec/ruro_occ_M1_naive/gamspy/estimation_spec_ruro_occ_M1_naive/run_2026-05-18_18-50-21/params.csv`
MNL base: `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2`
Hessian step (eps): 1e-5
Script: `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py`
Implementation report: `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md`

Comparison reference throughout: `ruro_occ_M1_clean`
(M1-clean supplementary diagnostics: `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`)

---

## Overview

Four diagnostics for the M1-naive extended opportunity block. The full 54×54
numerical Hessian was recomputed via central-difference finite differences on
the joint gradient function (108 gradient evaluations).

| Full-Hessian metric | M1-naive | M1-clean |
|---|---|---|
| Condition number (recomputed) | 5.1484×10¹⁰ | 5.0957×10¹⁰ |
| Negative eigenvalues | 1 | 1 |

The recomputed condition number is consistent with the estimation-time value
(5.148×10¹⁰ from `identification_diagnostics.txt`), confirming the recomputation
is accurate. The single negative eigenvalue is unchanged in count relative to
M1-clean.

CSV outputs:

- `Results/RURO_occ_M1_naive_vcv_region_block_20260518_170632.csv` — 7×7 region VCV
- `Results/RURO_occ_M1_naive_vcv_educ_gsur_region_block_20260518_170632.csv` — 9×9 educH+GSUR+region VCV
- `Results/RURO_occ_M1_naive_hessian_gsur_educ_region_block_20260518_170632.csv` — 9×9 Hessian sub-block

---

## D1 — Joint Wald test: β_E_drgn2 = … = β_E_drgn8 = 0

**H₀**: β_E_drgn2 = β_E_drgn3 = … = β_E_drgn8 = 0 (7 restrictions)

| | M1-naive | M1-clean |
|---|---|---|
| **Wald statistic W** | **28.20** | 28.18 |
| **Degrees of freedom** | **7** | 7 |
| **p-value** | **0.000202** | 0.000204 |
| **Classification** | Highly significant (p < 0.001) | Highly significant (p < 0.001) |

The seven region dummies remain jointly highly significant in M1-naive. The Wald
statistic is essentially identical to M1-clean (28.20 vs 28.18; p changes by 0.000002).
Adding `beta_E_educH` has no material effect on the joint significance of the region block.

### Individual region parameter table

SEs and p-values from the original estimation (GAMSPy Hessian); Wald statistic uses
recomputed VCV. M1-clean p-values shown for comparison.

| Parameter | Region | Estimate | SE | z | p | Sig | M1-clean p |
|---|---|---|---|---|---|---|---|
| `beta_E_drgn2` | Paris Basin | 0.8215 | 0.2671 | 3.076 | 0.0021 | ** | 0.0026 |
| `beta_E_drgn3` | North | 0.5563 | 0.3222 | 1.727 | 0.0842 | . | 0.0394 |
| `beta_E_drgn4` | East | 1.5422 | 0.4114 | 3.749 | 0.0002 | *** | 0.0001 |
| `beta_E_drgn5` | West | 0.8062 | 0.2735 | 2.948 | 0.0032 | ** | 0.0045 |
| `beta_E_drgn6` | South-West | 0.7780 | 0.3282 | 2.370 | 0.0178 | * | 0.0192 |
| `beta_E_drgn7` | Centre-East | 0.6591 | 0.3114 | 2.117 | 0.0343 | * | 0.0399 |
| `beta_E_drgn8` | Mediterranean | 0.4376 | 0.2806 | 1.560 | 0.1188 | — | 0.0974 |

*: p<0.05  **: p<0.01  ***: p<0.001  .: p<0.10

Five of seven dummies remain significant at 5% in M1-naive (drgn2, 4, 5, 6, 7).
`beta_E_drgn3` (North) weakens from p = 0.039 (M1-clean) to p = 0.084 (M1-naive),
falling below the 5% threshold. `beta_E_drgn8` (Mediterranean) was already
borderline in M1-clean (p = 0.097) and remains so (p = 0.119). The weakening of
drgn3 is consistent with `beta_E_educH` absorbing part of the North-region education
signal (see D4). The joint test is unaffected.

---

## D2 — 7×7 region covariance / correlation sub-block

### Standard errors (M1-naive vs M1-clean)

| Parameter | M1-naive SE | M1-clean SE | Δ |
|---|---|---|---|
| `beta_E_drgn2` | 0.2671 | 0.2664 | +0.0007 |
| `beta_E_drgn3` | 0.3222 | 0.3186 | +0.0036 |
| `beta_E_drgn4` | 0.4114 | 0.4100 | +0.0014 |
| `beta_E_drgn5` | 0.2735 | 0.2722 | +0.0013 |
| `beta_E_drgn6` | 0.3282 | 0.3275 | +0.0007 |
| `beta_E_drgn7` | 0.3114 | 0.3118 | −0.0004 |
| `beta_E_drgn8` | 0.2806 | 0.2794 | +0.0012 |

All region SEs are essentially unchanged (maximum increase 0.004 for drgn3). The
addition of `beta_E_educH` does not meaningfully inflate the uncertainty of any
region dummy.

### Correlation matrix (7×7)

|  | drgn2 | drgn3 | drgn4 | drgn5 | drgn6 | drgn7 | drgn8 |
|---|---|---|---|---|---|---|---|
| `drgn2` | 1.000 | 0.167 | 0.130 | 0.193 | 0.160 | 0.166 | 0.189 |
| `drgn3` | 0.167 | 1.000 | 0.125 | 0.137 | 0.118 | 0.109 | 0.182 |
| `drgn4` | 0.130 | 0.125 | 1.000 | 0.122 | 0.102 | 0.103 | 0.130 |
| `drgn5` | 0.193 | 0.137 | 0.122 | 1.000 | 0.164 | 0.176 | 0.177 |
| `drgn6` | 0.160 | 0.118 | 0.102 | 0.164 | 1.000 | 0.147 | 0.149 |
| `drgn7` | 0.166 | 0.109 | 0.103 | 0.176 | 0.147 | 1.000 | 0.152 |
| `drgn8` | 0.189 | 0.182 | 0.130 | 0.177 | 0.149 | 0.152 | 1.000 |

**No high-correlation flags** (all |corr| ≤ 0.70; maximum observed: 0.193).

The correlation structure is essentially unchanged from M1-clean (M1-clean maximum:
0.191). By construction (households belong to exactly one NUTS-1 region), the
cross-second-derivatives of drgn_i × drgn_j in the Hessian are zero — all off-diagonal
elements arise only through shared dependence on other parameters. The small changes
vs M1-clean (all |Δ corr| ≤ 0.014) confirm no new collinearity was introduced by
`beta_E_educH`.

---

## D3 — 9×9 GSUR+educH+region Hessian sub-block eigenvalues

Sub-block spanning {β_E_gsur, β_E_educH, β_E_drgn2, …, β_E_drgn8} extracted from
the full numerical Hessian. Extends the M1-clean 8×8 block by one dimension
(β_E_educH added).

**Sub-block condition number**: 51.51

**Eigenvalues** (ascending):

| # | Eigenvalue | Sign |
|---|---|---|
| 1 | 5.5587e+00 | positive |
| 2 | 8.1615e+00 | positive |
| 3 | 1.1131e+01 | positive |
| 4 | 1.2145e+01 | positive |
| 5 | 1.4379e+01 | positive |
| 6 | 1.6293e+01 | positive |
| 7 | 1.7163e+01 | positive |
| 8 | 3.9547e+01 | positive |
| 9 | 2.8633e+02 | positive |

Negative eigenvalues in 9×9 sub-block: **0**
Minimum eigenvalue: 5.559
Maximum eigenvalue: 286.3

**All 9 eigenvalues are positive.** The 9×9 GSUR+educH+region sub-block is locally
convex at the M1-naive solution; the extended opportunity block is well-identified.

**Comparison to M1-clean 8×8 block:**

| Metric | M1-naive 9×9 | M1-clean 8×8 |
|---|---|---|
| Negative eigenvalues | 0 | 0 |
| Minimum eigenvalue | 5.559 | 5.768 |
| Maximum eigenvalue | 286.3 | 285.5 |
| Condition number | 51.51 | ~49.5 (285.5/5.768) |

The minimum eigenvalue is slightly lower in M1-naive (5.559 vs 5.768), consistent
with the addition of one dimension that shares covariance with GSUR. The reduction
is small (−3.6%) and does not approach zero. The condition number of the sub-block
(51.51) is well below the global ill-conditioning threshold (κ ≈ 5×10¹⁰), confirming
that the pathological condition number of the full Hessian is localised in the
singles-consumption block, not the opportunity block.

The addition of `beta_E_educH` inserts one extra positive-curvature direction into
the sub-block, producing nine eigenvalues where M1-clean had eight. The expanded
block remains locally convex (all eigenvalues positive, minimum 5.559). Mapping
individual eigenvalues to specific parameters would require eigenvectors and is not
done here.

---

## D4 — β_E_educH cross-correlations with GSUR and region parameters

| β_E_educH ↔ | Cov | SE(educH) | SE(partner) | Corr |
|---|---|---|---|---|
| `beta_E_gsur` | 3.2652×10⁻² | 0.2323 | 0.2197 | **0.6397** |
| `beta_E_drgn2` | 2.2948×10⁻³ | 0.2323 | 0.2671 | 0.0370 |
| `beta_E_drgn3` | −1.1651×10⁻² | 0.2323 | 0.3222 | −0.1557 |
| `beta_E_drgn4` | −2.2599×10⁻³ | 0.2323 | 0.4114 | −0.0236 |
| `beta_E_drgn5` | 4.3083×10⁻³ | 0.2323 | 0.2735 | 0.0678 |
| `beta_E_drgn6` | 1.5948×10⁻³ | 0.2323 | 0.3282 | 0.0209 |
| `beta_E_drgn7` | 2.2738×10⁻³ | 0.2323 | 0.3114 | 0.0314 |
| `beta_E_drgn8` | −3.0883×10⁻³ | 0.2323 | 0.2806 | −0.0474 |

**Maximum |corr|**: 0.6397 (β_E_educH ↔ β_E_gsur)

### Mechanical interpretation

The β_E_educH ↔ β_E_gsur correlation is **0.640** — elevated but below the 0.70
collinearity flag threshold. This correlation confirms that education and GSUR capture
overlapping variation in employment opportunity: they co-move positively (both are
positive-opportunity variables), and conditioning on one affects the other.

However, 0.640 is below 0.70 and is structurally expected: GSUR is itself a
function of the regional unemployment-rate gap, which correlates with regional
education composition. The correlation does not indicate redundancy — it indicates
shared labour-market signal. The eigenvalue evidence (all 9 eigenvalues positive,
minimum 5.559) confirms that despite this correlation, the two variables contribute
genuinely separable curvature at the solution.

The β_E_educH ↔ region dummy correlations are all small (maximum |0.156| for drgn3).
The drgn3 (North) correlation is −0.156, consistent with the interpretation from D1:
the North region has above-average education composition, so `beta_E_educH` absorbs
part of the North-specific opportunity signal, weakening drgn3 individually (p: 0.039
→ 0.084). No other region shows a correlation with educH above |0.07|.

**Conclusion on allocation**: `beta_E_educH` primarily reallocates explanatory weight
from `beta_E_gsur` (corr = 0.640) and secondarily from `beta_E_drgn3` (corr = −0.156).
The reallocation from GSUR is the mechanism behind the `beta_E_gsur` reversion from
−1.329 (M1-clean) to −1.048 (M1-naive). The reallocation does not eliminate GSUR's
contribution (GSUR t = −4.77, p < 0.001 in M1-naive). The region block's joint
significance is unaffected. `beta_E_educH` therefore adds partially distinct
variation: it does not merely relabel GSUR, but it does share a substantial fraction
of its variance with GSUR.

---

## D5 — Evidence-only interpretation

This section assembles the four diagnostic results into factual evidence statements.
No verdict on whether M1-naive should replace M1-clean is made here.

### D5.1 — Whether the region block remains jointly significant in M1-naive

**Yes, unambiguously.** W = 28.20 (7 d.f.), p = 0.000202. The Wald statistic is
essentially identical to M1-clean (W = 28.18, p = 0.000204). Adding `beta_E_educH`
has no material effect on the joint significance of the region block.

### D5.2 — Whether the region block becomes materially weaker than in M1-clean

**Marginally, for one dummy (drgn3); no effect on the rest.**

- drgn3 (North): p weakens from 0.039 (M1-clean) to 0.084 (M1-naive). This is a
  real change in individual significance (crosses the 5% threshold) but is mechanically
  explained by the drgn3 × educH covariance (corr = −0.156): education composition in
  northern France is above average, and `beta_E_educH` absorbs part of the North effect.
  The point estimate is stable (0.6564 → 0.5563).
- drgn8 (Mediterranean): p moves from 0.097 to 0.119 — slightly weaker individually,
  but this was already below 5% in M1-clean. No material additional weakening.
- All other five region dummies retain significance at 5%; their SEs change by < 0.004.
- The joint Wald statistic is unchanged to two decimal places.

**Conclusion**: the region block is not materially weakened in M1-naive. One dummy
(drgn3) loses individual 5% significance due to a partial education–region correlation;
this is a minor realignment, not a structural failure of the regional specification.

### D5.3 — Whether β_E_educH introduces a new collinearity concern

**No new collinearity concern.** The thresholds used throughout this project are:

- |corr| > 0.90: pseudoinverse artefact (singles-consumption block)
- |corr| > 0.70: collinearity flag

The β_E_educH ↔ β_E_gsur correlation is 0.640 — below the 0.70 flag threshold.
No region dummy has |corr| with educH above 0.156. No high-correlation flag is
triggered in D2. The full-Hessian condition number is unchanged (5.15×10¹⁰ in M1-naive
vs 5.10×10¹⁰ in M1-clean) and continues to reflect the pre-existing singles-consumption
pathology, not a new educH-induced collinearity.

The D3 eigenvalue evidence confirms local convexity of the 9×9 opportunity sub-block
(minimum eigenvalue 5.559, condition number 51.5). There is no saddle-point direction
in the extended opportunity block.

**However**: the correlation of 0.640 is meaningfully elevated and does reflect partial
sharing of variance between GSUR and education. This is below the flag threshold but
is the key mechanism behind the structural changes in M1-naive (β_E_gsur reversion,
drgn3 weakening). The verdict should note that GSUR and educH are not fully separable
in this data — their correlation (0.640) is moderate, not negligible.

### D5.4 — Whether the M1-naive opportunity block remains locally identified

**Yes.** Evidence:

| Criterion | M1-naive | Status |
|---|---|---|
| 9×9 GSUR+educH+region sub-block: all eigenvalues positive | yes (min = 5.559) | PASS |
| 9×9 sub-block condition number | 51.51 | PASS (well below 10¹⁰) |
| No new NA SEs in opportunity block | confirmed (all 9 params have valid SEs) | PASS |
| No β_E_educH / region pairwise abs-corr > 0.70 | max = 0.156 (drgn3) | PASS |
| β_E_educH ↔ β_E_gsur abs-corr < 0.70 | 0.640 | PASS (marginal) |
| Joint region Wald p < 0.001 | p = 0.000202 | PASS |
| Full-Hessian negative eigenvalues | 1 (same as M1-clean) | unchanged |

The M1-naive opportunity block is locally identified and locally convex at the
solution. The single negative eigenvalue in the full Hessian is localised in the
singles-consumption block (pre-existing), not the opportunity block.

---

## Summary

| Diagnostic | M1-naive result | M1-clean reference | Assessment |
|---|---|---|---|
| D1: Region block Wald (7 d.f.) | W = 28.20, p = 0.000202 | W = 28.18, p = 0.000204 | Unchanged — highly significant |
| D2: Max pairwise region abs-corr | 0.193 | 0.191 | Unchanged — no collinearity |
| D3: 9×9 sub-block min eigenvalue | 5.559 (all positive) | 5.768 (8×8, all positive) | Slight decrease; sub-block locally convex |
| D4: β_E_educH ↔ β_E_gsur corr | 0.640 | — (M1-clean has no educH) | Below flag threshold; moderate sharing of variance |
| D4: Max β_E_educH ↔ region abs-corr | 0.156 (drgn3) | — | Low; drgn3 partial reallocation explained |
| Region block jointly significant | yes | yes | Unchanged |
| Region block materially weaker | no (drgn3 only, minor) | reference | Minor; joint test unaffected |
| New collinearity introduced | no | — | PASS |
| Opportunity block locally identified | yes | yes | Unchanged |

---

*Generated by `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py`*
*Evidence only — no verdict. See `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md` for implementation notes.*
