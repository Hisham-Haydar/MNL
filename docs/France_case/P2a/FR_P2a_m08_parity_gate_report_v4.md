# FR P2a — M08 Stage-B Reprice-Parity Gate Report v4 (UNCOMMITTED)

**Mission:** JMP-M08, contract §1–§2 (parity correction + gate), Stage B step 3.
**Authority:** Goal-1 ruling **R-60** (Route 6 → Route 1, ratified), applied to
`FR_P2a_m08_parity_diagnosis_memo_v1.md` §4.
**Scope discipline:** France 2016 singles **P2a cell only**. No production pricing
code changed. No redrawn node. No counterfactual covariate. No welfare number. No
couples, pooled years, or other cells. No stored consumption value modified,
replaced, or regenerated. EUROMOD executed **solely** for parity-validation
repricing.
**Produced against:** MNL `520441a653f04196bf1e92e3658a478b4feb3718` (tracked tree
clean; gate additions untracked); `dclaborsupply-monorepo`
`27756a06ea189339aa82915ed2124628afed20eb` (clean, `--untracked-files=all`).

---

## Report v4 status — E2 final closure

This report **supersedes `FR_P2a_m08_parity_gate_report_v3.md`**, which remains on
disk, unedited, as immutable history. It is issued under the binding disposition at
`Job_Market_paper/docs/Missions/JMP_M08_final_E2_literature_and_decomposition_architecture_ruling_v1.md`
§2 (Deputy Programme Director, 2026-08-07). The only substantive change from report
v3 is removal of the residual E2-2 pairwise inference in §0 below. The attempt of
record, the gate code, the gate packet, every certified statistic, the `1.0e-6`
EUR tolerance, and the `PASS` verdict are unchanged from report v3. No code,
config, manifest, chunk JSON, attempt directory, gate statistic, tolerance, or
verdict was touched to produce this report; no EUROMOD execution occurred. Full
change accounting: `FR_P2a_m08_parity_gate_report_v4_change_log.md`.

---

## Report v3 status — E2 documentary correction

This report **supersedes `FR_P2a_m08_parity_gate_report_v2.md`**, which remains on
disk, unedited, as immutable history. It is issued under the binding disposition at
`Job_Market_paper/docs/Missions/JMP_M08_E2_parity_report_v3_documentary_correction_ruling_v1.md`
(Deputy Programme Director, 2026-08-06), following the second narrow-review REJECT
recorded in `FR_P2a_m08_codex_reverification_T4_T7_v1.md` (verdict register: R1 T4
cure ACCEPT; R2 T4 witness delta ACCEPT; R3 T7 cure REJECT; R4 earned verdict
ACCEPT). R3's sole basis was that two numerical statements in packet-only §§3–4 did
not trace to the new attempt's manifest or chunk JSONs.

Only the two corrections the ruling authorizes were made, both documentary and both
confined to claim-to-evidence traceability:

1. **§3 runtime statement.** The projected-runtime, runtime-guard, and
   ex-ante-cost-decision language is deleted and replaced with a new-attempt-only
   realised-elapsed-time statement, citing `gate_manifest.json → started_utc` /
   `→ finished_utc` for the elapsed time and `→ run.requested_chunks` /
   `→ run.chunk_grid` / `→ run.is_full_run` / `→ aggregate.chunks_run` /
   `→ aggregate.chunks_on_grid` for the complete-grid claim (ruling §3.1).
2. **§4.4 determinism statement.** The three-execution, pairwise-`0.0`
   determinism claim is deleted and replaced with the ruling's exact substitute
   sentence stating that the certification verdict rests solely on the attempt of
   record (ruling §3.2). §5's historical-attempt table is retained below as
   code-lineage/procedural history only; no prior attempt is cited anywhere in
   this report as numerical support or pairwise-equality evidence.

Nothing else changed. The attempt of record
(`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`),
the gate packet, the gate code (`m08_p2a_parity.py`, `run_m08_p2a_parity_gate.py`,
`welfare_m08_p2a_parity_v1.yaml`), the comparator, the `1.0e-6` EUR tolerance, every
certified statistic in §§3–4, and the `PASS` verdict are unchanged from report v2.
No code, config, manifest, chunk JSON, attempt directory, gate statistic, tolerance,
or verdict was touched to produce this report; no EUROMOD execution was performed
for this correction; nothing was committed by this correction.

Full change accounting: `FR_P2a_m08_parity_gate_report_v3_change_log.md`.

---

## 0. Supersession note

This report **supersedes `FR_P2a_m08_parity_gate_report_v1.md`**, which remains on
disk unedited as history. It is issued as the rule-3 conversion of the REJECT
verdicts recorded in

> `docs/France_case/P2a/FR_P2a_m08_codex_production_path_review_v1.md`
> — *FR P2a — JMP-M08 Reprice-Parity Production-Path Review v1*, overall verdict
> **REJECT**: T1, T2, T3, T5, T6 **ACCEPT**; **T4 (comparison soundness) REJECT**;
> **T7 (claim-to-evidence) REJECT**.

Two things changed, and only two:

1. **T4 — the parity harness comparator was fixed.** The reviewed comparator
   failed *open* on non-finite values. Finiteness is now first-class evidence and
   the certification standard is tightened accordingly (§2, §3).
2. **T7 — this report replaces v1's claim-to-evidence packet.** Every numerical
   result claim now cites the exact manifest or chunk JSON of the **new** attempt;
   the code-lineage statement is corrected; the FR.xml timing passage is restated
   as attribution, not causation; the "bit-for-bit" characterisation is withdrawn.

