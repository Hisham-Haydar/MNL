# JMP NC Pilot — Diagnostic-Estimation Rerun Amendment v1

*France RURO multi-year extension | v1 | 2026-05-24*

**Document category: amendment to `docs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md`.**
Re-authorizes the first NC pilot couples-only 2016 diagnostic estimation on the
**loc4-complete** pkl, via **GAMSPy/CONOPT** (not scipy), under preflight and
capped-iteration/wall-time gates. The earlier scipy/L-BFGS-B run is **invalid and
non-interpretable**. Still **not verdict-grade**; no welfare, SA2, or promotion.
M1-clean 2016 active; corrected pooled P3a track unaffected.

---

## 1. Purpose

To run the pilot couples likelihood now that the `loc4_*` arrays exist, so the
six free `beta_occ_*` occupation-opportunity parameters are identified — using
the solver the production path actually supports (CONOPT/GAMSPy) and with
iteration/wall-time caps that prevent a repeat of the 4.8 h runaway. All spec
decisions from the base diagnostic authorization carry forward unchanged; this
amendment changes only the **input pkl**, the **solver**, and adds **explicit
caps + parallel-isolation rules**.

---

## 2. Previous diagnostic-estimation halt

The first attempt is **invalid and non-interpretable** and is not used:

- scipy / L-BFGS-B, ~17,312 CPU s (~4.8 h), no healthy convergence;
  `max_iterations: 3000` did not stop it.
- Root cause: `loc4_*` absent from the pkl → `beta_occ_*` zero gradient → a
  degenerate 6-D flat manifold the solver could not leave.
- Processes killed manually; **no result accepted, no output promoted, no
  welfare/SA2/estimation result recorded.** This amendment's report must restate
  that this run is invalid and discarded.

---

## 3. Loc4 augmentation status

The augmentation (`..._loc4_precompute_augmentation_report_v1.md`) passed all 12
validations:

- `fr_pilot_nc_2016_couples_precomputed_loc.pkl` written; prior pkl unchanged.
- `loc4_male`/`loc4_female` present; `loc4_1..4_{male,female}` present and
  **non-degenerate** (e.g. `loc4_4` mean ≈0.444, `loc4_3` ≈0.084 — all dummies
  carry both 0s and 1s).
