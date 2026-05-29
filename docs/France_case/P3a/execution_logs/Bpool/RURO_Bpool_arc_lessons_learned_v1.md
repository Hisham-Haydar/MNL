# RURO B-pool recovery arc — lessons learned (2026-05-27 → 2026-05-29)

Three-day investigation arc on the `bpool_p3a_v1` spec covering scale normalisation,
a chosen-row construction bug, solver behaviour at scale, and the discovery of
multi-basin LL structure. **The goal of this doc is to capture what we tried, what
failed, what worked, and why — so future work on the same model class doesn't
relive the same dead ends.**

This is the canonical narrative of the arc. For the verdict of record, see
`RURO_recovery_test_results_v3.md`. For the open question that came out of this
arc, see `RURO_solver_multibasin_findings_v1.md`.

---

## TL;DR

| topic | conclusion |
|---|---|
| Spec identification | ✅ Identified. CONOPT couples-full reaches LL = −10,862 with G2 = 4e−9 reproducibility, all signs correct on the recovered block. |
| `beta_c = 1` numéraire | ✅ Necessary. Eliminates the v1 scale ridge. (commit `31eaecc`) |
| Chosen-row `working_lh` flag | ✅ Was broken; fixed. Was the actual root cause of every pre-fix recovery failure. (commit `099e5c4`) |
| GAMSPy + CONOPT | ✅ Reaches the canonical optimum. Use for production estimation. |
| scipy gradient-based solvers | ❌ All trap at a non-global local maximum LL = −9,737 on singles male. Multi-basin LL surface. |
| scipy random multistart | ❌ Provably ineffective (6 random starts all trap). |
| Package distribution | 🔴 **OPEN HIGH PRIORITY.** Distributing to non-GAMSPy users requires accepting a wrong-basin result or implementing a different approach. Three options on the table (A/B/C in the multibasin findings doc). |

---

## 1. Five diagnoses that were WRONG (and how we figured out)

The arc generated five distinct "structural failure" diagnoses that turned out to
be artefacts of the solver, the harness, or a construction bug. **Each one led
to a recommended spec change that would have been wasted work.** Recognising
them in future investigations saves time.

### 1.1 "Scale ridge in `beta_c` × `beta_l0`" (v1 doc)

- **Claim:** the LL has a flat direction along which `beta_c` and `beta_l0`
  co-scale; min_eig = −0.012, Hessian non-PD, `beta_l0_m` drifts to its bound at
  +21.
- **Recommendation made:** fix `beta_c = 1` as numéraire.
- **Outcome:** the recommendation was **correct** (commit `31eaecc`), but the
  framing was incomplete. The scale ridge was real, but the more important issue
  was that the trust-constr / L-BFGS-B solver was getting trapped at a local max
  near initial values regardless of the ridge.
- **Lesson:** when a parameter drifts to its bound under a quasi-Newton solver,
  consider both "the spec is mis-identified along this direction" AND "the
  solver is at a local max where this parameter's gradient is zero against the
  bound." The numéraire fix addressed one but not both.

### 1.2 "Non-convexity in the couples leisure block on the 9×9 joint grid" (v2 doc)

- **Claim:** even after the `beta_c = 1` normalisation, the couples leisure
  block (5 male + 5 female + `beta_ll`) had a 10-parameter non-convex subspace
  on 300 HH × 9 × 9 = 270K joint-leisure cells.
- **Recommendation made:** parsimonise the leisure block — drop `beta_l_age2_*`,
  pool `beta_l_age_m = beta_l_age_f`.
- **Outcome:** **OVERTURNED.** CONOPT-couples-full recovers all 9 couples leisure
  interior params with correct signs. The "non-convexity" was the same trust-constr
  trap as v1.
- **Lesson:** when a "structural" diagnosis is based on trust-constr stopping
  with `success=False`, **try CONOPT before recommending a spec change**.
  Spec parsimonisation is a real cost; doing it on the basis of a trapped
  optimizer is wasted research effort.

