# RURO Welfare — Stage Two, Increment One: V_i^dir cross-check + multiplier stability

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT ONE only — build the `V_i^dir` redraw
cross-check and the draw-multiplier stability inputs that Stage One reported
BLOCKED.
**Status:** `V_i^dir` **redraw machinery BUILT**; `V_i^dir` **values BLOCKED**
(redrawn-node consumption needs a wholesale EUROMOD rebuild the contract forbids);
multiplier **2×/4× growth BLOCKED** (same blocker); a weaker **existing-node
subsample stability probe runs and converges**.
**Authority:** `RURO_welfare_scaffold_design_contract_v2.md`, `JMP_welfare_spec_v5.md`;
redraw design grounded in `welfare_proposal_individualisation_check.md`.

> **No W^3 welfare finding is produced, and no measure beyond W^3 is touched.**
> This increment builds the cross-check machinery and resolves the feasibility of
> its inputs; it does not promote W^3 to a result, extend to W^1/W^2/W^4/W^5/W^6,
> or implement decomposition / bootstrap / gender-split / dominance / intra-household
> work. Not committed automatically.

---

## What was built

- `scripts/welfare/welfare_vdir.py` — the `V_i^dir` redraw machinery and the
  EUROMOD-on-nodes coverage probe and the existing-node subsample stability probe.
  Extends the Stage-One core; **no estimator source edited**.
- `scripts/welfare/run_stage2_vdir.py` — runner: designed cross-check scope, the
  EUROMOD-on-nodes boundary, the redraw machinery probe, the multiplier-stability
  probe. Emits `outputs/welfare/stage1_w3/stage2_vdir_results.json` (provenance).

The redraw draws integration nodes `(w,h,occ,emp)` from the **estimated individual
opportunity density** `ĝ(·; x_i)` using the **same channel functions** the
estimator's proposal used — employment Bernoulli(`π0`), occupation
`p(loc4|dgn,educ3)` (`occ_draw_empirical.draw_loc4`), hours D1 five-mode mixture
(`hours_mixture_d1.draw_hours_d1`), wage `LogNormal(μ_i, σ)` with
`μ_i = X_i b + δ_occ[loc4_i]` (`pilot_wage_draw.draw_pilot_wages`). The extreme-value
shocks are integrated **analytically** via the log-sum: **no Fréchet draws, no
simulated argmax** — this is a welfare-integration estimator, not a behavioural
choice simulation. Probe: 150 nodes drawn per group across 3 households each for
`singles_male` / `singles_female` (`status: ok_locations_only_consumption_blocked`).

---

## A. `V_i^dir` redraw-from-`ĝ` cross-check

### Designed scope (fixed by the production ESS numbers)

| Group | designed target | n_target HH | of total | # below ESS<30 |
|---|---|---|---|---|
| singles_male | **full sample** | 2243 | 2243 | 1918 |
| singles_female | **full sample** | 2764 | 2764 | 2493 |
| couples | **sub-threshold flagged** | 1285 | 7438 | 1285 |

Singles run on the **full** samples: 85–90% fall below the ESS threshold (1918/2243,
2493/2764), so the flagged subset is nearly the whole and a blanket cross-check is
cleaner to reason about than a conditional one. Couples (median ESS ~63; only
1285/7438 flagged) are cross-checked on the **genuine sub-threshold flag**.

### The load-bearing boundary — redrawn-node consumption requires EUROMOD

For W^3 the laissez-faire reference lies in the household's own set, so each redrawn
node `(w,h)` needs its disposable income `c_is`. In this repo
`consumption = ils_dispy_real` (`harmonise_bpool_engine_ready.py:106-108`) =
**EUROMOD output**, produced per *existing* draw node by
`run_bpool_euromod_chunk.py` → `assemble_bpool_priced.py`. A **redrawn** node has no
`c_is` unless EUROMOD is run on it.

**EUROMOD-on-nodes is infeasible this increment without a wholesale rebuild** —
evidence, not assumption:

- The `euromod` package **is importable** (v0.2.17) and `em_root` resolves to a
  present install — so EUROMOD *could* run in principle.
- **But** the chunk runner requires a large input schema
  (`lcs, les, lfs, lhw, lhw_f, lindi, liwftmy, liwmy, liwmy_f, yivwg, yiy, yot, ypp,
  ypr, ypt, yse, yse_f, ysemy, …`). On the engine-ready parquet, **only 1 of 18
  sampled input vars is present** (`lhw`); the other **17 are missing**
  (`feasible_without_wholesale_rebuild: False`). Building EUROMOD input records for
  redrawn nodes therefore requires the raw microdata / priced long files — a
  **wholesale rebuild**, which contract **§6 gate 1.iii forbids**, alongside silent
  interpolation.

**Decision (contract-determined, not a guess).** The contract's own §6 gate 1.iii
resolves this: wholesale EUROMOD rerun and silent interpolation are both forbidden,
and the redrawn-node `c_is` requires one of them. So **redrawn-node consumption is
reported BLOCKED, with exact counts, and not approximated** — exactly the BLOCKED
branch the prompt anticipated.

### `V_i^dir` result

| Item | Value |
|---|---|
| redraw machinery built | **YES** (draws `(w,h,occ,emp)` from `ĝ` via estimator functions) |
| `\|V_i^dir − V_i^IS\|` computed | **NO — BLOCKED** |
| blocked households | singles_male **2243**, singles_female **2764**, couples **1285** |
| escalated set (V_dir-as-primary) | **∅ (empty)** |

