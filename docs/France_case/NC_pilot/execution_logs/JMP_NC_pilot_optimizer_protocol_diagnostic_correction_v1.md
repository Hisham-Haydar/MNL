# JMP NC Pilot — Optimizer-Protocol Diagnostic Correction v1

*France RURO multi-year extension | v1 | 2026-05-25*

**Document category: interpretive correction, narrow.** Corrects the summary
wording of `Results/NC_pilot/JMP_NC_pilot_optimizer_protocol_diagnostic_report_v1.md` so
it can serve as an operating document. The diagnostic's auto-generated headline
("multimodality evidenced") is **contradicted by its own Stage-2 results** and is
replaced here by the correct reading: the binding problem is **optimizer
conditioning/scaling**, and **parameter scaling is the required protocol fix**.
No estimate is accepted; `beta_l0_m` stays uninterpreted; no SE/welfare/SA2/
promotion. M1-clean 2016 active; corrected pooled P3a unaffected.

---

## 1. Purpose

To restate the optimizer-protocol diagnostic's verdict in terms its own evidence
supports, so downstream authorizations rest on the right conclusion. The data are
not in dispute — only the headline classification is — and the correct
classification (scaling/conditioning, not multimodality) changes what is
authorized next.

---

## 2. Why a correction is needed

The diagnostic report's §1 summary line reads
"NEAR-ORACLE STARTS DISAGREE AFTER LARGE BUDGET — multimodality evidenced." That
phrase is auto-generated from the Stage-1 LL-spread test alone and **ignores
Stage 2**, where the decisive result lives. Used as written, it would
mis-route the project toward a multimodality/specification investigation when the
evidence points to a fixable numerical cause. The body of the same report
already contains the correct finding; this document promotes it to the verdict.

---

## 3. What the diagnostic established

- **Scaling resolves cold-start recovery.** From the pilot defaults (initial LL
  −24,501.97), **scaled L-BFGS-B (S2c) reached the near-oracle basin with a
  TOLERANCE stop at LL ≈ −16,526.997** (nit=631). This is the central result.
- **Unscaled methods from defaults failed under the same budget:** plain long
  L-BFGS-B (S2a) **CAP-HIT** at −16,576.29 (‖g‖ 466), and Adam→L-BFGS-B (S2b)
  **CAP-HIT** at −16,627.74 (‖g‖ 2,116) — neither reached the basin.
- **Near-oracle starts do reach the basin** and now stop by **tolerance** (all
  four Stage-1 starts TOLERANCE_STOP), clustering at LL ≈ −16,527.0 to −16,527.3
  — i.e. they are in the **same neighborhood**, a large improvement over the
  cap-truncated validation run.
- The float64 JAX kernel and gradients are sound throughout (no NaN/Inf);
  subprocess isolation + watchdog held.

The contrast S2c (scaled, tolerance, basin) vs S2a/S2b (unscaled, cap, no basin),
**from the identical cold start**, isolates **conditioning/scaling** as the
operative variable.

---

## 4. What the diagnostic did NOT establish

- It did **not** establish multimodality. The Stage-1 spread (0.341 LL) coexists
  with the fact that **scaling let a distant cold start reach the basin** — the
  opposite of what a genuinely multimodal surface would show.
- It did **not** validate a single estimate. Stage-1 near-oracle starts still
  span **0.341 LL** (> 0.01), so **no point is accepted**.
- It did **not** resolve `beta_l0_m` economically (corner flag stands as a
  numerical diagnostic only).
- It did **not** authorize scaling-up, inference, or production estimation.

---

## 5. Correct interpretation of Stage 1

The four near-oracle starts (`theta_CONOPT` + three perturbations, maxiter 1,500)
**all reached tolerance-based stops** — a qualitative advance over the original
validation, where every start hit its cap. Their finals cluster between
−16,526.996 (S1_A) and −16,527.337 (S1_C3), a **0.341 LL spread**. Crucially the
larger-perturbation starts stop with **non-trivial gradient norms** (‖g‖ 14–30)
despite tolerance termination — the surface is **flat/ill-conditioned near the
optimum**, so L-BFGS-B's tolerance triggers on tiny *steps* while the gradient is
still appreciable. This is a **flat/bound-sensitive near-oracle region**, not
four distinct optima. It is, however, **not yet tight enough to accept a single
estimate**: formal *scaled* validation is required to bring the near-oracle
starts into agreement.

---

## 6. Correct interpretation of Stage 2

Stage 2 is the decisive stage and it points one way. From the **same** default
cold start:

| Variant | Method | Final LL | Termination | Basin? |
|---|---|---|---|---|
| S2a | Unscaled long L-BFGS-B (1,500) | −16,576.29 | CAP_HIT | NO |
| S2b | Adam(500)→L-BFGS-B (1,000) | −16,627.74 | CAP_HIT | NO |
| S2c | **Scaled L-BFGS-B (1,500)** | **−16,526.997** | **TOLERANCE_STOP** | **YES** |

Holding the start fixed and varying only the numerical treatment, **only scaling
reaches the basin, and it does so by tolerance** (nit=631, ‖g‖ 34). This is a
clean controlled result: the cold-start failure was a **conditioning** failure,
and **scaling is the fix**.

---

## 7. Correct classification of Start-B failure

