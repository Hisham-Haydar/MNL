# RURO Welfare — Stage Two, Increment Two-B: EUROMOD reprice parity diagnosis

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-B only — diagnose and (if justified) close the
EUROMOD reprice parity gap from `RURO_welfare_stage2_vdir_crosscheck_v2.md`.
**Status:** Parity **FAILS on every production year×mode cell**, with a single,
consistent **STRUCTURAL** root cause now identified: the divergence is **localised
entirely to `ils_ben` (benefits) on benefit-recipient households**. Original income
(`ils_origy`) and social contributions (`ils_sicdy`) reproduce to **machine zero**.
**No reprice-path repair is justified** by the diagnosis (the path is already
faithful for the income components; the build-faithful path was *not* closer), so
**node pricing stays BLOCKED** and no production V_i^dir is computed.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched.** No
> production redrawn-node pricing, no production V_i^dir, no 2×/4× multiplier growth.
> Not committed automatically.

---

## 1. Diagnosis of the failing rows (done BEFORE any reprice change)

Reproduced the v2 smoke exactly (2016 singles, first 5 households, ≤20 rows each =
100 rows, from the priced row-group-0), id-stamped via the build's `_stamp_draw_ids`,
fed through the build's `EuromodRunner` with the build's raw schema + system pairing.
8/100 rows exceed tolerance, max abs diff 422.35 — **reproducing the v2 result.**

**Concentration.** The 8 failures are scattered across **4 of the 5 households**
(496401×3, 502500×3, 495800×1, 504300×1), at assorted draws (3, 5, 6, 6, 6, 13, 15,
17). Not one household, not one draw.

**The decisive decomposition — which component of `ils_dispy` diverges.** EUROMOD
disposable income = `ils_origy − ils_tax − ils_sicdy + ils_ben`. Decomposing the
divergence per component on the 100-row smoke:

| component | n rows above tol | max abs diff (failing rows) | max abs diff (passing rows) |
|---|---|---|---|
| `ils_origy` (original income) | **0** | **0.000** | 0.000 |
| `ils_sicdy` (social contributions) | **0** | **0.000** | 0.000 |
| `ils_tax` (taxes) | 2 | 1.196 | 0.000 |
| **`ils_ben` (benefits)** | **8** | **422.350** | 0.000 |
| `ils_dispy` (net) | 8 | 422.350 | 0.000 |

**The divergence is benefit-driven.** `ils_origy` and `ils_sicdy` reproduce to
machine zero; the `ils_ben` divergence (max 422.35) is the entire `ils_dispy`
divergence; `ils_tax` moves only as a second-order consequence (≤1.2).

**All 8 failing rows are benefit recipients.** Stored `ils_ben ≠ 0` for **8/8**
failing rows. The 92 passing rows have zero benefit divergence.

**Distinguishing covariates (failing vs passing).** Failing rows differ
systematically on labour-history / annual income inputs that feed means-tested and
history-dependent benefits: `lunmy` (months unemployed: 1.5 vs 0.13), `liwmy`/
`liwftmy` (months in work: 12 vs 8.6), `lindi`, `yem`/`yemxp` (employment income
history), `yiy`, `xpp` (pensions). These are the populations whose benefits depend on
state EUROMOD computes from the household/annual context.

**Ruled-out hypotheses (each tested, not assumed):**
- *ID collision* — `idhh` is **globally unique** within the single-year priced file
  (0 reused across `stacked_hh_uid`); the 5 smoke households have distinct `idhh`.
- *Dropped household roster* — failing households have **no kinship links**
  (`idfather=idmother=idpartner=0`); they are genuine singles, no roster to drop.
- *Input-column feedback* — **no** `_RAW_SCHEMA` input column is an EUROMOD output
  (the output prefixes carry underscores, e.g. `bho_`, that the schema names do not
  match); benefit-input columns are **identical** between priced and precompute-long
  for the failing rows.
- *EUROMOD non-determinism* — feeding the **same** `em_input` twice gives **0**
  difference; EUROMOD is deterministic, so the gap is not RNG.
- *Reprice-path source* — reading from `priced` reproduces `ils_origy` **exactly**;
  the build-faithful path (reading from **precompute-long**, full-population draw
  band, build stamping) was strictly **WORSE** (7918/19160 bad, and even `ils_origy`
  then diverged), because the precompute-long input columns differ from those that
  produced the stored priced output. So the priced-row reprice path is the *more*
  faithful source, and the residual gap is **not** an "omitted preprocessing step."

The per-row diagnostic table is persisted at
`outputs/welfare/stage1_w3/stage2_parity_smoke_rows_diag.csv`. It contains the **FULL
smoke sample (all 100 rows, not only the failures)** for the reference cell
(2016 singles): row IDs, household ID, draw, stored/repriced `ils_dispy`, abs diff,
the per-component abs diffs (`ils_ben`/`ils_tax`/...), stored `ils_ben`, and a `FAIL`
flag (`FAIL == absdiff_ils_dispy > tol`). Filter `FAIL == True` for the 8 failing
rows.

## 2. Classification — **STRUCTURAL**

The evidence supports **STRUCTURAL**, not UNIFORM, not "remaining chunk-runner
preprocessing":

- It is **not UNIFORM**: an omitted preprocessing step affecting all rows would move
  `ils_origy`/`ils_sicdy` too, and would not localise to benefit recipients. Here
  income reproduces to machine zero and only benefit recipients fail.
- It **is STRUCTURAL**: a benefit-recipient / household-state-specific failure of the
  template-overwrite reprice. EUROMOD deterministically computes a **different
  benefit** for these specific recipient-households than the stored value, **given
  identical inputs** — meaning the stored `ils_ben` encodes household/annual state
  (means-test bases, prior-period or uprated benefit inputs) that the per-draw
  stamped row does not carry, and that the build established at original pricing time
  in a way the bounded reprice cannot reconstruct from the row alone.