Not changed, and deliberately so: **no production pricing code**, no redrawn node,
no welfare number, and — inside the harness — no change to pin verification,
reconstruction, batch geometry, join keys, tolerance, or the `attempts/`
transaction pattern. The reviewed ACCEPTs (T1, T2, T3, T5, T6) rest on that logic
and it is byte-for-byte the logic they were granted against.

**The v1 verdict `PARITY_PASS_FULL` is withdrawn as a certification.** It is
replaced by the verdict of the new attempt in §4, earned under the tightened
standard. The review classified its T4 rejection as an implementation defect that
blocked scientific certification rather than affirmative evidence of a finite
scientific mismatch.

---

## 1. Citation convention (T7 finding 1)

The review's decisive T7 observation was that v1 presented numbers that appear in
no manifest and no chunk JSON. This report answers it structurally:

- **§3 and §4 contain gate results only.** Every value in them is traceable to a
  named field of a named file of the new attempt. Each results table carries a
  caption naming the **full attempt id** and the file its cells come from, so
  every cell citation is complete (attempt id + file + field). Prose claims carry
  the full attempt id inline.
- **§6 contains non-packet context**, clearly fenced and labelled
  **NOT GATE-PACKET EVIDENCE**, with its actual source given for each figure. No
  such figure is used to support the verdict.

The attempt of record for this report is

```
20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL
```

published under
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/`. It contains
`gate_manifest.json`, eight `chunk_priced_*.json`, and `reconstruction_log.txt`.
No `failing_rows_*.csv` exists, because no row was captured (§4.3).

---

## 2. Gate definition and the tightened certification standard

### 2.1 What the gate is (unchanged from v1 §1)

The gate reprices the committed, hash-pinned P2a singles-2016 pricing cache — the
artifact M08 consumes — through the **same production pricing path** that produced
it, at the **same batch geometry**, and compares repriced against stored at the
frozen `1.0e-6` EUR tolerance (contract **D10** / `stage2.parity_grid.tol`).

- **Artifact binding.** Pins are read from the committed production config
  `scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml → frozen_inputs.pricing_cache`
  and never re-declared in the gate config; every chunk is hashed and verified
  before any comparison.
- **Geometry (D-BEN Option B, target-only).** `hh_all = sorted(single idhh)`,
  chunks of 200 source households, ONE `EuromodPricingRunner.price()` call per
  chunk, `alt_key_cols=['draw']`, each alternative replicated as an isolated
  synthetic household. In a **parity** run the target node *is* the stored node,
  so nothing is displaced and Option B degenerates onto the production batch
  itself.
- **Comparison.** Gate column `ils_dispy`; witness column `bsa00_s` (RSA — memo §5
  item 5); join `(source_idhh, draw, source_idperson)` with `validate="one_to_one"`
  and full row-set equality asserted before any statistic is computed.

None of this moved in the conversion.

### 2.2 What the review falsified (T4)

The reviewed comparator coerced both sides with `pd.to_numeric(..., errors='coerce')`,
summarised with `np.nanmax`/`np.nanmedian`, and built its **only** gate mask as
`d > tol` — with no `isfinite`/null assertion anywhere before the mask
(review memo §T4, citing `scripts/welfare/m08_p2a_parity.py:393-403`). A
non-numeric or `NaN` value on either side therefore produced `NaN > 1e-6 == False`:
it was neither counted, nor captured, nor visible in the summary. The reviewer
executed the real function with a finite stored `10.0` against a repriced `NaN` on
the same unique key and obtained

```text
status=PASS
n_rows_above_tol=0
max_abs_diff=nan
failing_rows_is_none=True
```

The chunk status rule (`m08_p2a_parity.py:416-434`) and the runner's aggregate
verdict (`run_m08_p2a_parity_gate.py:203-228`) then inherited that open failure,
and — decisively — **no field of the v1 manifest or chunk JSONs recorded a
non-finite count on either side**, so the historical eight-chunk packet could not
exclude the condition even in principle.

### 2.3 The tightened standard

The gate now certifies against this rule, which is recorded verbatim in the
manifest itself (`…_parity_PARITY_PASS_FULL/gate_manifest.json →
certification_standard` and `→ aggregate.certification_standard`):

> PASS requires, on EVERY chunk: zero rows above the frozen `tol_eur` on every
> gate column **AND** zero non-finite values on **BOTH** the stored and the
> repriced side of every gate column **AND** zero EUROMOD hard errors. A
> non-finite value on either side is treated as an infinite absolute difference,
> never a masked `NaN`, so it both fails the chunk and appears in the failing-row
> capture. Witness-column non-finiteness is counted, captured and reported but
> does not gate.

Three notes on the shape of that rule.

- **Why `+infinity` rather than a separate assertion.** Treating an incomparable
  row as an infinite difference *closes* the existing test rather than adding a
  parallel one: `d > tol` can no longer be silently `False`, so there is no second
  code path that could be forgotten. `max_abs_diff` becomes `inf` for such a
  chunk, which is a loud and correct summary; `max_abs_diff_finite_rows` is
  reported alongside it so the finite-comparable subset stays legible.
- **Why the witness does not gate.** The review's falsification is stated against
  the gate mask; it does not assert that a non-finite witness must fail a chunk.
  Witness non-finiteness is therefore counted on both sides, captured per row and
  reported at chunk and aggregate level — but `bsa00_s` remains a witness, not a
  gate. This is recorded as `witness_nonfiniteness_gates: false` in both the chunk
  JSON (`→ finiteness.witness_nonfiniteness_gates`) and the manifest
  (`→ aggregate.witness_nonfiniteness_gates`), so the choice is auditable rather
  than implicit.
- **Rows compared are asserted, not assumed.** Each chunk records
  `n_rows_compared` and asserts it equals the stored row count; the runner sums
  both independently and halts on disagreement. A comparison that quietly shrank
  can no longer masquerade as a clean one.

### 2.4 What changed in the harness, exactly

| File | Change | Where |
|---|---|---|
| `scripts/welfare/m08_p2a_parity.py` | new `_numeric_side()` — coerces one side and accounts its finiteness (`n_raw_null`, `n_noncoercible`, `n_nan`, `n_inf`, `n_nonfinite`) | `m08_p2a_parity.py:351-371` |
| | `CERTIFICATION_STANDARD` constant, persisted into every chunk JSON and the manifest | `m08_p2a_parity.py:374-382` |
| | `n_rows_compared` computed and asserted `== stored_rows` before any statistic | `m08_p2a_parity.py:445-451` |
| | non-finite on either side ⇒ `d = +inf`, per-row `nonfinite_<col>` flag, per-column counts both sides | `m08_p2a_parity.py:457-485` |
| | capture extended to every non-finite row, with `fails_gate` / `nonfinite_gate_column` columns | `m08_p2a_parity.py:491-506` |
| | per-chunk `finiteness` block | `m08_p2a_parity.py:508-527` |
| | chunk `status` = tolerance **AND** finiteness **AND** no hard error | `m08_p2a_parity.py:551-553` |
| `scripts/welfare/run_m08_p2a_parity_gate.py` | verdict rule restated in the module contract | `run_m08_p2a_parity_gate.py:15-22` |
| | `certification_standard` written into the manifest header | `run_m08_p2a_parity_gate.py:134` |
| | aggregate rows-compared cross-check (halts on mismatch) | `run_m08_p2a_parity_gate.py:220-225` |
| | aggregate finiteness fields, gate and witness, both sides | `run_m08_p2a_parity_gate.py:226-266` |
| | aggregate verdict = all-chunks-PASS **AND** zero above tol **AND** zero gate non-finite | `run_m08_p2a_parity_gate.py:267-272` |
| | per-chunk and final console lines report rows-compared and non-finite counts | `run_m08_p2a_parity_gate.py:203-211`, `:283-287` |

Untouched in both files: pin verification, `verify_frozen_inputs`,
`reconstruct_pipeline`, `verify_reconstructed_geometry`, `_alternatives`, the
`runner_full.price` call and its arguments, the duplicate-key / row-set /
one-to-one join checks, the `1.0e-6` tolerance, and `GateTransaction`.

### 2.5 The fix, proved against the review's own case

A read-only in-memory execution of the **real** `reprice_chunk` (stub runner,
throwaway stored parquet in scratch; no EUROMOD, no production file touched)
returns, on the fixed library:

| Case | `status` | `n_rows_above_tol` | gate `max_abs_diff` | non-finite stored/repriced | capture |
|---|:--:|---:|---|---|---|
| all rows equal | PASS | 0 | 0.0 | 0/0 | none |
| **review's case: repriced `NaN`** | **FAIL** | **1** | **inf** | **0/1** | **1 row, `fails_gate=True`, `nonfinite_ils_dispy=True`** |
| repriced `+inf` | FAIL | 1 | inf | 0/1 | 1 row, flagged |
| ordinary finite `2e-6` difference | FAIL | 1 | 2.000e-06 | 0/0 | 1 row, `nonfinite=False` |
| finite gate, non-finite **witness** | PASS | 0 | 0.0 | gate 0/0, witness 0/1 | 1 row, `fails_gate=False` |

Row 2 is the exact inverse of the review's recorded falsification, on the same
input. Row 4 confirms the ordinary finite-difference behaviour the review
accepted is unchanged. Row 5 confirms the witness policy is implemented as
declared.

---

## 3. Certified full re-run — execution record

All 8 chunks of the pinned P2a cache, chunk-sequential, one EUROMOD call per
chunk, manifest re-persisted after every chunk, under the unchanged
lock → staging → atomic-rename transaction. Prior attempts were not read, written,
or promoted; `complete/` was never created.

*All values in §3 and §4 come from attempt*
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`.

