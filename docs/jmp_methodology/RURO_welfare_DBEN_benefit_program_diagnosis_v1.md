# D-BEN — Program-level decomposition of the Two-L / F3 benefit wobble

**Read-only forensic.** No welfare, no decomposition, no V_i, no estimation, no EUROMOD
SYSTEM edits, no fix applied, no promotion, no commit. One report + one diagnostic parquet.

**Primary deliverables (the prompt's "one report + one diagnostic parquet"):**

- This report: `docs/jmp_methodology/RURO_welfare_DBEN_benefit_program_diagnosis_v1.md`
- Per-node × program parquet: `outputs/welfare/fastlane/diag_dben_program_attribution_v1.parquet`
  — **9,600 rows × 17 columns** (300 nodes = 3 anchors × 100 draws, × 32 tracked variables
  in the `program` row dimension: 17 benefit programs + 5 aggregates + 10 accumulators).
  Self-describing: each row carries `is_benmt_program` / `is_aggregate` / `is_accumulator`
  so downstream code must filter on `is_benmt_program` for benefit attribution.

**Retained provenance (a deliberate scope addition beyond the literal "one + one"):**

- Diagnostic script: `scripts/welfare/fastlane/run_dben_program_attribution.py`
- Summary JSON: `outputs/welfare/fastlane/diag_dben_program_attribution_v1_summary.json`
  (Task-0/closure/program-summary in machine-readable form). Kept for reproducibility;
  remove if strict one-report-one-parquet scope is required.

- Source finding this opens up: F3-R2/F3-R2B (`outputs/welfare/fastlane/f3r2b_diagnosis_v1.json`),
  memory `project_f3r2_joint_batch_not_licensed`.

---

## TASK 0 — Reproduction of the failing contrast (exact)

**The two batch constructions compared** (cited from source, both run on the same full
2016 singles band = 1,676 HHs × 100 draws + draw-0 = 169,276 rows; system `FR_2015`,
dataset `FR_2016_a3`):

| Batch | Construction | Code | Role |
|-------|--------------|------|------|
| **A — target-only** | Full 169,276-row band; **only the target HH's** decider rows overwritten with its 100 counterfactual nodes; **all other 1,675 HHs left at their original staged state**. | `run_f3r2_reconcile_joint_parity.py::_price_target_hh_full_em` (one run per anchor; frozen to `fastlane_anchors_v3/*_priced_v3.parquet`). Gate A (F3-R2B) proved re-run == frozen at max_abs = 0, so the frozen file *is* the faithful target-only run. | production geometry / "stored" |
| **B — joint-batch** | Same 169,276-row band; **all 1,676 HHs** simultaneously overwritten with their own counterfactual redraws. | rebuilt here deterministically (`BASE_SEED=20260604`, frozen anchor RNG, F3-R2B FIXED `yem = yem00+yemxp`). | alternative composition |

The anchor's **own** input rows are byte-identical between A and B (F3-R2B Gate B,
max_abs = 0 — re-confirmed: the redraw is seeded identically and uses the frozen anchor
nodes). The **only** difference between A and B is the state of the *other* 1,675
households' rows.

**Reproduction result — `ils_ben` divergence on the same anchors/draws F3 flagged:**

| Anchor | uid | `ils_ben` max\|diff\| (EUR) | nodes > tol | F3-R2/F3-R2B value | match |
|--------|-----|--------:|:--:|--------:|:--:|
| primary           | 200001593700 | **127.274966** | 1 / 100 | 127.275 | ✔ exact |
| top_ess_sm_2016   | 200003504101 | **158.757862** | 1 / 100 | 158.758 | ✔ exact |
| top_ess_sf_2016   | 200003672000 | **309.762031** | 1 / 100 | 309.762 | ✔ exact |

Reproduced to the micro-EUR. The contrast is valid; the diagnostic proceeds.

