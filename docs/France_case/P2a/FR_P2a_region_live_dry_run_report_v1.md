# FR P2a Region-Live — Phase 1–2 Dry-Run Report — v1

Date: 2026-07-24. Executor: production runner `scripts/p2a/run_p2a_regionlive_rebuild.py`
(dry-run mode, Phases 1–2 only). Governed by `FR_P2a_region_live_manager_decisions_v2.md`
(canonical), `FR_P2a_region_live_production_rebuild_plan_v2.md`, and
`FR_P2a_region_live_notebook_integration_addendum_v1.md`.

No estimation, no optimizer call, no EUROMOD, no draw generation, no notebook execution
or modification, no inference, no post-estimation, no welfare. No file outside
`outputs/p2a_singles2016/region_live_v1/` (plus the three new `scripts/p2a/` files and
this report) was written. The certified pooled baseline and all committed P2a artifacts
are untouched. Nothing was committed.

Command executed (from the MNL repo root, exit code 2):

```
python scripts/p2a/run_p2a_regionlive_rebuild.py
  --config scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
  --phase 2
  --out outputs/p2a_singles2016/region_live_v1
  --dry-run
```

Evidence markers used below: **EXECUTED** (produced by this run), **STATIC** (verified
by inspection without running the pipeline), **NOT REACHED** (blocked by the stop).

## 1. Dry-run verdict

**STOPPED** — pre-registered stop **S-1 at gate G-0** (frozen-inputs precondition).

The frozen draw-geometry artifact
`region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet` (+ `__meta.json`) does
not exist. It is the notebook-stabilization deliverable that manager decision **D-1 (v2)**
assigns to `fr_singles_pipeline_v2.ipynb`, and Phase 1 may not start without it. The
runner is prohibited from regenerating draws and from substituting an engine-ready
parquet, and this executor is prohibited from executing or modifying either notebook —
so the stop is the correct, binding outcome, not a defect. Every other frozen input
passed its hash-and-contract check (20 of 21 G-0 items PASS; see §3–§4, §20).

`rebuild_manifest.json` records `status: STOPPED, stop: {code: S-1, gate: G-0}`.
Partial evidence was written as required (§2). Wall time 0.7 s.

## 2. Files created

Code and config (untracked, for operator review — not committed):

1. `scripts/p2a/run_p2a_regionlive_rebuild.py` — Phases 1–2 orchestrator; complete
   Phase-1 port of the frozen checkpoint's deterministic transforms (funnel →
   features → gsur/pexp → take-up → `assemble_singles` → independent revival →
   B-pool band overwrite → freeze → reconciliation) plus the Phase-2 package-load /
   objective-reproduction battery (G-19). Hard S-0 refusals in code: prohibited-module
   guard (EUROMOD connector, `hours_mixture_d1`, `occ_draw_empirical`,
   `pilot_wage_draw`, `build_bpool_singles`, `scipy.optimize`), write-path guard
   (every write must resolve inside `region_live_v1/`), `--phase > 2` refused.
2. `scripts/p2a/verify_p2a_regionlive_reload.py` — fresh-process reload verifier;
   `--mode pre-estimation` (dry-run era reload check) and `--mode cold-reload`
   (Phase-7 strict gate body, present but **refuses to run** while estimation
   artifacts are absent; not invoked in this run, per plan v2 §26).
3. `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` — run-config with all ratified
   thresholds (D-2..D-6), frozen-input SHA-256 registry, checkpoint-derived
   determinism expectations, and the geometry-artifact contract.
4. `docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v1.md` — this report.

Outputs written by the stopped run (all inside `region_live_v1/`):

5. `outputs/p2a_singles2016/region_live_v1/data_wiring_validation.json` — full G-0
   per-item evidence (20 PASS / 1 FAIL).
6. `outputs/p2a_singles2016/region_live_v1/provenance.json` — partial provenance
   (input hashes, binding docs, lineage, targets).
7. `outputs/p2a_singles2016/region_live_v1/rebuild_manifest.json` — STOPPED manifest
   with stop record, config/script hashes, git heads, environment, log.

Both scripts parse and compile (`py_compile` PASS); the config parses (YAML PASS,
24 gate entries, 10 pins).

## 3. Authoritative inputs

All **EXECUTED** hash checks against the config registry — PASS:

| Input | Role | SHA-256 (verified) |
|---|---|---|
| `EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt` (10,056,505 B) | `drgn1, drgur, drgmd, drgru` source (db100-derived urbanisation) | `da3eed57…c8bf88` |
| `EUROMOD-STORAGE/Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet` | `gsur` lookup, keys `(drgn1, educ3, sex)`, opportunity year 2015 | `f51ad630…d03c83` |
| `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` | certified spec (read-only) | `492bcfa9…31f211` — **unchanged** |
| `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` | certified warm start | `c72e92b1…f76269` |
| `theta_p2a_singles_2016_v1.csv` / `_v2.csv` | stored region-live theta (`trial` column) | `930ef3aa…` / `9c8d7ee7…` |

## 4. Frozen priced-draw inputs

- **EUROMOD pricing cache — EXECUTED, PASS.** All 8 chunks
  `fr_singles_pricing_p2a/priced_{00000..01400}.parquet` present; every per-chunk
  SHA-256 matches the config registry; concatenated contract verified: **225,836 rows,
  1,555 unique `source_idhh`**, chunk grid `i = 0,200,…,1400`, exact 10-column set
  (`idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider, dgn,
  draw, ils_dispy, bsa00_s`).
- **Frozen draw-geometry artifact — EXECUTED, FAIL (the G-0 blocker).**
  `region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet` and
  `…__meta.json`: **both absent**. STATIC confirmation of the cause:
  `fr_singles_pipeline_v2.ipynb` on disk has 59 cells, **all
  `execution_count: None` (never run)**, and contains **no geometry-freeze cell** —
  no reference to `fr_p2a_draws_geometry` or `region_live_v1/inputs/` anywhere; its
  §9 draws section rebuilds `draws_p2a` in-memory (seed 2026) without persisting it.
  The stabilization deliverable (plan v2 §24 step 1, addendum §14 item 1) has not
  been produced.

## 5. Existing-frame reconciliation

Full value-level reconciliation of the rebuilt `er_b`: **NOT REACHED** (Phase 1 stopped
before assembly). One material **EXECUTED** result already stands: the three existing
region-live engine-ready frames are **byte-identical** — root
`fr_singles_engine_ready_p2a_bpool.parquet`, root `…_v2.parquet`, and the adapter stem
`outputs/p2a_singles2016/fr_p2a_singles2016__singles.parquet` all hash to
`8bf083ce…9f0d` (23,114,466 B each). The "three frames" are one artifact in three
locations, so the eventual er_b reconciliation reduces to a single comparison. The
committed adapter `__mnlmeta.json` (`495e7c6b…`) is registered as the normalization-
scales reference. All three frames remain **comparison artifacts only** — the runner
never reads them as construction inputs.

## 6. Household mapping validation

**NOT REACHED** (stopped at G-0, before pre-assembly). Implemented and armed in the
runner with hard gates: exactly 1,555 rows, unique `idhh`, no missing values, no
duplicates; funnel-endpoint checks (1,555 single households, 2,236 persons; funnel
household counts vs checkpoint {baseline 10,003 → … → 3,830}); take-up determinism
(seed 20162016; revealed rates 0.548/0.265 expected).

## 7. Region support

**NOT REACHED.** Armed gate: `drgn1 ∈ {1..8}`, all 8 present, counts exactly
{1: 245, 2: 254, 3: 122, 4: 135, 5: 279, 6: 175, 7: 182, 8: 163} at both the mapping
and the revived engine-ready frame.

## 8. Urbanisation validation

**NOT REACHED.** Armed gate: `drgur + drgmd + drgru == 1` per household with each
component in {0,1} (EU-SILC `db100` one-hot), at both the mapping and the revived frame.

## 9. GSUR validation

**NOT REACHED.** Armed gate: lookup filtered to 48 valid rows in [0,1]; 100% match rate
on `(drgn1, educ3, sex)`; household-level `gsur ∈ [0.05, 0.23]`, non-constant,
47 unique values, mean ≈ 0.0945; within-household constancy across the 101 alternatives;
no cross-household leakage (engine rows must equal the mapping row for their `idhh`).

## 10. Choice-geometry invariance

**NOT REACHED.** Armed gates: geometry artifact 157,055 rows = 1,555 × 101, draw 0
chosen-first with `log_prior == 0` and `is_chosen == 1`; assembled `er_b` 157,055 rows,
exactly 1,555 chosen; band-overwrite comparison counts vs the checkpoint
{pt1: 11,342, pt2: 7,391, ft: 7,541, lh: 0}; bpool flags zero on non-working rows;
draw-0 unknown-occupation mode imputation exactly 7 rows → `loc4 = 4`.

