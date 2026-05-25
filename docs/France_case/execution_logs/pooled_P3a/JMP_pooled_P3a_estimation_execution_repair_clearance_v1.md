# JMP Pooled P3a Estimation — Execution Repair Clearance v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Specification class: repair clearance memo. This memo adjudicates
whether the narrow execution repair authorized by
`docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`
has cleared the three preflight blockers, whether the pooled P3a
estimation is now execution-compatible, and whether — given a clean
preflight v2 — the pooled estimation may be run. It does not
re-scope the estimation, authorize welfare, issue an SA2 verdict, or
displace M1-clean. The pooled solver has not been run; no estimate
exists.

Reference documents:
- `docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`
  (the repair authorization being cleared)
- `docs/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`
  (the repair execution report)
- `Results/JMP_pooled_P3a_estimation_preflight_report_v1.md` (the v1
  HALT — three blockers PF6/PF7, PF8, PF9)
- `Results/JMP_pooled_P3a_estimation_preflight_report_v2.md` (the
  post-repair re-run — PASS, EXECUTION-READY)
- `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and
  `docs/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md`
  (the standing estimation authorization unblocked by this clearance)
- `docs/RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md`,
  `docs/estimation/RURO_cluster_robust_SE_implementation_report_v1.md`,
  `docs/estimation/RURO_cluster_robust_SE_implementation_correction_v1.md`,
  `Results/RURO_cluster_robust_SE_static_validation_v1.md` (the
  cluster-robust SE infrastructure and its smoke-test validation)
- `Results/JMP_pooled_P3a_v7_interface_check_placeholder_theta.json`
  (the V7 interface-callability diagnostic — placeholder theta only)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to adjudicate, strictly, whether the
narrow execution repair has cleared the three blockers that halted the
pooled P3a estimation preflight, and — only if preflight v2 passes
cleanly — to clear the pooled estimation for execution against the
repaired estimation-ready split stem. The memo confirms what the
repair restored and bounds what it did not: it did not run the solver,
did not produce an estimate, did not validate cluster-robust inference,
and does not authorize welfare, an SA2 verdict, canonical promotion, or
the displacement of M1-clean.

The adjudication turns on three findings. First, the repair report
confirms all three blockers (R1 post-estimation mode, R2 split-stem
contract, R3 year indicators) resolved with V1–V8 PASS. Second,
preflight v2 returns PASS — EXECUTION-READY across all fourteen checks
(PF1–PF15), with the v1 HALT (PF6/PF7) and the v1 FAILs (PF8, PF9) now
PASS. Third — and this is the load-bearing strict distinction — the
post-estimation cluster-robust SE run that exists today
(`...v7_interface_check_placeholder_theta.json`) was executed at the
YAML initial values, NOT at a converged pooled theta. It is an
interface-callability diagnostic only. Its T4 failure (15 non-positive
SEs) is the expected consequence of an ill-conditioned Hessian
(condition number ≈ 3.5 × 10⁷³) far from the optimum, and it carries no
inference content. The genuine post-estimation inference diagnostics
(T4, T5, and the on-the-converged-run confirmation of T3) remain to be
produced at estimation time with the converged theta and the true
Hessian.

On these findings the memo clears the repair, restores execution
compatibility, and authorizes the pooled estimation to be run against
the split-stem base — subject to the standing execution authorization
and its correction, the halt conditions, and the post-estimation
diagnostic requirements carried forward unchanged.

---

## 2. Previous halt condition

The v1 preflight returned **HALT — DO NOT RUN SOLVER** on three
blockers, and the solver was not invoked.

The primary HALT was PF6/PF7: `run_cluster_robust_se.py --mode
post-estimation` was scaffolded but not implemented — it returned
"Post-estimation mode not yet implemented in this smoke-test release."
and exited 1 — so the true-Hessian cluster-robust standard errors that
the standing authorization requires (§14 R1–R4, §19 as corrected)
could not be produced after convergence, and the post-estimation
diagnostics D9/D10/D11 (T3/T4/T5) could not be run.

Two additional data-loading blockers would have prevented the run even
had PF6/PF7 been resolved. PF8: `enh_RURO_estimate_FR.py` requires
split `{mnl_base}__singles.parquet` / `{mnl_base}__couples.parquet`
inputs with a `__mnlmeta.json`, while the pooled object was a single
unified parquet with a `household_type` column and no split-stem
counterparts. PF9: the market-opportunity shifters
`year_2015_indicator` and `year_2017_indicator` were absent from the
pooled parquet and did not match the engine's automatic one-hot
derivation pattern, so they resolved to `None` and the year effects
could not be estimated.

These three blockers — and only these three — are the subject of the
repair this memo clears.

---

## 3. Repair R1 result

**R1 — post-estimation cluster-robust SE mode: RESOLVED.**

The repair replaced the "not yet implemented" stub in
`run_cluster_robust_se.py` with a `run_post_estimation` path that
parses the spec (PE1, n_params = 55), loads the converged theta from an
estimation results JSON (PE2), loads the full split-stem data with no
row bound via `load_and_validate_mnl_data` (PE3), builds the
precomputed singles and couples objects with the year indicators and
occupation dummies in `extra_vars` (PE4), extracts the scores via
`compute_scores_joint` (PE5), computes the **true Hessian** by central
differences on `compute_gradient_joint` at the converged theta (PE6,
explicitly NOT the dummy Hessian H = 0.1·I of the smoke test), assembles
the sandwich VCV via `compute_cluster_robust_se` (PE7), and runs
T3/T4/T5 with the VCV saved to a documented `.npy` path (PE8) and the
no-welfare / M1-clean-active confirmations (PE9).

The existing `--mode smoke-test` interface is preserved: preflight v2
PF14 confirms C1–C17 still PASS with GA17 status "smoke-test
callability: CONFIRMED" unchanged. The final post-estimation CLI is
documented in the repair report §"Documented final post-estimation CLI
(V8)", with `--mnl-base`, `--results-json`, `--cluster-col` (default
`idorighh`), `--start-label`, and the `--spec-config` alias.

**Strict qualification on R1.** R1 establishes that the post-estimation
mode is callable end-to-end. It does NOT establish that the
cluster-robust inference is valid. The only post-estimation run
performed to date is the V7 interface check at placeholder (initial)
theta; its inference outputs are not valid (see §6). The true-Hessian
T4/T5 (and the on-the-converged-run T3) are produced only when the mode
is invoked on the actual `estimation_results.json` after the pooled
estimation converges.

---

## 4. Repair R2 result

**R2 — split-stem estimator contract: RESOLVED.**

The data-preparation script
`scripts/maintenance/prepare_pooled_estimation_ready.py` produced the
three estimation-ready split-stem files from the unified pooled parquet
without modifying the estimator (the preferred route; the `--parquet`
fallback was not used):

| File | Rows | Cols |
|------|------|------|
| `fr_p3a_gsurv2_estimation_ready__singles.parquet` | 500,700 | 148 |
| `fr_p3a_gsurv2_estimation_ready__couples.parquet` | 743,800 | 148 |
| `fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | — | — |

