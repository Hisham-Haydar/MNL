# FR P2a Region-Live — Production Rebuild Plan — v1

Plan-only document. Date: 2026-07-22 (reconciled 2026-07-23). Author: senior econometric software
architect (planning role). No file other than this plan was created; no code was written; no
estimation, EUROMOD, notebook, or welfare computation was run; no output was rewritten; the certified
pooled baseline (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987) is untouched and unaffected.

> **Reconciliation note (2026-07-23).** The manager decisions D-1…D-8 are now **ratified** in
> `FR_P2a_region_live_manager_decisions_v1.md`. This plan has been reconciled to that ratified text.
> Four changes were applied where the manager **amended** the plan's original recommendations:
> (1) **D-3** — added the required conditional regional-information (regional Schur-complement) test as
> hard gate **R-4**; (2) **D-3** — reclassified the regional-loading-share test **R-3** from a hard
> pass/fail gate to a **warning-only diagnostic** (removed from G-9 and stop-condition S-5);
> (3) **D-4** — encoded the three-tier condition-number scheme (≤1e7 clean / 1e7–1e10 warning /
> >1e10 hard failure); (4) **D-1** — tightened §8 so the runner **fully rebuilds `er_b` from
> draws/pricing** per §§12–§12b (with the on-disk frames as equality cross-checks) rather than
> reconstructing only the five revived columns. §25 now records the ratified decisions, not
> recommended defaults.

Companion governance documents: `Job_Market_paper/docs/JMP_cross_repo_manager_handoff_v1.md`,
`JMP_cross_repo_artifact_manifest_v1.md`, `JMP_open_decisions_cross_repo_v1.md`,
`dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md`.

---

## 1. Plan verdict

**READY TO IMPLEMENT.** (Was "READY AFTER MANAGER DECISIONS"; the decisions D-1…D-8 were ratified
2026-07-23 and this plan reconciled to them — see the reconciliation note above and §25.)

The rebuild is architecturally unambiguous: every required computational primitive exists and is
validated (loader, JAX engine, L-BFGS-B wrapper, exact JAX Hessian + verdict, chunked cluster
scores + T1–T5 sandwich, styled post-estimation), the target negLL 19053.4655 is reproduced by an
executed pipeline notebook cell with an in-notebook anchor assert, and the data-wiring repair is
fully understood (five columns mapped from source by `idhh`). Nothing technical blocks
implementation.

What blocks *execution* is pre-registered gate discipline: three required gate categories have **no
existing threshold anywhere in the project** (cold-reload negLL tolerance, numerical-rank tolerance,
region × urbanisation block-rank criterion), four more have **inconsistent values across sources**
(T1 score-identity tolerance, bound-hit epsilon, condition-number cutoff, optimizer-success
definition), and one **input-selection decision** (which of the three on-disk region-live engine-ready
frames is canonical) must be made by the manager, because the on-disk state moved *after* the
2026-07-22 audit (see §3). Section 25 enumerates the decisions with recommended defaults; once they
are ratified the plan is READY TO IMPLEMENT with no further design work.

## 2. Evidence inspected

Documents (read in full):

- `Job_Market_paper/docs/JMP_cross_repo_manager_handoff_v1.md` (verdicts, baseline, blocker, next gate)
- `Job_Market_paper/docs/JMP_cross_repo_artifact_manifest_v1.md` (artifact status registry, §F missing artifacts)
- `Job_Market_paper/docs/JMP_open_decisions_cross_repo_v1.md` (A1–A4 central decisions)
- `dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md` (§1–§17)
- `MNL/outputs/p2a_singles2016/P2A_MASTER_RECORD.md` (two-vintage header, 2026-07-22 doc-repair)
- `MNL/p2a_fit_provenance.json` (negll_fit 19053.46553160094; pointer-status notes)
- `MNL/outputs/p2a_singles2016/estimation_results_p2a_singles2016.json` (schema; final_ll −19053.46553160094; 10 pins; 2 at-bound; se_method note)
- `MNL/theta_p2a_singles_2016_v1.csv` and `_v2.csv` (47 params each; columns `param, certified, trial, moved`; same region-live theta to float precision)

Code and specs (inspected via read-only exploration):

- `dclaborsupply-monorepo/notebooks/fr_data_walkthrough.ipynb` (P2a-9, P2a-10 cell id `7c42e9bd`, `regionlive00–05` stubs, `_DE_ZERO_STUBS`)
- `dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb` (**mtime 2026-07-22 15:14** — now region-live: §12b revive, fit `negLL 19053.4655 iters=540 converged=True`, anchor assert `abs(r_b.fun − 19053.4655) < 1e-2`)
- `MNL/scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` (the active spec — see §5)
- `dclaborsupply-monorepo/packages/dclaborsupply/src/dclaborsupply/`: `data/loader.py`, `likelihood/engine_jax.py`, `spec/parser.py`, `solvers/jax_optimize.py`, `se/numerical.py`, `se/cluster_robust.py`, `gates/recovery.py`, `diagnostics/bundle.py`
- `MNL/scripts/bpool/`: `step4_realdata_baseline.py` (`_two_stage_optimize`, `_chunked_scores`, `_clustered_sandwich`, Hessian block), `jax_joint_hessian.py`, `joint_recovery_test.py` (`_hessian_verdict`), `jax_recovery_gate.py` (Check 1–5 thresholds), `step4_emit_results_json.py`
- `MNL/scripts/enhanced/RURO_post_estimation_styled.py` (styled report; region-dummy fallback at ~lines 2491–2501), `diagnostics_bundle.py` (cond warn > 1e10)
- `MNL/scripts/welfare/` gate scripts (Stage-3A/3B/4B TOL=1e-6 precedents), `stage_p2a_singles_welfare.py`, `run_p2a_singles_welfare.py`, `configs/welfare_p2a_singles2016.yaml`
- `MNL/docs/estimation/RURO_cluster_robust_SE_design_audit_v1.md` (T1–T5 spec)
- `Job_Market_paper/claude_uplods/RURO_model_spec_contract_v1.md` / `_v4_stijn_occ.md` (contract-level hard gates)
- `MNL/docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_variables.csv` (drgur/drgmd/drgru ← EU-SILC `db100`)
- `MNL/docs/France_case/_shared/gsur/RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md` (+ rebuild spec v2.1, acquisition, year-alignment decision)

On-disk artifact state (verified 2026-07-22): root engine-ready parquets `fr_singles_engine_ready_{v1..v5,p2a_bpool,p2a_bpool_v2}.parquet`; `outputs/p2a_singles2016/` full listing (28 files; region-dead 07-12 vintage + three 07-13 region-live files + 07-22 regenerations); no `MNL/scripts/p2a/` and no `MNL/docs/France_case/P2a/` directory existed before this plan.

## 3. Current artifact problem

The promotion-readiness audit's diagnosis stands, with one **new post-audit complication**.

Audit diagnosis (still true): the region-live fit (negLL 19053.4655) has no committed gradient, no
Hessian/eigenvalues/rank/condition number, no region-live cluster-robust SE, no region-live
post-estimation report, no persisted production optimizer status, and no verified cold-reload
anchor; the propagation script `propagate_regionlive.py` is absent from disk with no git record;
all committed diagnostics in `outputs/p2a_singles2016/` (SE CSV, solver diagnostics, PNGs, params
CSV) are the region-dead 2026-07-12 vintage; region-dead evidence showed **five near-zero
eigenvalues loading on the region block** — the identification question the repair must resolve is
unverified.

New post-audit facts (mtimes 2026-07-22 15:13–15:14, i.e. *after* the audit was written):

1. `fr_singles_pipeline_v1.ipynb` now **contains and asserts the region-live anchor** (§12b revive;
   fit `negLL 19053.4655, iters=540, converged=True`; `assert abs(r_b.fun − 19053.4655) < 1e-2`).
   The audit's statement that the pipeline notebook is "region-dead only" is stale.
