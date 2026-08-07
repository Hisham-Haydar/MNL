# FR P2a — M08 Stage-B Reprice-Parity Diagnosis Memo v1 (UNCOMMITTED)

**Mission:** JMP-M08, contract §1 (parity diagnosis), Stage B step 1–2.
**Scope discipline:** **READ-ONLY.** No code changed, no EUROMOD run, no node
redrawn, no node priced, no `V_i^dir`, no welfare number, no re-estimation, no
parquet written. The reproduction below was performed **against the stored
artifacts already on disk**, not by re-executing `run_stage2_parity.py`.
**Produced against:** MNL `520441a653f04196bf1e92e3658a478b4feb3718` (clean at
start of work); `dclaborsupply-monorepo` `27756a06ea189339aa82915ed2124628afed20eb`.
**Governing:** `Job_Market_paper docs/Missions/JMP_M08_singles_welfare_execution_contract_v1.md` §1;
charter §7 Stage B.

---

## 1. Diagnosis verdict

**The documented failure reproduces exactly — every number, every household,
every draw.** Nothing in the recorded signature is stale or wrong.

**Its classification is CONFIRMED as to localisation, REFUTED as to cause.**

| Claim in `RURO_welfare_stage2_parity_v1.md` | Verdict |
|---|---|
| Divergence localised entirely to `ils_ben`; `ils_origy`/`ils_sicdy` machine-zero | **CONFIRMED** (reproduced) |
| 8/100 rows over `1e-6`; `ils_ben` max 422.35; median 0.00 | **CONFIRMED** (reproduced to 10 dp) |
| Failure is not ID collision / roster / input feedback / non-determinism / omitted preprocessing | **CONFIRMED** — later increments re-tested and did not overturn any of the five |
| Classification "STRUCTURAL" | **PARTLY CONFIRMED** — a structural residual is real, but it is ~1/4 of the measured gap; the rest is instrument |
| **Suspected cause:** *"the stored `ils_ben` encodes household/annual state … that the per-draw stamped row does not carry"* | **REFUTED AS STATED, and REFINED** |
| Follow-up verdict (`…benefit_state_recoverability_v1.md`): `ils_ben` "does not reconstruct from stored standardized subtotals" | **REFUTED** — that test was run on columns a build bug left stale; it measures the bug, not benefit state |

**The refined cause.** Information is **not lost from the per-draw row.** The
gap is the sum of three distinct effects, all identified on disk after the
parity report was written, in descending order of contribution:

- **(A) Instrument defect — the harness batches 5 households.** FR means-tested
  benefits are **batch-context dependent**. `parity_grid.n_hh = 5` sits inside
  the regime where a bounded reprice is *known* to be unfaithful. Two-L's
  falsifiable ladder shows the same node returning `0.00` at 1/2/5 households
  and the **exact stored value** at 20/100. The harness measures its own batch
  size as much as the data.
- **(B) The channel — RSA (`bsa00_s`) via whole-batch population accumulators.**
  D-BEN attributes **100 %** of the batch-driven `ils_ben` divergence to one
  program, RSA, conducted through `i_bsa00_cumpers_nw` / `i_bsa00_cumpers_w`
  — cumulative eligible person-counts summed **over the entire input file**.
  Change who else is in the batch, and the target household's RSA moves across
  an eligibility margin. Direction is not signed: it flips.
- **(C) A genuine residual stored-target gap.** A faithful **full-production-
  chunk** rebuild (Two-N, 21/21 chunks, exact production granularity,
  deterministic, internally coherent) still fails to reproduce the stored
  headline on **2.04 %** of 2016-singles decider rows, max **€185.54**. This
  part is real, is not batch size, and is not explained by year/policy vintage,
  uprating, roster completeness, stamping, or chunking — all four were tested
  and rejected. It is a **build-vintage / EUROMOD-execution-state gap**.

**Separately: one piece of the original evidence base is invalid.** The
"`ils_ben` does not reconstruct from its stored subtotals" finding (259/808
rows, ±724) is an artefact of a build write-back bug — the chunk worker wrote
back only 5 headline columns per draw and left every simulated component as a
stale precompute carry-over. That bug was patched (Two-M) and the patch proven
headline-invariant to exactly 0.0. The reconstruction test therefore says
nothing about whether benefit state is recoverable.

