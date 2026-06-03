# RURO Welfare — Stage Two, Increment Two-L: cross-track stored-target `ils_ben` residual diagnosis

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-L only — diagnose the cross-track stored-target
`ils_ben` residual (singles + couples). Read-only.
**Status:** complete. **VERDICT: B — IDENTIFIED BUT REQUIRES BUILD-LEVEL / FULL-CHUNK
REPRICING.** The "residual" resolves into **two distinct build-level facts**, both
identified:

1. **The isolated/bounded clean-reprice instrument is UNFAITHFUL for benefits.** Means-tested
   French benefits depend on **population context**; a failing node's stored `ils_ben`
   reproduces **exactly** once a representative population shares the EUROMOD batch
   (≥ ~20 households), but gives the wrong value in isolation. So the per-node "16–22 %
   residual" measured in Two-G/H/I/K is largely a **measurement artefact of isolated
   repricing** — the stored **headline** `ils_dispy`/`ils_ben` are **valid** (they were
   priced at population scale in the production chunks).
2. **The stored simulated COMPONENT columns are genuinely defective (a real build bug).**
   The build writes only the 5 headline EUROMOD outputs per draw; every simulated component
   (`ils_benmt`, `ils_bennt`, `ils_pen`, and all `*_s`) is left as a **stale precompute
   carry-over, constant across draws**, so it does **not** correspond to the scenario
   actually run. Hence stored `ils_ben ≠ ils_pen + ils_benmt + ils_bennt` on **58–59 % of
   singles** and **32–40 % of couples** decider rows (up to ±€4,425).

Both require a **build-level fix**: re-price each draw and write **all** `ils_*` / `*_s`
from that draw's EUROMOD output (so every row is one coherent, draw-specific scenario), and
do it at **population/chunk scale** (so the means tests see the population they need).

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; no `V_i^dir` is
> computed; no redrawn node is priced; nothing is re-estimated; no correction candidate is
> produced; and no build / storage / engine-ready / priced / precompute / chunk parquet is
> written or overwritten.** Read-only diagnosis. Not committed automatically.

---

## Tasks 1–2 — localise the `ils_ben` gap, and the build write-back evidence

**Sample (cross-track).** Singles FAIL nodes from Two-K (2017, e.g. HH 300001809101
draws 1/6; HH 300001793700 draws 8/14) with PASS controls (same HH, other draws), and a
couples singleton FAIL node from Two-I (HH 300001801900). All `ils_ben`-localised, 0 TUDef,
income/contributions (`ils_origy`/`ils_sicdy`) machine-zero.

**Component localisation.** Two patterns appear:
- Some failing nodes localise to **housing** (`bhotn_s`/`bchlg_s`, inside `ils_benmt`) — the
  clean reprice's `ils_benmt` and `*_s` are internally consistent.
- Others have an `ils_ben` gap with **all stored subtotals and `*_s` machine-zero** — the
  stored headline carries a value none of its stored parts support.

**Decisive identity check (persisted outputs).** Stored
`ils_ben − (ils_pen + ils_benmt + ils_bennt)` on decider rows:

| cell | identity violations | max residual |
|---|---|---|
| singles 2015 / 2016 / 2017 | 58.9 % / 59.0 % / 57.8 % | €1,609 / 1,754 / 1,678 |
| couples 2015 / 2016 / 2017 | 39.9 % / 39.9 % / 31.6 % | €4,425 / 2,546 / 1,723 |

The stored **headline `ils_ben` is desynced from its own stored components** on a large
fraction of rows.

**Per-draw staleness (the build bug).** For singles 2017, the stored **headline** `ils_ben`
**varies across draws** (94.5 % of HH) and `ils_dispy` varies for 100 % — they **are**
draw-specific. But the stored **component** `ils_benmt` is **CONSTANT across draws for
100 %** of HH. The build code confirms why
(`scripts/bpool/run_bpool_euromod_chunk.py`, lines 186–194):

