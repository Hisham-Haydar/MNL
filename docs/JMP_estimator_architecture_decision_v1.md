# JMP — Estimator Architecture Decision v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: architecture decision, narrow.** Records the decision on
the estimator backend after the NC pilot diagnostic exposed GAMSPy/GAMS symbolic
**model generation** — not CONOPT optimization — as the dominant runtime cost.
**Decision: keep CONOPT/GAMSPy as a trusted oracle, and build a vectorized
autodiff likelihood as the candidate scalable estimator, gated by an
LL-equivalence prototype first.** No welfare, SA2, promotion, full JAX
optimization, denser product, or P3a rebuild is authorized here. M1-clean 2016
remains the active baseline.

---

## 1. Purpose

To decide how the RURO couples likelihood should be evaluated and optimized at
scale, given runtime evidence that the GAMSPy/GAMS path spends ~91% of wall time
in symbolic model generation. The decision must preserve the trusted CONOPT
result as an oracle while opening a path to an estimator that scales to denser
products and the pooled/singles cycle — without prematurely committing to a full
rewrite.

---

## 2. Current NC pilot estimation status

- FR_2016 **couples-only** (not pooled 2015–2017); 2,577 couples × 900 = 2,319,300
  rows; loc4-complete pkl.
- Diagnostic estimation PASS (technical feasibility): 2 starts → **LL =
  −16,527.1422**, both OptimalLocal/NormalCompletion, 24 iterations; `beta_occ_*`
  identified.
- **Not** verdict-grade, **not** welfare, **not** SA2, **not** promoted.
  M1-clean 2016 active; corrected pooled P3a unaffected.

---

## 3. What the diagnostic estimation proves

- The corrected pipeline (product / W1 / EUROMOD-joint / loc4 / EPS-floored
  consumption) **estimates** to a reproducible optimum.
- Two independent starts reach the **same** LL with parameters agreeing to
  ~1e-12 — a single reproducible local optimum.
- `beta_occ` is **identified** (non-zero, real gradients).
- The CONOPT optimum is a **trustworthy reference point** (the "oracle theta")
  against which any alternative estimator can be validated.

---

## 4. What it does not prove

- **Not an economics result.** No SEs, no inference; point estimates are
  feasibility evidence only. Several parameters diverge from P3a (`beta_E` +12.0,
  `sigma` +1.39, `beta_E_gsur` −4.15) — expected from product/W1, unexamined.
- **Not a scalable runtime.** Per-start ~3.7–3.8 h is dominated by generation,
  not solve (§5) — unworkable for denser products or the pooled scale.
- **Not the W1-vs-two-group decision; not welfare; not the 123-cell welfare
  treatment.**

---

## 5. Runtime evidence

From `solver.lst` / `solver2.lst` (the CONOPT listings), per start:

| Phase | start_1 | start_2 |
|---|---|---|
| **GAMSPy/GAMS generation time** | **12,534.1 s** (~3.48 h) | **12,271.8 s** (~3.41 h) |
| CONOPT solve (resource usage) | 1,126.5 s (~19 min) | 1,091.5 s (~18 min) |
| CONOPT time total | 1,117.1 s | 1,082.4 s |
| Total execution time | 13,672.1 s (~3.80 h) | 13,375.5 s (~3.72 h) |
| Model statistics | 1 equation, 36 variables | (same) |
| **Code length** | **368,685,287** | 368,685,287 |
| Constant pool | 9,055,657 | 9,055,657 |

**Generation is ~91% of wall time; CONOPT solve is ~8%.** The model is a single
scalar objective equation over 36 variables, but GAMS symbolically expands the
full 2,319,300-row log-likelihood into one expression tree of ~369M code units.
That symbolic build — not the nonlinear solve — is the bottleneck. **The solve
is fast; the compile is slow.**

---

## 6. Why parallel GAMSPy starts are insufficient

