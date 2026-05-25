# JMP NC Pilot — Diagnostic-Estimation Authorization v1

*France RURO multi-year extension | v1 | 2026-05-23*

**Document category: diagnostic-estimation authorization, narrow.** Authorizes
only the **first** NC pilot couples-only 2016 diagnostic estimation on the
precomputed object, preflight-gated. It is **not verdict-grade**, must not feed
welfare or SA2, and does not displace M1-clean 2016. No EUROMOD, GSUR, data
rebuild, full P3a estimation, welfare, SA2, or promotion. The corrected pooled
P3a track is unaffected.

---

## 1. Purpose

To run the pilot couples likelihood once (multi-start) on the
EUROMOD-priced, W1-conditioned, product-based precomputed object — the first
time the NC pilot meets the estimator — to confirm the corrected pipeline
*estimates* (objective evaluable, solver converges, parameters sane) and to
measure runtime/memory. This is a feasibility-and-sanity run, not a result.

---

## 2. Current NC pilot status

Precompute passed (10.5 s rebuild; precompute retry passed):

- Precomputed object:
  `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl`
  + `precompute_run_summary.json`.
- Source parquet: `__precompute_norm_ready.parquet` (2,319,300 rows; 2,577 ×
  900; chosen at position 0; W1 wage layer populated; `c_norm` pilot-normalized
  with EPS floor on 123 flagged rows; no scalar `draw`).
- `c_scale_pilot = 4,054.2856`; `c_scale = c_scale_pilot` in normmeta; leisure
  scales preserved (10.0).
- No EUROMOD/GSUR/estimation/welfare/SA2/promotion; production unaffected.

---

## 3. Why diagnostic estimation is now authorized

Every upstream gate is cleared: product choice set, W1 wages, EUROMOD income on
all 900 cells, true-ID merge, `is_chosen`/chosen-first, draw-resolution patch,
pilot normalization with explicit EPS floor, and a built `PrecomputedDataCouples`.
The only way to learn whether the corrected opportunity structure *estimates*
is to run the likelihood. This is gated to a single diagnostic run with a hard
preflight (§12): if the objective can't be evaluated at the start, it halts
before optimizing.

---

## 4. What this pilot estimation can answer

- Does the likelihood **evaluate** at the start on the product/W1/EPS-floored
  pilot data (finite, no NaN/inf)?
- Does the solver **converge** from ≥2 starts to a reproducible optimum?
- Are the **parameter estimates sane** (signs, magnitudes vs the old 2016
  couples baseline where comparable)?
- **Runtime/memory** at 900 alts × 2,577 couples — the budget number for the
  pooled cycle (×2.885 couples; re-check at 1,600 alts).
- First read on whether the product/W1 corrections **move** the couples
  estimates relative to the diagonal/unconditional baseline.

---

## 5. What this pilot estimation cannot answer

- **Not verdict-grade.** No SA2-readiness claim; no canonical status.
- **No welfare / decomposition** (the paper's contribution) — separate later
  slice.
- **No pooled / singles inference** (couples-only, 2016-only).
- **No final SEs** (cluster-robust SE not required here; §11).
- **Not the W1-vs-two-group decision** (that needs both draw variants estimated;
  this runs the W1 baseline).
- Nothing about the 123 EPS-floored cells' **welfare** treatment (computational
  floor only).

---

## 6. Input precomputed object

`Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl`
— the `PrecomputedDataCouples` bundle (log_c, log_l_male/female, log_wage_*,
prior, opportunity arrays, group structure 2,577 × 900, chosen at position 0).
Read-only. `precompute_run_summary.json` provides the build provenance.

---

## 7. Input metadata and normalization

`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json`
— `c_scale = c_scale_pilot = 4,054.2856`, leisure scales 10.0, the EPS-floor
record (123 rows), and the W1 calibrated `delta_occ` provenance. The estimation
consumes the precomputed object directly; the normmeta documents the
normalization the object was built under (do not re-normalize).

---

## 8. Required estimation specification

Couples-only, 2016-only, consistent with the current couples utility +
opportunity blocks:

