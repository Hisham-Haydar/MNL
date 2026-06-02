# RURO Welfare — Stage Two, Increment Two-D: node-pricing re-simulation feasibility probe

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-D only — bounded node-pricing EUROMOD
re-simulation **feasibility probe** on existing nodes.
**Status:** a **materially different** candidate path was defined, built, and tested.
**Existing-node parity still FAILS on all six year×mode cells** (roster-complete
inputs); the materially-different mechanism (full household roster) was **necessary
but not sufficient**. Per the Task-5 fail rule, this reports the failed cells and
diagnosis and goes no further.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched. No
> production redrawn-node pricing was run; no V_i^dir computed; no 2×/4× growth; no
> storage/precompute/priced parquet written.** EUROMOD was run only on tiny
> existing-node subsets (5 HH × ≤20 draws per cell). Not committed automatically.

---

## 1. Preflight — is there a materially different candidate, and what is the mechanism?

**Two-B path (the one that failed):** `_reprice_cell` in `welfare_vdir.py` reads its
EUROMOD input rows from the **priced** file and selects a tiny subset with
`groupby(stacked_hh_uid).head(rows_per_hh)`.

**The bpool rows are a household ROSTER.** Direct inspection of
`precompute__2016__singles__long.parquet` (and the priced file) shows the unique key
is `(stacked_hh_uid, draw, idperson)` — each `(stacked_hh_uid, draw)` carries **every
household member** (decider + children + partner), one row per `idperson`. E.g. HH
`200001495800` at draw 0 has **3 persons** (`ruro_decider`: 1 for the age-51 decider,
0 for an age-18 and an age-11 child).

**The concrete, testable input difference (Task 1 mechanism).** `head(20)` slices by
**row count**, so for a 3-person household it can cut a draw's roster mid-way: it
keeps draws 0–5 complete (18 rows) plus the decider and **one** child of draw 6 — and
**drops the second child** (which would be row 20). EUROMOD then computes that draw
against a **2-person** household instead of 3, so household-level means-tested
benefits (child benefits, housing AL, RSA) are wrong → `ils_ben` diverges. **Direct
evidence:** of the 8 Two-B failing rows, exactly the **2 roster-truncated** cells
(`495800` draw 6, `502500` draw 6) are among the failures.

**The Two-D candidate** is therefore materially different in two concrete, testable
ways: (a) EUROMOD input is built from **precompute-long** (the build's own EUROMOD
**input** source) rather than the priced **output** file; (b) selection is
**roster-complete** — for the chosen households it takes **all `idperson` rows** for a
bounded set of draws, so every `(hh, draw)` fed to EUROMOD has its **full roster**. It
keeps the build's node-dependent earnings fields as stored in precompute-long and
feeds EUROMOD only `raw_schema` input columns (never `*_s`/`ils_*`/tax-benefit outputs
as inputs). This is a real candidate (not "no new route"), so the probe proceeds.

**But the mechanism only covers 2 of 8 Two-B failures.** The other 6 Two-B failures
had **complete** rosters in the subset yet still failed — so roster completeness was
expected to be necessary, not obviously sufficient. The probe tests it empirically.

---

## 2-3. Existing-node parity probe — result: **FAIL on all six cells**

Tiny deterministic subset (5 HH, ≤20 draws/cell, **roster-complete** confirmed),
EUROMOD input from precompute-long, compared on **decider** rows against the stored
priced values; couples also report household-joint disposable income.

| cell | roster complete | `ils_dispy` max abs | rows>tol | `ils_ben` max | `ils_ben` bad | `ils_origy` max | couples JOINT max (bad) | status | failure localised to |
|---|---|---|---|---|---|---|---|---|---|
| 2015 singles | ✅ | 512.01 | 17 | 512.01 | 17 | 0.00 | — | **FAIL** | **ils_ben** |
| 2015 couples | ✅ | 2003.74 | 12 | 535.31 | 8 | 3622.03 (10) | 2678.87 (7) | **FAIL** | **ils_origy** |
| 2016 singles | ✅ | 601.73 | 11 | 601.73 | 11 | 0.00 | — | **FAIL** | **ils_ben** |
| 2016 couples | ✅ | 2345.01 | 17 | 463.08 | 12 | 4350.75 (10) | 3620.16 (12) | **FAIL** | **ils_origy** |
| 2017 singles | ✅ | 676.47 | 15 | 676.47 | 15 | 0.00 | — | **FAIL** | **ils_ben** |
| 2017 couples | ✅ | 2141.26 | 19 | 796.96 | 14 | 3642.84 (10) | 2944.85 (13) | **FAIL** | **ils_origy** |