**And a scope finding the contract does not currently carry.** The documented
failure was measured on `fr_p3a_bpool_priced__2016__singles.parquet` — the P3a
b-pool build. **The M08 baseline is not that artifact.** P2a region-live
consumption comes from a different, *committed*, hash-pinned pricing cache
(`MNL fr_singles_pricing_p2a/priced_*.parquet`, 8 chunks × 200 households) which
**is** component-coherent for RSA. Stage B must not assume the documented cell
is the M08 cell. See §3.6.

---

## 2. Reproduction — stored artifacts vs documented numbers

Read-only recomputation from `MNL outputs/welfare/stage1_w3/stage2_parity_smoke_rows_diag.csv`
(committed; the full 100-row smoke table for cell `2016__singles`) and
`…/stage2_parity_results.json` (committed).

### 2.1 Headline signature — exact match

| Quantity | Documented | Recomputed from stored artifact | Match |
|---|---|---|---|
| rows / households | 100 / 5 | 100 / 5 | ✔ |
| rows above tol (`1e-6` EUR) | 8 | 8 | ✔ |
| `ils_dispy` max abs diff | 422.35 | **422.3499969567** | ✔ |
| `ils_dispy` median abs diff | 0.00 | 0.0000000000 | ✔ |
| `ils_ben` max abs diff | 422.35 | **422.3499969567** | ✔ |
| `ils_origy` max abs diff | 0.00 | 0.0000000000 | ✔ |
| `ils_sicdy` max abs diff | 0.00 | 0.0000000000 | ✔ |
| `ils_tax` rows above tol / max | 2 / 1.196 | 2 / **1.1959078333** | ✔ |
| failing rows that are benefit recipients | 8/8 | 8/8 | ✔ |
| passing rows' benefit divergence | zero | max 0.0 over all 92 | ✔ |
| parity tolerance | `1.0e-6` EUR | `welfare_stage1_w3.yaml → stage2.parity_grid.tol = 1e-06` | ✔ |

### 2.2 Concentration — exact match

Documented: *"496401×3, 502500×3, 495800×1, 504300×1 … at assorted draws (3, 5,
6, 6, 6, 13, 15, 17)."* Recomputed: identical, both the per-household counts and
the multiset of draws.

### 2.3 The eight failing rows in full

| `stacked_hh_uid` | draw | stored `ils_ben` | Δ`ils_ben` | Δ`ils_tax` | stored `ils_dispy` | repriced `ils_dispy` | sign |
|---|---|---|---|---|---|---|---|
| 200001495800 | 6 | 880.44 | 233.106 | 1.166 | 1895.81 | 1663.87 | − |
| 200001496401 | 6 | 422.35 | **422.350** | 0.000 | 518.82 | 96.47 | − |
| 200001496401 | 15 | 286.44 | 251.050 | 0.000 | 740.57 | 489.52 | − |
| 200001496401 | 17 | 80.56 | 22.989 | 0.000 | 1076.48 | 1053.49 | − |
| 200001502500 | 3 | 582.14 | 159.373 | 0.000 | 1711.16 | 1870.53 | **+** |
| 200001502500 | 5 | 857.10 | 185.212 | 0.000 | 1791.69 | 1606.47 | − |
| 200001502500 | 6 | 1111.84 | 174.069 | 1.196 | 1486.19 | 1313.32 | − |
| 200001504300 | 13 | 269.43 | 92.519 | 0.000 | 986.10 | 1078.62 | **+** |

### 2.4 Three facts the documented report did not state (refinements, not corrections)

1. **Benefit recipiency is necessary but far from sufficient.** **38 of 100**
   rows carry `stored_ils_ben ≠ 0`; **30 of those 38 reprice exactly** (max
   divergence 0.0). Only 8 fail. A generic "stored benefit state is
   unreconstructible" cause would not spare 79 % of recipients.
2. **The divergence is signed both ways** (2 of 8 reprice *higher* than stored).
   An omitted or lost benefit input produces a one-sided deficit. A perturbed
   eligibility margin produces exactly this: a coin-flip in direction.