| Quantity | Value | Citation (file → field) |
|---|---|---|
| Attempt id | `20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity` | `gate_manifest.json → attempt_id` |
| Started / finished (UTC) | `2026-08-06T06:20:50Z` → `2026-08-06T06:40:10Z` (19 min 20 s) | `gate_manifest.json → started_utc`, `→ finished_utc` |
| EUROMOD seconds, total | `1138.1` | `gate_manifest.json → aggregate.euromod_seconds_total` |
| Pins verified | all 8 match; `225836` rows observed = `225836` declared; `1555` households = declared | `gate_manifest.json → artifact_binding.all_pins_match`, `→ artifact_binding.observed_rows_total`, `→ artifact_binding.expected_rows_total`, `→ artifact_binding.observed_hh`, `→ artifact_binding.expected_hh` |
| Reconstruction | cells `[2, 34]`, `20.8` s, `CHUNK = 200`, `1555` households | `gate_manifest.json → reconstruction.cells`, `→ reconstruction.seconds`, `→ reconstruction.chunk_size`, `→ reconstruction.n_households` |
| Rebuilt geometry vs frozen parquet | `157055` rows, `1555` households, max abs diff `0.0`, match `true` | `gate_manifest.json → geometry_check.rebuilt_rows`, `→ geometry_check.rebuilt_households`, `→ geometry_check.max_abs_diff_overall`, `→ geometry_check.matches_frozen_geometry` |
| Grid requested | `[0,200,400,600,800,1000,1200,1400]` = full committed grid; `is_full_run: true` | `gate_manifest.json → run.requested_chunks`, `→ run.chunk_grid`, `→ run.is_full_run` |
| EUROMOD system | `FR` / `FR_2015` / `FR_2016_a3`, `weeks_per_month = 4.333333333333333` | `gate_manifest.json → reconstruction.euromod` |

