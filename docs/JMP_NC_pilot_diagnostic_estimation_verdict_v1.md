# JMP NC Pilot — Diagnostic-Estimation Verdict v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: diagnostic-estimation verdict, narrow.** Records the
verdict on the first interpretable NC pilot couples-only 2016 diagnostic
estimation. **Verdict: PASS for technical feasibility** — the corrected
opportunity pipeline (product choice set, W1 wages, EUROMOD-priced joint
income, loc4-complete precompute) estimates cleanly and reproducibly. It is
**not** a promotion, **not** a welfare authorization, and **not** verdict-grade
inference. M1-clean 2016 remains the active baseline; corrected pooled P3a
unaffected.

---

## 1. Purpose

To classify the diagnostic-estimation rerun result and fix what it does and does
not establish, so the project has a clean decision record before the next gate.
The rerun was the first time the full corrected NC pilot pipeline met the
likelihood; this verdict states the feasibility outcome and holds every
promotion/welfare/SA2 line.

---

## 2. Current NC pilot status

End-to-end pilot pipeline complete through diagnostic estimation:

- Product choice set (30×30 = 900/couple), W1 occupation-conditioned wages,
  C′ blockwise EUROMOD income on all 900 cells, true-ID merge, `is_chosen` +
  chosen-first, draw-resolution patch, pilot normalization with explicit EPS
  floor (123 flagged rows), loc4-complete precompute.
- Diagnostic estimation: 2 starts, GAMSPy/CONOPT, both converged to identical
  LL; `beta_occ_*` identified and non-zero.
- No welfare, SA2, promotion, EUROMOD re-run, GSUR merge, or rebuild.

---

## 3. Diagnostic-estimation verdict

**PASS — technical feasibility.** The corrected NC pilot specification is
estimable: the likelihood evaluates finite at the start, the solver converges to
a local optimum from two independent starts to the **same** objective, and the
previously-dead occupation-opportunity parameters are now identified. This
establishes that the product/W1/EUROMOD-joint/loc4 pipeline produces a coherent,
solvable structural model — the question this diagnostic was authorized to
answer.

This is a **feasibility** verdict, not a **quality** or **welfare** verdict
(§4–§5).

---

## 4. What the estimation proves

- **The pipeline estimates.** End-to-end, the corrected opportunity data feeds a
  likelihood that CONOPT solves to `OptimalLocal / NormalCompletion`.
- **Reproducible optimum.** Two starts (warm-from-P3a, YAML defaults) reach
  **LL = −16,527.1422** with parameter vectors agreeing to ~1e-12 — a single,
  reproducible local optimum, not start-dependent noise.
- **`beta_occ` is identified** (§10): the six occupation-opportunity parameters
  are non-zero with real gradients — the loc4 augmentation fixed the degeneracy
  that hung the first attempt.
- **The corrections cohere.** Product choice set, W1 wages, EUROMOD joint income,
  and the EPS-floored consumption all pass through the estimator without
  producing non-finite or degenerate objectives.

---

## 5. What the estimation does not prove

- **Not verdict-grade.** No SA2-readiness claim; this is a diagnostic run.
- **No standard errors / inference.** Cluster-robust SEs were not computed; no
  parameter is interpreted as significant or not. The point estimates are
  feasibility evidence, not results.
- **Not a specification verdict.** Whether the parameter values are *economically
  right* is not established — several diverge substantially from P3a (e.g.
  `beta_E` +12.0, `sigma` +1.39, `beta_E_gsur` −4.15, `beta_w_educH` +1.90; see
  §8 note), which is **expected** given the different choice set (product vs
  diagonal) and wage draw (W1 vs unconditional), but unexamined here.
- **No W1-vs-two-group decision** (needs the two-group draw variant estimated).
- **No welfare / decomposition** — the paper's contribution — and nothing about
  the 123 EPS-floored cells' welfare treatment.
- **Not a runtime-acceptable result for scaling** (§12): per-start wall time
  ~3.7–3.8 h, dominated by GAMSPy/GAMS model generation, not CONOPT solve.

---

## 6. Input data and precomputed object

- Precomputed object: `fr_pilot_nc_2016_couples_precomputed_loc.pkl`
  (loc4-complete; the prior no-loc4 pkl was **not** used).
