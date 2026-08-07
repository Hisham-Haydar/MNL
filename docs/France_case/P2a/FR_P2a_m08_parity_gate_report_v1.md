# FR P2a — M08 Stage-B Reprice-Parity Gate Report v1 (UNCOMMITTED)

**Mission:** JMP-M08, contract §1–§2 (parity correction + gate), Stage B step 3.
**Authority:** Goal-1 ruling **R-60** (Route 6 → Route 1, ratified), applied to
`FR_P2a_m08_parity_diagnosis_memo_v1.md` §4.
**Scope discipline:** France 2016 singles **P2a cell only**. No production pricing
code changed. No redrawn node. No counterfactual covariate. No welfare number. No
couples, pooled years, or other cells. No stored consumption value modified,
replaced, or regenerated. EUROMOD executed **solely** for parity-validation
repricing.
**Produced against:** MNL `520441a653f04196bf1e92e3658a478b4feb3718` (tracked tree
clean; additions untracked); `dclaborsupply-monorepo`
`27756a06ea189339aa82915ed2124628afed20eb` (clean, `--untracked-files=all`).

---

## 0. Register pre-check (read-only, contract §3.2)

The four register entries named in the tasking were quoted verbatim from
`Job_Market_paper docs/Missions/JMP_M08_singles_welfare_execution_contract_v1.md`
§3.2 and assessed **against this gate only**. None was resolved.

> **Contract-location note.** The tasking cites the contract at
> `docs/missions/JMP_M08_…`. No such path exists in MNL; the document lives at
> `Job_Market_paper docs/Missions/JMP_M08_singles_welfare_execution_contract_v1.md`
> (DRAFT, uncommitted). That is the file quoted.

| # | R-59 status | Blocks this parity gate? |
|---|---|---|
| U3 — "up1 manifest note" | **ESCALATED** — R-59 gave no direction on U3; unchanged | **No.** No welfare-adjacent referent exists in any of the three repositories; the gate binds named, hash-pinned P2a pricing-cache manifests, not "up1". |
| U6 — draw-growth stability tolerance | **ESCALATED** — a data-creation decision, not a documentation gap; R-59 gave no direction; unchanged | **No.** U6 gates Stage-D integration certification (Gate 1(i)); no draw-multiplier dataset or redrawn node is touched by a reprice of stored nodes. |
| U10 — S-10 resolved numeric values | **Unchanged (pre-execution)** — the source artifact is now digest-bound under U1 | **No.** Stage-G scope; the gate perturbs no parameter and reads no θ. |
| U12 — common reference offer environment | **ESCALATED** — no on-disk candidate; remains blocking before Stage F | **No.** Explicitly Stage-F-blocking only; the register itself records it as non-blocking before then. |

**Pre-check verdict: no register entry blocks this gate.** Proceeded.

---

## 1. Gate definition

### 1.1 The correction, stated precisely

The diagnosis memo established two independent defects in the documented gate:
the harness measured the **wrong artifact** (§3.6 — a P3a b-pool cell M08 does not
consume) at the **wrong batch size** (§3.1/§3.3 — `n_hh = 5`, the last rung of
Two-L's ladder that returns `0.00`). R-60 ratified fixing both: Route 6 (re-scope
to the M08 artifact) then Route 1 (faithful batch context).

Both corrections live **entirely in the gate path**. Three new files were added;
**no existing file was modified**:

| File | Role |
|---|---|
| `scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml` | gate config (artifact binding, geometry, tolerance) |
| `scripts/welfare/m08_p2a_parity.py` | gate library (pin verification, path reconstruction, chunk reprice + compare) |
| `scripts/welfare/run_m08_p2a_parity_gate.py` | runner (`attempts/` transaction, chunk-sequential, intermediate persistence) |

`scripts/welfare/welfare_vdir.py` and `run_stage2_parity.py` are **untouched**, so
the documented 8/100 failure remains reproducible exactly as recorded. No
production pricing code, no production config, and no stored artifact was changed.
**No point in the work required a production-pricing-code change**, so the §1/§2
halt condition on that ground did not arise.

### 1.2 (a) Artifact bound — pins verified

