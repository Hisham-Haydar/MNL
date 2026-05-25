# JMP NC Pilot — JAX Optimizer-Benchmark Authorization v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: optimizer-benchmark authorization, narrow.** Authorizes only
a **limited** JAX optimizer benchmark from `theta_CONOPT`, in **float64**, capped
at 10–20 iterations, single start, to test whether the vectorized autodiff path
can *optimize* (not just evaluate). It is **not** production optimization, **not**
verdict-grade, and produces **no** Hessian/SEs, welfare, SA2, or promotion.
M1-clean 2016 active; corrected pooled P3a unaffected.

---

## 1. Purpose

To verify that the validated vectorized likelihood is *optimizable* — that a
gradient optimizer started at the CONOPT optimum stays put (or improves
slightly) without diverging, NaN-ing, or chasing float noise — establishing the
JAX path as a viable optimizer backend before any full optimization is
authorized. This is a controlled, short, single-start probe, not a re-estimation.

---

## 2. Current vectorized-likelihood status

The cleanup/validation slice passed (qualified PASS, v2):

- Both CONOPT oracle starts load correctly: LL = −16,527.1421831733; |Δ| across
  starts = 3.64e-11.
- NumPy LL at `theta_CONOPT` = −16,527.0669688818 (|Δ| vs oracle 0.0752); JAX
  (float32) −16,527.0664062500 (|Δ| 0.0758); NumPy-vs-JAX 5.63e-4.
- **JAX full-vector gradient at `theta_CONOPT`: all 35 finite, norm 6.1028.**
- 0.075 gap classified as formula-equivalence (not exact identity).
- No optimization/CONOPT/welfare/SA2/promotion run.

Both preconditions the architecture decision required — **faithful formula** and
**finite gradient** — are now satisfied. That is what unlocks this benchmark.

---

## 3. Why optimizer benchmarking is now allowed

The architecture decision (§10–§12) gated optimization behind two conditions:
(a) the vectorized LL reproduces the CONOPT formula, and (b) its gradient is
finite at `theta_CONOPT`. Both are met (§2). A *limited* benchmark is the minimal
next probe: does the optimizer **move sanely** from a known optimum? If it sits
near `theta_CONOPT` with a non-deteriorating LL under tight caps, the JAX path is
a viable optimizer and a later full-optimization authorization is justified. If
it diverges or NaNs, that surfaces a problem cheaply, before any production run.

---

## 4. What this benchmark can answer

- Does a gradient optimizer started at `theta_CONOPT` **stay near it** (the LL is
  already near-optimal, so it should barely move)?
- Are the objective and gradient **finite throughout** a short optimization (not
  just at the start)?
- Does the optimizer **complete or stop cleanly** under caps without divergence?
- **Per-iteration wall time** for the JAX optimize path — the throughput number
  that decides whether this backend replaces GAMSPy generation at scale.
- Does the LL **improve** off the CONOPT point (it may, slightly — float64 vs
  CONOPT precision), and if so, which parameters moved.

---

## 5. What this benchmark cannot answer

- **Not a re-estimation / new optimum.** 10–20 iterations from the optimum is a
  stability probe, not a fresh fit; any "improvement" is precision-boundary, not
  an economics result.
- **No inference.** No Hessian, no SEs, no cluster-robust SEs.
- **Not verdict-grade**; not welfare; not the W1-vs-two-group decision.
- **Not a scaling result** (still couples-only 2016, 900 alts).
- Does not validate JAX optimization *from cold starts* (single start from the
  optimum only).

---

## 6. Required precision mode

**float64, mandatory.** Set at import, before any JAX array is created:

```python
import jax
jax.config.update("jax_enable_x64", True)
```

- **Attempt JAX float64 first.** The residual 0.075 LL gap is already present in
  the NumPy float64 evaluation and is classified in the v2 equivalence report as
  an external CONOPT/reporting and accumulation precision boundary, not as a
  float32-only artifact. However, the JAX finite-gradient check was float32 and
  showed a non-trivial `beta_l0_m` component near a known optimum. L-BFGS-B on a
  float32 objective near an optimum could chase rounding noise rather than
  signal. Therefore float64 is required for the LL and the gradient used by the
  optimizer.