(Failure localisation is over true components only — `ils_origy`/`ils_ben`/`ils_tax`/
`ils_sicdy` — never the aggregate `ils_dispy`. For all three singles cells the gap is
in `ils_ben` with `ils_origy = ils_sicdy = 0` and `ils_tax ≈ 0`.)

**Two findings, both adverse:**

1. **Singles: still benefit-localised, and no better than Two-B.** With complete
   rosters, `ils_origy` reproduces to machine zero (as in Two-B) but `ils_ben` still
   fails (11–17 rows/cell, max up to 676). So the full-roster mechanism did **not**
   fix the singles benefit divergence — it removed the 2 truncation-caused failures
   but the residual benefit gap remains. Roster completeness is **necessary but not
   sufficient**.

2. **Couples: a NEW `ils_origy` divergence appears.** Reading couples from
   precompute-long makes even **original income** diverge (max ~2000–2345), which it
   did **not** in Two-B (couples origy was machine-zero there). So the precompute-long
   couples path is **not even income-faithful** — it is strictly worse than Two-B for
   couples.

**EUROMOD warning evidence (observed signal — persisted, NOT a proven root cause).**
The probe's EUROMOD runs emit `TUDef_fr/DefTu: more than one possible partner found
for assessment unit` warnings for the stamped roster persons. This evidence is now
captured reproducibly at the runner level (a process fd-1/fd-2 redirect around the
grid; the native EUROMOD engine writes these to the process console on fd 1, which a
per-cell in-Python fd-2 redirect missed): **48 TUDef partner-ambiguity warning lines**
in a representative run, across **8 distinct assessment units** —
`tu_household_fr`, `tu_fiscalunit_fr`, `tu_bsa00_fr`, `tu_bunmt_couple`, `tu_bch_fr`,
`tu_bch_extra_fr`, `tu_bchlg_fr`, `tu_bho_fr`. The full log is persisted at
`outputs/welfare/stage1_w3/stage2_resim_euromod_console.log` and the count + units +
a sample are in the provenance JSON
(`assessment_unit_warning_evidence`).

**What this does and does not establish.** It is a **plausible candidate mechanism**:
the per-draw `_stamp_draw_ids` transformation, applied to a multi-person roster, can
make EUROMOD unable to resolve a unique partner/assessment unit for some households,
which would feed household means-tested benefits (and, for couples, income
aggregation) a malformed unit. But this increment does **not prove** that these
warnings *fully* account for the `ils_ben` (singles) and `ils_origy` (couples) parity
gaps — the warnings are an **observed, persisted signal**, not a demonstrated cause.
Establishing causation (e.g. by a stamping scheme that eliminates the warnings and
re-checking parity) is a separate task, not performed here.

**Conclusion of the probe.** The materially-different candidate was genuinely tested
(roster-complete inputs from precompute-long) and **still fails every cell**. The
singles failure remains benefit-localised (`ils_ben`); the couples failure is now
income-localised (`ils_origy`, strictly worse than Two-B). The full-roster fix is
necessary but not sufficient. A candidate (not proven) contributor is the
stamped-roster ↔ EUROMOD assessment-unit ambiguity (48 persisted TUDef warnings),
on top of the Two-C benefit-state node-dependence.

---

## 4. Throughput probe

Measured on the tiny probe (existing-node EUROMOD runs):

| quantity | value |
|---|---|
| total EUROMOD wall time (6 cells) | **20.19 s** |
| total EUROMOD input rows priced | 1,345 |
| approx seconds per input row | **0.0150** |
| avg roster rows per node | 1.45 |
| designed cross-check households | 6,292 (singles 2243 + 2764, flagged couples 1285) |

**Production projection** (designed cross-check, per-node = one full-roster
household-draw):

| nodes/HH | approx EUROMOD input rows | approx wall time |
|---|---|---|
| 100 | ~0.91 M | **~3.8 h** |
| 300 | ~2.73 M | **~11.4 h** |
| 900 | ~8.19 M | **~34.1 h** |

**Assumptions / basis (stated, tractability NOT declared).** The per-input-row figure
is a wall-time **basis** from a 6-run probe; it does **not** include EUROMOD batch
overhead, model load, or process spin-up, so each projection is a **lower bound** on
per-node cost. No configured tractability threshold exists in the repo, so per the
Task-4 rule this is reported as a **projection only** — tractability is **not
declared**. (And it is moot here: the path does not pass parity, so its throughput is
not on the critical path.)

---

## 5. Verdict (Task-5 fail branch)

**Existing-node parity FAILS on all six cells**, so the per-node re-simulation route
is **NOT opened**. STOP. Failing cells, components, and localisation are tabulated in
§2-3:
- failing cells: **all six** (2015/2016/2017 × singles/couples);
- singles failures: **still benefit-localised** (`ils_ben`), max up to 676/cell, even
  with complete rosters;
- couples failures: now **`ils_origy`-localised** (the precompute-long couples path is
  strictly worse than Two-B);
- candidate (observed, NOT proven) contributor beyond Two-C: **per-draw ID stamping
  appears to produce ambiguous EUROMOD assessment units on a full roster** — 48
  persisted TUDef partner-ambiguity warnings across 8 assessment units
  (`assessment_unit_warning_evidence` in the JSON; full console log persisted). Whether
  these warnings fully explain the parity gaps is not proven here.

No redrawn-node pricing or V_i^dir was performed under this outcome (or any).
Production redrawn-node pricing and production V_i^dir remain **BLOCKED**.

This **narrows** the design space for any future increment: a per-node EUROMOD pricing
path must additionally solve the **stamped-roster ↔ assessment-unit** problem (a
stamping/tax-unit-keying scheme that EUROMOD resolves unambiguously for multi-person
households and couples), not merely keep rosters complete — and it must clear an
all-cells existing-node parity gate (`ils_dispy` and `ils_ben`, plus couples joint) to
machine tolerance before any redrawn node is priced. That is a separate, authorised
design+implementation increment, not performed here.

---

## Files

- **Feasibility-only source:** `scripts/welfare/welfare_resim_probe.py` (precompute-long
  roster-complete candidate + parity + throughput), `scripts/welfare/run_stage2_resim.py`
  (runner). No estimator/build source edited; no parquet written.
- **Config:** `scripts/welfare/configs/welfare_stage1_w3.yaml` (+`stage2.resim` block).
- **Provenance:** `outputs/welfare/stage1_w3/stage2_resim_results.json` (per-cell
  parity + component decomposition + couples joint + throughput projection +
  `assessment_unit_warning_evidence`: TUDef count, distinct units, sample).
- **EUROMOD console log:** `outputs/welfare/stage1_w3/stage2_resim_euromod_console.log`
  (the persisted process-console capture; 48 TUDef partner-ambiguity warning lines).

## Commands

```text
.venv\Scripts\python.exe scripts/welfare/run_stage2_resim.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --out-json outputs/welfare/stage1_w3/stage2_resim_results.json
```

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. No production
redrawn-node pricing was run, no V_i^dir computed, no 2×/4× growth run, and no
storage/precompute/priced parquet written. The Two-D path **is** materially different
from the failed Two-B path (precompute-long source + roster-complete selection). Its
existing-node parity **FAILS** on all cells (singles benefit-localised in `ils_ben`;
couples income-localised in `ils_origy`; a candidate, observed-not-proven contributor
is the stamped-roster ↔ EUROMOD assessment-unit ambiguity — 48 persisted TUDef
warnings). Throughput projection: ~3.8 h / ~11.4 h / ~34.1 h at 100 / 300 / 900
nodes/HH (lower bound; tractability not declared). Production redrawn-node pricing and
V_i^dir remain BLOCKED pending a separate authorised increment that also resolves the
assessment-unit problem and passes an all-cells parity gate.
