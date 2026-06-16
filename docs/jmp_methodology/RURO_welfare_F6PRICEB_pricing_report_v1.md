# F6-PRICE-B — Preflight report (Task 0)

**Scope:** Singles only, 2016 cross-section (n = 1676 HHs; band 169,276 rows).
**System:** `FR_2015` / `FR_2016_a3`.
**Task:** Preflight identity gate before counterfactual pricing harness.
**Governance:** No commit. No Task 1 (equalized covariate spec not ratified — see below).

---

## TASK 0(a) — Canonicalization

Non-employed decider draws (draw ≥ 1, working = 0) in the staged band carry stale
`lhw` and `yem` values from the pre-draw actual state of the household.  These rows
would be zeroed by the `_overwrite_fixed` canonicalization step before counterfactual
EUROMOD pricing in the full run (Task 1).

| uid | grp | dec draws | non-emp | stale lhw | stale yem |
|----:|-----|----------:|--------:|----------:|----------:|
|    200001495800 | sm  | 100 |  10 |  10 |  10 |
|    200001496401 | sm  | 100 |   8 |   8 |   8 |
|    200001498400 | sm  | 100 |  10 |  10 |  10 |
|    200001502500 | sm  | 100 |   8 |   8 |   8 |
|    200001516900 | sm  | 100 |   8 |   8 |   8 |
|    200001504300 | sf  | 100 |   5 |   5 |   5 |
|    200001526601 | sf  | 100 |   9 |   9 |   9 |
|    200001527000 | sf  | 100 |  12 |  12 |  12 |
|    200001531200 | sf  | 100 |  13 |   0 |   0 |
|    200001533500 | sf  | 100 |   9 |   9 |   9 |
|    200001593700 | sm  | 100 |  14 |   0 |   0 |
|    200003504101 | sf  | 100 |  11 |  11 |  11 |
|    200003672000 | sm  | 100 |   7 |   7 |   7 |
| **Totals** | | | **124** | **97** | **97** |

**Task 0(a): DIAGNOSTIC.**  No pass/fail threshold here; confirming that 97
stale-lhw rows across 13 HHs will be zeroed by canonicalization.

---

## TASK 0(b) — Identity gate

Reference: stored bpool priced `ils_dispy_real` (= `ils_dispy` × CPI; CPI = 1.0000 for
2016, so `ils_dispy_real = ils_dispy`).  Stored values were computed by
`run_bpool_euromod_chunk.py` using **draw-first chunk ordering** (each EUROMOD call
processes all 1,676 HHs across a contiguous draw range; accumulator resets per call).

**Method:** Full-band uid-first EUROMOD pass (169,276 rows).  ALL 1,676 HHs × 101
decider draws overwritten in `band_run` with correct draw-specific input values
(`lhw`, `yem`, `yem00`, `yemxp`, `yivwg`, `yem_hour`, `working`) from the bpool priced
parquet before running EUROMOD.

EUROMOD elapsed: 34.8s.  Tolerance: 0.01 EUR.

| uid | grp | draws | max\|diff\| EUR | n > 0.01 EUR | max bsa00 diff | ID gate | RSA gate |
|----:|-----|------:|-----------:|-------:|-------:|:-------:|:-------:|
|    200001495800 | sm  | 100 | 944.169617 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001496401 | sm  | 100 | 413.930940 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001498400 | sm  | 100 | 720.362500 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001502500 | sm  | 100 | 725.925250 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001516900 | sm  | 100 | 294.882500 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001504300 | sf  | 100 | 546.183754 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001526601 | sf  | 100 | 650.299850 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001527000 | sf  | 100 | 559.421673 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001531200 | sf  | 100 | 1626.338256 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001533500 | sf  | 100 | 313.135298 | 100 | 5.27e+02 | FAIL | FAIL |
|    200001593700 | sm  | 100 | 920.202875 | 100 | 5.27e+02 | FAIL | FAIL |
|    200003504101 | sf  | 100 | 748.427825 | 100 | 5.27e+02 | FAIL | FAIL |
|    200003672000 | sm  | 100 | 606.798181 | 100 | 5.27e+02 | FAIL | FAIL |

**Identity gate (0b): FAIL** —
all 13 preflight HHs fail; max bsa00_diff ~ 526 EUR at all 100 draws; see Task 0(c) for root cause.

---

## TASK 0(c) — RSA-leakage control (structural finding)

All 13 preflight HHs have stored `bsa00_s = 0` at every draw in the bpool priced
parquet.  The full-band uid-first run produces `bsa00_s = 526 EUR` at **ALL 100 draws**
for **ALL 13 preflight HHs** — despite correct `yem00`/`yemxp` provided to every row.

**Root cause: batch-ordering geometry incompatibility.**

The French RSA benefit (`bsa00_s`) in EUROMOD FR_2015 uses two cross-household
cumulative person-count accumulators (`i_bsa00_cumpers_nw`, `i_bsa00_cumpers_w`)
that are summed over the **entire input file in row order**.  These were identified
by D-BEN as the sole batch-sensitive channel (`RURO_welfare_DBEN_benefit_program_diagnosis_v1.md`,
Task 3).  D-BEN showed that they diverge by ~4 × 10⁸ between batch-A (target-only)
and batch-B (joint-batch), both using uid-first full-band ordering.

