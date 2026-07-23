# FR P2a Region-Live — Production Rebuild Plan — v2

Plan-only document. Date: 2026-07-23. Supersedes
`FR_P2a_region_live_production_rebuild_plan_v1.md` (retained as history). Governed by
`FR_P2a_region_live_manager_decisions_v2.md` (canonical; v1 decisions historical). No code was
written; no estimation, EUROMOD, notebook, draw generation, or welfare computation was run; no
data, theta, YAML, result JSON, parquet, or existing output was modified; the certified pooled
baseline (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987) is untouched and unaffected.
P2a region-live remains **provisional**.

**What changed vs v1 (reconciliation, 2026-07-23):**

1. **D-1 binding clarification adopted.** v1's §8 (as amended 2026-07-23) required a full `er_b`
   rebuild *including re-run of seeded draw generation and EUROMOD pricing*. That is **reversed**:
   Phase 1 must **not** rerun EUROMOD and must **not** regenerate proposal draws. The
   reconstruction starts from the **frozen already-priced P2a draw artifacts** and reruns only
   deterministic assembly, region/urbanisation/GSUR revival, and B-pool band logic (§8).
2. **Frozen upstream priced-draw inputs identified by name** (§8): the git-tracked EUROMOD pricing
   cache `MNL/fr_singles_pricing_p2a/priced_*.parquet`, plus a draw-geometry freeze that **does not
   yet exist** and must be produced during notebook stabilization (gate G-0).
3. **Notebook roles integrated** (§4): `fr_singles_pipeline_v1.ipynb` is the frozen region-live
   notebook checkpoint (executed end-to-end, anchor self-verified); `fr_singles_pipeline_v2.ipynb`
   (once created) is the active development notebook; `MNL/scripts/p2a/` is the
   production-validation path.
4. **D-5, D-6, D-7 fully ratified** — all "recommended / MAR / decide" placeholders removed (§19,
   §25); D-3 Schur-complement test R-4 and warning-only R-3, and the D-4 three-tier condition
   scheme, carried from the 2026-07-23 v1 amendment.
5. **Immediate next action** changed from manager ratification to **notebook stabilization followed
   by a Phase 1–2 dry-run** (§24, §27); the implementation prompt (§26) covers Phases 1–2 only;
   Phases 3–8 are preserved by design but **manager-gated** and not part of the next execution.

---

## 1. Plan verdict

**READY FOR NOTEBOOK STABILIZATION.**

The frozen upstream priced-draw inputs required by D-1 are identified unambiguously and the
EUROMOD-outcome half is available on disk and git-tracked (§8). The rebuild is therefore not
BLOCKED. However, Phase 1 **cannot start yet**: the draw-geometry half of the frozen inputs
(`draws_p2a`) was never persisted by the checkpoint notebook — it exists only in-memory (§9 of the
notebook, seed 2026). Producing that frozen geometry artifact is the defining deliverable of the
**notebook-stabilization step** (§24 step 1), executed in `fr_singles_pipeline_v2.ipynb` (the
active development notebook), never by the production runner. Once the geometry freeze exists and
hashes (gate G-0), the Phase 1–2 dry-run proceeds with no further design input. If stabilization
cannot produce the geometry freeze, Phase 1 is BLOCKED and the evidence returns to the manager.

## 2. Evidence inspected

Everything in plan v1 §2, plus (2026-07-23):

- `fr_singles_pipeline_v1.ipynb` read **in full** (57 cells, executed `ec=1..34`, mtime
  2026-07-22 15:14): §§1–8 raw read + eligibility funnel + features + gsur merge; §9 certified
  B-pool draws (in-memory, seed 2026, mirrors `build_bpool_singles.py`); §10 chunked/resumable
  EUROMOD pricing with cache `fr_singles_pricing_p2a/priced_{i:05d}.parquet` and a `SKIP_PRICING`
  mode ("no EUROMOD call is made (all chunks must already be cached)"); §11 take-up traits
  (seed 20162016); §12 `assemble_singles` → `er_p2a`; §12b five-column revival; band overwrite →
  `er_b` (cell `ec=26`); §13–14 spec + warm start + fit (`negLL 19053.4655, iters=540,
  converged=True`, in-cell anchor assert); §15 freeze; §16 cluster SEs; §18 master record +
  cold-reload anchor (numpy backend, "P2a ANCHOR HOLDS — notebook self-verified"); §19 welfare
  verification cell.
- `MNL/fr_singles_pricing_p2a/` verified on disk: 8 chunks (`priced_00000` … `priced_01400`),
  **git-tracked**, 225,836 rows, 1,555 unique `source_idhh`, columns
  `idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider, dgn, draw,
  ils_dispy, bsa00_s` — pricing outcomes only, **no geometry columns**.
- Full-disk search: **no frozen `draws_p2a` geometry artifact exists** anywhere (repo, monorepo,
  EUROMOD-STORAGE); the only draw-bearing parquets are the pooled-P3a and engine-ready/welfare
  files, all excluded by D-1.
- `FR_P2a_region_live_manager_decisions_v1.md` (ratified) and the v2 binding clarification.

## 3. Current artifact problem

Plan v1 §3 stands, updated by the notebook checkpoint:

- The **missing region-live diagnostic bundle** is unchanged: no committed gradient,
  Hessian/eigenvalues/rank/condition, region-live cluster SE (the notebook §16 SE run wrote
  `p2a_se_clustered.csv` region-live, but outside a pre-registered gate discipline), persisted
  production optimizer status, or production cold-reload verification. The region-dead evidence of
  five near-zero eigenvalues on the region block is still the unresolved identification question.
