# FR P2a Region-Live — Phase-5 Source Verification — v1

**Mission:** JMP-M05 Stage A — source audit closing gaps G-A to G-F of
`JMP_M05_task_plan_v1.md`
**Mode:** read-only repository audit; three new report files created; no commit
**Date:** 2026-07-31

---

## 1. Verification verdict

**SOURCE CONTRACT COMPLETE WITH NONBLOCKING GAPS**

All six source gaps G-A to G-F are closed by verified repository evidence, and
all twelve source-verification tasks V-1 to V-12 return verified values. No halt
condition fires: V-1 descendancy passes (HM-REV clear), the parameter map is
established by name from a committed artifact and a committed source (HM-MAP
clear), the additive likelihood composition is established from the production
JAX module (HM-LL clear), the scaling and weighting convention is established
(HM-WGT clear), the cluster identifier is aligned to loader group order with a
documented mechanism (HM-CLUS clear), the recorded bound direction is consistent
with the published gradient sign (HM-KKT clear), and float64 is confirmed at a
named enable point on the accepted route (HM-X64 clear).

Three nonblocking gaps remain, all recorded in §19. The material one is that the
JAX and jaxlib versions were **not recorded** in either accepted manifest;
Python, NumPy and pandas were. Nothing in the design memo's derivational or
decision content depends on closing it, but the Phase-5 implementation charter
must record the JAX version explicitly.

Five findings correct or sharpen working assumptions carried in the task plan.
They are stated as facts, not recommendations, and are collected in §20.

---

## 2. Scope

This audit establishes repository facts only. It computes no score, covariance,
standard error, test statistic, welfare quantity or decomposition; it invokes no
optimizer; it evaluates no gradient or Hessian; it runs no EUROMOD, notebook, or
data regeneration; it alters no theta, pin, artifact or specification.

Operations actually performed: `git` metadata reads; file reads; SHA-256 hashing
of existing files; loading of two accepted Phase-4 arrays (`hessian_free.npy`,
`hessian_free.csv`) for a numerical-equality comparison, as required by the
audit brief; column-level reads of the frozen engine-ready parquet for identifier
and covariate alignment; and `importlib.metadata` version queries. None of these
can trigger prohibited numerical work.

Three files were created (§21). No pre-existing file in any of the three
repositories was modified. No commit was made.

---

## 3. Repository provenance

| Item | Value |
| --- | --- |
| `Job_Market_paper` path | `C:\Users\hisham\Repo\Job_Market_paper` |
| `Job_Market_paper` HEAD | `1d31d10a355a5c154bdb84ac419f89fff46c12fa` |
| `MNL` path | `C:\Users\hisham\Repo\MNL` |
| `MNL` HEAD | `982c52217031158c4a2368709d4a6b211ebcde76` |
| Nested `dclaborsupply` path | `C:\Users\hisham\Repo\MNL\dclaborsupply-monorepo` |
| Nested `dclaborsupply` HEAD | `27756a06ea189339aa82915ed2124628afed20eb` |
| MNL gitlink for `dclaborsupply-monorepo` | `160000 27756a06ea189339aa82915ed2124628afed20eb 0` |

The three trees are siblings under `C:\Users\hisham\Repo` except that
`dclaborsupply-monorepo` is nested inside `MNL` as a submodule gitlink, which is
the expected layout.

All three binding revisions match the audit brief exactly:

- MNL accepted checkpoint `982c5221…` — **MATCH**;
- nested `dclaborsupply` HEAD `27756a06…` — **MATCH**;
- MNL gitlink `27756a06…` — **MATCH**, identical to the nested HEAD.

**Pre-audit worktree status.**

- `MNL`: clean. `git status --porcelain` empty.
- Nested `dclaborsupply`: clean. `git status --porcelain` empty.
- `Job_Market_paper`: clean except three **untracked** files, none modified:
  - `docs/Missions/JMP_M05_task_manager_operating_prompt_v1.md`
  - `docs/prompts/JMP_M05_management_checkpoint_commit_prompt_v1.md`
  - `docs/prompts/JMP_M05_source_verification_prompt_v1.md`

  These are the three v1 artifacts superseded by
  `JMP_M05_stageA_correction_memo_v1.md` §2–§3. No tracked file is modified in
  any repository.

Note for the record: `docs/Missions` and `docs/missions` are the same directory
on this case-insensitive filesystem; git tracks the mission files under
`docs/missions/`.

---

## 4. Governance provenance

**Governance checkpoint commit:** `30fbe2da40dd5c032fad8bd81f2840ef60ab0ba0`
— `docs(jmp): establish programme governance and launch M05`. This is the anchor
named in the Stage-A correction memo §5 and it is present in local history.

`Job_Market_paper` HEAD `1d31d10a…` is the immediately following commit,
`docs(jmp): delegate M05 design-stage management`, which added the delegation
and Stage-A management layer. The audit therefore runs against a governance state
one commit **ahead** of the anchor recorded in the correction memo; the
difference is additive documentation only (ten new files, 2,399 insertions, zero
deletions, zero modifications).

Committed governance / mission / prompt files relevant to JMP-M05, at HEAD:

| Path | Present |
| --- | --- |
| `docs/governance/JMP_program_governance_v1.md` | yes |
| `docs/governance/JMP_management_hierarchy_and_delegation_v1.md` | yes |
| `docs/governance/JMP_canonical_state_v1.md` | yes |
| `docs/governance/JMP_decision_log_v1.md` | yes |
| `docs/governance/JMP_roadmap_v1.md` | yes |
| `docs/governance/JMP_mission_template_v1.md` | yes |
| `docs/governance/JMP_Goal1_manager_operating_contract_v1.md` | yes |
| `docs/governance/JMP_governance_creation_report_v1.md` | yes |
| `docs/missions/JMP_M05_phase5_inference_mission_charter_v1.md` | yes |
| `docs/missions/JMP_M05_task_plan_v1.md` | yes |
| `docs/missions/JMP_M05_task_plan_manager_acceptance_v1.md` | yes |
| `docs/missions/JMP_M05_mission_ledger_v1.md` | yes |
| `docs/missions/JMP_M05_design_stage_delegation_packet_v1.md` | yes |
| `docs/missions/JMP_M05_stageA_correction_memo_v1.md` | yes |
| `docs/missions/JMP_M05_task_manager_operating_prompt_v2.md` | yes |
| `docs/prompts/JMP_M05_source_verification_prompt_v2.md` | yes |
| `docs/prompts/JMP_M05_task_plan_prompt_v1.md` | yes |
| `docs/prompts/JMP_M05_inference_design_prompt_v1.md` | yes |
| `docs/prompts/JMP_M05_methods_review_prompt_v1.md` | yes |

V-12 closes: every governance and mission path asserted by the charter exists at
the asserted path. `JMP_M05_task_manager_operating_prompt_v1.md` exists on disk
but is untracked and superseded by v2.

---

## 5. Revision descendancy

**V-1 PASSES. HM-REV does not fire.**

`git merge-base --is-ancestor fee60723… 982c5221…` succeeds: the canonical
checkpoint is a descendant of the execution revision.

`git log fee60723…..982c5221…` returns **exactly one** intervening commit, which
is the checkpoint itself:

`982c522 results(p2a): record accepted Phase-4 curvature diagnostics`

Its changed-file summary is ten files, 1,334 insertions, zero deletions:

| File | Class |
| --- | --- |
| `docs/France_case/P2a/FR_P2a_region_live_phase4_execution_report_v2.md` | execution report |
| `docs/France_case/P2a/FR_P2a_region_live_phase4_manager_acceptance_v1.md` | acceptance memo |
| `outputs/…/phase4_curvature_v1/complete/hessian_eigenvalues.csv` | bundle |
| `outputs/…/phase4_curvature_v1/complete/hessian_free.csv` | bundle |
| `outputs/…/phase4_curvature_v1/complete/hessian_free.npy` | bundle |
| `outputs/…/phase4_curvature_v1/complete/phase4_console.log` | bundle |
| `outputs/…/phase4_curvature_v1/complete/phase4_diagnostics.json` | bundle |
| `outputs/…/phase4_curvature_v1/complete/phase4_manifest.json` | bundle |
| `outputs/…/phase4_curvature_v1/complete/regional_hessian_subblock.csv` | bundle |
| `outputs/…/phase4_curvature_v1/complete/regional_schur_complement.csv` | bundle |

This is exactly the set V-1 required — acceptance memo, execution report, and
bundle, and nothing else. No source, config, spec, or theta file changed between
the execution revision and the checkpoint.

For the design memo: `fee60723ed27d6979976a3dc85b09cde3096e011` is the
**execution revision**; `982c52217031158c4a2368709d4a6b211ebcde76` is the
**canonical checkpoint revision**; the nested gitlink `27756a06…` is identical at
both.

---

## 6. Parameter ordering

**G-A closed. HM-MAP does not fire.**

Two independent committed sources agree, by name, on the ordering:

1. `dclaborsupply.spec.parser.EstimationSpec.from_yaml(…).all_param_names`, built
   from `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`
   (SHA-256 `492bcfa9c766bfcb5d8536f5e920cc0b00ffa600b7b89db60b250365f331f211`,
   verified unchanged).
2. `phase4_manifest.json → contract.parameter_map`, which publishes
   `all_names`, `free_names`, `pin_names`, `free_indices`, `pin_indices` and
   `pin_values` verbatim, plus round-trip proofs
   (`project_expand_free_exact: true`, `expand_project_full_free_coords_exact:
   true`, `pins_bitwise_accepted: true`).

The Phase-4 runner asserts `list(theta_estimated.csv["param"]) == names` before
proceeding, so the accepted theta table is bound to the same ordering.

### 6.1 Ordered 47-parameter vector (0-based)

```
 0 beta_l0_sm        12 beta_l_age2_m     24 beta_E_drgn2     36 beta_occ_3_m
 1 beta_l_age_sm     13 beta_l0_f         25 beta_E_drgn3     37 beta_occ_4_m
 2 beta_l_age2_sm    14 beta_l_age_f      26 beta_E_drgn4     38 beta_occ_2_f
 3 theta_l_sm        15 beta_l_age2_f     27 beta_E_drgn5     39 beta_occ_3_f
 4 beta_l0_sf        16 beta_l_nkids_f    28 beta_E_drgn6     40 beta_occ_4_f
 5 beta_l_age_sf     17 theta_l_f         29 beta_E_drgn7     41 beta_w0
 6 beta_l_age2_sf    18 beta_E            30 beta_E_drgn8     42 beta_w_educL
 7 beta_l_nkids_sf   19 beta_h_pt1        31 beta_E_y2015     43 beta_w_educH
 8 theta_l_sf        20 beta_h_pt2        32 beta_E_y2017     44 beta_w_pexp
 9 theta_c_singles   21 beta_h_ft         33 beta_E_drgur     45 beta_w_pexp2
10 beta_l0_m         22 beta_h_lh         34 beta_E_drgmd     46 sigma
11 beta_l_age_m      23 beta_E_gsur       35 beta_occ_2_m
```

### 6.2 Ordered 37-free vector (0-based)

Obtained by deleting the ten pinned full-vector indices
`{10, 11, 12, 13, 14, 15, 16, 17, 31, 32}` while preserving order.

```
 0 beta_l0_sm        10 beta_E            20 beta_E_drgn6     30 beta_occ_4_f
 1 beta_l_age_sm     11 beta_h_pt1        21 beta_E_drgn7     31 beta_w0
 2 beta_l_age2_sm *  12 beta_h_pt2        22 beta_E_drgn8     32 beta_w_educL
 3 theta_l_sm        13 beta_h_ft         23 beta_E_drgur     33 beta_w_educH
 4 beta_l0_sf        14 beta_h_lh         24 beta_E_drgmd     34 beta_w_pexp
 5 beta_l_age_sf     15 beta_E_gsur       25 beta_occ_2_m     35 beta_w_pexp2
 6 beta_l_age2_sf *  16 beta_E_drgn2      26 beta_occ_3_m     36 sigma
 7 beta_l_nkids_sf   17 beta_E_drgn3      27 beta_occ_4_m
 8 theta_l_sf        18 beta_E_drgn4      28 beta_occ_2_f
 9 theta_c_singles   19 beta_E_drgn5      29 beta_occ_3_f
```

`*` = active bound.

Cross-check: the 37-element `gradient_free` array in `phase4_diagnostics.json`
agrees element-by-element with the `grad` column of the 37 non-pinned rows of
`theta_estimated.csv`, to within `8.88e-16` (the recorded
`gradient_consistency_max_abs_dev`). Element 2 is `-0.8445544161794221` and
element 6 is `-1.4682021491125388`; both equal the `grad` entries of
`beta_l_age2_sm` and `beta_l_age2_sf` respectively. Element 33 is
`1.0992597206183063e-4`, equal to the `grad` entry of `beta_w_educH` and to the
recorded `g3_consistency_max_abs_grad_35free`. The task plan's V-3 provisional
inference that free positions 2 and 6 are the bound parameters is therefore
**confirmed by name**.

---

## 7. Free and interior maps

The interior-35 vector is the 37-free vector with `beta_l_age2_sm` (free 2) and
`beta_l_age2_sf` (free 6) removed **by name**.

```
 0 beta_l0_sm        10 beta_h_pt2        20 beta_E_drgn8     30 beta_w_educL
 1 beta_l_age_sm     11 beta_h_ft         21 beta_E_drgur     31 beta_w_educH
 2 theta_l_sm        12 beta_h_lh         22 beta_E_drgmd     32 beta_w_pexp
 3 beta_l0_sf        13 beta_E_gsur       23 beta_occ_2_m     33 beta_w_pexp2
 4 beta_l_age_sf     14 beta_E_drgn2      24 beta_occ_3_m     34 sigma
 5 beta_l_nkids_sf   15 beta_E_drgn3      25 beta_occ_4_m
 6 theta_l_sf        16 beta_E_drgn4      26 beta_occ_2_f
 7 theta_c_singles   17 beta_E_drgn5      27 beta_occ_3_f
 8 beta_E            18 beta_E_drgn6      28 beta_occ_4_f
 9 beta_h_pt1        19 beta_E_drgn7      29 beta_w0
```

The full 47 → 37 → 35 name-keyed map is delivered as
`docs/France_case/P2a/phase5_parameter_map_v1.csv`, with columns
`full_index_0based`, `free_index_0based`, `interior_index_0based`, `status`,
`block`, bounds, accepted value, and gradient entries.

Regional block position, obtained **by name** and not by arithmetic:

| Parameter | full | free | interior |
| --- | --- | --- | --- |
| `beta_E_gsur` | 23 | 15 | 13 |
| `beta_E_drgn2` | 24 | 16 | 14 |
| `beta_E_drgn3` | 25 | 17 | 15 |
| `beta_E_drgn4` | 26 | 18 | 16 |
| `beta_E_drgn5` | 27 | 19 | 17 |
| `beta_E_drgn6` | 28 | 20 | 18 |
| `beta_E_drgn7` | 29 | 21 | 19 |
| `beta_E_drgn8` | 30 | 22 | 20 |
| `beta_E_drgur` | 33 | 23 | 21 |
| `beta_E_drgmd` | 34 | 24 | 22 |