The contract escalation rule — *persistent `|V_i^dir − V_i^IS|` beyond tolerance is
the only trigger to mark a household for `V_i^dir`-as-primary* — **cannot fire**,
because `V_i^dir` is BLOCKED. **No household is escalated.** No welfare distribution
is recomputed from any escalated set (there is none).

---

## B. Draw-multiplier stability (Gate 1 part i)

The prompt's distinction is decisive: *welfare-integral node growth* vs
*estimation-draw rebuilding*.

### Configured 2×/4× growth — **BLOCKED**

Growing the welfare integral beyond the existing node count requires **new** nodes
drawn from `ĝ`, whose consumption `c_is` needs EUROMOD-on-nodes — the **same blocker
as A**. This is welfare-integral node **growth** (not estimation-draw rebuilding via
the B-pool builder); both are blocked by the missing `c_is`, not by the builder.
Stated precisely so the two are not conflated.

### Existing-node subsample probe — **runs (needs no new consumption)**

A *weaker* stability probe that needs **no new consumption**: subsample the
**existing** nodes at fractions and measure `V_i^IS` drift as the node count grows
toward the full set (chosen row always retained; log-mean normalisation matched
across node counts). Convergence here is **necessary-not-sufficient** for the full
draw-growth gate, which stays BLOCKED.

`|V_i^IS(frac) − V_i^IS(full)|`, max / median across households:

| Group | frac 0.25 (max / med) | frac 0.50 | frac 0.75 | frac 1.0 |
|---|---|---|---|---|
| singles_male (k of 101) | 2.49 / 0.276 | 1.36 / 0.158 | 1.27 / 0.087 | 0 / 0 |
| singles_female (k of 101) | 1.82 / 0.296 | 1.85 / 0.166 | 1.26 / 0.089 | 0 / 0 |
| couples (k of 901) | 1.53 / 0.149 | 1.23 / 0.088 | 1.31 / 0.050 | 0 / 0 |

**Reading.** Median drift falls monotonically toward zero as the node count grows
(sm 0.276→0.158→0.087; sf 0.296→0.166→0.089; cou 0.149→0.088→0.050) — the integral
is stabilising in the central mass. The **max** drift stays elevated (~1.3–2.5) and
does **not** collapse with the median — the tail is the low-ESS households (the same
set the ESS diagnostic flagged), where a few nodes carry concentrated weight and
subsampling perturbs the logsum most. This is the **necessary-not-sufficient**
signal: the integral converges on existing nodes for the bulk, but the low-ESS tail
remains exposed and is exactly what the (BLOCKED) full draw-growth gate and the
(BLOCKED) `V_i^dir` cross-check are meant to vet. The subsample probe does **not**
clear Gate 1 part (i); it characterises what clearing it must resolve.

---

## Status summary

| Item | Status |
|---|---|
| `V_i^dir` redraw machinery (`ĝ` draw + analytic EV) | **BUILT** (no estimator source edited) |
| EUROMOD package available | yes (v0.2.17) |
| EUROMOD-on-nodes feasible without wholesale rebuild | **NO** (17/18 input vars absent) |
| `V_i^dir` values / `\|V_dir − V_IS\|` | **BLOCKED** (HH: 2243 / 2764 / 1285) |
| escalated set | **∅** (trigger cannot fire) |
| multiplier 2×/4× growth | **BLOCKED** (new nodes need new `c_is`) |
| existing-node subsample stability | **RUNS** (median converges; low-ESS max tail persists) |
| Gate 1 part (i) draw-growth | **still BLOCKED** (subsample is necessary-not-sufficient) |

---

## What unblocks this (for Increment Two — not performed here)

Both blocked items share **one** root cause: **disposable income at redrawn /
additional nodes**. To clear them, the bounded EUROMOD-on-nodes touch must be built:
construct EUROMOD input records for the redrawn `(w,h)` nodes (the full input schema,
hours/wage overwritten) and evaluate them at the **same 2016-real price basis and
EUROMOD system year as the build** — **not** a wholesale re-deflation (`ĝ` wages are
already 2016-real), **not** a wholesale data rebuild, **not** silent interpolation.
With `c_is` available at redrawn nodes:
1. `V_i^dir` computes on the full singles samples and the flagged couples subset →
   `|V_i^dir − V_i^IS|` distributions and the escalation decision per household.
2. The 2×/4× multiplier growth computes (additional `ĝ` nodes with their `c_is`) →
   the full draw-growth stability gate.

Only after both clear is W^3 promotable from validation artifact to result (separate
authorisation). This increment does not promote it.

---

## Commands run

```text
.venv\Scripts\python.exe scripts/welfare/run_stage2_vdir.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --out-json outputs/welfare/stage1_w3/stage2_vdir_results.json
```

Provenance: `outputs/welfare/stage1_w3/stage2_vdir_results.json`. Resolved config
unchanged (`scripts/welfare/configs/welfare_stage1_w3.yaml`); this increment reads
the same Stage-One config (the `core.integration` controls already declare
`ess_threshold`, `draw_multipliers`, `cross_check_on_flagged`).

## Explicit scope statement

No W^3 welfare finding is produced. No measure beyond W^3 is touched. The `V_i^dir`
cross-check and the full draw-growth stability remain BLOCKED on the bounded
EUROMOD-on-nodes touch (Increment Two); they are reported BLOCKED with exact
household counts, never approximated.
