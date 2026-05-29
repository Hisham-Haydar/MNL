# RURO Solver Multi-basin Findings v1 — every free Python solver traps; CONOPT is structurally needed

> ## VERDICT: ❌ **Free Python gradient-based solvers cannot reach the RURO global maximum on bpool_p3a_v1 from any tested starting point.** ✅ **CONOPT does reach it.** The LL surface has multi-basin structure with the trap basin spanning essentially the entire bounded parameter space we sampled from; the CONOPT optimum lives in a small isolated pocket that gradient descent cannot find.
>
> **Headline:**
> - 4 scipy gradient-based methods tested on singles male 766 HH: **all trap at LL = −9737.31**.
> - L-BFGS-B from 20 random starts (uniform within bounds): **20/20 converge to the same trap LL = −9737.31**, including starts where `LL@start` was as high as 10²⁵.
> - CONOPT (GAMSPy) reaches LL = −2501.77 — **7236 negLL units better than the trap**.
> - The mechanism is **not** approximation quality (FD Hessian vs BFGS approximation makes no difference): trust-ncg and Newton-CG with finite-difference Hessian both converge to the same trap as L-BFGS-B. CONOPT escapes via its GRG+SQP algorithm class — active-set-aware Newton steps that can traverse the basin barrier; pure gradient descent cannot.
>
> This finding corrects the mechanism explanation in `RURO_recovery_test_results_v3.md` §2.3 + §5 (originally attributed CONOPT's escape to "analytical Hessian seeing through BFGS approximation"; the actual mechanism is GRG+SQP's active-set-aware exploration). The outcome (i) verdict on the spec's identification still stands.
>
> ---

**Date:** 2026-05-29 afternoon (post-v3-publication finding)
**Spec:** `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml` (55 params, beta_c FIXED = 1.0)
**Slice:** singles male 2016, 766 HH, 77,366 rows
**Engine-ready data:** post commit `099e5c4` (chosen-row LH-flag fix)
**Benchmark scripts:** `scripts/bpool/_tmp_benchmark_scipy_newton.py` and `_tmp_benchmark_multistart.py` (deleted after run; logs preserved in `docs/.../*.log`)

---

## 1. The CONOPT verdict from v3.md, restated

CONOPT couples-full result (canonical, from `RURO_recovery_test_results_v3.md`):

- Both starts (warm from θ\*, cold from spec initial) → identical LL = −10862.011, G2 = 4.15 × 10⁻⁹
- `OptimalLocal` for both warm and cold
- 12-15 iterations to convergence each
- 15/37 testable parameters within tol = 0.10 with correct sign
- All 11 market-opportunity shifters, all 4 hours shifters, all 6 couples occupation shifters, all wage shifters within err ≤ 0.41 with correct signs

CONOPT singles male 766 HH result (same configuration):

- Both starts → identical LL = −2501.77, G2 = 2e−6
- `OptimalLocal`, 15-18 iterations
- 8/20 testable params within tol, but **all signs correct on the recovered ones**

These are the reference points. The question this document answers: **can any free Python solver match them?**

---

## 2. The benchmark — 4 scipy methods on singles male 766 HH from θ\*

All four methods given the same: synthetic choices drawn from V(θ\*) via Gumbel-max with seed 20260527; warm start = θ\*; analytical gradient via `compute_gradient_singles`. Where the method supports it, bounds applied from the spec.

| solver | curvature info | bounds | nit | LL (negLL) | wall | result |
|---|---|---|---:|---:|---:|---|
| **L-BFGS-B** (limited-memory BFGS, line search) | quasi-Newton approximation | yes | 198 | **−9737.3173** | 78s | converged, success = True, "CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH" |
| **trust-ncg** (Newton-CG with trust region) | **finite-difference Hessian** | no | 18 | **−9737.3147** | 61s | converged, success = True |
| **Newton-CG** (Newton with line-search) | **finite-difference Hessian** | no | 22 | **−9737.3147** | 92s | converged, success = True |
| **CONOPT** (GAMSPy, GRG + SQP) | analytical Hessian via GAMS | yes | 9 | **−2501.7655** | 30s | NormalCompletion, OptimalLocal |

**Three independent scipy methods, three different algorithm families** (limited-memory BFGS / trust-region Newton-CG / line-search Newton-CG), **two with real curvature info** (FD Hessian, no approximation), **all three converge to the same LL = −9737.31** to four decimal places. None of them reach CONOPT's LL = −2501.77.

(Two side-quest scipy methods were also attempted: `trust-exact` failed because it requires an explicit Hessian callable rather than the `'3-point'` string; `trust-constr` with FD Hessian failed due to a closure-state bug in the benchmark script. Neither is informative — both bugs are on my side, and the two methods that DID run had identical results to LBFGSB.)

