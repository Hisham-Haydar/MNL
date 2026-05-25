# JMP NC Pilot — Vectorized-Estimator Design Contract v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: estimator design contract, narrow.** Fixes the design of
the vectorized JAX estimator and authorizes a **three-start validation
estimation** (capped, float64) to test whether the JAX path reaches the CONOPT
optimum from independent starts. It is **not** production estimation, **not**
verdict-grade, and produces **no** Hessian/SE, welfare, SA2, or promotion.
M1-clean 2016 active; corrected pooled P3a unaffected.

---

## 1. Purpose

To specify, before running, exactly how the vectorized JAX estimator is built and
validated — backend, precision, objective, bounds, transforms, starts, caps,
convergence, and bound-hit diagnostics — so the three-start validation produces
an auditable verdict on whether JAX optimization reproduces the CONOPT oracle.
The contract exists because the benchmark surfaced a bound-hit (`beta_l0_m` →
1e-6) that must be handled by design, not improvised.

---

## 2. Current evidence

The limited benchmark passed (single start from `theta_CONOPT`, float64,
maxiter=15):

- Initial LL = −16,527.0669688817; matched v2 LL to 8.73e-11; initial gradient
  all 35 finite, norm 6.1029.
- L-BFGS-B + JAX value_and_grad; final LL = −16,526.9947573048; **LL moved
  +0.0722**; **‖Δθ‖₂ = 1.23e-02**; **`beta_l0_m` hit its lower bound 1e-6**.
- Runtime 6.05 s total (~403 ms/iter) — vs CONOPT ~3.8 h/start.
- No CONOPT/GAMSPy/full-optimization/SE/welfare/SA2/promotion.

The optimizer stayed essentially at the optimum, the kernel is fast and finite —
but the `beta_l0_m` bound-hit is the open question this contract addresses.

---

## 3. Why a design contract is needed

The benchmark proved the JAX path *runs*; it did not prove it *reproduces the
oracle from independent starts*, which is the bar for using it as the estimator.
Three things need fixing in advance: (a) **multistart agreement** — do
independent starts reach the same optimum, or is the surface multimodal/bound-
dependent; (b) **the `beta_l0_m` bound-hit** — is the solution genuinely
bound-constrained (a corner solution) or just near-flat there, which changes
whether the optimum is interior and well-identified; (c) **caps and verdict
rules** — so a non-agreeing run halts to a design memo rather than being forced
to a conclusion. Writing these down now prevents post-hoc rationalization.

---

## 4. What the next validation run can answer

- Do **three independent starts** (CONOPT, defaults, perturbed) converge to the
  **same** optimum (LL and θ within tolerance)?
- Is the JAX optimum **consistent with the CONOPT oracle** (LL ≈ −16,527.07,
  θ ≈ `theta_CONOPT` up to the bound-hit parameter)?
- Is the `beta_l0_m` lower-bound hit a **genuine bound constraint** (projected
  gradient / KKT-style diagnostic) or a flat-direction artifact?
- **Per-start runtime** at the validation cap — the throughput basis for scaling.

---

## 5. What the next validation run cannot answer

- **Not verdict-grade / not production.** Three capped starts is a validation
  probe, not the final estimate.
- **No inference** (no Hessian/SE/cluster-robust SE unless cheap + documented
  optional).
- **No economics from a bound-hit solution** without a later specification
  review — a corner solution on `beta_l0_m` is a modelling question, not an
  accepted result.
- **No welfare; no W1-vs-two-group; no scaling** (still couples-only 2016, 900
  alts).
- Multimodality beyond the three starts (a fuller multistart is a separate memo
  if these three disagree).

---

## 6. Estimator architecture

Vectorized JAX likelihood (the v2-validated kernel) + scipy L-BFGS-B driven by
`jax.value_and_grad`. The LL is the couples RURO index — preference + hours +
wage + `beta_occ` occupation-opportunity + market (GSUR/region) + market-centering
− `log(prior)` — matching `gamspy_estimation_vectorized.py` term-for-term,
including the **4th-order Taylor Box-Cox** convention. No formula change from v2;
this contract governs *optimization over* that kernel, not the kernel itself.

---

## 7. Backend and precision

- **JAX, float64, mandatory** (`jax.config.update("jax_enable_x64", True)` before
  any array). If x64 unavailable → halt (HV-X64). No float32 optimization.
- `jax.value_and_grad`, JIT-compiled, float64 throughout.
- The v2 kernel is reused (documented import/refactor only; no logic change).

---

## 8. Objective function