2. Root `fr_singles_engine_ready_p2a_bpool.parquet` was regenerated **region-live** (07-22 15:13).
   Consequently **no region-dead bpool engine-ready parquet remains on disk** — the region-dead
   state is only reproducible by re-running assembly without the §12b revive.
3. `theta_p2a_singles_2016_v1.csv` was regenerated 07-22 15:13; v1 and v2 are the same region-live
   theta to float precision (v2, dated 07-13, actually being the *older* file).
4. `p2a_fit_provenance.json` `engine_ready` now points at `fr_singles_engine_ready_p2a_bpool.parquet`
   (no `_v2` suffix) while `P2A_MASTER_RECORD.md` names `_v2` — a pointer inconsistency that is now
   *materially ambiguous* because there are **three** region-live frames on disk: root
   `..._p2a_bpool.parquet` (07-22), root `..._p2a_bpool_v2.parquet` (07-13), and the adapter stem
   `outputs/p2a_singles2016/fr_p2a_singles2016__singles.parquet` + `__mnlmeta.json` (07-13) that the
   loader actually consumed.

So the artifact problem is now two-fold: (a) the missing diagnostic bundle (unchanged), and (b) a
**mixed-vintage, multi-copy engine-ready situation** in which the rebuild must first establish, by
column-level comparison and hashing, which frame is canonical and that all three agree on every
engine-consumed column (Decision D-1, §25). The rebuild is a **data-wiring repair being promoted to
production provenance — not a new specification** — and the plan treats it exactly so: same spec,
same bounds, same start, same engine; the only "new" work is reproducible wiring, diagnostics, and
provenance.

## 4. Repository ownership

| Concern | Repository | Rationale |
|---|---|---|
| Orchestration scripts (`scripts/p2a/…`), run config, output bundle, strict report | **MNL** | JMP-specific empirical provenance; matches existing convention (`scripts/bpool`, `scripts/welfare`, `scripts/enhanced`; `docs/France_case/P3a` precedent → new `docs/France_case/P2a`) |
| Loader, spec parser, JAX engine, L-BFGS-B wrapper, Hessian SE, sandwich + T1–T5, diagnostics bundle | **dclaborsupply-monorepo** (import only) | Already-validated reusable APIs; the rebuild imports them and adds nothing to the package |
| Job_Market_paper | **untouched** | Writing repo; receives only the eventual manager-level status update, not produced here |

**No package-core change is planned.** One genuinely reusable primitive is currently missing from
the package — the chunked per-group score computation (`_chunked_scores` + `_slice_data_groups`
live only in `MNL/scripts/bpool/step4_realdata_baseline.py`). Upstreaming it would satisfy the
"reusable missing primitive" test, but it is **not required** for this rebuild: the MNL rebuild
script will carry a thin local copy (~40 lines) of the chunked-score loop and feed the package's
`se/cluster_robust.py` assembly/T-checks. Upstreaming is proposed as a *separate, later* package PR
(Decision D-8), keeping this rebuild free of package edits. The monorepo
`dclaborsupply_app/reports/post_estimation.py` is a `NotImplementedError` stub and will not be used;
the working post-estimation path is MNL's `scripts/enhanced/RURO_post_estimation_styled.py`.

## 5. Active specification

**Exact YAML:** `MNL/scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` — the
certified pooled spec. **There is no P2a-specific spec YAML**; the P2a run is the certified spec
plus a *run-level overlay*, confirmed by `estimation_results_p2a_singles2016.json`
(`metadata.spec_config` points at this file; `specification: joint_pooled_v1_bll0_tlmpin_p2a_singles2016`).

Parameter partition for the P2a singles-2016 run (47-element theta vector, ordering as in
`theta_p2a_singles_2016_v*.csv`):

- **Spec-level fixed (not in theta):** `theta_l_m = −0.8` (`fixed_params`), `beta_c = 1.0`
  (consumption numeraire), couples `theta_c = 0.0`, `beta_ll` removed/fixed 0 (Check-5 non-PD
  provenance).
- **Run-level pinned (10, in theta but frozen at warm-start values):** `beta_l0_m, beta_l_age_m,
  beta_l_age2_m, beta_l0_f, beta_l_age_f, beta_l_age2_f, beta_l_nkids_f, theta_l_f` (couples
  leisure — no couples data in this singles-only run) and `beta_E_y2015, beta_E_y2017` (year
  dummies — single-year 2016 data).
- **Free (37):** singles leisure (`beta_l0_sm/sf`, `beta_l_age_sm/sf`, `beta_l_age2_sm/sf`,
  `beta_l_nkids_sf`, `theta_l_sm/sf`, `theta_c_singles`), hours (`beta_E, beta_h_pt1, beta_h_pt2,
  beta_h_ft, beta_h_lh`), market/region (`beta_E_gsur, beta_E_drgn2..8, beta_E_drgur, beta_E_drgmd`),
  occupation (`beta_occ_{2,3,4}_{m,f}` — **estimated, not pinned**), wage (`beta_w0, beta_w_educL,
  beta_w_educH, beta_w_pexp, beta_w_pexp2, sigma`).
- **At bound (2):** `beta_l_age2_sm`, `beta_l_age2_sf` (leisure curvature, not region params).
- **SE free block (35):** 37 free minus the 2 at-bound (per the recorded `se_method`).
- **Bounds:** the spec `optimization.bounds` block verbatim (e.g. `theta_l_*`/`theta_c_singles`
  [−8.0, 0.95], `beta_E` [−25, 25], hours [−10, 10], occ [−15, 15], region `beta_E_drgn*` and
  `beta_E_drgur/drgmd` [−10, 10], `sigma` [0.1, 20]).
- **Warm start:** `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` (the certified pooled theta),
  as encoded in the `certified` column of `theta_p2a_singles_2016_v*.csv` and the JSON
  `initial_values`.