- Off-axis product-consistency confirmed (occupation varies on a partner's own
  draw axis, constant across the other's — correct).
- GSUR/region arrays **bit-identical** to the prior pkl; 123 HN-POS EPS-floored
  rows preserved; 2,577 × 900; chosen at position 0; normalization reused
  (`c_scale = 4,054.2856`, `l_scale = 10.0`).

The object is ready for estimation.

---

## 4. Correct input artifact

**Use only** `Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl`.

**Do not use** the prior `fr_pilot_nc_2016_couples_precomputed.pkl` (no `loc4_*`
→ the original failure). The rerun must **fail loudly (HR-LOC4)** if any
`loc4_*` array is missing or degenerate in the loaded object — the same defect
must not slip through twice.

---

## 5. Solver correction

**Use GAMSPy/CONOPT.** `estimate_couples_vectorized_gamspy` in
`gamspy_estimation_vectorized.py` accepts a `PrecomputedDataCouples` object
directly (confirmed), so the pilot runner supports CONOPT — scipy was the wrong
default and is what hung.

- **scipy / L-BFGS-B is NOT authorized for this rerun.** It may be used **only**
  if the CONOPT/GAMSPy **import or license check fails** *and* the user
  **explicitly** authorizes a fallback (HR-SCIPY). Absent that, a CONOPT/GAMSPy
  failure is a halt, not a silent scipy fallback.
- Confirm `estimate_couples_vectorized_gamspy` imports and can consume the
  loc4-complete object before launch.

**Stale execution script — do NOT reuse as-is (HR-STALE).**
`scripts/pilot/_run_diagnostic_estimation.py` is stale and violates this
amendment on four counts: it (a) loads the **old no-loc4 pkl**
`fr_pilot_nc_2016_couples_precomputed.pkl`; (b) **injects `loc4_*` at runtime**
from the parquet (the HR-LOC4 / HL-INJECT failure mode); (c) calls GAMSPy/CONOPT
**without iteration/wall-time caps**; and (d) still references the **old
diagnostic authorization**, not this rerun amendment. Either write a **new**
rerun script or **replace** the stale one so that it: loads **only** `_loc.pkl`;
performs **no** runtime `loc4` injection; **verifies** `loc4_*` already present
and non-degenerate in the pkl; uses **GAMSPy/CONOPT only**; **sets and reports**
the iteration + wall-time caps before launch and **halts before the solver if
caps cannot be enforced**; uses **isolated** output/log/listing/work dirs per
parallel start, else runs **sequentially and reports why**; and cites **this
amendment** as its authorization. Reusing the stale script unmodified is itself
a halt (HR-STALE).

---

## 6. Start protocol

**≥2 starts:**

1. **Mapped warm start** from accepted couples parameters **if the mapping is
   unambiguous** (the pilot spec differs from the accepted spec — product vs
   diagonal, W1 wages, calibrated `delta_occ`; map only where unambiguous).
2. **Pilot defaults**, or **perturbed defaults** if the warm-start mapping is
   ambiguous.

If the warm-start mapping is ambiguous, either run defaults + a perturbed
default, or halt (HR-WARM) — do not guess a mapping. The report states which
path was taken.

**Parallel vs sequential (HR-ISO):** parallel starts are authorized **only if**
each start has an **isolated** output directory, solver log, listing file,
GAMS/GAMSPy work directory, and temp files. **If isolation cannot be
guaranteed, run sequentially.** No mutable file is shared across starts; the
loc4 pkl may be shared **read-only**. The report records: parallel or
sequential, number of workers, per-start wall time, total wall time.

---

## 7. Iteration and wall-time caps

Before launch, set and **verify**:

- a **solver iteration cap** (CONOPT iteration / major-iteration limit), and
- a **wall-time cap** (per start) that aborts a stuck solve in minutes, not
  hours.

**If the caps cannot be enforced or verified on the CONOPT/GAMSPy path, halt
before the solver (HR-CAP).** The exact solver options used (iteration limit,
resource/time limit, tolerances) must be documented in the report. The 4.8 h
runaway is the failure this gate exists to prevent.

---

## 8. Required pre-solver checks

Per start, before any optimization:

1. **Artifact check** — loaded pkl is the `_loc.pkl`; `loc4_*` present and
   non-degenerate (HR-LOC4); 2,577 × 900; chosen at position 0.
2. **Spec/parameter compatibility** — the six `beta_occ_*` map to the now-present
   `loc4_*` arrays; `delta_occ` fixed/calibrated, not free; no singles/year
   parameters required.
3. **Objective-at-start** — evaluate the log-likelihood at the start; **must be
   finite** (no NaN/inf). **If any start is non-finite, halt before optimization
   (HR-OBJ).**
4. **Caps verified** (§7) and **isolation verified** (§6) before launch.
5. **Output-path check** — pilot `Results/` path writable; no collision with
   accepted P3a outputs.

---

## 9. Required outputs (pilot-only)

Under a pilot `Results/` path (not overwriting any P3a output): per-start
converged parameter vector, objective value, convergence/solver status,
iteration count, the solver options used (caps included), per-start and total
wall time, peak memory if feasible, and the parallel/sequential + worker record.
Plus the minimal post-estimation diagnostics carried over from the base
authorization §14 (participation/hours fit, chosen-probability distribution,
wage fit, occupation `loc4` distribution fit, comparison to the old 2016 couples
baseline where feasible). Cluster-robust SE **not required**; Hessian/SE only if
cheap and already supported.

---

## 10. What is authorized

- Loading the `_loc.pkl`; the §8 preflight (artifact/spec/objective/caps/
  isolation/output-path).
- Running the pilot couples likelihood via `estimate_couples_vectorized_gamspy`
  (CONOPT/GAMSPy), ≥2 starts, isolated work dirs (or sequential), capped
  iterations + wall-time.
- Capturing §9 outputs and diagnostics; optional cheap Hessian/SE.
- The rerun report (§12).

---

## 11. What is not authorized

- Using the prior (no-loc4) pkl (HR-LOC4).
- scipy/L-BFGS-B, except under the explicit §5 fallback condition (HR-SCIPY).
- Uncapped or unverifiable-cap solves (HR-CAP); shared mutable files across
  parallel starts (HR-ISO).
- Free structural `delta_occ`; singles; year effects (unless structurally
  required → halt).
- Welfare; SA2; promotion; M1-clean displacement; treating this run as
  verdict-grade.
- Reusing `scripts/pilot/_run_diagnostic_estimation.py` unmodified (stale: old
  pkl, runtime loc4 injection, no caps, old authorization) — HR-STALE.
- Editing production estimator/spec/P3a YAML/data; overwriting accepted P3a
  outputs.
- EUROMOD, GSUR merge, data rebuild.

---

## 12. Required rerun report

`Results/JMP_NC_pilot_diagnostic_estimation_rerun_report_v1.md`, covering: scope
and provenance (amendment to the base authorization; **explicit statement that
the earlier scipy/L-BFGS-B run is invalid and non-interpretable and is not
used**); confirmation the `_loc.pkl` was used (not the prior pkl) and that
`estimate_couples_vectorized_gamspy` consumed it; **a statement that the stale
`_run_diagnostic_estimation.py` was not reused as-is — whether a new script was
written or the stale one replaced, with no runtime loc4 injection** (HR-STALE); the §8 preflight results
(loc4 present/non-degenerate, **objective-at-start finite per start**, caps
verified, isolation verified); the solver (CONOPT/GAMSPy; **exact options —
iteration + wall-time caps**; whether the §5 scipy fallback was invoked and, if
so, the explicit authorization for it); the start protocol (warm-start mapping +
fallback taken; defaults); **parallel-or-sequential, workers, per-start + total
wall time**; per-start objective, convergence status, iterations, parameter
estimates; the §9 diagnostics; halt-condition status; and required final
statements (not verdict-grade; earlier run invalid; loc4 pkl only; CONOPT not
scipy; capped; no welfare/SA2/promotion; no EUROMOD/GSUR/rebuild; `delta_occ`
fixed; M1-clean active; P3a unaffected; rerun slice only).

---

## 13. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. CONOPT/GAMSPy; preflight + caps + isolation
gated; pilot-only outputs; stop after diagnostics.

```text
Work locally in my RURO/MNL codebase. NC PILOT DIAGNOSTIC ESTIMATION RERUN,
FR_2016 couples only. Authorized by
docs/JMP_NC_pilot_diagnostic_estimation_rerun_amendment_v1.md. NOT verdict-grade.
The earlier scipy/L-BFGS-B run is INVALID and non-interpretable — do not use it.

HARD CONSTRAINTS (halt and report if any would be violated):
- Use ONLY the loc4-complete pkl:
  Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
  Do NOT use fr_pilot_nc_2016_couples_precomputed.pkl. If any loc4_* array is
  missing or degenerate in the loaded object -> HALT (HR-LOC4).
- Use GAMSPy/CONOPT via estimate_couples_vectorized_gamspy. scipy/L-BFGS-B is
  NOT authorized unless CONOPT/GAMSPy import or license check FAILS and the user
  explicitly authorizes a fallback -> otherwise HALT (HR-SCIPY).
- Set and VERIFY a solver iteration cap AND a per-start wall-time cap before
  launch. If caps cannot be enforced/verified -> HALT (HR-CAP).
- Parallel starts ONLY with fully isolated output dir, solver log, listing file,
  GAMS/GAMSPy work dir, and temp files per start. Else run SEQUENTIALLY. No
  shared mutable files; loc4 pkl shared READ-ONLY. (HR-ISO)
- delta_occ FIXED/calibrated, not free. Couples-only, 2016-only, no singles, no
  year effects (if spec would require them -> HALT).
- Do NOT edit production estimator/spec/P3a YAML/data; do NOT overwrite accepted
  P3a outputs. Pilot Results/ path only.
- Do NOT reuse scripts/pilot/_run_diagnostic_estimation.py as-is. It is STALE
  (loads old no-loc4 pkl; injects loc4 at runtime; no CONOPT caps; cites old
  authorization). Write a NEW rerun script OR replace it so it: loads ONLY
  _loc.pkl; NO runtime loc4 injection; VERIFIES loc4_* present+non-degenerate;
  CONOPT/GAMSPy only; SETS+REPORTS iteration+wall-time caps pre-launch and HALTS
  before solver if caps unenforceable; isolated dirs per parallel start else
  sequential+report-why; cites THIS amendment. Reusing it unmodified -> HALT
  (HR-STALE).
- Do NOT compute welfare/SA2/promote/displace M1-clean; do NOT run EUROMOD/GSUR/
  rebuild.

Read (read-only):
- docs/JMP_NC_pilot_diagnostic_estimation_rerun_amendment_v1.md
- docs/JMP_NC_pilot_diagnostic_estimation_authorization_v1.md (base spec)
- Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl
- scripts/enhanced/gamspy_estimation_vectorized.py (estimate_couples_vectorized_gamspy)
- the pilot couples spec (estimation_spec_nc_pilot_couples_2016.yaml)

STEP 0 — SCRIPT: do NOT reuse scripts/pilot/_run_diagnostic_estimation.py as-is.
Write a new rerun script (or replace the stale one) that loads ONLY _loc.pkl, does
no runtime loc4 injection, verifies loc4_* present+non-degenerate, uses CONOPT/
GAMSPy only, sets+reports caps and halts if unenforceable, isolates per-start dirs
or runs sequentially. Cite this amendment as authorization. (HR-STALE)

STEP 1 — Confirm runner: estimate_couples_vectorized_gamspy imports and can
consume the loc4-complete PrecomputedDataCouples object. CONOPT/GAMSPy license/
import check. If it fails -> HALT (HR-SCIPY) unless explicit fallback given.

STEP 2 — PREFLIGHT (per start, before any solve):
- loaded pkl is _loc.pkl; loc4_* present + non-degenerate (HR-LOC4);
  2,577 x 900; chosen at position 0.
- six beta_occ_* map to loc4_* arrays; delta_occ fixed; no singles/year params.
- objective-at-start: evaluate LL at each start; MUST be finite. If any
  non-finite -> HALT (HR-OBJ).
- iteration cap + wall-time cap set and VERIFIED (HR-CAP); isolation verified
  (HR-ISO); pilot Results/ path writable, no P3a collision.

STEP 3 — Starts (>=2), each with an ISOLATED output/work dir:
1. mapped warm start from accepted couples params if UNAMBIGUOUS; else
2. pilot defaults, or perturbed defaults if warm mapping ambiguous (HR-WARM:
   state which). 
Run parallel only if isolation guaranteed; else sequential.

STEP 4 — Solve (CONOPT/GAMSPy), capped iterations + wall-time. Capture per
start: objective, convergence status, iterations, wall time; total wall time;
peak memory if feasible; parallel-or-sequential + worker count.

STEP 5 — Diagnostics: participation/hours fit; chosen-probability distribution;
wage fit; loc4 occupation distribution fit; comparison to old 2016 couples
baseline where feasible.

STEP 6 — Persist to pilot Results/ only (no P3a overwrite): parameter vectors,
objectives, convergence, the EXACT solver options (caps), timing/worker record.

THEN STOP. No welfare, no SA2, no promotion.

Halt conditions: HR-STALE, HR-LOC4, HR-SCIPY, HR-CAP, HR-ISO, HR-OBJ, HR-WARM
(amendment s.5-8). On any fire: STOP, write report to that point, await direction.

Write ONE report: Results/JMP_NC_pilot_diagnostic_estimation_rerun_report_v1.md
per amendment s.12, stating the earlier scipy run is invalid/not used, the exact
CONOPT options + caps, and the parallel/sequential + timing record. End with
required final statements.
```

Save the report as:
`Results/JMP_NC_pilot_diagnostic_estimation_rerun_report_v1.md`

---

## Required final statements

- **The earlier scipy/L-BFGS-B run is invalid and non-interpretable and is not
  used.** This rerun supersedes it.
- **Input is the loc4-complete pkl only** (`_loc.pkl`); the prior no-loc4 pkl is
  not used; missing/degenerate `loc4_*` halts (HR-LOC4).
- **Solver is GAMSPy/CONOPT**; scipy is barred except under an explicit
  user-authorized fallback if CONOPT import/license fails (HR-SCIPY).
- **Iteration and wall-time caps are set and verified before launch** (HR-CAP);
  the 4.8 h runaway must not recur.
- **Objective-at-start is checked per start; non-finite halts before
  optimization** (HR-OBJ). `delta_occ` fixed; `beta_occ` free.
- **Parallel starts only with full per-start isolation; else sequential**
  (HR-ISO); parallel/sequential + timing recorded.
- **The stale `_run_diagnostic_estimation.py` is not reused as-is** (old pkl /
  runtime loc4 injection / no caps); a new or replaced script consumes `_loc.pkl`
  directly with caps enforced (HR-STALE).
- **Not verdict-grade. No welfare, SA2, promotion, EUROMOD, GSUR, or rebuild.**
  No production estimator/spec/P3a edit. M1-clean 2016 active; corrected pooled
  P3a track unaffected.

---

*Status: diagnostic-estimation rerun amendment v1. Re-authorizes the pilot
couples likelihood on the loc4-complete pkl via CONOPT/GAMSPy under preflight +
caps + isolation halts; executes nothing itself. Next: the rerun report (§12) —
the first interpretable NC pilot estimates and the estimator-cost number.*