Minimize **negative** log-likelihood `−LL(θ)` (L-BFGS-B minimizes). The LL is the
v2 vectorized couples LL evaluated over `_loc.pkl` (2,577 × 900, chosen at
position 0). The objective and its gradient must be finite at every evaluated
iterate (HV-NAN). `theta_c` is **fixed at 0.0** (not in the optimized vector).

---

## 9. Parameter vector and bounds

**35-parameter θ** in the v2 `PARAM_NAMES` order. **Bounds = the pilot CONOPT
spec** (`estimation_spec_nc_pilot_couples_2016.yaml` `optimization.bounds`)
exactly: `theta_l_*` [−8, 0.95]; `beta_c` [0.05, 50]; `beta_l0_m` **[1e-6, 50]**;
`beta_l0_f` [0.05, 50]; age/kids, hours, wage, region, occupation, `sigma`
[0.1, 20], `beta_ll` [0, 10] as listed. **No bound is widened or removed for
this validation** — the `beta_l0_m` lower bound 1e-6 stays, and a hit there is
diagnosed (§14), not engineered away.

---

## 10. Parameter transformations

None beyond what the spec/CONOPT used. L-BFGS-B handles box bounds natively, so
no log/logit reparmeterization is introduced. If any transform is added for
numerical conditioning, it must be **documented**, leave `theta_CONOPT` feasible,
and be inverted exactly for reporting θ on the native scale. `theta_c` fixed at
0.0 is the only fixed parameter.

---

## 11. Starting-value protocol

**Exactly three starts:**

- **A — `theta_CONOPT`** (start-1 `warm_P3a`, the oracle point).
- **B — pilot defaults** (`estimation_spec_nc_pilot_couples_2016.yaml`
  `initial_values`).
- **C — perturbed** `theta_CONOPT` *or* perturbed defaults (small random
  perturbation within bounds; document the seed and magnitude).

No more, no fewer. Each start runs independently (isolated logs; the pkl shared
read-only). Each start begins feasible (within bounds).

---

## 12. Optimizer protocol

- **L-BFGS-B first** (scipy.optimize.minimize, JAX value_and_grad, float64).
- **maxiter capped** (document the value; benchmark used 15 — validation may use
  a modestly higher cap, e.g. 50–200, but it must be **explicit and bounded**,
  not unlimited; HV-CAP if uncapped).
- **Wall-time cap:** external watchdog if available; else document absence and
  rely on the maxiter cap.
- If L-BFGS-B fails to converge cleanly, that is a finding for the verdict (§13),
  not a trigger to silently switch optimizer — any optimizer change is a
  documented design decision, not an in-run improvisation.

---

## 13. Convergence criteria

- A start **converges** if L-BFGS-B reports success (gradient/step tolerance met)
  **or** stops at the maxiter cap with a small projected gradient (§14).
- **Three-start agreement:** the validation **passes** only if all three starts
  reach the **same** optimum — LL within a tight tolerance (target |ΔLL| < 1e-2
  across starts) and θ within tolerance (up to the bound-hit parameter).
- **If the three starts do NOT agree, HALT the validation verdict** (HV-AGREE)
  and recommend an optimizer/multistart design memo — do **not** declare a
  winner or pick the best LL.

---

## 14. Bound-hit diagnostics

The benchmark's `beta_l0_m` → 1e-6 bound-hit is a **required diagnostic item**:

- For every start, **report which parameters hit a bound** (within tolerance of
  a bound).
- For each bound-hit, report a **projected-gradient / KKT-style diagnostic** if
  available: is the (negative) gradient pointing *into* the infeasible region
  (genuine active constraint — a corner solution) or is the parameter merely
  *near-flat* there (the LL is insensitive, so the bound is incidental)?
- **A bound-hit solution is NOT accepted as economics** without a later
  specification review (HV-ECON). `beta_l0_m` at 1e-6 may indicate the male
  leisure intercept wants to go to/below the floor — a substantive identification
  question (is the male leisure level pinned by the data, or is the parameter
  weakly identified?), not a number to report and move past.

---

## 15. Comparison to CONOPT oracle

- Compare the **selected JAX solution** (the agreed optimum, if §13 passes) to
  the CONOPT oracle: |ΔLL| vs −16,527.1422, and per-parameter |Δθ| vs
  `theta_CONOPT`.
- Expect the JAX float64 LL to sit near −16,527.07 (the v2/benchmark value), ~0.07
  above the CONOPT-reported LL — the documented external-precision boundary, not
  a discrepancy.