The original validation's Start-B failure (the 770-LL gap that fired HV-AGREE) is
now classified as an **optimizer conditioning/cold-start failure, resolved by
parameter scaling** — not multimodality. Evidence: scaled L-BFGS-B from those same
defaults reaches the near-oracle basin (S2c), whereas unscaled long L-BFGS-B
(S2a) and Adam-warm-up (S2b) do not within budget. A second basin would not be
reachable simply by rescaling the parameters; reaching it by rescaling is
diagnostic of conditioning.

---

## 8. Correct classification of near-oracle disagreement

The Stage-1 0.341-LL spread is a **flat / bound-sensitive near-oracle**
phenomenon: the region around the optimum is shallow (and entangled with the
`beta_l0_m` lower bound), so independent near-oracle starts settle at slightly
different points by tolerance without having found different basins. This
**requires formal scaled validation to resolve into a single accepted estimate**;
it is **not** a basis for economic interpretation and **not** evidence of
multimodality. The correct next step is to re-run the near-oracle starts **under
the scaling that worked in S2c**, with tightened tolerances, and check whether the
spread collapses below threshold.

---

## 9. beta_l0_m active-bound status

Across **every** tolerance-stopped point (S1_A, S1_C1–C3, S2c), `beta_l0_m` sits
at its lower bound 1e-6 with a strictly negative likelihood gradient
(grad_ll ≈ −5.6 to −6.9 < 0), i.e. the projected-gradient diagnostic classifies
it a **genuine active lower-bound corner**. This is now observed at *converged*
(tolerance) points, not just cap-truncated ones, so the corner is a **stable
numerical feature** rather than a convergence transient. **It remains
uninterpreted economically** (HV-ECON): a corner on the male leisure intercept is
a substantive specification/identification question reserved for a later
specification review, not a result to report. Its consistency across all
converged starts is recorded as a diagnostic fact only.

---

## 10. Revised verdict

**The optimizer-protocol diagnostic identifies parameter conditioning/scaling —
not multimodality — as the key problem, and shows parameter scaling to be the
required optimizer-protocol fix.** Specifically: scaled L-BFGS-B recovers the
near-oracle basin from the pilot defaults with a tolerance stop at LL ≈
−16,526.997, where unscaled long L-BFGS-B and Adam→L-BFGS-B both fail under the
tested budget. The Stage-1 near-oracle starts still disagree by 0.341 LL — a
flat/bound-sensitive near-oracle issue — so **no single estimate is accepted**;
this disagreement requires **formal scaled validation**, not economic
interpretation. `beta_l0_m` is a stable active lower-bound corner at all
tolerance-stopped points but **stays economically uninterpreted**. JAX remains
**technically viable but not yet accepted as the production estimator**.

---

## 11. What remains blocked

- **No estimate accepted;** no winner picked from any stage or from the original
  validation.
- **`beta_l0_m` not interpreted economically** (HV-ECON; specification review
  required first).
- **No standard errors, Hessian, or cluster-robust SEs;** no welfare; no SA2; no
  pilot promotion; **M1-clean 2016 not displaced**.
- **No 40×40 / denser product; no pooled; no singles; no P3a rebuild.**
- No formula/data/bound changes; prior reports/oracle/pkl unmodified.

---

## 12. Next authorized gate

**Formal scaled-JAX validation authorization.** The next document authorizes a
scaled-JAX validation run that: (i) adopts the S2c scaling as the standard
conditioning; (ii) re-runs the near-oracle starts (`theta_CONOPT` + perturbations)
**and** the cold start (defaults) under that scaling with tightened tolerances and
adequate budget; (iii) tests whether the near-oracle Stage-1 spread collapses
below the agreement threshold so that a **single estimate** can be accepted; and
(iv) only at a scaled, converged, agreed point re-opens the `beta_l0_m`
corner question for a specification review. SEs/Hessian remain deferred to a
later verdict-grade gate; welfare/SA2/promotion/scaling-up remain blocked.

---

## Required Final Statements

- **The diagnostic's primary finding is optimizer conditioning/scaling, not
  multimodality;** the "multimodality evidenced" headline is superseded by this
  correction.
- **Unscaled default L-BFGS-B failed to reach the basin even at the longer
  budget** (S2a CAP_HIT, −16,576.29); **Adam→L-BFGS-B also failed** under the
  tested budget (S2b CAP_HIT, −16,627.74).
- **Scaled L-BFGS-B from defaults reached the near-oracle basin with a tolerance
  stop at LL ≈ −16,526.997** (S2c) — supporting **parameter scaling as the
  required optimizer-protocol fix.**
- **Stage-1 near-oracle starts still show a 0.341 LL spread,** so **no single
  estimate is accepted;** this is a flat/bound-sensitive near-oracle issue
  requiring **formal scaled validation**, not a basis for economic
  interpretation.
- **`beta_l0_m` is an active lower-bound corner at tolerance-stopped points but
  remains economically uninterpreted** (specification review required first).
- **No welfare, SA2, SEs, promotion, 40×40, or P3a rebuild is authorized.**
- **M1-clean 2016 remains the active baseline;** corrected pooled P3a unaffected.
- **The next gate is formal scaled-JAX validation authorization.**

---

*Status: optimizer-protocol diagnostic correction v1. Verdict corrected from
"multimodality evidenced" to "conditioning/scaling is the key problem; parameter
scaling is the required fix." Scaled L-BFGS-B recovers the basin from defaults
(tolerance stop, LL ≈ −16,526.997); near-oracle 0.341-LL spread still open → no
estimate accepted. beta_l0_m a stable corner, uninterpreted. Next: formal
scaled-JAX validation authorization. M1-clean 2016 active.*
