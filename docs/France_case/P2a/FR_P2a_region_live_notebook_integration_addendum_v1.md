# FR P2a Region-Live — Notebook Integration Addendum (v1)

Date: 2026-07-23. Scope: creation of the isolated active-development notebook
`fr_singles_pipeline_v2.ipynb` from the frozen region-live checkpoint `fr_singles_pipeline_v1.ipynb`.
No notebook was executed; no estimation, inference, EUROMOD, post-estimation, or welfare was run.
Governs alongside `FR_P2a_region_live_manager_decisions_v2.md` (canonical).

## 1. Notebook status

The FR-2016 singles P2a region-live pipeline now has two notebooks:

- **v1** (`notebooks/fr_singles_pipeline_v1.ipynb`) — **frozen** region-live checkpoint. Verified to
  contain the region-live fit and anchor at negLL **19053.46553160094** (`|negLL − 19053.4655| < 1e-2`,
  anchor self-verified). Committed and unmodified.
- **v2** (`notebooks/fr_singles_pipeline_v2.ipynb`) — **active development**, output-isolated,
  provisional. All expensive stages default OFF.

P2a region-live remains **provisional**: not accepted, not safe for inference, manuscript results,
or certified welfare. The theta pointer in `p2a_fit_provenance.json` remains UNRESOLVED.

## 2. Frozen v1 role

v1 is the immutable reference state of the region-live rebuild. It is the notebook that first
reproduced negLL 19053.4655 with an in-notebook anchor assert. It must not be edited for development;
it is the comparison baseline for any v2 change and for the production rebuild's equality cross-checks.

## 3. Active v2 role

v2 is where development continues. It preserves all economic/computational code from v1 but:
adds a provisional banner; adds five run-flags (default False); redirects every notebook-generated
artifact beneath an isolated output root; corrects generated metadata; and adds provisional/scope
notes to the inference, reproduction, and welfare sections. Per manager decision **D-1**, notebook
stabilization (including persisting the in-memory `draws_p2a` geometry artifact) is a v2
responsibility — see §14.

## 4. Production-script role

The **strict production verdict is not produced by either notebook.** It comes from the JMP-specific
rebuild + strict-diagnostics code under **`MNL/scripts/p2a/`** (per manager decision D-8; this
directory does not exist yet and is the designated home for the chunked score orchestration and the
strict gate battery). The notebook produces preliminary evidence only. The **certified 47-parameter
pooled baseline** (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987; synthetic-recovery
certified; real-data Hessian PD; clustered on `idorighh`) remains the formal JMP baseline and is
untouched.

## 5. Output isolation

`NOTEBOOK_OUTPUT_ROOT = outputs/p2a_singles2016/notebook_dev_v2/`. Every write the v2 notebook itself
performs is routed beneath this root:

- engine-ready frame → `notebook_dev_v2/fr_singles_engine_ready_p2a_bpool.parquet`
- theta CSV → `notebook_dev_v2/theta_p2a_singles_2016_v1.csv`
- provenance → `notebook_dev_v2/p2a_fit_provenance.json`
- results JSON / staged parquet / mnlmeta → `notebook_dev_v2/…`
- cluster-SE CSV, master record, post-estimation report dir → `notebook_dev_v2/…`
- any v2-priced EUROMOD chunk → `notebook_dev_v2/fr_singles_pricing_p2a/` (the git-tracked
  `fr_singles_pricing_p2a/` cache is read-only shared input).

v2 does **not** write to: `outputs/p2a_singles2016/` root; `outputs/p2a_singles2016/region_live_v1/`
(**single exception, added 2026-07-24:** the operator-gated geometry freeze of §15, which writes only
`region_live_v1/inputs/`); `p2a_fit_provenance.json` (root); `theta_p2a_singles_2016_v1.csv` /
`_v2.csv` (root); or root `fr_singles_engine_ready_p2a_bpool*.parquet`. Verified by static scan
(§11; re-verified for the §15 amendment).

**Known non-isolation (welfare).** The welfare section shells out to the committed
`scripts/welfare/stage_p2a_singles_welfare.py` and `run_p2a_singles_welfare.py`, which hard-code
production/EUROMOD-STORAGE paths and cannot be redirected from the notebook. Under `RUN_WELFARE=False`
(default) nothing runs; if enabled they read the production baseline and write the shared welfare
store — provisional, non-isolated, and flagged in-notebook. Full isolation requires those scripts to
accept an output root (see §14).

## 6. Execution controls

Top-level flags in the controls cell, all default **False**:
`RUN_PRICING`, `RUN_ESTIMATION`, `RUN_INFERENCE`, `RUN_POST_ESTIMATION`, `RUN_WELFARE`.