Conservation is exact: 500,700 + 743,800 = 1,244,500 rows; 12,445
household-years; 9,657 unique `idorighh` clusters (V2 PASS).
`load_and_validate_mnl_data` accepts all three with
`strict_validation=True` (V1 PASS). The cluster key is preserved —
`cluster_id == idorighh` on 100% of rows in both files, no silent
`idhh` fallback (V4 / PF10 PASS). Income routing is preserved — singles
carry non-null `ils_dispy_real`; couples carry non-null
`ils_dispy_male` / `ils_dispy_female`; the couples consumption path
reads `c_norm` and does NOT read `ils_dispy_real`; no singles/couples
income mixing (V5 / PF11 PASS, GA15 carry-forward intact).

**Noted, non-blocking.** The repair report describes the split as
`household_type == "singles"` / `"couples"` (plural), whereas earlier
documents referenced `single` / `couple` (singular). This is a
cross-document wording difference only: the split produced exactly the
expected row counts and passed V1 strict validation and V2
conservation, so the split is verified correct by conservation
regardless of the exact label string. No action required; flagged for
awareness.

---

## 5. Repair R3 result

**R3 — year indicators: RESOLVED.**

The two indicators were derived from `year_tag` and written into both
split files as `float64`, per the authorized rule:
`year_2015_indicator = 1[year_tag == 1]`,
`year_2017_indicator = 1[year_tag == 3]`, with `year_tag == 2`
(FR_2016) the omitted reference (both indicators 0.0). Derivation
verified (V3 / PF9 PASS): `year_2015_indicator == 1` iff
`year_tag == 1`; `year_2017_indicator == 1` iff `year_tag == 3`; both 0
iff `year_tag == 2`. Counts: singles 166,900 / 166,200; couples
256,600 / 229,500.

Critically, the indicators are now visible to the precompute step:
`spec.market_opportunity_shifters` yields them in `extra_vars`, and the
corrected `_collect_extra_vars` no longer skips them. Preflight v2
confirms no year-effect shifter is dropped during precompute. Neither
the YAML nor the source unified parquet was modified; the indicators
exist only in the new split-stem files.