Realised elapsed time for the complete grid was 19 minutes 20 seconds; no chunk
was sampled, truncated, or deferred (`started_utc` `2026-08-06T06:20:50Z` →
`finished_utc` `2026-08-06T06:40:10Z`; requested chunks
`[0,200,400,600,800,1000,1200,1400]` equal the full chunk grid, `is_full_run: true`,
eight of eight chunks run — `gate_manifest.json → started_utc`,
`→ finished_utc`, `→ run.requested_chunks`, `→ run.chunk_grid`,
`→ run.is_full_run`, `→ aggregate.chunks_run`, `→ aggregate.chunks_on_grid`).

---

## 4. Certified results

### 4.1 Per chunk

*Every cell below cites attempt*
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`,
*file* `chunk_priced_<chunk>.json`, *field named in the column header.*

| `chunk` | `status` | `households_in_batch` | `alternatives_in_batch` | `n_rows_compared` | `stored_rows` | `column_summary.ils_dispy.max_abs_diff` | `column_summary.ils_dispy.n_rows_above_tol` | `column_summary.bsa00_s.max_abs_diff` | `column_summary.bsa00_s.n_rows_above_tol` | `row_order_identical_to_stored` | `euromod_hard_errors` | `euromod_seconds` |
|---|:--:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|:--:|---:|
| `priced_00000` | **PASS** | 200 | 20,200 | 29,492 | 29,492 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 148.7 |
| `priced_00200` | **PASS** | 200 | 20,200 | 29,593 | 29,593 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 146.7 |
| `priced_00400` | **PASS** | 200 | 20,200 | 27,775 | 27,775 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 145.2 |
| `priced_00600` | **PASS** | 200 | 20,200 | 30,704 | 30,704 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 147.8 |
| `priced_00800` | **PASS** | 200 | 20,200 | 28,583 | 28,583 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 144.6 |
| `priced_01000` | **PASS** | 200 | 20,200 | 28,078 | 28,078 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 146.5 |
| `priced_01200` | **PASS** | 200 | 20,200 | 28,482 | 28,482 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 145.7 |
| `priced_01400` | **PASS** | 155 | 15,655 | 23,129 | 23,129 | **0.0** | **0** | **0.0** | **0** | `true` | `[]` | 112.9 |

Every chunk also records `euromod_uprate_notes: 6` — the same uprating notices
production emits; they are not hard errors and are excluded from
`euromod_hard_errors` by the unchanged filter.

### 4.2 Finiteness certification table (T4)

*Every cell below cites attempt*
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`,
*file* `chunk_priced_<chunk>.json`, *field named in the column header.*

| `chunk` | `n_rows_compared` | `finiteness.rows_compared_equals_stored_rows` | `finiteness.n_nonfinite_gate_stored` | `finiteness.n_nonfinite_gate_repriced` | `n_rows_nonfinite_gate` | `finiteness.n_nonfinite_witness_stored` | `finiteness.n_nonfinite_witness_repriced` | `finiteness.all_gate_values_finite_both_sides` | `finiteness.all_compared_values_finite_both_sides` |
|---|---:|:--:|---:|---:|---:|---:|---:|:--:|:--:|
| `priced_00000` | 29,492 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_00200` | 29,593 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_00400` | 27,775 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_00600` | 30,704 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_00800` | 28,583 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_01000` | 28,078 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_01200` | 28,482 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| `priced_01400` | 23,129 | `true` | **0** | **0** | **0** | **0** | **0** | `true` | `true` |
| **total** | **225,836** | — | **0** | **0** | **0** | **0** | **0** | — | — |

The per-side breakdown is finer than the totals above: for both `ils_dispy` and
`bsa00_s`, on both sides, on all eight chunks,
`column_summary.<col>.{stored,repriced}_side_counts` records
`n_raw_null = 0`, `n_noncoercible = 0`, `n_nan = 0`, `n_inf = 0`,
`n_nonfinite = 0`. So the packet now excludes, per column and per side, *stored
nulls*, *values that would not coerce*, *computed `NaN`s* and *infinities* —
which is exactly the class of value the reviewed gate could not exclude.

### 4.3 Aggregate

