# 1. Review verdict

**REJECT.**

The Phase-3 implementation correctly reuses the `dclaborsupply` loader and package-built
JAX negative-log-likelihood, has the correct objective/Jacobian sign convention, uses the
pre-registered L-BFGS-B settings, isolates the optimizer import from the dry-run path, and
contains no Phase 4–8 computation. It must not execute yet because the implementation lacks
the required G-16 in-bounds gate, does not authenticate or recheck every consumed input,
does not protect a prior successful Phase-3 result from a later failed/repeated run, does not
enforce the canonical output root, and does not implement an explicit 37-free-vector ↔
47-name-full-vector mapping.

# 2. Scope

This was an independent static code review of the uncommitted Phase-3 diff. No notebook,
estimation, optimizer, EUROMOD, inference, post-estimation, or welfare operation was run.
Existing production outputs were not altered. Static work was limited to reading files,
inspecting Git state/diffs, parsing Python with `ast`, and parsing YAML with `yaml.safe_load`.

The review answers the 22 requested questions. “Pass” means the reviewed code establishes
the property statically; “fail” means a required property is absent or contradicted; “partial”
means the main path is sound but the contract is incomplete.

# 3. Files reviewed

- `docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase12_manager_acceptance_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_phase3_implementation_report_v1.md`
- `docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v2.md`
- `scripts/p2a/run_p2a_regionlive_rebuild.py`
- `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`
- The Phase-3 Git diff for the runner and config
- `dclaborsupply.data.loader.load_singles`
- `dclaborsupply.likelihood.engine_jax.build_jax_singles_ll`
- `dclaborsupply.solvers.jax_optimize.optimize_lbfgsb` and its bounds helper
- `dclaborsupply.spec.parser.EstimationSpec` ordering, bounds, and parameter-index APIs
- `dclaborsupply.gates.param_binding.check_param_binding`

The nested `dclaborsupply-monorepo` working tree was clean during review. The parent diff
contained the Phase-3 runner/config changes; the acceptance and implementation reports were
untracked. A pre-existing untracked `phase3_estimation_v1/` directory contained only a
manifest and console log. It was inspected as filesystem state but not executed or changed.

# 4. Objective implementation

**Question 1 — Pass.** `_phase3_contract` imports `load_singles` and
`build_jax_singles_ll`, builds the male and female package objectives, and sums them. It does
not duplicate utility, likelihood, proposal-correction, or wage-density mathematics.

**Question 11 — Pass.** `build_jax_singles_ll` returns negative log-likelihood. The runner
minimizes the summed negative log-likelihood, obtains `jax.value_and_grad` of that same
function, passes `(value, gradient)` with `jac=True`, and reports `final_ll = -negll_hat`.
The objective sign, Jacobian sign, bounds argument, and SciPy return interpretation are
coherent.

The direct SciPy call is a documented deviation from the package optimizer wrapper. The
reason is technically sound: the wrapper does not expose `maxcor` and hard-codes `maxls=60`,
whereas the registered checkpoint call requires `maxcor=30` and otherwise uses SciPy
defaults. This does not duplicate likelihood mathematics.

# 5. Input provenance

**Question 2 — Partial.** The data parquet path is formed only from
`run.frozen_stem_name`, currently `fr_p2a_singles2016_regionlive`, and its parquet hash is
checked against the accepted hash before loading. However, the stem name itself and canonical
output root are mutable config/CLI values and are not asserted against fixed accepted values.
The companion `__mnlmeta.json` is loaded but not hash-checked.

**Question 3 — Fail.** Before optimization the runner checks hashes for the geometry
parquet, frozen-stem parquet, certified spec, certified warm start, and stored start-theta
CSV. It does not hash-check every consumed input: notably the frozen-stem metadata,
`rebuild_manifest.json`, and `dry_run_report.json` are trusted after status/content checks.
It also does not compare the Phase 1–2 manifest’s recorded script/config hashes with accepted
anchors.

**Question 21 — Pass for named stale estimates, partial for evidence trust.** The estimation
path uses the accepted `theta_p2a_singles_2016_v1.csv` trial column and does not read an old
P2a result, SE, post-estimation, or welfare artifact. It does, however, trust unhashed
Phase 1–2 JSON evidence, so stale or substituted evidence is not categorically excluded.

S-8 also requires detection of input changes during a run. The code hashes selected files
only before optimization and never rechecks them after optimization, so a mid-run change is
undetected.

# 6. Parameter binding

**Question 4 — Partial.** The certified spec supplies 47 ordered names. The configured ten
pin names are removed from the logical `free` name list, giving 37, and the code checks those
counts. It does not check uniqueness of the pin list, set equality against a separately
accepted pin-name set, or use the package parameter-binding gate in Phase 3.

**Question 6 — Fail.** There is no explicit 37-vector representation and therefore no
free-to-full expansion or full-to-free projection to verify in both directions. SciPy is
given the complete 47-vector and 47 bounds, with ten bounds set to `(pinned_at, pinned_at)`.
Name-index lookups are internally consistent, but equal bounds are not the requested explicit
37↔47 mapping. Implement and test projection/expansion helpers, including round-trip and
ordering assertions.