- **Utility:** consumption + leisure (male, female) + interactions, as in the
  accepted couples spec.
- **Opportunity:** hours opportunity + wage opportunity + **`beta_occ`
  occupation-opportunity / availability-mass** + market opportunity + region,
  as in the couples opportunity block (region present in the pilot data; GSUR
  present).
- **W1 `delta_occ` are FIXED/calibrated** from the draw stage — **not** free
  structural parameters (free count unchanged, as in the spec contract). The
  occupation premium lives in the wage *draw*; `beta_occ` is the only free
  occupation parameter.
- **No singles parameters. No year effects** (2016 only) unless the pilot spec
  structurally requires them — if it would, **halt** (§16).

If no valid couples-only pilot spec exists, **create a pilot-only YAML under a
pilot path** (e.g. `scripts/pilot/specs/`); **do not alter any production
spec** or the frozen P3a YAML.

---

## 9. Pilot-only runner or wrapper

Use the production couples estimator if it can consume the precomputed pilot
object directly; otherwise a **pilot-only wrapper/runner** that calls the
production likelihood **without changing its logic**. No production estimator
code is edited in place. Outputs land under a pilot `Results/` path only.

---

## 10. Starting values

**≥2 starts:**

1. **Warm start** from the current accepted couples parameters, where the
   mapping to the pilot spec is **unambiguous**.
2. **Pilot spec defaults.**

**If the warm-start mapping is ambiguous, halt before the solver** *or* run
**spec defaults + a small perturbed-default start** (the report states which).
Do not guess a warm-start mapping.

---

## 11. Solver and convergence requirements

- Use **CONOPT/GAMSPy if the pilot runner supports it**; otherwise the
  repository-standard optimizer for the pilot likelihood.
- Convergence: solver-reported optimal/locally-optimal; reproducible objective
  across the starts (within tolerance).
- **Cluster-robust SE not required** in this first run. Hessian/SE only if
  cheap and already supported; otherwise **defer**.

---

## 12. Required pre-solver checks (preflight gate)

Before any optimization:

1. **Schema check** — precomputed object has the arrays the likelihood expects;
   group structure 2,577 × 900; chosen at position 0.
2. **Spec/parameter compatibility** — the pilot spec's free parameters map to
   the precomputed arrays; `delta_occ` fixed; no singles/year parameters
   required.
3. **Objective-at-start** — evaluate the log-likelihood at the starting
   values; **must be finite** (no NaN/inf). **If it cannot be evaluated, halt
   before optimization** (HE-OBJ).
4. **Output-path check** — pilot `Results/` path writable; no collision with
   accepted P3a outputs.

Any preflight failure → halt and report; do not optimize.

---

## 13. Required estimation outputs (pilot-only)

Under a pilot `Results/` path (not overwriting any P3a output): converged
parameter vector(s) per start, objective value(s), convergence status,
iteration count, gradient norm if available, and the run config (spec path,
starts, optimizer). Wall time + peak memory (§15).

---

## 14. Required post-estimation diagnostics (minimal)

- **Participation / hours fit** — predicted vs observed couples participation
  and hours distribution.
- **Chosen-probability distribution** — the model's probability on the chosen
  (`draw_joint==0`) alternative across couples.
- **Wage fit** — predicted vs observed accepted wages (sanity on the W1 layer).
- **Occupation distribution fit** — predicted vs observed `loc4` shares.
- **Comparison to the old 2016 couples baseline** where feasible (parameter
  signs/magnitudes; participation/hours) — flag where product/W1 moves them.

These are sanity diagnostics, not verdict diagnostics.

---

## 15. Runtime and memory capture

Record precompute-load time, preflight time, per-start solve wall time, total
wall time, and peak memory if feasible. Project the pooled couples budget
(×2.885) and note the 1,600-alt re-check is pending. This is the long-awaited
estimator-cost number.

---

## 16. Halt conditions