*Every cell below cites attempt*
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`,
*file* `gate_manifest.json`, *field named in the left column.*

| `aggregate.<field>` | Value |
|---|---|
| `chunks_run` / `chunks_on_grid` | **8 / 8** |
| `is_full_run` | `true` |
| `rows_compared` | **225,836** |
| `rows_compared_from_chunks` | **225,836** |
| `rows_compared_equals_stored_rows` | `true` |
| `gate_column` | `ils_dispy` |
| `tol_eur` | `1e-06` |
| `ils_dispy_max_abs_diff` | **0.0** |
| `rows_above_tol` | **0** |
| `gate_nonfinite_stored` | **0** |
| `gate_nonfinite_repriced` | **0** |
| `rows_with_nonfinite_gate_value` | **0** |
| `all_gate_values_finite_both_sides` | **`true`** |
| `chunks_with_nonfinite_gate_value` | `[]` |
| `bsa00_s_max_abs_diff` | **0.0** |
| `bsa00_s_rows_above_tol` | **0** |
| `bsa00_s_nonfinite_stored` / `bsa00_s_nonfinite_repriced` | **0** / **0** |
| `witness_nonfinite_stored` / `witness_nonfinite_repriced` | **0** / **0** |
| `witness_nonfiniteness_gates` | `false` |
| `chunks_failing` | `[]` |
| `euromod_seconds_total` | `1138.1` |
| **`verdict`** | **`PASS`** |

No `failing_rows_priced_*.csv` and no `failing_rows_all.csv` exist in the attempt
directory. Under the fixed comparator that is now a positive statement rather than
an absence: capture fires on any failing row **and** on any non-finite row in any
compared column, and every chunk records `n_rows_captured: 0`.

### 4.4 Verdict

## VERDICT: **PASS** — certified under the tightened standard

Across all **225,836** rows of the entire P2a 2016-singles pricing cache, on all
**8** chunks:

- **zero** rows above the frozen `1.0e-6` EUR tolerance on the gate column
  `ils_dispy`, maximum absolute difference **0.0**; and
- **zero** non-finite values on the stored side and **zero** on the repriced side
  of the gate column — and of the `bsa00_s` witness as well; and
- **zero** EUROMOD hard errors; and
- rows compared equals stored rows, chunk by chunk and in aggregate.

**Characterisation, stated exactly.** This is equality of `float64` values at
absolute tolerance `1.0e-6` EUR, with every compared value proven finite on both
sides, after `pd.to_numeric` coercion — and the observed maximum difference is
identically `0.0`. **It is not a bitwise comparison, and this report does not
claim bit-for-bit equality** (see §7, T7 finding 4). The gate compares two
`float64` arrays numerically; no byte-level comparison of the stored and repriced
representations is performed anywhere in the harness.

What the verdict rests on, in the order it was established:

1. **The artifact is the right one and is authentic** — all 8 committed SHA-256
   pins verified before any comparison, declared shape matched
   (`…ffa19dbe…_PARITY_PASS_FULL/gate_manifest.json → artifact_binding`).
2. **The path is the production path** — the rebuilt draw frame reproduces the
   committed frozen geometry at max abs diff `0.0` on every pricing-relevant
   column (`…ffa19dbe…_PARITY_PASS_FULL/gate_manifest.json → geometry_check`).
3. **The batch is the production batch** — row order identical to stored on all 8
   chunks (`…ffa19dbe…_PARITY_PASS_FULL/chunk_priced_*.json →
   row_order_identical_to_stored`), so the RSA whole-batch accumulators are
   reproduced by construction.
4. **The comparison is now closed** — §4.2; the failure mode the review
   demonstrated cannot occur undetected, and its absence is recorded per chunk,
   per column, per side.
5. The certification verdict rests solely on the attempt of record and its eight
   chunk JSONs. Earlier attempts are retained as code-lineage and procedural
   history only and do not provide numerical support for this verdict.

---

## 5. Code lineage across all attempts (T7 finding 2)

v1 stated that library `d79d05…` was "recorded in every attempt manifest". That is
false: the first attempt records `bde41a…`. The accurate lineage, read from the
four manifests, is:

| # | Attempt id | `config_sha256` | `library_sha256` | `runner_sha256` | Outcome |
|---|---|---|---|---|---|
| 1 | `20260805T175912Z_104548_c376a2bfd6b44912b60146ecc9a04f58_parity_STOPPED_HP_RECON` | `029d5ee6…979e81` | **`bde41a07…d82c7`** | `1eea3cc7…1423d8` | halted in reconstruction (`HP-RECON`, `cell-21`: notebook calls the IPython `display` builtin, absent outside a kernel) |
| 2 | `20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE` | `029d5ee6…979e81` | **`d79d05ae…856547`** | `1eea3cc7…1423d8` | bounded smoke, chunk `priced_00000` |
| 3 | `20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL` | `029d5ee6…979e81` | **`d79d05ae…856547`** | `1eea3cc7…1423d8` | v1's full run — **verdict withdrawn as a certification** (§0) |
| 4 | `20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL` | `029d5ee6…979e81` | **`441b416d…181046`** | **`69571a67…0b6467`** | **this report's gate of record** |

Full digests:

```
config  (all four attempts, unchanged)
        029d5ee618576c9a91cc2374500e3d632912c52d637a1b4268c1db4796979e81