Free positions 15–24 match `phase4_diagnostics.json → regional.
regional_positions_free` exactly. Interior positions 13–22 also match the task
plan's arithmetic prediction, but are recorded here as the by-name result.

---

## 8. Active bounds and KKT evidence

**G-C closed. HM-KKT does not fire.**

Bounds source: `EstimationSpec.get_bounds_tuple()` over the certified spec's
`optimization.bounds` block; the runner passes `bounds_free = [bounds_full[i]
for i in free_idx]` directly to `scipy.optimize.minimize(method="L-BFGS-B")`.
Pins are **removed from the optimization vector entirely** in Phase 3, so no
pin-clamped bound enters the optimizer. (`phase2` separately builds a
diagnostic pin-clamped bound table; that path is not the estimation route.)

| Item | `beta_l_age2_sm` | `beta_l_age2_sf` |
| --- | --- | --- |
| Free position (0-based) | 2 | 6 |
| Spec bound `[lb, ub]` | `[-1.0, 1.0]` | `[-1.0, 1.0]` |
| Accepted value | `1.0` | `1.0` |
| `dist_lb` | `2.0` | `2.0` |
| `dist_ub` | `0.0` | `0.0` |
| Active side | **upper** | **upper** |
| `at_bound` flag in `theta_estimated.csv` | `True` | `True` |
| Free-gradient component of **negLL** | `-0.8445544161794221` | `-1.4682021491125388` |

**KKT consistency.** The objective is minimised negLL subject to
`theta_j <= ub_j`. Stationarity at an active upper bound requires
`∂negLL/∂theta_j + mu_j = 0` with multiplier `mu_j >= 0`, i.e.
`∂negLL/∂theta_j <= 0`. Both observed components are strictly negative, giving
`mu_sm = 0.8446` and `mu_sf = 1.4682`. The recorded bound direction (upper) is
therefore **consistent** with the published gradient signs.

**Strict activity.** The two multipliers are 3 to 4 orders of magnitude above
the maximum absolute gradient over the 35 non-bound free coordinates,
`1.0992597206183063e-4` (at `beta_w_educH`, free position 33). The V-3 / §7.3
falsification criterion of the task plan — a bound-coordinate gradient of the
same order as the interior maximum — does **not** trigger.

Gate evidence from Phase 3: G-15 recorded bound hits exactly
`{beta_l_age2_sm, beta_l_age2_sf}`, matching both the spec-derived and the
config-declared expectation (`at_bound_expected_derived` ==
`at_bound_expected_config` == `("beta_l_age2_sm", "beta_l_age2_sf")`), with no
unexpected hit; G-16 recorded zero in-bounds violations over all 37 free
coordinates at `epsilon = 1e-9`.

---

## 9. Fixed pins

**V-9 closed.** All ten pins, their values, and their verified roles:

| # | Parameter | Full index | Pinned value | Role |
| --- | --- | --- | --- | --- |
| 1 | `beta_l0_m` | 10 | `1e-06` | structurally inapplicable — unreferenced |
| 2 | `beta_l_age_m` | 11 | `-0.067236897452355` | structurally inapplicable — unreferenced |
| 3 | `beta_l_age2_m` | 12 | `0.0877504891847849` | structurally inapplicable — unreferenced |
| 4 | `beta_l0_f` | 13 | `10.052237044896549` | structurally inapplicable — unreferenced |
| 5 | `beta_l_age_f` | 14 | `-1.780253386288037` | structurally inapplicable — unreferenced |
| 6 | `beta_l_age2_f` | 15 | `1.0` | structurally inapplicable — unreferenced |
| 7 | `beta_l_nkids_f` | 16 | `0.5857198501055841` | structurally inapplicable — unreferenced |
| 8 | `theta_l_f` | 17 | `-2.131739110508045` | structurally inapplicable — unreferenced |
| 9 | `beta_E_y2015` | 31 | `-0.2546064112385174` | structurally inapplicable — identically-zero covariate |
| 10 | `beta_E_y2017` | 32 | `-0.0694711073761977` | structurally inapplicable — identically-zero covariate |

**Source of the pin values.** `cfg["run_overlay"]["pinned_params"]` names the ten
coordinates in `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; the values
are taken from the accepted stored region-live theta
`theta_p2a_singles_2016_v1.csv` (`trial` column, SHA-256 `930ef3aa…`, verified
unchanged) and carried unchanged into the estimate. Phase 3 recorded
`pins_bitwise_accepted: true` — IEEE-754 byte equality from the accepted pin
values through the applied start vector to the final estimate. All ten have
gradient component exactly `0.0` in the published 47-element `gradient_final`.

**Two distinct mechanisms, established from `engine_jax.py` routing.**

- *Pins 1–8 are unreferenced.* `build_jax_singles_ll` resolves leisure names as
  `spec.utility_leisure_intercept + suffix` and `coefficient + suffix` with
  `suffix ∈ {"_sm", "_sf"}`, and `theta_l_name = spec.utility_leisure_theta +
  suffix`. The `_m` / `_f` couples coordinates are resolved **only** by
  `build_jax_couples_ll`, which the P2a run never calls. These eight coordinates
  cannot enter the P2a objective by construction.
- *Pins 9–10 are referenced but multiply a null covariate.*
  `year_2015_indicator` and `year_2017_indicator` are declared in the spec's
  `market_opportunity.shifters` with `applies_to: "household"`, which the singles
  routing does include. Both columns of the frozen engine-ready stem are
  **identically zero** across all 157,055 rows, and the stem carries no
  `year_tag` column. Their contribution to `log_market` and their derivative are
  therefore identically zero.

**Correction to the task-plan expectation.** Task plan §8.2 anticipated that at
least one of the ten pins is an identifying or curvature normalisation, naming
`theta_l_f` as the candidate. This is **not supported by source**: `theta_l_f` is
the couples-female leisure Box–Cox exponent, unreferenced by the singles
objective. **None of the ten pins is a normalisation.** All ten are structurally
inapplicable to a 2016 singles sample.

**Where the genuine normalisations live.** They are outside the 47-vector, at
specification level, and are therefore not candidates for the pin reporting
convention:

| Quantity | Value | Source | Enters the P2a singles objective? |
| --- | --- | --- | --- |
| `beta_c` | `1.0` | `utility.consumption.fixed_value` (scale numeraire) | **yes** |
| couples `theta_c` | `0.0` | `utility.consumption.couples_fixed_box_cox_exponent` | no |
| `theta_l_m` | `-0.8` | spec top-level `fixed_params` | no |
| `beta_ll` | removed | couples leisure interaction deleted from the spec | no |

`theta_l_m` is worth flagging: it is a *fixed_params* entry read through
`engine_jax`'s `_fixed` dictionary, is **not** a member of the 47-vector, and is
**not** one of the ten pins. Any statement that the specification has eleven
fixed quantities must distinguish it from the ten run-overlay pins.

**Decomposition relevance.** `beta_E_y2015` and `beta_E_y2017` are by name
opportunity/access coordinates, so the task plan's §8.2(4) flag stands
nominally; but because their covariates are identically zero in the 2016 sample,
they contribute nothing to the P2a opportunity index at any value. The other
eight are couples-block preference coordinates absent from the singles model.

---

## 10. Likelihood call route

**G-B closed (route). HM-LL does not fire.**

Production objective symbol: `tot`, constructed in
`scripts/p2a/run_p2a_regionlive_rebuild.py::_phase3_contract` (line ~2150) and
reused unchanged by Phase 4 through `ctx3["tot"]`:

```python
from dclaborsupply.data.loader import load_singles
from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll

dm  = load_singles(sm_df, spec, is_male=True,  metadata=meta)   # 714 households
df_ = load_singles(sf_df, spec, is_male=False, metadata=meta)   # 841 households

nm, _ = build_jax_singles_ll(dm,  spec, is_male=True)
nf, _ = build_jax_singles_ll(df_, spec, is_male=False)
tot   = jax.jit(lambda t: nm(t) + nf(t))         # t is the FULL 47-vector
```

Builder arguments are defaults: `use_actual_choice=False`, `per_group=False`,
`gender_split=None`. `sm_df` / `sf_df` are the `dgn == 1` / `dgn == 0` splits of
the frozen engine-ready stem.

Phase-4 free-coordinate wrapper
(`_phase4_contract`, lines 2844–2852):

```python
free_idx  = jnp.asarray(pmap["free_idx"])                       # int64, len 37
base_full = jnp.asarray(expand_free_to_full(pmap, np.zeros(37)))# pins in place

def negll_free(x_free):                 # x_free is the ordered 37-vector
    return tot(base_full.at[free_idx].set(x_free))

hess_fn = jax.hessian(negll_free)
grad_fn = jax.grad(negll_free)
```

`base_full` is the 47-vector with pins at their pin values and free coordinates
zeroed; the `.at[free_idx].set(...)` write installs the free vector. This is a
genuine reparameterisation with pins held constant, **not** a 47-vector
projection with zeros — the design memo's S-3 chain-rule statement must reflect
that.

Phase 3 used the same `tot` through
`vg_full = jax.jit(jax.value_and_grad(tot))` with an explicit
`expand_free_to_full` per call, and projected the 47-gradient onto the free
coordinates via `pmap["free_idx"]`. The Phase-4 gradient reproduced the published
Phase-3 free gradient to `8.881784197001252e-16`.

The manifest records the route verbatim:
`derivative_route.objective = "package build_jax_singles_ll sm+sf (float64)"`,
`.hessian = "jax.hessian over the ordered 37-free vector (pins fixed)"`,
`.gradient = "jax.grad over the same free vector"`.

Nested source file:
`dclaborsupply-monorepo/packages/dclaborsupply/src/dclaborsupply/likelihood/engine_jax.py`
(SHA-256 `49bf6b7048f0065f248bf49dc750797ca9d9809c2aade29bd8808baeea2ceeed`,
git blob `d64a5af624b3aff458ab007dfbfbee9e17620210`, clean at HEAD).

**Score hook already exists in the production module.** `build_jax_singles_ll`
accepts `per_group=True`, in which case `neg_ll` returns the `(n_groups,)`
**positive** log-likelihood vector instead of the summed negLL. The module
docstring states that `jax.jacrev` of that vector is the per-choice-set score
matrix. The summed path is unchanged; `negLL = -jnp.sum(vector)` holds
identically. No new likelihood code is required to obtain the score.

---

## 11. Likelihood composition

**G-B closed (composition).**

For each group `g` (one household) and each alternative `j` of the 101, the
index is built once:

```
V_gj = u_gj + log_h_gj + log_w_gj + log_market_gj - log_prior_gj
```

with the following terms, all read verbatim from `engine_jax.build_jax_singles_ll`:

| Term | Sign | Content |
| --- | --- | --- |
| `u` | `+` | `beta_l_coeff * BC(leisure; theta_l) + beta_c * BC(consumption; theta_c)` where `beta_l_coeff = beta_l0_s{m,f} + beta_l_age_s{m,f}·age_norm + beta_l_age2_s{m,f}·age_norm2 [+ beta_l_nkids_sf·n_children, female only]`, `theta_l = theta_l_s{m,f}`, `theta_c = theta_c_singles`, `beta_c = 1.0` fixed. `BC(x;θ) = (x^θ−1)/θ`, or `log x` for `|θ| < 1e-8`. |
| `log_h` | `+` | `beta_E·working + beta_h_pt1·working_pt1 + beta_h_pt2·working_pt2 + beta_h_ft·working_ft + beta_h_lh·working_lh`. No `interaction` key on any hours shifter, so no additional `working` gate is applied. |
| `log_w` | `+` | Worker-gated log-normal wage density with Jacobian: `where(working > 0, −0.5·((log_wage − mu)/sigma)² − log sigma − 0.5·log(2π) − log_wage, 0)`, `mu = beta_w0 + beta_w_educL·educL + beta_w_educH·educH + beta_w_pexp·pexp_years + beta_w_pexp2·pexp_years²`. Active because `wage_spec = "vw"`. |
| `log_market` | `+` | `Σ beta_E_gsur·(10·gsur·working) + Σ_{k=2..8} beta_E_drgn{k}·(reg{k}·working) + beta_E_y2015·(0·working) + beta_E_y2017·(0·working) + beta_E_drgur·(drgur·working) + beta_E_drgmd·(drgmd·working) + Σ beta_occ_{2,3,4}_{m,f}·(loc4_{2,3,4}·working)`, then **proposal-weighted within-choice-set centering**: `log_market ← log_market − Σ_j(w_j·log_market_j)/(Σ_j w_j + 1e-12)` with `w = prior`. |
| `log_prior` | `−` | `log(prior)`, the importance-sampling correction for the drawn alternatives. |

The household contribution and the objective are:

```
l_g    = V_obs,g − logsumexp_j(V_gj)          # per-group POSITIVE log-likelihood
negLL  = − Σ_{g in male} l_g  − Σ_{g in female} l_g
```

`V_obs,g = V_{g,0}` — the column-0 convention, valid because
`use_actual_choice=False` and the loader's `_validate_chosen_first` gate proves
exactly one chosen alternative per group and that it is the **first** row of the
group. Independently confirmed in the data: every `draw == 0` row has
`is_chosen == 1`, and every household has exactly one chosen row.

**Composition summary for the design memo.** The household contribution is
**not** a sum of separable additive components. There is exactly **one** additive
term per household in the objective, `−l_g`. The wage density, hours-offer,
market/regional, occupation and prior-correction terms enter **inside** the index
`V_gj`, are alternative-specific, and therefore do **not** cancel between
`V_obs` and the log-sum-exp. Any derivation that writes `l_g` as
"choice term + wage-density term" is wrong for this model.

**Correction to the task-plan V-4 reasoning.** Task plan §4/V-4 argued from the
accepted negLL of `19053.46553160093` over 1,555 households (`12.25` nats per
household) against a "uniform-choice benchmark `ln(101) = 4.615`" that a
choice-only likelihood "cannot exceed the uniform benchmark", so the excess must
come from continuous-density terms, weighting, or a term count above 1,555. The
source shows the premise is unfounded and the conclusion does not follow:

- `l_g = V_obs − logsumexp_j(V_gj) <= 0` always, because `V_obs` is one of the
  terms in the log-sum-exp. There is no lower bound at `−ln(101)`; that value
  obtains only in the degenerate case where all 101 indices are equal, which the
  alternative-specific `log_h`, `log_w`, `log_market` and `log_prior` terms
  preclude.
- There are exactly 1,555 additive terms (§13), no weighting (§12), and no
  additively separable density term. The per-household magnitude is a property
  of a simulated RURO likelihood over 101 priced draws, not evidence of extra
  terms.

Accordingly, `ln(101)` must **not** be used as an objective bound anywhere in the
design memo, and no inference about likelihood composition may rest on the
average negLL. That is consistent with the audit brief's interpretive
restrictions; it is recorded here because the task plan's V-4 deliverable was
framed around the opposite premise.

---

## 12. Objective scaling and weighting

**G-D closed. HM-WGT does not fire.**

| Question | Verified answer | Source |
| --- | --- | --- |
| Sum, mean, or weighted? | **Unweighted sum** over households | `engine_jax.py:279` — `return -jnp.sum(per)`; runner `tot = nm(t) + nf(t)` |
| Any survey weight in the objective? | **No** | No weight term anywhere in `build_jax_singles_ll`; no weight in `load_singles`' `_requirements` |
| Any frequency weight? | **No** | same |
| Any per-observation scaling? | **No** | no division by `n_groups` or `n_obs` on the objective path |

The only object in the likelihood carrying the word "weight" is
`market_opportunity.center_weights: "proposal"`, which is the within-choice-set
centering weight `w = prior` applied to `log_market` before the index is formed.
It is a within-group covariate transformation, not a sample weight, and it
cancels no part of the log-sum-exp.

A survey weight column **`dwt`** does exist in the frozen engine-ready stem
(household-level range `529.34` to `41,902.59`, mean `2,924.17`). It is **not**
in the loader's required-column set, is **not** attached to the
`PrecomputedDataSingles` container, and is **never read** by the likelihood.

**Consequence for the frozen score identity.** With an unweighted sum objective,
`Σ_g s_g = ∇ℓ = −∇negLL` holds with matched scaling and no correction factor.
The charter §8 identity is therefore consistent as written, and the design memo
may state the sum convention as verified rather than assumed.

---

## 13. Primitive contribution and cluster contract

**Primitive likelihood-contribution count: 1,555.**

| Quantity | Value | Source |
| --- | --- | --- |
| Alternative rows in the frozen stem | 157,055 | parquet row count |
| Alternatives per household `n_alts` | 101 | `n_obs // n_groups`; loader `_validate_groups` proves rectangularity (every household has exactly 101 rows) |
| Household choice blocks (loader groups) | 1,555 | `dm.n_groups = 714` + `df_.n_groups = 841` |
| Additive terms in `negLL` | **1,555** | one `l_g` per loader group; `-jnp.sum(per)` over each group's vector, summed across the two builders |
| Person / decision-maker records | 1,555 | singles: one decision-maker per household; `idhh` unique per decider row |
| Unique `idhh` | 1,555 | verified directly |
| Accepted clusters | 1,555 | `phase4_manifest.json → design_loader_binding.unique_households` |

