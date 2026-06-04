# RURO Welfare — Stage Four, Increment Four-B: population-faithful existing-node parity gate

**Date:** 2026-06-04
**Increment:** STAGE FOUR, INCREMENT FOUR-B only — population-faithful existing-node parity gate
against the STAGED reproducible welfare-pricing reference (the population-scale Gate-0 analogue
that licenses redrawn-node welfare pricing).
**Status:** complete. **GATE PASSES: all 6 year × mode cells reproduce the staged reference to
machine zero** (max abs = 0.0 on all 6 headline columns AND all 133–141 simulated components),
each repriced within the **full chunk population batch** (HH count in batch = full staged-chunk
HH count). **Welfare pricing declared POPULATION-FAITHFUL and READY** for the singles `V_i^dir`
gate-and-smoke (a separate authorisation).

> **No redrawn-node pricing; no `V_i^dir`; no `W^3` promotion; no re-estimation; no production
> parquet swapped/overwritten/moved/deleted; no promotion of the staged baseline to canonical;
> no production overwrite.** The reprice output went to a scratch dir only. Nothing beyond
> `W^3`. Not committed automatically.

---

## Method — what "population-faithful" means here, and a corrected design

Two-L established that French means-tested benefits are **population-dependent**: a node
reproduces its stored `ils_ben` only when priced **within a representative population batch**;
isolated or bounded per-node repricing is unfaithful. Four-B operationalises this by repricing
**one complete production chunk** per cell through the patched all-component worker, at the
**exact production chunk band the staged reference was itself priced in**, and comparing to the
staged stored chunk in full.

**Population-faithful unit = the production chunk batch.** The worker's push-down filter is on
the draw column only (no household filter), so a full chunk band contains the **entire
representative household population** across the chunk's draw range — the same EUROMOD batch the
staged chunk was built with (Two-N). Cells:

| mode | chunk | band | EUROMOD batch |
|---|---|---|---|
| singles | c0 | `[0,101)` | every singles HH × full draw range |
| couples | c0 | `[0,150)` | every couples HH × the draw_joint band |

**Corrected design (honest record).** A first attempt repriced a *narrow* draw sub-band
(`singles [0,3)`, `couples [0,1)`) on the reasoning that all households are present at those
draws. **That failed** on 2015 singles — and the failure was the textbook Two-L signature:
`ils_origy`/`ils_tax`/`ils_sicdy` reproduced to machine zero (income/contributions are
batch-independent), but the **means-tested** `ils_ben` (`ils_benmt`, `bsa00_s`) diverged on 615
/ 7,239 rows (max €955). The lesson is exactly Two-L's: **a draw sub-slice, even with all
households present, is a DIFFERENT EUROMOD batch** — the means test depends on the *full chunk
batch composition*, not merely on which households are present. The gate was corrected to
reprice the **full production chunk band**, which is the genuine population batch, and it then
passes to machine zero (below). This is recorded as a method correction, not a result of the
staged reference.

**Exact paths used.** Staged reference: stem `fr_p3a_bpool_engine_ready_staged_threeB1`; staged
stored chunks in `…/EUROMOD-STORAGE/new_data/staging_twoN/`. Reprice output (scratch, never
production / never the staging reference):
`…/EUROMOD-STORAGE/new_data/scratch_four_b_parity/` (6 chunks, distinct id `c90`). Worker:
`scripts/bpool/run_bpool_euromod_chunk.py` (the Two-M all-component patch). Pinned EUROMOD
pairing / CPI / schema read from the build module per the `welfare.stage4` config.

---

## Tasks 1–2 — population-scale reprice + parity grid (PASS)

Each cell: reprice the full production chunk at population scale, compare to the staged stored
chunk by node key (singles `stacked_hh_uid`/`draw`/`idperson_true`; couples
`stacked_hh_uid`/`draw_joint`/`draw_male`/`draw_female`/`idperson_true`), on the 6 headline
columns + every shared `ils_*` / `*_s` component.

| cell | band | rows compared | HH (batch / full chunk) | pop-faithful | max abs headline | components / OK | PASS | wall |
|---|---|---|---|---|---|---|---|---|
| 2015 singles | `[0,101)` | 243,713 | 1,669 / 1,669 | ✓ | **0.0** | 139 / ✓ | **PASS** | 127 s |
| 2015 couples | `[0,150)` | 1,276,554 | 2,566 / 2,566 | ✓ | **0.0** | 139 / ✓ | **PASS** | 380 s |
| 2016 singles | `[0,101)` | 241,895 | 1,676 / 1,676 | ✓ | **0.0** | 141 / ✓ | **PASS** | 109 s |
| 2016 couples | `[0,150)` | 1,280,178 | 2,577 / 2,577 | ✓ | **0.0** | 141 / ✓ | **PASS** | 458 s |
| 2017 singles | `[0,101)` | 238,764 | 1,662 / 1,662 | ✓ | **0.0** | 133 / ✓ | **PASS** | 112 s |
| 2017 couples | `[0,150)` | 1,139,446 | 2,295 / 2,295 | ✓ | **0.0** | 133 / ✓ | **PASS** | 410 s |

