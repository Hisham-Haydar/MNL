# RURO Recovery Test Results v2 — bpool_p3a_v1 (55 params, beta_c=1 scale normalisation)

> **Corrections-of-record (2026-05-29):** the "non-convexity in the couples leisure block on the 9×9 joint-leisure grid" diagnosed here was a scipy trust-constr local-plateau artefact, NOT a real LL surface feature. CONOPT on the same slice recovers the entire couples leisure interior with correct signs (9 of 9 within err 0.43) and the entire market-opportunity block with correct signs (11 of 11 within err 0.41). The actual root cause was a chosen-row `working_lh` flag construction bug (fixed in commit `099e5c4` — see `RURO_recovery_test_results_v3.md`), which silently zeroed the LH indicator on chosen rows and drove `beta_h_lh` to the −10 bound, with the LH-correlated misfit propagating to the leisure block. **Do not act on the "parsimonise the couples leisure block" recommendation in §5 of this document** — it would be solving the wrong problem. The v2 diagnostic of the scale ridge being eliminated is correct; the verdict against the leisure block is overturned.

> ## VERDICT: ❌ DID NOT PASS — beta_c=1 broke the v1 ridge but exposed a SECOND, sharper non-convexity in the couples leisure block.
>
> The Phase-1 fix (beta_c fixed to 1.0 as utility numeraire) **was correctly applied
> and is structurally sound** — parser excludes beta_c/beta_c_sm/beta_c_sf from the
> 55-vector, engine treats beta_c as a compile-time constant on LL+gradient in both
> modes, and analytical gradient matches finite-difference to 7e-7. But on the same
> couples-2016 300-HH recovery slice that failed in v1:
>
> - **G3 PD = False, min_eig = −1.728e+02, cond = inf** — strongly negative
>   eigenvalue, not a flat ridge. The stopping point is **not even a saddle of
>   the LL viewed as concave** — there is real negative curvature.
> - **G2 = 6.69e+0** (target ~1e-6) — warm and cold landed at **different
>   non-optima** (LL −6479.3 vs −6527.2). No unique nearby stationary point.
> - **G1 recovery: 4/37 testable within tol & correct sign.** The miss is
>   concentrated, not random — see Section 3.
>
> **This is a different failure mode than v1.** The geometry has changed:
>
> | gate | v1 (beta_c free) | v2 (beta_c=1) |
> |---|---|---|
> | min Hessian eigenvalue | −0.0124 (near-flat ridge) | **−172.8** (sharp neg curvature) |
> | parameter at bound at stop | beta_l0_m → +21.05 (bound) | beta_l0_m → +0.057 (interior) |
> | beta_c at stop | +22.45 (drifted along ridge) | 1.0 (fixed; ridge eliminated) |
> | beta_l0_m at stop | +21.05 (pinned to bound) | +0.057 (interior, ‖g‖=205) |
> | beta_ll at stop | +2.25 | **+0.000 (collapsed)** |
> | G2 max\|warm−cold\| | n/a (1 start) | **6.69** |
>
> The v1 ridge (beta_c / beta_l0_* co-scaling, near-flat surface) is **eliminated**.
> What replaces it is a **non-convexity in the couples leisure block** — preference
> coefficients (`beta_l0_m`, `beta_l_age*_m/f`, `theta_l_m/f`, `beta_ll`) that
> collectively shape `[A_g(x)]·BC(l_m) + [A_g(x)]·BC(l_f) + beta_ll·BC(l_m)·BC(l_f)`
> on a 9×9=81-cell joint leisure grid for only 300 households. The likelihood has
> multiple competing local optima in that subspace; the optimiser lands at one
> and the Hessian shows the negative curvature toward the others.
>
> **Per Phase-2 instruction: no further spec modification.** Two open questions
> defer to user decision (Section 5).
>
> ---