> Note already visible here: the divergence is **concentrated at exactly one draw per
> household** (1 of 100), not spread across the node set — it strikes a single
> RSA-eligibility margin.

---

## TASK 1 — Per-program attribution of the divergence

Across all 300 flagged nodes (3 anchors × 100 draws), opening `ils_ben` → `ils_benmt`
→ component programs. Tolerance 1e-6 EUR.

### Ranked per-program contribution to the EUR 127–310

| Rank | Program | Scheme | max\|diff\| (EUR) | median\|diff\| | nodes>tol | share of `ils_ben` div |
|---:|---------|--------|--------:|--------:|:--:|:--:|
| 1 | **`bsa00_s`** | **RSA** (revenu de solidarité active) | **309.762** | 0.000 | 3 | **100 %** |
| — | all other `ils_benmt` programs | PAJE/CF/AF/ARS/AAH/ASS/AL/ASPA/PPE/… | 0.000 | 0.000 | 0 | 0 % |

`bsa00_s` (RSA) carries the **entire** wobble at all three anchors: 127.275 / 158.758 /
309.762 EUR. Every other means-tested component is flat to 0.000.

**Closure check (per node, all 3 anchors):**

| Anchor | Σ(program diffs) − `ils_benmt` diff | `ils_benmt` diff − `ils_ben` diff | `ils_bennt` \|diff\| | `ils_pen` \|diff\| |
|--------|:--:|:--:|:--:|:--:|
| primary         | 1.4e-14 | 0.0 | **0.0** | **0.0** |
| top_ess_sm_2016 | 0.0     | 0.0 | **0.0** | **0.0** |
| top_ess_sf_2016 | 0.0     | 0.0 | **0.0** | **0.0** |

The single moving program (`bsa00_s`) reconstructs the full `ils_benmt` and `ils_ben`
divergence to machine precision. **`ils_bennt` (non-means-tested benefits) and `ils_pen`
(pensions) do not move** — as expected. The chain `bsa00_s → ils_benmt → ils_ben →
ils_dispy → ils_b1_bsa → ils_b2_bsaho → ils_udb_bsa → ils_udb_yds` all carry the identical
127/158/310 EUR (they are all downstream sums containing RSA).

### Mechanism conduits (not benefits — the cross-household carriers)

Two EUROMOD intermediate accumulators diverge at **population scale** at *every* node
(300/300), orders of magnitude above any single-household quantity:

| Conduit | max\|diff\| | what it is |
|---------|--------:|------------|
| `i_bsa00_cumpers_nw` | 4.11e8 | RSA cumulative **non-worker** eligible person-count, summed over the **whole batch** |
| `i_bsa00_cumpers_w`  | 1.70e8 | RSA cumulative **worker** eligible person-count, summed over the **whole batch** |

These are not benefit amounts; they are the channel by which other households' rows reach
the target's RSA (see Task 3).

---

## TASK 2 — Classification of each program

Classifier cross (per spec): within-draw variation in a **faithful** run (does the program
respond to *this* household's earnings across the 100 draws?) × batch-sensitivity (does it
move between A and B?).

| Program | Scheme | within-draw varies? | batch-sensitive? | **classification** |
|---------|--------|:--:|:--:|---|
| `bsa00_s` | **RSA** | **yes** (std ≈ 106–171 EUR; active in 67/300 nodes; max 526 EUR) | **yes** (≤309.76) | **INCOME-DRIVEN** |
| `tinrf_s` | **PPE** (in-work transfer) | yes (active 109/300; tracks earnings) | **no** (0.000) | income-driven but **batch-robust → inert** |
| `bch00_s` AF, `bchyc_s` PAJE, `bchlg_s` CF, `bchba_s` PN, `bched_s` ARS | family/child (demographic) | n/a — **structurally 0** for this singles population | no (0.000) | **inert** |
| `bdi_s` AAH, `bunmt_s` ASS, `bhotn_s` AL, `bsaoa_s` ASPA, `bsuwd_s`, `bch*_s` other | disability / unemployment / housing / old-age | structurally 0 here | no (0.000) | **inert** |