---

## 6. Preflight v2 result

**Preflight v2 verdict: PASS — EXECUTION-READY.** The solver was not
run.

All fourteen checks pass. The v1 HALT and the two v1 FAILs are cleared:

| Check | v1 | v2 |
|-------|----|----|
| PF6/PF7 post-estimation mode | HALT | **PASS** |
| PF8 split-stem contract | FAIL | **PASS** |
| PF9 year indicators | FAIL | **PASS** |
| PF1–PF5, PF10–PF15 | PASS | PASS |

PF13 (region/occupation dummies) passes with expected, informational
engine warnings (`"skipping 'loc4_2_male'"`), which are unchanged from
M1-clean behavior and do not prevent correct computation: the
occupation attribute is set correctly on the precomputed couples object
via `_extract_or_derive_gender`. This is documented and is not a
blocker.

**The V7 interface diagnostic is NOT a clean post-estimation result and
must not be read as one.** `...v7_interface_check_placeholder_theta.json`
was run at the YAML initial values, explicitly labelled as a
placeholder-theta interface check. PE1–PE7 PASS and T3 confirms exactly
9,657 clusters on the full dataset — these establish callability. But
T4 reports 15 non-positive SEs, which the artifact correctly attributes
to an ill-conditioned Hessian (condition number ≈ 3.5 × 10⁷³) at a
theta far from the optimum; the robust SE vector is degenerate (≈ 10⁻¹⁶
or exactly 0.0) across roughly fifteen parameter positions. This T4
failure is expected at non-converged theta and is NOT a preflight
blocker. The V7 placeholder JSON records the placeholder VCV path
historically, but the no-value placeholder VCV binary was intentionally
removed in commit 85ee874. The placeholder robust-SE/VCV outputs carry
no inference content and must not be used; T3/T4/T5 must be rerun after
estimation with converged theta and the true Hessian.

Preflight v2 therefore passes cleanly for the purpose of authorizing
execution: the infrastructure is complete and callable, the data is
loadable and structurally correct, and the only outstanding items
(T4/T5 inference validity) are by construction post-estimation checks,
not preflight checks.

---

## 7. Whether execution compatibility is now restored

**Yes. Execution compatibility is restored.**

The three incompatibilities that the v1 preflight identified are
resolved and independently confirmed by preflight v2. The estimator can
now load the pooled data through its existing, validated split-stem
contract (`--mnl-base
Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`), the year
effects can enter the likelihood, and the true-Hessian cluster-robust
SE path is callable for the post-estimation stage. No deep modification
of `enh_RURO_estimate_FR.py` was required or made; the estimator's load
path, income routing, and group filtering are untouched, and the
M1-clean-frozen behavior is preserved.

The one substantive change to the standing authorization's mechanics is
the data input path: the authorized `--mnl-base` is now the
estimation-ready split-stem base
`Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`, not the
unified `fr_p3a_gsurv2_harmonised.parquet` directly. The specification
(55-parameter `ruro_occ_P3a_pooled` YAML), the cluster key (`idorighh`),
the income rule (GA15), the three starts, the solver/vectorised mode,
the halt conditions, and the not-authorized scope are all unchanged.

Restoration of execution compatibility is an infrastructure statement.
It does not certify the inference, which remains a post-estimation
matter (§6, §8).

---

## 8. Whether pooled estimation may now be run