- **If JAX x64 is unavailable or fails to enable, HALT before optimizer
  benchmarking** (HJ-X64). Do not fall back to float32 optimization.
- A **float32 fixed-theta LL/gradient smoke check** may be reported **as
  diagnostic only** — **no float32 optimization is authorized.**

---

## 7. Input precomputed object

`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`
— loc4-complete; 2,577 × 900; chosen at position 0; EPS-floored consumption;
123 HN-POS flagged rows. Read-only.

---

## 8. Theta source

**Start only from `theta_CONOPT`** = the start-1 (`warm_P3a`) 35-parameter
vector from
`Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json`.

- **Do not start from YAML defaults.**
- **Do not run multiple starts** (single start only).
- The benchmark begins at the known optimum by design — the question is
  stability, not search.

---

## 9. Optimizer choice

**L-BFGS-B (scipy.optimize.minimize, method="L-BFGS-B")** driven by a JAX
**value-and-gradient** function (`jax.value_and_grad`, float64), or an equivalent
JAX/scipy L-BFGS-B. The optimizer consumes the JAX-AD gradient (not finite
differences). No other optimizer; no Adam unless explicitly substituted and
documented (L-BFGS-B is the default and preferred here).

---

## 10. Bounds and parameter transformation

Respect the **same parameter bounds as the pilot/CONOPT spec**
(`estimation_spec_nc_pilot_couples_2016.yaml` `optimization.bounds`): the Box-Cox
`theta_l_*` in [−8.0, 0.95], `beta_c` in [0.05, 50], `sigma` in [0.1, 20],
`beta_ll` in [0, 10], the region/occupation/wage/hours bounds as listed, etc.
`theta_c` stays **fixed at 0.0** (not optimized). No new parameter transformation
is introduced beyond what the spec/CONOPT used; if a transform is needed for
L-BFGS-B box handling, document it and confirm it leaves `theta_CONOPT` feasible.

---

## 11. Iteration and wall-time caps

- **Max iterations: 10–20** (L-BFGS-B `maxiter` in [10, 20]). Document the exact
  value.
- **Wall-time cap:** an **explicit external watchdog** around the whole benchmark
  if available; **otherwise document its absence** and rely on the low maxiter.
  (Per-iteration JAX eval is ~sub-second to low-seconds vs CONOPT's 18-min solve,
  so 10–20 iters is minutes — but the watchdog is the belt-and-suspenders guard.)
- If neither the maxiter cap nor any time bound can be enforced, **halt before
  the optimizer** (HJ-CAP).

---

## 12. Acceptance criteria

The benchmark **passes** iff all hold:

1. **Initial LL** equals the v2 vectorized LL within tolerance (≈ −16,527.067,
   |Δ| small — confirms the float64 start matches the validated eval).
2. **All gradients finite at start** (re-confirm in float64).
3. **Optimizer completes or stops cleanly** under the caps (no hang, no crash).
4. **No NaN/Inf** objective or gradient at any iteration.
5. **Final LL does not deteriorate** (final LL ≥ initial LL − tiny tolerance; it
   should hold or improve, never worsen materially).
6. **Parameter movement from `theta_CONOPT` is reported** (per-parameter Δ, and
   ‖Δθ‖).
7. **If final LL improves materially, report which parameters moved — and do NOT
   interpret economically.** Any improvement is a precision-boundary or
   optimizer-path artifact at a single start, not a result.

---

## 13. Required diagnostics

- Initial vs final LL; |Δ| of initial LL vs the v2 LL.
- Gradient norm at start and at finish; finiteness throughout.
- Iteration count; termination message/status; per-iteration and total wall time.
- Per-parameter Δ from `theta_CONOPT`; ‖Δθ‖₂.
- Whether any parameter hit a bound.
- The float32 smoke check (diagnostic only), if reported.

---

## 14. Halt conditions