Parallelizing starts (the §17 hardening in the verdict memo) addresses
*wall-clock across starts*, but **each start still pays the full ~3.4–3.5 h
generation cost**. Parallelism over 2 starts at best collapses 7.5 h → ~3.8 h —
still bounded below by one generation. Worse, the cost **scales with the row
count** (the expression tree grows with observations × alternatives), so a denser
product (1,600 alts) or the pooled couples scale (×2.885) makes generation
*longer*, not shorter. Parallel starts are a constant-factor win on a cost that
grows with the problem; they do not solve the architecture. (Caching/reusing one
generated model across starts helps within a fixed problem size — see §7 — but
still doesn't bound the per-problem generation.)

---

## 7. Option A: harden the GAMSPy/CONOPT path

Keep GAMSPy/CONOPT; attack generation cost directly.

- **Parallel-safe work dirs + external watchdog** (verdict §17) — necessary
  regardless, but a constant-factor win only.
- **Reuse/cache the generated model across starts** — the model *structure* is
  identical across starts (only starting values differ), so generating once and
  re-solving from new start values could amortize generation over starts within
  one problem size. Caps the per-*problem* cost, not the per-*scale* growth.
- **Reformulate to reduce code length** — e.g. avoid the single-giant-equation
  expansion (indexed/blocked equations, externalized data) so GAMS generates a
  compact model. Uncertain payoff; deep GAMSPy-internals work.

**Verdict on A:** worth the cheap parts (watchdog, cache-across-starts) as
interim insurance, but it does not remove the generation bottleneck's growth with
problem size. Not the scalable answer on its own.

---

## 8. Option B: vectorized autodiff likelihood path

Re-implement the RURO couples log-likelihood as a **vectorized, automatically
differentiated** function (JAX or PyTorch; NumPy for reference), optimized with a
standard gradient optimizer (L-BFGS / trust-region with analytic-AD gradients).

- **No symbolic generation.** The likelihood is a compiled numeric kernel over
  arrays; gradients come from autodiff, not symbolic expansion. The ~3.4 h
  generation cost **disappears entirely**.
- **Scales with the data, not a code-length explosion.** 2.3M rows is a modest
  array workload; denser products and the pooled scale grow it linearly, not as a
  symbolic tree.
- **Must reproduce** the exact RURO index: preference block + hours + wage +
  `beta_occ` occupation-opportunity + market (GSUR/region) + `−log(prior)`, with
  market-centering and the EPS floor, all matching `gamspy_estimation_vectorized.py`.
- **Risk:** correctness. An independent re-implementation can silently differ
  (centering convention, prior-correction sign, EPS handling, loc4 reference
  coding). This risk is exactly what the §12 equivalence prototype controls.

**Verdict on B:** the scalable candidate — but only after LL-equivalence to the
CONOPT oracle is demonstrated.

---

## 9. Option C: hybrid path with CONOPT as oracle

Use both, by role:

- **CONOPT/GAMSPy = oracle.** The trusted, already-validated optimum
  (−16,527.1422 at the known theta) is the reference. CONOPT is retained for
  verdict-grade *validation* runs and as the arbiter of correctness, even if slow.
- **Vectorized autodiff = workhorse.** Once it matches the oracle, it becomes the
  scalable estimator for denser products, robustness variants, and the pooled
  cycle — with CONOPT spot-checking key configurations.

This decouples *correctness* (anchored to CONOPT) from *throughput* (the autodiff
kernel), and never throws away the trusted result.

---

## 10. Recommended architecture decision

**Adopt Option C (hybrid), built via Option B, validated against the Option A
oracle.** Concretely:

1. **CONOPT/GAMSPy is a valid oracle, not necessarily the scalable production
   estimator.** Its −16,527.1422 optimum is the reference truth.
2. **Build a vectorized autodiff likelihood (B)** as the candidate scalable
   estimator.
3. **Gate it behind an LL-equivalence prototype (§11–§12)** before any
   optimization is trusted: the autodiff LL, evaluated at the CONOPT theta, must
   reproduce −16,527.1422.
4. **Keep Option A hardening as a separate follow-on slice** (watchdog;
   cache-across-starts) for any CONOPT runs in the meantime. This decision
   records the need; it does not authorize those code changes inside the
   LL-equivalence prototype.

This is decisive about *direction* (vectorized autodiff is the scalable path)
while *risk-gating* the commitment (no full rewrite until equivalence is proven).

---

## 11. Immediate validation target

**A single number.** The vectorized-LL prototype, evaluated at the converged
CONOPT theta (the 35-parameter vector from
`Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json`,
cross-checked against the start-2 JSON), must return:

```
LL(theta_CONOPT) ≈ −16,527.1422
```

within a tight tolerance (target |Δ| < 1e-3 in LL; ideally < 1e-6 after matching
conventions). **This is the only deliverable of the first prototype.** No
optimization, no new optimum — just: does the re-implemented likelihood agree
with the oracle at the oracle's own point? If yes, the kernel is faithful and
optimization can be authorized later. If no, the discrepancy localizes a
convention bug (centering, prior sign, EPS, loc4 reference) before any scaling.

---

## 12. Required JAX/PyTorch/NumPy equivalence prototype

Scope (next technical gate, separately executed):

- **Re-implement the couples RURO LL** as a vectorized function over the
  precomputed arrays in `_loc.pkl`, matching `gamspy_estimation_vectorized.py`
  term-for-term: preference (consumption `beta_c`/`beta_ll`, leisure CES
  `theta_l_*`, age/kids shifters), hours (`beta_h_pt1/pt2/ft`), wage
  (`beta_w0/educL/educH/pexp/pexp2`, `sigma`), occupation-opportunity
  (`beta_occ_*` × loc4), market (`beta_E`, `beta_E_gsur` × gsur, `beta_E_drgn*` ×
  reg, × working), the **market-centering** step, and the **`−log(prior)`**
  correction.
- **Match conventions exactly:** EPS = 1e-12 floor on consumption/leisure;
  loc4 reference coding (codes −2/−1 → all-dummy-zero); chosen at position 0;
  group structure 2,577 × 900.
- **Evaluate at `theta_CONOPT`** and compare LL to −16,527.1422 (§11).
- **NumPy reference first** (unambiguous), then JAX or PyTorch for AD/speed; all
  three should agree at the oracle theta.
- **Read-only on the pkl;** pilot scratch only; **no optimization**, no new
  result, no welfare, no production edit.

Deliverable: a prototype report stating the LL at `theta_CONOPT` from each
backend, the |Δ| vs −16,527.1422, and — if non-matching — the localized
convention discrepancy. **Full JAX optimization is NOT authorized** by this
decision; it is a later gate contingent on equivalence passing.

---

## 13. Required GAMSPy generation-cost benchmark

In parallel (cheap, informative), measure on the existing GAMSPy path:

- **Generation time vs solve time** per start (confirm the ~12,300 s vs ~1,100 s
  split — already evidenced in `solver.lst`).
- **Generation time vs problem size** — e.g. a small subsample (say 200 couples ×
  900) to estimate how generation scales with rows, projecting the 1,600-alt and
  pooled costs.
- **Cache-across-starts feasibility** — whether one generated model can be
  re-solved from new start values without regeneration.

This quantifies exactly how much Option A hardening can and cannot buy, and
confirms the §10 decision with numbers rather than a single data point.

---

## 14. What remains blocked

- Welfare; decomposition; the 123-cell welfare treatment.
- SA2; canonical promotion; M1-clean displacement.
- Verdict-grade estimation (SEs, post-estimation review).
- **Full JAX/PyTorch optimization** (only the LL-equivalence prototype is the
  next gate).
- Denser product (1,600 alts / 40×40); pooled 2015–2017; singles; P3a rebuild.
- Any production estimator/spec/P3a edit.

---

## 15. What is authorized next

- The **LL-equivalence prototype** (§11–§12): re-implement the couples LL
  (NumPy reference + JAX/PyTorch), evaluate at `theta_CONOPT`, compare to
  −16,527.1422. Read-only pkl; pilot scratch; **no optimization.**
- A **read-only generation-cost audit** may parse existing solver listings and
  report the observed generation-vs-solve split. Any new GAMSPy hardening,
  cache-across-starts implementation, external watchdog implementation, or
  generation-vs-size run requires a separate authorization.

---

## 16. What is not authorized

- Treating NC pilot estimates as economics results; welfare; SA2; promotion;
  M1-clean displacement.
- Full JAX/PyTorch optimization or any new optimum on the vectorized path.
- Denser product (40×40 / 1,600 alts); full P3a rebuild; pooled/singles runs.
- Editing the production estimator, spec, frozen P3a YAML, or production data;
  overwriting accepted outputs.

---

## 17. Exact Claude Code audit/prototype prompt

Use **Claude Code Opus if available**; otherwise use Claude Code Sonnet. This is
a numerical architecture task. LL-equivalence only; read-only pkl; no
optimization.

```text
Work locally in my RURO/MNL codebase. ESTIMATOR LL-EQUIVALENCE PROTOTYPE,
FR_2016 couples pilot. Authorized by docs/JMP_estimator_architecture_decision_v1.md.
GOAL: re-implement the couples RURO log-likelihood as a vectorized function and
confirm it reproduces the CONOPT oracle LL at the oracle theta. NO optimization.

HARD CONSTRAINTS (halt and report if any would be violated):
- Read-only on the pkl and all data. Pilot scratch outputs only. (no mutation)
- NO optimization, NO new optimum, NO welfare, NO SA2, NO promotion. Evaluate LL
  at a FIXED theta only.
- Do NOT edit gamspy_estimation_vectorized.py or any production file.
- Do NOT run a denser product / pooled / P3a anything.

Read (read-only):
- docs/JMP_estimator_architecture_decision_v1.md
- scripts/enhanced/gamspy_estimation_vectorized.py (the AUTHORITATIVE LL: term
  structure, market-centering, -log(prior), EPS=1e-12, loc4 reference coding)
- scripts/enhanced/estimation_utils.py (precompute array semantics)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/diagnostic_rerun_summary.json
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json
  (primary theta_CONOPT source: the 35-param vector; LL = -16527.1422)
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_2_yaml_defaults/estimation_result2.json
  (cross-start confirmation; same optimum)

STEP 1 — NumPy reference LL:
- Implement L(theta) over the precomputed arrays, matching
  gamspy_estimation_vectorized.py term-for-term: preference (beta_c, beta_ll,
  leisure CES theta_l_*, age/kids), hours (beta_h_pt1/pt2/ft), wage
  (beta_w0/educL/educH/pexp/pexp2, sigma), occupation-opportunity (beta_occ_*
  x loc4), market (beta_E, beta_E_gsur x gsur, beta_E_drgn* x reg, x working),
  market-centering, -log(prior). EPS=1e-12 floors; loc4 codes -2/-1 -> all
  dummies zero; chosen at position 0; 2,577 x 900.
- Evaluate at theta_CONOPT. Report LL and |LL - (-16527.1422)|.

STEP 2 — JAX (or PyTorch) LL:
- Same function in JAX/PyTorch (for AD + speed). Evaluate at theta_CONOPT.
- Report LL, |Δ| vs oracle, and agreement with the NumPy reference.

STEP 3 — Localize any discrepancy:
- If |Δ| is not tiny, bisect by term (preference / hours / wage / occ / market /
  centering / prior) to find the divergent convention. Report which term.

THEN STOP. Do NOT optimize. Do NOT proceed to JAX optimization.

Write ONE report: Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md
with: LL at theta_CONOPT from NumPy and JAX/PyTorch; |Δ| vs -16527.1422 for each;
backend agreement; any localized convention discrepancy; wall time per LL eval
per backend (the throughput signal). End with: equivalence PASS/FAIL; no
optimization run; no welfare/SA2/promotion; M1-clean active; P3a unaffected;
LL-equivalence prototype only.
```

Save the report as:
`Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v1.md`

---

**Required Final Statements**

- **NC pilot estimates are not economics results.** No welfare, no SA2, no
  promotion; M1-clean 2016 remains the active baseline; corrected pooled P3a
  unaffected.
- **CONOPT/GAMSPy is a valid oracle, not necessarily the scalable production
  estimator.** Its −16,527.1422 optimum is the reference truth.
- **The bottleneck is symbolic model generation (~12,300 s/start, ~91% of wall
  time), not CONOPT solve (~1,100 s).** Parallel starts are a constant-factor
  win on a cost that grows with problem size — insufficient alone.
- **Decision: build a vectorized autodiff likelihood (B) as the scalable
  candidate, validated against the CONOPT oracle (C).**
- **Next gate = an LL-equivalence prototype only:** the vectorized LL at
  `theta_CONOPT` must reproduce −16,527.1422. **Full JAX optimization is not
  authorized;** neither is a 40×40/1,600-alt denser product or a P3a rebuild.

---

*Status: estimator architecture decision v1 — hybrid (CONOPT oracle + vectorized
autodiff workhorse), gated by an LL-equivalence prototype. No optimization,
welfare, SA2, or promotion authorized. M1-clean 2016 active; corrected pooled P3a
unaffected.*
