# FR P2a Region-Live — Phase-3 Implementation Report — v1

Date: 2026-07-24. Scope: implementation and static validation of Phase-3 (estimation) support
in the production runner, under the Phase 1–2 acceptance and Phase-3 authorization recorded in
`FR_P2a_region_live_phase12_manager_acceptance_v1.md`. **No real Phase-3 estimation was
executed; no optimizer was called anywhere in this task.** Nothing was committed.

## 1. Implementation verdict

**READY FOR INDEPENDENT CODE REVIEW.**

Phase-3 support is implemented, statically validated, and regression-proven: the Phase 1–2
dry-run still passes bit-identically (regenerated stem hash `8bf083ce…` in a fresh output
root), the Phase-3 dry-run verifies the full input contract with **zero optimizer involvement**
(`optimizer_called: false`, pre-optimization objective deviation 0.00e+00), no pre-existing
artifact changed (0 changed files in the hash sweep), and `--phase 4` is refused. One
design decision needs reviewer attention (§7): the package optimizer wrapper cannot express the
pre-registered `maxcor=30`, so the runner makes the checkpoint-exact scipy L-BFGS-B call over
the package-built JAX objective — documented here and in the config, not selected silently.

## 2. Files inspected

All binding documents re-read this session: manager decisions v2; production rebuild plan v2
(§11 estimation, §12 gradient/convergence, G-1..G-4/G-15/G-16, S-2/S-3); dry-run report v2;
notebook-integration addendum; the accepted evidence set (`rebuild_manifest.json`,
`dry_run_report.json`, `pre_estimation_reload_verification.json`); both p2a scripts and the
run-config; the validated optimizer API
(`dclaborsupply/solvers/jax_optimize.py` — read in full: `optimize_lbfgsb` signature, wrapped
scipy call, hard-coded options) and the JAX objective route
(`likelihood/engine_jax.build_jax_singles_ll`, already exercised by the accepted Phase 2);
the frozen checkpoint's fit cell (optimizer options source).

## 3. Manager authorization

`FR_P2a_region_live_phase12_manager_acceptance_v1.md` (created first, as instructed): Phase
1–2 **ACCEPTED** on the canonical hashes (geometry `5bcf0e54…`, stem `8bf083ce…`, theta vector
`5f3722dc…`), Phase 3 implementation + execution **AUTHORIZED**, Phases 4–8 **NOT YET
AUTHORIZED**, the 47-parameter pooled model remains the formal certified baseline, P2a remains
provisional, welfare remains non-reportable. The runner records this authorization pointer in
every `phase3_manifest.json`.

## 4. Files modified