library attempt 1   bde41a0718093855ec310e1725633df5532d50c44def056a2b041389823d82c7
library attempts 2,3 d79d05ae326276506bc950449af737da35042cac4d16e733963c1ae1b9856547
library attempt 4   441b416d164827eab6b0822b2f6dfbda9d3de639aac61ddbdc0f144ac3181046
runner  attempts 1-3 1eea3cc7583811170426c12e2a44058d9145dac52eceb202c7f10ecda31423d8
runner  attempt 4   69571a671492ec37151ca322003a4c551c6b218996949ea47e11b74a1a0b6467
```

Two library transitions, each with its cause stated:

- **`bde41a…` → `d79d05…` (between attempts 1 and 2): the display-shim fix.** After
  the `HP-RECON` halt, the reconstruction namespace was seeded with inert
  `display` / `get_ipython` lambdas returning `None`
  (`m08_p2a_parity.py:211-219` at that revision). The review verified this change
  in memory — reverting exactly those lines reproduces `bde41a…` byte-for-byte —
  and verified it is presentation-only: within reconstructed cells 2–34 the
  notebook has two `display(...)` calls, both expression statements whose return
  values are unused, and no `get_ipython` call. T5 was **ACCEPTed** on that basis.
  The runner and config did not change.
- **`d79d05…` → `441b416d…` and `1eea3cc7…` → `69571a67…` (between attempts 3 and
  4): this conversion's T4 comparator fix**, itemised at §2.4. This is the only
  change between attempt 3 and attempt 4; the config is identical across all four
  attempts.

**Correction to v1's notebook description (T7 finding 2b).** v1 described notebook
code cells 2–34 as "the loop that wrote the cache". They are not. Cells 2–34 build
the state the pricing loop ran inside — cell 34 defines the FR earnings policy,
the full-entitlement baseline, `EuromodPricingRunner`, `hh_all = sorted(single_idhh)`
and `CHUNK = 200`. **The loop that wrote the cache is code cell 35**
(`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:1233-1253`), which
copies `draws_p2a` into `alt2`, sets the source/decider identifiers, iterates the
sorted household list in 200-household slices and makes one `runner_full.price`
call per slice with `alt_key_cols=['draw']`. The gate **reconstructs cells 2–34**
and **separately reimplements cell 35's pricing call** in `reprice_chunk` — which
is what makes the geometry claim checkable rather than assumed, and is exactly
what the review confirmed under T3 (**ACCEPT**). The reconstruction span is
recorded as `[2, 34]` at
`…ffa19dbe…_PARITY_PASS_FULL/gate_manifest.json → reconstruction.cells`.

---

## 6. Non-packet context — **NOT GATE-PACKET EVIDENCE** (T7 finding 1)

Everything in this section is *background*. **None of it is produced by the gate,
none of it appears in any manifest or chunk JSON, and none of it supports the
verdict in §4.4.** It is retained because v1 used it and a reader of both
documents needs to know where it actually comes from.

### 6.1 RSA exposure in chunk 0 (v1 §2 and §4 item 4)

v1 asserted "182 of 200 households (91.0 %)" and "23.7 % of rows" carry
`bsa00_s > 0`, presenting them among gate results. **The gate does not compute
these figures**; the chunk JSON carries batch sizes, timing, errors, available
columns and difference summaries only.

They are, however, reproducible by a read-only inspection of the pinned cache —
independently by the reviewer (review memo §T7 item 1) and again for this report:

```
priced_00000.parquet:  households with bsa00_s > 0 at some draw:  182 / 200 = 91.0000 %
priced_00000.parquet:  rows with bsa00_s > 0:                   6,993 / 29,492 = 23.7115 %
```

**Status:** true, reproducible, *and not gate output*. The gate-packet fact about
RSA — the one that does carry evidentiary weight — is that `bsa00_s` is compared
at full row resolution on every chunk and returns max abs diff `0.0` with zero
non-finite values on both sides (§4.1, §4.2).

### 6.2 The P3a b-pool residual (v1 §5)

| Figure used by v1 | Actual source | In this gate packet? |
|---|---|---|
| max abs diff `184.6123` EUR on `ils_dispy`, 3,460 rows / 372 HHs | `docs/jmp_methodology/RURO_welfare_F6PRICEB0_geometry_audit_v1.md:15`, `:142`, `:148` | **No** |
| `185.5400` EUR on `ils_ben`, 3,460 rows | `docs/jmp_methodology/RURO_welfare_F6PRICEB0_geometry_audit_v1.md:143` | **No** |
| 3,460 / 169,276 = 2.04 % of 2016-singles decider rows, max €185.54 | `docs/France_case/P2a/FR_P2a_m08_parity_diagnosis_memo_v1.md:50`, `:217`, `:235` | **No** |
| P3a chunk `c0` created `2026-05-24T23:21:08Z` | `RURO_welfare_F6PRICEB0_geometry_audit_v1.md:58`, `:159` | **No** |
| `FR.xml` / `FR_DataConfig.xml` last modified `2026-05-26T09:30:39Z` | **Yes** — `…ffa19dbe…_PARITY_PASS_FULL/gate_manifest.json → frozen_inputs.euromod_system_files` | **Yes** (mtimes only) |
| P2a cache written `2026-07-12` (10:46–11:03Z) | filesystem mtimes of `fr_singles_pricing_p2a/priced_*.parquet` | **No** |

v1 additionally conflated `184.61` and `185.54` — they are two different columns
of the same audit (`ils_dispy` and `ils_ben` respectively), not one figure.

### 6.3 EUROMOD system timing — **attribution, not causation** (T7 finding 3)

v1 wrote that three facts *"explain the difference"*, that another task *"traced
the … residual precisely"* to system drift, and that the cause *"is now identified
as build vintage against a changed EUROMOD system"*. Those are proven-cause
formulations and they overstate what any of the cited evidence establishes. They
are withdrawn and replaced by the following.

**What is established.** The gate manifest of this attempt records only the
current size and mtime of the FR system files:
`FR.xml` `57,072,125` bytes, mtime `2026-05-26T09:30:39Z`; `FR_DataConfig.xml`
`808,223` bytes, mtime `2026-05-26T09:30:39Z`
(`…ffa19dbe…_PARITY_PASS_FULL/gate_manifest.json → frozen_inputs.euromod_system_files`).
Nothing else about the EUROMOD system is measured by this gate; the mtimes are
recorded and never gated on.

**What is attribution.** The P3a b-pool chunk `c0` predates those mtimes by ~35
hours (§6.2), while the P2a cache postdates them by ~7 weeks. The observed P2a
result is consistent with a *no-drift* configuration and the observed P3a failure
is consistent with a *drift* configuration. That is a temporal co-occurrence
between two independently recorded facts. **Causation is not established by this
gate or by anything cited in this report.** No controlled comparison was run: the
XML content difference was never diffed, no rollback of `FR.xml` to its
pre-`2026-05-26` state was performed and repriced, and no alternative explanation
of the P3a residual was excluded. Establishing causation would require at minimum
repricing the P3a b-pool cell against a rolled-back system and observing the
residual close — which is not authorised, not attempted, and not implied here.

**What is therefore claimed:** the FR.xml timing is *consistent with*, and is
*attributed as the leading candidate explanation for*, the difference between the
P3a b-pool failure and this P2a PASS. It is not a demonstrated cause.

Two further facts distinguish the two cells and are independent of the timing
question. They are stated as differences, not as excuses for the PASS:

- **Batch geometry.** The documented harness ran `n_hh = 5`, the last rung of
  Two-L's ladder returning `0.00`, while the stored value came from a single-call
  chunk — two different experiments. This gate reproduces the production chunk
  exactly: same 200-household membership, same order, same synthetic ids
  (§4.1, `row_order_identical_to_stored`).
- **Stale components (Two-M).** In the P3a build only five headline columns were
  written back and `bsa00_s` was a stale precompute carry-over, so the original
  EUROMOD-computed RSA was never stored. The P2a cache persists `bsa00_s` live,
  and it reproduces at `0.0` with zero non-finite values, which is what makes RSA
  a binding witness here rather than a formality (§4.1, §4.2).

Contract §2 classification, restated with the same caution: for the cell M08
consumes, the documented defect was an **instrument-and-scope defect** — the
harness measured a different artifact at a different batch size — and correcting
the instrument and the scope closed it. The 2026-06-02 "STRUCTURAL" classification
is superseded **for the P2a cell**. It stands for the P3a b-pool cell, where the
failure remains open and its leading attributed candidate is build vintage against
a changed EUROMOD system, on the attribution-only basis stated above.

---

## 7. Findings register — how each REJECT finding is discharged

### T4 — comparison soundness

| Finding (review memo) | Disposition |
|---|---|
| `errors='coerce'` on both sides with no `isfinite`/null assertion before `d > tol`; `NaN > tol` is `False` so a non-finite value is neither counted nor captured (memo §T4, citing `m08_p2a_parity.py:393-403`) | **Fixed.** Both sides are accounted for finiteness by `_numeric_side`; a non-finite value on either side sets `d = +inf`, so it necessarily exceeds tolerance. `m08_p2a_parity.py:351-371`, `:457-485` |
| `np.nanmax` / `np.nanmedian` hide the same value from the summary (memo §T4) | **Fixed.** `d` contains no `NaN` by construction, so the summaries are plain `np.max`/`np.median`; `max_abs_diff_finite_rows` is reported separately for legibility. `m08_p2a_parity.py:468-472` |
| Executed proof: stored `10.0` vs repriced `NaN` returned `status=PASS`, `n_rows_above_tol=0`, `max_abs_diff=nan`, `failing_rows_is_none=True` (memo §T4) | **Falsified on the fixed library.** Same input now returns `status=FAIL`, `n_rows_above_tol=1`, `max_abs_diff=inf`, capture of 1 row with `fails_gate=True`, `nonfinite_ils_dispy=True` (§2.5, row 2) |
| Neither manifest nor chunk JSON records a repriced non-finite count, so the packet cannot exclude the condition (memo §T4) | **Fixed and exercised.** Per chunk, per column, per side: `n_raw_null`, `n_noncoercible`, `n_nan`, `n_inf`, `n_nonfinite`, plus chunk-level `finiteness` and aggregate totals — all persisted and all reported at §4.2/§4.3 |
| Chunk `status` = PASS whenever the masked count is zero and there are no hard errors (`m08_p2a_parity.py:416-434`) | **Fixed.** `status` = zero above tol **AND** zero gate non-finite **AND** no hard error. `m08_p2a_parity.py:551-553` |
| Runner verdict merely requires every chunk status to be PASS (`run_m08_p2a_parity_gate.py:203-228`) | **Fixed.** Aggregate verdict independently re-tests zero above tol and zero gate non-finite across all chunks, and cross-checks rows-compared against stored rows. `run_m08_p2a_parity_gate.py:220-225`, `:267-272` |
| *Requirement added by this conversion:* rows compared must be asserted equal to stored rows | **Implemented.** Per chunk (`m08_p2a_parity.py:445-451`) and in aggregate (`run_m08_p2a_parity_gate.py:220-225`); recorded at §4.2 and `aggregate.rows_compared_equals_stored_rows` |

Not altered, as required: pin verification, reconstruction, batch geometry, join
keys, the `1.0e-6` tolerance, and the transaction pattern (§2.4).

### T7 — claim-to-evidence

| Finding (review memo) | Disposition |
|---|---|
| **1a.** RSA claims 182/200 (91.0 %) and 23.7 % of rows appear in no manifest or chunk JSON (v1 `:194-197`, `:292-295`) | **Fixed.** Removed from the results sections entirely; relocated to §6.1 under an explicit **NOT GATE-PACKET EVIDENCE** fence with its actual source and an exact reproduction. §3–§4 now contain gate output only |
| **1b.** Historical residual counts/amounts and build times do not originate in this gate packet (v1 `:306-317`) | **Fixed.** Relocated to §6.2 with a per-figure source table stating, for each, whether it is in this gate packet. Only the FR system-file mtimes are; everything else is marked **No**. v1's conflation of `184.61` (`ils_dispy`) with `185.54` (`ils_ben`) is corrected there |
| **2a.** Library `d79d05…` presented as "recorded in every attempt manifest" while attempt 1 records `bde41a…` (v1 `:95-98`) | **Fixed.** §5 gives the per-attempt digest table with full values, both library transitions and their causes; no all-attempt identity claim is made anywhere |
| **2b.** Cells 2–34 called "the loop that wrote the cache"; the actual loop is cell 35 (v1 `:111-113`) | **Fixed.** §5 final paragraph states the correction explicitly, with the notebook line range, and describes what the gate reconstructs versus what it reimplements |
| **3.** FR.xml timing framed as causation — "explain the difference", "traced … precisely", "the cause is now identified" (v1 `:310-315`, `:328-333`) | **Fixed.** §6.3 withdraws those formulations and rewrites the passage as attribution, with an explicit statement of what is established, what is only co-occurrence, and what would be required to establish causation (a rolled-back-system reprice, not authorised and not attempted) |
| **4.** "bit-for-bit" equality claim (v1 `:269-276`) while the implementation performs float64 numeric comparison after coercion | **Fixed.** Withdrawn. §4.4 states the characterisation exactly: `float64` numerical equality at `1.0e-6` EUR absolute with all compared values proven finite on both sides, observed maximum difference `0.0`; no bitwise comparison is performed anywhere in the harness |

The review's accepted element of T7 — the reproducibility-versus-joint-batching
limitation — is retained unchanged and restated at §8.

---

## 8. Limitations carried forward (unchanged in substance from v1 §1.4 and §6)

These are carried deliberately and without weakening.

1. **The cache persists only two pricing outputs.** The pinned P2a cache carries
   exactly ten columns — `idhh`, `idperson`, `source_idhh`, `source_idorighh`,
   `source_idperson`, `ruro_decider`, `dgn`, `draw`, `ils_dispy`, `bsa00_s` — of
   which only `ils_dispy` and `bsa00_s` are priced outputs; the rest are keys and
   identifiers. `ils_origy`, `ils_sicdy`, `ils_tax` and `ils_ben` are **not
   stored**, so a stored-versus-repriced *difference* for those components does
   not exist and cannot be manufactured. The gate captures all four components and
   both RSA accumulators from the live repriced side for any captured row, so a
   divergence would be localisable — but the stored side is silent for them. This
   is the maximum decomposition the bound artifact supports. Widening it would
   require regenerating the cache with more columns: a separate, currently
   unauthorised decision.
2. **A PASS licenses reproducibility only.** It establishes that the M08
   baseline's own consumption is exactly reproducible through the production path
   at production geometry. It establishes nothing about pricing *redrawn* nodes.
   Because this gate reprices stored nodes, target-only and full-chunk geometry
   coincide here — an equivalence that holds *only* for parity.
3. **Joint batching is not licensed.** F3-R2B's finding stands unchanged:
   batch-context dependence is proven, and joint batching is not licensed. Any
   future redrawn-node pricing must use **target-only Option B geometry**, with
   the counterfactual on the target household alone. A PASS here is not a licence
   for joint-batch redrawing.
4. **Scope.** Only FR-2016 singles on the P2a artifact is gated. If the redraw path
   is ever pointed at a P3a cell, that cell needs its own gate and will meet the
   open P3a-build failure recorded at §6.2/§6.3.

---

## 9. Provenance

**Attempts published** under
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/` (U9-resolved
namespace; `complete/` never created or promoted):