3. **The magnitude is not proportional to the stored benefit.** Δ/stored ranges
   from 0.16 (HH 496401 draw 17) to 1.00 (HH 496401 draw 6). Not a scaling
   factor; a threshold effect.

All three are predictions of the batch-accumulator mechanism (§3.2) and
anti-predictions of the documented suspected cause.

---

## 3. Root cause — the reprice path end-to-end, with evidence

### 3.1 What the path actually does

`scripts/welfare/run_stage2_parity.py` → `welfare_vdir.parity_grid` →
`welfare_vdir._reprice_cell` (lines 404–528). Traced in full:

1. open `bpool_dir()/fr_p3a_bpool_priced__{year}__{mode}.parquet`; read
   **row-group 0 only** (line 430);
2. take the **first `n_hh = 5`** distinct `stacked_hh_uid`, then the first
   `rows_per_hh = 20` rows of each (lines 432–434) → 100 rows;
3. `bmod._stamp_draw_ids(...)` — the build's own stamping (line 443);
4. project onto the build's `_RAW_SCHEMA[year]` input columns (line 444),
   coerce numeric, `fillna(0.0)` (lines 445–446);
5. `EuromodRunner.run_on_dataframe(em, country, system_code, dataset_name)`
   (lines 448–450) — **one EUROMOD call on those 100 rows and nothing else**;
6. compare `sim["ils_dispy"]` and the four components to the stored values.

**Step 5 is the defect.** The stored value was produced by EUROMOD given a
*production chunk* — the whole 2016 singles band. The comparison value is
produced by EUROMOD given *five households*. The two runs are not the same
experiment, and for French means-tested benefits they are not even close.

`ils_origy` and `ils_sicdy` reproduce to machine zero precisely because they are
**row-local**: gross income and contributions depend only on the row's own
`(w, h)` and the household's own invariant inputs. `ils_ben` does not.

### 3.2 The channel is RSA, and it is a whole-batch accumulator

`RURO_welfare_DBEN_benefit_program_diagnosis_v1.md` (2026-06-16) opened
`ils_ben → ils_benmt →` component programs across 300 nodes under two batch
constructions that differ **only** in the state of other households' rows
(the target household's own EUROMOD input rows are byte-identical — Gate B,
`max_abs = 0`):

| Program | Scheme | max abs diff | share of `ils_ben` divergence |
|---|---|---|---|
| **`bsa00_s`** | **RSA** | **309.762 EUR** | **100 %** |
| every other `ils_benmt` program | PAJE/CF/AF/ARS/AAH/ASS/AL/ASPA/PPE/… | 0.000 | 0 % |

Closure to machine precision (Σ program diffs − `ils_benmt` diff ≤ 1.4e-14;
`ils_bennt` and `ils_pen` do not move at all). The conduits:

| Conduit | max abs diff | what it is |
|---|---|---|
| `i_bsa00_cumpers_nw` | 4.11e8 | RSA cumulative **non-worker** eligible person-count, summed over the **whole batch** |
| `i_bsa00_cumpers_w` | 1.70e8 | RSA cumulative **worker** eligible person-count, summed over the **whole batch** |

A single household's own eligible-person count cannot be ~10⁸. These are
file-level sums. D-BEN's verdict: the batch-sensitivity of RSA is **100 %
cross-household**; RSA's *within*-household response to the draw's earnings is
real, correct, and identical under both constructions.

**The specificity control is decisive.** PPE (`tinrf_s`) is *also* an
income-tested transfer, *also* active and earnings-varying (109/300 nodes), and
its batch diff is **exactly 0.000**. So this is not "means-tested benefits are
fragile." It is the RSA accumulator implementation specifically.

`F3-R2B` (2026-06-13) had already recorded the dispositive gate outcome:
`BATCH-CONTEXT DEPENDENCE: proven`, `JOINT BATCHING METHOD: not licensed`
(Gate B PASS, Gate A PASS, Gate C FAIL).

### 3.3 The instrument effect is quantified, and it is large