Guarded sections and behaviour when disabled:

- **pricing** (`RUN_PRICING`): EUROMOD is never called unless True; the shared/dev cache is loaded and
  the run raises if a chunk is missing. Prints a clear skip message.
- **estimation** (`RUN_ESTIMATION`): L-BFGS-B fit + freeze/adapter; when off, sets fit objects to
  `None` and prints skip (downstream sections check `r_b is not None`).
- **inference** (`RUN_INFERENCE and r_b is not None`): cluster-robust sandwich SEs.
- **post-estimation** (`RUN_POST_ESTIMATION`): styled report subprocess.
- **welfare** (`RUN_WELFARE`): V_i^IS + W-family (provisional).

Every disabled section prints a `[SKIPPED: <FLAG>=False] …` message and avoids referencing
unavailable downstream objects.

## 7. Metadata corrections

In the v2-generated results JSON / mnlmeta:

- `produced_by = notebooks/fr_singles_pipeline_v2.ipynb`
- `analytical_gradient = true`
- `strict_validation = false`
- `status = provisional_notebook_result`
- the incorrect `command_line` reference to `fr_data_walkthrough.ipynb` is removed (replaced by the
  v2 notebook).

## 8. Existing notebook evidence

- The pipeline reproduces the region-live objective negLL **19053.4655** (v1 anchor; `beta_E −4.31 →
  −2.8974` after reviving region/urbanisation/gsur).
- A **35-parameter non-bound** Hessian and cluster-robust sandwich (T1 score identity, occupation
  block free and identified) is computed — **preliminary evidence only**.
- Same-kernel disk-reload anchor holds (the master/anchor section explicitly labels this a
  same-kernel disk-reload check, not a fresh-process cold-reload gate).

## 9. Evidence still missing

The strict production verdict (in `MNL/scripts/p2a/`) separately evaluates, and the notebook does
**not** establish:

- all **37 run-level free parameters** (not just the 35 non-bound) and **bound handling**;
- **regional design-matrix rank = 10**; raw **10×10 regional Hessian block** positive definite;
  **conditional regional Schur complement** (rank 10, positive min-eigenvalue) — manager D-3/R-4;
- **persisted gradients**, **chunked cluster scores**, and a **fresh-process reload** (cold-reload
  `|Δ negLL| ≤ 1e-6`) — manager D-2;
- **synthetic-recovery certification** of the regional/access block (mandatory before any promotion —
  manager D-7).
- Note: `FR_P2a_region_live_production_rebuild_plan_v2.md` is **not on disk** (only `_v1`); this
  addendum reconciles to `FR_P2a_region_live_manager_decisions_v2.md` (canonical) and the `_v1` plan.

## 10. Welfare warning

**PROVISIONAL P2a WELFARE — NOT CERTIFIED AND NOT SAFE FOR MANUSCRIPT USE.** The v2 welfare section
carries this banner in-notebook. Welfare outputs derive from the provisional region-live P2a fit, not
the certified 47-parameter pooled JMP baseline; they are development diagnostics. The welfare scripts
are additionally non-isolated (§5).

## 11. Validation performed

Without executing the notebook:

- **nbformat parse**: v2 valid (59 cells; 35 code, 24 markdown).
- **AST compile**: all 35 code cells compile (guards/indentation intact).
- **v1 unchanged**: `git diff`/`git status --porcelain` empty for v1; working-tree bytes are
  LF-normalized-identical to the committed blob (raw-byte difference is `core.autocrlf` CRLF↔LF only).
- **prohibited-write scan**: 0 violations; all 10 notebook write-verb lines route through
  `NOTEBOOK_OUTPUT_ROOT` / `OUT2` (= root) / the isolated `PRICE_DIR2`.
- **run flags**: all five present and default False; `NOTEBOOK_OUTPUT_ROOT` defined.
- **outputs/exec-counts**: every code cell has `execution_count = None` and empty `outputs`.
- **required notes**: disk-reload note (§12 req), inference-scope note (§13 req), and the welfare
  warning (§14 req) present.

## 12. Files created

- `dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb`
- `docs/France_case/P2a/FR_P2a_region_live_notebook_integration_addendum_v1.md` (this file)

(The v2 notebook run would additionally create `outputs/p2a_singles2016/notebook_dev_v2/` when a stage
is enabled; nothing was executed, so that directory is not yet populated.)

## 13. Files not modified

- `notebooks/fr_singles_pipeline_v1.ipynb` (frozen; verified unchanged)
- `outputs/p2a_singles2016/` production artifacts, `p2a_fit_provenance.json`,
  `theta_p2a_singles_2016_v1.csv` / `_v2.csv`, root `fr_singles_engine_ready_p2a_bpool*.parquet`