Plan: the certified YAML is **not edited**. The 10 run-level pins, engine-ready stem, warm-start
source and output paths are declared in a new run-config
`MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; the rebuild script applies the pins by
free-masking the 47-vector exactly as the notebook adapter did (pinned entries held at warm-start
values, excluded from the optimizer's free vector and from SEs). Phase 2 verifies this binding
reproduces the notebook's objective before any optimization.

## 6. JAX compatibility

**The active route is entirely inside the validated JAX implementation.** The fit uses
`build_jax_singles_ll(data, spec, is_male=…)` from
`packages/dclaborsupply/src/dclaborsupply/likelihood/engine_jax.py` (float64, jit; lifted verbatim
from `scripts/bpool/jax_ll_probe.py`/`jax_joint_hessian.py`, which reproduce the certified baseline
negLL 238504.6360973987 bit-for-bit per `03_migration_matrix.md`). The singles-only "joint"
objective is `neg_ll_sm(theta) + neg_ll_sf(theta)` with one shared 47-vector. `wage_spec = vw` is
inside the JAX-validated set; no unsupported feature (`loc_empirical`, `vw_occupation`) is invoked
(both are parser-recognised but have **no JAX implementation** and are barred from structural use by
`docs/known_limitations.md`). Region/urbanisation/gsur enter as ordinary linear regressors in the
opportunity (`beta_E`) block, which the engine already handles; the loader
(`data/loader.py`: `_region_dummies`, `_drgn1`, `_gsur`, `drgur/drgmd/drgru` via `_col`) fully
supports them. Hessian = `jax.hessian` on the same jit objective; scores = `jax.jacrev` of the
`per_group=True` positive-LL vector. Nothing in the rebuild leaves this validated surface.

## 7. Proposal versus structural occupation treatment

Occupation appears in **both** layers, but in strictly separated roles — the rebuild changes
neither:

- **Proposal generation (sampling design, frozen upstream):** the certified B-pool draws were
  generated with "D1 hours mixture, **W1 occ-conditional wages, empirical occ**, pi0=0.10, seed
  2026". Occupation conditioning lives in the *proposal density* used to draw the 101 alternatives;
  its likelihood footprint is confined to the `prior` column consumed by the engine as the
  McFadden-style sampling correction `−log_prior` inside `V = u + log_h + log_w + log_market −
  log_prior`, plus proposal-weighted within-set centering (`_center_proposal`, active because the
  spec sets `market_opportunity_center_within_choice_set` with `center_weights: proposal`). The
  rebuild does **not** regenerate draws; the correction is data-carried.
- **Structural access:** occupation enters the structural model only as the estimated
  `occupation_opportunity` dummy block (`variable: loc4`, reference 1; shifters `loc4_2/3/4` ×
  `applies_to: male|female`, gated by `working`), which the parser folds into
  `market_opportunity_shifters` → `log_market`. The **structural wage density is plain `vw`**
  (log-normal with `sigma`) — occupation does *not* condition the structural wage distribution.

So: proposal side = occ-conditional draw density, handled entirely through `prior`; structural side
= occ offer dummies in `log_market` only. This matches the promotion-readiness doc §5 and the
contract rule distinguishing proposal occupation conditioning from structural occupation-wage
modelling.

## 8. Data-wiring reconstruction

**Authoritative sources (Question 9):**

- `drgn1` (8 NUTS-1 macro-regions, values 1–8), `drgur/drgmd/drgru` (degree-of-urbanisation one-hot
  derived from EU-SILC `db100`: 1=urban, 2=intermediate, 3=rural per
  `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_variables.csv`): the raw
  EUROMOD FR input **`EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`** (tab-separated), the single
  authoritative source.
- `gsur`: **not** in the raw input; constructed by merge from the GSURv2 Stage-A lookup
  **`EUROMOD-STORAGE/Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`** (48 valid rows) on key
  `(drgn1, educ3, sex)`, opportunity-year 2015 for the 2016 wave (per
  `JMP_GSUR_year_alignment_decision_v1.md`; merge audit
  `RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md`).

**Reconstruction route (Questions 7–8) — ratified D-1: full `er_b` rebuild.** Per the ratified D-1,
the geometry/reference object is the in-memory `er_b` construction of `fr_singles_pipeline_v1.ipynb`
§§12–§12b, and the production runner must **reconstruct that same `er_b` object independently** — not
merely re-map the five revived columns onto an existing frame. The committed adapter stem and the
existing root parquets are **comparison artifacts only**, never authoritative inputs. The route is
therefore a full independent rebuild of the construction pipeline, with the on-disk frames used only
as equality cross-checks:

1. **Draws / pricing.** Reproduce the certified B-pool proposal draws (D1 hours mixture,
   W1 occ-conditional wages, empirical occupation, `pi0=0.10`, **seed 2026**) and the EUROMOD pricing
   of each drawn alternative, exactly as §12–§12b build them, from the raw source
   (`EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`) — **not** from any committed engine-ready parquet. This
   step re-runs the seeded draw generation and the tax-benefit pricing; its determinism (fixed seed,
   pinned EUROMOD system/data version, recorded library versions) is a Phase-1 precondition and is
   hashed into the manifest. (This supersedes the earlier "no EUROMOD run / verification-only" stance:
   D-1 requires the object be rebuilt, so the pricing that defines it is re-run.)
2. **`assemble_singles` → revival → B-pool bands → `er_b`.** Run `assemble_singles` on the priced
   draws; then perform the **independent** region/urbanisation/GSUR revival — read `drgn1, drgur,
   drgmd, drgru` from `FR_2016_a3.txt` and merge `gsur` from the Stage-A lookup on `(drgn1, educ3,
   sex)` (opportunity-year 2015 for the 2016 wave) — and apply the B-pool band overwrite, yielding the
   in-memory `er_b`. This is the §12–§12b pipeline reproduced end-to-end in `MNL/scripts/p2a/`.
3. **Freeze + equality cross-check.** Freeze `er_b` as the canonical engine-ready stem
   (`region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json`), so every
   downstream phase reads only from `region_live_v1/`. Then **prove equality** of the freshly rebuilt
   `er_b` against each of the three on-disk region-live frames (`_v2` 07-13, root bpool 07-22, adapter
   stem 07-13) after canonical row sorting, common-column ordering and dtype normalization: they must
   agree on **every** engine-consumed column (not only the five revived ones), and the three existing
   frames must agree with each other. Any disagreement triggers **S-1** and stops the run (Decision D-1).

The five-column idempotence map (source → `drgn1, drgur, drgmd, drgru, gsur`) is retained as a
**secondary** confirmation inside step 3, not as the primary construction. Because the rebuilt `er_b`
must reproduce the reference fit, the objective-reproduction gate (G-1) and the "materially-better is
also a stop" rule (S-2) apply to the fit on the rebuilt frame: if independently reproduced draws/pricing
do not land within the D-2 tolerances of negLL 19053.46553160094, that is a **finding** returned to the
manager (a signal that the reference `er_b` was not deterministically reproducible), never silently
accepted.

**Validations (Question 10)**, all hard-gated in Phase 1:

| Check | Criterion | Precedent |
|---|---|---|
| One-to-one mapping | mapping has exactly 1,555 rows, unique `idhh`, no duplicate keys; every engine-ready `idhh` matched (inner-join count = 1,555; anti-join empty) | notebook §12b assert pattern |
| Region support | `drgn1 ∈ {1..8}`, all 8 present; counts equal source counts {1:245, 2:254, 3:122, 4:135, 5:279, 6:175, 7:182, 8:163} | pipeline §12b printed counts |
| Urbanisation one-hot | `drgur + drgmd + drgru == 1` for every household; each ∈ {0,1} | notebook assert `sum(axis=1) == 1` |
| GSUR non-constant, in range | `gsur ∈ [0.05, 0.23]`, `nunique > 1` (expected 47 unique values, mean ≈ 0.0945) | notebook asserts `between(0.05, 0.23)`, `nunique() > 1` |
| Within-household constancy | `groupby(idhh)[five cols].nunique() == 1` across all 101 alternatives (no draw-level variation) | loader within-group contract |
| No cross-household leakage | for every `idhh`, engine-ready values equal the mapping row for that `idhh` exactly (merge-and-compare, zero mismatches); no value imputed from another household | new (explicit) |
| Frame reconciliation | the three region-live frames agree on all engine-consumed columns (max abs diff = 0 for the five columns; loader-level array equality for the rest) | new (required by §3) |
| Shape | 157,055 rows × expected columns; n_hh 1,555 (841 sf + 714 sm), 101 alts/HH | mnlmeta / provenance |

All Phase-1 outputs (mapping table, comparison report, SHA-256 hashes) are written to
`region_live_v1/` before any estimation runs.

## 9. Production script architecture

Two scripts in a new `MNL/scripts/p2a/` directory (peer of `scripts/bpool`, `scripts/welfare`),
plus one run-config. Naming departs slightly from the prompt's proposal to follow the repository's
`run_*`/`verify_*` convention (cf. `run_p2a_singles_welfare.py`, `run_stage3a_…`); the content
contract is identical:

- **`MNL/scripts/p2a/run_p2a_regionlive_rebuild.py`** (proposed name for
  `rebuild_p2a_region_live.py`) — single orchestrator, phase-structured (Phases 1–6 + 8 below), CLI
  flags `--config`, `--phase` (resume), `--out` (default the region_live_v1 folder), `--dry-run`
  (Phase 1+2 only, no optimization). Imports **only** dclaborsupply package APIs
  (`spec/parser.EstimationSpec`, `data/loader.load_singles`/`load_engine_ready_stem`,
  `likelihood/engine_jax.build_jax_singles_ll`, `solvers/jax_optimize.optimize_lbfgsb` +
  `build_bounds_list`, `se/cluster_robust.assemble_meat_matrix`/`compute_cluster_robust_se`/
  `run_t1..t5`, `se/numerical` finalization helpers) plus stdlib/numpy/pandas/jax. Local code is
  limited to: the funnel/mapping reconstruction (Phase 1), the 10-pin free-mask wrapper, a thin
  chunked-score loop (patterned on `step4_realdata_baseline._chunked_scores`), eigen/rank/condition
  reporting around `jax.hessian`, and artifact/provenance emission. **No likelihood math is
  duplicated.**
- **`MNL/scripts/p2a/verify_p2a_regionlive_reload.py`** (for `verify_p2a_region_live_reload.py`) —
  Phase-7 cold-reload verifier, runnable in a *fresh process* with no state from the rebuild run:
  reads only `region_live_v1/` files (+ the certified spec YAML), rebuilds the objective through the
  same package APIs, evaluates at the stored theta, checks the anchor, hashes, parameter ordering,
  and writes `cold_reload_verification.json`.
- **`MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`** — run-config: certified spec path,
  engine-ready seed frame (per D-1), warm-start theta source, the 10 run-level pins, cluster column
  `idorighh`, target negLL 19053.4655 (and full-precision 19053.46553160094), gate thresholds
  (filled from §19 after manager ratification), output folder.

Post-estimation (Phase 6) reuses `scripts/bpool/step4_emit_results_json.py`-style per-group emission
plus `scripts/enhanced/RURO_post_estimation_styled.py` as-is (see §16). The monorepo receives no
changes.

## 10. Output-directory contract

All new artifacts go to **`MNL/outputs/p2a_singles2016/region_live_v1/`** — a fresh folder; nothing
in the existing mixed-vintage `outputs/p2a_singles2016/` root is overwritten, moved, or deleted.
Contract:

```
outputs/p2a_singles2016/region_live_v1/
  region_map_p2a_singles2016.parquet          # Phase 1: idhh -> 5-column source mapping (+ audit cols)
  data_wiring_validation.json                 # Phase 1: all §8 checks, per-frame reconciliation, hashes
  fr_p2a_singles2016_regionlive__singles.parquet   # Phase 1: frozen canonical engine-ready stem
  fr_p2a_singles2016_regionlive__mnlmeta.json
  estimation_results.json                     # Phase 3: full production schema (see §11)
  theta.csv                                   # Phase 3: param, value, se_hessian, se_clustered, pinned/at_bound flags
  optimizer_diagnostics.json                  # Phase 3: status, message, n_iter, negLL, max|grad|, start vector, bounds
  hessian_diagnostics.json                    # Phase 4: eigenvalues, rank, cond, min-eig loadings, region-block test
  cluster_robust_se.csv                       # Phase 5: sandwich SEs + T1–T5 results
  post_estimation/                            # Phase 6: per-group results JSON + styled report tables/PNGs
  cold_reload_verification.json               # Phase 7 (written by the verify script)
  provenance.json                             # Phase 8: hashes, versions, git SHAs, pointers (see §18)
  rebuild_manifest.json                       # Phase 8: machine-readable strict-verdict manifest
