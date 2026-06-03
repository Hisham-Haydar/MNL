# RURO Welfare — Stage Two, Increment Two-K: singles V_i^dir gate + smoke

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-K only — SINGLES track. Existing-node parity gate
(Task 1), bounded `V_i^dir` smoke (Task 2, gate-conditional), readiness report (Task 3).
**Status:** complete. **GATE OUTCOME: FAIL → STOP after Task 1. Readiness: NOT READY.**
The singles existing-node clean-reprice path does **not** reproduce stored `ils_ben` at
production scope — it fails in **every** one of the 6 (year × sex) cells, on ~16–22 % of
sampled nodes, with the **same stored-target signature** as the couples residual
(`ils_ben`-localised, income/contributions machine-zero, 0 TUDef, identical inputs,
isolated-confirmed). Per the stop rule, **no redrawn singles node was priced** and the
`V_i^dir` smoke (Task 2) was **not run**.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched; couples were
> not touched; nothing was re-estimated; no full-sample singles `V_i^dir` production run
> was executed; no build / storage / engine-ready / priced / precompute / chunk parquet
> was written or overwritten.** EUROMOD was run only on bounded existing-node singles
> parity samples. Not committed automatically.

---

## Task 1 — existing-node parity gate at production scope

**Sample (deterministic, larger than the Two-E ladder).** For each of the 6 cells
(2015/2016/2017 × {singles_male, singles_female}, split by `dgn`: male = 1, female = 0):
the **first 30 households by `stacked_hh_uid`** within the cell, and the **first 20
existing draws per household** (the Two-E ladder used 6). Singles node key
`(stacked_hh_uid, draw)`; the production stamp `idperson × 1000 + draw` is **unique per
node** (collision-free — Two-E Rung-3 verified the stamped singles batch reproduces
stored), so each cell is repriced in **one batched EUROMOD call** and compared to stored
on decider rows keyed by `(stacked_hh_uid, draw, original idperson)`.

**Per-cell parity grid** (`|clean − stored|`, max abs over the cell; `bad` = nodes above
tol = 1 × 10⁻⁶; each cell = 600 decider nodes):

| cell | status | TUDef | `ils_origy` | `ils_ben` (max / bad) | `ils_tax` (bad) | `ils_sicdy` |
|---|---|---|---|---|---|---|
| 2015 · male | **FAIL** | 0 | 0.0 | **678.41 / 124** | 26 | 0.0 |
| 2015 · female | **FAIL** | 0 | 0.0 | **678.41 / 125** | 22 | 0.0 |
| 2016 · male | **FAIL** | 0 | 0.0 | **672.84 / 98** | 19 | 0.0 |
| 2016 · female | **FAIL** | 0 | 0.0 | **666.55 / 131** | 25 | 0.0 |
| 2017 · male | **FAIL** | 0 | 0.0 | **942.02 / 126** | 14 | 0.0 |
| 2017 · female | **FAIL** | 0 | 0.0 | **1237.27 / 116** | 28 | 0.0 |

**PASS requires every cell to reproduce, including `ils_ben`. Every cell FAILS.** The
divergence is **localised to `ils_ben`** (and the small benefit-driven `ils_tax`);
`ils_origy` and `ils_sicdy` reproduce to **machine zero** in all cells; `ils_dispy` tracks
`ils_ben` exactly. Failure prevalence is ~16–22 % of nodes per cell (98–131 of 600).

### 1.1 The failure is real (isolated-confirmed), not a batch artefact
Four batch-flagged failures were re-tested under the independent **isolated** Two-E
`_compare` path (single node, original IDs — the validated benchmark). All four **also
FAIL isolated**, 0 TUDef, with matching `ils_ben` divergences:

| HH (2017) | draw | batch clean `ils_ben` | stored `ils_ben` | isolated status |
|---|---|---|---|---|
| 300001793700 | 8 | 180.13 | 268.00 | FAIL |
| 300001793700 | 14 | 311.36 | 656.54 | FAIL |
| 300001809101 | 1 | 0.00 | 186.14 | FAIL |
| 300001809101 | 6 | 0.00 | 110.79 | FAIL |