**Date:** 2026-05-28
**Spec:** `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` (v2, 55 params, beta_c FIXED=1.0)
**Mode:** couples  **Years:** 2016  **n_hh:** 300  **Solver:** scipy-trustconstr (BFGS Hessian approx, trust-region; analytical gradient)
**Seed:** 20260527  **Flat-tol:** 5e-3 (loosened from 1e-6 to avoid grinding micro-steps in the flat region; well below any economically interpretable precision)
**Raw report:** `RURO_recovery_test_results_v2_raw.md`
**Console:** `recovery_v2_console.log`

---

## 1. Phase 1 — implementation of the normalisation (SOUND)

The mechanical fix is correct and verified end-to-end:

| check | result |
|---|---|
| `spec.utility_consumption_coef_fixed = 1.0` (read from `utility.consumption.fixed_value`) | ✅ |
| `len(spec.all_param_names) == 55` (was 58; beta_c, beta_c_sm, beta_c_sf removed) | ✅ |
| beta_c family absent from `initial_values` and `bounds` of the estimated vector | ✅ |
| LL finite on both modes (couples 742.8052; singles 402.2086 on 30-HH probes) | ✅ |
| Analytical gradient vs finite-difference (both modes, theta* random): max rel-err 7.36e-07 | ✅ |
| expression_constraints (numpy + GAMSPy symbolic) both use the fixed constant | ✅ |

Sites generalised (no hardcoding of `beta_c`; all use `spec.utility_consumption_coef_fixed`):
- `estimation_spec_parser.py`: dataclass field, parser block, `_build_parameter_list` threaded with `consumption_coef_fixed`, three exclusion sites (sm/sf/couples).
- `estimation_engine.py`: `_compute_utility_singles` (LL, 506-514), `_compute_utility_couples` (LL, 1462-1473), `_compute_utility_derivatives_singles` (943-952 + skip 980-984), `_compute_utility_derivatives_couples` (1898-1908 + skip 2007-2011). The `theta_c` derivative branches that multiply `(beta_c + …)·dbc_c_dθ` are robust because `beta_c` is the correct scalar either way.
- `expression_constraints.py`: numpy path (~292) and GAMSPy symbolic path (~555) both gated by `utility_consumption_coef_fixed`.

**The Phase-1 implementation is not the cause of the v2 failure.** Phase 2 ran cleanly; the failure is in the likelihood's geometry under this parameterisation, not in the fix.

---

## 2. Phase 2 — the verdict (FAIL)

### Starts

| start | success | LL | nit | sec | termination |
|---|---|---|---|---|---|
| warm (from θ\*) | False | −6479.27 | 353 | 439.6 | callback flat-stop |
| cold (from spec init) | False | −6527.24 | 295 | 389.5 | callback flat-stop on beta_l0_m ‖g‖=205 |

### G2 — reproducibility
`max|warm − cold|(testable) = 6.691e+00` against a ~1e-6 target. **Two different optima.**

### G3 — Hessian conditioning at warm-stop
- **PD: False**
- **min eig: −1.728e+02** (compare v1: −0.0124)
- **max eig: 1.638e+04**
- **cond: inf**

The Hessian has **5 negative eigenvalues** (carried over from the same diagnostic shape seen in M0c_b2 and P3a-pooled) but with much larger magnitude than v1. This is **not** a flat ridge; it is genuine negative curvature.

### G3b — market-opportunity collinearity
`worst |corr| = nan` because cov = H⁻¹ is undefined (non-PD H). Verdict cannot be assessed at this stopping point — defer until the model converges.

### G1/G4 — per-param recovery (testable only; 18 inert excluded)
**4 of 37** within tol=0.1 with correct sign. The 33 misses are **structured, not random** — see Section 3.

---

## 3. The pattern: where the non-convexity lives

Three observations group the misses:

### 3.1 The couples leisure block is unidentified at this stopping point
All five interior couples-leisure preference parameters have large errors, and four are wrong-signed:

| param | θ\* | θ̂ | abs_err | wrong_sign |
|---|---:|---:|---:|---|
| beta_l0_m | +0.0125 | +0.0004 | 0.012 | — |
| beta_l_age_m | −0.600 | +0.047 | 0.647 | **yes** |
| beta_l_age2_m | +0.120 | −0.982 | 1.102 | **yes** |
| theta_l_m | −0.750 | +0.945 | 1.695 | **yes** |
| beta_l0_f | +1.250 | +0.057 | 1.193 | — (collapsed to 0) |
| beta_l_age_f | −0.600 | −0.417 | 0.183 | — |
| beta_l_age2_f | +0.120 | −0.985 | 1.105 | **yes** |
| beta_l_nkids_f | −0.600 | −1.284 | 0.684 | — |
| theta_l_f | −1.250 | +0.116 | 1.366 | **yes** |
| **beta_ll** | **+2.500** | **+0.0002** | **2.500** | — (collapsed to 0) |

**`beta_ll` collapsed to zero** — the male×female leisure interaction shut off entirely. With `beta_ll = 0`, the joint leisure utility decomposes into independent male and female terms, and `beta_l0_m·BC(l_m) + beta_l0_f·BC(l_f)` becomes the only structure on the 9×9 = 81 joint-leisure cells. With both `beta_l0_*` near zero and the age/age² shifters mostly wrong-signed, the couples leisure utility is **near-flat in the preference parameters' values** — the negative-curvature direction sits inside that block.

### 3.2 Opportunity shifters scrambled by the unidentified preference block
The hours and market-opp parameters with the largest miss / wrong sign are all **dependent on the leisure margin**:

| param | θ\* | θ̂ | abs_err | wrong_sign |
|---|---:|---:|---:|---|
| beta_E (hours-intercept) | −3.000 | +0.747 | 3.747 | **yes** |
| beta_h_pt1 | +1.200 | −1.901 | 3.101 | **yes** |
| beta_h_lh (long-hours) | −1.200 | **−9.990** | 8.790 | — (at bound) |
| beta_E_gsur (great surrounding region) | +1.200 | −3.350 | 4.550 | **yes** |
| beta_E_drgn6, beta_E_drgn8 | ±1.200 | ±3.4–3.5 | 4.6, 4.6 | **yes** |
| beta_occ_2_cm | +1.200 | −1.837 | 3.037 | **yes** |
| beta_occ_3_cf, beta_occ_4_cf | ±1.200 | ∓0.6, +0.67 | 1.83, 1.87 | **yes** |

`beta_h_lh = −9.99` is at its bound (−10). This is the same "well-identified blocks show wrong signs because the optimizer never reached the optimum along the unidentified direction" pattern v1 documented, but here the unidentified direction is in the **couples leisure preference block**, not the consumption/leisure scale.

### 3.3 Singles preference block + wage block + sigma all correct
What recovers cleanly tells us where the non-convexity is **not**:

| param | θ\* | θ̂ | abs_err |
|---|---:|---:|---:|
| sigma | +0.3750 | +0.3749 | **0.0001** ✅ |
| beta_w0 | +2.500 | +2.291 | 0.209 ✅ |
| beta_w_educL | −0.0750 | −0.1800 | 0.105 ✅ |
| beta_w_educH | +0.2500 | +0.3046 | 0.055 ✅ |
| beta_E_y2015/y2017 | ±0.600 | ±0.51/−0.59 | 0.09/0.01 ✅ |
| beta_occ_*_sm, beta_occ_*_sf | all | all | 0.03–0.37 ✅ |
| beta_E_drgn2/3/7 | various | various | 0.13–0.46 ✅ |

The wage equation, sigma, year fixed effects, singles occupation block, and several region intercepts all recover. **The wage and access-margin equations are not the problem.** The couples leisure preferences are.

---

## 4. Why beta_c=1 did not suffice (and why this is informative)