**Every cell reprices the staged reference to machine zero** — on all six headline columns
(`ils_dispy`, `ils_origy`, `ils_ben`, `ils_tax`, `ils_sicdy`, `ils_dispy_real`) **and** every
simulated `ils_*` / `*_s` component (133–141 per cell), with the full chunk household population
present in the EUROMOD batch (`population_faithful = True` in all six). 0 rows above the 1e-6
tolerance anywhere.

This is the population-scale confirmation that the means-tested benefit — the component the
isolated/bounded instruments (Two-G/H/I/K) could not reproduce — **does** reproduce against the
staged reproducible reference when priced in its faithful population batch, exactly as Two-L
predicted and Three-A's full-chunk determinism gate established.

---

## Task 3 — readiness for direct-redraw welfare pricing

**`population_faithful_and_ready_for_singles_vdir_gate = TRUE`** (all 6 tested cells PASS, none
blocked, none stopped).

The passage of this gate is the precondition for redrawn-node welfare pricing. It licenses
**only** the singles `V_i^dir` gate-and-smoke, as a **separate authorisation** — this increment
prices no redrawn node and computes no `V_i^dir`.

**Coverage caveat (carried forward).** Four-B reprices **one full couples chunk per year** (c0,
band `[0,150)`) and the full singles chunk (c0, `[0,101)`), not all six couples chunks per year.
This is acceptable as a **gate / smoke** because Three-A already established full-chunk
determinism at production scale (a full chunk re-run reproduces staging to 0.0, validated on
2017 singles c0 + 2017 couples c5), and Four-B confirms it holds for the c0 band of every year.
**The `V_i^dir` runner must reuse the SAME full-chunk population-batch construction** — reprice
within the complete production chunk batch — and must **not** optimise back down to draw
sub-bands or isolated nodes (the corrected design above shows a sub-band is a different EUROMOD
batch and fails the means-tested benefit). This constraint is recorded in the carried-forward
constraints below and in the provenance JSON.

**Carried-forward constraints for the `V_i^dir` runner** (recorded in provenance):

- use the **staged reproducible welfare-pricing reference** (`fr_p3a_bpool_engine_ready_staged_threeB1`), **not** production canonical;
- price counterfactual nodes **within representative population batches** (the full-chunk batch, never isolated/sub-band);
- express counterfactual wages in the **draw's nominal frame before EUROMOD**;
- return disposable income to **real terms via `phi_y` after EUROMOD**;
- **no double deflation** (EUROMOD inputs nominal + system-year consistent; estimator-facing 2016-real deflation is separate);
- **no silent interpolation**;
- **reuse the full-chunk population-batch construction** (the complete production chunk band); do NOT optimise down to draw sub-bands or isolated nodes — a sub-band is a different EUROMOD batch and breaks means-tested-benefit parity (the Four-B method correction).

---

## Files

- **Driver:** `scripts/welfare/run_stage4b_population_parity_gate.py` (config-driven; reprices
  the full production chunk per cell at population scale, compares to the staged reference,
  emits the parity grid + readiness; STOP on first failing cell). Ruff-clean.
- **Report:** this document.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage4b_population_parity_gate.json`
  (per-cell parity grid, population-faithfulness evidence, readiness, carried constraints).
- **Reprice scratch (NOT production / NOT the staging reference; not committed):**
  `…/EUROMOD-STORAGE/new_data/scratch_four_b_parity/` (6 `c90` reprice chunks).
- **Unchanged:** staged reference engine-ready + `staging_twoN` chunks (21/21), certified
  production priced files (2025-05-26), certified + rebuilt theta CSVs.

## Explicit scope statement

No redrawn pricing; no `V_i^dir`; no `W^3` promotion; no re-estimation; no production swap; no
canonical promotion; no production overwrite; nothing beyond `W^3`. This increment runs the
population-faithful existing-node parity gate against the staged welfare-pricing reference and
reports readiness only; the singles `V_i^dir` gate-and-smoke remains a separate authorisation.