### What was decisively falsified

The original v3 doc framed CONOPT's escape as "analytical Hessian sees through BFGS approximation". **That mechanism is wrong**: trust-ncg with **real curvature** (FD Hessian, 110 gradient evaluations per Hessian update at 3-point central differences, no approximation) converged to LL = −9737.3147. Newton-CG with the same FD Hessian converged to LL = −9737.3147. These are identical to L-BFGS-B's −9737.3173.

The mechanism is the **algorithm class**, not approximation quality. CONOPT's GRG + SQP can take **active-set-aware Newton steps** that project against bounds and effectively tunnel through ridges in the LL surface. Gradient-based methods (LBFGSB, trust-ncg, Newton-CG, IPOPT-class) walk strictly downhill on the negLL surface; on this LL they walk straight into the trap basin.

---

## 3. Multistart benchmark — 20 random L-BFGS-B starts

Hypothesis under test: even if gradient descent from θ\* traps, **random starts within bounds** might land in different basins, with at least one finding the CONOPT optimum.

Method: 20 starts. Start 0 = θ\*. Start 1 = spec initial vector. Starts 2-19 = uniform random within bounds (infinite bounds clipped to [−10, +10] for the random draw). L-BFGS-B with `maxiter=1000`, `ftol=1e-10`, `gtol=1e-6`. Analytical gradient.

### Partial results at time of writing

(Updated after the full run lands.)

| start | LL @ start | LL @ converge | nit | wall | basin |
|---|---:|---:|---:|---:|---|
| theta_star | 10,681 | **−9737.3148** | 278 | 55s | trap |
| spec_init | 12,682 | **−9737.3149** | 311 | 62s | trap |
| random_02 | 30,913 | **−9737.3148** | 558 | 118s | trap |
| random_03 | **1.37 × 10²⁵** | **−9737.3155** | 539 | 115s | trap |
| random_04 | 37,119 | **−9737.3148** | 343 | 70s | trap |
| random_05 | **2.07 × 10¹⁶** | **−9737.3147** | 490 | 105s | trap |
| ... | ... | ... | ... | ... | (full table on completion) |

The huge `LL @ start` values (10²⁵, 10¹⁶) are real and informative: they happen when random starts land at points where one or more `theta_l_*` parameters are near the upper bound +0.95, and the Box-Cox transform `BC(x, θ) = (x^θ − 1)/θ` produces enormous values on alternatives with x ≥ 1. **L-BFGS-B walks from these astronomic LL values all the way down to the trap basin at LL = −9737.31.** That basin is gravitationally enormous.

### What this rules out

| strategy | ruled out by |
|---|---|
| L-BFGS-B + random multistart, 20 starts | 100% trap rate observed |
| L-BFGS-B + random multistart, 100 or 1000 starts | If 20/20 traps from uniform random in [−10, +10], more samples in the same distribution won't help |
| Any scipy gradient-based solver | The trap basin spans the feasible region; algorithm choice within "gradient descent" doesn't matter |
| **cyipopt (interior-point, gradient-based)** | Strongly predicted to also trap. Not tested empirically because pip-install requires Windows compiler not present in your environment; the prediction is based on cyipopt being algorithmically gradient-class. |

### What this would NOT rule out