**Only one program is both income-linked and batch-sensitive: `bsa00_s` (RSA).** It is
correctly classified **INCOME-DRIVEN** — RSA is the means-tested income floor; it
legitimately varies with the draw's earnings (the std ≈ 171 EUR across draws in the
faithful target-only run is the *real* consumption-floor response we must preserve).

**No program is classified DEMOGRAPHIC-ARTIFACT.** The family/demographic lines that the
prompt flagged as artifact-suspects (PAJE, CF, AF, PN, ARS) are **structurally zero** for
these single, childless anchor households — there is no demographic benefit present to be
perturbed, so none moves.

**Control that proves specificity — PPE (`tinrf_s`):** PPE is an income-tested in-work
transfer (active in 109/300 nodes, varies with earnings) yet its batch diff is **exactly
0.000**. An income-driven, means-tested benefit that does **not** leak across batch
composition. This proves the leakage is **specific to the RSA accumulator
implementation**, not a generic property of means-tested benefits.

---

## TASK 3 — Within- vs cross-household dependence (the precision the fix turns on)

Only `bsa00_s` (RSA) moves, so the question is whether *its* batch-sensitivity is
within-household (real, must be preserved) or cross-household (the Two-L pathology).

**Verdict: 100 % CROSS-household leakage.** Three independent pieces of evidence:

1. **The anchor's own inputs are byte-identical between A and B** (Gate B, max_abs = 0).
   The target HH's members, ages, disability flags, *and* its earnings/hours/wage at every
   one of the 100 nodes are the same in both batches. Its within-household RSA means-test
   therefore receives identical own-household inputs in A and B. Any difference in its RSA
   output cannot come from within the household.

2. **The only thing that differs between A and B is the other 1,675 households' rows**
   (A holds them at original state; B redraws them all). Therefore the entire 127–310 EUR
   is, by construction, attributable to other households.

3. **The conduit is explicitly a cross-household population accumulator.** At the flagged
   nodes, `i_bsa00_cumpers_nw` is ~1.8e8 in A vs ~2.0e7 in B; `i_bsa00_cumpers_w` is
   ~5e4 in A vs ~6.8e7 in B. A single household's own RSA-eligible person count cannot be
   ~10^8 — that number is a cumulative sum over **the entire input file**. The FR RSA
   add-on references these whole-batch counters; changing who else is in the batch shifts
   them, which nudges the target's RSA across an eligibility/amount margin (the direction
   even flips: +127 / +159 at primary / sm, but −310 at sf — pure margin perturbation).