| Halt | Condition |
|---|---|
| **HE-OBJ** | Log-likelihood not finite at starting values (NaN/inf). Halt before optimization. |
| **HE-SPEC** | The pilot spec would require singles data, pooled-year effects, welfare objects, or production P3a paths. Halt. |
| **HE-DELTA** | `delta_occ` treated as a free structural parameter (must be fixed/calibrated). |
| **HE-WARM** | Warm-start mapping ambiguous and neither fallback (halt, or defaults + perturbed default) is taken cleanly. |
| **HE-PROD** | Any edit to a production estimator, production spec, frozen P3a YAML, or production data; any overwrite of an accepted P3a output. |
| **HE-DRAW** | A scalar `draw` written to the pilot data. |
| **HE-SCHEMA** | Precomputed object fails the schema/group-structure check. |
| **HE-STAGE** | Any attempt to run EUROMOD, GSUR, data rebuild, full P3a estimation, welfare, SA2, promotion, or M1-clean displacement; or to treat this run as verdict-grade. |

Any fired halt → stop, write the report up to the halt, await direction. Do not
work around.

---

## 17. What is authorized

- The §12 preflight gate on the precomputed object.
- Creating a pilot-only couples-2016 spec (pilot path) if none exists.
- Running the pilot couples likelihood, ≥2 starts (§10), via the production
  estimator or a logic-preserving pilot wrapper.
- Capturing the §13 outputs, §14 diagnostics, §15 runtime/memory.
- Optionally Hessian/SE only if cheap and already supported.
- The estimation report (§19).

---

## 18. What is not authorized

- EUROMOD; GSUR; data rebuild; full/pooled P3a estimation; singles; year
  effects (unless structurally required — then halt); welfare; SA2; promotion;
  M1-clean displacement.
- Free structural `delta_occ` (HE-DELTA).
- Editing production estimator/spec/P3a YAML/data; overwriting accepted P3a
  outputs (HE-PROD).
- Adding a scalar `draw` (HE-DRAW).
- Treating this run as verdict-grade or feeding it to welfare/SA2 (HE-STAGE).
- Cluster-robust SE as a requirement (deferred).

---

## 19. Required estimation report

`Results/JMP_NC_pilot_diagnostic_estimation_report_v1.md`, covering: scope and
authorization provenance (not verdict-grade); the preflight-gate results
(schema, spec compatibility, **objective-at-start finite**, output path); the
spec used (couples-only 2016; `delta_occ` fixed; `beta_occ` free; no singles/
year); the starts (warm-start mapping + fallback taken; defaults); solver +
convergence (objective, status, iterations, gradient norm, reproducibility
across starts); parameter estimates; the §14 diagnostics (participation/hours,
chosen-prob, wage, occupation, baseline comparison); **wall time + peak memory +
pooled-cycle projection**; halt-condition status; and required final statements
(not verdict-grade; no welfare/SA2/promotion; no EUROMOD/GSUR/rebuild/full-P3a;
`delta_occ` fixed; M1-clean active; P3a unaffected; diagnostic-estimation slice
only).

---

## 20. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Preflight-gated; ≥2 starts; pilot-only
outputs; stop after diagnostics.

