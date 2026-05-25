# JMP NC Pilot — Scaled-JAX Validation Authorization v1

*France RURO multi-year extension | v1 | 2026-05-25*

**Document category: scaled-validation authorization, narrow.** Authorizes one
formal **scaled-JAX** three-start validation run — adopting the S2c scaling that
recovered the basin in the optimizer-protocol diagnostic — to test whether the
three starts now reach **tolerance-based** stops and **agree** on a single
optimum. It is **not** production estimation, **not** verdict-grade, and produces
**no** SE/Hessian (beyond cheap-optional), welfare, SA2, or promotion. M1-clean
2016 active; corrected pooled P3a unaffected.

---

## 1. Purpose

To convert the diagnostic's scaling finding into a controlled acceptance test:
under the S2c scaling, do the near-oracle starts and the cold start all converge
**by tolerance** to the **same** point, so that — for the first time — a single
NC-pilot point estimate can be accepted as numerically validated? This is the
gate that either certifies the JAX estimator or sends the 0.341-LL near-oracle
spread to a specification question.

---

## 2. Current optimizer status

From the optimizer-protocol diagnostic (and its correction):

- Unscaled long L-BFGS-B from defaults (S2a) **CAP-HIT** at −16,576.29; Adam→
  L-BFGS-B (S2b) **CAP-HIT** at −16,627.74 — neither reached the basin.
- **Scaled L-BFGS-B from defaults (S2c) reached the near-oracle basin with a
  TOLERANCE stop at LL ≈ −16,526.997** (nit=631) — the decisive result.
- Near-oracle Stage-1 starts all tolerance-stopped but spanned **0.341 LL** — no
  estimate accepted.
- `beta_l0_m` is an active lower-bound corner at every tolerance-stopped point
  (grad_ll < 0), uninterpreted economically.

The diagnosis is **conditioning/scaling, not multimodality**; scaling is the
fix and must now be applied uniformly across all three starts.

---

## 3. Why scaled validation is now required

The original validation conflated three starts under no scaling and one (the cold
start) could not converge, firing HV-AGREE. The diagnostic isolated the cause
(parameter scales spanning ~7 orders of magnitude) and the remedy (S2c scaling).
But S2c demonstrated the remedy on the **cold start alone**; it did not run all
three starts under the scaling and check **mutual agreement at tolerance**. That
is the missing test: a scaling that lets one start converge is necessary but not
sufficient — acceptance requires that **independent starts converge to the same
point** under that scaling.

---

## 4. What the scaled validation can answer

- Under S2c scaling, do **all three starts reach tolerance-based stops** (not
  maxiter caps)?
- Do they **agree** on a single optimum — LL within the documented tolerance and
  θ (native scale) within tolerance up to `beta_l0_m`?
- Does the near-oracle **0.341-LL spread collapse** below threshold once scaling
  conditions the surface?
- Is the cold-start recovery (S2c) **reproducible** as part of an agreeing set,
  not a one-off?
- Per-start runtime under scaling — the throughput basis for the production
  protocol.

---

## 5. What the scaled validation cannot answer

- **Not verdict-grade / not production.** A passed validation certifies the
  *optimizer*, not the final estimate; verdict-grade adds inference.
- **No inference** (no SE/cluster-robust SE; Hessian only if cheap + documented
  diagnostic).
- **No economics from `beta_l0_m`** — the corner is reported, never interpreted
  (specification review is a separate, later gate).
- **No welfare; no scaling-up** (still couples-only 2016, 900 alts); no W1-vs-
  two-group.
- If starts still disagree at tolerance under scaling, that escalates to a
  specification/identification question — this run surfaces it, it does not
  resolve it.

---

## 6. Scaling convention

**Adopt the S2c scaling verbatim as the baseline rule, and document the exact
35-vector used.** The S2c `scale` vector (recorded in the diagnostic's
`result_S2c.json`) is, componentwise:

```
scale[i] = max( |theta_CONOPT[i]| , 1e-3 )
```