**Yes — the pooled estimation may now be run**, because preflight v2
passes cleanly, and subject to the conditions below. This clearance
unblocks the standing execution authorization
(`docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and its
correction); it does not re-scope it.

Binding conditions on the run:

1. **Data input.** Run against the split-stem base
   `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready` (the
   estimator appends `__singles.parquet`, `__couples.parquet`,
   `__mnlmeta.json`). Do NOT run against the unified parquet.
2. **Specification and cluster key.** `ruro_occ_P3a_pooled` (55
   parameters); `cluster_id = idorighh`, with the strictness safeguard
   active and the silent `idhh` fallback prohibited (HALT if it would
   fire).
3. **Income routing (GA15).** Singles use `ils_dispy_real`; couples use
   `ils_dispy_male` / `ils_dispy_female`; the couples consumption path
   must not read `ils_dispy_real` (HALT if it would).
4. **Three starts.** Warm from M1-clean (53 → 55 with
   `beta_E_y2015 = beta_E_y2017 = 0.0`); spec defaults
   (`--warm-start none`); perturbed M1-clean (seed 42, ±0.1).
5. **Post-estimation inference (mandatory, on each converged start).**
   Invoke `run_cluster_robust_se.py --mode post-estimation` with the
   actual `estimation_results.json` and the **true Hessian** (NOT the
   dummy Hessian, NOT the placeholder-theta V7 outputs). Produce, as
   the report's required artifacts: converged theta by start; the
   true-Hessian/bread source explicitly identified; the on-the-
   converged-run confirmation of T3 (9,657 clusters); the cluster-robust
   SE vector; the robust VCV (or a documented path); T4 robust-SE
   positivity; and the T5 robust-vs-Hessian comparison.
6. **Halt conditions.** The standing authorization's halt conditions
   H1–H6 remain in force (cluster key not `idorighh`; income routing
   wrong; a start fails to converge; cluster-robust SE computation
   fails — T3 not 9,657, a free-parameter T4 SE not positive at the
   converged theta, or a sandwich error; any welfare or canonical step;
   any specification modification).

The V7 placeholder artifact does not satisfy condition 5 and must not
be presented as if it did. The T4/T5 results that gate the subsequent
review must come from the converged theta with the true Hessian.

**Sequencing after the run (carried forward from the authorization
correction).** After estimation, the immediate next gate is a strict
post-estimation review / SA2-readiness verdict adjudicating whether the
estimation report and all mandatory diagnostics pass. The SA2 verdict
is drafted only if that review passes; it is NOT the immediate next
step, and it is not issued by this clearance.

---

## 9. Whether welfare computation is authorized

**No. Welfare computation is NOT authorized.** It is separately gated
behind an accepted SA2 verdict and a separate welfare-computation
authorization. No welfare object was produced by the repair, and none
may be produced by the estimation run this clearance unblocks. Any
welfare or canonical-promotion step during the run is a halt condition
(H5).

---

## 10. Whether M1-clean remains active

**Yes. M1-clean 2016 remains the active JMP baseline.** The repair did
not displace it, and this clearance does not displace it. The pooled
estimation, once run, produces candidate results at a versioned path;
nothing is promoted to canonical status. M1-clean is displaced only by
a future SA2 verdict — itself drafted only after the strict
post-estimation review passes — that explicitly promotes the pooled
specification. Until then, and through the estimation and its
post-estimation review, M1-clean 2016 stays active.

---

## 11. Immediate next task

**If this clearance is accepted, the immediate next task is to run the
pooled P3a estimation against the repaired estimation-ready split
stem.**

Tool path: Claude Code (local codebase, pooled estimation).
Interpreter: `.venv\Scripts\python.exe`.

The run executes the three-start estimation of `ruro_occ_P3a_pooled`
under the standing execution authorization and its correction, against
`--mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`,
with `--solver gamspy-conopt --vectorized` (or the documented exact
solver/vectorised syntax). After each start converges,
`run_cluster_robust_se.py --mode post-estimation` is invoked on the
resulting `estimation_results.json` with the true Hessian to produce
the cluster-robust SEs and the post-estimation diagnostics — the
on-the-converged-run T3 (9,657-cluster confirmation), T4 (robust-SE
positivity), and T5 (robust-vs-Hessian comparison) — which the V7
placeholder explicitly does not provide. The estimation report is saved
per the corrected §19 of the standing authorization (the full
cluster-robust SE artifact list, not only point estimates).

What follows the run is NOT this task and is not authorized here: the
strict post-estimation review / SA2-readiness verdict is the gate after
the estimation report, and the SA2 verdict is drafted only if that
review passes. Welfare computation, canonical promotion, and M1-clean
displacement remain gated.

---

**Required final statements**

- **The execution repair is cleared.** R1 (post-estimation mode), R2
  (split-stem contract), and R3 (year indicators) are resolved with
  V1–V8 PASS, and preflight v2 returns PASS — EXECUTION-READY across all
  checks.

- **The pooled P3a estimation may now be run**, against the split-stem
  base `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`, under
  the standing execution authorization and its correction, the halt
  conditions H1–H6, and the mandatory post-estimation diagnostics.

- **The V7 placeholder-theta artifact is diagnostic-only.** Its T4
  failure is expected at non-converged theta and is not a blocker; its
  cluster-robust SEs are not valid inference and must be discarded. T3
  (on the converged run), T4, and T5 must be recomputed after
  estimation with the converged pooled theta and the true Hessian.

- **Welfare computation is NOT authorized.** Separately gated behind an
  accepted SA2 verdict.

- **No SA2 verdict is issued, and no output is promoted to canonical
  status.** After estimation, the immediate next gate is the strict
  post-estimation review / SA2-readiness verdict, not the SA2 verdict.

- **M1-clean 2016 remains the active JMP baseline**, through the
  estimation and its post-estimation review, displaced only by a future
  SA2 verdict explicitly promoting the pooled specification.