`157,055 = 1,555 × 101` exactly. The relationship is:

```
alternative rows (157,055)
    └─ 101 per household choice block
household choice blocks (1,555)          ← loader groups, keyed on idhh
    └─ exactly 1 likelihood term each
person / decision-maker records (1,555)  ← singles: 1 decider per household
idhh (1,555 unique)                      ← group key AND group_id
accepted clusters (1,555)                ← cluster_ids, one per group
```

**Is one household one primitive score contribution?** **Yes.** Each loader group
produces exactly one element of the `per` vector, hence one additive term in the
objective, hence one row of the per-group score matrix. There is one group per
`idhh` and one `idhh` per cluster.

**Is household-cluster covariance algebraically identical to a household-level
OPG sandwich here?** **Yes**, in this application. The cluster score is
`s_j = Σ_{g in cluster j} s_g`; with exactly one `g` per cluster `j`, the sum has
a single element, so `s_j = s_g` and the meat
`Σ_j s_j s_j' = Σ_g s_g s_g'` is the outer-product-of-gradients meat. Clustering
is **degenerate**, not binding: the 101 alternatives per household are a row-level
implementation concern and are already integrated out inside `l_g`; they are not
a source of statistical dependence across score contributions. The resulting
sandwich is misspecification-robust, not dependence-robust.

This is a source-verified structural fact. Choosing the manuscript's terminology
from it is a design-memo decision and is not made here.

*Inventory note, not a recommendation.* The package already ships
`dclaborsupply/se/cluster_robust.py` with `assemble_meat_matrix`,
`compute_cluster_robust_se` and T1–T5 checks, lifted verbatim from
`MNL/scripts/enhanced/cluster_robust_se.py`. Its `run_t3_cluster_count_check`
default is `expected=9657`, a P3a-pooled constant that does **not** apply to P2a;
the P2a config states the cluster count policy explicitly as
"auto-resolve unique nonmissing `idorighh` in frozen sample (D-6); never 9657".

---

## 14. Household-ID alignment

**G-E closed. HM-CLUS does not fire.**

**Grouping mechanism** (`loader.py::_group_bounds`). The frame carries no
`year_tag` column, so the non-pooled branch is taken:

```python
df.sort_values(["idhh"], kind="mergesort", inplace=True)   # stable
df.reset_index(drop=True, inplace=True)
idhh   = df["idhh"].to_numpy()
change = idhh[1:] != idhh[:-1]
starts = np.concatenate([[0], np.flatnonzero(change) + 1])
ends   = np.concatenate([starts[1:], [len(df)]])
group_ids = idhh[starts]        # one idhh per group -> already unique
```

Group `g` of the likelihood is therefore, by construction, the contiguous row
block `[starts[g], ends[g])` of the `idhh`-sorted frame, and `group_ids[g]` is
that block's `idhh`. The stable mergesort preserves the chosen-first ordering
within each household, which `_validate_chosen_first` then verifies (`is_chosen`
binary; exactly one chosen per group; `isc[starts] == 1` for every group).

**Cluster identifier mechanism** (`loader.py::_cluster_ids`). Candidates are
tried in order `metadata["cluster_key"]["cluster_id_col"]` → `["source_col"]` →
`"idorighh"` → `"idhh"`. The stem metadata records
`cluster_key = {"cluster_id_col": "cluster_id", "source_col": "idorighh"}` and
the `cluster_id` column is present, so `cluster_id` resolves first. The function
verifies the candidate is finite and constant within every group, then returns
`vals[starts]` — one value per group, **in loader group order**.

Because both `group_ids` and `cluster_ids` are taken at the same `starts`
indices of the same sorted frame, row `g` of any per-group array corresponds to
the same household as group `g` of the likelihood. This is the documented
alignment guarantee: a shared group-boundary array, not a re-merge or a re-sort.

**Verified counts and identity.**

| Check | Result |
| --- | --- |
| `nunique(idhh)` | 1,555 |
| `nunique(idorighh)` | 1,555 |
| `nunique(cluster_id)` | 1,555 |
| `cluster_id` constant within `idhh` | yes |
| `idorighh` constant within `idhh` | yes |
| rows per `idhh` | 101 for every household |
| chosen rows per `idhh` | exactly 1 for every household |
| `cluster_id == idhh` elementwise (at group starts) | **yes** |
| `cluster_id == idorighh` elementwise (at group starts) | **yes** |
| missing / non-finite cluster ids | none |
| male / female household split | 714 / 841 = 1,555 |

For this sample the three identifiers are the same integer sequence. The
certified spec header states the same: "Cluster key: `idorighh` (present on
engine-ready parquets, `cluster_id == idorighh`)". Phase 2 recorded
`cluster.consistency_ok`, `no_missing_ok`, `one_cluster_per_household_ok` and
`bounds_ok` all true, with `resolved_t3_count = map_idorighh_nunique = 1,555`.

Because the sorted-frame concatenation is `male block then female block`,
`np.concatenate([dm.cluster_ids, df_.cluster_ids])` is the canonical row order
for any stacked 1,555-row score matrix; the Phase-4 regional design applies an
additional `np.argsort(gid, kind="stable")` when it needs `idhh`-ascending order
across both genders. The design memo must fix one of these two orders explicitly.