i.e. each parameter is scaled by the absolute value of its CONOPT optimum, with a
**floor of 1e-3** to keep near-zero parameters well-conditioned. The floor binds
on exactly two entries — `beta_l_age2_f` (|θ_CONOPT| ≈ 6.3e-4 → 1e-3) and
`beta_w_pexp2` (|θ_CONOPT| ≈ 6.0e-4 → 1e-3); all other 33 entries equal
|θ_CONOPT[i]|. The optimizer works in scaled coordinates `θ̃[i] = θ[i]/scale[i]`;
**bounds are transformed consistently** (`bound̃ = bound/scale`); and **all
reporting is on the native scale** (`θ[i] = θ̃[i]·scale[i]`). The exact 35-vector
must be written into the validation report so the run is reproducible and the
scaling is not silently re-derived. The scaling is a **change of optimization
coordinates only** — it does not touch the model, the data, the bounds (in native
space), or `theta_c` (fixed 0.0).

---

## 7. Input data and objective

Same NC pilot data
(`fr_pilot_nc_2016_couples_precomputed_loc.pkl`, 2,577 × 900) and the **same
validated v2 float64 JAX likelihood kernel** (4th-order Taylor BC; preference +
hours + wage + `beta_occ` + market/GSUR/region + centering − log prior).
Objective: minimize `−LL(θ)` with θ recovered from scaled coordinates. No formula
change, no data change, no bound change (native), `theta_c` fixed 0.0.

---

## 8. Starting-value protocol

**Exactly three scaled starts:**

- **A — scaled `theta_CONOPT`.**
- **B — scaled pilot defaults** (`estimation_spec_nc_pilot_couples_2016.yaml`
  `initial_values`) — the cold start S2c recovered.
- **C — scaled perturbed `theta_CONOPT`** (or scaled perturbed defaults; document
  seed + magnitude).

Each start is mapped into scaled coordinates, run, and mapped back to native for
reporting. No more, no fewer than three.

---

## 9. Optimizer protocol

- **L-BFGS-B with parameter scaling** (scipy.optimize.minimize, JAX
  value_and_grad, float64), operating in scaled coordinates — the S2c method.
- **maxiter** large enough to permit tolerance stops (S2c converged in 631; use a
  cap ≥ ~1,500, documented), with `ftol`/`gtol` set so a **tolerance stop is
  achievable** (S2c used ftol 1e-9, gtol 1e-7).
- **Wall-time / external watchdog** per subprocess if available; else documented
  (subprocess isolation as in the diagnostic, to avoid XLA memory accumulation).
- No optimizer substitution; Adam warm-up is **not** needed (scaling alone
  recovered the basin) and is not part of this run.

---

## 10. Convergence and agreement criteria

The validation **passes** iff **both**:

1. **All three starts reach tolerance-based stops** (L-BFGS-B success /
   `TOLERANCE_STOP`), **not** maxiter caps; and
2. **They agree:** LL across A/B/C within the documented tolerance, and θ (native
   scale) within tolerance up to the `beta_l0_m` bound-hit parameter.

**LL agreement threshold:** use **0.1 LL units** as the pilot-diagnostic pass
threshold, **while also reporting against the stricter 0.01**. (The diagnostic's
near-oracle spread was 0.341 at tolerance *without* uniform scaling; the test is
whether uniform scaling brings A/B/C inside 0.1 — and ideally 0.01.) If any start
caps, or the spread exceeds 0.1, the validation **does not pass** and the result
is reported as such (no winner picked).

---

## 11. Bound-hit diagnostics

For every start, **report all bound hits** (native scale) and, for each, the
projected-gradient / KKT-style diagnostic (active-constraint/corner vs near-flat),
exactly as in the diagnostic. The scaling changes coordinates, not bounds, so a
genuine corner should persist across scaled starts — its consistency is itself
diagnostic.

---

## 12. beta_l0_m treatment