### 1.3 "Box-Cox `theta_l` multi-modality" (singles_v1 doc)

- **Claim:** the leisure Box-Cox exponent `theta_l` had two attractors on the
  LL surface — one at the correct sign (negative), one at the wrong sign
  (positive). Singles trust-constr converged to the wrong-sign basin.
- **Recommendation made:** sign-constrain `theta_l` to strictly negative
  (`theta_l ∈ [−8, −0.05]`).
- **Outcome:** **PARTIALLY OVERTURNED.** The multi-modal LL framing was
  qualitatively right (the LL does have multiple basins). But the specific
  fix — constraining `theta_l` — was tested empirically and gave only an 8%
  improvement in min_eig (−84 → −77.5); the trap basin doesn't depend on
  `theta_l`'s sign. CONOPT recovers `theta_l` with correct sign without any
  constraint.
- **Lesson:** when a parameter looks wrong-signed under one solver,
  empirically test the proposed fix (the sign-constraint) **before** committing
  to it. The 10-minute experiment that rejected this fix saved a real spec
  change that would have biased estimates.

### 1.4 "Block-wide flat ridge in market-opportunity parameters" (couples-full trust-constr post-mortem)

- **Claim:** the trust-constr couples-full run had `beta_E = −0.80` (vs θ\*
  −3.00) with all `beta_E_drg*` scrambled, supposedly indicating the entire
  market-opportunity block was non-identified jointly.
- **Recommendation made:** investigate the synthetic-DGP draw for E × region
  collinearity, possibly redesign the regional dummies.
- **Outcome:** **OVERTURNED.** CONOPT-couples-full recovers `beta_E` to −3.29
  (err 0.29) and all 11 market-opp shifters correct sign within err 0.41. The
  data DOES separately identify E from each region. Trust-constr was stuck at
  the trapped basin where the wrong values of these parameters happen to fit
  better than θ\* values.
- **Lesson:** "params with wrong signs at the same time" under a trapped
  solver doesn't mean they're jointly unidentified. CONOPT verified all 11
  recover separately.

### 1.5 "CONOPT escapes because analytical Hessian sees through BFGS approximation" (v3 doc, since corrected)

- **Claim:** the original v3 verdict attributed CONOPT's success to its
  analytical Hessian, contrasting with scipy's BFGS approximation.
- **Outcome:** **WRONG MECHANISM.** Tested by running scipy `trust-ncg` and
  `Newton-CG` with **finite-difference Hessian** (real curvature info, no
  approximation). Both converged to the same trap as L-BFGS-B (LL = −9737.31
  to 4 decimals). The mechanism is **algorithm class** (CONOPT's GRG + SQP
  active-set-aware steps), not approximation quality.
- **Lesson:** when explaining why one solver works and another doesn't, test
  the proposed mechanism. "Analytical Hessian" sounded plausible but FD
  Hessian falsified it. The actual mechanism (GRG + SQP traversing basin
  barriers that gradient descent walks along) only became visible once the
  approximation hypothesis was eliminated.

---

## 2. Two diagnoses that were RIGHT

### 2.1 Chosen-row `working_lh` flag construction bug (singles_v1 §3)

- **Discovery path:** in §3 of `RURO_recovery_test_results_singles_v1.md`,
  inspected the chosen-row data and found `working_lh` was 0 (or NaN) for
  every chosen row, while ~16% of simulated alternatives had `working_lh = 1`.