---

## 15. Regional/access mapping

**V-8 closed.**

**This is the regional / urbanisation / GSUR access block. It is not the complete
opportunity mechanism.** The opportunity index `log_market` additionally carries
the six occupation coordinates `beta_occ_{2,3,4}_{m,f}`; the separate `log_h`
block carries the five hours-offer coordinates `beta_E`, `beta_h_pt1`,
`beta_h_pt2`, `beta_h_ft`, `beta_h_lh`; and `log_w` carries the six wage-density
coordinates. Statements about "the opportunity environment" that rest only on
these ten coordinates must be qualified accordingly.

**Names, design columns and free positions** (`phase4_manifest.json →
contract_phase4.regional`, verbatim):

| Design column | Parameter | Free position | Interior position |
| --- | --- | --- | --- |
| `gsur` | `beta_E_gsur` | 15 | 13 |
| `reg2` | `beta_E_drgn2` | 16 | 14 |
| `reg3` | `beta_E_drgn3` | 17 | 15 |
| `reg4` | `beta_E_drgn4` | 18 | 16 |
| `reg5` | `beta_E_drgn5` | 19 | 17 |
| `reg6` | `beta_E_drgn6` | 20 | 18 |
| `reg7` | `beta_E_drgn7` | 21 | 19 |
| `reg8` | `beta_E_drgn8` | 22 | 20 |
| `drgur` | `beta_E_drgur` | 23 | 21 |
| `drgmd` | `beta_E_drgmd` | 24 | 22 |

**Loader covariate definitions and omitted categories.**

- **`gsur`** — a **continuous** local labour-market rate, not a dummy. Loaded by
  `loader._gsur`, which reads column `gsur` or falls back to `u_rate`. Sourced
  from `EUROMOD-STORAGE/Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`
  (SHA-256 `f51ad630…`), matched on keys `(drgn1, educ3, sex)` at opportunity
  year 2015; 48 valid lookup rows, 100 % match. Household-level values verified:
  47 unique values, range `[0.053183, 0.225]`, mean `0.09450886`, constant within
  household across the 101 alternatives, no cross-household leakage. It enters
  as `beta_E_gsur · (10.0 · gsur · working)` — the `variable_scales: {gsur:
  10.0}` factor and the `interaction: ["working"]` gate are both applied.
  **`gsur` is not a regional-heterogeneity dummy.** It varies with region,
  education and sex jointly, and it is declared `offer_only_vars: ["gsur"]` in
  the spec. Assigning it to a null over "across-region differences" would
  conflate a rate with a set of region intercepts. It is not a member of the
  NUTS-1 dummy set and has **no omitted category**.
- **`reg2` … `reg8`** — NUTS-1 region dummies. `loader._region_dummies` finds no
  `reg_nuts1_2..8` columns in this stem, so it takes the documented fallback
  `reg{k} = (drgn1 == k)`. **The stem's stored `reg2..reg8` columns are
  identically zero region-dead placeholders and are never read by the
  likelihood** — this was the Phase-4 R-1 correction, and the Phase-4 design is
  built from the production loader arrays (`regional_design_source:
  "production_likelihood_loader_arrays"`), not from the stored columns.
  `drgn1` takes values `{1,…,8}` with household counts
  `{1: 245, 2: 254, 3: 122, 4: 135, 5: 279, 6: 175, 7: 182, 8: 163}`, summing to
  1,555. **The omitted / reference region is `drgn1 == 1` (245 households).**
  Each dummy enters as `beta_E_drgn{k} · (reg{k} · working)`, `applies_to:
  "household"`.
- **`drgur`, `drgmd`** — urbanisation-degree indicators, EU-SILC `db100` one-hot.
  Yes, they are urbanisation-degree indicators: `drgur` = urban (`db100 == 1`),
  `drgmd` = intermediate (`db100 == 2`), `drgru` = rural (`db100 == 3`).
  Household counts `drgur = 832`, `drgmd = 328`, `drgru = 395`, summing to 1,555;
  the runner gates `drgur + drgmd + drgru == 1` per row. `drgru` is loaded but
  carries **no coefficient** in the spec. **The omitted / reference urbanisation
  category is `drgru` (rural, 395 households).** Both enter as
  `beta_E_drg{ur,md} · (indicator · working)`, `applies_to: "household"`. The
  spec comment states the interpretation directly: "urban / middle access
  RELATIVE TO rural. +2 df."

**Design matrix.** Shape `(1555, 10)`, one row per household, extracted at the
loader's own group boundaries with within-block constancy and finiteness
verified. Recorded rank 10, singular values `30.400, 19.677, 16.411, 15.070,
13.356, 12.880, 12.027, 11.269, 7.717, 1.679`, no `|corr| > 0.9` pair.

**Consequence for the joint nulls.** With `gsur` a continuous rate rather than a
region dummy, and with the ten coordinates spanning three distinct constructs —
one continuous access rate, seven region intercepts against reference region 1,
two urbanisation intercepts against rural — the task plan's H0-A (`q = 10`),
H0-B (`q = 7`, the seven NUTS-1 dummies) and H0-C (`q = 2`, the urbanisation
pair) are each writable. `gsur` belongs to none of H0-B or H0-C and must be
stated separately, exactly as task plan §9.2(1) required conditional on this
verification.

---

## 16. Phase-4 bread provenance

**G-F closed. V-10 closed.**

**Exact complete-bundle filenames — eight files, all present:**

```
hessian_eigenvalues.csv
hessian_free.csv
hessian_free.npy
phase4_console.log
phase4_diagnostics.json
phase4_manifest.json
regional_hessian_subblock.csv
regional_schur_complement.csv
```

Seven of these are the runner's `PHASE4_ARTIFACTS` tuple; `phase4_manifest.json`
is written last and is excluded from its own hash map. The runner enforces the
exact set twice — before the console log is written, and again after the manifest
— so the bundle membership is closed, not conventional.

*Discrepancy, nonblocking.* `FR_P2a_region_live_phase4_execution_report_v2.md`
describes `hessian_free.npy` as "optional". In the accepted runner it is a
**required** member of `PHASE4_ARTIFACTS` and of the exact-set check; a bundle
without it would be refused publication. The report wording understates the
artifact's status.

**Per-file hashes recomputed against the manifest — all seven MATCH:**

| File | SHA-256 | Manifest |
| --- | --- | --- |
| `hessian_eigenvalues.csv` | `f29a1a1b31cbfe73e9359c6e38f175cd55e744744d0835a006511afe10476611` | match |
| `hessian_free.csv` | `8985b619858ce8b6c5f4bbb2700bfbb7c22333c17538cc1eb8dc5b09b58f470e` | match |
| `hessian_free.npy` | `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061` | match |
| `phase4_console.log` | `581a307e92534277534c04fedf150044b651e5ef65beffde7e29e5f7983c887d` | match |
| `phase4_diagnostics.json` | `5facb3ab9a6aa326e688eede781da8178b6033569c5891eb7bd0b8197ba3a1f3` | match |
| `regional_hessian_subblock.csv` | `2dc64925319773235d6ceb30c49aa4cf59a44781af4c592eb0bd017f9511b909` | match |
| `regional_schur_complement.csv` | `c00127bbb650d7edf46934e1e6189d5e88dd470ca616df4312b808c57705614d` | match |

**Bundle hash recomputed.** Algorithm read from
`_phase4_finalize` (lines 3076–3087):