## 11. Proposal-density invariance

**NOT REACHED** at runtime. Armed gates: `prior > 0` everywhere;
`prior == clip(exp(clip(log_prior, −700, 700)), 1e-16, ∞)` (package Wave-0.1 identity,
rtol 0 / atol 1e-9, enforced by `assemble_singles._validate_wave01`);
`log_prior == log_q_E + working·(log_q_H + log_q_W + log_q_Occ)`; loader-level
`|log(prior) − log_prior| ≤ 1e-9`. The correction is data-carried from the frozen
geometry — the runner contains no draw path (S-0 guard).

## 12. Frozen stem

**NOT REACHED.** On a PASS run Phase 1 freezes
`region_live_v1/fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json`
(produced_by `scripts/p2a/run_p2a_regionlive_rebuild.py`; normalization scales gated
equal to the committed adapter meta at atol 1e-9; cluster key
`cluster_id ← source_idorighh`; prior convention recorded). Not created in this run —
the output folder holds only the three STOPPED evidence JSONs.

## 13. Specification and pin binding

**EXECUTED (partial):** certified YAML hash verified unchanged (`492bcfa9…`).
**NOT REACHED (runtime):** the Phase-2 binding battery — 47 `spec.all_param_names`
matching both theta CSVs' order; `wage_spec == "vw"`; `fixed_params == {theta_l_m: −0.8}`;
proposal-weighted centering flags; exactly 10 run-level pins (bounds clamped to
warm-start values, the checkpoint mechanism) at explicit indices with 37 free
parameters and per-parameter bounds emitted into `dry_run_report.json`; warm-start
equality against the `certified` columns (≤1e-9 vs v2 full-precision; ≤5e-7 vs v1
rounded); `trial` v1 ≡ v2 cross-check.

## 14. JAX loader liveness

**NOT REACHED.** Armed checks per gender: loader `reg2..reg8` arrays nonzero and
exactly `(drgn1 == k)` from the frozen columns; `gsur` nonzero and array-equal to the
frozen column; urbanisation arrays one-hot and array-equal; `prior` strictly positive;
`cluster_ids` present with one id per household; group counts 841 (sf) + 714 (sm).

## 15. Wage and occupation route

**STATIC (spec + engine source, promotion-readiness §5 + plan v2 §7):** structural
`wage_spec = vw` (log-normal, `sigma`); `loc_empirical` and `vw_occupation` are
parser-recognised only, have no JAX implementation, and are **not** active
structurally; occupation-conditioned proposal information enters only through the
data-carried `prior`/`log_prior`; structural occupation enters only as the estimated
`loc4` access dummies folded into `log_market`. **NOT REACHED (runtime):** the Phase-2
assertions of these facts (`spec.wage_spec`, `wage_loc_groups` absent, `loc4_*`
shifters present in `market_opportunity_shifters`).

## 16. Proposal-correction checks

**NOT REACHED** at runtime (see §11 for the armed identity battery). Design fact
(STATIC): the validated engine applies the correction exactly once —
`V = u + log_h + log_w + log_market − log_prior` — and Phase 2's NumPy/JAX
cross-backend agreement (§18) is the numerical witness that no double-correction
occurs in either backend.

## 17. JAX objective reproduction

**NOT REACHED.** Armed gate G-19: JAX negLL at the stored region-live theta
(`trial` column) within **1e-4** of **19053.46553160094** (and < 1e-2 of the 4-dp
anchor). A materially better objective is equally a stop (D-2). No optimizer exists in
the runner (`scipy.optimize` is on the prohibited-module list; nothing imports it).

## 18. NumPy/JAX agreement

**NOT REACHED.** Armed gate G-19: `|negLL_jax − negLL_numpy| ≤ 1e-6` via
`compute_index(spec, (sm, sf, None), θ, ruro=True, backend="numpy")` against the jitted
`build_jax_singles_ll` sum — the checkpoint's own §18 anchor used the NumPy backend and
printed 19053.465532, so both backends are expected to land on the target.

## 19. Resolved cluster count