- The notebook checkpoint **self-verifies the anchor** (fit 19053.4655; cold reload
  19053.465532 = full-precision 19053.46553160094 to print precision) — good evidence, but a
  notebook cell is not a production pipeline; the strict verdict still requires `scripts/p2a/`.
- **New gap (decisive for scheduling):** the priced-draw cache carries outcomes only; the draw
  geometry/proposal densities consumed by §12 (`feat2`/`alt2` from `draws_p2a`) were never frozen.
  Until stabilization freezes them, no production Phase 1 can satisfy D-1 without either
  regenerating draws (prohibited) or reading an engine-ready parquet (prohibited).
- The mixed-vintage `outputs/p2a_singles2016/` root and the three on-disk region-live engine-ready
  frames remain **reconciliation objects only** (§8): compared and hashed, never copied to
  canonical.
- Caution for stabilization: the checkpoint notebook's §15/§18 cells **overwrite**
  `P2A_MASTER_RECORD.md`, `p2a_fit_provenance.json`, `theta_p2a_singles_2016_v1.csv` and the root
  engine-ready parquet at the repo root/outputs root. Any stabilization re-run in
  `fr_singles_pipeline_v2.ipynb` must redirect writes into `region_live_v1/` (or suppress them) so
  the doc-repaired artifacts and labelled history are not clobbered again.

## 4. Repository ownership and notebook roles

| Concern | Owner | Rationale |
|---|---|---|
| Orchestration scripts (`scripts/p2a/`), run config, output bundle, strict report | **MNL** | JMP-specific empirical provenance (`scripts/bpool`, `scripts/welfare` convention; `docs/France_case/P2a`) |
| Loader, spec parser, JAX engine, L-BFGS-B wrapper, Hessian SE, sandwich + T1–T5, diagnostics | **dclaborsupply-monorepo** (import only) | Validated reusable APIs; the rebuild imports and adds nothing |
| Job_Market_paper | untouched | Writing repo |

**Notebook roles (binding):**

- `fr_singles_pipeline_v1.ipynb` — **frozen region-live notebook checkpoint.** The executed
  reference defining `er_b` and the anchor. Never modified, never re-run by this rebuild.
- `fr_singles_pipeline_v2.ipynb` — **active development notebook, once created.** The only place
  notebook-side work happens (notebook stabilization, §24 step 1): it freezes the draw geometry,
  redirects all writes into `region_live_v1/`, and re-verifies the anchor. Created from v1;
  v1 itself stays untouched.
- `MNL/scripts/p2a/` — **production-validation path.** Consumes only frozen inputs; never
  generates draws, never calls EUROMOD, never opens a notebook.

No package-core change (D-8): the chunked-score primitive stays a thin local copy in
`scripts/p2a/`; `dclaborsupply-monorepo` receives no edits.

## 5. Active specification

Unchanged from plan v1 §5. Exact YAML `MNL/scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`
(certified, read-only; no P2a-specific spec exists — the P2a run is a run-level overlay).
Partition of the 47-vector: spec-level fixed (`theta_l_m = −0.8`, `beta_c = 1`, couples
`theta_c = 0`, `beta_ll = 0`); **10 run-level pins** (`beta_l0_m, beta_l_age_m, beta_l_age2_m,
beta_l0_f, beta_l_age_f, beta_l_age2_f, beta_l_nkids_f, theta_l_f, beta_E_y2015, beta_E_y2017`);
**37 free** (singles leisure, hours, market/region incl. `beta_E_gsur, beta_E_drgn2..8,
beta_E_drgur, beta_E_drgmd`, occupation block free, wage block); **2 at bound**
(`beta_l_age2_sm, beta_l_age2_sf`); SE free block **35**. Warm start
`scripts/bpool/specs/theta_hat_realdata_901_v1.csv` (= the `certified` column of
`theta_p2a_singles_2016_v*.csv`). Pins declared in
`MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`; certified YAML not edited.

## 6. JAX compatibility

Unchanged from plan v1 §6. The route is entirely inside the validated JAX surface
(`build_jax_singles_ll`, float64; `wage_spec = vw`; `loc_empirical`/`vw_occupation` barred; loader
fully supports `drgn1/drgur/drgmd/drgru/gsur`; Hessian = `jax.hessian`; scores = chunked
`jax.jacrev` of the `per_group=True` positive-LL). The NumPy reference engine
(`engine_numpy`/`compute_index`) provides the cross-backend check used in Phase 2.

## 7. Proposal versus structural occupation treatment

Unchanged from plan v1 §7. Proposal side: occupation-conditional draw density (W1 wages, empirical
occ), carried **entirely in the data** through `prior`/`log_prior` and proposal-weighted centering —
the rebuild does not regenerate draws, so the correction is frozen in the priced-draw inputs.
Structural side: occupation enters only the estimated `occupation_opportunity` dummy block in
`log_market`; the structural wage density is plain `vw`. Proposal occupation conditioning is not
structural occupation-wage modelling.

## 8. Data-wiring reconstruction (binding D-1 boundary)

**The reconstruction boundary (Decision D-1 v2, verbatim):**

frozen already-priced P2a draw artifacts
→ `assemble_singles`
→ independently reconstruct `drgn1/drgur/drgmd/drgru/gsur`
→ apply B-pool band overwrite
→ `er_b`
→ freeze under `region_live_v1/`

