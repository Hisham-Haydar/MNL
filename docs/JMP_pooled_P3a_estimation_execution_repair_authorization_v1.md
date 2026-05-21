# JMP Pooled P3a Estimation — Execution Repair Authorization v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Specification class: narrow repair authorization memo. This memo
authorises the resolution of the three execution blockers that the
pooled P3a estimation preflight found, and nothing more. It does not
re-authorise the estimation itself (that authorization already exists
in `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and
its correction); it authorises only the narrow infrastructure repairs
that must complete before the existing estimation authorization can be
acted on. The pooled solver is not run by this memo. Welfare is not
computed. No SA2 verdict is issued. No output is promoted to canonical
status. M1-clean 2016 remains the active JMP baseline.

Reference documents:
- `Results/JMP_pooled_P3a_estimation_preflight_report_v1.md` (the
  preflight HALT — DO NOT RUN SOLVER verdict; PF6/PF7 primary HALT;
  PF8, PF9 data-loading blockers)
- `docs/JMP_pooled_P3a_estimation_execution_authorization_v1.md` and
  `docs/JMP_pooled_P3a_estimation_execution_authorization_correction_v1.md`
  (the estimation authorization being unblocked — unchanged in scope)
- `docs/RURO_occ_P3a_pooled_GA17_clearance_addendum_v1.md` (GA17
  smoke-test callability CONFIRMED; T3 full-count / T4 / T5 deferred)
- `docs/RURO_cluster_robust_SE_implementation_report_v1.md`,
  `docs/RURO_cluster_robust_SE_implementation_correction_v1.md`,
  `Results/RURO_cluster_robust_SE_static_validation_v1.md` (the
  cluster-robust SE infrastructure and its smoke-test validation)
- `scripts/enhanced/run_cluster_robust_se.py` (the post-estimation
  mode being implemented under R1)
- `scripts/enhanced/enh_RURO_estimate_FR.py` (the estimator whose
  split-stem data contract is satisfied under R2/R3)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to authorise a narrow, well-scoped repair
that clears the three execution blockers the pooled P3a estimation
preflight identified, so that the already-authorised pooled estimation
can subsequently be run under a clean preflight. The memo authorises
exactly three repairs and nothing beyond them.

The preflight returned **HALT — DO NOT RUN SOLVER**. It found three
blockers. First (PF6/PF7, the primary HALT): the post-estimation mode
of `run_cluster_robust_se.py` is scaffolded but not implemented — it
returns "Post-estimation mode not yet implemented in this smoke-test
release." and exits 1 — so the true-Hessian cluster-robust standard
errors that the estimation authorization requires (§14 R1–R4, §19)
cannot be produced after convergence. Second (PF8): `enh_RURO_estimate_FR.py`
expects split `{mnl_base}__singles.parquet` and `{mnl_base}__couples.parquet`
inputs with a `{mnl_base}__mnlmeta.json`, while the pooled P3a object is
a single unified parquet (`fr_p3a_gsurv2_harmonised.parquet`) with a
`household_type` column. Third (PF9): the market-opportunity shifters
`year_2015_indicator` and `year_2017_indicator` are absent from the
pooled parquet and do not match the engine's automatic one-hot
derivation pattern, so they resolve to `None` and the year effects
cannot be estimated.

This memo authorises the repairs R1, R2, and R3 that resolve these
blockers, fixes the preferred repair route for R2/R3 (the
estimation-ready split-stem route, §7), and binds the validation that
must pass before the estimation may proceed. It does not authorise the
estimation, the welfare computation, the SA2 verdict, canonical
promotion, or any displacement of M1-clean. The repairs are
infrastructure-only: no solver invocation, no parameter estimate, no
welfare object.

---

## 2. Current preflight verdict

**The pooled P3a estimation preflight verdict is HALT — DO NOT RUN
SOLVER. The estimation is not started; no solver was invoked.**

The preflight report records three blocking issues. PF6/PF7 is the
primary HALT: `run_cluster_robust_se.py --mode post-estimation` is
scaffolded only — the CLI flag and the `--results-json` argument exist,
but the mode body logs "Post-estimation mode not yet implemented in
this smoke-test release." and returns exit code 1, with no
`compute_scores_joint` call, no true-Hessian computation, no sandwich
assembly, and no T3/T4/T5 diagnostics. PF8 and PF9 are additional
data-loading blockers that would prevent the estimation from running
even if PF6/PF7 were resolved: the estimator's split-stem data contract
is unmet for the unified pooled parquet (PF8), and the two year
indicators are absent and do not auto-derive (PF9).

The preflight per its own halt rule did not run the solver. No
estimation result exists. M1-clean 2016 remains the active JMP baseline
and is not displaced.

---

## 3. What passed in preflight

The following preflight checks passed and require no repair. They are
recorded here so the repair is not over-scoped: the repair must not
touch anything in this list.

- **PF1 (CLI syntax, with the PF8 caveat).** All estimator flags exist
  in `enh_RURO_estimate_FR.py`: `--mnl-base`, `--metadata`,
  `--spec-config`, `--output-dir`, `--group joint`,
  `--solver gamspy-conopt`, `--vectorized`, `--warm-start`,
  `--init-params`. The caveat is that `--mnl-base` requires the
  split-stem files (PF8), which the repair supplies under R2.
- **PF2 (M1-clean warm-start results JSON).** The M1-clean
  `estimation_results.json` exists (53 parameters; LL = −6487.55;
  `success = True`) and is the Start 1 warm-start source.
- **PF3 (Start 1 mapping).** The 53 M1-clean parameters map 1:1 to the
  55 pooled positions, with `beta_E_y2015 = 0.0` and `beta_E_y2017 = 0.0`
  at positions 35–36.
- **PF4 (Start 2).** `--warm-start none` is valid and initialises all
  55 parameters at the YAML `initial_values`.
- **PF5 (Start 3).** The perturbed Start 1 vector (seed 42, ±0.1) can
  be written to JSON and passed via `--init-params`; no solver blocker.
- **The pooled YAML and parquet structural validity.** The 55-parameter
  pooled YAML parses (Gate-A PASS, 53 M1-clean frozen + 2 year dummies);
  the pooled parquet exists (1,244,500 rows, 146 columns); `idorighh`
  is present and `cluster_id == idorighh` holds on the bounded sample.
- **GA15 income columns present.** `ils_dispy_real`, `ils_dispy_male`,
  and `ils_dispy_female` all exist in the pooled parquet.
- **Region and occupation dummies build.** `reg_nuts1_2`–`reg_nuts1_8`
  and `loc4` / `loc4_male` / `loc4_female` exist and build via the
  existing code path.
- **GA17 smoke-test callability CONFIRMED.** C1–C17 pass; the score
  interface, meat assembly, and sandwich call are correct at
  initial_values with a dummy Hessian.
- **Cluster-key strictness safeguard active.** Both
  `precompute_data_singles` and `precompute_data_couples` use
  `idorighh` and log an explicit warning rather than silently falling
  back to `idhh`.

Nothing in this list is reopened by the repair.

---

## 4. Blocking issue R1: post-estimation cluster-robust SE mode

**Blocker.** `scripts/enhanced/run_cluster_robust_se.py`, in
`main()`, the `post-estimation` branch validates that `--results-json`
is provided and exists, then logs "Post-estimation mode not yet
implemented in this smoke-test release." and returns 1. There is no
callable path to the true-Hessian cluster-robust standard errors.

**Why it blocks.** The estimation authorization (§14 R1–R4; §19, as
corrected) requires that after each converged start the cluster-robust
SEs are computed with the **true Hessian** — the numerical Hessian of
the negative log-likelihood at the converged theta — not the dummy
Hessian `H = 0.1 × I` used in the smoke test. The GA17 clearance
explicitly deferred T3 (full 9,657-cluster count), T4 (robust-SE
positivity), and T5 (robust-vs-Hessian comparison) to this
post-estimation stage. With the mode unimplemented, the stated
inference deliverable of the pooled estimation cannot be produced and
the mandatory post-estimation diagnostics D9/D10/D11 cannot be run.
This is the primary HALT condition.

**Repair (R1).** Implement the `post-estimation` mode of
`run_cluster_robust_se.py` so that, given a converged-theta estimation
results JSON, it:
1. loads the converged 55-parameter theta for the nominated start;
2. loads the full pooled dataset (no smoke-test row bound) and builds
   the precomputed singles and couples data objects;
3. calls `compute_scores_joint(theta_converged, data_sm, data_sf,
   data_cou, spec)` to extract the per-choice-set scores and aligned
   cluster ids on the full dataset;
4. obtains the **true Hessian** as the sandwich bread — either by
   loading it from the estimation results / a saved Hessian artifact,
   or by recomputing it via the estimator's existing
   `compute_standard_errors` central-difference Hessian on
   `compute_gradient_joint` at the converged theta — and must NOT use
   the dummy Hessian;
5. calls `compute_cluster_robust_se(hessian_true, scores_all,
   cluster_ids_all, free_mask)` to assemble the sandwich VCV with the
   `free_mask` excluding fixed/bounded parameters;
6. runs T3 (confirm exactly 9,657 unique `idorighh` clusters on the
   full dataset), T4 (robust-SE positivity for all free parameters),
   and T5 (robust-vs-Hessian SE comparison with the per-parameter
   ratio, flagging any robust SE smaller than its Hessian SE);
7. writes the cluster-robust SE vector, the robust VCV matrix (or a
   documented output path to it), and the T3/T4/T5 diagnostic results.

The existing `--mode smoke-test` interface and behaviour must be
preserved byte-for-byte (§7, R2-smoke preservation).

---

## 5. Blocking issue R2: split-data estimator contract

**Blocker.** `enh_RURO_estimate_FR.py` lines 1180–1187 unconditionally
construct the data paths by appending fixed suffixes to `--mnl-base`:

```python
mnl_base    = Path(args.mnl_base)
singles_path = Path(str(mnl_base) + "__singles.parquet")
couples_path = Path(str(mnl_base) + "__couples.parquet")
metadata_path = Path(str(mnl_base) + "__mnlmeta.json")   # unless --metadata
df_singles, df_couples, metadata = load_and_validate_mnl_data(
    singles_path=singles_path,
    couples_path=couples_path if couples_path.exists() else None,
    metadata_path=metadata_path, ...)
```

There is no `--parquet` flag; the loader has no unified-parquet path.
The pooled P3a object is a single unified parquet
(`fr_p3a_gsurv2_harmonised.parquet`) with a `household_type` column
(`single` / `couple`) and no pre-split `__singles.parquet` /
`__couples.parquet` counterparts. Running the estimator with
`--mnl-base .../fr_p3a_gsurv2_harmonised` therefore fails because the
expected split-stem files do not exist.

**Why it blocks.** The estimator cannot load the pooled data in its
current form. The split-stem contract is a hard precondition of
`load_and_validate_mnl_data`.

**Repair (R2).** Produce the three estimation-ready split-stem files
from the unified pooled parquet, so the estimator's existing contract
is satisfied without modifying the loader. The split-stem route is the
preferred route (§7). The deeper alternative — rewriting
`enh_RURO_estimate_FR.py` to consume a unified parquet via a new
`--parquet` flag and an internal `household_type` split — is NOT the
preferred route and is authorised only as a fallback if the split-stem
route proves impossible (§7, §9).

---

## 6. Blocking issue R3: missing year indicators

**Blocker.** The pooled parquet contains `year_tag` (integer values
1/2/3) but not `year_2015_indicator` or `year_2017_indicator`. The
pooled YAML requires both as market-opportunity shifters (positions
35–36). The engine's `_extract_or_derive_single` regex one-hot
derivation matches the pattern `colname_N` (e.g. `year_tag_1`) but not
names ending in `_indicator`, so `year_2015_indicator` and
`year_2017_indicator` resolve to `None`. The smoke test already emitted
`"skipping 'year_2015_indicator' not found on data"` warnings.

**Why it blocks.** Without the two indicators, the pooled year effects
`beta_E_y2015` and `beta_E_y2017` — the two parameters that distinguish
the pooled specification from M1-clean — cannot enter the likelihood,
and the estimation degenerates to a malformed run.

**Repair (R3).** Derive the two indicators from `year_tag` and write
them as columns into the split-stem outputs (§7), so they are present
on the estimation-ready data the estimator loads. The derivation is:

```
year_2015_indicator = 1[year_tag == 1]
year_2017_indicator = 1[year_tag == 3]
```

(stored as float 0.0/1.0). This modifies neither the YAML nor the
source unified parquet; the indicators are materialised only in the
new estimation-ready split-stem files. The lower-risk
derive-at-split-time option is preferred over renaming the YAML
shifters to `year_tag_1` / `year_tag_3`, which would modify the
specification and is not authorised.

---

## 7. Preferred repair route

The preferred repair route is the **estimation-ready split-stem
route**: build pre-split estimation-ready inputs from the unified
pooled parquet so the estimator's existing split-stem contract is
satisfied unchanged, and implement the `run_cluster_robust_se.py`
post-estimation mode against the converged result and the true Hessian.
This route is chosen because it leaves the estimator's validated data
loader (`load_and_validate_mnl_data`), its income routing, and its
group-filtering logic untouched, confining the repair to (a) a new
data-preparation step and (b) the cluster-robust SE post-estimation
mode. The deeper alternative of rewriting the estimator to consume
unified parquets is rejected as the default because it modifies the
estimation engine's load path, which carries a higher risk of
silently altering the M1-clean-frozen behaviour.

**R2/R3 — create the split pooled inputs.** From
`Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`, produce:

- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json`

The split is by `household_type` (`single` → singles file; `couple` →
couples file). The two year indicators are derived during the split
(R3) and written into both split files:
`year_2015_indicator = 1[year_tag == 1]`,
`year_2017_indicator = 1[year_tag == 3]`. The cluster key is preserved:
`cluster_id = idorighh` is carried into both split files unchanged.
The household-type-specific income routing is preserved exactly:
singles carry `ils_dispy_real`; couples carry `ils_dispy_male` and
`ils_dispy_female`; no step assumes the scalar `ils_dispy_real` covers
couples, and the couples file's consumption path must not read
`ils_dispy_real`. The `__mnlmeta.json` is produced in the format
`load_and_validate_mnl_data` expects (the normalization and draw-count
metadata), sourced from or consistent with the existing pooled
`__stage_m1_meta.json`. The estimator is then run (under the existing
authorization, not this memo) with
`--mnl-base Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready`.

**Do NOT deeply modify `enh_RURO_estimate_FR.py`** to consume unified
pooled parquets unless the split-stem route proves impossible. If, and
only if, the split-stem route is demonstrably impossible (for example,
if `load_and_validate_mnl_data` cannot validate the split files for a
structural reason that cannot be fixed in the data-preparation step),
the fallback is a minimal `--parquet` addition to the estimator; that
fallback must be reported, justified, and validated before use, and is
not the authorised default.

**R1 — implement the post-estimation mode** of
`run_cluster_robust_se.py` per §4, using the converged estimation
result and the true Hessian / bread, and preserving the existing
`--mode smoke-test` interface unchanged.

**Post-estimation CLI (R1) — final supported interface.** The current
smoke-test CLI uses `--spec` and `--parquet`. The repair must document
the exact final post-estimation invocation. The post-estimation mode
must support, at minimum, the spec, the data source, the converged
results JSON, the cluster column, and the output path. The repair may
extend the CLI with aliases such as `--spec-config` (alias of
`--spec`), `--mnl-base` (the estimation-ready split-stem base, as an
alternative data source to `--parquet`), and `--cluster-col` (default
`idorighh`) only if needed, but the final supported interface — every
flag, its meaning, its default, and the exact post-estimation
invocation string — must be documented in the repair report (§13). The
smoke-test invocation (`--spec`, `--parquet`, `--output`,
`--mode smoke-test`) must remain valid and unchanged.

---

## 8. What is authorized

The following are authorized by this memo, and only these.

- **(A1) Implement R1** — the `post-estimation` mode of
  `scripts/enhanced/run_cluster_robust_se.py`, so it computes
  true-Hessian cluster-robust SEs from a converged estimation result
  and runs T3/T4/T5, per §4 and §7. The existing `--mode smoke-test`
  interface must be preserved unchanged.
- **(A2) Implement R2/R3** — create the estimation-ready split-stem
  inputs from `fr_p3a_gsurv2_harmonised.parquet`
  (`...__singles.parquet`, `...__couples.parquet`,
  `...__mnlmeta.json`), splitting by `household_type`, deriving the two
  year indicators from `year_tag`, preserving `cluster_id = idorighh`,
  and preserving the household-type-specific income routing, per §5,
  §6, §7.
- **(A3) Document the final post-estimation CLI** — the exact supported
  flags, defaults, and invocation string for
  `run_cluster_robust_se.py --mode post-estimation`, including any
  added aliases, per §7 and §13.
- **(A4) Run the repair validation checks** (§11) — the static and
  smoke-level checks that confirm the split files load, the year
  indicators are present and correct, the income routing is preserved,
  the cluster key is preserved, and the post-estimation mode is
  callable. These checks do not invoke the pooled solver.
- **(A5) Write the repair report** (§13) and the new split-stem files
  to their versioned/documented paths.

---

## 9. What is not authorized

The following are NOT authorized by this memo. Each remains gated.

- **(N1) Running the pooled solver.** No pooled estimation is run by
  this memo. The estimation remains gated behind the existing execution
  authorization and a clean re-run of the preflight.
- **(N2) Welfare computation.** No welfare object is computed.
  Separately gated behind an accepted SA2 verdict.
- **(N3) The SA2 verdict.** No SA2 verdict is issued. The SA2 verdict
  and the strict post-estimation review that precedes it are later
  gates.
- **(N4) Canonical promotion.** No output — the split-stem files, the
  implemented post-estimation mode, any future estimate — is promoted
  to canonical status. The split files are estimation-ready candidate
  inputs at a versioned/documented path.
- **(N5) M1-clean displacement.** M1-clean 2016 remains the active JMP
  baseline. The repair does not displace it.
- **(N6) Deep modification of `enh_RURO_estimate_FR.py`.** The
  estimator's unified-parquet `--parquet` fallback (§7) is not the
  authorised default and may be implemented only if the split-stem
  route proves impossible, with justification and validation in the
  repair report. No other modification of the estimator's load path,
  income routing, or group filtering is authorised.
- **(N7) Modifying the YAML specification or the source unified
  parquet.** The pooled YAML, the M1-clean YAML, the M1-naive YAML, and
  `fr_p3a_gsurv2_harmonised.parquet` are not modified. The year
  indicators are materialised only in the new split-stem files.
- **(N8) Modifying existing estimation outputs or the smoke-test
  interface.** The M1-clean results and the `--mode smoke-test`
  behaviour are not changed.

---

## 10. Required repair outputs

The repair must produce the following outputs.

- **(O1) The implemented post-estimation mode** in
  `scripts/enhanced/run_cluster_robust_se.py`, replacing the
  "not yet implemented" stub with the §4 implementation, with the
  smoke-test interface preserved.
- **(O2) The three estimation-ready split-stem files:**
  - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`
  - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`
  - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json`
- **(O3) The data-preparation script** that produces O2 from the
  unified pooled parquet (deriving the year indicators, preserving the
  cluster key and income routing), written to a versioned path under
  `scripts/`.
- **(O4) The documented final post-estimation CLI** — the exact flags,
  defaults, and invocation string — recorded in the repair report.
- **(O5) The repair report** (§13) at
  `Results/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`.

No solver output, no estimate, no welfare object, and no canonical
artifact are produced.

---

## 11. Required validation checks

The repair must pass the following checks. None of them invokes the
pooled solver.

- **(V1) Split files load via the estimator's loader.**
  `load_and_validate_mnl_data` accepts the three split-stem files with
  `strict_validation=True` and returns non-empty `df_singles` and
  `df_couples`, with the metadata parsed.
- **(V2) Row-count conservation.** The singles and couples split rows
  sum to the unified pooled parquet's row count (1,244,500), and the
  household-year and cluster counts are conserved (12,445
  household-years; 9,657 unique `idorighh`).
- **(V3) Year indicators present and correct.** Both split files
  contain `year_2015_indicator` and `year_2017_indicator` as float
  columns, with `year_2015_indicator == 1` iff `year_tag == 1`,
  `year_2017_indicator == 1` iff `year_tag == 3`, and both `0` iff
  `year_tag == 2`.
- **(V4) Cluster key preserved.** `cluster_id == idorighh` holds on
  both split files; `idorighh` is present and non-null.
- **(V5) Income routing preserved.** The singles file carries
  `ils_dispy_real` (non-null for singles); the couples file carries
  `ils_dispy_male` and `ils_dispy_female`; the couples consumption path
  does not read `ils_dispy_real`. No singles/couples income mixing.
- **(V6) Smoke-test interface unchanged.**
  `run_cluster_robust_se.py --mode smoke-test` (with `--spec` and
  `--parquet`) still runs and still returns the C1–C17 PASS validation
  (GA17 smoke-test callability: CONFIRMED).
- **(V7) Post-estimation mode callable (interface-level).**
  `run_cluster_robust_se.py --mode post-estimation` no longer returns
  "not implemented"; it parses its arguments, loads a converged-theta
  results JSON, and reaches the score / true-Hessian / sandwich path.
  Where no real converged theta is yet available, the interface is
  confirmed callable using the M1-clean results JSON or a documented
  placeholder, with the check explicitly labelled as an
  interface-callability check, not a T3/T4/T5 inference confirmation
  (T3/T4/T5 require the converged pooled theta and run during the
  authorised estimation, not in this repair).
- **(V8) Final CLI documented.** The repair report contains the exact
  final post-estimation invocation string and the full flag list with
  defaults.

---

## 12. Halt conditions

The repair halts under the following conditions. Each halt preserves
the outputs produced up to the halt and requires diagnosis before the
repair proceeds.

- **(H1) Split-stem route impossible.** If the split-stem files cannot
  be made to load via `load_and_validate_mnl_data` for a structural
  reason that the data-preparation step cannot fix, the repair halts
  and reports the obstruction before any deep modification of
  `enh_RURO_estimate_FR.py` is attempted. The estimator fallback (§7,
  N6) is considered only after this halt and its diagnosis.
- **(H2) Income routing would be corrupted.** If the split would place
  `ils_dispy_real` on the couples consumption path, or drop the
  gender-specific couples income columns, or mix singles and couples
  income, the repair halts: this would corrupt the couples consumption
  (estimation-authorization H2 carried forward).
- **(H3) Cluster key not preserved.** If the split would not preserve
  `cluster_id = idorighh` (for example, if it would substitute `idhh`),
  the repair halts (estimation-authorization H1 carried forward).
- **(H4) Year indicators wrong.** If V3 fails — if the derived
  indicators do not satisfy `1[year_tag == 1]` / `1[year_tag == 3]`, or
  are absent from a split file — the repair halts.
- **(H5) Row/cluster count not conserved.** If V2 fails — if the split
  loses or duplicates rows, household-years, or clusters — the repair
  halts.
- **(H6) Smoke-test interface broken.** If V6 fails — if the
  post-estimation implementation changes or breaks the existing
  `--mode smoke-test` behaviour — the repair halts.
- **(H7) Solver, welfare, SA2, canonical, or out-of-scope modification
  attempted.** If the repair would invoke the pooled solver, compute
  welfare, issue an SA2 verdict, promote any output to canonical
  status, modify the YAML or the source unified parquet, or make any
  estimator modification beyond the §7 fallback (and only after H1),
  the repair halts: these are not authorised (§9).

---

## 13. Required repair report

The repair must be recorded in a report saved as
`Results/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`. The
report must include:

- the repair verdict (repairs applied; whether the estimation is now
  preflight-ready) and a one-line status per blocker R1, R2, R3;
- the files created and the files modified, with a one-line change
  summary each (the implemented post-estimation mode; the three
  split-stem files; the data-preparation script);
- for R2/R3: the split method (by `household_type`), the row-count and
  cluster-count conservation result (V2), the year-indicator derivation
  and its V3 verification, the cluster-key preservation result (V4),
  and the income-routing preservation result (V5), with explicit
  confirmation that the couples consumption path does not read
  `ils_dispy_real`;
- for R1: the post-estimation mode design (score extraction via
  `compute_scores_joint`; the true-Hessian / bread source, explicitly
  identified as the true Hessian and NOT the dummy Hessian; the
  sandwich assembly via `compute_cluster_robust_se` with the
  `free_mask`); and a statement that T3 (full 9,657-cluster count), T4
  (robust-SE positivity), and T5 (robust-vs-Hessian comparison) are
  computed at estimation time on the converged pooled theta, not in
  this repair;
- the documented final post-estimation CLI: the exact invocation
  string, every flag (including any added aliases such as
  `--spec-config`, `--mnl-base`, `--cluster-col`), each flag's meaning
  and default, and explicit confirmation that the smoke-test invocation
  (`--spec`, `--parquet`, `--output`, `--mode smoke-test`) is unchanged;
- the validation results V1–V8, each PASS/FAIL with detail;
- any halt (§12) and its diagnosis;
- a "what was not executed" section confirming: no solver invoked, no
  estimate produced, no welfare computed, no SA2 verdict, no canonical
  promotion, no YAML or source-parquet modification, no estimator
  modification beyond the documented fallback (if any);
- the five required final statements (below).

**Required final statements (to appear in the repair report):**
- The three execution blockers R1/R2/R3 are repaired (or the repair
  halted, with the halting blocker named).
- The pooled solver was NOT run; no estimate was produced.
- Welfare computation is NOT authorized; none was run.
- No SA2 verdict was issued; no output was promoted to canonical
  status.
- M1-clean 2016 remains the active JMP baseline.

---

## 14. Exact Claude Code task

Tool path: **Claude Code** (local codebase repair). Not the project
chat — this task inspects and modifies local files.

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present before starting: the unified pooled parquet
(`Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`) and its
`__stage_m1_meta.json`; the estimator
(`scripts/enhanced/enh_RURO_estimate_FR.py`) and its loader
(`load_and_validate_mnl_data`); the cluster-robust SE CLI
(`scripts/enhanced/run_cluster_robust_se.py`) and library
(`cluster_robust_se.py`); the pooled YAML
(`estimation_spec_ruro_occ_P3a_pooled.yaml`); this repair
authorization; and the preflight report.

Prompt to use:

> Execute the narrow pooled P3a estimation repair per
> `docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`.
> Use the interpreter `.venv\Scripts\python.exe`. Do NOT run the pooled
> solver. Do NOT compute welfare. Do NOT issue an SA2 verdict. Do NOT
> promote any output to canonical status. Do NOT modify the pooled,
> M1-clean, or M1-naive YAML specifications or the source unified
> parquet. Do NOT replace M1-clean 2016 as the active baseline.
>
> Repair the three preflight blockers R1, R2, R3 via the
> estimation-ready split-stem route.
>
> R2/R3 — Create estimation-ready split inputs from
> `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`:
> - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`
> - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`
> - `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json`
>   Split by `household_type` (`single` / `couple`). Derive
>   `year_2015_indicator = 1[year_tag == 1]` and
>   `year_2017_indicator = 1[year_tag == 3]` (float 0.0/1.0) and write
>   them into BOTH split files. Preserve `cluster_id = idorighh` in both
>   files. Preserve income routing: singles carry `ils_dispy_real`;
>   couples carry `ils_dispy_male` and `ils_dispy_female`; the couples
>   consumption path must NOT read `ils_dispy_real`. Produce
>   `__mnlmeta.json` in the format `load_and_validate_mnl_data` expects,
>   sourced from / consistent with the existing pooled
>   `__stage_m1_meta.json`. Write the data-preparation script to a
>   versioned path under `scripts/`. Do NOT deeply modify
>   `enh_RURO_estimate_FR.py` to consume unified parquets unless the
>   split-stem route proves impossible; if it is impossible, HALT and
>   report before attempting any estimator modification.
>
> R1 — Implement the `--mode post-estimation` path in
> `scripts/enhanced/run_cluster_robust_se.py`, replacing the
> "not yet implemented" stub. It must: load the converged theta from a
> results JSON; load the full pooled data (no smoke bound) and build
> precomputed singles/couples; call `compute_scores_joint`; obtain the
> TRUE Hessian (load it, or recompute via the estimator's
> central-difference Hessian on `compute_gradient_joint` at the
> converged theta) — NOT the dummy Hessian; call
> `compute_cluster_robust_se` with the `free_mask`; and run T3
> (9,657-cluster confirmation), T4 (robust-SE positivity), T5
> (robust-vs-Hessian). Preserve the existing `--mode smoke-test`
> interface and behaviour byte-for-byte. Document the EXACT final
> post-estimation CLI: every flag, default, and the full invocation
> string. The smoke-test CLI uses `--spec` and `--parquet`; you may add
> aliases such as `--spec-config`, `--mnl-base`, `--cluster-col` only if
> needed, but document the final supported interface.
>
> Run the validation checks V1–V8 from the authorization §11 (none
> invoke the solver): split files load via the estimator's loader;
> row/cluster-count conservation (1,244,500 rows; 12,445 household-years;
> 9,657 clusters); year indicators present and correct; cluster key
> preserved; income routing preserved (couples path does not read
> `ils_dispy_real`); smoke-test interface still C1–C17 PASS;
> post-estimation mode callable at the interface level (label it an
> interface-callability check, not a T3/T4/T5 inference confirmation);
> final CLI documented.
>
> HALT conditions: split-stem route impossible (HALT before any
> estimator modification); income routing would be corrupted; cluster
> key not preserved; year indicators wrong; row/cluster count not
> conserved; smoke-test interface broken; any solver, welfare, SA2,
> canonical, or out-of-scope modification attempted.
>
> Save the repair report as
> `Results/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`,
> recording the repair verdict and per-blocker status; files created
> and modified; the R2/R3 split method, conservation, year-indicator,
> cluster-key, and income-routing results; the R1 post-estimation
> design with the true-Hessian source explicitly identified (and a note
> that T3/T4/T5 run at estimation time on the converged pooled theta,
> not in this repair); the documented final post-estimation CLI;
> validation results V1–V8; any halt and diagnosis; a "what was not
> executed" section; and the five required final statements. Write all
> outputs to versioned/documented paths. Do NOT run the solver. Do NOT
> compute welfare. Do NOT issue an SA2 verdict. Do NOT promote
> canonically.

Output to save: the repair report at
`Results/JMP_pooled_P3a_estimation_execution_repair_report_v1.md`, plus
the three split-stem files (O2), the data-preparation script (O3), and
the implemented post-estimation mode (O1).

What to do next: return the repair report to the project chat for a
re-run of the pooled P3a estimation preflight against the
estimation-ready split-stem inputs and the implemented post-estimation
mode. Only after a clean preflight pass may the pooled estimation be
run under the existing execution authorization and its correction. The
SA2 verdict, welfare computation, canonical promotion, and M1-clean
displacement remain gated and are not authorised by this repair.

---

**Required final statements**

- **The narrow repair of the three preflight blockers (R1, R2, R3) is
  authorized** via the estimation-ready split-stem route: implement the
  `run_cluster_robust_se.py` post-estimation mode (R1); create the
  three `fr_p3a_gsurv2_estimation_ready__{singles,couples}.parquet` /
  `__mnlmeta.json` files from the unified pooled parquet, deriving the
  two year indicators from `year_tag`, preserving `cluster_id =
  idorighh`, and preserving the household-type-specific income routing
  (R2/R3).

- **The pooled solver is NOT run by this memo.** The estimation remains
  gated behind the existing execution authorization and a clean re-run
  of the preflight.

- **Welfare computation is NOT authorized.** Separately gated behind an
  accepted SA2 verdict.

- **No SA2 verdict is issued, and no output is promoted to canonical
  status.** The split-stem files are estimation-ready candidate inputs
  at a versioned/documented path.

- **M1-clean 2016 remains the active JMP baseline.** The repair does
  not displace it.