`beta_l0_m`'s lower-bound hit **must be reported** (value, native-scale gradient,
projected-gradient verdict) **but must not be interpreted economically** (HV-ECON).
It has been a stable active corner at every tolerance-stopped point so far; if it
remains so under uniform scaling at an **agreed** optimum, that *strengthens the
case for* a subsequent specification review — but the review itself is a separate,
later gate, not part of this run. No economic statement about the male leisure
intercept is made here.

---

## 13. Required outputs (pilot-only)

- A scaled-validation script (e.g.
  `scripts/pilot/_run_scaled_jax_validation.py`) — new; reusing the v2 kernel
  (documented import; no logic change); subprocess isolation.
- `Results/NC_pilot/JMP_NC_pilot_scaled_JAX_validation_report_v1.md`.
- The **exact 35-element scale vector** written into the report.
- Per-start (native scale): initial LL, final LL, termination type
  (tolerance vs cap), nit, gradient norm (start + final), θ_final, per-parameter
  Δ from `theta_CONOPT` (native), bound hits + projected-gradient verdicts,
  per-start + total runtime.
- Cross-start agreement table (LL spread vs both 0.1 and 0.01; θ agreement).
- **Do not overwrite** prior reports, oracle JSONs, or the pkl.

---

## 14. Halt conditions

| Halt | Condition |
|---|---|
| **HS-X64** | JAX float64 unavailable/fails. Halt; no float32 optimization. |
| **HS-SCALE** | Scaling vector not the documented S2c rule `max(|θ_CONOPT|,1e-3)`, or bounds/native-reporting not transformed consistently, or the exact vector not recorded. |
| **HS-START** | Other than exactly three scaled starts (A=scaled θ_CONOPT, B=scaled defaults, C=scaled perturbed). |
| **HS-CAP** | maxiter set so tolerance stops are unreachable, or uncapped. |
| **HS-NAN** | NaN/Inf objective or gradient at any iterate. Halt, report the iterate. |
| **HS-AGREE** | Starts do not all tolerance-stop, or disagree beyond 0.1 LL (native θ beyond tolerance). Report as non-pass; do NOT pick a winner; recommend a specification/identification memo. |
| **HS-ECON** | Any economic interpretation of `beta_l0_m` or acceptance of a bound-hit as a result. |
| **HS-SCOPE** | SE/cluster-robust SE; Hessian beyond cheap-documented diagnostic; welfare; SA2; promotion; M1-clean displacement; 40×40 / denser product; pooled; singles; P3a rebuild. |
| **HS-MUT** | Overwriting prior reports/oracle/pkl; model/data/bound (native) change; un-documented kernel edit. |

Any fired halt → stop, write the report up to the halt, await direction.

---

## 15. What is authorized

- One formal **scaled-JAX three-start validation** under the S2c scaling (§6),
  float64, L-BFGS-B, same data/kernel/bounds (native), `theta_c` fixed 0.0.
- The §10 convergence + agreement test (0.1 pass threshold, 0.01 also reported).
- §11 bound-hit diagnostics; §13 outputs incl. the exact scale vector.
- A **cheap, explicitly-documented** Hessian diagnostic **only if** trivially
  available — otherwise deferred (no SE either way).
- The validation report (§17).

---

## 16. What is not authorized

- Production/full optimization; more/fewer than three starts; un-scaled or
  differently-scaled runs (HS-SCALE/HS-START).
- float32 optimization (HS-X64); model/data/bound (native) changes (HS-MUT).
- SEs/cluster-robust SEs; Hessian beyond cheap-documented; welfare; SA2;
  promotion; M1-clean displacement (HS-SCOPE).
- Economic interpretation of `beta_l0_m` or any bound-hit (HS-ECON).
- 40×40 / denser product; pooled; singles; P3a rebuild.
- Overwriting prior reports/oracle/pkl; un-documented kernel change (HS-MUT).

---

## 17. Required validation report

