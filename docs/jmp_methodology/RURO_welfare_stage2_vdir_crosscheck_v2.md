# RURO Welfare — Stage Two, Increment Two-A: V_i^dir feasibility re-audit & repair

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-A only — inspect and repair the Stage-Two
`V_i^dir` feasibility claim.
**Supersedes:** the v1 audit `RURO_welfare_stage2_vdir_crosscheck_v1.md` on the
feasibility question (v1's "wholesale rebuild required" conclusion is **overturned**).
**Authority:** `RURO_welfare_scaffold_design_contract_v2.md`, `JMP_welfare_spec_v5.md`;
redraw design grounded in `welfare_proposal_individualisation_check.md`.

> **No W^3 welfare finding is produced, and no measure beyond W^3 is touched.** This
> increment re-audits the `V_i^dir` blockage, fixes agnosticism, builds couples node
> generation, and runs a bounded EUROMOD parity smoke. It does **not** promote W^3
> to a result, extend to W^1/W^2/W^4/W^5/W^6, or implement decomposition / bootstrap
> / gender-split / dominance / intra-household work. Not committed automatically.
> **The bounded EUROMOD touch is feasible but parity did NOT pass; node pricing
> stays BLOCKED, and no production `V_i^dir` run is performed — awaiting both a
> faithful reprice path and separate production authorisation.**

---

## Headline corrections to v1

1. **v1's "wholesale rebuild required" is WRONG and is narrowed.** v1 checked only the
   *engine-ready* parquet — the stripped, estimation-facing slice — found 17/18
   EUROMOD input vars missing, and concluded redrawn-node pricing needs a wholesale
   rebuild. **The storage-level priced-long files
   (`fr_p3a_bpool_priced__{year}__{mode}.parquet`) carry the FULL EUROMOD input
   schema and the stored `ils_dispy`** for every year and mode. Redrawn-node input
   records can be built from these household templates by overwriting only the
   decider's choice variables — **no wholesale rebuild**.
2. **But a new gate now binds: EUROMOD-reprice PARITY (the `V_dir` analogue of
   Stage-One Gate 0) FAILS** on existing nodes, so node pricing stays BLOCKED until
   the reprice path is made faithful — exactly as the increment's own discipline
   requires ("if parity fails … do not price redrawn nodes against an unvalidated
   path").
3. **Agnosticism repaired.** The Stage-Two welfare source no longer hardcodes the
   engine-ready singles filename, a 2015/2016/2017 year-tag map, or a singles-only
   schema probe. Stems/years/modes come from config; system-year pairing, CPI(φ),
   and the EUROMOD input schema are **reused from the build module** (so the welfare
   path matches the build exactly); `year_tag` is read from the data row.
4. **Couples redraw is now BUILT and probed** (not implied from singles).

---

## PASS / FAIL / BLOCKED status

| # | Item | Status |
|---|---|---|
| **a** | precompute/priced-long schema availability | **PASS** — all 6 year×mode priced-long files carry the full input schema (122–128/122–128 vars present) + stored `ils_dispy`. |
| **b** | bounded EUROMOD-on-redrawn-nodes feasibility | **FEASIBLE but BLOCKED on parity** — templates make the bounded touch possible; reprice parity (below) does not yet pass, so pricing is held. |
| **c** | singles redraw node construction | **PASS (BUILT)** — `redraw_nodes_singles` draws (w,h,occ,emp) from `ĝ` via the estimator's own functions; probed 3 HH/group × 50 nodes. |
| **d** | couples redraw node construction | **PASS (BUILT)** — `redraw_nodes_couples` builds joint two-partner node locations from per-partner `_male`/`_female` covariates via the same channel structure; probed 2 HH × 120 partner-nodes. |
| **e** | v1's "wholesale rebuild required" conclusion | **OVERTURNED** — false at storage level; a bounded template-overwrite touch suffices (pending a faithful reprice path). |

---

## 1. Re-audit: storage-level template availability (item a) — **PASS**

The re-audit reads the storage-level files the v1 audit missed, across all configured
years and both modes, with the **required schema taken from the build module's
`_RAW_SCHEMA[year]`** (not a welfare-hardcoded list):

| year__mode | priced-long exists | input vars present | `ils_dispy` stored | template-overwrite feasible |
|---|---|---|---|---|
| 2015__singles | yes | 122 / 122 | yes | **yes** |
| 2015__couples | yes | 122 / 122 | yes | **yes** |
| 2016__singles | yes | 124 / 124 | yes | **yes** |
| 2016__couples | yes | 124 / 124 | yes | **yes** |
| 2017__singles | yes | 128 / 128 | yes | **yes** |
| 2017__couples | yes | 128 / 128 | yes | **yes** |

`feasible_via_template_overwrite = True`; `v1_wholesale_rebuild_conclusion_holds =
False`. The engine-ready parquet that misled v1 is the downstream estimation slice;
the priced-long files are the upstream household templates that retain everything.

## 2. Redraw node construction (items c, d) — **PASS (BUILT, both modes)**

`ĝ` redraw reuses the estimator's own draw functions (employment Bernoulli(`π0`),
occupation `p(loc4|dgn,educ3)`, D1 hours, lognormal wage at `μ_i = X_i b +
δ_occ[loc4]`), EV shocks integrated analytically — **no Fréchet draws, no simulated
argmax**.

| Group | machinery | households probed | nodes drawn |
|---|---|---|---|
| singles_male | **BUILT** | 3 | 150 |
| singles_female | **BUILT** | 3 | 150 |
| couples | **BUILT** | 2 | 120 (per-partner summed) |

Couples node locations are generated jointly from the wide couples record's per-partner
`_male`/`_female` covariates, mirroring `build_bpool_couples` (partners independent).
The probe produces node **locations only**; pricing them is the gated EUROMOD touch.

## 3. EUROMOD-on-nodes parity — the `V_dir` analogue of Gate 0 (item b) — **FAIL → pricing BLOCKED**

Before pricing any redrawn node, the template-overwrite path is validated on
**existing** nodes: take a tiny set of priced-long rows whose `ils_dispy` is stored,
feed them **unchanged** (no choice overwrite) through the build's `EuromodRunner`
with the build's raw schema + system pairing **and the build's `_stamp_draw_ids`
step**, and compare repriced `ils_dispy` to stored `ils_dispy`.

**Result (2016, singles, 5 HH / 100 rows, id-stamped):**

| metric | value |
|---|---|
| status | **FAIL** |
| median abs diff | **0.0** |
| max abs diff | 422.35 |
| rows above tol (1e-6) | **8 / 100** |
| EUROMOD ran | yes (`Simulation for system FR_2015 with dataset FR_2016_a3 finished`) |

**Diagnosis (two contributing causes, both identified):**
1. **Missing draw-ID stamping** — the build stamps unique per-draw IDs
   (`_stamp_draw_ids`) so per-draw rows don't collide on `idhh`/`idperson` inside
   EUROMOD. Without it the divergence was worse (21/100 bad, max 3163). **Now
   applied** in the parity path → 8/100 bad, max 422.
2. **A residual reprice gap** — even id-stamped, 8/100 rows still diverge, so the
   reprice is **not yet fully faithful** to the build (the chunk runner performs
   additional preprocessing the smoke path does not yet replicate). **Median 0.0
   confirms the path is fundamentally correct**; the tail is a faithfulness gap, not
   a conceptual error.

**Consequence (contract-mandated).** Parity FAIL ⇒ the template-overwrite EUROMOD
path is **not trustworthy yet** ⇒ **no redrawn node is priced against it.** Node
pricing stays **BLOCKED** regardless of the (now-confirmed) schema availability.
This is exactly the increment's instruction: *"If this parity fails, the
template-overwrite path is not trustworthy and node pricing stays BLOCKED regardless
of schema availability — do not price redrawn nodes against an unvalidated EUROMOD
path."*

## 4. `V_i^dir` cross-check status

| Item | Status |
|---|---|
| redraw machinery (singles + couples) | **BUILT** |
| EUROMOD-on-nodes feasible (schema) | **YES** (templates) |
| EUROMOD reprice parity | **FAIL** (median 0, 8/100 tail) |
| `\|V_i^dir − V_i^IS\|` computed | **NO** — blocked on parity; and even if parity passed, production `V_dir` is **deferred** per the increment scope (stop after smoke, await authorisation) |
| households deferred | singles_male 2243, singles_female 2764, couples 1285 |
| escalated set | **∅** (no `V_dir` value computed → trigger cannot fire) |

## 5. Multiplier stability (Gate 1 part i)

`full_2x_4x_status = DEFERRED` (not BLOCKED): the re-audit shows the 2×/4× node
growth is **feasible** via the same template-overwrite pricing — but it shares the
**same unpassed parity gate**, so it is deferred to the authorised production run,
not run here. The existing-node subsample probe (needs no new consumption) is
unchanged from v1 and still converges in the median while the low-ESS max tail
persists (sm/sf/cou @0.75: max ≈ 1.27 / 1.25 / 1.31, median ≈ 0.087 / 0.089 / 0.050)
— necessary-not-sufficient, as before.

---

## What unblocks the next increment (Two-B — not performed here)

One thing remains: **make the reprice path fully faithful** so parity passes to
machine tolerance on existing nodes. Concretely, replicate the chunk runner's
remaining preprocessing (beyond `_stamp_draw_ids`) that the smoke path does not yet
reproduce, then re-run the parity smoke. **Only when parity PASSES** may the bounded
redrawn-node pricing proceed — at the same 2016-real basis and EUROMOD system year
as the build (φ reused from `_CPI`; **no re-deflation**, **no silent interpolation**,
**no wholesale rebuild**). With a parity-validated path:
1. price the redrawn `ĝ` nodes for the full singles samples + flagged couples →
   compute `|V_i^dir − V_i^IS|` and the escalation decision;
2. price the 2×/4× additional `ĝ` nodes → the full draw-growth stability gate.

Both then require separate production-run authorisation (this increment stops at the
feasibility + parity smoke per scope).

---

## Files

- **Source (updated):** `scripts/welfare/welfare_vdir.py` (storage-level audit,
  singles+couples redraw, EUROMOD reprice parity with build's `_stamp_draw_ids`,
  subsample stability), `scripts/welfare/run_stage2_vdir.py` (runner). Agnostic:
  no hardcoded case constants; system/CPI/schema reused from the build module.
- **Config (updated):** `scripts/welfare/configs/welfare_stage1_w3.yaml` — new
  `welfare.stage2` block (priced/precompute stems, years, modes, build_module,
  EUROMOD-on-nodes parity tol + tiny smoke params). Case values live in config.
- **Provenance:** `outputs/welfare/stage1_w3/stage2_vdir_v2_results.json`.

## Commands run

```text
.venv\Scripts\python.exe scripts/welfare/run_stage2_vdir.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --out-json outputs/welfare/stage1_w3/stage2_vdir_v2_results.json
```

Parity smoke: 2016 / singles / 5 HH / 100 rows / tol 1e-6 (config
`welfare.stage2.euromod_on_nodes`). EUROMOD reused from the build
(`run_bpool_euromod_chunk._SYSTEM_PAIRING / _CPI / _RAW_SCHEMA / EuromodRunner`).

## Explicit scope statement

No W^3 welfare finding is produced. No measure beyond W^3 is touched. The bounded
EUROMOD-on-nodes touch is **feasible** (v1's wholesale-rebuild conclusion overturned)
but the reprice **parity FAILS**, so node pricing — and therefore `V_i^dir` and the
2×/4× growth — stays **BLOCKED** pending a faithful reprice path and separate
production authorisation. Per the increment scope, this stops after the smoke
feasibility report.