**NOT RESOLVED** (Phase 2 not reached). D-6 armed logic: T3 expected count
auto-resolves as the unique nonmissing `idorighh` count measured in the frozen sample,
gated on mapping↔stem consistency, one cluster per household, range [1, 1,555], no
missing ids; persisted in `dry_run_report.json` and the manifest; the pooled default
9,657 is never used. Checkpoint §16 evidence anticipates **1,555** ("clusters: 1555").

## 20. Hashes and provenance

**EXECUTED.** `provenance.json` (partial, stop-time) records: all 17 verified input
hashes of §3–§4 (spec, warm start, raw txt, gsur lookup, both stored thetas, 8 pricing
chunks, 3 comparison frames, adapter mnlmeta); binding documents; lineage pointers
(walkthrough cell `7c42e9bd`; `propagate_regionlive.py` missing-from-disk note —
superseded by this runner); targets (19053.4655 / 19053.46553160094; region-dead
19071.6562 as context only). `rebuild_manifest.json` self-hashes the config
(`68d152e7…`) and the runner script (`be11294b…`), and records git heads —
MNL `d034574` (working tree carrying only the new untracked `scripts/p2a/` +
`region_live_v1/` paths), dclaborsupply-monorepo `2df94bc` (clean) — plus the
environment (Python 3.12.2, numpy 2.3.5, pandas 2.3.3; repo venv with jax 0.10.1).

## 21. Stop-condition status

| Stop | Status |
|---|---|
| **S-1 (G-0)** | **TRIGGERED** — geometry artifact missing (both files absent); all other 20 G-0 items PASS |
| S-0 prohibited operation | not triggered — guards armed and verified at startup (no EUROMOD / draw / optimizer module loaded; write-guard active) |
| S-8 mid-run hash change | not triggered |
| S-9 (G-19 theta evaluation) | not reached |
| G-18 data-wiring gates | not reached (armed) |

Manifest: `status = STOPPED`, never a PASS. No auto-retry, no threshold loosening, no
substitution was attempted.

## 22. Git diff summary

`git status --short` (MNL) after the run — **no tracked file modified**, three new
untracked paths only:

```
?? docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v1.md
?? outputs/p2a_singles2016/region_live_v1/
?? scripts/p2a/
```

`git diff --stat`: empty (no tracked-file changes). `dclaborsupply-monorepo`
`git status --short`: **clean** (both notebooks untouched — v1 frozen checkpoint and
v2 unmodified). Job_Market_paper: untouched. Nothing was committed (operator reviews
this diff first).

## 23. Whether Phase 3 may run

**NO.** Three independent blocks, in order:

1. Phases 1–2 have not passed — the dry-run stopped at G-0 (S-1); there is no frozen
   stem, no G-18 evidence, no G-19 objective reproduction.
2. The G-0 geometry artifact does not exist, and producing it is a notebook-
   stabilization deliverable outside this runner's authority (D-1 v2).
3. Phases 3–8 are manager-gated on review of a **passing** Phase 1–2 dry-run evidence
   set (plan v2 §24 step 4); the runner itself refuses `--phase > 2`.

## 24. Immediate next action

**Notebook stabilization, then re-run this exact dry-run command.** Concretely, in
`fr_singles_pipeline_v2.ipynb` (the active development notebook — an operator action;
this executor may not run or modify notebooks):

1. Add the geometry-freeze cell after §9: persist the in-memory `draws_p2a` frame —
   the **full** column set (162 columns), covering the config's
   `frozen_inputs.draws_geometry.required_columns` and everything `assemble_singles`
   consumes — to `outputs/p2a_singles2016/region_live_v1/inputs/
   fr_p2a_draws_geometry__singles.parquet`, and write
   `fr_p2a_draws_geometry__meta.json` with at least `{seed: 2026, draw_design,
   sha256 (of the parquet), n_rows: 157055, columns}`.
2. Execute the notebook far enough to produce that freeze (draws only — pricing stays
   on the cached chunks; `RUN_ESTIMATION` may remain False; the estimation/inference/
   welfare stages are not needed for G-0).
3. Re-run: `python scripts/p2a/run_p2a_regionlive_rebuild.py --config
   scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml --phase 2 --out
   outputs/p2a_singles2016/region_live_v1 --dry-run` — G-0 then admits Phase 1, and
   the full G-18 + G-19 battery runs to a PASS / PASS WITH WARNINGS / STOPPED verdict
   for manager review.

**FINAL VERDICT: STOPPED** (pre-registered S-1 at G-0; partial evidence persisted;
nothing committed).