### 1.2 Same stored-target signature as the couples residual
For a failing singles node (HH 300001809101, draw 1: stored `ils_ben` 186.14, clean 0.0),
**all 16 EUROMOD input fields are identical** between precompute-long and priced (`lhw`,
`yivwg`, `yem`, `bch00`, all benefit inputs). So — exactly as for couples (Two-G/Two-H) —
the stored value was produced under an effective EUROMOD state the current precompute
inputs do not reproduce: **same inputs → different stored output**, `ils_ben`-localised,
0 TUDef, isolated-confirmed. The singles stored-target reproducibility gap is the **same
phenomenon** as the couples singleton residual, now shown to affect **singles** too at
production scope.

**Relation to Two-E.** Two-E reported that singles repriced cleanly — but its ladder was
tiny (6 draws on a couples-focused case). At production scope (600 nodes/cell) the singles
`ils_ben` residual is clearly present. Two-E's "singles collision-free" conclusion stands
(node key makes the stamp unique; 0 TUDef here confirms it); what Two-E did **not** surface
is this separate, non-collision **stored-target** `ils_ben` gap, which this larger sample
exposes.

---

## Task 2 — bounded V_i^dir smoke: NOT RUN (gate failed)

Per the increment's stop rule — *"If any cell fails, STOP and report. Do not price redrawn
nodes against an unvalidated path."* — the `V_i^dir` smoke was **not run**. No node was
drawn from `g_hat`; no redrawn node was priced; no `|V_i^dir − V_i^IS|` was computed.
Pricing redrawn singles nodes against a path that cannot reproduce stored existing-node
`ils_ben` for ~1 in 5 nodes would be invalid.

---

## Task 3 — readiness report

- **Task 1 per-cell parity:** FAIL in all 6 cells (table above); localised to `ils_ben`;
  income/contributions machine-zero; 0 TUDef; isolated-confirmed; identical inputs.
- **Task 2 smoke `|V_i^dir − V_i^IS|`:** not produced (gate failed).
- **Blocked households/nodes:** 0 blocked (no EUROMOD aborts); the failures are parity
  failures, not run failures.
- **EUROMOD timing (smoke basis, batched):** 6 cells, ≈ 20 s total wall over 6,400 input
  rows ⇒ ≈ **0.0031 s/input-row** (batched; a lower bound for per-node cost — it excludes
  per-call model-load/process spin-up that a finer-grained run would incur; the per-row
  basis varies a little run-to-run with EUROMOD timing — see the provenance JSON for the
  exact value of the recorded run).
- **Projected cost of the later full singles run** (full `singles_male` 2,243 +
  `singles_female` 2,764 = 5,007 households, ≈ 1 person-row per singles node):

  | nodes/HH | approx input rows | approx hours (lower bound) |
  |---|---|---|
  | 100 | 500,700 | ≈ 0.43 |
  | 300 | 1,502,100 | ≈ 1.29 |
  | 900 | 4,506,300 | ≈ 3.88 |

  (Basis ≈ 0.0031 s/row; lower bound — excludes batch overhead and model load. Moot for
  now since the gate fails.)

- **READINESS: NOT READY** for a separately authorised full singles `V_i^dir` production
  run. The existing-node parity precondition is **not met**: the singles clean-reprice path
  does not reproduce stored `ils_ben` at production scope.

### What a later (separately authorised) increment must do first
The singles `V_i^dir` track is blocked on the **same stored-target `ils_ben` residual** as
couples. The next step is **not** a `V_i^dir` run and **not** a redrawn-node smoke; it is to
**diagnose the stored-target `ils_ben` reproducibility gap** (now shown to be cross-track:
singles + couples, ~16–22 %, `ils_ben`-localised, identical inputs, isolated-confirmed,
mechanism unresolved). Until clean reprice reproduces stored `ils_ben` for existing nodes,
no redrawn-node pricing on either track can be trusted.

---

## Files

- **Source (Two-K, singles gate only):**
  `scripts/welfare/run_stage2_singles_vdir_gate.py`.
- **Config block:** `welfare.stage2.singles_vdir_gate` in
  `scripts/welfare/configs/welfare_stage1_w3.yaml`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_singles_vdir_gate.json`
  (per-cell parity grid, sample rule, throughput, gate verdict).
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_singles_vdir_gate_euromod_console.log`.

## Explicit scope statement

No W^3 welfare finding is produced; no measure beyond W^3 is touched; couples were not
touched; nothing was re-estimated; no full-sample singles `V_i^dir` production run was
executed; and no build / storage / engine-ready / priced / precompute / chunk parquet was
written or overwritten. EUROMOD was run only on bounded existing-node singles parity
samples. The gate failed, so no `V_i^dir` smoke was produced and nothing is authorised.