Both the v1 ridge and the v2 non-convexity are properties of **how the multiplicative-shifter (ACS) couples utility decomposes**:

$$ U_{couple} = [A_g^m(x)]\cdot BC(l_m) + [A_g^f(x)]\cdot BC(l_f) + \beta_c\cdot BC(c) + \beta_{ll}\cdot BC(l_m)\cdot BC(l_f) $$

with $A_g^g(x) = \beta_{l0}^g + \beta_{age}^g\cdot age + \beta_{age2}^g\cdot age^2 + \beta_{nkids}^g\cdot nkids$.

**v1 ridge:** scaling $(\beta_c, \beta_{l0}^m, \beta_{l0}^f) \to \alpha\cdot(\beta_c, \beta_{l0}^m, \beta_{l0}^f)$ with compensating shift in alternative-invariant utility level is (almost) a flat direction → −0.012 eigenvalue at the bound.

**v2 non-convexity:** with $\beta_c$ pinned, the ridge is gone. But the couples leisure subspace
$\{\beta_{l0}^m, \beta_{age}^m, \beta_{age2}^m, \theta_l^m; \beta_{l0}^f, \beta_{age}^f, \beta_{age2}^f, \beta_{nkids}^f, \theta_l^f; \beta_{ll}\}$
— 10 parameters that all enter as products/multipliers of the Box-Cox leisure terms — defines a **non-convex 10-dimensional choice probability map** on 9×9 = 81 joint leisure cells per household. With 300 households, this map has **multiple local optima**. The likelihood is no longer flat; it is **multi-modal**, and trust-constr's BFGS Hessian approximation lands at a saddle of the negative log-likelihood (= a non-max of the LL).

**This is consistent with the R reference's behaviour** (the v1 memo §3 already noted unconstrained BFGS in R lands on the flat ridge without revealing it). R never normalises; v1 here didn't normalise either; both report apparent success at a non-stationary point. Once we normalise, the ridge becomes a non-convexity, which trust-constr can detect via the Hessian — and that detection is what is happening here.

---

## 5. Decision — two questions, no spec change

**Per Phase-2 instruction, no further modification is being made.** The recovery test was the gate; the gate failed; the spec, engine, and data are unchanged from the Phase-1 commit. The choice of what to do next is yours.

The pattern in §3 narrows the contingencies the task spec anticipated:

| Phase-2 contingency | match? | evidence |
|---|---|---|
| (i) ridge persists → second scale freedom | **partial** | Geometry **changed** (min_eig −0.012 → −173); the v1 scale ridge **is gone** (beta_c, beta_l0_* no longer drift to bounds along a flat direction). The new failure is **non-convexity in the couples-leisure subspace**, not a scale freedom. |
| (ii) PD but recovery fails on thin-margin → sample-size | no | not PD. min_eig of −173 is not thin-margin. |
| (iii) PD + clean recovery | no | failed both. |

So the right framing is **a fourth contingency the spec did not enumerate**: the normalisation succeeded mechanically and structurally, and **revealed a sharper identification problem the ridge was masking** — the multi-modality of the couples leisure preference subspace on a 300-HH slice with a 9×9 joint leisure grid.

### Two open questions for the user

1. **Is this multi-modality intrinsic to the couples ACS leisure structure**, or is it a sample-size artefact of 300 households with only 9 male × 9 female joint leisure cells? The v1 memo argued (correctly) that a *normalisation* indeterminacy does not sharpen with more data. But **multi-modality of a non-convex likelihood** *can* sharpen with more data — additional households add independent constraints on the same 10-parameter preference subspace, which may consolidate multiple local optima into one. The test is empirical: re-run on the full P3a couples pool (~7k HH) and see whether min_eig flips positive. If it does, this was a sample-size effect; if it stays negative, the multi-modality is structural.