```python
out_df = chunk_df.reset_index(drop=True).copy()        # starts as the PRECOMPUTE input
...
em_out_cols = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]   # only the 5 headline cols
for c in em_out_cols:
    out_df[c] = sim_df[c].values                       # overwrite ONLY these 5 per draw
```
`_EM_OUTPUT_COLS = ["ils_dispy", "ils_origy", "ils_ben", "ils_tax", "ils_sicdy"]`. Every
other simulated column EUROMOD produced for that draw (`ils_benmt`, `ils_bennt`, `ils_pen`,
all `*_s`, `tin*_s`, …) is **discarded** and the **stale precompute value is kept**. This is
exactly the reviewer's requirement: *any `ils_*` file should always be draw-specific, and
the sync must happen for each draw after the EUROMOD run so any `ils_*` corresponds to a
scenario actually run.* **Build bug #1 — confirmed in code and data.**

---

## Task 3 — year-gradient / policy-vintage hypothesis: REJECTED

For deterministic singles 2017 FAIL nodes, repricing the stored node under each available
policy system (`FR_2014`, `FR_2015`, `FR_2016`) with the **dataset held fixed** to the
node's own:

- the clean `ils_ben` **does vary** by policy system (e.g. node 793700/8: FR_2014 → 241,
  FR_2015 → 245, FR_2016 → 180), **but none equals the stored value** (268);
- across the tested genuine-failure nodes, **the stored value reproduces under NONE of the
  three vintages**.

**The stored value is not reproducible under any available policy system.** The residual is
**not** a system-pairing / policy-vintage mismatch. (The rising-by-year prevalence is a
by-product of population/benefit-mix differences across the data years, not a vintage
mismatch.)

---

## Task 4 — full-chunk / population-context hypothesis: CONFIRMED (the key finding)

Falsifiable test on a singles FAIL node (HH 300001809101, draw 1, stored `ils_ben` 186.14):
reprice with progressively more households sharing the EUROMOD batch (same draw):

| households in batch | clean `ils_ben` |
|---|---|
| 1 (isolated) | 0.00 |
| 2 | 0.00 |
| 5 | 0.00 |
| **20** | **186.14 = stored ✓** |
| 100 | 186.14 = stored ✓ |

The failing node **reproduces the stored value exactly once a representative population
(~≥ 20 households) shares the batch**, and not before. (It does **not** depend on draws —
the same HH's all-101-draws batch in isolation still gives 0.00; it is **population**, not
draw count.) This is the signature of a EUROMOD policy element that reads a population-level
quantity (a means-test reference / national aggregate). The reviewer's point — *of course
the means-tested benefit takes into consideration all household members* — generalises here:
the French means tests also need the **population** EUROMOD was given in the production
chunk. **CONFIRMED:** a failing node that fails in isolation reproduces the stored value in
faithful population context; matched PASS controls also reproduce. The stored **headline**
value is therefore **valid**, and the isolated/bounded reprice instrument used in
Two-G/H/I/K is **unfaithful for benefits**.

*Couples caveat (honest):* for the couples singleton FAIL node, an 80-household same-node
population batch did **not** reproduce the stored value, and a faithful per-household
full-`draw_joint`-band replay (the production couples chunk shape) was **infeasible to run
to completion in the bounded budget** (dense-stamp full-band batches abort/split and time
out). So for couples the population-context mechanism is **demonstrated for singles and
strongly indicated but not yet exact-reproduced** at the bounded scale here; a faithful
full-production-couples-chunk replay is required to confirm exactly (which is itself the
build-level path of Verdict B).

---

## Task 5 — verdict

**B. IDENTIFIED BUT REQUIRES BUILD-LEVEL / FULL-CHUNK REPRICING.**

The cross-track `ils_ben` "residual" is identified as two build-level facts, neither a
state-reconstruction gap recoverable by bounded plumbing:

1. **Benefit pricing is population-dependent** → the existing-node clean-reprice instrument
   must run at **production-chunk (population) scale**, not isolated/bounded. The stored
   **headline** `ils_dispy`/`ils_ben` are valid (they reproduce at population scale, singles
   exact; couples indicated). The Two-G/H/I/K per-node "16–22 % residual" is, for the
   headline, an **instrument artefact of isolated repricing**, not a stored-data defect.