Two-L's falsifiable ladder (`RURO_welfare_stage2_cross_track_benefit_residual_diagnosis_v1.md`
§4), one failing node, same draw, batch size varied:

| households in batch | clean `ils_ben` |
|---|---|
| 1 (isolated) | 0.00 |
| 2 | 0.00 |
| 5 | 0.00 |
| **20** | **186.14 = stored ✓** |
| 100 | 186.14 = stored ✓ |

*"It does not depend on draws — the same HH's all-101-draws batch in isolation
still gives 0.00; it is population, not draw count."*

**The parity harness runs at `n_hh = 5`** — the last rung that returns 0.00.

The size of the instrument effect, for the same 2016-singles cell:

| Instrument | batch given to EUROMOD | rows over tol | `ils_ben` max abs |
|---|---|---|---|
| Two-B parity smoke (the documented failure) | **5 HH / 100 rows** | 8 / 100 = **8.0 %** | **422.35** |
| Two-N full-chunk rebuild (faithful production granularity) | full 2016 singles band, 21/21 chunks | 3,460 / 169,276 = **2.04 %** | **185.54** |

Restoring faithful batch context cuts the failure rate by ~4× and the worst-case
magnitude by ~2.3×. It does not reach zero.

*(Comparison caveat, stated honestly: these are different instruments over
different denominators — a 100-row reprice-from-priced-row vs a full rebuild
from precompute. The comparison bounds the instrument's contribution; it does
not decompose it exactly.)*

### 3.4 The residual gap is real and is NOT batch size

Two-N (`RURO_welfare_stage2_full_rebuild_validation_v1.md`) rebuilt **every**
production chunk under the patched worker at exact production granularity
(21/21 chunks, exact row counts, 2.17 h), and gated it:

| cell | decider rows | `ils_origy` bad | `ils_sicdy` bad | `ils_ben` bad (max) | verdict |
|---|---|---|---|---|---|
| 2016 singles | 169,276 | 0 | 0 | **3,460 (€185.54)** | FAIL |
| 2015 singles | 168,569 | 0 | 0 | 3,519 (€359.39) | FAIL |
| 2017 singles | 167,862 | 0 | 0 | 7,297 (€360) | FAIL |
| 2016 couples | 4,643,754 | 0 | 0 | 215,643 (€905) | FAIL |

The rebuild is **deterministic** (re-run reproduces to max abs 0.0) and
**internally coherent** (`ils_ben = ils_pen + ils_benmt + ils_bennt` and the
`ils_dispy` identity, **0 violations**, all six cells). Four candidate causes
were tested and rejected: policy-system/year vintage (no clean split — 2017 is
worst), uprating/CPI (ratio on failing rows median 0.71, std 0.28, range 0–0.92
— not a scalar), roster completeness (full 5-member roster present), and
stamping/chunking (byte-identical `_stamp_draw_ids`, same 6-band grid). The
`*.pre_wage_deflation.bak` backups are byte-identical to the current files, so
there is no silent input drift.

**Conclusion:** the stored production headline `ils_ben`/`ils_dispy` are not
reproducible from the current inputs by *any* faithful EUROMOD run. The residual
originates in the original production execution's EUROMOD state (model version,
dataset, or transient run condition) that the current repo + data do not
reconstruct. **This is the only part of the failure that is genuinely
structural, and it is ~2 % of rows at ≤€185.54 for the 2016 singles cell.**

### 3.5 Why the "benefit state is unreconstructible" evidence is invalid

The Two-C verdict rested on: *"`|ils_ben − (ils_pen+ils_benmt+ils_bennt)|` is
nonzero on 259/808 rows, up to ±724."*

Reproduced here, read-only, on the same four households in
`fr_p3a_bpool_priced__2016__singles.parquet` row-group 0:

```text
n_rows = 808   n_with_gap = 259   max_gap = 724.3314336377      <- exact match
ils_dispy identity max residual = 4.547e-13                     <- headline coherent
```

Now the columns themselves, same rows:

| HH | rows | distinct `ils_ben` across draws | distinct `bsa00_s` | `bsa00_s` max | distinct `ils_benmt` |
|---|---|---|---|---|---|
| 200001495800 | 303 | 67 | **1** | **0.00** | 3 |
| 200001496401 | 101 | 22 | **1** | **0.00** | 1 |
| 200001502500 | 303 | 81 | **1** | **0.00** | 2 |
| 200001504300 | 101 | 29 | **1** | **0.00** | 1 |

The headline `ils_ben` varies across draws (22–81 distinct values). Every
simulated component is frozen at a single value, and RSA is stored as
**identically zero** for all four failing households. That is exactly the
build defect Two-L found in code
(`scripts/bpool/run_bpool_euromod_chunk.py`, pre-patch lines 186–194):

```python
out_df = chunk_df.reset_index(drop=True).copy()        # starts as the PRECOMPUTE input
em_out_cols = [c for c in _EM_OUTPUT_COLS if c in sim_df.columns]   # only the 5 headline cols
for c in em_out_cols:
    out_df[c] = sim_df[c].values                       # overwrite ONLY these 5 per draw
```

with `_EM_OUTPUT_COLS = ["ils_dispy","ils_origy","ils_ben","ils_tax","ils_sicdy"]`.

So the 259/808 "reconstruction gap" is the distance between a **live** headline
and a **stale** set of components. It is a measurement of the write-back bug.
It carries no information about whether benefit state is recoverable — and
Two-C's sub-claim that *"two of the four HH have all-zero simulated benefits yet
still fail parity"* is the same artefact: their components are all-zero because
they were never written, not because those households receive nothing.

The bug was patched (Two-M) with the patch proven **headline-invariant to
exactly 0.0** on every headline column in all three validation cells, and the
identity violations went from 58–59 % (singles) to **0**.

### 3.6 Scope: the documented cell is not the M08 cell

| | Documented parity cell | M08 baseline |
|---|---|---|
| priced artifact | `EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__2016__singles.parquet` | `MNL fr_singles_pricing_p2a/priced_{00000…01400}.parquet` (**committed**, 8 files, SHA-256 pinned in `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`) |
| households | 1,676 (2016 singles band) | **1,555** |
| rows | 169,276 decider | 225,836 total / **157,055 decider** |
| EUROMOD batch composition | production chunks of the P3a build | **8 chunks × 200 households** (`chunk_grid: [0,200,…,1400]`) |
| persisted columns | 5 headline live + ~560 stale components | `[idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider, dgn, draw, ils_dispy, **bsa00_s**]` |
| RSA column state | **stale** (constant 0.00 at the failing HH) | **live** — 25.0 % of rows have `bsa00_s > 0`; **1,412 / 1,555 (90.8 %)** of households have RSA > 0 at some draw; within-household spread up to €1,590.56 |

Two consequences:

1. **The M08 baseline's own pricing cache already tracks `bsa00_s` explicitly
   and coherently.** Whoever froze the P2a pricing contract had already
   identified RSA as the material program. It is the one benefit column carried
   alongside `ils_dispy`.
2. **RSA is first-order for this population.** 90.8 % of P2a singles households
   are RSA-exposed at some node. Any repair that mishandles RSA batch context
   mishandles the welfare of nine tenths of the sample.

**Not established, and Stage B must not assume it:** whether the P2a pricing
cache carries the §3.4 residual gap. No parity test has ever been run against
it. The documented 8/100 result says nothing about it either way.

### 3.7 What the parity gate actually blocks for M08

Recorded because it bounds the cost of every route in §4. Under contract D1,
`V_i^IS` (importance sampling over **existing** draws) is the primary
estimator; `V_i^dir` (redraw) is a validation cross-check only. Reading the
committed P2a welfare runner (`scripts/welfare/run_p2a_singles_welfare.py`),
`W1/W3/W4/W6` are computed by **inversion in consumption space over the
existing 101-alternative draw set** — box-cox utility, bracketed root-find, no
EUROMOD call anywhere in the runner.

So the reprice-parity gate binds:

- **redrawn-node pricing** → `V_i^dir`, the U6/U7 cross-check, draw-growth;
- **any measure that would need a consumption value at an alternative outside
  the stored draw set**, if M08 chooses to build one that way.