- The comparison is **descriptive** (does JAX reproduce the oracle), not an
  acceptance of either as the final estimate.

---

## 16. Required outputs (pilot-only)

- A validation script (e.g. `scripts/pilot/_run_jax_validation_estimation.py`) —
  new; reusing the v2 kernel (documented).
- `Results/JMP_NC_pilot_JAX_validation_estimation_report_v1.md`.
- Per-start: initial LL, final LL, gradient norm (start + final), projected-
  gradient/bound-aware diagnostic, θ_final, per-parameter Δ from start and from
  `theta_CONOPT`, bound hits, iteration count, optimizer message, per-start +
  total wall time.
- **Do not overwrite** the equivalence v1/v2, cleanup-validation, or benchmark
  reports; the oracle JSONs; or the pkl.

---

## 17. Required diagnostics

- **Three-start cross-comparison:** LL and θ across A/B/C; agreement verdict
  (§13).
- **CONOPT comparison** of the selected solution (§15).
- **Bound-hit table** with the `beta_l0_m` projected-gradient diagnostic flagged
  explicitly (§14).
- Per-start runtime + throughput vs CONOPT.
- Finiteness of objective/gradient throughout each start.
- (Optional, only if cheap and documented) Hessian/SE — otherwise deferred.

---

## 18. Halt conditions

| Halt | Condition |
|---|---|
| **HV-X64** | JAX float64 unavailable/fails. Halt; no float32 optimization. |
| **HV-START** | Other than exactly three starts (A=theta_CONOPT, B=defaults, C=perturbed), or any start infeasible. |
| **HV-CAP** | maxiter uncapped, or neither maxiter nor a time bound enforceable. |
| **HV-NAN** | NaN/Inf objective or gradient at any iterate. Halt, report the iterate. |
| **HV-AGREE** | The three starts do not converge to the same optimum (LL/θ outside tolerance). Halt the verdict; recommend an optimizer/multistart design memo. Do NOT pick a winner. |
| **HV-ECON** | Any economic interpretation of a bound-hit solution, or acceptance of it as a result, without a later specification review. |
| **HV-SCOPE** | Hessian/SE/cluster-robust SE (beyond cheap-optional), welfare, SA2, promotion, M1-clean displacement, denser product (40×40 / 1,600), pooled, singles, P3a. |
| **HV-MUT** | Overwriting prior reports, oracle JSONs, the pkl, or any production/pilot data; un-documented kernel edit. |

Any fired halt → stop, write the report up to the halt, await direction.

---

## 19. What is authorized next

- Building the validation script (reusing the v2 float64 JAX kernel, documented).
- **Exactly three** capped, float64 L-BFGS-B validation starts (A/B/C, §11).
- The §14 bound-hit diagnostics, §15 CONOPT comparison, §16–§17 outputs.
- (Optional, cheap, documented) Hessian/SE — else deferred.
- The validation report (§16).

---

## 20. What is not authorized

- Production/full optimization; more or fewer than three starts; unlimited
  iterations (HV-START/HV-CAP).
- float32 optimization (HV-X64); bound widening/removal (§9).
- Accepting/interpreting a bound-hit solution economically without specification
  review (HV-ECON).
- Hessian/SE beyond cheap-optional; welfare; SA2; promotion; M1-clean
  displacement (HV-SCOPE).
- Denser product (40×40 / 1,600 alts); pooled; singles; P3a rebuild/start.
- Overwriting prior reports/oracle/pkl; un-documented kernel change (HV-MUT).

---

## 21. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. float64; exactly three capped starts; bound
diagnostics; no inference/welfare.