Exactly the two authorized files (`git diff --stat`: +547/−12):

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` (+~500) — Phase-3 module (§5), conditional
   optimizer prohibition, atomic-write helpers, CLI routing, updated module docstring.
2. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (+51) — `phase3:` block:
   authorization pointer, accepted-evidence anchors, start-theta source, optimizer
   settings + route note, ratified gates, prohibited-operations list.

Created: this report and the acceptance doc. **Not modified:**
`verify_p2a_regionlive_reload.py` (no Phase-3 need — the existing pre-estimation mode already
covers the pre-final reload check; Phase-7 cold reload remains out of scope), both notebooks,
`dclaborsupply-monorepo`, certified spec/thetas, all Phase 1–2 evidence and thresholds.

## 5. Phase-3 runner architecture

Three additions, isolated from the Phase 1–2 code path:

- **`_phase3_contract(out, cfg, log)`** — the full pre-optimization input contract (§6);
  returns the working context (spec, pins, bounds, start vector, jitted objective) plus an
  evidence dict; raises `StopRun` on any failure.
- **`_phase3_estimate(ctx, paths, cfg, log)`** — the estimation call (§7) plus post-gates
  (§9–§11) and atomic artifact emission (§12–§13). Contains **no** Hessian, eigenvalue, rank,
  score, sandwich-SE, post-estimation, welfare, or synthetic-recovery code.
- **`run_phase3(args, cfg)`** — orchestration with its **own manifest and console log**
  (`phase3_manifest.json`, `phase3_console.log`); never writes a Phase 1–2 evidence file;
  S-0 module guards at start (optimizer prohibited), at dry-run end (still prohibited), and at
  real-run end (optimizer permitted, EUROMOD/draw modules still prohibited).

CLI behavior: `--phase 1` / `--phase 2` byte-for-byte unchanged code path; `--phase 3`
routes to `run_phase3` **before** the Phase 1–2 orchestration (never re-runs or rewrites
Phases 1–2); `--phase 3 --dry-run` = contract only, hard-asserted optimizer-free;
`--phase > 3` refused (verified: exit 2 with refusal message). Exit codes: 0 complete,
2 STOPPED, 3 unexpected, 4 REVIEW_REQUIRED_TARGET_MISMATCH.

## 6. Input contract

Enforced before any optimization (all verified live in the Phase-3 dry-run):

1. Phase 1–2 manifest present with `status == DRY_RUN_PHASES_1_2_COMPLETE` (accepted run's
   script/config hashes recorded alongside the current ones).
2. Frozen input hashes unchanged: geometry `5bcf0e54…`, stem `8bf083ce…`, certified YAML
   `492bcfa9…`, warm-start CSV `c72e92b1…`, start-theta CSV `930ef3aa…` (S-8 on mismatch).
3. Parameter ordering identical to the accepted `dry_run_report.json` (47 names).
4. Structural route: `wage_spec == "vw"`; `wage_loc_groups` absent (`loc_empirical` /
   `vw_occupation` inactive structurally); proposal-weighted centering flags on; prior
   strictly positive with `max|log(prior) − log_prior| ≤ 1e-9` (correction active exactly
   once — single `−log_prior` term in the validated engine, witnessed by the accepted
   3.64e-12 cross-backend agreement).
5. 1,555 households; 101 alternatives per household (loader-level `n_obs == n_groups × 101`
   per gender).
6. Exactly 10 pins / 37 free (bounds-clamped at certified warm-start values — the accepted
   mechanism).
7. Start vector = accepted stored region-live theta (`trial` column), float64-bytes hash
   gated equal to the accepted `5f3722dc…`; pinned entries set to their `pinned_at` values
   (adjustment magnitude recorded: max-abs 2.9e-09).
8. JAX pre-optimization objective at the applied start within 1e-4 of 19053.46553160094 —
   **measured dev 0.00e+00** in the dry-run.

Any failure writes a **STOPPED `phase3_manifest.json`** (with the stop code/gate/message)
before the process exits — implemented via the `finalize` path in `run_phase3`.

## 7. Optimizer route

**Settings (pre-registered, both sources agree):** `maxiter=5000, maxcor=30, ftol=1e-15,
gtol=1e-10` — plan v2 §11/G-4 and the frozen checkpoint's fit cell are identical.

**Route decision requiring reviewer sign-off:** the package wrapper
`dclaborsupply.solvers.jax_optimize.optimize_lbfgsb` exposes only `gtol`/`maxiter` and
hard-codes `ftol=1e-15, maxls=60`; it has **no `maxcor` parameter** (scipy would default to
10) and forces `maxls=60` (the checkpoint ran scipy's default). Using the wrapper would
therefore silently alter two pre-registered settings. The runner instead makes the
**checkpoint-exact call**: `scipy.optimize.minimize(method="L-BFGS-B", jac=True,
bounds=b4, options={maxiter: 5000, maxcor: 30, ftol: 1e-15, gtol: 1e-10})` over
`jax.jit(jax.value_and_grad(nm + nf))` built from the package's `build_jax_singles_ll` —
the identical construction the frozen checkpoint used for the anchor fit. No likelihood
mathematics is duplicated; the objective is 100% package code. The decision, the wrapper's
surface analysis, and the settings sources are recorded in the config (`phase3.optimizer`)
and in every `optimizer_diagnostics.json`. This was judged a wrapper-API limitation, not a
conflict between the two pre-registered settings sources (which agree) — flagged here rather
than resolved silently.

## 8. Parameter and pin binding

47-vector binding via `spec.all_param_names`; 10 pins bounds-clamped at certified warm-start
values (`pinned_at` recorded per pin, e.g. `beta_l0_m` at 1e-06); 37 free with explicit
bounds; occupation block free. Post-fit gates: pin/free structure unchanged **and** pins
**bitwise unchanged** (`float64.tobytes()` equality of `theta_hat[pin]` vs `pinned_at` —
L-BFGS-B keeps `lb == ub` parameters exactly at the bound). Structure or pin violation →
STOPPED.

## 9. Gradient gate

Full 47-vector analytic gradient (`jax.value_and_grad`) at the final theta persisted;
`max|grad|` computed over the **35 non-bound free** parameters (37 free minus the two
expected at-bound parameters); gate `< 1e-2` (D-5). Failure → STOPPED (S-3/G-3). The two
at-bound parameters' gradients are reported, not gated.

## 10. Bound handling

Bound-hit epsilon **1e-5** (D-5). The expected at-bound set is **derived from the accepted
input** — stored theta vs spec bounds at ε — and cross-checked against the configured
expectation; the dry-run derived exactly **`{beta_l_age2_sm, beta_l_age2_sf}`** (both at the
+1.0 upper bound), matching config. After estimation, detected hits among free parameters
must equal that set **exactly**; any additional or different hit → STOPPED (S-3/G-15).
Per-parameter lb/ub and distances to both bounds are persisted for all 47 parameters.

## 11. Objective target gate

`|negLL_final − 19053.46553160094| ≤ 1e-4` → PASS (`PHASE_3_COMPLETE`). Any material
mismatch — **above or below** — with all other gates passing yields
**`REVIEW_REQUIRED_TARGET_MISMATCH`** (manifest status + exit code 4), never automatic
acceptance; a better-than-target objective is treated as a finding for manager review
(D-2: the reference fit would then not have been reproduced as claimed). No identification
certification is claimed anywhere (D-7); the results JSON carries the PROVISIONAL banner.

## 12. Output contract

All Phase-3 writes confined to `outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/`
(the `OutRoot` guard covers it; Phase 1–2 files are never opened for write in the Phase-3
path). Artifacts: `estimation_results.json` (accepted-schema results with PROVISIONAL
status), `theta_estimated.csv` (param, value, pinned, at_bound, lb, ub, dist_lb, dist_ub,
grad), `optimizer_diagnostics.json` (start/final thetas + hashes, objectives, success/
status/message, `n_iter`/`n_fev`/`n_jev`, elapsed, full gradient, bounds table, gate table,
route record), `phase3_manifest.json`, `phase3_console.log`.

## 13. Atomic-write behavior

All Phase-3 JSON and CSV artifacts are written via tmp-file + `os.replace` promotion
(`_atomic_write_json` / `_atomic_write_csv` / `_atomic_write_text`); the console log uses the
same helper. No partially-written artifact can be left behind by an interrupt.

## 14. Stop conditions

- Contract failures → STOPPED manifest written before exit (S-1 structure/route, S-8 hash
  change, S-9 pre-optimization objective).
- Post-fit: optimizer failure (S-2/G-2), pin violation (S-3), bound-hit mismatch (S-3/G-15),
  gradient gate (S-3/G-3) → STOPPED with the failing gate named; target mismatch →
  REVIEW_REQUIRED_TARGET_MISMATCH (exit 4).
- S-0 prohibited-operation guards: optimizer module barred at phase3-start and at dry-run
  end; EUROMOD/draw modules barred always; no Phase-4+ computation exists in the path.

## 15. Phase 1–2 regression

Re-run unchanged (`--phase 2 --dry-run`) against a scratch output root (chosen so the
**accepted evidence files are not rewritten**, honoring the do-not-modify-evidence
prohibition): **exit 0, `DRY_RUN_PHASES_1_2_COMPLETE`**, identical funnel/take-up/assembly/
reconciliation/liveness/objective results, and the regenerated stem hashed
**`8bf083ce…` — byte-identical again** (fresh determinism proof). The Phase 1–2 code path was
not touched by the Phase-3 edits (routing returns before it).

## 16. Phase-3 dry-run

Mandated command executed: **exit 0, `PHASE_3_DRY_RUN_COMPLETE`**. Contract verified live:
ordering ok; 10 pins / 37 free; derived at-bound `{beta_l_age2_sm, beta_l_age2_sf}`;
`negLL(start) = 19053.4655316009`, deviation **0.00e+00**; `optimizer_called: false` in the
manifest; internal assert confirmed `scipy.optimize` absent from `sys.modules` at dry-run
end. Only `phase3_manifest.json` + `phase3_console.log` were created.

## 17. Prohibited operations

Confirmed for this task: no optimizer call (module-level assert, both runs), no EUROMOD, no
draw generation, no estimation, no Hessian/rank/eigenvalue, no clustered inference, no
post-estimation, no welfare, no notebook execution or modification, no monorepo change
(`git status` clean at `27756a0`), no certified-baseline or theta-file change, no Phase 1–2
evidence or threshold change — the post-run hash sweep found **0 changed pre-existing files**
under `region_live_v1/` (only the two new `phase3_estimation_v1/` files).

## 18. Git diff summary

```
 M scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml   (+51: phase3 block)
 M scripts/p2a/run_p2a_regionlive_rebuild.py            (+~500/−12: Phase-3 support)
