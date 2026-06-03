# RURO Welfare — Stage Two, Increment Two-N: full production rebuild to staging + full-scale validation

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-N only — full production rebuild under the patched
chunk worker, written to STAGING, gated on full-scale validation.
**Status:** complete. **GATE OUTCOME: STOP. Full-scale HEADLINE PARITY FAILS for BOTH
singles and couples.** Per the increment's stop rule, **no swap is recommended and none was
performed.** Readiness: `singles_ready=false`, `couples_ready=false`,
`overall_ready_for_separate_swap_authorisation=false`.

The rebuild itself completed cleanly (21/21 chunks, exact row counts, internally coherent,
deterministic), and the component-staleness bug is fixed. **But the rebuilt headline
`ils_ben` / `ils_dispy` do NOT match the existing stored production** on the means-tested
benefit (income and contributions match exactly). Because the rebuild is **deterministic**
(a re-run reproduces it to 0.0) and **internally coherent**, the mismatch means the **stored
production headline is not reproducible by a faithful current-input rebuild** — and swapping
staging into production would therefore **change the certified estimator's consumption input
(`ils_dispy_real`)**. That is exactly what the headline-invariance gate is there to prevent.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; no `V_i^dir` is
> computed; no redrawn welfare node is priced; nothing is re-estimated; and no production
> parquet was swapped, overwritten, moved, or deleted.** All rebuild output went to a
> staging directory. Not committed automatically.

---

## Task 1 — rebuild to staging (COMPLETE)

The patched `scripts/bpool/run_bpool_euromod_chunk.py` was run via `--staging-dir` for every
production chunk at exact production granularity (same year/mode cells, chunk IDs, draw
bands, system pairing, CPI). Each chunk ran as its own subprocess; output went ONLY to
`…/EUROMOD-STORAGE/new_data/staging_twoN/`.

- **Staging dir:** `C:\Users\hisham\MNL\EUROMOD-STORAGE\new_data\staging_twoN` (5.54 GB).
- **Manifest:** singles 1 chunk/year `[0,101)`; couples 6 chunks/year (draw_joint bands of
  150 over `[0,900)`). **21 chunk runs, all OK; 0 failed; 0 timed out.**
- **Row counts vs production:** **every chunk matches production exactly** (e.g. 2017
  couples c0 = 1,139,446 rows; 2015 couples c0 = 1,276,554; full per-chunk table in the
  Task-1 provenance JSON).
- **Wall time:** 7,810 s ≈ **2.17 h**. Each ~1.14M-row couples-chunk EUROMOD call completed
  in ~6-7 min without OOM/abort — full-scale couples feasibility CONFIRMED.
- The patched worker writes **all 266 simulated output columns per draw** (586-col output,
  vs ~566 before).

---

## Task 2 — full-scale headline parity gate (FAIL → STOP)

Rebuilt staging headline vs the EXISTING stored production priced files, per year × mode, on
ALL rows and on DECIDER rows separately. Columns: `ils_dispy`, `ils_origy`, `ils_ben`,
`ils_tax`, `ils_sicdy`, `ils_dispy_real`. PASS requires decider-row machine-tolerance parity.

| cell | decider rows | `ils_origy` bad | `ils_sicdy` bad | **`ils_ben` bad (max abs)** | **`ils_dispy` bad** | decider PASS? |
|---|---|---|---|---|---|---|
| 2015 singles | 168,569 | 0 | 0 | 3,519 (€359) | 3,519 | **FAIL** |
| 2015 couples | 4,623,932 | 0 | 0 | **205,854 (€1,161)** | 205,399 | **FAIL** |
| 2016 singles | 169,276 | 0 | 0 | 3,460 (€186) | 3,460 | **FAIL** |
| 2016 couples | 4,643,754 | 0 | 0 | **215,643 (€905)** | 215,131 | **FAIL** |
| 2017 singles | 167,862 | 0 | 0 | 7,297 (€360) | 7,297 | **FAIL** |
| 2017 couples | 4,135,590 | 0 | 0 | **348,216 (€980)** | 348,216 | **FAIL** |

**Every cell FAILS, singles and couples.** The divergence is **exclusively on the
means-tested benefit** `ils_ben` (and the benefit-driven `ils_dispy` / `ils_dispy_real`):
`ils_origy` and `ils_sicdy` (origin income and social contributions) reproduce the stored
production to **machine zero on every row**. Prevalence on decider rows ≈ 2-4 % (singles)
and ≈ 4.5-8.4 % (couples) — the benefit-recipient share, consistent with Two-G/H/I/K/L.

Per the increment's rule — *"If couples headline parity fails at full scale, STOP and report.
Do not proceed to any swap recommendation."* — this increment **STOPS** at Task 2.

### Root cause: the rebuild is correct; the STORED production headline is the unreproducible artifact
Two checks pin this down:

1. **The rebuild is DETERMINISTIC.** Re-running 2017 singles c0 a second time reproduces the
   staging `ils_ben` / `ils_dispy` to **max abs 0.0**. So the mismatch vs stored production is
   **not** my rebuild varying run-to-run — it is a stable, reproducible difference.
2. **The rebuild is INTERNALLY COHERENT** (Task 3 below): `ils_ben = ils_pen + ils_benmt +
   ils_bennt` and the `ils_dispy` identity hold to machine tolerance, and the components are
   draw-specific.

Combined with Two-L (the stored production `ils_ben` was not reproducible by any faithful
reprice) and Two-M Gate A2 (the patched worker's means-tested headline did not reproduce
stored even at bounded scale), the conclusion is: **the existing stored production headline
`ils_ben` / `ils_dispy` were not produced by a faithful, current-input EUROMOD run at this
granularity.** They differ from what the patched worker deterministically produces from the
*current* precompute inputs at the *exact production chunk definitions*. The most likely
explanation (not proven here, stated as candidate): the production priced files were assembled
from a **different / earlier precompute or build state** than the precompute-long files now on
disk, so the means-tested benefit — which is population/draw-dependent (Two-L) — differs.

**Critical consequence (this is why STOP is mandatory):** the certified estimate is fit on the
STORED `ils_dispy_real` / `c_norm`. The rebuilt `ils_dispy` differs from stored on the
benefit-recipient rows. Therefore **swapping staging into production WOULD change the
estimator's consumption input** on those rows — exactly the failure mode the headline-invariance
gate exists to catch. The Two-M Gate A1 result (patch does not move the headline *on the same
sim*) still holds; what fails here is reproducing the *stored production sim itself*.

### Provenance investigation (follow-up): three reviewer hypotheses, all tested
A targeted build-provenance investigation was run (read-only) to test three candidate causes
raised in review. **All three are rejected**, and the residual cause is narrowed to an
unreproducible stored-target.

1. **Year / policy-system effect ("is it the non-2016 systems?").** *Rejected as a clean
   split.* The `ils_ben` failure rate does NOT favour 2016 (FR_2015): it is 2.0 %/2.0 %/4.3 %
   (singles) and 4.5 %/4.6 %/8.4 % (couples) for 2015/2016/2017. 2017 (FR_2016, the latest
   system) is the worst, 2015 ≈ 2016 — a rising-by-year gradient, not a single-system artefact.

