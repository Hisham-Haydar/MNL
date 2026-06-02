# RURO Welfare — Stage Two, Increment Two-E: assessment-unit / ID-stamping diagnosis

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-E only — bounded diagnostic isolating EUROMOD
assessment-unit / ID-stamping artefacts from the structural benefit-state question.
**Status:** complete. **Verdict (split by case): SINGLES — current stamping is NOT
the binding artefact; existing-node state is sufficient and reproduces cleanly.
COUPLES — clean-household repricing of the *collision-affected* nodes still fails,
because the STORED couples values for nodes that share a `draw_joint` were themselves
produced under the production `_stamp_draw_ids` collision.** Production redrawn-node
pricing and `V_i^dir` remain **BLOCKED**.

> **No W^3 welfare finding is produced and no measure beyond W^3 is touched.** This
> increment priced no production/redrawn node, computed no `V_i^dir`, ran no 2×/4×
> growth, and wrote no storage/precompute/priced/chunk parquet. EUROMOD was run only
> on tiny existing-node diagnostic subsets. Not committed automatically.

---

## 1. What this increment tests, and the two structural facts it rests on

Two-D showed that the materially-different roster-complete precompute-long path still
failed existing-node parity on all six cells (singles → `ils_ben`; couples →
`ils_origy`), with 48 persisted TUDef partner/assessment-unit warnings treated as
*observed signal, not proven cause*. This increment runs a clean-isolation ladder to
decide whether that failure is driven by the **ID-stamping / batched-presentation**
of multiple draws to EUROMOD, or by **irrecoverable benefit state**.

Two facts, established by direct schema/row inspection of the precompute-long and
priced-long parquets (recorded in the provenance JSON), shape the whole ladder:

1. **Singles node key = `(stacked_hh_uid, draw)`.** Each `(hh, draw)` is one clean
   roster — distinct `idperson` per row, no within-node ID collision. The production
   stamp `idperson*1000 + draw` is **unique per node** (verified: 6 nodes → 6 distinct
   stamped ids). Singles therefore *cannot* fail for a "two persons share a stamped
   idperson" reason.

2. **Couples node key = `(stacked_hh_uid, draw_joint, draw_male, draw_female)`, NOT
   `draw_joint` alone.** A single `draw_joint` can pack **more than one** labour-supply
   alternative — distinct `(draw_male, draw_female)` combinations stacked in the same
   block, each copy carrying the **same `idperson`** but **different earnings**. For
   the diagnosed household, `draw_joint=0` packs two alternatives `(0,0,0)` and
   `(0,1,1)`. The production stamp `idperson*10000 + draw_joint` keys on `draw_joint`,
   so **both alternatives of `draw_joint=0` receive the SAME stamped idperson** → an
   in-batch collision → EUROMOD's TUDef "more than one possible partner". (Across this
   household's 900 `draw_joint` values the stacking is rare — mean 1.0 alternatives
   per `draw_joint`, ~0.1 % carry >1 — but where it occurs it collides.) **Two-D
   selected couples on `draw_joint` only and fed those stacked, colliding alternatives
   to EUROMOD together**; this increment uses the correct 4-tuple node key so a single
   node is one clean 4-person roster (verified: 4 rows, 4 distinct `idperson`).

**Selected cases** (deterministic, from Two-D failing cells, 2016 / policy FR_2015):

| case | mode | `stacked_hh_uid` | structure | why selected |
|---|---|---|---|---|
| `singles_benefit_recipient` | singles | 200001495800 | 3-person roster: decider age 51 + dependent children 11 & 18 | benefit recipient with a dependent child; stored decider `ils_ben` varies 392→1351 across draws (node-dependent benefit); Two-D `ils_ben` parity failure |
| `couples_partner_structure` | couples | 200001483000 | 2 adults (41, 55) + 2 children (4, 7); reciprocal `idpartner` | Two-D `ils_origy` / joint-disposable parity failure; TUDef-relevant partner structure; `draw_joint=0` packs 2 stacked alternatives |

Parity target: stored **priced-long** value for the same node on **decider** rows,
**nominal** (no CPI/φ). EUROMOD input is built from **precompute-long**, raw-schema
columns only; no `*_s` / `ils_*` / tax-benefit outputs are fed back as inputs.

---

## 2. The ladder, per rung, per case

Per-rung TUDef warning counts and component parity (max abs diff; rows above
tol = 1e-6). Full per-node detail in the provenance JSON.

### 2.1 Singles — HH 200001495800 (node key `(stacked_hh_uid, draw)`)