The gate binds the committed, hash-pinned P2a pricing cache — the artifact M08's
consumption comes from. Pins are **not restated** in the gate config; they are read
from the committed production config
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml → frozen_inputs.pricing_cache`,
the G-0 single source of truth. **Every chunk was verified before comparison; all
8 match.**

| Chunk | Committed SHA-256 | Verified | Rows | HH | Draws |
|---|---|:--:|---:|---:|---:|
| `priced_00000.parquet` | `c35ed8b553f24bfa9e51bbdad6ec9aab609c8765e850afc5be8424fceb924d30` | ✔ | 29,492 | 200 | 101 |
| `priced_00200.parquet` | `f00923ac60705ca70ea53bb77127d3977e628dde8f2bc07de9805f7d732c912c` | ✔ | 29,593 | 200 | 101 |
| `priced_00400.parquet` | `d21fe881bdfe3768a3c7b6af729919bd2bde166b567c1f397865e0e2d44a42e6` | ✔ | 27,775 | 200 | 101 |
| `priced_00600.parquet` | `8a9153de01c033b85bd6fa4d40327f5311263a787288e3919f4163ca6ab0f87f` | ✔ | 30,704 | 200 | 101 |
| `priced_00800.parquet` | `d24e6d6db6c73288b800f4550f0075272bcbc01791734b4f245d6891cec4df8a` | ✔ | 28,583 | 200 | 101 |
| `priced_01000.parquet` | `184bae4430d4b248cbf73b93527b760db22afb146712078334c20a3a28f63cb5` | ✔ | 28,078 | 200 | 101 |
| `priced_01200.parquet` | `aef0b58678ff59e6512d2bcbee67766c3fe19135941b70605c24831875c53d83` | ✔ | 28,482 | 200 | 101 |
| `priced_01400.parquet` | `e89d73678f97a9468bffff965d068263e25ea2b8f16ef3556e33c0e585e9d63b` | ✔ | 23,129 | 155 | 101 |

Shape contract also verified: **225,836 rows total = declared**; **1,555
households = declared**; chunk grid `[0,200,…,1400]` as declared.

Upstream pinned inputs consumed by the reconstruction, verified in the same pass:

| Input | Committed SHA-256 | Verified |
|---|---|:--:|
| Raw FR microdata `FR_2016_a3.txt` | `da3eed570ff67cb06f9b0cef16bf9e7aa1d33ae579baff14a97f22c0f2c8bf88` | ✔ |
| GSUR lookup `FR_gsur_ruro_v2_stageA_y2015.parquet` | `f51ad6306574bf3a1d7b577e7741222c5bf2fb8126e512c0bbf965d6a2d03c83` | ✔ |
| Frozen draws geometry `fr_p2a_draws_geometry__singles.parquet` | `5bcf0e5409ef74c57f6de24efdfd24d0075132dc3138ddb57a22740b916cf235` | ✔ (parquet ↔ meta self-declaration) |

Gate-code identity (recorded in every attempt manifest):
config `029d5ee618576c9a91cc2374500e3d632912c52d637a1b4268c1db4796979e81`,
library `d79d05ae326276506bc950449af737da35042cac4d16e733963c1ae1b9856547`,
runner `1eea3cc7583811170426c12e2a44058d9145dac52eceb202c7f10ecda31423d8`.

### 1.3 (b) Geometry — target-only production batch (D-BEN Option B)

**What Option B means here.** D-BEN Option B is the *per-household isolated full
run*: the target carries the node being priced while **every other household is
held at its actual staged state** (D-BEN Task 4; = batch A, already the certified
production method, F3-R2B Gate A `max_abs = 0`). In a **parity** run the target
node *is* the stored node, so no household is displaced from its actual state and
Option B degenerates exactly onto the production batch that produced the stored
value. Target-only and full-chunk coincide **because nothing is redrawn** — that
equivalence holds only for parity and does not extend to counterfactual pricing.

**The batch actually executed**, reconstructed from the production pricing loop
(`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb`, code cells 2–34,
which is the loop that wrote the cache):

- `hh_all = sorted(single idhh)`; chunks of **200 source households** on the
  committed `chunk_grid`; final chunk 155.
- **One** `EuromodPricingRunner.price()` call per chunk,
  `alt_key_cols=['draw']`, `weeks_per_month = 13/3`.
- Each alternative replicated as an **isolated synthetic household**
  (`idhh = 900000000 + alt_idx`), all household members restored — **20,200
  synthetic households per full chunk**, 29,492 EUROMOD rows for chunk 0.
- EUROMOD `FR` / system `FR_2015` / dataset `FR_2016_a3`.
- Earnings mutation: the production `fr_earnings_policy_v2` (35 h `yem00`/`yemxp`
  split, working-zero and full-year columns), unchanged.

This is **not** `n_hh = 5`, not a row-group slice, and not an arbitrary batch. It
is the production batch, re-executed.

**Reconstruction fidelity, independently checked.** The rebuilt draw frame was
compared against the committed frozen geometry parquet on every pricing-relevant
column — `hours`, `wage`, `working`, `loc4`, `log_prior`, `is_chosen`,
`idhh_true`, `idperson_true`: **max abs diff 0.0 on every column**, 157,055 rows,
1,555 households. The notebook's execution guards (`RUN_PRICING`,
`EXPORT_PRODUCTION_GEOMETRY`) were asserted OFF and its dev-artifact root was
redirected out of the worktree, so the rebuild performed no EUROMOD call and no
production write.

**Batch composition declaration** (memo §5 item 6): for chunk starting at offset
`k`, the EUROMOD batch is exactly the households `sorted(single idhh)[k:k+200]`,
each at its actual staged state, across all 101 alternatives — and no other
household. Row order was additionally checked against the stored chunk and found
**identical**, so the RSA whole-batch accumulators
(`i_bsa00_cumpers_nw` / `i_bsa00_cumpers_w`) are reproduced by construction rather
than by coincidence.

### 1.4 (c) Comparison and tolerance

- **Tolerance:** `1.0e-6` EUR absolute — contract **D10** /
  `stage2.parity_grid.tol`. Not relaxed, not re-derived.
- **Gate column:** `ils_dispy`, per row. PASS requires **zero** rows above
  tolerance on **every** chunk.
- **Witness column:** `bsa00_s` (RSA), per row — the program D-BEN attributes
  **100 %** of the benefit divergence to, and the one benefit column the P2a cache
  persists live. Memo §5 item 5 requires it explicitly.
- **Join:** `(source_idhh, draw, source_idperson)`, `validate="one_to_one"`, with
  full row-set equality asserted before any statistic is computed.

**Decomposition — an honest constraint, stated rather than worked around.** The
pinned P2a cache persists exactly ten columns
(`idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider,
dgn, draw, ils_dispy, bsa00_s`). `ils_origy`, `ils_sicdy`, `ils_tax` and `ils_ben`
are **not stored**, so a stored-vs-repriced *difference* for those components does
not exist and cannot be manufactured. What the gate does instead: it captures all
four components **and** both RSA accumulators from the live repriced run and emits
them per **failing** row, so any divergence is localisable to a component even
though the stored side is silent. Both columns the artifact does persist are
compared at full row resolution. This is the maximum decomposition the bound
artifact supports; widening it would require regenerating the cache, which is out
of scope and forbidden by the tasking.

---

## 2. Smoke result (bounded)

**Geometry:** one chunk — `priced_00000`, offset 0, 200 households, 20,200
alternatives, 29,492 EUROMOD rows. Single EUROMOD call, 148.7 s.

| Quantity | Result |
|---|---|
| Rows compared | 29,492 |
| Row-set match (stored ↔ repriced) | exact |
| Row order identical to stored | **yes** |
| `ils_dispy` max abs diff | **0.000000000** |
| `ils_dispy` median abs diff | 0.000000000 |
| `ils_dispy` rows above `1e-6` | **0** |
| `bsa00_s` (RSA) max abs diff | **0.000000000** |
| `bsa00_s` rows above `1e-6` | **0** |
| EUROMOD hard errors | none (6 `uprate` notices only, as in production) |
| Components available on repriced side | `ils_origy`, `ils_sicdy`, `ils_tax`, `ils_ben` |
| Accumulators available | `i_bsa00_cumpers_nw`, `i_bsa00_cumpers_w` |

**Smoke verdict: PASS**, exactly — not "within tolerance".

RSA exposure in this chunk is representative, so the result is not vacuous:
**182 of 200 households (91.0 %)** have `bsa00_s > 0` at some draw and 23.7 % of
rows carry RSA — matching the memo's 90.8 % population figure. The channel that
carried 100 % of the documented divergence is live in the smoke and reproduces to
zero.

Artifact: `outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/
20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE/`.

---

## 3. Full-run result

**Complete run over the entire P2a 2016-singles cache — all 8 chunks, all
households, all 101 alternatives, all persons.** Chunk-sequential, one EUROMOD
call per chunk, manifest re-persisted after every chunk.

`2026-08-05T18:03:01Z → 18:22:10Z` (19 min 09 s wall; 1,126.9 s in EUROMOD).
No sampling, no truncation, no projected-cost stop: the full run was affordable
and was executed in full.

### 3.1 Per chunk

| Chunk | HH | Alternatives | Rows | `ils_dispy` max abs Δ | rows > 1e-6 | `bsa00_s` max abs Δ | rows > 1e-6 | Row order = stored | EUROMOD errors | Sec |
|---|---:|---:|---:|---:|---:|---:|---:|:--:|:--:|---:|
| `priced_00000` | 200 | 20,200 | 29,492 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 146.5 |
| `priced_00200` | 200 | 20,200 | 29,593 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 144.5 |
| `priced_00400` | 200 | 20,200 | 27,775 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 143.9 |
| `priced_00600` | 200 | 20,200 | 30,704 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 145.5 |
| `priced_00800` | 200 | 20,200 | 28,583 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 144.2 |
| `priced_01000` | 200 | 20,200 | 28,078 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 145.6 |
| `priced_01200` | 200 | 20,200 | 28,482 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 145.5 |
| `priced_01400` | 155 | 15,655 | 23,129 | **0.0** | **0** | **0.0** | **0** | ✔ | none | 111.2 |

Every chunk: row-set equality with the stored chunk asserted before any statistic;
`validate="one_to_one"` join on `(source_idhh, draw, source_idperson)`; row order
byte-for-byte identical to the stored ordering.

### 3.2 Aggregate

| Quantity | Value |
|---|---|
| Chunks run / on grid | **8 / 8** (full run) |
| Rows compared | **225,836** (= the entire pinned cache) |
| Households | **1,555** |
| Gate column | `ils_dispy` |
| Tolerance | `1.0e-6` EUR absolute (D10, unrelaxed) |
| **`ils_dispy` max abs diff, all rows** | **0.0** |
| **Rows above tolerance** | **0** |
| Failing chunks | **none** |
| `bsa00_s` (RSA) max abs diff | **0.0** |
| `bsa00_s` rows above tolerance | **0** |
| EUROMOD hard errors | **none** on any chunk (`uprate` notices only, as in production) |

No `failing_rows_*.csv` was emitted, because no row failed. All artifacts are MNL
outputs; nothing was written to `Job_Market_paper`.

### 3.3 Memo §5 checklist — what the correction was required to prove

| # | Requirement | Status |
|---|---|---|
| 1 | Existing nodes only, no redrawn node priced | **Met** — stored nodes repriced unchanged |
| 2 | All rows, not a smoke | **Met** — 225,836 / 225,836 rows |
| 3 | Every cell the redraw path will touch | **Met for the M08 baseline cell** (FR-2016 singles, P2a). P3a cells are not M08's consumption and were not gated — see §6 |
| 4 | Tolerance `1.0e-6` EUR, not relaxed | **Met** |
| 5 | Component decomposition reported, `bsa00_s` explicitly | **Met for every column the artifact stores** (`ils_dispy`, `bsa00_s`); `ils_origy`/`ils_sicdy`/`ils_tax`/`ils_ben` are not persisted by the cache so no stored-vs-repriced difference exists — captured live for failing rows, of which there were none (§1.4) |
| 6 | Batch composition declared and reproducible | **Met** — §1.3, declared per chunk and verified by identical row order |
| 7 | Determinism: re-run, require `max_abs = 0.0` | **Met** — `priced_00000` was priced twice (smoke 148.7 s, full 146.5 s) in two independent EUROMOD executions; both returned 0.0 against stored, hence 0.0 against each other |
| 8 | Headline invariance (`ils_dispy_real`/`c_norm` unmoved) | **Met, trivially and strictly** — the gate writes nothing to the cache, and the repriced headline equals the stored headline exactly, so no estimator input moves under any adoption of this result |
| 9 | Only an all-cells, all-rows PASS unblocks pricing | **Met for this cell**; see the §6 scope statement |

---

## 4. Verdict

## VERDICT: **PASS**

**Zero rows above `1.0e-6` EUR on every chunk. The maximum absolute divergence
across all 225,836 rows of the entire P2a 2016-singles pricing cache is exactly
`0.0` — on the gate column `ils_dispy` and on the RSA witness `bsa00_s` alike.**

This is not a pass "within tolerance". Repriced equals stored bit-for-bit, on
every row, in every chunk.

Evidence supporting the verdict, in the order it was established:

1. **The artifact is the right one and is authentic.** All 8 committed SHA-256
   pins verified before comparison; declared row/household counts matched
   (225,836 / 1,555); upstream raw microdata, GSUR lookup and frozen draws
   geometry pins all verified.
2. **The path is the production path.** The rebuilt draw frame reproduces the
   committed frozen geometry with max abs diff `0.0` on every pricing-relevant
   column; the pricing call, earnings policy, chunk grid, system and dataset are
   the production ones.
3. **The batch is the production batch.** Row order is identical to stored in all
   8 chunks, so the RSA whole-batch accumulators
   (`i_bsa00_cumpers_nw`/`i_bsa00_cumpers_w`) — the exact conduit D-BEN proved
   carries 100 % of the documented divergence — are reproduced by construction.
4. **The mechanism that broke the documented cell is live here and still passes.**
   RSA is not dormant in this population: 91.0 % of chunk-0 households carry
   `bsa00_s > 0` at some draw, 23.7 % of rows are RSA-positive, matching the
   memo's 90.8 % figure. The channel is fully exercised and reproduces to zero.
5. **Determinism holds** (§3.3 item 7).

---

## 5. Residual characterisation — the P2a cell does **not** carry the §3.4 residual

The diagnosis memo §3.6 recorded, as an explicit open question: *"Not established,
and Stage B must not assume it: whether the P2a pricing cache carries the §3.4
residual gap. No parity test has ever been run against it."*

**It is now established: it does not.** Zero rows, zero euros. The §3.4 residual
(2.04 % of 2016-singles decider rows, max €185.54) is a property of the **P3a
b-pool build**, not of the artifact M08 consumes.

Three independent, previously-recorded facts explain the difference, and each is
consistent with the PASS rather than being invoked to excuse it:

| # | P3a b-pool cell (documented failure) | P2a pricing cache (this gate) |
|---|---|---|
| 1 | **EUROMOD system drift.** Chunk `c0` created `2026-05-24T23:21:08Z`; `FR.xml` and `FR_DataConfig.xml` last modified `2026-05-26T09:30:39Z` — the system changed **35 h after** the build. F6-PRICE-B0 Task 2 traced the 3,460-row / €184.61 residual precisely to this and called it not fixable without rolling back the XML. | Cache priced **2026-07-12**, ~7 weeks **after** the same `2026-05-26T09:30:39Z` system files, whose mtimes were recorded in this run's manifest and are unchanged. **No system drift to absorb.** |
| 2 | **Batch geometry.** Documented harness ran `n_hh = 5` — the last rung of Two-L's ladder returning `0.00`; the stored value came from a 241,895-row single-call chunk. Two different experiments. | Reprice reproduces the production chunk exactly — same 200-HH membership, same order, same synthetic ids. **Same experiment.** |
| 3 | **Stale components (Two-M bug).** Only 5 headline columns written back; `bsa00_s` a stale precompute carry-over, constant `0.00` at the failing households, so the original EUROMOD-computed RSA was never stored and is unrecoverable. | Cache persists `bsa00_s` **live** — and it reproduces to `0.0`, which both confirms it is live and makes RSA a genuine, binding witness rather than a formality. |

**What this does and does not settle.** It settles that the M08 baseline's own
consumption is exactly reproducible through the production path at production
geometry. It does **not** settle anything about pricing *redrawn* nodes: this gate
reprices stored nodes, so target-only and full-chunk geometry coincide (§1.3).
F3-R2B's finding stands unchanged — **batch-context dependence is proven and joint
batching is not licensed** — so any future redrawn-node pricing must use
target-only geometry with the counterfactual on the target household alone. A PASS
here is not a licence for joint-batch redrawing.

Contract §2 classification: the documented defect, **for the cell M08 consumes**,
is neither structural nor type-specific — it was an instrument-and-scope defect,
and correcting the instrument and the scope closed it completely. The 2026-06-02
"STRUCTURAL" classification is **superseded for the P2a cell**; it remains
accurate for the P3a b-pool cell, where the cause is now identified as build
vintage against a changed EUROMOD system.

**No halt condition fired.** No production pricing code change was needed at any
point; no generic `dclaborsupply` package change was needed; parity is not
structural or unresolved for this cell; accepted P2a inputs bound cleanly.

---

## 6. Next action

1. **Goal-1 Manager: accept or reject this gate report.** On acceptance, contract
   §1–§2 close for the France-2016-singles P2a cell and the charter §7 Stage-B
   parity precondition is satisfied for that cell.
2. **Record the §3.6 scope finding as answered** in the Stage-A freeze: the M08
   parity gate binds the P2a pricing cache (R-60, Route 6), the gate passes at
   `0.0`, and the §3.4 residual is a P3a-build property that M08 does not inherit.
   Contract §1.2's "STRUCTURAL / never closed" language should carry the currency
   note already added at §1.3 plus this result.
3. **Contract §2 item 5 — the bounded Stage-C review.** Its nominal subject ("the
   changed production path") is **empty**: no production path changed. The review
   scope is therefore the three new gate files, the artifact binding, and this
   evidence packet — one bounded review, not a general software-review loop.
4. **Scope limits to carry forward, explicitly:**
   - Only FR-2016 singles on the P2a artifact is gated. If the redraw path is ever
     pointed at a P3a cell, that cell needs its own gate and will meet the
     system-drift blocker recorded in §5.
   - The gate licenses **reproducibility**, not joint-batch redrawing. Target-only
     geometry remains mandatory for counterfactual pricing.
   - Component decomposition is bounded by what the cache stores (§1.4). If a
     later stage requires stored-vs-repriced differences on
     `ils_origy`/`ils_sicdy`/`ils_tax`/`ils_ben`, that requires regenerating the
     cache with more columns — a separate, currently unauthorised decision.
5. **Still open and unchanged — these gate Stage D–G, not this gate:** U3, U4, U6,
   U12, U15 (escalated); U7, U8 (proposed, pending ratification); U10 (pre-execution
   values to be pulled from the digest-bound reporting map). Nothing in this run
   resolved, touched, or depended on any of them.

**Authorised by this report: nothing beyond the record of the gate.** No redrawn
node, no `V_i^dir`, no welfare number, no promotion to `complete/`.

---

## Provenance

**Attempts published** (`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/`,
U9-resolved namespace; `complete/` never created or promoted):

| Attempt | Outcome |
|---|---|
| `20260805T175912Z_104548_c376a2bfd6b44912b60146ecc9a04f58_parity_STOPPED_HP_RECON` | first attempt, halted in reconstruction: the production notebook calls the IPython `display` builtin, absent outside a kernel. Recorded for completeness; fixed by seeding inert display shims into the reconstruction namespace (presentation only — no notebook logic branches on them). |
| `20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE` | bounded smoke, chunk `priced_00000` |
| `20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL` | **full run, all 8 chunks — the gate of record** |

Each attempt carries `gate_manifest.json` (pins, frozen inputs, geometry check,
per-chunk results, aggregate verdict), `chunk_priced_*.json`, and
`reconstruction_log.txt`.

**Gate code added (new files, uncommitted; no existing file modified):**
`scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml`,
`scripts/welfare/m08_p2a_parity.py`,
`scripts/welfare/run_m08_p2a_parity_gate.py`.

**Read-only, unmodified:** the 8 pinned `fr_singles_pricing_p2a/priced_*.parquet`;
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`;
`outputs/p2a_singles2016/region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet`;
`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb`;
`EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`; the FR EUROMOD system files;
`scripts/welfare/welfare_vdir.py` and `run_stage2_parity.py` (deliberately left as
they stand, so the documented failure remains reproducible as recorded).

## Explicit scope statement

France 2016 singles P2a cell only. No production pricing code changed. No redrawn
node. No counterfactual covariate. No welfare number, no measure, no `V_i^dir`, no
re-estimation. No couples, no pooled years, no other cell. No stored consumption
value modified, replaced, or regenerated. EUROMOD executed solely for
parity-validation repricing. Uncommitted.