2. **Uprating / CPI ("wages are real for estimation; rewind the uprate before EUROMOD").**
   *Rejected at the input level.* (a) The rebuilt/stored `ils_ben` ratio on failing rows is NOT
   constant (median 0.71, std 0.28, range 0–0.92) — a scalar uprate/deflation factor would give
   a tight constant ratio (~0.9886), so the gap is **structural, not a scaling**. (b) The
   EUROMOD earnings inputs fed by the rebuild are **identical** to production: `yem`, `yem00`,
   `yivwg`, `lhw`, `bch00` match the stored priced values exactly, and the current precompute-long
   equals its own `*.pre_wage_deflation.bak` to **ratio 1.00000 over 3.73 M rows** — the wage
   deflation only ever touched the *estimator-facing* wage columns (build-confirmed: *"keep
   EUROMOD earnings inputs nominal upstream… preventing double deflation"*), never the EUROMOD
   inputs. So a pre-EUROMOD uprate rewind would move inputs that **already match** production and
   would not close the gap.

3. **Couples roster completeness ("all household members must be present").** *Rejected.* The
   failing couples node (HH 300001801900) has its **complete 5-member roster** (2 adults + 3
   children) present in the EUROMOD input, matching the full household across all draws. No
   members are missing.

**What the provenance check additionally established.** The `*.pre_wage_deflation.bak` backups
of precompute and priced are **byte-identical to the current files** (0 differing columns;
priced `ils_ben`/`ils_dispy`/`ils_dispy_real` max diff 0.0) — so the current on-disk inputs and
the stored priced ARE the production artefacts (no silent input drift). The two pricing scripts
(`run_bpool_euromod.py` single-pass and `run_bpool_euromod_chunk.py` chunk worker) use
**byte-identical `_stamp_draw_ids` logic** and the **same 6-band `[0,150)…[750,900)` chunking**,
so neither stamping nor chunk granularity explains the difference. The stored priced `idperson`
column is the **un-stamped original** (2 distinct ids across 900 draws), i.e. IDs were restored
post-pricing — consistent across both runners.

**Narrowed conclusion.** Every *reproducible* cause is excluded. The stored production
`ils_ben`/`ils_dispy` are **not reproducible from the current inputs by any faithful EUROMOD run**
(isolated, bounded, population, full-chunk, or single-pass) — consistent with Two-I, which already
found the same stored couples value (e.g. 432.83) unreproducible. The means-tested divergence
therefore originates **inside EUROMOD's tax-unit / assessment-unit resolution under the original
production execution**, whose exact state (EUROMOD model version, dataset, or a transient run
condition) the current repo + data do not reconstruct. This is a **stored-target reproducibility
gap at the EUROMOD-execution level**, not an input, uprating, roster, stamping, or chunking bug.

---

## Task 3 — full-scale component-coherence gate (PASS on rebuilt data)

On the rebuilt staging data (decider rows), per year × mode:

| cell | `ils_ben` identity violations | `ils_dispy` identity violations | `ils_benmt` varies across draws | rows where `ils_benmt` ≠ stale stored |
|---|---|---|---|---|
| 2015 singles | 0 | 0 | 97.0 % | 99,427 / 243,713 |
| 2015 couples | 0 | 0 | 98.3 % | 1,737,498 / 7,617,054 |
| 2016 singles | 0 | 0 | 96.8 % | 99,972 / 241,895 |
| 2016 couples | 0 | 0 | 98.3 % | 1,761,433 / 7,638,678 |
| 2017 singles | 0 | 0 | 94.4 % | 97,092 / 238,764 |
| 2017 couples | 0 | 0 | 96.0 % | 1,036,644 / 6,798,946 |

The Two-M / Two-L staleness bug is **fixed on the rebuilt data**: `ils_ben = ils_pen +
ils_benmt + ils_bennt` and `ils_dispy = ils_origy − ils_tax − ils_sicdy + ils_ben` hold with
**0 violations** everywhere (the stored data had 58-59 % singles / 32-40 % couples), the
simulated components now **vary across draws** (94-98 % of HH), and 1-1.7 M rows per couples
cell carry a corrected draw-specific `ils_benmt` differing from the old stale carry-over. So
the rebuild's *internals* are correct and coherent — it is the *match to stored production
headline* that fails.

---

## Task 4 — readiness (NOT READY; no swap)

| condition | result |
|---|---|
| Task 1 complete chunk coverage | ✓ (21/21, exact row counts) |
| Task 2 headline parity PASS (singles) | ✗ FAIL |
| Task 2 headline parity PASS (couples) | ✗ FAIL |
| Task 3 component coherence PASS | ✓ |

- **`singles_ready`: FALSE** — headline parity fails.
- **`couples_ready`: FALSE** — headline parity fails (couples reported explicitly: up to
  €1,161 on `ils_ben`, ~4.5-8.4 % of decider rows).
- **`overall_ready_for_separate_swap_authorisation`: FALSE.** **No swap was performed.**

### What a later (separately authorised) increment must resolve first
The blocker is **not** the write-back patch (the patch is correct and fixes the components).
The blocker is that **the stored production headline `ils_ben` / `ils_dispy` is not
reproducible from the current precompute inputs at the production chunk definitions** — so the
estimator's stored consumption input cannot be matched by a faithful rebuild. Before any swap:

1. Determine whether the production priced files were built from a **different precompute /
   build vintage** than the on-disk precompute-long (compare a provenance/build hash or rebuild
   the precompute and re-diff). If so, identify the correct input vintage.
2. Decide the **policy question** this forces: the certified estimate is fit on a stored
   `ils_dispy_real` that a faithful current rebuild does **not** reproduce on benefit-recipient
   rows. Either (a) the stored headline is itself defective (and a corrected rebuild + a
   controlled re-estimation is warranted), or (b) the current precompute inputs differ from
   those used in production (and the rebuild must use the production-vintage inputs). This is a
   **build-provenance / re-estimation** decision, explicitly out of scope here.

Until that is resolved, **the staging rebuild must not be swapped into production**, and the
component-staleness fix cannot be shipped via a naive swap (it would move the estimator input).

---

## Files

- **Rebuild orchestrator:** `scripts/welfare/run_stage2_full_rebuild_staging.py`
  (drives the patched worker to staging; per-chunk status/rows/wall).
- **Validation harness:** `scripts/welfare/run_stage2_full_rebuild_validation.py`
  (Tasks 2-4; headline parity all + decider, coherence, no-stale-carryover, readiness).
- **Worker patch (Two-N):** `scripts/bpool/run_bpool_euromod_chunk.py` gained an optional
  `--staging-dir` (default = unchanged production behaviour) so the rebuild never touches
  production.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_full_rebuild_staging.json` (Task 1
  manifest + per-chunk results), `outputs/welfare/stage1_w3/stage2_full_rebuild_validation.json`
  (Tasks 2-4 gates + readiness).
- **Staging directory:** `…/EUROMOD-STORAGE/new_data/staging_twoN/` (20 chunk parquets, 5.54 GB)
  — NOT a production path, NOT committed.

## Explicit scope statement

No W^3 finding; no measure beyond W^3; no `V_i^dir`; no redrawn pricing; nothing re-estimated;
the full rebuild ran to STAGING only; and **no production parquet was swapped, overwritten,
moved, or deleted** (all production priced files are unchanged, 228+ h old). The swap of
staging into production is a separate authorisation and was NOT performed; this increment STOPS
at the failed headline-parity gate.
