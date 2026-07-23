# FR P2a Region-Live — Plan Reconciliation Report — v1

Date: 2026-07-23. Documentation-only design-control task: reconcile the production rebuild plan
with the ratified manager decisions and the advanced notebook state. No scientific code written or
modified; no notebook, EUROMOD, draw generation, estimation, inference, post-estimation, or welfare
run; no data, theta, YAML, result JSON, parquet, or existing output modified. The certified pooled
baseline (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987) is unchanged; P2a region-live
remains provisional.

## 1. Reconciliation verdict

**READY FOR NOTEBOOK STABILIZATION.**

The frozen upstream priced-draw inputs required by binding D-1 are identified unambiguously (§5)
and the EUROMOD-outcome half is available on disk and git-tracked — so the plan is **not BLOCKED**.
However, the draw-geometry half (`draws_p2a`) was never persisted by the checkpoint notebook; it
must be frozen during notebook stabilization (the sanctioned next step) before Phase 1 may start.
Plan v2 encodes this as gate G-0. If stabilization cannot produce the geometry freeze, Phase 1 is
BLOCKED at G-0 and the evidence returns to the manager.

## 2. Files inspected

Read in full for this task:

- `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v1.md` (786 lines, incl.
  the 2026-07-23 D-3/D-4/R-4 amendments and the now-superseded "full er_b rebuild incl. EUROMOD"
  §8)
- `MNL/docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v1.md` (ratified D-1..D-8)
- `Job_Market_paper/docs/JMP_cross_repo_documentation_repair_report_v1.md` (§12 inconsistency)
- `MNL/dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb` (57 cells, executed
  `ec=1..34`, mtime 2026-07-22 15:14; full cell-by-cell read of §§9–12b, 13–18)
- `MNL/dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md`

Disk evidence verified: `MNL/fr_singles_pricing_p2a/` (8 chunks, git-tracked, schema and household
coverage checked); full-disk search for any frozen draw-geometry artifact (none found);
`theta_p2a_singles_2016_v1.csv` column semantics (`param, certified, trial, moved` — the
region-live estimate is the `trial` column, e.g. `beta_E = −2.897390227013939`, matching the
estimation JSON).

## 3. Contradictions found

1. **Plan v1 §8 vs binding D-1 (the headline contradiction).** The 2026-07-23 amendment of v1 §8
   required a *full* `er_b` rebuild **including re-running seeded draw generation and EUROMOD
   pricing** ("This supersedes the earlier 'no EUROMOD run / verification-only' stance"). The
   binding clarification reverses this: Phase 1 must **not** rerun EUROMOD or regenerate draws.
   Corrected in plan v2 §8.
2. **Plan v1 §1/§24/§27 vs ratified state.** v1's verdict ("READY AFTER MANAGER DECISIONS"),
   sequence step 1 ("Manager ratifies §25"), and §27 ("Submit §25 to the manager for ratification")
   predate ratification. Corrected: v2 verdict READY FOR NOTEBOOK STABILIZATION; next action =
   stabilization + Phase 1–2 dry-run.
3. **Placeholders after ratification.** v1 §26 contains `⟨INSERT RATIFIED VALUES⟩`; v1 §19 marks
   G-1/G-3/G-6/G-7/G-10/G-12/G-15/G-17 "MAR"/recommended; v1 §25 D-5/D-6/D-7 still read
   *Recommended / ratify / Decide*. All removed in v2 (§19, §25, §26) — every value final.
