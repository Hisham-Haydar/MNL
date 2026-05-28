# ACS Reparameterisation — Premise Mismatch & Re-Diagnosis (Phase 0 done, Phase 1 halted)

**Date:** 2026-05-27
**Status:** Phase 0 PASSED. Phase 1 HALTED at the user's instruction ("stop, report the
premise mismatch") after the engine inspection contradicted the task's premise.
**No spec, engine, gradient, data, or report was modified.**

---

## 0. One-paragraph summary

The task asked to reparameterise the RURO utility from an **additive** Box-Cox form to the
**ACS multiplicative-shifter** form. On inspection, **the engine is already in the ACS
multiplicative form** — `U = A_g(x)·BC(leisure) + beta_c·BC(c) + beta_ll·BC(l_m)·BC(l_f)`,
matching the R reference (`ff_calc_util`, lines 685–714) structurally. Therefore the
additive→multiplicative reparameterisation is a **no-op**: there is nothing to convert. The
scale ridge diagnosed in v1 (`beta_c`/`beta_l0_*` co-scaling → non-PD Hessian) is **intrinsic
to the ACS form itself**, present in both the additive and multiplicative writings, and it is
**also present, unfixed, in the R reference** (which estimates fully unconstrained, normalising
nothing). The genuine remedy is a **scale normalisation** (e.g. fix `beta_c = 1`), not a
form change. Decision deferred to the user with this evidence in hand.

---

## 1. Phase 0 — repricing variation (PASSED, 6/6)

Read-only verification that EUROMOD repricing produced the variation the likelihood needs.
On the engine-ready B-pool parquets:

| check | singles | couples |
|---|---|---|
| 0a within-HH std of `ils_dispy_real` | median €868/mo; **0** zero-var HH | median €1,338/mo; **0** zero-var HH |
| 0b working: dispy vs drawn earnings (Spearman) | median **0.999**, 100% positive (monotone) | median **0.998**, 100% positive |
| 0c non-working dispy across HH | 99.4% positive, cross-HH std €834 | 99.4% positive, cross-HH std €926 |

**Verdict: PASS.** The data is sound — the identification problem is NOT a data/repricing
defect; it is a parameterisation issue. (Script: `scripts/bpool/phase0_repricing_variation.py`.)

---

## 2. The premise mismatch (why Phase 1 was halted)

**Task premise:** utility is additive —
`U = beta_l0·BC_l(leisure) + (shifters·leisure_terms) + beta_c·BC_c(c)` — to be changed to
multiplicative `U = A_g(x)·BC_l(leisure) + beta_c·BC_c(c)`.

**Engine reality (already multiplicative):**
- Singles `_compute_utility_singles` (estimation_engine.py:472–519):
  ```
  beta_l_coeff = beta_l0                       # = A_g constant (alpha_0)
  for shifter: beta_l_coeff += beta_l_X * X    # + alpha_k * X_k  (age_norm, age_norm2, n_children)
  u = beta_l_coeff * bc_l + beta_c * bc_c + beta_cl * bc_c * bc_l
  ```
- Couples `_compute_utility_couples` (estimation_engine.py:1318–1393, docstring 1329–1330):
  `u_male = [beta_l0_m + Σ beta_l_X·X_m]·BC(l_m) + beta_c·BC(c)`; female analogous;
  `+ beta_ll·BC(l_m)·BC(l_f)`.

This **is** `A_g(x)·BC(leisure) + beta_c·BC(c) + interaction`, the same structure as R
`ff_calc_util` 685–714. The leisure intercept `beta_l0` already multiplies the Box-Cox
leisure term; the demographic shifters are already inside the multiplicative bracket.

**Conclusion:** the additive→multiplicative reparameterisation has effectively already been
done in the engine. Implementing it again is a no-op / rename.