```python
hashes = {n: sha256(staging / n) for n in PHASE4_ARTIFACTS if present}   # manifest excluded
joined = "\n".join(f"{n}:{hashes[n]}" for n in sorted(hashes))
bundle_sha256 = sha256(joined.encode("utf-8")).hexdigest()
```

Recomputed value:
`5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`
— identical to the manifest field and to the expected value in the audit brief
and the charter. **MATCH.**

**Authoritative Hessian artifact: `hessian_free.npy`.**

Both files are written from the same in-memory array `arrays["H"]`
(`_phase4_write_artifacts`, lines 2996–3003): the `.npy` via `np.save`, the CSV
via `pandas.DataFrame(...).to_csv` at default float formatting. Loading both and
comparing:

| Property | Value |
| --- | --- |
| `.npy` dtype / shape / layout | `float64`, `(37, 37)`, C-contiguous |
| CSV row labels == `free_names` | yes |
| CSV column labels == `free_names` | yes |
| Entries differing | **337 of 1,369** |
| `max abs(npy − csv)` | `1.8189894035458565e-12` |
| `max rel(npy − csv)` | `4.649896209284979e-13` |
| Largest-deviation entry | `[34, 34]`: npy `10002.427387503121`, csv `10002.42738750312` |
| Bitwise identical | **no** |

The CSV is written at pandas' default ~16-significant-digit float formatting and
does **not** round-trip float64 exactly. `hessian_free.npy` is bit-exact to the
evaluated Hessian; `hessian_free.csv` is a rendering. **This corrects task plan
§10.2(3), which asserted that "float64 written at 17 significant digits
round-trips exactly under IEEE-754" and that the Phase-4 dual-format precedent is
lossless.** The precedent is dual-format, but the CSV leg is lossy at the
`1e-12` level.

**The stored Hessian is the RAW, unsymmetrised matrix.** `_phase4_diagnose`
computes `sym, Hs = _phase4_symmetry(H, …)` and uses `Hs` for the eigenspectrum,
the loading shares, the regional subblock and the Schur complement, but the
persisted `arrays["H"]` is the pre-symmetrisation `H`. Confirmed numerically: the
`.npy` has `max abs(H − Hᵀ) = 1.8189894035458565e-12`, exactly the recorded
`symmetry.max_abs_asymmetry`. `Hs` is **not** persisted anywhere in the bundle.
Any Phase-5 consumer must therefore load `hessian_free.npy` and apply the same
symmetrisation that Phase 4 applied, against the recorded threshold
`2.3588019878151842e-4`.

**Curvature facts carried forward** (`phase4_diagnostics.json`): `min_eig
0.1037326963880782`; `max_eig 42048.457934380494`; rank 37 of 37 at tolerance
`4.204845793438049e-06`; `n_nonpos 0`; condition number `405353.94719781954`,
tier `clean`; regional Schur `rank 10`, `min_eig 2.255741652065068`;
`solve_vs_pinv_max_abs_diff 8.526512829121202e-14`.

---

## 17. Numerical environment

**V-11 partially closed. HM-X64 does not fire.**

**float64 enable point — verified.** The single enable point on the accepted
route is
`dclaborsupply/likelihood/engine_jax.py::_load_jax()`, line 54:

```python
_jax.config.update("jax_enable_x64", True)
import jax.numpy as _jnp
```

`_load_jax()` is called as the **first statement** of `build_jax_singles_ll`
(line 124). In the runner, every `jnp` array creation occurs strictly after the
corresponding builder call:

| Runner line | Statement | Preceded by a builder call? |
| --- | --- | --- |
| 1157 | `tot(jnp.asarray(theta_star))` | yes (1153–1154) |
| 2153 | `tot(jnp.asarray(theta_start_full))` | yes (2150–2151) |
| 2198, 2221 | `vg_full(jnp.asarray(full))` | yes, via `ctx["tot"]` |
| 2832 | `ctx3["tot"](jnp.asarray(theta_hat))` | yes, via `_phase3_contract` |
| 2844–2845 | `jnp.asarray(free_idx)`, `jnp.asarray(base_full)` | yes |
| 2892, 2909 | `grad_fn(...)`, `hess_fn(...)` | yes |

The runner itself never calls `jax.config.update`; `import jax` / `import
jax.numpy` at function scope do not create arrays and do not fix the x64 flag.
Therefore `jax_enable_x64=True` is in force before any array creation on the
accepted pipeline. All data arrays are captured as `jnp.float64` device
constants inside the builder, and the persisted Hessian is `float64`.

Two other modules set the same flag independently — `se/numerical.py:138` and
`solvers/jax_optimize.py:59` — neither of which is on the accepted Phase-3/4
route.

**Versions.**

| Item | Recorded in accepted manifests | Audit-time interpreter |
| --- | --- | --- |
| Python | `3.12.2` | `3.12.2` |
| NumPy | `2.3.5` | `2.3.5` |
| pandas | `2.3.3` | `2.3.3` |
| SciPy | not recorded | `1.16.2` |
| **JAX** | **not recorded** | `0.10.1` |
| **jaxlib** | **not recorded** | `0.10.1` |
| Platform | not recorded | `Windows-2022Server-10.0.20348-SP0` |
| Machine | not recorded | `AMD64` |
| Thread / XLA flags | not recorded | not queried |

Both the Phase-3 and Phase-4 manifests write
`environment = {"python": …, "numpy": …, "pandas": …}` only
(`_phase4_manifest_skeleton`, lines 3049–3050). No console log records a JAX
version. The audit-time interpreter matches the recorded Python, NumPy and pandas
versions exactly, which is consistent with — but not proof of — its being the
execution environment. The JAX and jaxlib versions at execution time are
therefore recorded as **UNKNOWN**; `0.10.1` is the current environment's value,
not a provenance fact.

This does not block the design memo. Float64 is established from source, not from
a version string, so the `1e-8` score-identity tolerance precondition holds.

---

## 18. Accepted-artifact integrity

All hashes recomputed at audit time. **Every check MATCHES.**

**Accepted theta.** `estimation_results.json → results.joint.theta` is a
47-element float64 vector; `sha256(np.ascontiguousarray(theta).tobytes())` =
`c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`, equal to
`optimizer_diagnostics.json → final_theta_sha256` and to
`phase4_diagnostics.json → theta_hat_sha256`. Accepted negLL
`19053.46553160093`.

**Pins.** All ten remain bitwise equal to their accepted pin values in the
accepted theta; recorded by Phase 3 as `pins_bitwise_accepted: true` and
implied by the matching theta hash.

**Phase-3 bundle.** Four hashed members plus manifest; recomputed bundle SHA-256
`2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b` — **MATCH**
to the expected value, to `phase3_manifest.json`, and to
`phase4_manifest.json → accepted_phase3_bundle_sha256`.

**Phase-4 bundle.** Recomputed `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`
— **MATCH** (§16).

**Runtime inputs and sources.** Thirteen files rehashed against the values
recorded in the Phase-4 manifest; all thirteen match:

| File | SHA-256 (first 12) | Result |
| --- | --- | --- |
| `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` | `492bcfa9c766` | match |
| `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` | `c72e92b16170` | match |
| `theta_p2a_singles_2016_v1.csv` | `930ef3aa753d` | match |
| `outputs/…/fr_p2a_singles2016_regionlive__singles.parquet` | `8bf083ce3be1` | match |
| `outputs/…/fr_p2a_singles2016_regionlive__mnlmeta.json` | `05be40300288` | match |
| `outputs/…/inputs/fr_p2a_draws_geometry__singles.parquet` | `5bcf0e5409ef` | match |
| `outputs/…/inputs/fr_p2a_draws_geometry__meta.json` | `ff2d44221746` | match |
| `outputs/…/rebuild_manifest.json` | `1ed3041ff275` | match |
| `outputs/…/dry_run_report.json` | `ec50ea980343` | match |
| `outputs/…/pre_estimation_reload_verification.json` | `6f457de9f35a` | match |
| `scripts/p2a/run_p2a_regionlive_rebuild.py` | `9dd368180794` | match |
| `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` | `4e9b4f57aec9` | match |
| `docs/France_case/P2a/FR_P2a_region_live_phase4_code_review_v7.md` | `cd0bb6ee5a0c` | match |