It does **not** mechanically block the `V_i^IS` primary path or the existing
inversion-based measure family. That is an observation about blast radius, not
a request to relax the gate — the charter's gate wording stands.

---

## 4. Repair routes — enumerated, with what each preserves

Every route below is stated with what changes, what it preserves **bit-for-bit**,
what it cannot preserve, and the evidence for/against. **Nothing is implemented.**

### Route 1 — Fix the instrument: run parity at faithful batch scale

**What changes.** `parity_grid.n_hh` from 5 to the full production population,
and the comparison batch is composed identically to the batch that produced the
stored value (target household's counterfactual nodes overwritten; every other
household held at its actual observed state). This is D-BEN's **Option B**, the
"target-only" geometry, and it is *already the certified production method*
(F3-R2B Gate A: re-run == frozen at `max_abs = 0`).

**Preserves bit-for-bit.** Everything: no code path change to pricing, no data
change, no estimator input touched. Only the harness's batch is enlarged.

**Cannot preserve / cannot fix.** The §3.4 residual (~2 % of rows, ≤€185.54).
Route 1 removes (A) and (B); (C) survives it — Two-N *is* Route 1 at full scale
and still failed.

**Cost.** D-BEN's estimate for the target-only geometry: one EUROMOD pass per
household (~35–40 s each). For P2a singles that is 1,555 runs ≈ 15–17 h; the
Two-N full-band precedent ran 21 chunks in 2.17 h, so a chunked variant is far
cheaper but only reproduces chunk-level, not target-only, context.

**Evidence.** Strong. The ladder (§3.3), the program attribution (§3.2), and the
Gate-A determinism result all support it. It is the single highest-value change
and the cheapest to justify.

### Route 2 — Freeze the offending benefit component

**What changes.** Hold `bsa00_s` at its stored value across redrawn nodes.

**Preserves.** Batch reproducibility trivially.

**Cannot preserve.** The economics. **REJECTED on the record.** D-BEN Task 4:
the freeze-legal list is *empty*; `bsa00_s` is classified **INCOME-DRIVEN**, and
freezing it *"would delete the means-tested response to the counterfactual wage
— the consumption-floor mechanism welfare is built on."* With 90.8 % of P2a
singles households RSA-exposed (§3.6), this would bias exactly the households
the exercise is meant to value. **Do not pursue.**

### Route 3 — Measure and tolerate

**What changes.** Widen the parity tolerance to admit the residual, document the
bias.

**Preserves.** Everything; zero implementation.

**Cannot preserve.** Credibility at the affected nodes. **REJECTED on the
record.** D-BEN: at the affected node the divergence is **13.6 %–38.0 % of
`ils_dispy`**. It strikes ~1 node in 100 per household, but where it strikes it
is first-order. *"Measure-and-tolerate is not advisable."*

### Route 4 — Reconstruct the stored benefit state from the row

**What changes.** Join invariant state and recompute benefits without EUROMOD.

**Cannot preserve.** Correctness. **REJECTED** — but note the *reason* has moved.
Two-C rejected it on evidence now known to be invalid (§3.5). It still fails, on
better grounds: RSA depends on whole-batch accumulators (§3.2), which no
per-row join can supply, and the FR policy internals are not exposed by the repo.

### Route 5 — Close the residual: identify the production build vintage

**What changes.** Determine whether the stored priced files were built from a
different precompute/EUROMOD state than what is on disk now (Two-N's own
recommended next step), and either recover that vintage or accept that the
stored headline is the defective artifact.

**Preserves.** Nothing yet — it is an investigation, not a fix.

**Cannot preserve.** Possibly the certified estimate: Two-N is explicit that the
estimator is fit on the **stored** `ils_dispy_real`, and a corrected rebuild
moves it on benefit-recipient rows. That makes this a **re-estimation policy
question**, not an engineering task. It is squarely inside charter §11's halt
conditions.

**Note for M08 specifically.** This residual belongs to the *P3a b-pool* build.
Whether it exists in the **P2a** pricing cache is untested (§3.6). Route 5 may
be entirely out of M08's scope.

### Route 6 — Re-scope the gate to the M08 artifact