```

The prompt's proposed filenames are kept verbatim where they appear above; additions (the frozen
stem, mapping table, wiring-validation JSON, manifest) are required by Phases 1 and 8. The
region-dead vintage and the 07-13 propagated files stay in place untouched as labelled history
(§P2A_MASTER_RECORD two-vintage header); root-level parquets/thetas are preserved and merely hashed
into provenance (see §15, §22).

## 11. Estimation procedure

Phase-3 procedure (after Phases 1–2 pass):

1. Load the frozen `region_live_v1` stem via `load_engine_ready_stem` → `PrecomputedDataSingles`
   (sm, sf); no couples load. Assert loader-level liveness: `reg2..reg8` non-degenerate (mean of
   reg2 ≈ 0.181), `gsur` mean ≈ 0.0945–0.098, `drgur/drgmd/drgru` one-hot; cluster ids present.
2. Build `neg_ll(theta) = neg_ll_sm(theta) + neg_ll_sf(theta)` with `build_jax_singles_ll`
   (`use_actual_choice=False`), 47-vector binding via spec `pidx`; apply the 10-pin free-mask
   wrapper (37 free).
3. Warm start `t0` = certified pooled theta (`theta_hat_realdata_901_v1.csv` projected onto the
   47-name ordering — must equal the `certified` column of `theta_p2a_singles_2016_v2.csv` to float
   precision; gated in Phase 2). Bounds = `build_bounds_list(spec)` restricted to the free block.
4. Optimize with **`solvers/jax_optimize.optimize_lbfgsb`** (scipy L-BFGS-B, `jac = jax.grad`,
   float64) using the notebook-matching options `maxiter=5000, maxcor=30, ftol=1e-15, gtol=1e-10`
   (the pipeline cell's exact settings; the wrapper's defaults `gtol=1e-6, maxiter=2000` are
   overridden to match the anchor run). Record everything the wrapper returns: `theta_hat`,
   `neg_ll`, `max_abs_grad`, `success`, `status`, `message`, `n_iter`.
5. Persist `optimizer_diagnostics.json` with: full options dict, start vector + its hash, bounds
   list, per-iteration negLL trace (callback), final status/message/n_iter, final negLL at full
   precision, `max|grad|` over the free block, at-bound report (ε per §19), wall-clock.
6. Objective-reproduction gate: `|negLL_hat − 19053.46553160094| ≤ TOL_OBJ` (§19 G-1). On failure →
   stop condition S-2, no downstream phase runs.

No optimistix polish is used (bound-active solution; `polish_optimistix` is contraindicated, and
the optimistix-verbose API is a known crash — package memory). No two-stage/basin protocol is
planned: this is a *reproduction* of an anchored fit from the certified warm start, not a fresh
search (a second-start basin check may be added later by manager request, not pre-registered here).

## 12. Gradient and convergence diagnostics

- **Analytic gradient**: `jax.grad(neg_ll)` (same jit objective), evaluated at `theta_hat`;
  persisted as the full 47-vector (pinned entries reported but excluded from the gate) plus
  `max|grad|` over the 35 non-bound free params and separately over the 37 free params (the 2
  at-bound params may legitimately carry nonzero projected gradient — reported, not gated).
- **Convergence gates** (§19): optimizer `success == True` *and* warm-convergence guard
  `max|grad|` below the pre-registered threshold (existing precedent `< 1e-2` from
  `jax_recovery_gate.py:282–285`; the certified pooled baseline recorded max|grad| 44.2 under a much
  larger objective, so the singles-scale guard needs manager confirmation — D-5).
- **Iteration sanity**: `n_iter` recorded and compared against the two observed anchor runs (353
  walkthrough / 540 pipeline) — informational only, no gate (iteration counts are not stable across
  BLAS/jax versions).
- **At-bound report**: every free param's distance to its bounds; expected set exactly
  `{beta_l_age2_sm, beta_l_age2_sf}` (gate G-11: any *other* param within ε of a bound → fail).
- All of the above goes into `optimizer_diagnostics.json`; nothing is left only in stdout.

## 13. Hessian and rank diagnostics

Phase 4, all at `theta_hat`, all persisted to `hessian_diagnostics.json`:

1. **Exact JAX Hessian** `H = jax.hessian(neg_ll)(theta_hat)` (float64), then restricted to the
   free block (37×37) and to the SE block (35×35, excluding at-bound). For a 47-param singles-only
   objective this is cheap (see §23) — no chunking needed for H itself.
2. **Symmetry check**: `max|H − Hᵀ|` reported *before* symmetrization, gated at the pre-registered
   tolerance (§19 G-6; existing precedents are exact-equality in the unit test and atol 1e-10 for
   the meat matrix; production code symmetrizes without testing — manager to ratify 1e-8·max|H|,
   D-4). Then symmetrize `H ← (H + Hᵀ)/2` as production code does.
3. **Eigendecomposition** (`np.linalg.eigh` on the free block): full spectrum persisted;
   `min_eig`, `max_eig`, `n_nonpos = #{eig ≤ 1e-8}` (Check-5 counter).
4. **PD gate**: `min_eig > 0` strictly (Check-5 precedent, `jax_recovery_gate.py:397–399`) — the
   central identification result the rebuild exists to produce. Non-PD → stop S-4 with flat-direction
   report.