| rung | presentation | TUDef | `ils_origy` | `ils_ben` | `ils_tax` | `ils_sicdy` | status |
|---|---|---|---|---|---|---|---|
| **1** single node, original IDs | 1 node, no stamping | **0** | 0.0 | **0.0** | 0.0 | 0.0 | **PASS** |
| **2** 6 nodes, separate one-node calls | original IDs | **0** | 0.0 | **0.0** | 0.0 | 0.0 | **PASS (6/6)** |
| **3** 6 nodes, one batch, `_stamp_draw_ids` | production stamping | **0** | 0.0 | **0.0** | 0.0 | 0.0 | **PASS** |

Stamping-collision evidence: 6 distinct nodes → **6 distinct stamped ids, 0
collisions**. Every rung reproduces the stored value to machine zero, including
node-dependent `ils_ben`, with **zero** TUDef warnings even in the production stamped
batch.

### 2.2 Couples — HH 200001483000 (node key `(stacked_hh_uid, draw_joint, draw_male, draw_female)`)

| rung | presentation | TUDef | `ils_origy` | `ils_ben` | `ils_tax` | joint dispy | status |
|---|---|---|---|---|---|---|---|
| **1** single node `(0,0,0)`, original IDs | 1 node, no stamping | **0** | 0.0 | **333.08** (1 row) | 197.88 (2 rows) | 133.53 | **FAIL** |
| **2** 6 nodes, separate one-node calls | original IDs | **0** | 0.0 | **first to diverge** | — | — | **FAIL (4/6 pass)** |
| **3** 6 nodes, one batch, `_stamp_draw_ids` | production stamping | **8** | 0.0 | 0.0 | 0.0 | 0.0 | **PASS** |

Rung 2 per-node: the only two failures are exactly the two alternatives that **share
`draw_joint=0`** — `(0,0,0)` and `(0,1,1)`. The four nodes whose `draw_joint` is a
singleton (`(1,1,2)`, `(2,1,3)`, `(3,1,4)`, `(4,1,5)`) **all PASS** to machine zero.
Stamping-collision evidence: 6 distinct nodes → **5 distinct stamped ids, 1
collision** (the `draw_joint=0` pair). Rung 3's 8 TUDef warnings span the assessment
units `tu_bsa00_fr, tu_bch_fr, tu_bch_extra_fr, tu_bchlg_fr, tu_bho_fr,
tu_bunmt_couple, tu_fiscalunit_fr, tu_household_fr` (persisted in JSON).

`ils_origy` and `ils_sicdy` reproduce to **machine zero** in every couples rung —
income and contributions reprice faithfully; only `ils_ben` / `ils_tax` (and hence
`ils_dispy`) diverge, and only on the collision-affected nodes.

---

## 3. The couples paradox, resolved (the central finding)

Rung 1 runs node `(0,0,0)` **clean and alone**, with original IDs and **zero** TUDef
warnings — yet it **fails** parity (`ils_ben` off by 333.08). Rung 3 batches the same
node under production stamping, **fires 8 TUDef collision warnings**, and **passes**.
A clean run failing while a collision-warning run passes is the opposite of the naïve
expectation. The mechanism (verified row-by-row in the JSON and by direct inspection):

- Under production `_stamp_draw_ids`, the stamp is `idperson*10000 + draw_joint`. Both
  alternatives of `draw_joint=0` — `(0,0,0)` and `(0,1,1)` — collapse to the **same
  stamped `idperson`** (`1483000010000`, `1483000020000`: 2 ids for 4 decider rows).
  EUROMOD then sees two people each claiming the same partner → the TUDef warnings →
  and prices the two alternatives against a **merged/ambiguous assessment unit**.
- The **stored priced value the build wrote for node `(0,0,0)` is precisely that
  collided result.** Rung 3 reproduces the build's stamping exactly, so it reproduces
  the collided value and "passes."
- Rung 1 prices node `(0,0,0)` as a **clean, isolated household** — the *correct*
  tax-benefit computation for that single labour-supply alternative — and gets a
  **different** `ils_ben`. It "fails" because it disagrees with a **contaminated**
  stored target.

So for couples the binding artefact is the **`draw_joint`-keyed stamping collision**:
where two alternatives share a `draw_joint`, the production build priced them under an
ambiguous assessment unit, and the **stored couples value for those nodes is itself an
artefact of that collision**. Rung-3 "parity" against such a target passes only by
**reproducing the build's bug**, not by being correct. This is a stronger and more
consequential result than "stamping is the artefact": it means existing-node couples
parity on collision-affected nodes is contaminated at the *stored-target* level.