**Phase 1 must not rerun EUROMOD and must not regenerate proposal draws.** The existing
engine-ready frames are comparison artifacts only and must not be copied as the new canonical
object. A later separate gate may test end-to-end draw-generation and EUROMOD-pricing
reproducibility; that is outside this rebuild.

**Authoritative sources by role:**

1. **Geometry, draws, proposal densities, and already-computed EUROMOD outcomes — the frozen
   upstream priced-draw artifacts actually consumed by §§12–12b of the checkpoint notebook,
   identified by name:**
   - *(available, git-tracked)* **EUROMOD pricing cache**
     `MNL/fr_singles_pricing_p2a/priced_{00000,00200,00400,00600,00800,01000,01200,01400}.parquet`
     — 8 chunks (CHUNK=200 over the 1,555 sorted single households), 225,836 rows, columns
     `idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider, dgn, draw,
     ils_dispy, bsa00_s`. This is exactly what notebook §10 (cell `ec=22`) reads back in
     `SKIP_PRICING` mode, i.e. the already-computed EUROMOD outcomes per (household, draw).
   - *(missing — G-0 blocker, stabilization deliverable)* **Frozen draw-geometry artifact**:
     the per-(idhh, draw) geometry and proposal densities of `draws_p2a` (hours, wage, loc4,
     working flag, B-pool band flags `working_pt1/pt2/ft/lh`, `log_prior` and its `log_q_E/H/W/Occ`
     components, plus the carry columns `feat2` adds: `age_norm, age_norm2, n_children,
     source_idhh, source_idorighh`). The checkpoint notebook builds this in-memory (§9, seed 2026)
     and never persists it. **Notebook stabilization must freeze it** as
     `outputs/p2a_singles2016/region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet`
     (+ a small `__meta.json` with seed, draw design string, row/column contract, SHA-256), written
     by `fr_singles_pipeline_v2.ipynb`. The production runner treats it as read-only frozen input.
     **An engine-ready parquet must not be substituted for it.**
2. **Region and urbanisation** — reconstructed independently from the raw EUROMOD FR input
   `EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`: `drgn1` (8 NUTS-1 macro-regions, 1–8);
   `drgur/drgmd/drgru` one-hot from EU-SILC `db100` (1=urban, 2=intermediate, 3=rural, per
   `euromod_fr_2015_2017_input_variables.csv`).
3. **GSUR** — reconstructed by merge from
   `EUROMOD-STORAGE/Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` (48 valid rows) on the
   documented keys `(drgn1, educ3, sex)`, opportunity-year 2015 for the 2016 wave
   (`JMP_GSUR_year_alignment_decision_v1.md`; `RURO_GSUR_SOURCE_AND_MERGE_AUDIT_v1.md`).

**Phase 1 procedure (deterministic assembly only — no EUROMOD, no draw generation):**

1. **Deterministic pre-assembly.** Re-run the checkpoint's deterministic raw-data transforms
   (§§1–8 equivalents ported to `scripts/p2a/`): read `FR_2016_a3.txt`, reproduce the eligibility
   funnel to the 1,555 decider households (`singles_dec`-equivalent), derive features
   (`educ3/educL/educH`, `pexp`, `loc4`, worker flag, `n_children` from household members), and
   merge `gsur` per role 3. Output the audit mapping
   `region_map_p2a_singles2016.parquet` (one row per `idhh`: `drgn1, drgur, drgmd, drgru, gsur`
   + `idorighh, educ3, sex`).
2. **Load frozen inputs.** Read the pricing cache (all 8 chunks; assert full coverage of the 1,555
   households and the chunk grid `i = 0, 200, …, 1400`) and the frozen geometry artifact (G-0:
   exists + hash matches + 1,555×101 = 157,055 decider rows + column contract). Rebuild the
   take-up traits deterministically (§11 equivalent: revealed-first rates from priced draw-0 +
   seeded Bernoulli, seed 20162016) and apply the take-up income mask
   (`ils_dispy_takeup = ils_dispy − bsa00_s·(1−take)`).