- Sample: **2,577 couples × 900 alternatives = 2,319,300 rows**, FR_2016
  **couples-only** — **not** pooled 2015–2017.
- Normalization: `c_scale = 4,054.2856`, `l_scale = 10.0` (pilot); 123 EPS-floored
  rows preserved; GSUR/region bit-identical to the prior pkl.

---

## 7. Solver route used

**GAMSPy/CONOPT** via `estimate_couples_vectorized_gamspy`, consuming the
loc4-complete object directly. scipy/L-BFGS-B was **not** used (HR-SCIPY clear).
CONOPT options: `iterlim=500`, `reslim=1800 s`. A **new** rerun script was
written (HR-STALE): loads only `_loc.pkl`, no runtime loc4 injection, caps set,
cites the rerun amendment.

---

## 8. Cross-start convergence

| Start | LL at start | Final LL | Status | Iterations |
|---|---|---|---|---|
| `start_1_warm_P3a` | −24,386.4468 | **−16,527.1422** | OptimalLocal / NormalCompletion | 24 |
| `start_2_yaml_defaults` | −24,393.4403 | **−16,527.1422** | OptimalLocal / NormalCompletion | 24 |

Both starts reach the **same** optimum; parameter vectors agree to ~1e-12. This
is the convergence evidence the diagnostic required. (The P3a-vs-pilot parameter
deltas are large for several parameters — expected from the product/W1 change,
and a matter for the *next, specification-grade* examination, not this
feasibility verdict.)

---

## 9. Log-likelihood result

**LL = −16,527.1422** at the converged optimum (both starts). Average
P(chosen) ≈ 0.0016 (≈ 1.5× the uniform 1/900 ≈ 0.00111 — the model places more
than uniform mass on chosen alternatives). This is reported as feasibility
evidence; no fit verdict is drawn from it here.

---

## 10. beta_occ identification status

**Identified.** The six occupation-opportunity parameters are now non-zero with
real gradients (vs the prior dead-parameter degeneracy):

| Parameter | Pilot | P3a | Δ |
|---|---|---|---|
| `beta_occ_2_cm` | −1.6173 | −1.5026 | −0.115 |
| `beta_occ_3_cm` | −2.3462 | −2.2222 | −0.124 |
| `beta_occ_4_cm` | 0.0437 | 0.4764 | −0.433 |
| `beta_occ_2_cf` | 1.0988 | 0.1134 | +0.985 |
| `beta_occ_3_cf` | 1.1090 | −0.3292 | +1.438 |
| `beta_occ_4_cf` | 0.4439 | 1.0755 | −0.632 |

Male occupation parameters are close to P3a; female ones move more — consistent
with the product choice set giving the female opportunity axis genuine
off-diagonal variation it lacked under the diagonal. This is feasibility
evidence (the parameters live and identify), not an interpretation of the
occupation-opportunity structure.

---

## 11. Treatment of the invalid scipy run

**The earlier scipy/L-BFGS-B run is invalid and non-interpretable and is
excluded from all interpretation.** It hung ~4.8 h on a degenerate 6-D manifold
(loc4 absent → `beta_occ_*` zero gradient); no result was accepted, recorded, or
promoted. The HR-STALE prohibition prevented its script from being reused. Only
the CONOPT/loc4-complete rerun is interpreted.

---

## 12. Runtime and infrastructure caveat

The result is correct but the **runtime is not yet scale-acceptable**:

- Per-start wall time ~3.7–3.8 h; total ~7.5 h (sequential, 2 starts).
- **Dominated by GAMSPy/GAMS model generation (~3.4–3.5 h/start), not CONOPT
  solve (~18 min/start).** `iterlim`/`reslim` cap the **solve**, not the
  generation — so the realized wall time exceeded `reslim=1800 s` even though
  the solve respected it. The caps worked as specified; they simply don't bound
  the generation phase.
- Starts ran **sequentially** because `ensure_local_workdir()` does
  `os.chdir()` on the shared process CWD (UNC-path workaround), so two parallel
  `Container()` calls would race on one working directory.

**Implications:** the binding cost is model generation, not optimization; and
parallelism is currently unsafe. Both must be addressed before any denser/pooled
run (§17). The pooled couples scale (×2.885 couples) and the 1,600-alt
consistency re-check are gated on this hardening, not authorized here.

---

## 13. Whether the NC pilot is technically feasible