?? docs/France_case/P2a/FR_P2a_region_live_phase12_manager_acceptance_v1.md
?? docs/France_case/P2a/FR_P2a_region_live_phase3_implementation_report_v1.md   (this file)
?? outputs/p2a_singles2016/region_live_v1/phase3_estimation_v1/   (dry-run manifest + console)
```

`dclaborsupply-monorepo`: clean (HEAD `27756a0`). MNL HEAD `9b3926c`; nothing committed by
this task. New script/config hashes (recorded in the phase3 manifest): runner `c48dd122…`,
config `db245ec8…` (the accepted Phase 1–2 hashes `be11294b…`/`68d152e7…` are preserved in
the acceptance doc and the accepted manifest).

## 19. Whether independent review may begin

**YES.** The implementation is complete, statically validated, regression-proven, and
evidence-bundled. Review focus suggested: (a) the §7 optimizer-route decision
(checkpoint-exact scipy call vs the wrapper's narrower surface); (b) the pin-consistency
choice (start vector's pinned entries set to `pinned_at`, max adjustment 2.9e-09, both
vectors + hashes persisted); (c) the REVIEW_REQUIRED_TARGET_MISMATCH semantics (exit 4,
never auto-accepted); (d) the derived-at-bound gate.

## 20. Immediate next action

Independent code review of the two modified files against this report. After review sign-off,
execute the real Phase-3 estimation:

```
python scripts/p2a/run_p2a_regionlive_rebuild.py
  --config scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
  --phase 3 --out outputs/p2a_singles2016/region_live_v1
```

(no `--dry-run`), then submit `phase3_estimation_v1/` to the manager. Phases 4–8 remain
unauthorized until that review.

**FINAL VERDICT: READY FOR INDEPENDENT CODE REVIEW** (no estimation executed; nothing
committed; no thresholds, evidence, notebooks, or package code touched).