**What changes.** Run the parity gate against `fr_singles_pricing_p2a/priced_*.parquet`
— the artifact M08's consumption actually comes from — at faithful batch
composition (8 × 200-HH chunks, or target-only), instead of against a P3a cell
M08 does not consume.

**Preserves bit-for-bit.** All P2a stored values; nothing is rebuilt.

**Cannot preserve.** Nothing — but it may *reveal* a residual, in which case
Routes 1/5 apply to P2a too.

**Evidence.** The scope mismatch is documented in §3.6 and is not currently
recorded in the contract. Charter §7 Stage B says "reproduce the documented
failure on accepted existing nodes" — the documented failure has now been
reproduced (§2); binding the *gate* to the artifact M08 consumes is the natural
next move.

### Recommendation

**Route 6 first, then Route 1, then re-assess.** Concretely, and in order:

1. **Route 6 (cheap, read-only-adjacent, no design decision):** point the
   existing parity harness at the committed P2a pricing cache and run it with
   the batch composed as the P2a pricing run composed it (200-household chunks
   on the `chunk_grid`). This answers the only question that actually gates
   M08: *is the M08 baseline's own consumption reproducible?* No current
   evidence answers it.
2. **Route 1 (the correction the diagnosis supports):** whatever cell is
   gated, replace `n_hh = 5` with faithful batch context — target-only
   geometry per D-BEN Option B, which is already the certified production
   method and needs no new licence.