| Halt | Condition |
|---|---|
| **HJ-X64** | JAX float64 (`jax_enable_x64`) unavailable or fails to enable. Halt before optimizer; do NOT optimize in float32. |
| **HJ-START** | Start theta is anything other than `theta_CONOPT` (start-1), or multiple starts attempted. |
| **HJ-CAP** | maxiter not in [10,20], or neither maxiter nor a time bound enforceable. |
| **HJ-NAN** | NaN/Inf objective or gradient at any iteration. Halt and report the iterate. |
| **HJ-DETERIORATE** | Final LL materially worse than initial (optimizer moved away from the optimum) — report as a failure to investigate, not a result. |
| **HJ-SCOPE** | Any Hessian, SE, cluster-robust SE, welfare, SA2, promotion, multi-start, cold-start, denser-product, pooled, or P3a action. |
| **HJ-MUT** | Overwriting the v1/v2 equivalence reports, the oracle JSONs, the pkl, or any production/pilot data; un-documented edit to the fixed-theta equivalence script. |

Any fired halt → stop, write the report up to the halt, await direction.

---

## 15. What is authorized

- Setting JAX float64; the float32 smoke check (diagnostic only).
- A **single** L-BFGS-B optimization from `theta_CONOPT`, JAX value-and-gradient,
  spec bounds, maxiter 10–20, external watchdog if available.
- A new pilot-only benchmark script (e.g.
  `scripts/pilot/_run_jax_optimizer_benchmark.py`).
- The §12 acceptance checks, §13 diagnostics, and the report (§17).
- A small, **documented** import/refactor of the fixed-theta equivalence script
  if needed to reuse its LL function (no logic change).

---

## 16. What is not authorized

- Full/production optimization; multiple starts; cold starts; starts from
  defaults (HJ-START).
- float32 optimization (HJ-X64); maxiter > 20 (HJ-CAP).
- Hessian; SEs; cluster-robust SEs; welfare; SA2; promotion; M1-clean
  displacement (HJ-SCOPE).
- Denser product (1,600 alts); pooled/singles; P3a rebuild.
- Overwriting v1/v2 reports or oracle JSONs; modifying pkl/production/pilot data
  (HJ-MUT); economic interpretation of any LL improvement.

---

## 17. Required benchmark report

`Results/JMP_NC_pilot_JAX_optimizer_benchmark_report_v1.md`, covering: scope and
authorization provenance (limited benchmark, not production, not verdict-grade);
**float64 confirmation** (jax_enable_x64 set; or HJ-X64 halt); the start
(`theta_CONOPT` only, single start); optimizer (L-BFGS-B + JAX value-and-grad,
spec bounds, maxiter); the §12 acceptance criteria results (initial LL vs v2,
gradients finite at start + throughout, clean completion, no NaN/Inf, final LL
non-deteriorating, parameter movement + ‖Δθ‖, bound hits); **per-iteration and
total wall time** (the throughput signal); the float32 smoke check (diagnostic
only); halt-condition status; and required final statements (limited benchmark
only; float64; single start from theta_CONOPT; no Hessian/SE/welfare/SA2/
promotion; no economic interpretation of any LL change; M1-clean active; P3a
unaffected).

---

## 18. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. float64; single start from theta_CONOPT;
maxiter 10–20; no inference; no welfare.