**Yes — technically feasible.** The corrected pipeline estimates to a
reproducible optimum with identified parameters. Feasibility is established. What
remains before it could become a *result* is: standard errors/inference, the
W1-vs-two-group decision, the simulation-consistency (400/900/1,600) check, the
runtime hardening (§17), and — separately — welfare. Feasible ≠ final.

---

## 14. Whether the NC pilot replaces M1-clean

**No.** The NC pilot is **not promoted** to baseline status. **M1-clean 2016
remains the active baseline.** The **corrected pooled P3a track remains
unaffected** and proceeds independently. A feasibility PASS is not a promotion;
promotion would require verdict-grade estimation (SEs, post-estimation review,
SA2) on a spec-graduated run, none of which has occurred.

---

## 15. Whether welfare computation is authorized

**No. Welfare computation remains unauthorized.** The decomposition (the paper's
contribution) is not run on a diagnostic-grade estimate. Welfare requires a
verdict-grade parameter vector with inference and a resolved treatment of the
123 EPS-floored negative-income cells (a welfare-domain question deferred since
the HN-POS slice). **SA2 is not issued.**

---

## 16. Immediate next gate

**Infrastructure hardening (§17)** — parallel-safe GAMSPy work directories and
an external wall-clock watchdog around the whole start — is the immediate next
gate, because the runtime/parallelism limits (§12) block any denser or pooled
run. Specification-grade work (SEs, W1-vs-two-group, simulation-consistency) and
welfare sit *behind* that gate, not before it.

---

## 17. Required infrastructure-hardening task

A dedicated hardening slice (next document), covering:

1. **Parallel-safe GAMSPy work directories** — eliminate the shared-CWD race
   (`ensure_local_workdir()` `os.chdir`): give each start its own GAMS/GAMSPy
   work dir, listing, log, and scratch, so starts can run in parallel safely.
2. **External wall-clock watchdog** — a process-level timeout around the **whole
   start** (generation + solve), since `reslim`/`iterlim` bound only the CONOPT
   solve and not the dominant generation phase. The watchdog must kill and report
   a start that exceeds a set wall-clock budget.
3. **Generation-cost benchmark** — measure whether the ~3.4–3.5 h generation can
   be reduced: e.g. reused/cached GAMSPy model generation across starts (the
   model structure is identical; only starting values differ), or a corrected
   NumPy/SciPy likelihood path as an alternative. Generation, not solve, is the
   binding cost — this is where the runtime win is.

This hardening is a prerequisite for the pooled scale (×2.885 couples) and the
1,600-alt simulation-consistency re-check.

---

## 18. What remains blocked

- Welfare computation; decomposition; the 123-cell welfare treatment.
- SA2; canonical promotion; M1-clean displacement.
- Verdict-grade estimation (SEs, post-estimation review).
- W1-vs-two-group decision; simulation-consistency (400/900/1,600).
- Pooled 2015–2017 / singles / denser-product runs.
- Any production estimator/spec/P3a edit.

All gated behind the infrastructure hardening (§17) and subsequent
specification-grade authorizations.

---

## Required Final Statements

- **Diagnostic estimation: PASS for technical feasibility.** The corrected NC
  pilot pipeline estimates to a reproducible optimum (LL = −16,527.1422, both
  starts, OptimalLocal); `beta_occ_*` identified and non-zero.
- **The NC pilot is not promoted to baseline status.**
- **M1-clean 2016 remains the active baseline.**
- **Corrected pooled P3a remains unaffected.**
- **Welfare computation remains unauthorized; SA2 is not issued.**
- **The old scipy/L-BFGS-B run is invalid and excluded from interpretation.**
- **The next gate is parallel-safe GAMSPy work directories + an external
  wall-clock watchdog** (and a generation-cost benchmark) — the binding cost is
  GAMSPy model generation (~3.4–3.5 h/start), not CONOPT solve (~18 min/start).
- Feasible ≠ final: SEs, W1-vs-two-group, simulation-consistency, and welfare
  remain blocked behind the hardening gate.

---

*Status: diagnostic-estimation verdict v1 — PASS (technical feasibility). Not a
promotion, not verdict-grade, no welfare/SA2. M1-clean 2016 active; corrected
pooled P3a unaffected. Next: infrastructure-hardening authorization (parallel
GAMSPy workdirs + external watchdog + generation-cost benchmark).*