```text
Work locally in my RURO/MNL codebase. JAX VALIDATION ESTIMATION (3 starts),
FR_2016 couples pilot. Authorized by
docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md. NOT production,
NOT verdict-grade.

HARD CONSTRAINTS (halt and report if any would be violated):
- float64 MANDATORY (jax_enable_x64=True before any array). If unavailable ->
  HALT (HV-X64). No float32 optimization.
- EXACTLY THREE starts: A=theta_CONOPT, B=pilot defaults, C=perturbed (document
  seed+magnitude). Not more, not fewer. Each feasible. (HV-START)
- maxiter capped + documented (e.g. 50-200, NOT unlimited); watchdog if
  available else document absence. (HV-CAP)
- NaN/Inf objective/gradient at any iterate -> HALT (HV-NAN).
- If the three starts do NOT agree (LL within ~1e-2, theta within tol up to the
  bound-hit param) -> HALT the verdict, recommend an optimizer/multistart memo;
  do NOT pick a winner. (HV-AGREE)
- Do NOT interpret a bound-hit solution economically / accept it as a result
  without later spec review. (HV-ECON)
- NO Hessian/SE (beyond cheap+documented optional), welfare, SA2, promotion,
  M1-clean displacement, denser product, pooled, singles, P3a. (HV-SCOPE)
- Do NOT overwrite prior reports, oracle JSONs, or the pkl; document any kernel
  import/refactor (no logic change). (HV-MUT)

Read (read-only except the new script + new report):
- docs/JMP_NC_pilot_vectorized_estimator_design_contract_v1.md
- scripts/pilot/_run_jax_optimizer_benchmark.py and
  scripts/pilot/_run_ll_equivalence_prototype.py (reuse the float64 JAX kernel)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json (theta_CONOPT)
- estimation_spec_nc_pilot_couples_2016.yaml (initial_values + optimization.bounds; theta_c fixed 0.0)

STEP 1 — float64 kernel: enable x64; reuse the v2 JAX LL (4th-order Taylor BC).
Build neg-LL value_and_grad (jit, float64). Confirm LL(theta_CONOPT) ~= -16527.067.

STEP 2 — Three starts (A theta_CONOPT, B defaults, C perturbed; seed+mag
documented), each L-BFGS-B with spec bounds (theta_c fixed 0.0), maxiter capped.
Per start capture: initial LL, final LL, grad norm (start+final), per-param
delta (from start AND from theta_CONOPT), bound hits, iters, optimizer message,
wall time.

STEP 3 — Bound-hit diagnostics: for every bound-hit (esp. beta_l0_m -> 1e-6),
report projected-gradient/KKT-style diagnostic if available: active constraint
(corner) vs near-flat. Flag beta_l0_m explicitly. Do NOT accept economically.

STEP 4 — Agreement + oracle comparison:
- cross-compare A/B/C (LL + theta). If they DISAGREE -> HALT verdict (HV-AGREE),
  recommend multistart memo.
- if they agree, compare the selected solution to CONOPT oracle (|dLL| vs
  -16527.1422; per-param |dtheta| vs theta_CONOPT). Descriptive only.

STEP 5 — Write NEW outputs (do not overwrite prior reports/oracle/pkl):
- scripts/pilot/_run_jax_validation_estimation.py
- Results/JMP_NC_pilot_JAX_validation_estimation_report_v1.md (per contract
  s.16-17: 3-start table, agreement verdict, CONOPT comparison, bound-hit
  table w/ beta_l0_m projected-gradient, runtime/throughput).

THEN STOP. No welfare, SE (beyond cheap-optional), SA2, promotion, scaling.

Halt conditions: HV-X64, HV-START, HV-CAP, HV-NAN, HV-AGREE, HV-ECON, HV-SCOPE,
HV-MUT (contract s.18). On any fire: STOP, write report to that point, await
direction.

End the report with required final statements (3-start float64 validation only;
agreement verdict; bound-hit diagnosed not accepted; selected-vs-CONOPT
descriptive; no welfare/SE/SA2/promotion/scaling; M1-clean active; P3a
unaffected).
```

Save the report as:
`Results/JMP_NC_pilot_JAX_validation_estimation_report_v1.md`

---

**Required Final Statements**

- **This contract fixes the vectorized JAX estimator design and authorizes
  exactly three capped, float64 L-BFGS-B validation starts** (A=theta_CONOPT,
  B=defaults, C=perturbed) — a validation probe, not production.
- **float64 mandatory; same bounds as the pilot CONOPT spec; `theta_c` fixed
  0.0; no bound widening.**
- **Three-start disagreement halts the verdict** (HV-AGREE) and triggers an
  optimizer/multistart design memo — no winner is picked.
- **The `beta_l0_m` lower-bound hit is a required diagnostic** (projected-
  gradient/KKT): a bound-hit solution is **not accepted as economics** without a
  later specification review (HV-ECON).
- **No Hessian/SE (beyond cheap-optional), welfare, SA2, promotion, denser
  product, pooled, singles, or P3a.** M1-clean 2016 active; corrected pooled P3a
  unaffected; prior reports/oracle/pkl unmodified.

---

*Status: vectorized-estimator design contract v1. Authorizes a three-start,
float64, capped JAX validation estimation under the §18 halts; executes nothing
itself. Next: the validation report (§16). If the three starts agree and the
beta_l0_m bound-hit is diagnosed clean, the path to verdict-grade estimation
(AD-Hessian SEs) opens; if they disagree, an optimizer/multistart memo precedes
any verdict.*