**Nested package sources.** Thirteen `dclaborsupply` modules verified: every
working-tree blob equals its `HEAD:` blob at `27756a06…`. Two files —
`spec/parser.py` and `likelihood/_numpy_primitives.py` — have a working-tree
SHA-256 that differs from the `committed_sha256` recorded in the Phase-4
manifest, but their manifest-recorded `working_sha256` values
(`94d436749f7f…` and `4d1a2ad6d781…`) match the audit-time bytes exactly and
`blob_equal` is true in both. This is a line-ending normalisation difference
between the git object and the checked-out file, not a content change; the bytes
seen by the interpreter today are the bytes seen at execution.

**Package identity as recorded.** `package_identity_ok: true`,
`module_path_ok: true`, `module_failures: []`, `ancestry_ok: true` for all ten
imported modules, `expected_commit == gitlink == nested_head == 27756a06…`.
Post-evaluation input recheck in the accepted manifest: `pre == post == accepted`
for all ten authenticated labels; runtime-map fingerprint `f9a5ba9f4d7d…`
unchanged.

---

## 19. Remaining unknowns

1. **JAX / jaxlib version at execution time — UNKNOWN.** Neither accepted
   manifest records it and no console log carries it. The audit-time interpreter
   reports `jax 0.10.1` / `jaxlib 0.10.1`; this is the current environment, not a
   provenance record. Nonblocking: float64 is established from source.
2. **Platform string and thread / XLA flag settings at execution time —
   UNKNOWN.** Not recorded in either manifest. The audit-time platform is
   `Windows-2022Server-10.0.20348-SP0`, `AMD64`.
3. **SciPy version at execution time — UNKNOWN.** Not recorded. Relevant only to
   the Phase-3 L-BFGS-B call, which Phase 5 does not repeat. Audit-time value
   `1.16.2`.

No other fact required by the audit brief or by tasks V-1 to V-12 is UNKNOWN.

---

## 20. Design-blocking gaps

**None.** Gaps G-A to G-F are all closed; none of the eight charter §13 halts or
the seven plan-stage halts fires. The design memo may proceed to finalisation on
every axis, including those the task plan marked as prerequisite-blocked.

Five findings **change content the design memo would otherwise have written**.
They are stated as facts; the decisions they bear on remain the design memo's and
the manager's.

1. **`ln(101)` is not an objective bound (§11).** The task plan's V-4 premise
   that "a fitted choice-only likelihood cannot exceed the uniform benchmark" is
   not supported by the source. `l_g = V_obs − logsumexp_j(V_gj) ≤ 0` with no
   `−ln(101)` floor, because every index term is alternative-specific. Nothing in
   the memo may rest on the average negLL, and the `ln(101)` comparison must be
   dropped rather than restated.
2. **No pin is a normalisation (§9).** All ten are structurally inapplicable to a
   2016 singles sample, by two distinct mechanisms — eight unreferenced by the
   singles builder, two multiplying an identically-zero covariate. The genuine
   normalisations (`beta_c = 1.0`, couples `theta_c = 0.0`, `theta_l_m = -0.8`,
   `beta_ll` removed) sit **outside** the 47-vector. A category-specific pin
   reporting convention with a "normalisation" category would have no members.
3. **`gsur` is a continuous rate, not a region dummy (§15).** It is sourced from
   a `(drgn1, educ3, sex)` lookup, scaled by 10, and declared `offer_only_vars`.
   It cannot be placed in the seven-dummy NUTS-1 null and must carry its own
   statement. Reference categories are verified: NUTS-1 region 1 (`drgn1 == 1`,
   245 households) and rural (`drgru`, 395 households).
4. **The CSV Hessian is not bit-exact (§16).** 337 of 1,369 entries differ from
   the `.npy` at up to `1.82e-12` absolute / `4.65e-13` relative. The
   dual-format precedent exists, but the "17 significant digits round-trips
   exactly" premise in task plan §10.2(3) is false for this writer. The
   authoritative bread is `hessian_free.npy`.
5. **The stored bread is unsymmetrised (§16).** The bundle persists the raw `H`,
   not the symmetrised `Hs` that Phase 4 used for every downstream diagnostic.
   Phase 5 must symmetrise on load, against the recorded threshold
   `2.3588019878151842e-4`, or it will not be using the object Phase 4 accepted.

Two further facts firm up decisions the task plan left conditional:

- The correction-scalar analysis may use `N = G = 1,555` as verified, not
  presumed: there are exactly 1,555 additive terms, exactly 1,555 clusters, and
  no weighting (§12, §13). The row count 157,055 is definitively not a candidate
  for `N`.
- Clustering is verified **degenerate** (§13), so the algebraic identity to the
  OPG sandwich holds in this application. Task plan §13's L-3 literature check is
  therefore the one whose priority is realised.

---

## 21. Files created

Exactly three, all new, all in the MNL repository:

1. `docs/France_case/P2a/FR_P2a_region_live_phase5_source_verification_v1.md`
   — this report.
2. `docs/France_case/P2a/phase5_parameter_map_v1.csv`
   — 47 rows plus header; columns `full_index_0based`, `param`, `block`,
   `status` ∈ {`interior`, `active_bound`, `pinned`}, `free_index_0based`,
   `interior_index_0based`, `accepted_value_full_precision`, `spec_bound_lb`,
   `spec_bound_ub`, `runtime_bound_lb`, `runtime_bound_ub`,
   `active_bound_side`, `dist_to_lb`, `dist_to_ub`, `grad_full_negll`,
   `grad_free_negll`, `pin_value`, `pin_role`, `regional_design_column`,
   `regional_free_position`. Generated directly from the accepted Phase-3 and
   Phase-4 artifacts with order assertions against `free_names` and the
   interior-35 derivation.
3. `docs/France_case/P2a/phase5_source_inventory_v1.json`
   — verified path, SHA-256, git blob and cleanliness for every audited source;
   bundle inventories and hash algorithm; likelihood, cluster and numerical
   contracts; open unknowns.

No other file was created. No pre-existing file was modified. No commit was made.

---

## 22. Immediate next action

Return this report, the parameter map and the source inventory to the Goal 1
manager, together with the task-manager completeness verdict, per
`JMP_M05_stageA_correction_memo_v1.md` §6 step 6.

On the manager's acceptance, the design memo
`docs/France_case/P2a/FR_P2a_region_live_phase5_inference_design_v1.md` may be
drafted to the twenty-two headings of `JMP_M05_task_plan_v1.md` §14, executing
steps 4 to 11 of §17 — step 1 to 3, source verification and gap triage, are
discharged by this report. The five findings in §20 must be carried into the memo
as verified inputs; in particular the memo must not restate the `ln(101)`
argument, must not assign a normalisation category to any pin, must treat `gsur`
separately from the seven NUTS-1 dummies, must name `hessian_free.npy` as the
bread source, and must specify symmetrisation on load.

**FINAL VERDICT: SOURCE CONTRACT COMPLETE WITH NONBLOCKING GAPS**