# 7. Pin handling

**Question 5 — Partial.** The ten pins are clamped to equal lower/upper bounds, their start
values are replaced by certified warm-start values, and final values are checked bitwise.
This should keep them fixed under L-BFGS-B, but the optimizer is still passed 47 coordinates
rather than a 37-coordinate free vector. Thus preservation is guarded, while literal
exclusion from the optimization vector is not established.

Pin values are mapped by the 47-name index and output by name correctly. Add assertions that
pin names are unique, exist in the spec, exactly equal the accepted pin-name set, and are
disjoint from the free set.

# 8. Bounds and bound hits

**Question 9 — Pass.** The expected two bound parameters are derived from the accepted stored
theta and spec bounds at epsilon `1e-5`, then cross-checked with the named configured
expectation. They are not silently hard-coded only at the post-fit gate.

**Question 10 — Pass.** The detected final non-pin bound-hit set must exactly equal the
derived expected set; an additional, missing, or different hit produces `STOPPED`/S-3.

**G-16 defect.** The plan requires an explicit no-free-parameter-below-`lo−1e-9` or
above-`hi+1e-9` gate. The Phase-3 config has no G-16 tolerance and `_phase3_estimate` computes
distances but never gates them. Reliance on SciPy’s box constraints is not equivalent to
persisting and enforcing G-16. Add a named `g16_inbounds_ok` diagnostic and S-3 stop.

# 9. Gradient gate

**Question 7 — Pass.** `grad_hat[i]` uses the same `idx` map derived from
`spec.all_param_names`; the diagnostics row and full gradient vector therefore follow the
47-name order.

**Question 8 — Pass, contingent on the expected-bound derivation.** The gate constructs
`nonbound_free = free − expected_bounds` and evaluates exactly those 35 named components.
The two expected bound parameters and ten pins are excluded. Add an explicit
`len(nonbound_free) == 35` assertion rather than relying only on upstream counts.

# 10. Optimizer configuration

**Question 12 — Pass for the current config.** The call is `L-BFGS-B` with
`maxiter=5000`, `maxcor=30`, `ftol=1e-15`, and `gtol=1e-10`, exactly matching the
pre-registered settings. No polish or alternate optimizer is present.

For stronger fail-closed behavior, validate `phase3.optimizer.method == "L-BFGS-B"` and
validate that the option-key set is exactly the four registered keys. The method is currently
hard-coded at the call site, while an inconsistent config value would only be misleading
metadata.

# 11. Target-objective gate

**Question 13 — Pass.** The final gate uses
`abs(negll_hat - target) <= objective_tol_full`. Both a materially worse and a materially
better objective therefore become `REVIEW_REQUIRED_TARGET_MISMATCH`, not an automatic pass.
The pre-optimization reproduction gate is also two-sided.

# 12. Output isolation

**Question 14 — Fail.** The named artifact paths are placed under the configured
`phase3_estimation_v1` subdirectory, but confinement is not canonical:

- `--out` can point to any filesystem directory.
- `OutRoot` proves only that paths remain below that caller-selected directory.
- `phase3.output_subdir` is not asserted to equal `phase3_estimation_v1`.
- Phase-3 paths are constructed directly from `out3`, bypassing an additional canonical
  phase-subdirectory guard.

Require the resolved output root to equal
`MNL/outputs/p2a_singles2016/region_live_v1` (unless a separately authorized test-only root
is explicitly supported), require the exact Phase-3 subdirectory name, and route every
Phase-3 write through a guard rooted at that directory.

# 13. Atomicity and failure handling

Individual files use temporary-file plus `os.replace`, so each file replacement is atomic.
The artifact set as a whole is not atomic.

**Question 15 — Fail.** `run_phase3` creates/reuses a fixed directory and has no
prior-success refusal, attempt directory, lock, backup, or publish transaction. A new dry-run
can overwrite a successful manifest/console. A new real run writes diagnostics, theta, and
results sequentially to the same names. A failure after one replacement can leave a mixed
old/new artifact set and can overwrite a prior success.

**Question 16 — Pass for ordinary caught failures, with a durability caveat.** `StopRun` and
unexpected exceptions are caught and `finalize` writes a `STOPPED` manifest before returning
a nonzero code. Post-optimizer gate failures also persist diagnostics and then a stopped
manifest. This is not guaranteed for process termination, disk failure, or failure inside
`finalize`, and the overwrite defect means the STOPPED evidence may replace successful
evidence. The console’s final “manifest status” message is logged after the console file is
written, so that last line is absent from the persisted console log.

The manifest’s `artifact_hashes` is computed before replacing the manifest. If a prior
manifest exists, its old hash can be recorded as the new manifest’s hash; on a first run,
the manifest is omitted. Do not self-hash the manifest this way.

# 14. Phase 1–2 regression safety

**Question 17 — Pass by control-flow inspection.** `--phase 3` routes to `run_phase3`
before the Phase 1–2 orchestration. Phase 1–2 functions and their ordinary route remain
present. Phase 3 reads Phase 1–2 evidence and does not call their builders or writers.