2. **The stored simulated COMPONENT columns are stale** (`ils_benmt`/`ils_bennt`/`ils_pen`/
   `*_s` not written per draw) → a genuine build defect requiring a **build-level re-write**
   that persists **all** `ils_*` / `*_s` from each draw's EUROMOD `sim_df`, at population
   scale.

**Consequence for welfare pricing.** The blocker for redrawn-node `V_i^dir` welfare pricing
is **not** an irrecoverable benefit-state gap and **not** a policy-vintage mismatch. It is
that (a) any reprice (existing or redrawn) must be done at **population/chunk scale** to be
faithful, and (b) the build must be re-run to write **draw-specific, internally-consistent**
`ils_*` / `*_s` columns. Both are **build-level**, and both are now precisely specified. Per
scope, **no correction candidate is produced and no parquet is written** in this increment.

### Does this invalidate the certified estimate? — NO (important nuance)
The stale **component** columns do **not** necessarily invalidate the certified estimate.
The likelihood consumes **headline consumption** only: the estimator's couples/singles
consumption is `ils_dispy_real` → household-joint sum → `c_norm` (verified in Two-G:
`c_norm × c_scale == priced joint ils_dispy_real`, diff 0.0), and `ils_dispy` is among the
**five headline columns that ARE overwritten per draw** from `sim_df`. So the estimator
input (`ils_dispy_real` / normalized consumption) is the **correct draw-specific value**;
the stale columns are `ils_benmt` / `ils_bennt` / `ils_pen` / `*_s`, which the likelihood
does **not** read. The build bug is therefore a serious defect for **auditability,
component validation, benefit decomposition, and any later welfare diagnostics that rely on
`ils_*` / `*_s` internals** — but it is **not**, on the present evidence, a defect in the
consumption series the certified estimate was fit on. (This increment does not re-verify the
certified estimate; it scopes the bug's blast radius to the component internals.)

### Minimal specification for the (separately authorised) build-level fix + bounded validation
The immediate next step is **not** `V_i^dir` and **not** re-estimation. It is a build-level
patch plus a **bounded** rebuild validation, before any full production rebuild:

1. **Patch the chunk worker** (`run_bpool_euromod_chunk.py`): after the per-draw EUROMOD run,
   write **every** simulated output column present in `sim_df` into `out_df`, not only the
   five headline `_EM_OUTPUT_COLS`, so each row's `ils_*` / `*_s` correspond to that draw's
   scenario actually run (the reviewer's "sync per draw").
2. **Run a tiny bounded chunk rebuild** at production / population context (a small
   household subset priced as a faithful chunk, not isolated/bounded per-node batches).
3. **Verify two gates on the bounded rebuild:** (i) **headline parity** — the rebuilt
   `ils_dispy` / `ils_ben` reproduce the existing stored headline at chunk scale; (ii)
   **internal component identity** — `ils_ben == ils_pen + ils_benmt + ils_bennt` holds to
   tolerance and each `*_s` is now draw-specific.
4. **Do not rebuild the full production data** until that bounded validation passes.

(The existing-node parity gate — the Two-K gate — must itself be re-run **population-faithfully
at chunk scale**, not isolated, since Two-L shows isolated reprice is unfaithful for benefits.)

---

## Files

- **Diagnostic source:** `scripts/welfare/welfare_cross_track_residual_diag.py` (benefit
  decomposition + cross-policy + node helpers), `scripts/welfare/run_stage2_cross_track_diag.py`
  (T2a identity scan, T2b per-draw staleness, T3 policy-vintage, T4 population driver).
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_cross_track_residual_diag.json`.
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_cross_track_diag_euromod_console.log`.
- **Build evidence:** `scripts/bpool/run_bpool_euromod_chunk.py` lines 186–194 (read-only;
  not modified).

## Explicit scope statement

No W^3 welfare finding is produced; no measure beyond W^3 is touched; no `V_i^dir` is
computed; no redrawn node is priced; nothing is re-estimated; no correction candidate is
produced; and no build / storage / engine-ready / priced / precompute / chunk parquet is
written or overwritten. This increment is read-only diagnosis.