| Attempt | Outcome |
|---|---|
| `20260805T175912Z_104548_c376a2bfd6b44912b60146ecc9a04f58_parity_STOPPED_HP_RECON` | attempt 1 — halted in reconstruction; fixed by the display shim (§5) |
| `20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE` | attempt 2 — bounded smoke, chunk `priced_00000` |
| `20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL` | attempt 3 — v1's full run; **certification withdrawn** (§0), artifact retained as history, untouched by this conversion |
| `20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL` | **attempt 4 — the gate of record for this report** |

Attempt 4 contains `gate_manifest.json`, eight `chunk_priced_*.json`, and
`reconstruction_log.txt`. Attempts 1–3 were not read, written, or promoted by this
run and retain their original modification times.

**Gate code (all three files untracked/new relative to MNL `520441a…`; two
modified by this conversion):**
`scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml` (**unchanged**,
`029d5ee6…979e81`); `scripts/welfare/m08_p2a_parity.py` (**modified**, T4
comparator fix, now `441b416d…181046`);
`scripts/welfare/run_m08_p2a_parity_gate.py` (**modified**, T4 aggregate/verdict,
now `69571a67…0b6467`).

**Read-only, unmodified:** the 8 pinned `fr_singles_pricing_p2a/priced_*.parquet`;
`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml`;
`outputs/p2a_singles2016/region_live_v1/inputs/fr_p2a_draws_geometry__singles.parquet`;
`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb` (nested repo clean
at `27756a06ea189339aa82915ed2124628afed20eb`);
`EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`; the FR EUROMOD system files;
`scripts/welfare/welfare_vdir.py` and `run_stage2_parity.py` (deliberately left as
they stand, so the documented failure remains reproducible as recorded);
`FR_P2a_m08_parity_gate_report_v1.md` and
`FR_P2a_m08_codex_production_path_review_v1.md`.

## Explicit scope statement

France 2016 singles P2a cell only. No production pricing code changed. No redrawn
node. No counterfactual covariate. No welfare number, no measure, no `V_i^dir`, no
re-estimation. No couples, no pooled years, no other cell. No stored consumption
value modified, replaced, or regenerated. EUROMOD executed solely for
parity-validation repricing, in one full-grid run. Uncommitted.

**Authorised by this report: nothing beyond the record of the gate.**