```text
Work locally in my RURO/MNL codebase. LIMITED JAX OPTIMIZER BENCHMARK, FR_2016
couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md. NOT production
optimization, NOT verdict-grade.

HARD CONSTRAINTS (halt and report if any would be violated):
- float64 MANDATORY: set jax.config.update("jax_enable_x64", True) BEFORE any
  jax array. If x64 unavailable/fails -> HALT (HJ-X64). No float32 optimization.
- Start ONLY from theta_CONOPT (start_1_warm_P3a). NO defaults, NO multiple
  starts, NO cold start. (HJ-START)
- maxiter in [10,20]; external watchdog if available else document absence.
  If no cap enforceable -> HALT (HJ-CAP).
- NaN/Inf objective or gradient at any iter -> HALT (HJ-NAN).
- NO Hessian, SE, cluster-robust SE, welfare, SA2, promotion, multi-start,
  cold-start, denser-product, pooled, P3a. (HJ-SCOPE)
- Do NOT overwrite the v1/v2 equivalence reports, oracle JSONs, pkl, or any
  production/pilot data. Document any import-refactor of the equivalence script. (HJ-MUT)

Read (read-only except the new script + new report):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_JAX_optimizer_benchmark_authorization_v1.md
- scripts/pilot/_run_ll_equivalence_prototype.py (reuse the validated LL formula; create x64 arrays only after jax_enable_x64 is set; import/refactor documented)
- Results/JMP_NC_pilot_vectorized_likelihood_equivalence_v2.md (the v2 LL target)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json (theta_CONOPT)
- estimation_spec_nc_pilot_couples_2016.yaml (optimization.bounds; theta_c fixed 0.0)

STEP 1 — float64 + smoke:
- jax.config.update("jax_enable_x64", True) at top. If fails -> HALT (HJ-X64).
- Recompute LL + gradient at theta_CONOPT in float64; confirm LL ~= v2
  (-16527.067) and all 35 gradient entries finite. (Optional float32 LL/grad
  smoke check, DIAGNOSTIC ONLY.)

STEP 2 — Single benchmark optimize:
- scipy.optimize.minimize(method="L-BFGS-B", jac=JAX value_and_grad float64),
  x0 = theta_CONOPT, bounds = spec bounds (theta_l_* [-8,0.95], beta_c [0.05,50],
  sigma [0.1,20], beta_ll [0,10], etc.; theta_c FIXED 0.0 not optimized),
  maxiter in [10,20]. External watchdog around the call if available.
- Capture per-iteration LL + grad norm; total + per-iter wall time.

STEP 3 — Acceptance (authorization s.12):
- initial LL == v2 LL within tol; grads finite at start AND throughout;
  clean completion under caps; no NaN/Inf; final LL NOT materially worse;
  report per-param delta from theta_CONOPT and ||dtheta||; any bound hits.
- If final LL improves materially: report which params moved; do NOT interpret
  economically.

STEP 4 — Write NEW outputs only:
- scripts/pilot/_run_jax_optimizer_benchmark.py
- Results/JMP_NC_pilot_JAX_optimizer_benchmark_report_v1.md (authorization s.17)
- Do NOT overwrite equivalence v1/v2 or cleanup-validation reports.

THEN STOP. No Hessian, SE, welfare, SA2, promotion.

Halt conditions: HJ-X64, HJ-START, HJ-CAP, HJ-NAN, HJ-DETERIORATE, HJ-SCOPE,
HJ-MUT (authorization s.14). On any fire: STOP, write report to that point,
await direction.

End the report with required final statements (limited benchmark; float64;
single start from theta_CONOPT; no Hessian/SE/welfare/SA2/promotion; no economic
interpretation of any LL change; M1-clean active; P3a unaffected).
```

Save the report as:
`Results/JMP_NC_pilot_JAX_optimizer_benchmark_report_v1.md`

---

**Required Final Statements**

- **This authorizes only a limited JAX optimizer benchmark** — single start from
  `theta_CONOPT`, float64, maxiter 10–20 — to test optimizability, not to
  re-estimate.
- **float64 is mandatory** (`jax_enable_x64`); if unavailable, halt — **no
  float32 optimization** (a float32 smoke check is diagnostic only).
- **Start only from `theta_CONOPT`; no defaults, no multiple starts.**
- **L-BFGS-B + JAX value-and-gradient; spec bounds; `theta_c` fixed 0.0.**
- **No Hessian, SEs, cluster-robust SEs, welfare, SA2, or promotion.** Any LL
  improvement is **not** interpreted economically.
- **New benchmark script + report only;** v1/v2 equivalence reports, oracle
  JSONs, pkl, and all production/pilot data unmodified.
- M1-clean 2016 active; corrected pooled P3a unaffected.

---

*Status: JAX optimizer-benchmark authorization v1. Authorizes one float64,
single-start, capped L-BFGS-B probe from theta_CONOPT under the §14 halts;
executes nothing itself. Next: the benchmark report (§17), then — only if it
passes cleanly — a full-optimization / cold-start authorization.*