2. **Is the couples leisure parameterisation over-rich for the data?** 10 parameters in the couples leisure block (5 male, 5 female: intercept + age + age² + nkids + theta) plus `beta_ll` for the interaction means 10 free parameters shaping the per-household joint leisure utility on 81 cells. The R reference reportedly uses age-banded children (`children0_3`, `children4_6`, `children7_9`) and `log(age)`, `log(age)²` instead of `age_norm`, `age_norm²` — a different but not obviously smaller parameterisation. A more parsimonious choice (e.g. drop `beta_l_age2_*` entirely; constrain `beta_l_age_m = beta_l_age_f`) would test whether the non-convexity dissolves when the leisure block has fewer DoF.

Neither question can be settled by reading the current diagnostic. Both require an additional run (or design discussion); neither is a "fix this specific thing" instruction the recovery test mandates.

---

## 6. Recommendation

**Do not modify the spec further from this evidence.** The recovery test established that:
- the beta_c numéraire normalisation is correct and necessary;
- it eliminates the v1 scale ridge;
- a separate, sharper, distinct non-convexity remains in the couples leisure preference block at 300 HH;
- the full G2/G3/G1 picture above is consistent with **multi-modality of a 10-parameter non-convex subspace on a 9×9 joint leisure grid with 300 HH** — diagnosable but not fixable from this run alone.

The natural next step is one of (and the choice is yours):

(a) **Re-test at the full P3a pool** (~7k couples HH) to distinguish sample-size multi-modality from structural multi-modality. This is the cheapest experiment that yields a definitive answer to question 1. ~3.5 h with CONOPT at full size, per the M0c_b2 baseline.

(b) **Trial a more parsimonious couples leisure block** (drop `beta_l_age2_*`, or pool `beta_l_age_m = beta_l_age_f`) and re-run the 300-HH recovery test. Cheap (~10 min) and directly tests question 2.

(c) **Switch the recovery test to multistart** (10–20 random starts within bounds; report best LL + dispersion of theta_hat across starts). If the non-convexity is real, multistart will land at multiple distinct local optima, with one having the best LL and a PD local Hessian; the others having negative eigenvalues toward it. This re-frames the diagnostic from "did it converge?" to "where are the local optima?" — cleanly fits the multi-modality reading.

No work has been committed past Phase 1.

---

## 7. Phase-1 artefacts to be committed (separately, on user say-so)

Per the task's success commit plan, the Phase-1 implementation is sound and ready to commit *independently* of the Phase-2 verdict (it is a structurally correct refactor regardless of whether it suffices for identification). Two atomic commits proposed:

- **Commit A — spec + engine + expression_constraints (Phase 1):**
  - `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` — fixed_value: 1.0; remove beta_c/beta_c_sm/beta_c_sf from initial_values + bounds; param count 58→55; documentation updated.
  - `scripts/enhanced/estimation_spec_parser.py` — new `utility_consumption_coef_fixed` field; parser block; threading into `_build_parameter_list`; three exclusion sites.
  - `scripts/enhanced/estimation_engine.py` — beta_c read + gradient column skipped, generically, at all four sites (singles/couples × LL/grad).
  - `scripts/enhanced/expression_constraints.py` — numpy and symbolic paths gated.
  - `scripts/bpool/recovery_test.py` — `--report` default points at `RURO_recovery_test_results_v2_raw.md`.

- **Commit B — execution log (this document and Phase 0 verifier):**
  - `docs/France_case/P3a/execution_logs/Bpool/RURO_recovery_test_results_v2.md` (this file).
  - `docs/France_case/P3a/execution_logs/Bpool/RURO_recovery_test_results_v2_raw.md` (raw harness output).
  - `docs/France_case/P3a/execution_logs/Bpool/recovery_v2_console.log` (full live trace).
  - `scripts/bpool/phase0_repricing_variation.py` (Phase-0 read-only verifier).

These are awaiting user confirmation; no `git commit` has been run.
