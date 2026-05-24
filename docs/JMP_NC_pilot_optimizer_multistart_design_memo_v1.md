# JMP NC Pilot — Optimizer/Multistart Design Memo v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: optimizer/multistart design memo, narrow.** Diagnoses the
HV-AGREE halt of the three-start JAX validation and specifies a **staged
optimizer-protocol diagnostic** (not production estimation) to determine whether
the cross-start disagreement is a convergence-budget/conditioning artifact or
genuine multimodality. No winner is picked; no estimate is accepted; no SE,
welfare, SA2, or promotion. M1-clean 2016 active; corrected pooled P3a
unaffected.

---

## 1. Purpose

To turn the HV-AGREE halt into a tested decision rather than an assumption. The
three starts disagreed by ~770 LL units, but **all three hit their iteration
cap** — so the disagreement may be unfinished optimization, not distinct optima.
This memo specifies a diagnostic protocol to distinguish the two before any
estimate is accepted or the JAX path is declared production-ready.

---

## 2. Current validation status

The three-start validation halted at HV-AGREE (by contract — correct behavior):

| Start | θ source | Final LL | Cap hit |
|---|---|---|---|
| A | `theta_CONOPT` | −16,526.99362655 | maxiter 150 |
| B | pilot defaults | −17,296.73821497 | maxiter 200 |
| C | perturbed `theta_CONOPT` | −16,527.63457774 | maxiter 150 |

- Cross-start LL spread ≈ **769.7** (≫ 0.01 agreement threshold) → HV-AGREE
  fired; **no winner picked** (contract §13).
- JAX float64; no NaN/Inf; no CONOPT/GAMSPy/SE/welfare/SA2/promotion.
- `beta_l0_m` hit its lower bound in A and C, classified ACTIVE_CONSTRAINT/corner
  by the projected-gradient diagnostic.

---

## 3. What HV-AGREE means

It means the three starts **did not converge to the same point** within
tolerance, so the validation **cannot certify** the JAX optimizer reproduces a
single optimum. The contract correctly **withholds a verdict** and forbids
selecting the best-LL start as "the" estimate. The optimizer protocol is not yet
validated; that is the only firm conclusion.

---

## 4. What HV-AGREE does NOT mean

- It does **not** mean the model is multimodal. **All three starts hit their
  maxiter cap** (150/200/150) — none reported gradient/step convergence — so the
  disagreement is at least as consistent with **unfinished optimization** as with
  distinct basins.
- It does **not** mean Start A or C is correct (they're closest to the oracle,
  but cap-truncated and bound-hit — not validated optima).
- It does **not** mean Start B's basin is real (it may simply be far from the
  optimum and under-budgeted from a cold start).
- It does **not** condemn the JAX path — the kernel and gradients are sound
  (benchmark PASS); this is an **optimizer-protocol** problem, not a likelihood
  problem.

---

## 5. Evidence from Start A (theta_CONOPT)