The bpool priced parquet was built with **draw-first chunk ordering**: each EUROMOD
call processes one draw-range for all 1,676 HHs (≈ 84k rows per call, accumulator
resets between calls).  The F6 preflight uses **uid-first full-band ordering**: one
EUROMOD call processes all 101 draws for uid 1, then uid 2, … uid 1,676 (169,276
rows, accumulator runs continuously).

At any given HH's row position:

| Geometry | Rows preceding HH draw k | Approx. prior RSA-eligible rows |
|----------|--------------------------|----------------------------------|
| Draw-first chunk (bpool) | k draws × 1 prior HH per draw batch | small (draw-local) |
| Uid-first full-band (F6) | all 101 draws × all prior HHs | ~20–30 × larger |

The different accumulator values at each row position alter the FR RSA add-on
formula output, shifting `bsa00_s` from 0 (draw-first) to 526 (uid-first) for the
13 preflight HHs at every draw.  This is **not a fixable input error** — it is a
structural incompatibility between the two batch geometries.

**RSA-leakage gate (0c): FAIL** —
bsa00_s = 526 EUR at all 100 draws for all 13 HHs; structural geometry mismatch (see above).

---

## STRUCTURAL IMPLICATION FOR F6 DESIGN

The identity gate failure exposes a welfare-consistency risk for F6:

- **F4C/F5 actual values** (`V_i^IS`, `ils_dispy_real`) were computed from bpool priced
  parquet (draw-first chunk geometry) → `bsa00_s = 0` for these 13 preflight HHs.
- **F6 counterfactual values** under any uid-first or target-only full-band pricing
  geometry → `bsa00_s = 526` for the same HHs at non-employed draws.
- **Decomposition** comparing actual (bsa00_s=0) to counterfactual (bsa00_s=526)
  would inflate welfare changes for RSA-eligible HHs by ~526 EUR/month — a
  first-order artefact, not an economic effect.

For welfare consistency, F6 must use the **same batch-ordering geometry** as the bpool
(draw-first chunk runs) OR the F4C/F5 actual baseline must be recomputed using the
uid-first geometry.  **Operator input required before Task 1 can proceed.**

---

## GOVERNANCE STOP — two independent blockers

### Blocker 1: Identity gate FAIL (structural)

The preflight identity gate (Task 0b+c) **FAILS** due to a structural batch-geometry
incompatibility between the bpool reference (draw-first chunk) and the F6 pricing
geometry (uid-first full-band).  The identity gate is a prerequisite for Task 1:
without a validated pricing path, the full counterfactual run is not authorized.

### Blocker 2: Equalized covariate spec not ratified

`docs\jmp_methodology\JMP_decomposition_design_memo_v1.md` **does not exist on disk.**

The corrected F6 design prompt (commit `bde5085`, stored in `Prompts/replies/codex_!`)
states:

> F6 IMPLEMENTATION AUTHORIZED: NO
> F6-BOOT AUTHORIZED: NO
> REQUIRED NEXT INPUT: operator sign-off on the unresolved checklist.

The access operator is incomplete (hours subchannel undefined, sigma equalization
impossible, reference-state rules unratified).  Task 1 (full parallel counterfactual
pricing across 1676 households on 24 cores) is **NOT authorized** until BOTH
blockers are resolved.

---

## Final readout

**PREFLIGHT GATE (0b + 0c): FAIL**

| Sub-task | Verdict | Detail |
|----------|:-------:|--------|
| 0(a) canonicalization | DIAGNOSTIC | 97 stale-lhw rows across 13 HHs |
| 0(b) identity gate    | FAIL       | tol = 0.01 EUR; STRUCTURAL FAIL: uid-first vs draw-first geometry incompatibility |
| 0(c) RSA leakage      | FAIL       | tol = 1e-06 EUR; bsa00_s = 526 EUR at all 100 draws, all 13 HHs; structural |

**READY FOR F6-RUN ACCESS OPERATOR: NO**

Two blockers: (1) identity gate FAIL (geometry incompatibility — requires design
decision on batch ordering before Task 1 can be validated); (2) equalized covariate
spec not ratified (JMP_decomposition_design_memo_v1.md not on disk).

---

### Provenance

- Band: `fr_p3a_bpool_engine_ready_staged_threeB1__singles.parquet`, 169,276 rows, 1676 HHs, year_tag=2.
- Reference: `fr_p3a_bpool_priced__2016__singles.parquet` (stored bpool chunk-based pricing).
- EUROMOD: `FR_2015` / `FR_2016_a3`, 34.8s for full-band pass.
- Manifest: `outputs\welfare\fastlane\f6_price_b_manifest_v1.json`
- Immutable F3/F3-R2/F3-R2B artifacts + fastlane_anchors_v3/* not touched.
- No commit.