3. **Re-assess.** If Route 6 + Route 1 give an all-rows PASS on the P2a cache,
   the gate is met for M08 and redrawn-node pricing can be proposed on that
   basis. If a residual survives, it is the §3.4 class, Route 5 opens, and
   **that is a halt-and-escalate** under charter §11 ("reprice parity is
   structural/type-specific and unresolved" / "a generic package change is
   required"), not a Stage-B repair.

**Explicitly not recommended:** Routes 2, 3, 4 (rejected on the record above).

**Contract §2 note.** §2 says the correction must be "the smallest
production-path correction the diagnosis supports," and anticipates that if no
path change closes the gap the correction is one of two *design* paths. The
diagnosis now supports a third, smaller answer: **the largest single defect is
in the parity harness, not the production path.** Fixing the harness is smaller
than either design path and must be tried first.

---

## 5. What the correction must prove — the parity gate, restated

Binding, and unchanged in strictness from
`RURO_welfare_stage2_benefit_state_recoverability_v1.md` §6 and charter §7:

1. **Existing nodes only.** Re-run reprice parity on **existing** stored nodes
   through the corrected path. No redrawn node is priced until this passes.
2. **All rows, not a smoke.** Every decider row of the gated cell, not a 5-HH /
   100-row sample. The smoke's own failure mode was its size.
3. **Every cell the redraw path will touch.** For M08 that is at minimum
   FR-2016 singles on the P2a artifact; if the P3a cells are also touched,
   all of them, both modes, all three years.
4. **Tolerance `1.0e-6` EUR absolute** on `ils_dispy` (contract D10;
   `stage2.parity_grid.tol`). Not relaxed. Not re-derived.
5. **Component decomposition reported**, not just the headline: `ils_origy`,
   `ils_ben`, `ils_tax`, `ils_sicdy` — and, given §3.2, **`bsa00_s` explicitly**,
   plus `i_bsa00_cumpers_nw` / `i_bsa00_cumpers_w` as batch-context witnesses.
   A PASS whose RSA accumulators differ from production is not a PASS; it is a
   coincidence.
6. **Batch composition declared and reproducible.** The gate report must state
   exactly which households shared the EUROMOD batch, because the quantity being
   gated is batch-conditional. A parity number without a declared batch is not
   interpretable.
7. **Determinism check.** Re-run once; require `max_abs = 0.0` (the Two-N and
   F3-R2B Gate-A standard) before comparing to stored.
8. **Headline invariance.** The correction must not move `ils_dispy_real` /
   `c_norm` on any row — the certified estimate is fit on it (Two-M Gate A1
   standard: exactly `0.0`). If a candidate correction moves the estimator's
   consumption input, **STOP**: that is a re-estimation decision, not a parity
   repair.
9. **Only an all-cells, all-rows PASS unblocks pricing.** Partial passes,
   recipient-only exemptions, and tolerance widening are all excluded.

---

## 6. Immediate next action

1. **Goal 1 Manager accepts or rejects this memo** (contract §1.3 / charter §7
   Stage B step 2). No code may change before acceptance.
2. **Ruling required on the scope question (§3.6):** should the M08 parity gate
   bind the **P2a pricing cache** (`fr_singles_pricing_p2a/priced_*.parquet`,
   the artifact M08's consumption comes from) or the **P3a b-pool cell** the
   documented failure was measured on? This determines everything downstream and
   is not answerable from the contract as written.
3. **Contract corrections to carry into the Stage-A freeze** (all
   documentation-only; a currency note has been added at contract §1.3):
   - §1.2's *"the gap was never closed after 2026-06-03"* is superseded — four
     later increments bear on it (Two-L/M/N, F3-R2A/B, D-BEN).
   - §1.2's transcription of the suspected cause should be marked **refuted as
     stated**; the §3 refinement replaces it.
   - §1.2's citation of the Two-C "NOT FEASIBLE" verdict should be marked
     **evidence invalid** (§3.5) — the verdict may still be right, but not for
     the reason given.
   - §1.1's instruction to rerun `run_stage2_parity.py` "against the same
     2016-singles smoke" should be revisited: rerunning the 5-household smoke
     reproduces the instrument defect by construction.
4. **Then, and only then:** Route 6 → Route 1 as sequenced in §4.

**Nothing is authorised by this memo.** No redrawn node, no `V_i^dir`, no
paper-facing welfare number, no code change.

---

## Provenance — every artifact read

**Reproduced from (committed, MNL):**
`outputs/welfare/stage1_w3/stage2_parity_smoke_rows_diag.csv`;
`outputs/welfare/stage1_w3/stage2_parity_results.json`;
`outputs/welfare/stage1_w3/stage2_benefit_state_inventory.json`;
`outputs/welfare/stage1_w3/stage2_full_rebuild_validation.json`;
`fr_singles_pricing_p2a/priced_{00000,00200,00400,00600,00800,01000,01200,01400}.parquet`.

**Read (storage, not modified):**
`EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__2016__singles.parquet` (row-group 0).

**Code traced (read-only):**
`scripts/welfare/welfare_vdir.py` (`_reprice_cell` 404–528, `parity_grid` 531–558);
`scripts/welfare/run_stage2_parity.py`;
`scripts/welfare/run_p2a_singles_welfare.py`;
`scripts/welfare/configs/welfare_stage1_w3.yaml` (`stage2.parity_grid`);
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml` (`frozen_inputs.pricing_cache`);
`scripts/p2a/run_p2a_regionlive_rebuild.py` (pricing-cache gate 361–390).

**Reports relied on (MNL `docs/jmp_methodology/`):**
`RURO_welfare_stage2_parity_v1.md` (Two-B, 2026-06-02);
`RURO_welfare_stage2_benefit_state_recoverability_v1.md` (Two-C, 2026-06-02);
`RURO_welfare_stage2_singles_vdir_gate_v1.md` (Two-K, 2026-06-03);
`RURO_welfare_stage2_cross_track_benefit_residual_diagnosis_v1.md` (Two-L, 2026-06-03);
`RURO_welfare_stage2_chunk_writeback_fix_validation_v1.md` (Two-M, 2026-06-03);
`RURO_welfare_stage2_full_rebuild_validation_v1.md` (Two-N, 2026-06-03);
`RURO_welfare_F3R2A_repair_diagnosis_v1.md` + `RURO_welfare_F3R2B_gate_bc_v1.md` (2026-06-13);
`RURO_welfare_DBEN_benefit_program_diagnosis_v1.md` (2026-06-16).

## Explicit scope statement

No welfare finding is produced; no measure is computed; no `V_i^dir`; no redrawn
node priced; no EUROMOD run; nothing re-estimated; no source, config, or data
file modified; no parquet written. This memo is read-only diagnosis and a
recommendation. Uncommitted.