`Results/NC_pilot/JMP_NC_pilot_scaled_JAX_validation_report_v1.md`, covering: scope and
authorization provenance (scaled validation, not production, not verdict-grade);
float64 confirmation; the **exact 35-element scale vector** and the
`max(|θ_CONOPT|,1e-3)` rule (noting the two floored entries); the three scaled
starts (A/B/C, seed/mag for C); optimizer settings (maxiter, ftol/gtol);
per-start native-scale results (initial/final LL, termination type, nit, gradient
norms, θ_final, per-parameter Δ from θ_CONOPT, runtime); the **agreement verdict**
against **both** 0.1 and 0.01 thresholds (all-tolerance-stop AND within-threshold
→ PASS; else non-pass, no winner); bound-hit table with `beta_l0_m`
projected-gradient verdict (reported, not interpreted); any cheap Hessian
diagnostic if run; halt-condition status; and required final statements
(scaled validation only; float64; three scaled starts; S2c scaling documented;
agreement verdict; `beta_l0_m` not interpreted; no SE/welfare/SA2/promotion/
scaling-up; M1-clean active; P3a unaffected).

---

## 18. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. float64; three scaled starts; S2c scaling
verbatim; tolerance-stop required; no inference/welfare.

```text
Work locally in my RURO/MNL codebase. SCALED-JAX VALIDATION (3 scaled starts),
FR_2016 couples pilot. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md. NOT production,
NOT verdict-grade.

HARD CONSTRAINTS (halt and report if any would be violated):
- float64 MANDATORY (jax_enable_x64=True before any array). If unavailable ->
  HALT (HS-X64). No float32 optimization.
- SCALING: use the S2c rule scale[i]=max(|theta_CONOPT[i]|,1e-3) VERBATIM (same
  35-vector as result_S2c.json "scale"). Optimize in scaled coords
  th~=theta/scale; transform bounds consistently; report ALL theta on NATIVE
  scale. Record the exact 35-vector in the report. Else HALT (HS-SCALE).
- EXACTLY THREE scaled starts: A=scaled theta_CONOPT, B=scaled pilot defaults,
  C=scaled perturbed (document seed+mag). (HS-START)
- maxiter large enough for tolerance stops (>=~1500; S2c took 631), ftol=1e-9
  gtol=1e-7 so TOLERANCE_STOP is achievable. If caps make tolerance unreachable
  -> HALT (HS-CAP).
- NaN/Inf objective/gradient at any iterate -> HALT (HS-NAN).
- PASS iff ALL THREE tolerance-stop AND agree within 0.1 LL (native theta within
  tol up to beta_l0_m). ALSO report the stricter 0.01. If any caps or spread>0.1
  -> non-pass, do NOT pick a winner, recommend a specification/identification
  memo. (HS-AGREE)
- beta_l0_m bound-hit REPORTED (value, native grad, projected-grad verdict) but
  NOT interpreted economically. (HS-ECON)
- NO SE/cluster-robust SE; Hessian only if cheap + explicitly documented
  diagnostic; NO welfare, SA2, promotion, M1-clean displacement, 40x40/denser,
  pooled, singles, P3a. (HS-SCOPE)
- Do NOT overwrite prior reports, oracle JSONs, or the pkl; no model/data/bound
  (native) change; document any kernel import/refactor (no logic change). (HS-MUT)

Read (read-only except new script + new report):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_scaled_JAX_validation_authorization_v1.md
- scripts/pilot/_run_optimizer_protocol_diagnostic.py (S2c scaling implementation)
  and scripts/pilot/_run_jax_validation_estimation.py (3-start harness; reuse v2 kernel)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json (theta_CONOPT -> scale vector)
- estimation_spec_nc_pilot_couples_2016.yaml (defaults + bounds; theta_c fixed 0.0)

STEP 1 — Scaling: build scale[i]=max(|theta_CONOPT[i]|,1e-3) (35-vector; confirm
it matches result_S2c.json "scale"; note floored entries beta_l_age2_f,
beta_w_pexp2). Optimize in scaled coords; transform bounds; native-scale reporting.

STEP 2 — Three scaled starts (A scaled theta_CONOPT, B scaled defaults, C scaled
perturbed; seed/mag documented). L-BFGS-B + JAX value_and_grad float64, spec
bounds (native, theta_c fixed 0.0), maxiter>=1500, ftol=1e-9 gtol=1e-7.
Per start (native): initial/final LL, term TYPE (tolerance vs cap), nit, grad
norm start+final, theta_final, per-param delta from theta_CONOPT, bound hits +
projected-grad verdict, runtime. Subprocess isolation.

STEP 3 — Agreement: ALL three tolerance-stop AND LL spread<=0.1 (native theta in
tol up to beta_l0_m) -> PASS; also report vs 0.01. Else non-pass (no winner;
recommend specification/identification memo).

STEP 4 — beta_l0_m: report native value + projected-grad verdict (corner vs flat);
DO NOT interpret economically.

STEP 5 — Write NEW outputs (do not overwrite prior reports/oracle/pkl):
- scripts/pilot/_run_scaled_jax_validation.py
- Results/NC_pilot/JMP_NC_pilot_scaled_JAX_validation_report_v1.md (authorization s.17:
  exact scale vector; 3 starts; agreement vs 0.1 AND 0.01; bound-hit table;
  runtime; halt status).

THEN STOP. No SE/welfare/SA2/promotion/scaling-up.

Halt conditions: HS-X64, HS-SCALE, HS-START, HS-CAP, HS-NAN, HS-AGREE, HS-ECON,
HS-SCOPE, HS-MUT (authorization s.14). On any fire: STOP, write report to that
point, await direction.

End the report with required final statements (scaled validation only; float64;
three scaled starts; S2c scaling rule + exact vector; agreement verdict vs 0.1
and 0.01; beta_l0_m reported not interpreted; no SE/welfare/SA2/promotion/
scaling-up; M1-clean active; P3a unaffected).
```