The **within-household** income response of RSA (the means-tested floor reacting to the
draw's wage) is **real and is preserved identically in both A and B** — it is *not* the
source of the wobble and must not be touched by any fix.

---

## TASK 4 — Fix-option readout (analysis only; nothing implemented)

| Option | Supported by findings? | Reason |
|--------|:--:|--------|
| **A** — faithful full pre-filtration population run | partial | Divergence *is* income-driven, so a faithfully-composed population gives the correct RSA *baseline*. But a single all-actual run yields no per-node counterfactual welfare; it fixes the reference, not the 100-draw node set. |
| **B** — per-household isolated full run (target counterfactual, rest at actual) | **YES — gold standard** | This **is** batch-A. It holds the other 1,675 HHs at their true observed state, so the RSA accumulator reflects the correct population — the partial-equilibrium counterfactual we want. It is already the certified production method; it eliminates the wobble by construction. Cost: 1,676 EUROMOD runs vs 1 (one ~35–40 s pass each). |
| **C** — freeze specific programs to data-level | **NO** | Legal *only* for DEMOGRAPHIC-ARTIFACT + CROSS programs. **The freeze-legal list is empty.** The sole mover (RSA) is INCOME-DRIVEN; freezing it would delete the means-tested response to the counterfactual wage — the consumption-floor mechanism welfare is built on. |
| measure-and-tolerate | **NO** | Magnitude is not negligible (next paragraph). |

**Freeze-legal programs:** *none.*
**Freeze-illegal programs:** `bsa00_s` (RSA) — and by inheritance every downstream sum
(`ils_benmt`, `ils_ben`, `ils_dispy`, `ils_b1_bsa`, `ils_b2_bsaho`, `ils_udb_bsa`,
`ils_udb_yds`).

**Magnitude context** (NOT a welfare computation) — the divergence as a fraction of the
affected node's `ils_dispy`:

| Anchor | flagged draw | \|diff\| (EUR) | node `ils_dispy` | **diff / dispy** |
|--------|:--:|--------:|--------:|:--:|
| primary         | 40 | 127.27 | 932.58 | **13.6 %** |
| top_ess_sm_2016 | 1  | 158.76 | 859.05 | **18.5 %** |
| top_ess_sf_2016 | 83 | 309.76 | 816.14 | **38.0 %** |

At the affected (RSA-eligible) node the wobble is **13.6 %–38.0 % of disposable income** —
large. It hits only 1 of 100 nodes per household, but at that node it is first-order, so
*measure-and-tolerate is not advisable*.

---

## Final readout

**Ranked per-program contribution to the EUR 127–310:**
1. `bsa00_s` (RSA) — **100 %** (127.275 / 158.758 / 309.762 EUR; closes `ils_benmt`/`ils_ben` to ≤1.4e-14).
2. every other `ils_benmt` program — 0 %.
   (Cross-household conduits, not benefits: `i_bsa00_cumpers_nw` ~4.1e8, `i_bsa00_cumpers_w` ~1.7e8.)

**Each moving program classified:**
- `bsa00_s` (RSA) — **INCOME-DRIVEN.**
- `tinrf_s` (PPE) — income-driven but **batch-robust → inert** (control).
- PAJE / CF / AF / PN / ARS / AAH / ASS / AL / ASPA — **inert** (structurally zero for the singles population; no DEMOGRAPHIC-ARTIFACT mover exists).

**WITHIN vs CROSS per moving program:**
- `bsa00_s` (RSA): batch-sensitivity is **100 % CROSS-household** (anchor inputs byte-identical between A and B; sole difference is other HHs; conduit is the whole-batch `i_bsa00_cumpers_nw/w` population counters). Its within-household income response is real and preserved in both batches — not the source of the wobble.

**Freeze-legal programs:** none.
**Freeze-illegal programs:** `bsa00_s` (RSA) + its downstream sums.

**PRIMARY DRIVER OF THE WOBBLE: income-driven** — the sole mover is RSA, an income-driven
program; it diverges through a **cross-household batch-accumulator leakage** channel. Not
demographic-artifact, not mixed.

**RECOMMENDED PATH: B** (per-household isolated full run = target-only; already the certified
production method, eliminates the wobble by construction; cost = 1,676 EUROMOD runs).
Option A is acceptable only for the population baseline, not the per-node counterfactuals.
**Option C is rejected** (freeze-legal list empty; RSA is income-driven). Measure-and-tolerate
rejected (≤38 % of `ils_dispy` at the affected node).

---

### Provenance
- Joint-batch EUROMOD: 169,276 rows, `FR_2015` / `FR_2016_a3`, 39.9 s; redraw 18.7 s; total 64.4 s.
- Target-only (batch-A): frozen `fastlane_anchors_v3/*_priced_v3.parquet` (F3-R2A/B, Gate A deterministic).
- Tolerance 1e-6 EUR (batch-sensitivity & within-draw variation). 3 anchors × 100 draws × {17 programs + 5 aggregates + 10 accumulators} in the parquet.
- No EUROMOD system files touched; no commit; immutable F3/F3-R2 artifacts not overwritten.