- It is **explicitly NOT "remaining chunk-runner preprocessing"** — the prompt's
  caution. The build-faithful chunk path was tested and is *worse*, so no missing
  build step explains it.

## 3. Repair — none justified

Per "implement only the minimal repair justified by the diagnosis": the diagnosis
shows the income side of the reprice path is already faithful (machine-zero on
`ils_origy`/`ils_sicdy`), and **no path change tested closes the benefit gap** (the
build-faithful path is worse; inputs are already correct and unaltered; EUROMOD is
deterministic). Changing the reprice path further would be unjustified guessing.
**No repair is made.** The step-by-step path audit (row subset, `_stamp_draw_ids`,
schema selection, numeric coercion/fill, ID/kinship fields, row order, output
alignment, nominal-`ils_dispy` comparison, CPI handling) found the path
build-consistent for everything except the structural benefit state — which is not a
path field.

## 4. Parity grid — all production year×mode cells

Deterministic reprice (5 HH × ≤20 rows per cell), id-stamped, nominal `ils_dispy`
(not `ils_dispy_real`), with component decomposition; couples additionally report
household-joint summed disposable income at the alternative level.

| cell | n rows / HH / alts | `ils_dispy` max abs | median | rows>tol | `ils_ben` max | `ils_origy` max | couples JOINT max (bad/alts) | status | class |
|---|---|---|---|---|---|---|---|---|---|
| 2015 singles | 100 / 5 | 512.01 | 0.00 | 17 | 512.01 | **0.00** | — | **FAIL** | STRUCTURAL |
| 2015 couples | 100 / 5 | 346.69 | 0.00 | 3 | 346.69 | **0.00** | 346.69 (3/32) | **FAIL** | STRUCTURAL |
| 2016 singles | 100 / 5 | 422.35 | 0.00 | 8 | 422.35 | **0.00** | — | **FAIL** | STRUCTURAL |
| 2016 couples | 100 / 5 | 230.00 | 0.00 | 4 | 185.54 | **0.00** | 230.00 (4/32) | **FAIL** | STRUCTURAL |
| 2017 singles | 100 / 5 | 345.18 | 0.00 | 13 | 345.18 | **0.00** | — | **FAIL** | STRUCTURAL |
| 2017 couples | 100 / 5 | 266.78 | 0.00 | 7 | 266.78 | **0.00** | 266.78 (7/34) | **FAIL** | STRUCTURAL |

**All six cells FAIL with the identical signature**: median 0.00, a minority of rows
above tolerance, divergence localised to `ils_ben` (`ils_origy` machine-zero
everywhere). For couples the household-**joint** disposable income — the budget
couples welfare consumes — fails identically (the joint max equals the benefit
divergence), so the structural benefit gap propagates to the joint budget. The
failure is systematic across all years and both modes.

Provenance: `outputs/welfare/stage1_w3/stage2_parity_results.json` (full per-cell
component decomposition + couples joint parity).

## 5. Consequence

Parity **FAILS on every cell** ⇒ the template-overwrite EUROMOD path is **not
trustworthy** for benefit-recipient households ⇒ **node pricing stays BLOCKED**, and
no redrawn node is priced against it. Therefore `V_i^dir` and the 2×/4× growth remain
BLOCKED, and **W^3 stays a validation artifact, not a welfare finding.**

The structural cause is now precise (benefit-state non-reconstructibility from the
per-draw row), replacing the v2 hypothesis ("remaining chunk-runner preprocessing"),
which this increment **tested and rejected**. Closing the gap is no longer a
path-faithfulness task; it requires either (a) recovering the stored per-row
benefit-state inputs the build used (so benefits reprice exactly), or (b) a design
decision to price redrawn nodes with a benefit model whose state is reconstructible
from the node — both of which are design questions for a separate increment, not a
mechanical repair, and neither is performed here.

## Agnosticism

The Stage-Two welfare source hardcodes no country/year/case constant: stems, years,
modes, tolerances, and smoke/grid sizes come from config (`welfare.stage2`); the
EUROMOD system pairing, CPI(φ), input schema, `_stamp_draw_ids`, and `EuromodRunner`
are reused from the build module; **country is derived from the EUROMOD system-code
prefix** (`FR_2015` → `FR`) with an optional config override
(`parity_grid.country_override`, default null). Verified: no `country="FR"`, no year
map, no case stems in `welfare_vdir.py` / `run_stage2_parity.py`.

## Files

- **Source:** `scripts/welfare/welfare_vdir.py` (+`parity_grid` / `_reprice_cell`
  with component decomposition + couples joint parity),
  `scripts/welfare/run_stage2_parity.py` (grid runner).
- **Config:** `scripts/welfare/configs/welfare_stage1_w3.yaml` (+`stage2.parity_grid`
  block).
- **Diagnostic table:** `outputs/welfare/stage1_w3/stage2_parity_smoke_rows_diag.csv`
  (FULL smoke sample for the reference cell; `FAIL` column flags the failing rows).
- **Provenance:** `outputs/welfare/stage1_w3/stage2_parity_results.json`.

## Commands

```text
.venv\Scripts\python.exe scripts/welfare/run_stage2_parity.py \
  --config scripts/welfare/configs/welfare_stage1_w3.yaml \
  --out-json outputs/welfare/stage1_w3/stage2_parity_results.json
```

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. Parity FAILS
on all year×mode cells (STRUCTURAL, benefit-localised); per the increment's stop
rule, this reports the failed cells and the diagnosis and goes no further — no
production redrawn-node pricing and no production V_i^dir, which require separate
authorisation and first a resolution of the structural benefit-state gap.