**Question 18 — Pass.** The sole `scipy.optimize.minimize` call is inside
`_phase3_estimate`. `run_phase3` returns from the dry-run branch before calling that
function, and checks that `scipy.optimize` has not been loaded at both dry-run boundaries.
The AST inspection found one `minimize` call site only.

No Phase-3 dry-run was performed during this review.

# 15. Prohibited-operation audit

**Question 19 — Pass.** The Phase-3 path contains no Hessian, eigenvalue, rank, scores,
sandwich SE, inference, post-estimation, cold-reload, or welfare operation. CLI phases above
3 are refused.

**Question 20 — Pass for the reviewed diff.** The Phase-3 diff modifies the runner and
config only. The nested package repository was clean, and no notebook or certified baseline
file was modified by this implementation diff. The runner does not import or call EUROMOD or
draw-generation code in Phase 3.

The module-presence guard is useful defense in depth but is not a complete call audit:
Python code imported under an unexpected module name would not be detected. Static inspection
found no such prohibited calls in the Phase-3 path.

# 16. Reproducibility

**Question 22 — Partial.** The runner is a CLI entry point and records Python/package-repo Git
state, script/config hashes, objective inputs, named parameters, optimizer settings, start
and final vectors, and diagnostics. The accepted evidence also records a prior fresh-process
Phase 1–2 objective reload.

Phase 3 itself does not establish a fresh-process guarantee because it does not pin or
validate installed dependency versions beyond limited manifest fields, does not authenticate
all consumed evidence, does not recheck inputs after optimization, permits an arbitrary
output root/configured stem, and has no Phase-3 fresh-process reload test. A fresh process can
run the code, but identical and provenance-safe reproduction is not yet enforced.

Static validation performed:

- Python AST parse: PASS.
- YAML safe parse: PASS.
- Phase-3 configured optimizer values: exact match to the four registered settings.
- Static optimizer call count: one, inside `_phase3_estimate`.
- Phase > 3 refusal: present.
- No execution, import of the runner, compile-to-bytecode, notebook run, or optimizer test.

# 17. Defects found

1. **Critical — prior successful results can be overwritten.** Fixed artifact names are
   replaced by dry-runs, failed runs, and repeated runs; the multi-file result is not
   transactionally published.
2. **High — G-16 is absent.** No explicit free-parameter in-bounds diagnostic or stop exists.
3. **High — input provenance is incomplete.** Stem metadata and accepted Phase 1–2 JSON
   evidence are consumed without accepted hash checks; inputs are not rehashed after
   optimization.
4. **High — output confinement is configurable rather than canonical.** Arbitrary `--out`
   and a mutable subdirectory value can redirect Phase-3 writes outside the authorized
   production location.
5. **High — explicit 37↔47 mapping is absent.** The optimizer receives 47 coordinates with
   ten equal bounds instead of a 37-coordinate free vector expanded into the 47-name vector.
6. **Medium — pin identity is under-validated.** Counts are checked, but uniqueness and exact
   accepted pin-name set equality are not.
7. **Medium — artifact-set atomicity and manifest self-hashing are incorrect.** Per-file
   replacement can leave mixed vintages, and the manifest can record its predecessor’s hash.
8. **Low — persisted console omits the final status line.** Logging occurs after the console
   file replacement.

# 18. Required fixes

1. Implement explicit ordered `free_names`, `project_full_to_free`, and
   `expand_free_to_full` helpers; optimize the 37-vector while injecting ten immutable pins
   into the package objective. Add round-trip, order, count, uniqueness, and pin-bitwise tests.
2. Add and persist G-16 with epsilon `1e-9`; stop S-3 on any free parameter outside bounds.
3. Extend the accepted contract to hash every consumed file, including frozen-stem metadata,
   Phase 1–2 manifest, and dry-run report. Recheck every input hash after optimization and
   before publishing results.
4. Assert the canonical resolved root and exact `phase3_estimation_v1` subdirectory. If test
   roots are needed, separate them behind an explicit non-production mode.
5. Refuse to overwrite a prior `PHASE_3_COMPLETE`; use unique attempt staging plus an atomic
   publish/rename strategy so a failed run cannot alter the last successful artifact set.
6. Validate the exact accepted pin-name set and exact optimizer method/option-key set.
7. Correct artifact hashing and write the complete console before atomic replacement.
8. Add safe tests using a fake objective/fake optimizer result or dependency injection. Tests
   must verify mapping, signs, gates, dry-run optimizer prohibition, STOPPED evidence,
   canonical path refusal, and successful-result preservation without invoking real
   estimation.

# 19. Whether Phase 3 may execute

**No.** Phase 3 must not execute while the critical/high defects above remain. The correct
final verdict is **REJECT**, not approval after runtime observation: the missing safeguards
are statically demonstrable and a real run could overwrite accepted evidence or publish a
result without all registered gates.

# 20. Immediate next action

Implement the required fixes in the runner/config and add non-optimizing unit tests for the
contracts and failure paths. Then request a second independent static review. Only an
`APPROVE` verdict from that review should unblock the first real Phase-3 execution.