3. **`assemble_singles` → revival → bands → `er_b`.** Run
   `dclaborsupply_app.de.engine_ready.assemble_singles` on the merged priced+geometry frame
   (including the checkpoint's draw-0 unknown-occupation mode-imputation rule); independently
   revive the five columns from the step-1 mapping (never from any engine-ready file); apply the
   B-pool band overwrite from the frozen geometry's band flags. The result is `er_b`.
4. **Freeze + reconcile.** Freeze `er_b` as
   `region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json` — the
   canonical stem every downstream phase reads. Then **prove equality** against each existing
   region-live frame (root `fr_singles_engine_ready_p2a_bpool.parquet` 07-22, root `_v2.parquet`
   07-13, adapter stem `outputs/p2a_singles2016/fr_p2a_singles2016__singles.parquet` 07-13) after
   stable row sorting, common-column ordering, and dtype normalization — agreement required on
   **all substantive values** (every engine-consumed column), and the three frames must agree with
   each other. Any disagreement → **S-1**, stop. The five-column idempotence check (applying the
   step-1 mapping to the existing frames reproduces them unchanged) is retained as a secondary
   confirmation. The existing frames are never copied into `region_live_v1/`.

**Validations (all hard-gated in Phase 1, G-18):** one-to-one mapping (1,555 rows, unique `idhh`,
anti-join empty); region support (`drgn1 ∈ {1..8}`, all 8 present, counts equal source counts
{1:245, 2:254, 3:122, 4:135, 5:279, 6:175, 7:182, 8:163}); urbanisation one-hot
(`drgur+drgmd+drgru == 1`); GSUR in `[0.05, 0.23]`, non-constant (≈47 unique, mean ≈ 0.0945);
within-household constancy across the 101 alternatives; no cross-household leakage; frame
reconciliation (above); shape 157,055 × contract columns, 1,555 HH (841 sf + 714 sm), 101 alts/HH.
All Phase-1 outputs (mapping, comparison report, SHA-256 hashes) written to `region_live_v1/`
before anything else runs.

## 9. Production script architecture

Two scripts + one run-config in `MNL/scripts/p2a/` (repo `run_*`/`verify_*` convention):

- **`run_p2a_regionlive_rebuild.py`** — phase-structured orchestrator; CLI `--config`, `--phase`,
  `--out` (default `region_live_v1/`), `--dry-run` (**Phases 1–2 only — the next execution**).
  Imports only dclaborsupply package APIs (`EstimationSpec`, `load_singles` /
  `load_engine_ready_stem`, `build_jax_singles_ll`, `compute_index` (numpy + jax backends),
  `solvers/jax_optimize`, `se/cluster_robust`, `se/numerical`) plus stdlib/numpy/pandas/jax. Local
  code is limited to: Phase-1 funnel/mapping/assembly reconstruction, the 10-pin free-mask wrapper,
  a thin chunked-score loop (Phase 5, later), eigen/rank/condition reporting (Phase 4, later), and
  artifact/provenance emission. No likelihood math duplicated. **Hard-coded refusals:** the runner
  contains no EUROMOD import, no draw-generation code path, no notebook I/O, and asserts every
  write path resolves inside `region_live_v1/`.
- **`verify_p2a_regionlive_reload.py`** — Phase-7 fresh-process cold-reload verifier (unchanged
  design, manager-gated).
- **`configs/p2a_regionlive_rebuild_v1.yaml`** — run-config carrying: certified spec path, frozen
  input paths + SHA-256 (pricing cache chunks, geometry artifact, raw txt, gsur lookup), warm-start
  source, the 10 pins, cluster column `idorighh`, targets 19053.4655 / 19053.46553160094, and the
  ratified gate thresholds of §19 (all values final — no placeholders).

## 10. Output-directory contract

All new artifacts go to **`MNL/outputs/p2a_singles2016/region_live_v1/`**; nothing outside it is
written, overwritten, moved, or deleted (runner-enforced). Contract:

```text
outputs/p2a_singles2016/region_live_v1/
  inputs/
    fr_p2a_draws_geometry__singles.parquet    # stabilization deliverable (notebook v2) — frozen geometry
    fr_p2a_draws_geometry__meta.json          # seed 2026, draw-design string, contract, SHA-256
  region_map_p2a_singles2016.parquet          # Phase 1: idhh -> 5-column source mapping (+ audit cols)
  data_wiring_validation.json                 # Phase 1: §8 checks, frame reconciliation, hashes, G-0 evidence
  fr_p2a_singles2016_regionlive__singles.parquet   # Phase 1: frozen canonical engine-ready stem (er_b)
  fr_p2a_singles2016_regionlive__mnlmeta.json
  dry_run_report.json                         # Phase 2: theta evaluation + backend agreement + resolved T3 count
  estimation_results.json                     # Phase 3 (manager-gated)
  theta.csv                                   # Phase 3 (manager-gated)
  optimizer_diagnostics.json                  # Phase 3 (manager-gated)
  hessian_diagnostics.json                    # Phase 4 (manager-gated)
  cluster_robust_se.csv                       # Phase 5 (manager-gated)
  post_estimation/                            # Phase 6 (manager-gated)
  cold_reload_verification.json               # Phase 7 (manager-gated)
  provenance.json                             # assembled from Phase 1 onward
  rebuild_manifest.json                       # Phase 8 (manager-gated)
```

The mixed-vintage `outputs/p2a_singles2016/` root, the root parquets/thetas, and
`p2a_fit_provenance.json` stay in place untouched as labelled history — hashed into provenance,
never edited (theta-pointer repair remains a manager-gated doc action after the strict verdict).

## 11. Estimation procedure (Phase 3 — manager-gated, NOT part of the next execution)

Preserved from plan v1 §11 unchanged in design: load the frozen `region_live_v1` stem; build
`neg_ll = neg_ll_sm + neg_ll_sf` (47-vector binding, 10-pin free-mask, 37 free); warm start =
certified pooled theta; bounds from the spec; L-BFGS-B via the package wrapper with the checkpoint
options `maxiter=5000, maxcor=30, ftol=1e-15, gtol=1e-10`; persist full optimizer diagnostics;
objective gate G-1 (D-2). No optimistix polish; no two-stage/basin protocol (a reproduction, not a
search). **Runs only after the manager reviews the Phase 1–2 dry-run evidence.**

## 12. Gradient and convergence diagnostics (Phase 3 — manager-gated)

Preserved from plan v1 §12: analytic `jax.grad` at `theta_hat`; gates = optimizer `success == True`
(G-2) **and** `max|grad| < 1e-2` over the **35 non-bound free** parameters (G-3, ratified D-5); the
2 at-bound parameters reported, not gated; at-bound set must equal `{beta_l_age2_sm,
beta_l_age2_sf}` exactly (G-15, ε = 1e-5, ratified D-5); iteration count informational (anchors:
353 walkthrough / 540 checkpoint).

## 13. Hessian and rank diagnostics (Phase 4 — manager-gated)

Preserved from plan v1 §13 (as amended 2026-07-23): exact JAX Hessian, free block 37×37 and SE
block 35×35; symmetry `max|H − Hᵀ| ≤ 1e-8·max|H|` (G-6, D-4) then symmetrize; full spectrum
persisted; PD gate `min_eig > 0` strictly (G-5); numerical rank `== 37` under
`ε_rank = 1e-10·max_eig` (G-7, D-3); **condition number three-tier (D-4): ≤ 1e7 clean / 1e7–1e10
warning (recorded, no halt) / > 1e10 hard failure (S-4)**, actual value reported against the
certified pooled cond 1.295e6; smallest-eigenvector loadings compared against the region-dead flat
direction; bounds-and-pins restated for a self-contained verdict.

## 14. Region × urbanisation identification test (Phase 4 — manager-gated)

Preserved from plan v1 §14 (as amended 2026-07-23, ratified D-3):

- **R-1 (hard):** 10-column household-level regional design matrix (`gsur, reg2..reg8, drgur,
  drgmd`; 1,555 × 10) has `matrix_rank == 10` under `ε_rank`; singular values and pairwise
  correlations reported (|corr| > 0.9 flag retained as sub-check).
- **R-2 (hard):** raw 10×10 regional Hessian sub-block PD (`min_eig > 0`).
- **R-4 (hard, Schur):** conditional regional-information matrix
  `S_R = H_RR − H_RO · H_OO⁻¹ · H_OR` (pinv rcond 1e-10) has `rank == 10` and `min_eig > 0`
  strictly; spectrum persisted.
- **R-3 (warning only, never gates):** regional squared-loading share on each of the 3 smallest
  eigenvectors, warning flag at ≥ 0.5 (`region_loading_share_warning`); informative
  "flat-direction lifted" narrative vs the region-dead 5-near-zero-eigenvalue evidence.
- **Verdict** `region_urbanisation_identification: PASS / FAIL` = R-1 ∧ R-2 ∧ R-4. FAIL → S-5,
  evidence to the manager (keep all 10 / reduce / regularise); no silent re-specification. A PASS
  is a real-data **local**-identification result only (D-7): no synthetic-recovery claim.

## 15. Cluster-robust inference (Phase 5 — manager-gated)

Preserved from plan v1 §15, with D-5/D-6 fully ratified: chunked per-group `jax.jacrev` scores
(~200 households/chunk); **T1** identity `np.allclose(sum_scores, −gradient, atol=1e-8, rtol=1e-8)`
(G-10, D-5); meat + sandwich on the 35-param SE block via `compute_cluster_robust_se` (pinv rcond
1e-10, no finite-sample correction); **T2** meat symmetry atol 1e-10; **T3** cluster count = the
integer resolved **automatically in Phase 1/2** as the unique nonmissing `idorighh` count in the
frozen sample (consistency across mapping and stem; every household in exactly one cluster; range
1–1,555; no missing ids; persisted in `dry_run_report.json` and the manifest; pooled default 9,657
never used — G-12, D-6, self-ratifying); **T4** all 35 SEs finite and > 0; **T5** robust-vs-Hessian
comparison informational. The stale region-dead `p2a_se_clustered.csv` is never read.

## 16. Post-estimation regeneration (Phase 6 — manager-gated)

Preserved from plan v1 §16: per-group emission (`step4_emit_results_json` pattern) + styled report
(`RURO_post_estimation_styled.py`) reading only the frozen `region_live_v1` stem; everything
labelled `PROVISIONAL — region-live rebuild, pending strict verdict`; stale-input guard (no path
outside `region_live_v1/` opened for write, no region-dead artifact read).

## 17. Cold-reload verification (Phase 7 — manager-gated)

Preserved from plan v1 §17: fresh-process verifier; hash re-verification; parameter-ordering check;
anchors `|negLL − 19053.4655| < 1e-2` and `|negLL − negLL_stored| ≤ 1e-6` (D-2);
`cold_reload_verification.json` with environment record.

## 18. Provenance and hashing

Preserved from plan v1 §18, extended for the frozen inputs: `provenance.json` records SHA-256 of
raw `FR_2016_a3.txt`; gsur lookup; **all 8 pricing-cache chunks**; **the frozen geometry artifact +
meta**; the mapping table; the three pre-existing region-live frames (reconciliation record); the
frozen `region_live_v1` stem + mnlmeta; certified spec YAML; warm-start theta CSV; run-config; both
scripts (self-hash). Plus: the ordered 47-name contract, pins, at-bound names, bounds; targets
(19053.4655 / 19053.46553160094; region-dead 19071.6562 context); environment and git state (MNL +
monorepo SHAs, dirty flags); lineage pointers (checkpoint notebook cells, `p2a_fit_provenance.json`,
the missing-`propagate_regionlive.py` note, walkthrough cell `7c42e9bd`); the full gate table
mirrored into `rebuild_manifest.json`.

## 19. Pre-registered pass criteria (all ratified — no open values)

| # | Criterion | Threshold (ratified) | Source |
|---|---|---|---|
| G-0 | Frozen-inputs gate (Phase 1 precondition) | pricing cache: all 8 chunks present, hashes match run-config, 1,555 HH covered; geometry artifact exists + hash matches + 157,055 decider rows + column contract; raw txt + gsur lookup hashes match | D-1 v2 (binding); produced by notebook stabilization |
| G-1 | Objective reproduction (Phase 3) | `\|negLL − 19053.4655\| < 1e-2` AND `\|negLL − 19053.46553160094\| ≤ 1e-4` | D-2 |
| G-2 | Optimizer success | scipy `success == True`, status recorded | D-5 |
| G-3 | Gradient at optimum | `max\|grad\|` (35 non-bound free) `< 1e-2` | D-5 |
| G-4 | Solver options (inputs, not gates) | `ftol 1e-15, gtol 1e-10, maxiter 5000, maxcor 30` | checkpoint anchor run |
| G-5 | Hessian PD | `min_eig > 0` strictly (free block); `n_nonpos` counter at eig ≤ 1e-8 | Check-5 precedent |
| G-6 | Hessian symmetry | `max\|H − Hᵀ\| ≤ 1e-8 · max\|H\|` before symmetrization | D-4 |
| G-7 | Numerical rank | free-block rank == 37 with `eig > 1e-10 · max_eig` | D-3 |
| G-8 | Condition number (three-tier) | `≤ 1e7` clean; `1e7–1e10` warning (no halt); `> 1e10` hard failure; actual value reported vs pooled 1.295e6 | D-4 |
| G-9 | Region × urbanisation block | R-1 design rank == 10; R-2 raw sub-Hessian PD; R-4 Schur complement rank == 10 and `min_eig > 0`. R-3 loading share = warning only, never gates | D-3 |
| G-10 | Cluster-score identity (T1) | `np.allclose(sum_scores, −grad, atol=1e-8, rtol=1e-8)` | D-5 |
| G-11 | Meat symmetry (T2) | atol 1e-10 | package precedent |
| G-12 | Cluster count (T3) | exact match to the Phase-1/2 measured unique nonmissing `idorighh` count; consistency mapping↔stem; one cluster per household; range 1–1,555; no missing; **never 9,657** | D-6 (self-ratifying) |
| G-13 | SE validity (T4) | all 35 free SEs finite and > 0; negative-variance→NaN count == 0 | package precedent |
| G-14 | Robust-vs-Hessian SE (T5) | informational log | package precedent |
| G-15 | No unintended bound hits | at-bound set == `{beta_l_age2_sm, beta_l_age2_sf}` exactly, ε = 1e-5 | D-5 |
| G-16 | In-bounds sanity | no free param `< lo − 1e-9` or `> hi + 1e-9` | existing |
| G-17 | Cold reload | hashes + ordering match; `\|negLL − 19053.4655\| < 1e-2`; `\|negLL_reload − negLL_stored\| ≤ 1e-6` | D-2 |
| G-18 | Data-wiring gates | all §8 checks exact/boolean (incl. frame reconciliation and idempotence) | checkpoint asserts + loader contract |
| G-19 | Phase-2 theta evaluation (dry-run gate) | JAX `negLL(theta_stored)` within `1e-4` of 19053.46553160094; NumPy/JAX backend agreement within `1e-6`; **no optimizer call** | mandate (Phase-2 scope) |

## 20. Stop conditions

Any stop halts downstream phases, writes partial diagnostics + a `STOPPED` manifest (never a PASS),
and returns to the manager. No auto-retry, no threshold loosening, no silent re-specification.

- **S-0 (any phase): prohibited-operation stop.** Any attempt to call EUROMOD, generate/regenerate
  proposal draws, call an optimizer during Phases 1–2, run welfare or post-estimation during
  Phases 1–2, modify either notebook, or write outside `region_live_v1/` → immediate halt. These
  refusals are asserted in code, not just documented.
- **S-1 (Phase 1):** G-0 or any data-wiring gate G-18 fails — including the existing frames
  disagreeing with the rebuilt `er_b`, with the source mapping, or with each other.
- **S-2 (Phase 3, gated):** optimizer failure (G-2) or objective-reproduction failure (G-1); a
  negLL *better* than target by more than tolerance is also a stop (the anchor was then not an
  optimum — a finding, not a success).
- **S-3 (Phase 3, gated):** gradient gate G-3 fails, or unintended bound hit (G-15) /
  out-of-bounds (G-16).
- **S-4 (Phase 4, gated):** Hessian non-PD (G-5), symmetry failure (G-6), rank < 37 (G-7), or
  condition number > 1e10 (G-8 hard tier).
- **S-5 (Phase 4, gated):** region × urbanisation hard gates fail (G-9: R-1/R-2/R-4) → evidence
  packaged for manager decision A2; R-3 warnings never trigger S-5.
- **S-6 (Phase 5, gated):** T1/T2/T3/T4 failure (G-10..G-13).
- **S-7 (Phase 7, gated):** cold-reload failure (G-17), including any hash mismatch.
- **S-8 (any phase):** any read of a stale region-dead artifact as input, or any input-file hash
  change mid-run.
- **S-9 (Phase 2):** dry-run theta-evaluation failure (G-19): stored region-live theta does not
  reproduce the objective, or NumPy/JAX disagree beyond 1e-6.

## 21. Files to create

Notebook stabilization (in `dclaborsupply-monorepo/notebooks/`, by the active dev notebook):

1. `fr_singles_pipeline_v2.ipynb` — created from v1; writes redirected into `region_live_v1/`;
   freezes the draw geometry (item 5–6); re-verifies the anchor; v1 untouched.

Code and config (MNL):

2. `MNL/scripts/p2a/run_p2a_regionlive_rebuild.py`
3. `MNL/scripts/p2a/verify_p2a_regionlive_reload.py`
4. `MNL/scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`

Outputs (`MNL/outputs/p2a_singles2016/region_live_v1/`):

5. `inputs/fr_p2a_draws_geometry__singles.parquet` *(stabilization deliverable — G-0)*
6. `inputs/fr_p2a_draws_geometry__meta.json` *(stabilization deliverable)*
7. `region_map_p2a_singles2016.parquet` *(Phase 1)*
8. `data_wiring_validation.json` *(Phase 1)*
9. `fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json` *(Phase 1 frozen stem)*
10. `dry_run_report.json` *(Phase 2)*
11. `provenance.json` *(assembled from Phase 1)*
12.–18. `estimation_results.json`, `theta.csv`, `optimizer_diagnostics.json`,
    `hessian_diagnostics.json`, `cluster_robust_se.csv`, `post_estimation/`,
    `cold_reload_verification.json`, `rebuild_manifest.json` *(Phases 3–8 — manager-gated)*

19. `MNL/docs/France_case/P2a/FR_P2a_region_live_strict_estimation_report_v1.md` *(Phase 8 —
    manager-gated)*

This plan itself (`_v2.md`), the decisions v2, and the reconciliation report are the only files
created by the present design-control task.

## 22. Files not to modify

- `MNL/scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` and
  `theta_hat_realdata_901_v1.csv` (certified — read-only)
- **`MNL/fr_singles_pricing_p2a/priced_*.parquet`** — the frozen pricing cache is read-only frozen
  input; never regenerated, never rewritten
- Everything in `MNL/outputs/p2a_singles2016/` outside `region_live_v1/` (labelled history, incl.
  `P2A_MASTER_RECORD.md`, `p2a_se_clustered.csv`, `estimation_results_p2a_singles2016.json`, PNGs)
- `MNL/p2a_fit_provenance.json`, `theta_p2a_singles_2016_v1.csv`, `_v2.csv`, root
  `fr_singles_engine_ready_*.parquet` (hashed, not touched; the theta pointer stays UNRESOLVED
  until after the strict verdict)
- **Both existing notebooks** — `fr_data_walkthrough.ipynb` and `fr_singles_pipeline_v1.ipynb`
  (the frozen checkpoint); stabilization work happens only in the new `fr_singles_pipeline_v2.ipynb`
- The entire `dclaborsupply-monorepo` package tree (D-8) and anything in `Job_Market_paper`
- The certified pooled baseline artifacts and `EUROMOD-STORAGE` inputs (read-only sources)

## 23. Runtime and memory considerations

Lighter than v1 (no EUROMOD, no draw generation): Phase 1 = raw-txt read + funnel + cache load +
assembly + reconciliation — **minutes, < 4 GB**. Phase 2 = two objective evaluations (JAX + NumPy)
at one theta — **~2–5 min** including jit compile. Gated Phases 3–7 estimates unchanged from v1
(fit 5–20 min; Hessian < 5 min; scores minutes; post-estimation ~10 min; reload ~3 min). Total
dry-run: **well under 15 minutes**; full gated pipeline under 1 hour; no GPU, no EUROMOD, no
cluster resources.

## 24. Implementation sequence

1. **Notebook stabilization** (active dev notebook `fr_singles_pipeline_v2.ipynb`, created from the
   frozen v1 checkpoint): redirect all write paths into `region_live_v1/` (stop clobbering the
   doc-repaired root artifacts); add the geometry-freeze cell persisting `draws_p2a`+`feat2` carry
   columns to `region_live_v1/inputs/` with hashes (G-0 deliverable); re-verify the in-notebook
   anchor. No estimation change; v1 checkpoint untouched.
2. Create `scripts/p2a/` scaffolding (both scripts + run-config; no execution); commit.
3. **Phase 1** — deterministic assembly per §8 from frozen inputs; freeze `er_b`; reconcile;
   `data_wiring_validation.json`. Stop-checks S-0/S-1.
4. **Phase 2** — dry-run verification (no optimizer): package load; loader liveness (reg2 mean ≈
   0.181, gsur mean ≈ 0.0945–0.098, one-hot urbanisation; cluster ids present); spec/param binding
   (47-name ordering; warm-start equality with the `certified` column); proposal-correction sanity
   (`prior` present, `−log_prior` active, proposal-weighted centering on); **evaluate the stored
   region-live theta** (the `trial` column of `theta_p2a_singles_2016_v1.csv` ≡ `_v2.csv`):
   JAX `negLL` within 1e-4 of 19053.46553160094 and NumPy/JAX agreement within 1e-6 (G-19);
   resolve and persist the T3 cluster count (D-6). Write `dry_run_report.json`. Stop-check S-9.
   **`--dry-run` exits here. Manager reviews the evidence.**
5.–11. **Phases 3–8 (manager-gated, preserved by design, not part of the next execution):**
   estimation (§11) → Hessian/rank + region test (§13–14) → cluster SEs (§15) → post-estimation
   (§16) → cold reload (§17) → strict-verdict package (§18–19), ending "awaiting manager strict
   verdict"; single final commit of the §21 list; no push; no promotion; no welfare.

## 25. Ratified manager decisions

Canonical text: **`FR_P2a_region_live_manager_decisions_v2.md`** (v1 historical). Summary of
record — all final, no open values:

- **D-1 (v2 binding):** frozen-inputs reconstruction boundary (§8); no EUROMOD, no draw
  regeneration in Phase 1; existing frames comparison-only; geometry freeze = stabilization
  deliverable; engine-ready parquets never substituted.
- **D-2:** `< 1e-2` (4-dp) and `≤ 1e-4` (full) fit anchors; `≤ 1e-6` cold reload; materially
  better = stop.
- **D-3:** `ε_rank = 1e-10·max_eig`; free rank 37; regional design rank 10; R-2 raw sub-block PD;
  **R-4 Schur complement rank 10 + min_eig > 0 (hard)**; R-3 loading share warning-only.
- **D-4:** symmetry `≤ 1e-8·max|H|`; condition three-tier `≤1e7 / 1e7–1e10 warn / >1e10 fail`;
  compare with pooled 1.295e6.
- **D-5:** T1 `atol=1e-8, rtol=1e-8`; bound ε `1e-5`; gradient gate `1e-2` on 35 non-bound free;
  optimizer success required.
- **D-6:** T3 cluster count auto-resolved from unique nonmissing `idorighh` (consistency; 1–1,555;
  no missing); persisted; never 9,657; no further manager round.
- **D-7:** real-data local diagnostics only; **synthetic recovery mandatory** before promotion,
  structural-identification claims, or baseline replacement; report language capped at
  "real-data Hessian/rank diagnostics pass."
- **D-8:** package upstreaming deferred; no `dclaborsupply-monorepo` changes.

## 26. Exact implementation prompt (Phases 1–2 only)

> **ROLE.** Implement **Phases 1–2 only** of the FR-2016 singles P2a region-live production
> rebuild, exactly per `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md`
> and `FR_P2a_region_live_manager_decisions_v2.md`. The plan is binding: phases, gates (G-0, G-18,
> G-19), stop conditions (S-0, S-1, S-8, S-9), file lists, and the ratified thresholds — all values
> are final in the plan and decisions v2; there are no placeholders to fill.
>
> **PROHIBITED (hard stops, assert in code):** optimizer calls of any kind; EUROMOD (no import, no
> connection, no pricing); draw generation or regeneration (no call into `hours_mixture_d1`,
> `occ_draw_empirical`, `pilot_wage_draw`, `build_bpool_singles`, or any RNG-based draw path);
> welfare; post-estimation; modification of either notebook (`fr_data_walkthrough.ipynb`,
> `fr_singles_pipeline_v1.ipynb`); any write outside
> `MNL/outputs/p2a_singles2016/region_live_v1/` (plus the three new files under
> `MNL/scripts/p2a/`). Do not modify the certified spec YAML, `theta_hat_realdata_901_v1.csv`, the
> pricing cache, root thetas/parquets, `p2a_fit_provenance.json`, anything in
> `dclaborsupply-monorepo` or `Job_Market_paper`. Do not loosen any gate. On any stop condition:
> halt, persist partial diagnostics + a STOPPED manifest, report — never write a PASS.
>
> **PHASE 1 (build + freeze).** Precondition G-0: verify the frozen inputs exist and hash —
> `MNL/fr_singles_pricing_p2a/priced_{00000..01400}.parquet` (8 chunks, 1,555 HH) and
> `region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet` (+ meta) from notebook
> stabilization; if either is missing or mismatched → S-1, stop (do NOT substitute an engine-ready
> parquet). Then: deterministic pre-assembly from `EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`
> (funnel → 1,555 deciders → features) + gsur merge from
> `Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` on `(drgn1, educ3, sex)`; take-up traits
> (seed 20162016) and income mask; `assemble_singles` on the merged frozen priced+geometry frame;
> independent five-column revival from the source mapping; B-pool band overwrite → `er_b`; freeze
> as `region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json`; run every
> §8 validation (G-18) and the three-frame reconciliation (existing engine-ready frames are
> comparison artifacts only); write `region_map_p2a_singles2016.parquet` +
> `data_wiring_validation.json` + provenance hashes.
>
> **PHASE 2 (dry-run verification — no optimizer).** Load the frozen stem through the dclaborsupply
> loader; assert loader liveness (reg2 mean ≈ 0.181, gsur mean ≈ 0.0945–0.098, urbanisation
> one-hot, cluster ids present); verify the 47-name binding and warm-start equality with the
> `certified` column of `theta_p2a_singles_2016_v1.csv`; verify proposal-correction sanity;
> **evaluate the stored region-live theta (the `trial` column)**: JAX objective within `1e-4` of
> **19053.46553160094**, NumPy/JAX backend agreement within `1e-6` (G-19; failure → S-9); resolve
> the T3 cluster count per D-6 and persist it. Write `dry_run_report.json`.
>
> **DELIVER.** `MNL/scripts/p2a/run_p2a_regionlive_rebuild.py`,
> `verify_p2a_regionlive_reload.py` (scaffold; Phase-7 body may be present but must not be
> invoked), `configs/p2a_regionlive_rebuild_v1.yaml`, and the Phase 1–2 artifact set (§21 items
> 7–11). Stop after Phase 2 and report to the manager. No estimation, no promotion, no welfare, no
> welfare-readiness statements; P2a region-live remains provisional.

## 27. Immediate next action

**Notebook stabilization, then the Phase 1–2 dry-run.** Concretely: (1) create
`fr_singles_pipeline_v2.ipynb` from the frozen v1 checkpoint — redirect writes into
`region_live_v1/`, add the geometry-freeze cell (G-0 deliverable), re-verify the anchor in-notebook;
(2) run the production Phase 1–2 dry-run per §26 and put `data_wiring_validation.json` +
`dry_run_report.json` in front of the manager. Manager ratification is **no longer** the next
action — the decisions are ratified in v2; Phases 3–8 wait for the manager's dry-run review.
(Doc-repair A3 — theta pointer — and the missing-`propagate_regionlive.py` note A4 remain open in
the manager's queue; neither blocks stabilization or the dry-run, since Phase 1 supersedes the
missing script's logic reproducibly.)