5. **Numerical rank**: rank of the free-block Hessian under a pre-registered cutoff (no existing
   project threshold — D-3; recommended default `rank = #{eig_i > ε_rank · max_eig}` with
   `ε_rank = 1e-10`, consistent with the pinv `rcond=1e-10` precedent), gated `== 37`.
6. **Condition number**: `max_eig/min_eig`, reported as an actual value and gated on the ratified
   D-4 three-tier scheme (§19 G-8): **`≤ 1e7` clean**, **`1e7`–`1e10` warning** (recorded, does not
   halt), **`> 1e10` hard failure** (stop S-4). The actual value is compared against the certified
   pooled baseline's approximate condition number **1.295e6** (which sits in the clean band).
7. **Smallest-eigenvector loadings**: top-|loading| parameters of the eigenvectors of the 3 smallest
   eigenvalues (the `_hessian_verdict` "bad_dirs" pattern), explicitly compared against the
   region-dead flat direction (`beta_E_drgn3 −0.616, beta_E_drgur −0.420, beta_E_drgmd −0.405, …`)
   to demonstrate the flat direction is lifted.
8. **Bounds-and-pins report**: the 10 pins, 2 at-bound params, and spec-level fixings restated next
   to the spectrum so the verdict is self-contained.

## 14. Region × urbanisation identification test

Dedicated block in `hessian_diagnostics.json`, since this is the question the repair must settle
(open decision A2):

- **Regional parameter set (10):** `beta_E_gsur, beta_E_drgn2..drgn8, beta_E_drgur, beta_E_drgmd`
  (`beta_E_drgru` is the omitted urbanisation reference; `drgn1` the omitted region reference).
- **Test R-1 — design-matrix full column rank:** build the household-level regressor matrix
  `[gsur, reg2..reg8, drgur, drgmd]` (1,555 × 10) from the frozen stem; require
  `matrix_rank == 10` under the pre-registered cutoff (no existing threshold — D-3) and report its
  singular-value spectrum and pairwise correlations (near-collinear flag at |corr| > 0.9, the
  `_hessian_verdict` precedent).
- **Test R-2 (hard gate) — raw Hessian sub-block PD:** the raw 10×10 sub-Hessian on the regional
  params must be PD (min_eig > 0) — necessary for joint identification of the block.
- **Test R-4 (hard gate) — conditional regional-information matrix (regional Schur complement,
  ratified D-3):** partition the free-block Hessian `H` (37×37) into the 10 regional params `R` and
  the other 27 free params `O`:
  `H = [[H_RR, H_RO], [H_OR, H_OO]]`. Form the **conditional regional-information matrix** as the
  Schur complement of `H_OO` in `H`, `S_R = H_RR − H_RO · H_OO⁻¹ · H_OR` (use a pinv with the
  `ε_rank`/`rcond = 1e-10` precedent for `H_OO⁻¹`). Require `rank(S_R) == 10` under the `ε_rank`
  cutoff **and** `min_eig(S_R) > 0` strictly. This is the decisive test that the region block is
  identified **conditional on** (not confounded with) the other parameters — the raw sub-block R-2
  can be PD while the block is still jointly weakly identified against `O`; R-4 rules that out.
  Persist `S_R`, its spectrum, rank, and `min_eig`.
- **Test R-3 (warning diagnostic only — NOT a gate, ratified D-3) — regional loading on near-null
  directions:** report, for each eigenvector of the 3 smallest free-block eigenvalues, the sum of
  squared loadings of the 10 regional params; flag a **warning** if that share `≥ 0.5` in any of the
  three. This is an informative "flat direction lifted" narrative vs the region-dead evidence of 5
  near-zero eigenvalues loading exactly there, **but the 0.5 cutoff is too arbitrary to determine
  identification by itself**, so it does **not** contribute to the PASS/FAIL verdict and does **not**
  halt the pipeline. It is recorded in the diagnostics as `region_loading_share_warning: true/false`.
- **Verdict field:** `region_urbanisation_identification: PASS / FAIL` is determined by the **hard
  gates R-1, R-2 and R-4 only** (design rank 10; raw sub-block PD; conditional Schur-complement rank
  10 and min_eig > 0); the R-3 loading-share result is attached as a warning that never changes the
  verdict. FAIL does not trigger silent re-specification: it stops the pipeline (S-5) and returns the
  evidence to the manager for decision A2 (keep all 10 / reduce / regularise). Per the gsplit lesson
  recorded in the manifest ("PD Hessian is not sufficient without recovery"), a PASS here is a
  *necessary* real-data local-identification result for this data-wiring repair, and the strict report
  states its scope precisely (no synthetic-recovery claim is made for the region block by this
  rebuild — see §25 D-7).

## 15. Cluster-robust inference

