# RURO Welfare — Stage Two, Increment Two-M: chunk write-back fix + bounded validation

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-M only — build-level EUROMOD chunk write-back fix
and bounded validation.
**Status:** complete. **Patch applied to `scripts/bpool/run_bpool_euromod_chunk.py`;
bounded validation PASSES the decisive estimate-protecting gate exactly.** Readiness is
split: **singles_ready = TRUE; couples patch-valid, but exact full-scale stored-headline
reproduction is DEFERRED to the authorised full rebuild** (a full-production-chunk
property, not bounded).

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; no `V_i^dir` is
> computed; no redrawn welfare node is priced; nothing is re-estimated; no full production
> rebuild was run; and no production parquet was written or overwritten** (validation
> parquets go to a temporary dir only). Not committed automatically.

---

## Task 1 — the patch

In `scripts/bpool/run_bpool_euromod_chunk.py`, the per-draw write-back previously wrote
back **only** the five headline columns from the EUROMOD `sim_df`, leaving every other
simulated output column (`ils_benmt`, `ils_bennt`, `ils_pen`, all `*_s`, `t*_s`, …) as a
stale precompute carry-over (Two-L). **Exact change** (lines 190–205):

```python
# BEFORE
em_out_cols = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]
for c in em_out_cols:
    out_df[c] = sim_df[c].values

# AFTER (Two-M)
_raw_input_cols = set(_RAW_SCHEMA[year])
sim_output_cols = [c for c in sim_df.columns if c not in _raw_input_cols]
for c in sim_output_cols:
    out_df[c] = sim_df[c].values
em_out_cols = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]
```

It now writes back **every simulated-output column** EUROMOD produced for that draw
(`sim_df` columns that are **not** raw EUROMOD inputs — 266 columns in practice), so each
row's `ils_*` / `*_s` correspond to the scenario actually run. **Preserved exactly:**
`idhh_true`, `idperson_true` (set from the original `chunk_df` ids before the write-back),
`ils_dispy_real` (recomputed as `ils_dispy × phi`), the CPI handling, the metadata block
(plus a new `n_simulated_output_cols_written` field), row order (positional
`sim_df[c].values` assignment; EUROMOD preserves row order — re-verified), and all keys
(`stacked_hh_uid` / `draw*` / `ruro_decider` are not in `sim_df`, so they pass through
untouched). The five headline columns are a **subset** of the new write-back set, so they
remain byte-identical to the previous behaviour. **No estimation or welfare code changed.**

---

## Task 2 — bounded validation

**Scope.** Tiny deterministic, population-scale validation chunks for 2017, written to a
**temporary** dir only (`…/Temp/.../mnl_twoM_validation/`), never a production path:

| cell | households | rows | EUROMOD wall | TUDef |
|---|---|---|---|---|
| singles_male 2017, draws [0,20) | 120 | 2,780 | ~5 s | 0 |
| singles_female 2017, draws [0,20) | 120 | 3,060 | ~3 s | 0 |
| couples 2017, draws [0,20) | 120 | 8,379 | ~7 s | 909 |

Each cell is built through the **patched** assembly path (stamp → raw-schema EUROMOD input
→ per-draw `sim_df` → write back all simulated outputs), and also through the **unpatched**
(5-headline-only) assembly on the *same* `sim_df`, so the patch's effect can be isolated.

### Gate A — headline invariance (estimate-protecting)

This gate is evaluated in two parts:

- **A1 — patch invariance (decisive, scale-independent).** Patched vs unpatched assembly on
  the **same** EUROMOD `sim_df`: the headline columns must be **identical**. Result —
  `max |Δ| = 0.0` exactly for **every** headline column (`ils_dispy`, `ils_origy`,
  `ils_ben`, `ils_tax`, `ils_sicdy`, `ils_dispy_real`) in **all three cells**. **The patch
  does not move any estimator input.** ✓ (This is the gate the prompt's "if any headline
  column moves, STOP" rule targets; it passes exactly.)

- **A2 — production reproduction (informational, population-context).** Patched headline vs
  the **stored production** values at *bounded* chunk scale. `ils_origy` and `ils_sicdy`
  reproduce to machine zero (0 rows above tol). The **means-tested** `ils_ben` / `ils_dispy`
  do **not** fully reproduce at this bounded scale (≈ 30 % of rows differ) — **as expected
  from Two-L**: production priced at **full** chunk scale, and the French means tests depend
  on the population EUROMOD is given. A2 is therefore **not** used to gate the patch (A1
  settles that); exact means-tested headline reproduction is a **full-production-chunk
  property**, validated only when the authorised full rebuild runs.

### Gate B — component coherence (the bug, now fixed)

On the rebuilt (patched) rows, decider-level:

| cell | `ils_ben == pen+benmt+bennt` violations | `ils_dispy` identity violations | `ils_benmt` varies across draws | rows with corrected `ils_benmt` |
|---|---|---|---|---|
| singles_male 2017 | **0** (max 0.0) | **0** (max 0.0) | 92.2 % of HH | 1,566 |
| singles_female 2017 | **0** | **0** | 93.8 % of HH | 1,435 |
| couples 2017 | **0** | **0** | 81.7 % of HH | 1,220 |

The stale-data identity violation (Two-L: **58–59 % singles / 32–40 % couples**) is **gone**
— `ils_ben = ils_pen + ils_benmt + ils_bennt` and `ils_dispy = ils_origy − ils_tax −
ils_sicdy + ils_ben` both hold to machine tolerance. The simulated component columns now
**vary across draws** (82–94 % of HH), and 1,220–1,566 rows per cell carry a **corrected
draw-specific** `ils_benmt` that differs from the old stale carry-over — direct evidence the
staleness is repaired. ✓

### Gate C — couples population-context

The couples cell passes **A1 (patch invariance) and B (coherence) exactly**, and its
income/contribution headline reproduces (A2). But **exact reproduction of the stored couples
means-tested headline (`ils_ben`/`ils_dispy`) at population scale was NOT achieved at the
bounded validation scale** (A2: ~30 % of rows differ, the Two-L population-context effect).
Per the increment's split-readiness rule this is reported as: the patch is **valid and
coherent for couples**, but **couples full-scale headline reproduction is NOT yet confirmed**
— it requires a faithful **full-production-couples-chunk** run, which is the authorised
full-rebuild step, not a bounded validation. (The same caveat applies to singles
means-tested headline; A1+B+A2-income are the bounded gates that pass.)

### Gate D — row / warning stability

- **No row-count mismatch:** `len(sim_df) == len(input)` enforced; all cells `OK`.
- **Keys / ordering stable:** positional write-back; EUROMOD preserves row order
  (re-verified); `stacked_hh_uid`/`draw*`/`ruro_decider`/`idhh_true`/`idperson_true`
  pass through untouched.
- **No new TUDef / warning regression:** the patch is **post-EUROMOD** (write-back only), so
  the EUROMOD run and its TUDef count are **identical** patched vs unpatched by construction.
  Singles 0 TUDef; couples 909 TUDef — the latter is the **pre-existing** `draw_joint`
  collision count at this scale (Two-E/F), **not** introduced by the patch.
- **Output location:** validation parquets written only to the temp dir; **0 production
  parquet modified** (verified).

---

## Task 3 — readiness

| gate | singles | couples |
|---|---|---|
| A1 patch invariance (headline identical patched vs unpatched) | ✓ exact 0.0 | ✓ exact 0.0 |
| A2 income/contribution reproduce stored production | ✓ | ✓ |
| A2 means-tested headline reproduce at bounded scale | n/a (full-chunk) | n/a (full-chunk) |
| B component coherence (identities hold; components draw-specific) | ✓ | ✓ |
| D row/warning stability; no production overwrite | ✓ | ✓ |

- **`singles_ready`: TRUE** — the patch is headline-invariant and produces coherent,
  draw-specific components for singles; income/contributions reproduce production.
- **`couples_ready`: patch valid and coherent, but FULL-SCALE HEADLINE REPRODUCTION
  DEFERRED.** The bounded validation cannot reproduce the stored couples means-tested
  headline at population scale (Two-L); that confirmation belongs to a faithful
  full-production-couples-chunk run.

**READY / NOT READY for a separately authorised full production rebuild:** **READY to
proceed to a full rebuild *with a mandatory full-chunk validation gate*.** The patch is
proven safe for the estimator (A1 exact) and fixes the component staleness (B). Before the
rebuilt data is trusted as a replacement, the full rebuild must itself pass, at
**full-production-chunk scale**: (i) headline parity vs the existing stored production on
**all** rows (the population-context check this bounded increment could only do for
income/contributions), and (ii) the component-coherence identities. Do **not** swap the
production parquets until that full-scale validation passes.

---

## Files

- **Patched build source:** `scripts/bpool/run_bpool_euromod_chunk.py` (write-back block
  lines 185–206; meta line; no other change).
- **Validation source:** `scripts/welfare/run_stage2_chunk_writeback_validation.py`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_chunk_writeback_validation.json`.
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_chunk_writeback_validation_euromod.log`.
- **Validation parquets:** temporary dir only (`…/Temp/.../mnl_twoM_validation/`); **not**
  a production path and **not** committed.

## Explicit scope statement

No W^3 welfare finding is produced; no measure beyond W^3 is touched; no `V_i^dir` is
computed; no redrawn welfare node is priced; nothing is re-estimated; no full production
rebuild was run; and no production parquet was written or overwritten. The patch changes
only previously-stale simulated component columns; the five headline columns are proven
invariant to machine zero.