- the certified pooled baseline and all `scripts/` and `dclaborsupply-monorepo` package code.

## 14. Immediate next action

1. **Persist the geometry artifact.** Per manager D-1, v2 must freeze the in-memory `draws_p2a`
   (per-(idhh, draw) hours/wage/loc4/working/band-flags/`log_prior`) under `NOTEBOOK_OUTPUT_ROOT` and
   hash it, before any Phase-1 production rebuild consumes it. (Not done here — no execution.)
   (**Update 2026-07-24:** the freeze cell now exists in v2 — operator-gated by
   `EXPORT_PRODUCTION_GEOMETRY` and targeting `region_live_v1/inputs/` per plan v2 §8, which
   supersedes the `NOTEBOOK_OUTPUT_ROOT` destination named above; see §15. Execution is still
   pending, so the frozen artifact does not exist yet.)
2. **Stand up `MNL/scripts/p2a/`** for the strict production rebuild + gate battery (D-1…D-8); it does
   not exist yet.
3. **Welfare isolation (optional):** teach the welfare scripts to accept an output root so v2 welfare
   can write beneath `NOTEBOOK_OUTPUT_ROOT` instead of the shared store.
4. Do **not** commit automatically — the operator reviews the diff summaries first.

## 15. Amendment (2026-07-24) — operator-gated production-geometry freeze cell

The controlled geometry-freeze operation required by manager decision **D-1 (v2)** and plan v2
§8/§24 step 1 was added to `fr_singles_pipeline_v2.ipynb` (nbformat edit; no execution; v1
byte-identical, sha256 `61b9cf4d…`). Output-isolation statement of record:

- **Ordinary notebook outputs remain under `notebook_dev_v2/`** (§5 unchanged in substance).
- The **sole authorized production-output exception** is the explicit, operator-gated,
  **immutable geometry freeze** to `outputs/p2a_singles2016/region_live_v1/inputs/`
  (`fr_p2a_draws_geometry__singles.parquet` + `__meta.json`) — the G-0 frozen input of the
  `scripts/p2a` Phase 1–2 production runner.
- The exception **requires `EXPORT_PRODUCTION_GEOMETRY=True`**, a sixth controls-cell flag
  defaulting **False** (the five original run flags are unchanged and still default False).
- It **does not authorize** estimation, inference, post-estimation, or welfare writes to
  `region_live_v1/` — those remain prohibited from this notebook.

Freeze-cell contract (single code cell, inserted directly after the `draws_p2a`
construction-and-gates cell and before pricing §10; the entire body is one top-level
`if EXPORT_PRODUCTION_GEOMETRY:` — with the flag False it only prints
`[SKIPPED: EXPORT_PRODUCTION_GEOMETRY=False] production geometry freeze not run.`):

- freezes the **already-built in-memory `draws_p2a` only** — no draw-generation call, no
  engine-ready derivation; full column set preserved; canonical stable mergesort by
  `(idhh, draw)` with a fresh index;
- validates against the `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` contract:
  157,055 rows; 1,555 households; exactly 101 alternatives per household; all
  `required_columns` present; exactly one `draw==0` row per household with `is_chosen==1`
  and `log_prior==0`; no duplicate `(idhh, draw)`; seed 2026 (config check + child-seed
  reproduction from `default_rng(2026)`); `prior > 0`; `log_prior` finite; the Wave-0.1
  identity `log_prior == log_q_E + working·(log_q_H+log_q_W+log_q_Occ)` at exact equality;
- atomic write: temporary parquet → SHA-256 of the completed file → contract re-validated on
  the on-disk bytes → `os.replace` promotion; metadata JSON records status
  `frozen_production_input`, producer, seed, draw design, sha256, row/household/column
  counts, dtypes, required columns, UTC timestamp, and the governing decisions/plan documents;
- existing-file rule: create only when neither file exists; if both exist and the parquet
  matches its declared sha256 and re-passes the contract, print "already frozen" and do not
  rewrite; if only one exists or the pair fails its contract, raise without overwriting.

Static validation (2026-07-24, no execution): v1 hash unchanged; v2 nbformat-parses and
schema-validates (60 cells); all 36 code cells AST-compile; every `execution_count` is None
with empty outputs; `EXPORT_PRODUCTION_GEOMETRY` present and False; exactly one code cell
references `region_live_v1` (the freeze cell, targeting `inputs/` only); the freeze cell is a
single top-level `if` on the flag whose False-branch only prints the skip message; no
draw-generation function invoked; all five original run flags default False; placement
verified (after draws gates, before pricing); banner documents the exception. ALL CHECKS PASS.