- **Root cause:** the builders (`build_bpool_singles.py`, `build_bpool_couples.py`)
  constructed the band flags from each row's hours **on simulated alternatives
  only**. Chosen rows inherited the flag from upstream pooled parquets, which
  didn't carry `working_lh` at all → NaN cast to 0 (singles) or `obs.get(col,
  0.0)` default (couples).
- **Impact:** the MNL likelihood saw "no chosen workers in the LH band, but
  ~16% of simulated alternatives carry LH = 1" and drove `beta_h_lh` to its
  lower bound at −10. The LH-correlated misfit then propagated into wrong-signed
  values on `beta_h_pt1`, `beta_E_gsur`, `beta_occ_*`.
- **Fix:** `099e5c4` — recompute the band flags from the chosen row's own hours
  in both builders. Added CHECK 7 invariant to `check_bpool_engine_ready.py`
  that asserts `band_flag == fresh_recompute_from_own_hours` on every row.
- **Validation:** CONOPT singles male `beta_h_lh = −1.41` (err 0.21, interior);
  CONOPT couples-full `beta_h_lh = −1.058` (err 0.14, interior). Across all
  four post-fix CONOPT slices, recovery is correct.
- **Lesson:** when an MNL parameter saturates at its bound and you can't find
  a spec-level reason, **inspect the data directly** for the variable that
  parameter multiplies. Construction bugs in chosen-row columns are silent
  killers in MNL recovery.

### 2.2 Multi-basin LL structure (the multibasin findings doc)

- **Discovery path:** after the LH-flag fix and Phase 1 numéraire,
  trust-constr still didn't converge cleanly while CONOPT did. The mechanism
  hypothesis ("CONOPT's analytical Hessian") was tested and rejected.
  6-start L-BFGS-B random multistart all trapped at the same point across 21
  orders of magnitude of initial LL.
- **Finding:** the LL has multiple local maxima. The basin containing the
  global max (LL = −2501 singles male, −10862 couples full) is small and
  isolated. The trap basin (LL = −9737 singles male) covers essentially all
  of the bounded parameter space.
- **Why it matters for the package:** scipy multistart cannot find the
  global optimum on this LL surface — provably, not just empirically. Any
  user without GAMSPy/CONOPT who runs this spec on real data will report a
  wrong-basin result with `success = True`.
- **Lesson:** when a published model relies on global optimisation, **test
  multistart explicitly**. Don't assume "any solver from a good starting
  point" works. The recovery test was the right diagnostic; running it under
  multiple solvers exposed a constraint that wouldn't have been visible
  under any single solver alone.

---

## 3. The canonical setup

The eight commits that compose the current canonical configuration:

| commit | what |
|---|---|
| `31eaecc` | Phase 1 numpy: `beta_c = 1` numéraire + variable conditioning (decade-rescale pexp/age) |
| `26fef70` | execution logs + Phase-0 repricing verifier |
| `76f0611` | singles diagnostic + `--sex` flag for per-gender slice isolation |
| `099e5c4` | **chosen-row band-flag fix** + CHECK 7 invariant in `check_bpool_engine_ready.py` |
| `ecc98ab` | GAMSPy Phase 1 completion (gamspy LL builders honour `beta_c` fixed) |
| `93667ab` | recovery_test UNC-cwd fix (chdir to local C: before GAMSPy Container) |
| `a12729c` | GAMSPy threads/solve_link benchmark (closed: defaults are right) |
| `af02cd7` + `cf3537c` | v3 doc + truthful 6/20 multistart result |

Plus `5f575b8` from the user side (benchmark script preservation).

To reach the canonical optimum: launch CONOPT via GAMSPy from a U-mapped
or local-C: cwd, on the engine-ready parquet rebuilt post-`099e5c4`.
Expect 30 seconds (singles male) to 6 hours (couples-full at 2.3M rows)
of wall time.

---

## 4. What to do differently next time

For future RURO work, or any model in this class:

1. **Always benchmark CONOPT vs scipy on the recovery test.** Two solvers from
   the same start landing at different LL values is the multi-basin signature.
   If CONOPT lands at a better LL, that's the global; if they agree, either
   could be wrong but you have no way to know without a third reference.

2. **For chosen-row diagnostics, never trust a flag that was built only on
   simulated alternatives.** Always assert `flag == fresh_recompute_from_own_hours`
   on every row including the chosen row. CHECK 7 in
   `check_bpool_engine_ready.py` does this for the B-pool track now.

3. **Don't propose a spec parsimonisation based on a trust-constr `success=False`
   verdict alone.** Test the proposed parsimonisation against CONOPT first.
   Trust-constr stopping somewhere does not mean the LL has nowhere good to
   go.

4. **The "bound saturation" signal is highly diagnostic.** When a parameter
   saturates at its bound and you can't find a spec-level reason, the next
   inspection step is **the data column that parameter multiplies**, not the
   parameter itself. Construction bugs in MNL builders silently produce this
   signature.

5. **For the recovery test harness, the `min_eig` line at the bottom of the
   summary is currently silently wrong on non-PD Hessians** — `np.linalg.inv`
   returns garbage on non-PD matrices and the harness's clip-then-sqrt path
   poisons every downstream SE value. See `workitem-recovery-test-g3b-cov-poison`
   in memory. **Read CONOPT's own status (NormalCompletion + OptimalLocal)
   in preference to the harness's recomputed Hessian** until that's fixed.

---

## 5. Open question

**Package distribution under multi-basin LL (workitem-package-distribution-multibasin-LL).**

The bpool_p3a_v1 spec produces canonical results under CONOPT/GAMSPy. Under
any scipy gradient-based solver from any tested starting point, the result is
a wrong-basin local maximum 7000+ negLL units worse than the canonical, with
`success = True` and no diagnostic warning.

Three options for the package:

- **A** — restrict to GAMSPy users (correct, narrow distribution)
- **B** — ship scipy default with explicit warnings + a multistart detection
  diagnostic (broad distribution, user-burden)
- **C** — model reformulation to flatten the trap basin (1-2 weeks research,
  uncertain payoff)

Decision needed before any further package work. See
`RURO_solver_multibasin_findings_v1.md` §5 for the full option matrix.

---

## 6. Provenance

What remains in this directory after the 2026-05-29 consolidation:

- `RURO_Bpool_arc_lessons_learned_v1.md` (this file) — the canonical narrative
- `RURO_recovery_test_results_v3.md` — the verdict of record
- `RURO_solver_multibasin_findings_v1.md` — the open package question
- `RURO_recovery_test_results_v3_couples_full_conopt_wc_raw.md` — canonical
  headline run, raw data
- `RURO_recovery_test_results_v3_singles_male_conopt_wc_raw.md` — canonical
  singles male, raw data
- `RURO_recovery_test_results_v3_singles_female_conopt_wc_raw.md` — canonical
  singles female, raw data
- `RURO_Bpool_column_diff_v1.md` — schema reference across pipeline stages
- `RURO_Bpool_draws_verification_v1.md` — D1 focal-modes verification + post-fix
  addendum on `working_lh`
- `RURO_Bpool_euromod_run_v1.md` — EUROMOD execution reference
- `RURO_Bpool_precompute_gate_v1.md` — engine-ready contract reference
- `benchmark_gamspy_options_v1.json` — threads/solve_link benchmark raw data

What was deleted in the 2026-05-29 consolidation (the trapped-basin diagnostic
churn that this lessons doc supersedes):

- Trust-constr / L-BFGS-B raw recovery reports (10 files) — superseded by §1
- Original `_v1.md`, `_v2.md`, `_singles_v1.md`, `_bpool_recovery_identification_report_v1.md`
  narrative docs — replaced by §1 corrections in this doc, with full text
  recoverable from git history at commit `cf3537c` and earlier.
- `RURO_ACS_reparam_premise_mismatch_v1.md` — the "engine is already ACS,
  no refactor needed" finding; the conclusion is preserved in §1.1; full text
  in git history.
- `RURO_recovery_test_results_v3_singles_male_conopt_raw.md` (warm only) — superseded by the `_wc` version.
- `benchmark_gamspy_options_v1.md` and `benchmark_scipy_lbfgsb_singles_male_raw.md` — benchmark conclusions absorbed into §2.2 + memory work items.

To recover any deleted file: `git show <commit>:<path>` against any commit at
or before `cf3537c` (2026-05-29).