### The only genuine differences vs the R reference (variable choices, not structure)
| element | R reference (685–714) | current spec |
|---|---|---|
| age in A_g | `log(dag)`, `log(dag)^2` | `age_norm`, `age_norm2` (demeaned) |
| children in A_g | age-banded `children0_3 / 4_6 / 7_9` | single `n_children` |
| regional in A_g | `regW`, `regB` | (none in preference layer; B-strict keeps them access-only) |
| leisure arg | `(168 − hours)/168` | normalised `leisure` (=80 − hours, then /l_scale) |
| consumption | `beta_c·BC(c)` free | `beta_c·BC(c)` free; `theta_c` fixed=0 (couples) |

These are variable-definition differences, not the additive-vs-multiplicative distinction
the task targeted.

---

## 3. Re-diagnosis: the ridge is intrinsic to ACS, and the R reference has it too

The v1 memo speculated the ridge might be an additive-form artifact. It is not. In
`A_g·BC(l) + beta_c·BC(c)`, the constant of `A_g` (`beta_l0` = `alpha_0`) and `beta_c` are
**both free scalar multipliers** of level terms. The data weakly pins their absolute scale →
a (near-)flat direction → the non-PD Hessian / `beta_l0_m`-to-bound signature seen in:
the B-pool recovery test, M0c_b2, and P3a-pooled (5 negative eigenvalues). See
`RURO_recovery_test_results_v1.md` and `RURO_bpool_recovery_identification_report_v1.md`.

**New evidence — the R reference does NOT normalise the scale either.**
`stijn/Ruro_estimation_new.Rmd` (lines 1498–1540):
- starting point `param_x0 <- c(rep(1,9), -10, 1, 1, …)` — the 9 `A_g` coefficients (incl.
  intercept), then `theta_l=-10`, `beta_c=1`, `theta_c=1`, all **free**;
- optimiser: **unconstrained** `optim(method="BFGS")` and `Rcgmin` — **no bounds, no fixed
  parameters, no normalisation.**

So the R reference carries the **identical** `beta_c`/`beta_l0` scale freedom. Its
"convergence" is unconstrained BFGS landing somewhere on the flat ridge (no bounds to hit,
and `optim` reports success when the gradient is small along the directions it explored —
masking the flat direction), exactly analogous to GAMSPy's "NormalCompletion" on our runs.
**The R form is not identified by a normalisation our Python spec dropped.** Both are
un-normalised; both have the ridge.

---

## 4. What this means for the decision

- **Switching to ACS does not fix the ridge** — we are already in ACS.
- **Matching the R variables (`log(age)`, age-banded children)** is a variable-choice change;
  it would NOT remove the `beta_c`/`beta_l0` scale freedom (that freedom is in the structure,
  not the age coding). It may still be desirable for fidelity to the reference, separately.
- **The actual ridge fix is a scale normalisation** — fix one scalar multiplier so the
  remaining utility weights are identified relative to it. Conventional choice:
  **`beta_c = 1`** (consumption numéraire). The engine already supports fixing a parameter to
  a compile-time constant (the `couples_fixed_box_cox_exponent` mechanism for `theta_c`);
  `beta_c` can be fixed the same way across the LL and gradient paths, singles and couples.
  Likely 58→57 free params (or keep 58 by freeing a currently-fixed quantity — a separate
  choice).

### Two open questions worth resolving before committing the normalisation
1. **Does fixing `beta_c=1` actually break the ridge here?** Verify empirically: apply it,
   re-run the recovery test (trust-constr, minutes) → expect PD Hessian + `theta*` recovery.
2. **Is `beta_c=1` the right normalisation vs. fixing a leisure intercept** (or another
   identification restriction)? An economic/governance call — `beta_c` numéraire is standard
   and keeps consumption interpretable, but it fixes the marginal utility of consumption's
   scale rather than estimating it.

---

## 5. Recommendation

1. **Do the normalisation, not a form change.** Fix `beta_c = 1` (or a chosen reference),
   re-run the recovery test to confirm PD Hessian + recovery. This is the smallest change
   that targets the actual diagnosed cause.
2. **Optionally, separately**, align the A_g variables to the R reference (`log(age)`,
   age-banded children) for fidelity — but as its own increment, not conflated with the
   scale fix.
3. **Do not** re-run the additive→multiplicative reparameterisation (no-op).

No artefacts changed. The `_2016c` couples subset prepared earlier remains available; nothing
was committed.