---

## 4. Verdict

**Per the increment's verdict rules:**

- **Singles — current-stamping artefact: ruled OUT.** Rung 1 passes warning-free, Rung
  2 passes 6/6, and the production stamped batch (Rung 3) also passes with zero TUDef
  warnings. Existing-node state — including node-dependent `ils_ben` — is **sufficient
  and reproduces cleanly** for singles. The stamping convention is harmless here
  because the singles node key (`draw`) makes stamped ids unique. (This narrows Two-D's
  singles `ils_ben` failure to its `draw_joint`-free path: with the correct clean
  per-node presentation, singles `ils_ben` reproduces exactly.)

- **Couples — clean-household failure on collision-affected nodes.** Rung 1 fails
  **warning-free** on `ils_ben` for a single clean household-draw, so the failure is
  **not merely multi-draw stamping** of an otherwise-correct target. The deeper cause
  (§3) is that the **stored** couples value for nodes sharing a `draw_joint` was
  produced under the `_stamp_draw_ids` collision; the clean run correctly differs from
  that contaminated target. Nodes with a singleton `draw_joint` reprice to machine zero
  (4/6 here), so the contamination is **localised to the rare stacked-alternative
  `draw_joint` values**, not to couples generally.

**Narrowing of Two-C (as the rules require, stated precisely):** existing-node state is
sufficient when EUROMOD sees **clean household units** — demonstrated for singles (all
rungs) and for couples on **singleton-`draw_joint` nodes** (Rung 2: 4/6). Two-C's
broader "benefits are node-dependent simulated state" verdict is unchanged for
*redrawn* nodes. What Two-E adds: the existing-node *parity failures* observed in Two-D
are **presentation/keying artefacts**, not evidence that existing benefit state is
irrecoverable — for singles entirely, and for couples except where the production
`draw_joint` stamping collided and contaminated the stored target.

**Production remains BLOCKED.** No rung result unblocks production. Redrawn-node pricing
still requires a **separately authorised per-node EUROMOD path** AND a
**parity-passing batching/keying scheme** that stamps on the **full node key**
(couples: include `draw_male`, `draw_female`) so no two distinct alternatives ever
share a stamped `idperson`. Additionally, because the **stored** couples values for
collision-affected `draw_joint` nodes are themselves contaminated, any future couples
work must **not** treat the current stored couples baseline on those nodes as ground
truth without re-pricing them under a collision-free key.

---

## 5. Rung 4 (relationship-preserving alternative keying) — not triggered

Rung 4 runs only when Rungs 1 **and** 2 PASS and Rung 3 FAILS (i.e. when the *only*
problem is the stamped batch). Observed:

- Singles: r1=PASS, r2=PASS, r3=PASS → **SKIPPED** (nothing for Rung 4 to fix).
- Couples: r1=FAIL, r2=FAIL, r3=PASS → **SKIPPED** (Rungs 1–2 do not pass, so an
  alternative keying scheme is not the isolated remedy; the stored target itself is
  contaminated). A relationship-preserving node-offset keying scheme **is implemented**
  in the runner (`_rung4_alt_keying`, diagnostic only, remaps `idpartner`/`idfather`/
  `idmother` consistently and STOPs if any kinship reference is unresolved against the
  node roster) but is **not exercised** under these results, by the gate.

---

## 6. Files

- **Diagnostic source:** `scripts/welfare/welfare_assessment_unit_diag.py`
  (ladder + fd-level TUDef capture + parity compare),
  `scripts/welfare/run_stage2_assessment_unit_diag.py` (runner + collision evidence).
- **Config block:** `welfare.stage2.assessment_unit_diag` in
  `scripts/welfare/configs/welfare_stage1_w3.yaml` (cases, year, tol, components).
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_assessment_unit_diag.json`
  (per-rung component parity, per-rung TUDef counts/units/sample lines, per-node detail,
  stamping-collision evidence, per-case verdict).

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. EUROMOD was
run only on tiny **existing-node** diagnostic subsets; **no production/redrawn node
was priced**, no `V_i^dir` computed, no 2×/4× growth run, and no
storage/precompute/priced/chunk parquet written. Production redrawn-node pricing and
production `V_i^dir` remain **BLOCKED** pending separate authorisation of a per-node
EUROMOD pricing path and a parity-passing, collision-free batching/keying scheme.