Phase 5, cluster key **`idorighh`** (loader `cluster_ids`), per the recorded P2a `se_method`
("cluster-robust sandwich, analytic per-household scores (jacrev of per_group +LL),
cluster=idorighh, free block = 35 params"):

1. **Scores:** thin local chunked loop patterned on `step4_realdata_baseline._chunked_scores` /
   `_slice_data_groups`: for each group chunk (~200 households), `jax.jacrev` of the
   `per_group=True` positive-LL vector from `build_jax_singles_ll`; stack sm + sf scores with their
   `cluster_ids`. This is the existing chunked route the prompt requires (and the reason the pooled
   baseline's 11-TB naive-jacrev failure cannot recur; at P2a scale memory is trivial anyway).
2. **Identity check (T1):** row-sum of scores over households equals `−grad(negLL)(theta_hat)`
   componentwise within the pre-registered tolerance (code default atol 1e-6; design doc says
   1e-10; runbook 1e-8 — inconsistency D-5).
3. **Meat and sandwich:** sum scores within `idorighh` clusters; `B = Σ s_j s_jᵀ`
   (`assemble_meat_matrix`); `V = H⁻¹ B H⁻¹` on the 35-param SE block via
   `compute_cluster_robust_se(hessian, scores, cluster_ids, free_mask=…)` (pinv rcond 1e-10;
   no finite-sample correction, matching the certified pooled route).
4. **T-checks, all persisted:** T1 (identity, above); T2 meat symmetry atol 1e-10; **T3 cluster
   count** — the package default `expected=9657` is the *pooled* count and must be overridden: the
   expected value is the number of unique `idorighh` among the 1,555 households, measured in Phase 1
   and written into the run-config (gate = exact match; D-6 ratifies the measured number);
   T4 all 35 free SEs strictly positive and finite; T5 robust-vs-Hessian SE comparison
   (informational, logged per package behaviour).
5. **Outputs:** `cluster_robust_se.csv` (param, theta_hat, se_hessian, se_clustered, ratio,
   pinned/at_bound flags) + a `t_checks` block (T1–T5 with values and pass/fail) inside
   `estimation_results.json` and the manifest. The stale region-dead `p2a_se_clustered.csv` is
   never read.

## 16. Post-estimation regeneration

Phase 6 regenerates the full report **only** from region-live inputs inside `region_live_v1/`:

1. **Per-group emission** (pattern: `scripts/bpool/step4_emit_results_json.py`): from the rebuilt
   joint (sm+sf) results, emit `post_estimation/{sm,sf}/estimation_results.json` in the enhanced
   schema `RURO_post_estimation_styled.py` consumes, carrying the full 47-theta, both SE sets, and
   the Hessian diagnostics.
2. **Styled report per group**: run `scripts/enhanced/RURO_post_estimation_styled.py` with
   `--mnl-base` pointed at the frozen `region_live_v1` stem
   (`fr_p2a_singles2016_regionlive`). Note the styled report *reads region variables from the data*
   (`reg_nuts1_*` with `drgn1` fallback, ~lines 2491–2501) — the frozen stem carries `drgn1`, so the
   V-function/MUC/MUL diagnostics compute on live regional data. All tables/PNGs are written under
   `region_live_v1/post_estimation/`; nothing under the mixed-vintage root is read or written.
3. **Labelling**: every emitted table/figure header and the report front-matter carries
   `PROVISIONAL — region-live rebuild, pending strict verdict` until the manager rules on the Phase-8
   package; the master-record update itself is out of scope (§22, doc-repair A3 owns it).
4. Stale-input guard: the runner asserts that no file path it opens resolves into
   `outputs/p2a_singles2016/` outside `region_live_v1/` (defensive check against the region-dead
   artifacts).

## 17. Cold-reload verification

Phase 7, executed by `verify_p2a_regionlive_reload.py` in a **fresh process** (fresh Python
invocation; no in-memory state from the rebuild; ideally after a machine-level restart of the JAX
runtime, recorded in the JSON):

1. Re-read: certified spec YAML, `region_live_v1` frozen stem, `theta.csv`,
   `estimation_results.json`, `provenance.json`.
2. Re-verify hashes of every input against `provenance.json` (mismatch → fail).
3. Rebuild the objective through the same package APIs; verify parameter ordering: the 47-name
   sequence from the spec binding equals the `theta.csv` order exactly (string-level check).
4. Evaluate `negLL(theta_hat)`; check both anchors: (a) against the 4-dp target
   `|negLL − 19053.4655| < 1e-2` (the notebook's existing anchor tolerance — the only pre-existing
   precedent), and (b) against the stored full-precision value
   `|negLL − negLL_stored| ≤ TOL_RELOAD` (no existing threshold — D-2; recommended 1e-6 abs,
   matching the project's machine-tolerance gates).
5. Evaluate `max|grad|` at the reload and compare to the stored value (informational).
6. Write `cold_reload_verification.json` (pass/fail per check, environment: python/jax/scipy/numpy
   versions, platform, timestamp) — the manifest's Phase-7 evidence.

## 18. Provenance and hashing

`provenance.json` (Phase 8, assembled incrementally from Phase 1) must contain:

- **SHA-256 hashes**: raw `FR_2016_a3.txt`; gsur lookup parquet; mapping table; all three
  pre-existing region-live frames (for the reconciliation record); the frozen `region_live_v1` stem
  (+ mnlmeta); certified spec YAML; warm-start theta CSV (`theta_hat_realdata_901_v1.csv`);
  `theta.csv`; `estimation_results.json`; run-config; both rebuild scripts (self-hash).
- **Parameter contract**: the ordered 47-name list, its hash, the 10 run-level pins, the 2 at-bound
  names, spec-level fixings, bounds per free param.
- **Targets**: negLL target 19053.4655 (4 dp) and 19053.46553160094 (full precision); region-dead
  reference 19071.6562 (context only).
- **Environment**: python, jax, jaxlib, scipy, numpy, pandas versions; float64 flag; platform;
  hostname; timestamps (UTC).
- **Git state**: MNL and dclaborsupply-monorepo HEAD SHAs + dirty-tree flags at run time.
- **Lineage pointers**: predecessor artifacts (`p2a_fit_provenance.json`, notebook cell ids
  `7c42e9bd` / pipeline §12b, the missing-`propagate_regionlive.py` note), and the statement that
  this bundle supersedes the propagated 07-13 set *for the region-live vintage only* — the certified
  pooled baseline is explicitly out of scope.
- **Gate table**: every §19 gate with its threshold, source, measured value, and PASS/FAIL — duplicated
  into `rebuild_manifest.json` as the machine-readable strict-verdict input.

## 19. Pre-registered pass criteria

No thresholds are invented silently. Existing sources are cited; absent or conflicting ones are
marked **MANAGER APPROVAL REQUIRED (MAR)** with a recommended default. (Threshold inventory verified
against code on 2026-07-22.)

| # | Criterion | Threshold | Status / source |
|---|---|---|---|
| G-1 | Objective reproduction (Phase 3) | `\|negLL − 19053.46553160094\| ≤ TOL_OBJ` | **MAR (D-2)** — no existing negLL-reproduction tolerance; nearest precedents: notebook anchor `< 1e-2` vs 4-dp target (pipeline fit assert); machine-tol gates 1e-6 (Stage-3A/4B, Check-4). Recommended: 1e-2 vs 4-dp target AND 1e-4 vs full-precision value |
| G-2 | Optimizer success | scipy `success == True` and status recorded | Existing pattern (`optimize_lbfgsb` records success/status; legacy gates on `res.success`); note active JAX gate uses G-3 instead — both applied |
| G-3 | Gradient at optimum | `max\|grad\|` (35 non-bound free) `< 1e-2` | Existing: warm-convergence guard `jax_recovery_gate.py:282–285`; scale-appropriateness for singles **MAR (D-5)** if tightened |
| G-4 | Solver tolerances (inputs, not gates) | `ftol 1e-15, gtol 1e-10, maxiter 5000, maxcor 30` | Existing: the anchor run's exact options (pipeline fit cell); wrapper defaults documented |
| G-5 | Hessian PD | `min_eig > 0` strictly (free block); `n_nonpos` counter at eig ≤ 1e-8 | Existing: Check-5 `jax_recovery_gate.py:397–399`, `gates/recovery.py:95–96` |
| G-6 | Hessian symmetry | `max\|H − Hᵀ\|` before symmetrization ≤ tol | **MAR (D-4)** — production code symmetrizes untested; precedents: exact (unit test), 1e-10 (meat T2). Recommended: 1e-8 · max\|H\| |
| G-7 | Numerical rank | free-block rank == 37 with `eig > ε_rank · max_eig` | **MAR (D-3)** — no existing rank cutoff; recommended ε_rank = 1e-10 (pinv rcond precedent) |
| G-8 | Condition number (three-tier, ratified D-4) | `≤ 1e7` clean; `1e7`–`1e10` **warning** (records, no halt); `> 1e10` **hard failure** (S-4) | **Ratified (D-4).** Report actual value; compare with certified pooled cond 1.295e6 (clean band). Precedents: warn `diagnostics_bundle.py:571` (>1e10), contract `<1e7` (`RURO_model_spec_contract_v1.md:476`) — reconciled into the three tiers |
| G-9 | Region × urbanisation block (hard gates, ratified D-3) | **R-1** design rank == 10; **R-2** raw sub-Hessian PD; **R-4** conditional regional-information (regional Schur complement vs other free params) rank == 10 **and** min_eig > 0. **R-3** loading-share is a **warning only**, not part of this gate | **Ratified (D-3).** Verdict = R-1 ∧ R-2 ∧ R-4 (§14). `\|corr\|>0.9` near-collinear flag (`joint_recovery_test.py:343–353`) retained as a sub-check; R-3 (share ≥ 0.5 on 3 smallest eigvecs) recorded as `region_loading_share_warning`, never gating |
| G-10 | Cluster-score identity (T1) | `Σ_h s_h = −grad` within atol | Existing but **inconsistent — MAR (D-5)**: code 1e-6 (`cluster_robust.py:181`), design doc 1e-10, runbook 1e-8. Recommended: 1e-8 |
| G-11 | Meat symmetry (T2) | atol 1e-10 | Existing: `cluster_robust.py:212` |
| G-12 | Cluster count (T3) | exact match to measured unique `idorighh` (override package default 9657) | Existing check, expected value **MAR (D-6)** — Phase-1 measured count to be ratified |
| G-13 | SE validity (T4 + NaN policy) | all 35 free SEs finite and > 0; negative-variance → NaN policy of `se/numerical.py` applied and count == 0 | Existing: `cluster_robust.py:224–228`; `se/numerical.py:57,81` |
| G-14 | Robust-vs-Hessian SE (T5) | informational log (no raise) | Existing: `cluster_robust.py:231–253` |
| G-15 | No unintended bound hits | at-bound set == {`beta_l_age2_sm`, `beta_l_age2_sf`} exactly, with ε = 1e-5 | Existing ε precedents **inconsistent** (1e-5 active gate `jax_recovery_gate.py:278`; 1e-4; contract 1e-3; SE-audit 1e-6) — adopt active-gate 1e-5; deviation **MAR (D-5)** |
| G-16 | In-bounds sanity | no free param `< lo − 1e-9` or `> hi + 1e-9` | Existing: `step4_realdata_baseline.py:420–422` |
| G-17 | Cold reload | hashes match; ordering match; anchors per G-1's ratified tolerances | Anchor `< 1e-2` existing (notebook); full-precision reload tol **MAR (D-2)**, recommended 1e-6 |
| G-18 | Data-wiring gates | all §8 checks (one-to-one, support, one-hot, gsur range/variation, constancy, leakage, frame reconciliation, shape) — all exact/boolean | Existing patterns: notebook §12b asserts; loader contract; new exact checks need no numeric threshold |

## 20. Stop conditions

Any stop halts all downstream phases, writes the partial diagnostics collected so far plus a
`STOPPED` manifest (never a PASS), and returns to the manager. No auto-retry, no threshold
loosening, no silent re-specification.

- **S-1 (Phase 1):** any data-wiring gate G-18 fails — including the three on-disk frames
  disagreeing with each other or with the source mapping.
- **S-2 (Phase 3):** optimizer failure (G-2) or objective-reproduction failure (G-1). A negLL
  *better* than the target by more than TOL_OBJ is also a stop (it would mean the anchor run was
  not at the optimum — a finding, not a success).
- **S-3 (Phase 3):** gradient gate G-3 fails, or any unintended bound hit (G-15) / out-of-bounds
  (G-16).
- **S-4 (Phase 4):** Hessian non-PD (G-5), symmetry failure (G-6), rank < 37 (G-7), or
  condition-number hard-fail (G-8).
- **S-5 (Phase 4):** region × urbanisation test G-9 fails → evidence packaged for manager decision
  A2 (keep/reduce/regularise the region block); no unilateral spec change.
- **S-6 (Phase 5):** T1/T2/T3/T4 failure (G-10..G-13).
- **S-7 (Phase 7):** cold-reload failure (G-17), including any hash mismatch.
- **S-8 (any phase):** any attempt to read a stale region-dead artifact, or any input file whose
  hash changed mid-run.

## 21. Files to create

Code and config (MNL; names adjusted to repo `run_*`/`verify_*` convention — see §9):

1. `MNL/scripts/p2a/run_p2a_regionlive_rebuild.py` (≙ proposed `rebuild_p2a_region_live.py`)
2. `MNL/scripts/p2a/verify_p2a_regionlive_reload.py` (≙ proposed `verify_p2a_region_live_reload.py`)
3. `MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (new — run-config; keeps the certified
   spec YAML untouched)

Outputs (all under the fresh folder; prompt names kept, additions marked *new*):

4. `MNL/outputs/p2a_singles2016/region_live_v1/region_map_p2a_singles2016.parquet` *(new — Phase 1)*
5. `…/region_live_v1/data_wiring_validation.json` *(new — Phase 1)*
6. `…/region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json` *(new — frozen stem)*
7. `…/region_live_v1/estimation_results.json`
8. `…/region_live_v1/theta.csv`
9. `…/region_live_v1/provenance.json`
10. `…/region_live_v1/optimizer_diagnostics.json`
11. `…/region_live_v1/hessian_diagnostics.json`
12. `…/region_live_v1/cluster_robust_se.csv`
13. `…/region_live_v1/post_estimation/` (per-group results JSON + styled tables/PNGs)
14. `…/region_live_v1/cold_reload_verification.json`
15. `…/region_live_v1/rebuild_manifest.json` *(new — machine-readable strict-verdict manifest, Phase 8)*
16. `MNL/docs/France_case/P2a/FR_P2a_region_live_strict_estimation_report_v1.md` (human-readable
    strict-verdict report; the `docs/France_case/P2a/` directory is new, mirroring `P3a`)

This plan itself: `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v1.md`
(the only file created by the planning task).

## 22. Files not to modify

- `MNL/scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` (certified spec — read-only)
- `MNL/scripts/bpool/specs/theta_hat_realdata_901_v1.csv` (certified theta — read-only warm start)
- Everything in `MNL/outputs/p2a_singles2016/` outside `region_live_v1/` — region-dead vintage and
  07-13 propagated files stay as labelled history (incl. `P2A_MASTER_RECORD.md`,
  `p2a_se_clustered.csv`, `estimation_results_p2a_singles2016.json`, all PNGs)
- `MNL/p2a_fit_provenance.json`, `MNL/theta_p2a_singles_2016_v1.csv`, `_v2.csv`, root
  `fr_singles_engine_ready_*.parquet` (hashed into provenance, not touched; pointer repairs belong
  to doc-repair decision A3, *after* the strict verdict)
- Both notebooks (`fr_data_walkthrough.ipynb`, `fr_singles_pipeline_v1.ipynb`) — per D3 of the open-
  decisions doc, no notebook edits
- The entire `dclaborsupply-monorepo` package tree (no package changes in this rebuild; D-8 governs
  any later upstreaming)
- Anything in `Job_Market_paper`
- The certified pooled baseline artifacts and `EUROMOD-STORAGE` inputs (raw data and gsur lookup are
  read-only sources)

## 23. Runtime and memory considerations

Problem scale: 1,555 households × 101 alternatives = 157,055 rows, 47 params (37 free), float64,
singles-only — roughly 1/40th of the pooled baseline's likelihood work.

- **Phase 1** (raw read + funnel + mapping + verification): `FR_2016_a3.txt` is a full EUROMOD input
  (~100–200 MB read); minutes, < 4 GB.
- **Phase 3 fit:** anchor runs took 353–540 L-BFGS-B iterations; each iteration is one jit
  value+grad on 157k rows — sub-second. Expect **5–20 min CPU**, < 4 GB (first-call jit compile
  ~1–2 min extra).
- **Phase 4 Hessian:** `jax.hessian` on a 47-param singles objective — one 47×47 exact Hessian;
  expect **< 5 min**, < 8 GB. No chunking required (the 11-TB naive-jacrev hazard from the pooled
  sandwich does not arise at this scale, and scores are chunked anyway by design).
- **Phase 5 scores:** 1,555 per-group jacrev rows in ~8 chunks of 200 — **minutes**, < 8 GB.
- **Phase 6 post-estimation:** two styled-report runs — **~5–10 min**.
- **Phase 7 cold reload:** one objective evaluation + hashing — **~2–3 min** (dominated by jit
  compile and parquet hashing).
- **Total: well under 1 hour wall-clock on the current Windows CPU box; peak memory < 8 GB.**
  No GPU, no EUROMOD, no cluster resources needed. (Estimates are planning figures, not gates;
  actuals are recorded in the manifest.)

## 24. Implementation sequence

1. **Manager ratifies §25 decisions** (D-1..D-8); ratified thresholds are written into
   `p2a_regionlive_rebuild_v1.yaml`.
2. Create `scripts/p2a/` with the run-config and both scripts (no execution yet); commit
   ("P2a region-live rebuild scaffolding — plan v1, no run").
3. **Phase 1** — mapping reconstruction + frame reconciliation + freeze + `data_wiring_validation.json`.
   Stop-check S-1.
4. **Phase 2** — cold package load through dclaborsupply APIs: loader liveness asserts, spec/param
   binding check (47-name ordering vs theta CSVs; warm-start equality with the `certified` column),
   proposal-correction sanity (`prior` present, `−log_prior` active, proposal-weighted centering on).
   `--dry-run` exits here.
5. **Phase 3** — estimation (§11). Stop-checks S-2/S-3.
6. **Phase 4** — Hessian/rank/condition + region × urbanisation block test (§13–14). Stop-checks
   S-4/S-5.
7. **Phase 5** — chunked scores + sandwich + T1–T5 (§15). Stop-check S-6.
8. **Phase 6** — post-estimation regeneration (§16), everything labelled PROVISIONAL.
9. **Phase 7** — fresh-process cold reload (§17). Stop-check S-7.
10. **Phase 8** — strict-verdict package: `rebuild_manifest.json` +
    `FR_P2a_region_live_strict_estimation_report_v1.md` (gate table, spectrum, region verdict,
    SE table, environment, lineage). **No promotion**: the report ends with a recommendation and an
    explicit "awaiting manager strict verdict" status; master-record/pointer repairs and welfare
    re-examination (B1) remain manager-gated follow-ups.
11. Single final commit of scripts + outputs + report (git add limited to the §21 list), message
    referencing this plan; no push/PR unless the manager asks.

## 25. Ratified manager decisions

**Ratified 2026-07-23** in `FR_P2a_region_live_manager_decisions_v1.md`. The entries below record the
ratified decisions (no longer "recommended defaults"); D-3 and D-4 carry the manager's amendments.

- **D-1 — Canonical engine-ready input frame (RATIFIED).** The geometry/reference object is the
  in-memory `er_b` construction defined by §§12–§12b of `fr_singles_pipeline_v1.ipynb`:
  `draws/pricing` → `assemble_singles` → independent region/urbanisation/GSUR revival → B-pool
  band overwrite → `er_b`.
  The committed adapter stem and the existing root parquets are comparison artifacts, not
  automatically authoritative inputs.
  The production runner must **fully reconstruct the same `er_b` object independently** (rebuilding
  draws/pricing per §8, not merely re-mapping the five revived columns), freeze it under
  `region_live_v1`, and prove equality with the relevant existing frames after canonical sorting,
  dtype normalization, and common-column alignment.
- **D-2 — Objective-reproduction and cold-reload tolerances (G-1, G-17) (RATIFIED).**
  `|negLL − 19053.4655| < 1e-2` (4-dp target) **and** `|negLL − 19053.46553160094| ≤ 1e-4` (full);
  cold reload `|negLL_reload − negLL_stored| ≤ 1e-6`. A materially better objective is also a stop.
- **D-3 — Rank and regional-block criteria (G-7, G-9) (RATIFIED, amended).** `ε_rank = 1e-10 · max_eig`;
  full free Hessian rank == 37; regional design-matrix rank == 10. For the regional block, the hard
  requirements are: **(R-1)** the 10-column household-level regional design matrix has rank 10;
  **(R-2)** the raw 10×10 regional Hessian sub-block is positive definite; **(R-4)** the conditional
  regional-information matrix — the regional **Schur complement** against the other free parameters —
  has rank 10 and strictly positive minimum eigenvalue. The **regional-loading-share** check (R-3;
  share < 0.5 on each of the 3 smallest eigenvectors) is a **warning diagnostic only**, reported but
  **not a hard pass/fail gate** (the 0.5 cutoff is too arbitrary to determine identification by itself).
- **D-4 — Symmetry and condition number (G-6, G-8) (RATIFIED).** Symmetry `max|H − Hᵀ| ≤ 1e-8 · max|H|`.
  Condition number is a **three-tier** gate: `≤ 1e7` clean / `1e7`–`1e10` warning / `> 1e10` hard
  failure. The strict report shows the actual value and compares it with the certified pooled
  baseline's approximate condition number 1.295e6.
- **D-5 — Tolerance reconciliations.** T1 identity (1e-6 / 1e-8 / 1e-10 → *recommend 1e-8*);
  bound-hit ε (1e-3 / 1e-4 / 1e-5 / 1e-6 → *recommend 1e-5*, the active gate); gradient gate scale
  (*recommend keep 1e-2*).
- **D-6 — T3 expected cluster count.** Package default 9657 is pooled; the P2a value must be the
  Phase-1 measured unique `idorighh` count (≤ 1,555). *Recommended:* ratify the measured number
  post-Phase-1 (before Phase 5 runs).
- **D-7 — Scope of the identification claim.** This rebuild demonstrates PD + rank + block
  identification on **real data** only; per the gsplit precedent, no synthetic-recovery
  certification of the region block is claimed. *Decide:* whether a later synthetic re-gate of the
  region block is required before any promotion of the P2a track (recommended: yes, as a separate
  gate after A2).
- **D-8 — Package upstreaming (deferred).** Whether to later upstream the chunked per-group score
  primitive into `dclaborsupply/se` as a reusable API (justified as a genuinely missing reusable
  primitive). Not needed for this rebuild; *recommended:* defer to a separate package PR.

## 26. Exact implementation prompt

The following prompt is ready to hand to the implementing agent once §25 is ratified:

> **ROLE.** Implement the FR-2016 singles P2a region-live production rebuild exactly per
> `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v1.md` (this plan). The plan
> is binding: phases, gates, stop conditions, file lists, and the ratified thresholds inserted in
> `MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (manager decisions D-1..D-8:
> ⟨INSERT RATIFIED VALUES⟩).
>
> **HARD CONSTRAINTS.** Do not modify: the certified spec YAML, `theta_hat_realdata_901_v1.csv`,
> anything in `outputs/p2a_singles2016/` outside `region_live_v1/`, `p2a_fit_provenance.json`,
> the root theta/parquet files, either notebook, any file in `dclaborsupply-monorepo` or
> `Job_Market_paper`. Do not run EUROMOD, welfare, or any notebook. Do not re-generate draws. Do not
> loosen any gate at runtime. On any stop condition (plan §20), halt, persist partial diagnostics +
> a STOPPED manifest, and report — never write a PASS.
>
> **BUILD.** Create `MNL/scripts/p2a/run_p2a_regionlive_rebuild.py`,
> `MNL/scripts/p2a/verify_p2a_regionlive_reload.py`, and the run-config, per plan §9. Import the
> likelihood, loader, optimizer, and SE machinery from the dclaborsupply package
> (`data/loader.py`, `likelihood/engine_jax.build_jax_singles_ll`,
> `solvers/jax_optimize.optimize_lbfgsb` + `build_bounds_list`, `se/cluster_robust.*`); do not
> duplicate any likelihood math. Local code only for: the Phase-1 funnel/mapping reconstruction
> from `EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt` + `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`,
> the 10-pin free-mask wrapper (pins per plan §5), the chunked per-group jacrev score loop
> (pattern: `scripts/bpool/step4_realdata_baseline.py`), Hessian/eigen/rank/condition and the
> region × urbanisation block tests (plan §13–14), and artifact/provenance emission (plan §10, §18).
>
> **RUN.** Execute Phases 1–8 in order with stop-checks (plan §24). Optimizer: L-BFGS-B via the
> package wrapper with `maxiter=5000, maxcor=30, ftol=1e-15, gtol=1e-10`, warm start = certified
> pooled theta, bounds from the spec, 37 free / 10 pinned / spec-level fixings. Target:
> negLL 19053.46553160094 within the ratified tolerance. Cluster SEs on `idorighh` with T1–T5.
> Post-estimation via `step4_emit_results_json`-style per-group emission +
> `scripts/enhanced/RURO_post_estimation_styled.py`, reading only `region_live_v1/` inputs, all
> outputs labelled PROVISIONAL. Cold reload in a fresh process via the verify script.
>
> **DELIVER.** The complete `region_live_v1/` bundle (plan §21 items 4–15) +
> `MNL/docs/France_case/P2a/FR_P2a_region_live_strict_estimation_report_v1.md` with the full gate
> table and a recommendation, ending in status "awaiting manager strict verdict". One commit of
> exactly the §21 file list; no push; no promotion; no edits to the certified baseline; no welfare
> runs; no welfare-readiness statements.

## 27. Immediate next action

Submit §25 (D-1..D-8) to the manager for ratification — every other prerequisite is satisfied. The
recommended defaults are stated inline, so ratification can be a single approve/amend pass; once the
thresholds are fixed in `p2a_regionlive_rebuild_v1.yaml`, implementation proceeds under §24 with no
further design input. (Independently and in parallel, doc-repair A3 and the missing-script note A4
remain open in the manager's own queue; they are not blockers for this rebuild since Phase 1
supersedes the missing `propagate_regionlive.py` logic reproducibly.)