Save the report as:
`Results/NC_pilot/JMP_NC_pilot_scaled_JAX_validation_report_v1.md`

---

## Required Final Statements

- **This authorizes only a formal scaled-JAX validation run** — three scaled
  starts (A=scaled θ_CONOPT, B=scaled defaults, C=scaled perturbed), float64,
  L-BFGS-B with parameter scaling — using the **same NC pilot data and the same
  validated likelihood kernel.**
- **Scaling = the S2c rule `scale[i]=max(|θ_CONOPT[i]|,1e-3)`,** adopted as the
  baseline; the **exact 35-element vector is documented** in the report; the
  floor binds only on `beta_l_age2_f` and `beta_w_pexp2`. Model formula, data,
  and bounds (native) unchanged; `theta_c` fixed 0.0.
- **The validation passes only if all three starts reach tolerance-based stops
  and agree** within a documented LL/θ tolerance: **0.1 LL** as the pilot
  threshold, with **0.01 also reported.** Parameter movements reported on the
  **native scale.**
- **All bound hits reported;** **`beta_l0_m` reported but not interpreted
  economically** (HS-ECON).
- **No SEs; no Hessian unless cheap and explicitly documented as diagnostic; no
  welfare; no SA2; no promotion; no M1-clean displacement; no 40×40; no full
  P3a.**
- M1-clean 2016 active; corrected pooled P3a unaffected; prior reports/oracle/pkl
  unmodified.

---

*Status: scaled-JAX validation authorization v1. Authorizes one three-start
scaled (S2c-rule) float64 L-BFGS-B validation under the §14 halts; executes
nothing itself. PASS = all three tolerance-stop AND agree within 0.1 LL (0.01
also reported). On PASS, a single NC-pilot point estimate is numerically
validated and the next gate (beta_l0_m specification review, then verdict-grade
SEs) opens; on non-pass, a specification/identification memo precedes any
verdict. M1-clean 2016 active.*