Started at the oracle point (LL −16,527.067), moved to **−16,526.994** — i.e. it
*improved* ~0.07 off the CONOPT iterate (consistent with the benchmark's +0.072)
and kept going to maxiter 150 without converging. `beta_l0_m` → lower bound 1e-6
(ACTIVE_CONSTRAINT). So even from the oracle, L-BFGS-B at 150 iters is **still
moving** — the cap, not convergence, stopped it. This is the strongest single
signal that the budget is too short.

---

## 6. Evidence from Start B (pilot defaults)

Cold start from YAML defaults reached only **−17,296.74** at maxiter 200 — ~770
LL **worse** than A/C. Defaults are far from the optimum (the CONOPT run itself
started defaults at LL −24,393 and took 24 CONOPT iterations to reach
−16,527). L-BFGS-B from a poor cold start at 200 iters plausibly **hasn't
arrived yet** — this is the classic cold-start-under-budget pattern, not
evidence of a separate optimum.

---

## 7. Evidence from Start C (perturbed theta_CONOPT)

Perturbed near-oracle start reached **−16,527.635** at maxiter 150 — close to A
(within ~0.6 LL) but **not** equal, and also cap-stopped with `beta_l0_m` at the
bound. A and C are in the **same neighborhood** (~0.6 apart) but neither
finished. That A and C bracket the oracle within <1 LL while B sits 770 away is
exactly what "near-oracle starts share a basin, cold start under-budgeted" looks
like.

---

## 8. Interpretation of the Start-B failure

**Most likely a convergence-budget / cold-start problem, not multimodality —
but this must be tested, not assumed** (contract discipline). Defaults are far
from the optimum; 200 L-BFGS-B iters from there, on a possibly ill-conditioned
surface (§13), may be insufficient. The test (§17, §22) is direct: give B a
longer budget and/or an Adam warm-up and/or scaling, and see whether it reaches
the A/C basin. **Until that test runs, B's 770-LL gap is not proof of a second
optimum.**

---

## 9. Interpretation of the Start-A / Start-C basin

A and C are ~0.6 LL apart, both near the oracle, both cap-truncated, both with
`beta_l0_m` at the bound. This is consistent with a **single basin** that
neither start fully resolved within 150 iters. The test: give both more budget
and check whether they **converge to each other** (and whether `beta_l0_m`
behavior stabilizes). If A and C agree under a longer budget, the near-oracle
basin is established; B's reconciliation is then the separate question.

---

## 10. beta_l0_m active-bound issue

`beta_l0_m` (male leisure intercept) hits its lower bound 1e-6 in A and C, flagged
ACTIVE_CONSTRAINT by the projected gradient. **Not interpreted economically here**
(contract HV-ECON). Two things to disentangle, and they interact with the
optimizer problem:

- The bound-hit may be **real** (the LL genuinely wants `beta_l0_m` at/below the
  floor — a corner solution, a substantive identification finding for later spec
  review), **or**
- an artifact of **incomplete convergence** (the optimizer is mid-trajectory and
  `beta_l0_m` is transiting toward the bound but the run was cut at maxiter).

These cannot be separated until the optimizer converges. So the `beta_l0_m`
verdict is **deferred** until the protocol is validated (§18) — accepting it as a
corner solution now would conflate a convergence artifact with an economic
result.

---

## 11. Optimizer protocol problem

The core issue: **the iteration budget is too short to certify convergence.** All
three starts hit their cap; none reported L-BFGS-B success
(gradient/step-tolerance termination). A validation that asks "do starts agree?"
is meaningless if no start has actually converged. The protocol must either (a)
budget enough iterations that starts reach a tolerance-based stop, or (b)
diagnose why L-BFGS-B isn't converging (conditioning, §13).

---

## 12. Starting-value protocol problem

Mixing a near-oracle start (A), a perturbed near-oracle start (C), and a distant
cold start (B) in one agreement test **conflates two distinct questions**:
(i) *do near-oracle starts converge to the same optimum?* (a basin-uniqueness
check), and (ii) *can a cold start reach that optimum?* (a recovery check). These
need **different budgets and different success criteria** and should be **staged
separately** (§17), not judged by one cross-start tolerance.

---

## 13. Parameter scaling and conditioning issue

The parameters span ~7 orders of magnitude in scale: `beta_w_pexp2` ~ 6e-4,
`beta_l0_m` ~ 1e-2, `beta_E` ~ 9.6, `beta_E_gsur` ~ −5.3. L-BFGS-B's inverse-
Hessian approximation conditions poorly when parameters and gradients differ by
orders of magnitude — the benchmark's final gradient already showed
`beta_w_pexp2` at +8.8 alongside near-zero others. **Ill-conditioning would
explain slow convergence from any start** and is independently testable via
parameter scaling (§16). This is a leading candidate cause distinct from
multimodality.

---

## 14. Candidate strategy 1: longer L-BFGS-B budget

Re-run A, B, C with a substantially **larger maxiter** (e.g. 500–2,000) and
tolerance-based termination, to see whether each reaches an L-BFGS-B *success*
stop (not a cap). **Cheapest, most direct test.** If A and C converge to each
other and B closes most of the gap, the problem was budget. If they stall with
large gradients, conditioning (§16) is implicated.

---

## 15. Candidate strategy 2: Adam (or gradient warm-up) before L-BFGS-B

For the cold start (B) especially: run a first-order optimizer (Adam, modest
learning rate) for a few hundred steps to get into the basin, **then** hand off
to L-BFGS-B for final convergence. Adam is robust to poor conditioning and bad
initialization where L-BFGS-B struggles; the L-BFGS-B finish gives the precise
optimum. Tests whether B's failure is "can't find the basin from cold" (warm-up
fixes) vs "different basin" (warm-up doesn't).

---

## 16. Candidate strategy 3: parameter scaling / transformed optimization

Rescale parameters to comparable magnitude (e.g. divide each by its CONOPT-scale,
or optimize in a normalized space) so L-BFGS-B's curvature approximation
conditions well; invert the scaling for reporting. Directly tests the §13
conditioning hypothesis. If scaled optimization converges where unscaled didn't,
conditioning was the cause — and scaling becomes part of the production protocol.

---

## 17. Candidate strategy 4: near-oracle multistart before cold-start validation

**Stage the validation.** First establish basin-uniqueness with **near-oracle
starts only** (`theta_CONOPT` + several small perturbations): if they all converge
to one point under an adequate budget, the near-oracle optimum is validated.
**Then, separately**, run the **cold-start recovery test** (defaults, with the
warm-up/scaling tools) as its own question. Only after both pass does formal
multistart acceptance make sense. This separates "is there a well-defined optimum
near the oracle?" from "can we find it from anywhere?".

---

## 18. Recommended next optimizer protocol

**Staged, diagnostic (not production):**

1. **Stage 1 — near-oracle basin test:** A (`theta_CONOPT`) + C (perturbed
   `theta_CONOPT`) + 1–2 more small perturbations, with a **large budget**
   (maxiter ~1,000–2,000, tolerance-based stop). **Question:** do they converge
   to the same point (LL within ~1e-2, θ within tolerance up to `beta_l0_m`)?
2. **Stage 2 — cold-start recovery test:** B (defaults) with, in order, (a)
   longer L-BFGS-B; (b) Adam warm-up → L-BFGS-B; (c) parameter scaling.
   **Question:** does B reach the Stage-1 basin under any of these?
3. **Stage 3 — `beta_l0_m` verdict:** only once a start *converges* (tolerance
   stop, not cap), re-assess whether `beta_l0_m` is a genuine corner (deferred
   from §10).
4. Formal multistart acceptance is a **later** gate, after Stages 1–2.

Same model, data, bounds, `theta_c` fixed 0.0 throughout. JAX float64.

---

## 19. Acceptance criteria for the next run

The **diagnostic** run (not production) succeeds if it **answers** the two
questions, whichever way:

- **Convergence achieved:** at least the near-oracle starts reach a **tolerance-
  based** L-BFGS-B stop (not a maxiter cap) — so "convergence" is meaningful.
- **Basin test resolved:** Stage-1 starts either agree (→ near-oracle optimum
  validated) or genuinely disagree *after* adequate budget (→ multimodality is
  now actually evidenced, not assumed).
- **Cold-start test resolved:** B either reaches the basin under longer-budget /
  warm-up / scaling (→ budget/conditioning was the cause) or demonstrably cannot
  (→ escalate to a multimodality/specification memo).
- **`beta_l0_m` behavior reported** at a *converged* point (corner vs transient).
- No winner is forced; a clean "still disagrees after adequate budget" is a
  valid, informative outcome.

---

## 20. What is authorized next

- A **diagnostic optimizer-protocol run** (Stages 1–2, §18): near-oracle basin
  test (large budget) and cold-start recovery test (longer L-BFGS-B; Adam warm-up
  → L-BFGS-B; parameter scaling), JAX float64, same model/data/bounds, `theta_c`
  fixed 0.0.
- Recording per-start: termination type (tolerance vs cap), iters, LL trajectory,
  gradient norm, `beta_l0_m` behavior, cross-start agreement, runtime.
- A diagnostic report (§22 output).

---

## 21. What is not authorized

- Picking a winner from the halted validation; accepting A/B/C as estimates;
  interpreting `beta_l0_m` economically (HV-ECON).
- Declaring multimodality before the longer-budget/warm-up/scaling tests run.
- Treating A/C as accepted estimates before the protocol is validated.
- SEs/Hessian (beyond cheap-optional diagnostic), welfare, SA2, promotion,
  M1-clean displacement.
- Denser product (40×40/1,600), pooled, singles, P3a rebuild.
- Production optimization; formula/data/bound changes; un-documented kernel edit.

---

## 22. Exact Claude Code task for the next diagnostic

Use **Claude Code (Sonnet)**, local. Diagnostic optimizer-protocol run; JAX
float64; staged; no production, no inference, no welfare.

```text
Work locally in my RURO/MNL codebase. OPTIMIZER-PROTOCOL DIAGNOSTIC, FR_2016
couples pilot. Authorized by
docs/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md. DIAGNOSTIC ONLY — NOT
production, NOT verdict-grade. Goal: determine whether the HV-AGREE disagreement
is a convergence-budget/conditioning artifact or genuine multimodality.

HARD CONSTRAINTS (halt and report if any would be violated):
- JAX float64 (jax_enable_x64=True before any array). Reuse the v2/benchmark
  kernel (documented import; no logic change). Same model, data, bounds,
  theta_c fixed 0.0.
- Do NOT pick a winner from the prior halted validation; do NOT accept A/B/C as
  estimates; do NOT interpret beta_l0_m economically.
- Do NOT declare multimodality unless B fails to reach the basin AFTER longer
  budget + Adam warm-up + scaling.
- NO SEs/Hessian (beyond a cheap optional diagnostic), welfare, SA2, promotion,
  M1-clean displacement, denser product, pooled, singles, P3a.
- Do NOT overwrite prior reports, oracle JSONs, or the pkl. New script + new
  report only.

Read (read-only except new script + new report):
- docs/JMP_NC_pilot_optimizer_multistart_design_memo_v1.md
- scripts/pilot/_run_jax_validation_estimation.py and
  scripts/pilot/_run_jax_optimizer_benchmark.py (reuse float64 kernel)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json (theta_CONOPT)
- estimation_spec_nc_pilot_couples_2016.yaml (bounds; theta_c fixed 0.0)

STAGE 1 — Near-oracle basin test (LARGE budget):
- Starts: theta_CONOPT, perturbed theta_CONOPT (seed/mag documented), +1-2 more
  small perturbations. L-BFGS-B, maxiter ~1000-2000, tolerance-based stop
  (ftol/gtol so success is possible, NOT cap-bound). float64, spec bounds.
- Record per start: termination TYPE (tolerance vs cap), iters, final LL, grad
  norm, beta_l0_m final + projected-gradient (corner vs transient), runtime.
- QUESTION: do near-oracle starts converge to the SAME point (LL within ~1e-2,
  theta within tol up to beta_l0_m)?

STAGE 2 — Cold-start recovery test (Start B = defaults), try in order:
  (a) longer L-BFGS-B (maxiter ~1000-2000, tolerance stop);
  (b) Adam (modest lr, few hundred steps) warm-up -> then L-BFGS-B;
  (c) parameter scaling (e.g. divide by CONOPT-scale) -> optimize -> invert.
- QUESTION: does B reach the Stage-1 basin under any of (a)/(b)/(c)?

STAGE 3 — beta_l0_m verdict ONLY at a CONVERGED point (tolerance stop): corner
vs transient. If nothing converged, report "deferred — no tolerance-based stop".

Report (NEW): Results/JMP_NC_pilot_optimizer_protocol_diagnostic_report_v1.md
- Stage-1 basin verdict (agree / disagree-after-adequate-budget);
- Stage-2 cold-start verdict (which of a/b/c reached the basin, or none);
- termination types (tolerance vs cap) for every run — this is the key signal;
- beta_l0_m corner-vs-transient (or deferred);
- runtime/throughput; clear statement: budget/conditioning artifact vs evidenced
  multimodality (or still-undetermined + recommended next step).

THEN STOP. No winner, no acceptance, no SE/welfare/SA2/promotion/scaling-up.

End the report: diagnostic only; no estimate accepted; beta_l0_m not interpreted
economically; M1-clean active; P3a unaffected.
```

Save the report as:
`Results/JMP_NC_pilot_optimizer_protocol_diagnostic_report_v1.md`

---

**Required final statements:**

- **No winner is picked from the halted validation;** Start A and Start C are not
  final estimates; Start B's failure is **not** treated as proof of multimodality
  until longer-budget / warm-up / scaling diagnostics run.
- **`beta_l0_m` is not interpreted economically;** its corner-vs-transient verdict
  is deferred to a *converged* (tolerance-stop) point.
- **JAX is technically viable but not yet accepted as the production estimator;**
  the optimizer protocol is unvalidated until starts converge by tolerance, not
  cap.
- **Staged protocol recommended:** (1) near-oracle basin test (large budget);
  (2) cold-start recovery test (longer L-BFGS-B / Adam warm-up / scaling);
  (3) formal multistart acceptance only after both.
- **The next run is a diagnostic optimizer-protocol run, not production
  estimation;** no SEs, welfare, SA2, or promotion.
- M1-clean 2016 active; corrected pooled P3a unaffected; prior reports/oracle/pkl
  unmodified.

---

*Status: optimizer/multistart design memo v1. HV-AGREE diagnosed as a likely
convergence-budget/conditioning issue (all starts hit caps) — to be tested, not
assumed. Authorizes a staged diagnostic optimizer-protocol run; no winner, no
estimate, no inference/welfare/SA2/promotion. M1-clean 2016 active.*