```text
Work locally in my RURO/MNL codebase. FIRST NC PILOT DIAGNOSTIC ESTIMATION,
FR_2016 couples only. Authorized by
docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md. NOT verdict-grade.

HARD CONSTRAINTS (halt and report if any would be violated):
- Preflight FIRST. If the log-likelihood is not finite at the starting values,
  HALT before optimization. (HE-OBJ)
- delta_occ are FIXED/calibrated, NOT free structural parameters. (HE-DELTA)
- Couples-only, 2016-only. No singles params. No year effects (if the spec
  would require them -> HALT, HE-SPEC).
- Do NOT edit any production estimator, production spec, frozen P3a YAML, or
  production data; do NOT overwrite accepted P3a outputs. Pilot wrapper + pilot
  Results/ path only. (HE-PROD)
- Do NOT add a scalar 'draw'. (HE-DRAW)
- Do NOT run EUROMOD/GSUR/rebuild/full-P3a/welfare/SA2/promotion; do NOT
  displace M1-clean; do NOT treat this as verdict-grade. (HE-STAGE)
- Cluster-robust SE NOT required. Hessian/SE only if cheap and already
  supported; else defer.

Read (read-only):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed.pkl
- Data/pilot/nc_2016_couples/precomputed/precompute_run_summary.json
- Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__precompute_norm_ready__normmeta.json
- scripts/enhanced/estimation_utils.py and the couples estimator/spec it uses
  (identify the accepted couples spec for warm-start mapping)

STEP 1 — Spec:
- Use the existing couples-only spec if valid for 2016 couples. If none exists,
  CREATE a pilot-only YAML under scripts/pilot/specs/ (do NOT alter production
  specs). Utility = consumption + leisure(m,f) + interactions; opportunity =
  hours + wage + beta_occ + market + region. delta_occ FIXED. No singles/year.

STEP 2 — PREFLIGHT GATE (before any solver):
- Schema: precomputed arrays present; 2,577 groups x 900; chosen at position 0.
- Spec/param compatibility: free params map to arrays; delta_occ fixed; no
  singles/year params required (else HE-SPEC).
- Objective-at-start: evaluate LL at each start; MUST be finite. If not -> HALT
  (HE-OBJ).
- Output path writable under pilot Results/; no P3a collision.

STEP 3 — Starts (>=2):
1. Warm start from accepted couples params where mapping is UNAMBIGUOUS.
   If ambiguous -> either HALT (HE-WARM) or use defaults + small perturbed
   default; STATE which.
2. Pilot spec defaults.

STEP 4 — Solve:
- CONOPT/GAMSPy if the pilot runner supports it; else repo-standard optimizer.
- Capture per start: objective, convergence status, iterations, gradient norm,
  wall time; total wall time + peak memory if feasible.

STEP 5 — Diagnostics (minimal):
- participation/hours fit; chosen-probability distribution; wage fit;
  occupation (loc4) distribution fit; comparison to old 2016 couples baseline
  where feasible.

STEP 6 — Persist (pilot Results/ only): parameter vectors, objectives,
convergence, config. Do NOT overwrite any P3a output.

THEN STOP. No welfare, no SA2, no promotion.

Halt conditions: HE-OBJ, HE-SPEC, HE-DELTA, HE-WARM, HE-PROD, HE-DRAW,
HE-SCHEMA, HE-STAGE (authorization s.16). On any fire: STOP, write report to
that point, await direction.

Write ONE report: Results/JMP_NC_pilot_diagnostic_estimation_report_v1.md per
authorization s.19, INCLUDING wall time + peak memory + pooled-cycle projection.
End with required final statements (not verdict-grade; no welfare/SA2/promotion;
no EUROMOD/GSUR/rebuild/full-P3a; delta_occ fixed; M1-clean active; P3a
unaffected; diagnostic-estimation slice only).
```

Save the report as:
`Results/JMP_NC_pilot_diagnostic_estimation_report_v1.md`

---

## Required final statements

- **This authorizes only the first NC pilot couples-only 2016 diagnostic
  estimation** on the precomputed object, preflight-gated. **Not verdict-grade.**
- **`delta_occ` are fixed/calibrated; `beta_occ` is the free occupation-
  opportunity parameter.** No singles, no year effects.
- **Preflight halts before optimization** if the likelihood is not finite at the
  start (HE-OBJ).
- **≥2 starts** (warm from accepted couples params where unambiguous; pilot
  defaults); cluster-robust SE not required.
- **Pilot-only spec/wrapper/outputs**; no production estimator/spec/P3a YAML/data
  edited; no accepted P3a output overwritten; no scalar `draw`.
- **No EUROMOD, GSUR, rebuild, full-P3a, welfare, SA2, or promotion.** M1-clean
  2016 active; corrected pooled P3a track unaffected.

---

*Status: diagnostic-estimation authorization v1. Authorizes one preflight-gated
pilot couples likelihood run under the §16 halts; executes nothing itself. Next
document: the estimation report (§19) — the first NC pilot estimates and the
estimator-cost number.*