4. **Notebook-state staleness.** The promotion-readiness audit (and v1 §2's carried claim) says
   `fr_singles_pipeline_v1.ipynb` "reproduces only region-dead 19071.6562". The checkpoint is now a
   full region-live pipeline (fit 19053.4655, iters=540, converged; self-verified cold-reload
   anchor 19053.465532). v2 §2–§3 record this; the audit doc is retained as history (not edited
   here).
5. **Checkpoint notebook overwrites doc-repaired artifacts.** Its §15/§18 cells rewrite
   `P2A_MASTER_RECORD.md`, `p2a_fit_provenance.json`, `theta_p2a_singles_2016_v1.csv`, and the root
   engine-ready parquet — which is how the 2026-07-22 doc-repaired master record was regenerated
   without its two-vintage banner. Stabilization instruction in v2 (§3, §24): `v2` notebook must
   redirect writes into `region_live_v1/`.
6. **Repair-report §12 self-contradiction.** §12 still listed the methods manual and mirrored
   README as "flagged, not edited," contradicting §§3–4/10 of the same document. Corrected (§13
   below).
7. **Priced-cache content vs v1's assumption.** v1 treated "draws/pricing" as one regenerable
   stage; in fact the cache holds **outcomes only** (`ils_dispy`, `bsa00_s` per household×draw) and
   the geometry/proposal densities exist only in notebook memory — the decisive gap driving the
   G-0 stabilization deliverable.

## 4. D-1 final interpretation

The production runner independently reconstructs the notebook's in-memory `er_b`, **starting from
frozen already-priced draw artifacts** — never from EUROMOD, never from fresh draws, never by
copying an engine-ready parquet:

frozen already-priced P2a draw artifacts → `assemble_singles` → independent
`drgn1/drgur/drgmd/drgru/gsur` reconstruction (raw txt + gsur lookup) → B-pool band overwrite →
`er_b` → freeze under `region_live_v1/`.

Existing engine-ready frames (root bpool 07-22, root `_v2` 07-13, adapter stem 07-13) are
**comparison artifacts only**: the rebuilt `er_b` must equal them on all substantive values after
stable row sorting, common-column ordering, and dtype normalization (disagreement → S-1). "Phase 1
reruns deterministic assembly, region revival and band logic" — nothing stochastic, nothing priced.
End-to-end draw-generation + EUROMOD-pricing reproducibility is a **later separate gate**, outside
this rebuild.

## 5. Frozen upstream priced-draw inputs

Identified by name from the executed checkpoint (§§10–12b):

1. **EUROMOD pricing cache — available, git-tracked.**
   `MNL/fr_singles_pricing_p2a/priced_{00000,00200,00400,00600,00800,01000,01200,01400}.parquet`
   — 8 chunks (CHUNK=200 over 1,555 sorted single households), 225,836 rows, all 1,555
   `source_idhh` covered; columns `idhh, idperson, source_idhh, source_idorighh, source_idperson,
   ruro_decider, dgn, draw, ils_dispy, bsa00_s`. This is precisely what notebook §10 (cell
   `ec=22`) reads back in resumable/`SKIP_PRICING` mode — the already-computed EUROMOD outcomes.
2. **Draw-geometry + proposal densities — identified but NOT frozen (G-0 blocker).**
   `draws_p2a`/`feat2`/`alt2`: per-(idhh, draw) hours, wage, loc4, working, B-pool band flags,
   `log_prior` (+ `log_q` components), and carry features (`age_norm`, `age_norm2`, `n_children`,
   source ids). Built in-memory by §9 (seed 2026, mirroring `build_bpool_singles.py`) and consumed
   by §12; **no persisted copy exists anywhere on disk** (full search: only pooled-P3a,
   engine-ready, and welfare parquets — all excluded by D-1). Stabilization must freeze it as
   `region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet` (+ meta with seed/design/hash).

Because item 1 is unambiguous and available, the verdict is not BLOCKED; because item 2 is not yet
frozen, Phase 1 is gated on stabilization (G-0). No engine-ready parquet may be substituted for
either item.

## 6. Manager decisions carried forward

D-2 through D-8 carried into decisions v2 **exactly as ratified in v1** (objective/reload
tolerances incl. materially-better-is-a-stop; rank criteria with the R-4 Schur-complement hard test
and warning-only R-3; symmetry 1e-8·max|H| and the three-tier condition scheme vs pooled 1.295e6;
T1 1e-8/1e-8, bound ε 1e-5, gradient gate 1e-2 on 35 non-bound free, optimizer success; T3
auto-resolved cluster count 1–1,555 never 9,657; local-diagnostics-only scope with mandatory
synthetic recovery before promotion; package upstreaming deferred, no monorepo changes). D-1 is
**replaced** by the binding clarification (§4 above). Decisions v2 adds the status header: v2
canonical; v1 historical; pooled baseline unchanged; P2a provisional.

## 7. Plan sections repaired

Plan v2 was created from v1 with corrections concentrated in §§8, 9, 10, 20, 21, 24, 25, 26, 27
(plus the header, §1 verdict, and §§2–4 evidence/roles):

- **§8** rewritten to the binding boundary: frozen inputs named; no EUROMOD; no draw regeneration;
  deterministic assembly + revival + band logic only; existing frames reconciliation-only;
  idempotence secondary.
- **§9** runner hard-codes refusals (no EUROMOD import, no draw path, no notebook I/O, writes
  jailed to `region_live_v1/`); `--dry-run` = Phases 1–2.
- **§10** adds `inputs/` (frozen geometry) and `dry_run_report.json`; Phases 3–8 outputs marked
  manager-gated.
- **§19** all gates ratified (no MAR/recommended); adds **G-0** (frozen-inputs gate) and **G-19**
  (Phase-2 theta evaluation).
- **§20** adds **S-0** (prohibited-operation stop) and **S-9** (dry-run theta failure); S-5
  excludes R-3 warnings.
- **§21** adds the stabilization deliverables (notebook v2 + geometry freeze) and re-scopes the
  output list by phase.
- **§22** adds the pricing cache and both notebooks to the do-not-modify list.
- **§24** sequence now: stabilization → scaffolding → Phase 1 → Phase 2 (manager review point) →
  gated Phases 3–8.
- **§25** points to decisions v2; summary of record with all values final.
- **§26** implementation prompt covers **Phases 1–2 only**, with the explicit prohibition list and
  the Phase-2 stored-theta evaluation.
- **§27** immediate next action: notebook stabilization, then the Phase 1–2 dry-run (not manager
  ratification).

## 8. Notebook integration

- `fr_singles_pipeline_v1.ipynb` — **frozen region-live notebook checkpoint**: executed end-to-end
  (raw read → funnel → features/gsur → certified B-pool draws → chunked EUROMOD pricing (cached) →
  take-up → assemble → §12b revival → bpool bands → fit 19053.4655 (540 iters, converged) →
  freeze → cluster SEs → master record + self-verified cold-reload anchor → welfare check). It
  defines `er_b` and the anchor; it is never modified or re-run by this rebuild.
- `fr_singles_pipeline_v2.ipynb` — **active development notebook, once created** (stabilization
  step): redirects writes into `region_live_v1/`, freezes the draw geometry (G-0 deliverable),
  re-verifies the anchor.
- `MNL/scripts/p2a/` — **production-validation path**: consumes frozen inputs only; asserts the
  S-0 refusals in code.

## 9. EUROMOD and draw-generation scope

**Excluded from this rebuild entirely.** Phase 1 performs no EUROMOD call (the pricing cache is
the frozen record of already-computed outcomes — the checkpoint's own `SKIP_PRICING` discipline)
and no draw generation or regeneration (geometry comes from the frozen artifact; the seeded
generator modules are not imported by the runner). End-to-end draw-generation and EUROMOD-pricing
reproducibility testing is a **later, separate, manager-authorized gate** — explicitly outside
this rebuild (D-1 v2).

## 10. Phase 1 scope

Deterministic assembly only, from frozen inputs (plan v2 §8): G-0 frozen-inputs verification →
raw-txt funnel + features + gsur merge (the independent five-column reconstruction) → take-up
traits (seed 20162016) + income mask → `assemble_singles` → §12b-equivalent revival → B-pool band
overwrite → `er_b` → freeze under `region_live_v1/` → three-frame reconciliation + G-18 wiring
gates → `region_map_p2a_singles2016.parquet`, `data_wiring_validation.json`, provenance hashes.
Stops: S-0/S-1/S-8. No optimizer, no EUROMOD, no draws, no welfare, no post-estimation, no
notebook modification, no writes outside `region_live_v1/`.

## 11. Phase 2 scope

Dry-run verification, **no optimizer**: package load of the frozen stem; loader liveness; 47-name
binding + warm-start equality (`certified` column); proposal-correction sanity; **evaluation of the
existing stored region-live theta** (`trial` column of `theta_p2a_singles_2016_v1.csv` ≡ `_v2.csv`):
JAX objective within **1e-4** of **19053.46553160094**, NumPy/JAX backend agreement within
**1e-6** (gate G-19; failure → S-9); automatic T3 cluster-count resolution per D-6, persisted in
`dry_run_report.json`. The dry-run ends here; the manager reviews before anything further.

## 12. Later phases retained

Phases 3–8 (estimation; gradient/convergence; Hessian/rank + region×urbanisation test with
R-1/R-2/R-4 hard and R-3 warning-only; chunked cluster-robust inference T1–T5; post-estimation
regeneration labelled PROVISIONAL; fresh-process cold reload; strict-verdict package ending
"awaiting manager strict verdict") are **preserved by design in plan v2 §§11–18** with all ratified
thresholds — but **manager-gated and not part of the next execution**. They run only after the
manager reviews the Phase 1–2 dry-run evidence.

## 13. Documentation-report correction

`Job_Market_paper/docs/JMP_cross_repo_documentation_repair_report_v1.md` §12 was corrected: the
stale bullet claiming `RURO_METHODS_AND_PIPELINE_MANUAL_v1.md` and `docs/mirrored/root/README.md`
were "flagged, not edited" is struck through and superseded by a note that the 2026-07-23 follow-up
repaired both (consistent with §§3–4 and §10 of the same report). The verdict remains **PASSED WITH
WARNINGS**, and the only remaining warning is the deliberately **unresolved P2a theta pointer**.

## 14. Remaining blockers

1. **G-0 — frozen draw-geometry artifact does not yet exist.** The single hard blocker for
   Phase 1; deliverable of notebook stabilization (`fr_singles_pipeline_v2.ipynb`). If it cannot be
   produced, Phase 1 is BLOCKED.
2. **Theta pointer UNRESOLVED** (`p2a_fit_provenance.json`) — deliberate; repair is manager-gated
   after the strict verdict. Not a Phase 1–2 blocker.
3. **Stabilization write-redirect** — until notebook v2 redirects its freeze cells, any notebook
   re-run would again clobber the doc-repaired root artifacts (master record, provenance, theta
   v1, root parquet). Guarded by making redirection a stabilization requirement (plan v2 §24 step
   1); not a blocker for the production runner itself (which never opens those paths).
4. Open manager-queue items A3 (pointer/master-record doc repair) and A4 (missing
   `propagate_regionlive.py` note) — tracked, non-blocking (Phase 1 supersedes the missing script's
   logic reproducibly).

## 15. Canonical files after reconciliation

| File | Status |
|---|---|
| `MNL/docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v2.md` | **Canonical decisions** (implementation must trace here) |
| `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v2.md` | **Canonical plan** (Phases 1–2 executable after stabilization; 3–8 manager-gated) |
| `MNL/docs/France_case/P2a/FR_P2a_region_live_manager_decisions_v1.md` | Historical (pre-notebook-integration decision record) |
| `MNL/docs/France_case/P2a/FR_P2a_region_live_production_rebuild_plan_v1.md` | Historical (superseded by v2; retains the 2026-07-23 amendment trail) |
| `dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v1.ipynb` | Frozen region-live notebook checkpoint (never modified) |
| `fr_singles_pipeline_v2.ipynb` | Active development notebook, once created (stabilization) |
| `MNL/fr_singles_pricing_p2a/priced_*.parquet` | Frozen priced-draw input (read-only) |
| `dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md` | Historical audit (its "pipeline notebook is region-dead-only" claim is superseded by the checkpoint) |
| This report | Reconciliation record |

Certified pooled baseline artifacts: unchanged and canonical for the JMP baseline (out of P2a
scope). P2a region-live artifacts under the mixed-vintage root: labelled history.

## 16. Immediate next action

**Notebook stabilization, then the Phase 1–2 dry-run.** (1) Create `fr_singles_pipeline_v2.ipynb`
from the frozen checkpoint; redirect all writes into `region_live_v1/`; add the geometry-freeze
cell producing `inputs/fr_p2a_draws_geometry__singles.parquet` (+ meta, hashed); re-verify the
in-notebook anchor. (2) Execute plan v2 §26 (Phases 1–2 only) and put
`data_wiring_validation.json` + `dry_run_report.json` before the manager. Phases 3–8 remain
manager-gated; no promotion; no welfare; P2a region-live remains provisional.

---

**FINAL VERDICT: READY FOR NOTEBOOK STABILIZATION**