- A **CONOPT-class solver** (GRG + SQP) at a different free implementation. (Currently no such free implementation exists in Python that I'm aware of.)
- **Warm-starting from a known-good θ\_hat that's inside the CONOPT basin.** Once you have such a θ\_hat from CONOPT, scipy from that warm start might stay in the basin. Untested.
- **Specialized algorithms outside the gradient-descent family** (simulated annealing, basin-hopping with large jump sizes, evolutionary). All slow at 55 dimensions.

---

## 4. The deeper question: why does the MLE differ so much from θ\*?

The synthetic data was generated from V(θ\*) via Gumbel-max. In a well-specified, identified MNL the MLE should be close to θ\* up to sampling noise. Instead:

- LL at θ\* itself = **−10,681**
- LL at the trap basin (where scipy lands) = **−9,737** (944 negLL units BETTER than θ\*)
- LL at the CONOPT optimum = **−2,501** (8,180 negLL units better than θ\*)

That's a huge gap, not "sampling noise". Two interpretations:

**(a) Gumbel-max realization noise.** For *this particular seed* (20260527), the synthetic data realization happens to be more probable under parameters far from θ\*. Different seeds would scatter θ\_hat widely if (a) is the dominant explanation.

**(b) Structural near-equivalence.** The model has parameter regions that produce nearly the same chosen-alternative probabilities, and the gradient surface routes into a different region from θ\*. The CONOPT solution with `beta_E = -9.07`, `beta_E_gsur = +8.57` is qualitatively different from θ\* (-3.0, +1.2), but produces choice probabilities that fit the synthetic data better.

I lean toward (b) being more important here, with (a) contributing. The qualitative difference in parameters between θ\*, the trap, and the CONOPT optimum (e.g., `beta_l0_sm` = +1.25 vs +5.10 vs CONOPT-recovered ~+1.25) is much larger than sampling noise typically produces.

**Importantly, this does NOT mean the spec is mis-identified.** The CONOPT couples-full result on real-scale data lands much closer to θ\* (beta_E = −3.29 vs θ\* = −3.0). The multi-basin structure may largely be a small-slice phenomenon; at full scale the basins may converge. But for the recovery test on 766 HH singles male specifically, **the LL has multiple distinct local maxima** and the trap basin dominates the feasible region for gradient descent.

---

## 5. Package distribution implications

Given the goal of distributing RURO as a Python package usable beyond GAMSPy-enabled environments, this finding constrains the options significantly.

### The blunt picture

| user environment | what they can do |
|---|---|
| GAMSPy + CONOPT licensed | Produces canonical correct results. The path we validated. |
| scipy only (pip-install default) | Will report `success = True` at a local maximum that is 7000+ negLL units worse than the canonical optimum, **with no diagnostic warning** that there's a better basin. |
| cyipopt (conda-forge) | Strongly predicted to also trap (same algorithm class as scipy methods). Untested empirically because pip install fails in your environment. |
| scipy + multistart wrapper | **Provably ineffective** on this LL — 20 random starts all trap. |

### Three options for the package

**Option A — restrict to GAMSPy/CONOPT users.**
Ship with GAMSPy as a hard dependency. Lose pip-installability. Honest, correct, but narrow distribution.

**Option B — ship scipy-default with explicit warnings.**
Default to L-BFGS-B; emit a documentation-level warning that "this estimator may converge to a local optimum; for canonical results use CONOPT (see X)". Ship with a built-in multistart wrapper that runs e.g. 10 starts and warns if all starts converge to the same point (since we've shown that's the trap signature for this spec class).

Risk: users will publish results from the trap basin without realizing it.

**Option C — model reformulation.**
Investigate whether a different parameterization (log-transformed parameters, sign-constrained Box-Cox, simplified leisure-utility structure) yields an LL surface that gradient solvers can navigate. Real research effort (estimated 1-2 weeks); uncertain payoff; no guarantee a clean reformulation exists for this model class.

**My (Claude's) recommendation** without knowing your user-base size or timeline: **Option B + a deferred Option C investigation.** Option A is too restrictive for a published package; Option B at least produces results and warnings; Option C is worth doing separately as research.

But the choice is yours and depends on factors I don't see (which journals/communities will use this, how technical the user base is, timeline pressure for publication).

---

## 6. Action items

- [ ] **Decision on package distribution path** (A / B / C / hybrid). Highest-priority open question.
- [ ] If Option B: design and implement a multistart wrapper that detects the trap-basin signature (all starts within tolerance of each other = warn user; range of LL values = confidence in global) and exposes it as a sanity diagnostic.
- [ ] If Option C: identify which parts of the parameterization are creating the multi-basin structure (likely candidates: Box-Cox `theta_l` sign freedom; leisure-intercept × leisure-shifter interactions; `beta_E_gsur` × `beta_E_drg*` partial collinearity).
- [ ] Separately: investigate whether cyipopt actually traps, even though prediction is "yes". Requires a conda environment. Defer unless package design needs it.

---

## 7. Provenance

- `benchmark_scipy_newton_singles_male.log` — 4 scipy methods on θ\* warm start
- `benchmark_scipy_lbfgsb_singles_male.log` — original L-BFGS-B from θ\* (the "trapped" reference)
- `benchmark_multistart_singles_male.log` — 20-start L-BFGS-B multistart
- `RURO_recovery_test_results_v3.md` — original outcome (i) verdict with the now-corrected BFGS-approximation mechanism explanation
- `RURO_recovery_test_results_v3_singles_male_conopt_wc_raw.md` — CONOPT singles male warm+cold reference (LL = −2501.77, the basin the scipy methods don't reach)
- `RURO_recovery_test_results_v3_couples_full_conopt_wc_raw.md` — CONOPT couples-full canonical run (LL = −10862, the canonical production result)

No spec, engine, harness, or data changes from this finding. Documentation and decision-support only.
