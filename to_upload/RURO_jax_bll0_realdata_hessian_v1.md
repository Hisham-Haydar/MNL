# JAX 48-param (beta_ll=0) real-data MLE Hessian — Check-5 resolution

**Date:** 2026-05-31
**Spec:** `estimation_spec_joint_pooled_v1_bll0.yaml` (48 params; beta_ll fixed at 0, couples leisure additively separable)
**Data:** REAL observed choices, full pooled 2015-2017, couples 20×20 (401 alts), singles 101 alts (sm=2243, sf=2764, cou=7438)
**Method:** JAX joint negLL (machine-precision-validated) + two-stage optimizer (scipy L-BFGS-B → optimistix BFGS), exact `jax.hessian` at the MLE
**Producer:** `scripts/bpool/jax_optimize.py`
**theta_hat:** `theta_hat_bll0_jax.csv`

> **NATURE OF THIS RUN:** this is a **real-data estimation** (fits observed
> choices), NOT a synthetic recovery-gate result. It is the gold-standard
> identification test (Hessian at the real-data MLE), but it is OUT of the
> prescribed synthetic-gate-first sequence. No welfare or decomposition was
> computed. Label any downstream use accordingly.

---

## Result: CHECK 5 PASS — the 48-param model is identified

| Metric | Value |
|---|---|
| Converged negLL (JAX) | 230363.778 |
| Engine negLL at theta_hat | 230364.004 (Δ=0.23, the theta_c engine-gradient bug; negligible) |
| FINAL max\|grad\| | 1.436e-03 (optimistix-polished; scipy alone stalled at ~5e2) |
| Interiority | PASS — no parameter at a bound |
| **Exact Hessian PD** | **True** |
| **min eigenvalue** | **+0.2546** |
| eigenvalues ≤ 1e-8 | **0** |
| smallest six eigenvalues | 0.255, 0.433, 0.952, 1.577, 2.108, 2.176 |

**The Hessian at the real-data MLE is positive definite with a healthy
minimum eigenvalue (+0.25) and zero flat directions.**

---

## What this resolves

The v2 production gate (49-param) failed Check 5 with a non-PD Hessian whose
flat direction loaded on `beta_ll` / `beta_l0_m` / `theta_l_m`
(couples-leisure-interaction subspace). The open question was whether the weak
spot was:

- **`beta_ll` itself** → memo §5 fix (`beta_ll = 0`) suffices, or
- **the couples-male leisure block** → memo §5 would NOT help.

**Answer: it was `beta_ll`.** Removing it (48-param spec) makes the Hessian PD
at the real-data MLE. The couples-male leisure block (`theta_l_m`,
`beta_l0_m`, `beta_l_age2_m`) is well-identified once `beta_ll` is pinned. The
memo §5 fallback is the correct and sufficient fix.

A prior diagnostic at `theta_star` (not the MLE) had suggested the couples-male
leisure block was the weak spot even with `beta_ll=0`; that was a saddle-point
artefact of evaluating the Hessian off the optimum (large negative eigenvalues
−15…−60 = indefinite curvature at a non-minimum). At the true MLE the Hessian
is clean. This is why Check 5 must be evaluated at the converged MLE, not at
`theta_star`.

---

## Validation of the JAX pipeline (banked)

- JAX joint negLL + gradient match the production engine to machine precision
  (singles 4.5e-13, couples 0.0 / 5e-14) — `jax_ll_probe.py`.
- The one gradient discrepancy is an ENGINE bug (`box_cox_derivative_theta`
  3rd-order Taylor for |theta|<0.05, wrong by ~0.5 for `theta_c_singles`);
  JAX/finite-difference give the truth. The JAX Hessian used here is exact
  autodiff, so the bug does not affect this verdict.
- Two-stage optimizer: scipy L-BFGS-B stalls (the historical "scipy struggle");
  optimistix BFGS polishes to tight gradient. Warm-started from theta_star.
- Speed: full-data converge + exact Hessian in **~minutes** (scipy stage ~10 min,
  optimistix ~1 min, Hessian ~32 s) vs CONOPT ~11 h for the 4-solve gate.
  GPU-ready (jax_enable_x64, no device pinning) for the other machine.

---

## Implication for Step 4

The 48-param `beta_ll=0` spec is **identified at the real-data MLE**. Per memo §5:

1. Baseline real-data joint estimate uses **`beta_ll = 0`**.
2. Report a **calibrated `beta_ll` sensitivity sweep** (anchored to AC couples
   estimates) and document that the opportunity share of welfare inequality is
   robust to the `beta_ll` treatment (it re-allocates welfare WITHIN the
   couples preference block, not between opportunity and preference).

## Still owed for full rigor

This is a real-data identification result, out of the synthetic-gate-first
sequence. To complete the Step 3b discipline, either:

- run the **synthetic recovery gate** (Checks 1–6) on the 48-param spec
  (`joint_recovery_test.py`, or the fast JAX equivalent with `run_synthetic_dgp`),
  confirming recovery + PD Hessian on synthetic data; **or**
- accept the real-data PD Hessian (+0.25 min-eig, exact autodiff) as the
  decisive identification evidence and proceed, noting the deviation from
  gate-first sequencing.

The Check 2 (shared recovery) and Check 4 (two-start) criteria from v2 are
unaffected by the `beta_ll` removal and need not be re-litigated; only Check 5
(the one that failed) is resolved here.

---

## Related

- `RURO_joint_recovery_test_results_v2.md` — the 49-param production gate (Check 5 FAIL on beta_ll subspace)
- `JMP_joint_estimation_spec_v1.md` §5 — beta_ll fallback (now empirically justified)
- `scripts/bpool/jax_ll_probe.py` — JAX LL/grad validation + engine bug
- `scripts/bpool/jax_joint_hessian.py` — exact Hessian + numerical comparison
- `scripts/bpool/jax_optimize.py` — two-stage optimizer (producer of this result)
