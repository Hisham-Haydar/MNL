# Correction Notice - 2026-06-03

Two-I (`docs/jmp_methodology/RURO_welfare_stage2_twoH_validation_v1.md`) supersedes the
model-fit reading of near-zero `P_chosen` in Section 5. The near-zero probability / rank
interpretation came from the importance-sampling-corrected V, dominated by the
`-log_prior` proposal correction; it should not be cited as evidence of severe couples
model misfit. The contamination measurement remains a first-order screen at fixed
`theta_hat`, not a re-estimation.

# RURO Welfare — Stage Two, Increment Two-G: couples clean-reprice instrument validation and chosen-alternative contamination

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-G only — validate the couples clean-reprice
instrument and measure chosen-alternative contamination. **Measurement/audit-only.**
**Status:** complete. **Materiality classification: POTENTIALLY MATERIAL (bounded).**
The chosen alternative's consumption is provably the EUROMOD-priced stored value, it is
collision-exposed for 100% of couples, and a large clean-reprice sample shows it is
contaminated in ~76% of households (household-joint disposable income off by a median
≈ €196/month, up to ≈ €1,526). A first-order screen finds the per-household
log-likelihood contribution shifts by a median ≈ 0.048 nats (max ≈ 1.25); whether this
moves `theta_hat` cannot be settled without re-estimation (out of scope). A separate,
**unresolved** stored-target reproducibility gap (the 3 Two-F singleton failures) is
diagnosed as **not** the `draw_joint=0` collision and **not** an instrument defect.

> **No W^3 welfare finding is produced and no measure beyond W^3 is touched.** Nothing
> was re-estimated; no redrawn node was priced; no `V_i^dir` was computed; no 2×/4×
> growth was run; and no engine-ready / priced / precompute / chunk parquet was written
> or overwritten. EUROMOD was run only on bounded clean-reprice subsets of **existing**
> couples nodes. Not committed automatically.

---

## 1. Two-E / Two-F singleton-control reconciliation (Task 1)

The diagnostic cases are **derived from prior provenance** (the Two-E assessment-unit-diag
JSON and the Two-F reprice JSON), not hardcoded in source: the Two-E case is the first
Rung-2 PASS node of the couples singleton ladder; the Two-F cases are the
`singleton_control` FAIL nodes. The provenance paths and the structural production
draw-band live in config (`welfare.stage2.couples_contamination_audit.task1_singleton_reconcile`).

**No contradiction.** The single couples singleton node tested in **both** increments —
HH `200001483000`, node `(draw_joint=1, draw_male=1, draw_female=2)`, 2016 — **passes in
both** Two-E and the Two-F path, reproducing the stored value to machine zero
(`stored = iso = production-batch = collision-free = 130.00`). The 3 Two-F singleton
"failures" are **different households** Two-E never tested — a **sample difference**, not
a same-construction contradiction.

**Diagnosis of the 3 Two-F singleton failures.** Production prices couples in draw-bands;
chunk 0 covers `draw_joint [0, 150)` across **all** households in one EUROMOD batch
(verified from chunk meta), so `draw_joint=0`'s collision pair shares the batch with
`draw_joint=1`. For each failing household I repriced the node four ways and compared the
parity-relevant `ils_ben` on each decider (nominal):

| HH (year) | decider | stored | isolated clean | production-band batch (stamp on draw_joint, [0,150)) | collision-free batch | prod = stored? | clean = collision-free? |
|---|---|---|---|---|---|---|---|
| 200001487600 (2016) | 148760001 | 362.83 | 362.83 | 362.83 | 362.83 | ✓ | ✓ |
| 200001487600 (2016) | 148760002 | **92.77** | **0.00** | 0.00 | 0.00 | ✗ | ✓ |
| 300001801900 (2017) | 180190001 | 296.83 | 296.83 | 296.83 | 296.83 | ✓ | ✓ |
| 300001801900 (2017) | 180190002 | **432.83** | **170.59** | 170.59 | 170.59 | ✗ | ✓ |
| 300001804500 (2017) | 180450001 | 468.42 | 468.42 | 468.42 | 468.42 | ✓ | ✓ |
| 300001804500 (2017) | 180450002 | **313.10** | **220.22** | 220.22 | 220.22 | ✗ | ✓ |

All four reprices (isolated, production-band, collision-free) **agree** on a clean value;
the **stored value alone differs** and is **not reproduced by any of them** — including a
faithful replay of the production chunk-0 band with production `draw_joint` stamping
(which *does* fire 8 TUDef warnings, yet still returns the clean value, not the stored
one). The EUROMOD **inputs are identical** between precompute-long and priced for the
failing decider (lhw, yivwg, yem, bch00, all benefit inputs match to machine precision),
so this is **not** a stale-input mismatch.

**Classification:** these singleton failures are a **stored-target reproducibility gap** —
the stored priced value was produced under an effective EUROMOD state that the current
precompute-long inputs do not reproduce, even under the exact production batching/stamping.
It is **not** the `draw_joint=0` collision (the collision-free batch reproduces the same
clean value the colliding production-band batch does), **not** an instrument defect (the
instrument reproduces every non-failing decider and the Two-E pass node exactly), and
**not** a code-path contradiction. Its exact mechanism is **UNRESOLVED** by this bounded
audit (candidate, unproven: a full-chunk, ~1.13M-row tax-unit attribution effect not
reconstructible from a single-household band — note one failing decider's stored value
≈ its partner's child benefit, suggesting a cross-decider benefit attribution).

---

## 2. Status of the clean-reprice instrument (Task 2)

**Benchmark clean reprice (the instrument):** one existing node, isolated household
roster, original IDs, raw-schema inputs only, nominal output comparison on decider rows
against stored priced, full node key `(stacked_hh_uid, draw_joint, draw_male, draw_female)`.

**USABLE for chosen-contamination measurement.** All three usability conditions hold:

1. *Two-E pass node reproduces:* the Two-E singleton pass node reproduces to machine zero
   under the current implementation (§1).
2. *Singleton failures explained or reported unresolved:* the 3 singleton-control failures
   are diagnosed as a **stored-target reproducibility gap, mechanism unresolved** — not an
   instrument defect and not the collision (§1). They are clearly reported, not swept up.
3. *Clean isolated path is well-behaved:* across the 900-household Task-4 sample the clean
   isolated/collision-free path produced **0 TUDef warnings** and reproduced the
   income/contribution components `ils_origy` and `ils_sicdy` to **machine zero**
   (max over sample = 0.0 for both).

A **collision-free full-node-key stamping** scheme (stamp on `(draw_joint, draw_male,
draw_female)` instead of `draw_joint`, remapping kinship consistently) is used for
*batched* diagnostics only — Task 1 verified it equals isolated clean repricing to machine
tolerance on every decider tested. It is **diagnostic only, not production-ready**.

---

## 3. Chosen-alternative consumption source (Task 3)

**Confirmed: the chosen alternative's consumption is the EUROMOD-priced stored value, not
an independent observed-income value.** Evidence, traced precompute → priced →
engine-ready → V grid:

- The engine-ready builder (`harmonise_bpool_engine_ready.py`, documented) sets
  `consumption = household-joint ils_dispy_real` (couples: sum of per-person
  `ils_dispy_real` over the tax unit) and `c_norm = consumption / c_scale`,
  `c_scale = mean(consumption)`. `ils_dispy_real = ils_dispy × CPI(year)` (the
  EUROMOD-priced nominal disposable income, deflated).
- The chosen alternative is `(draw_joint=0, draw_male=0, draw_female=0)` for **100% of
  households** (verified: within `draw_joint=0`, `is_chosen_joint=1` is always at
  `(0,0,0)`); its consumption is summed from the priced rows with `is_chosen_joint=1`.
- **Empirical check:** `c_norm × c_scale` (engine-ready) equals the priced joint
  `ils_dispy_real` (sum over the tax unit, `is_chosen_joint=1`) to **diff = 0.0** for a
  per-year household in each of 2015/2016/2017. `c_scale = 3936.008863`.
- **Alignment of the V grid to node keys** (reproducing the estimator's load + sort order):
  max abs `|consumption(data object) − c_norm(reproduced order)| = 0.0`.

So the consumption that enters the estimator's `V_chosen` is exactly the contaminated
EUROMOD-priced chosen-node value — the chosen channel is real.

---

## 4. Chosen-alternative contamination measurement (Task 4)

Large deterministic sample: first **300 households/year × 3 years = 900 households**;
clean-reprice the chosen node `(0,0,0)` only (collision-free batched, == isolated clean),
compare to stored **nominal**.

- **Clean-reprice failure rate: 76.1% (685/900).**
- `ils_origy`, `ils_sicdy` reproduce to **machine zero** over the whole sample (income and
  contributions faithful); divergence localises to **`ils_ben`** (528 hh) and **`ils_tax`**
  (157 hh). 0 TUDef warnings.
- **Household-joint disposable income `|clean − stored|` (nominal, €/month):**

| statistic | value |
|---|---|
| median | 195.98 |
| mean | 307.22 |
| 90th pct | 806.79 |
| 99th pct | 1,136.39 |
| max | 1,526.38 |

- **Share of households above material thresholds (|Δ joint disposable|, €/month):**

| threshold | share | count |
|---|---|---|
| > €1 | 76.1 % | 685 |
| > €10 | 75.7 % | 681 |
| > €50 | 72.3 % | 651 |
| > €100 | 67.2 % | 605 |
| > €250 | 44.1 % | 397 |

The chosen alternative — universally exposed and entering the likelihood directly — is
**materially mis-priced in the stored baseline for roughly three-quarters of couples**, by
amounts that are large relative to monthly disposable income (median ≈ €196, and ≈ 44 % of
households exceed €250/month).

---

## 5. First-order theta_hat influence screen (Task 5; NOT a re-estimation)

Reusing the welfare/estimator couples V machinery at `theta_hat`, replacing **only** the
chosen alternative's consumption with its clean reprice (all other alternatives fixed,
`theta_hat` unchanged), over the same 900 households:

| quantity | median | 90th pct | 99th pct | max |
|---|---|---|---|---|
| `|Δ V_chosen|` (nats) | 0.0476 | 0.1533 | 0.2657 | 1.2463 |
| `|Δ P_chosen|` | 1.8 × 10⁻¹² | 5.2 × 10⁻¹¹ | 4.9 × 10⁻⁹ | 8.4 × 10⁻⁶ |
| `|Δ ll_i|` (nats) | 0.0476 | 0.1533 | 0.2657 | 1.2463 |

**Stored chosen probability `P_chosen`** is *extremely small*: median **8.0 × 10⁻¹¹**, mean
2.2 × 10⁻⁸, max 1.0 × 10⁻⁵, min 8.8 × 10⁻¹⁹. The model assigns **near-zero probability to
the observed chosen alternative** for couples (a notable model-fit observation in its own
right).

**Interpretation (bounded, cautious).** Because `P_chosen ≈ 0`, the household logsum
denominator is essentially insensitive to the chosen alt, so `|Δ P_chosen|` is negligible
and `|Δ ll_i| ≈ |Δ V_chosen|`: the contamination perturbs each couple's log-likelihood
**directly through the `V_obs` term** by a median ≈ 0.048 nats (max ≈ 1.25). Summed over
the ~7,438 couples this is a few hundred nats of first-order log-likelihood shift — not
obviously negligible in aggregate — but this is a **first-order screen at fixed
`theta_hat`**, **not** a re-estimation and **not** proof that `theta_hat` moves. The
near-zero `P_chosen` means the *gradient* channel through the choice probabilities is tiny;
the influence, if any, runs through the direct `V_obs` term.

---

## 6. Materiality classification

**POTENTIALLY MATERIAL (bounded).**

- *Source (Task 3):* the chosen-alt consumption IS the EUROMOD-priced stored value
  (alignment 0.0); contamination of it is contamination of an estimator input.
- *Prevalence/magnitude (Task 4):* ~76 % of couples have a contaminated chosen node;
  joint disposable off by a median ≈ €196/month (≈ 44 % exceed €250/month).
- *Influence (Task 5):* direct per-household `|Δ ll_i|` ≈ 0.048 nats median (max 1.25),
  but choice-probability channel negligible because `P_chosen ≈ 0`.

It is **not negligible** (universal, direct, materially mis-priced) and **not proven
material** (no re-estimation; the probability-gradient channel is tiny). It is **not
"nontrivial-but-likely-small"** at the per-household magnitude level, but the aggregate
parameter consequence is genuinely **unresolved** without a re-estimation, which is out of
scope here. A separate stored-target reproducibility gap (the singleton residual, §1)
remains **unresolved** as to mechanism.

**Implication (stated, not actioned):** any decision to repair the stored couples baseline
or to re-estimate must (a) target the chosen node's contamination, (b) resolve the
singleton stored-target gap, and (c) be validated by an all-nodes clean-reprice parity gate
— all under separate authorisation.

---

## 7. Files

- **Source:** `scripts/welfare/welfare_chosen_contamination.py` (instrument + collision-free
  stamping + reprice helpers), `scripts/welfare/run_stage2_chosen_task1.py` (Task 1
  reconciliation), `scripts/welfare/run_stage2_chosen_measure.py` (Task 4 + Task 5).
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_chosen_task1.json`,
  `outputs/welfare/stage1_w3/stage2_chosen_measure.json`.
- **Diagnostic CSV:** `outputs/welfare/stage1_w3/stage2_chosen_measure_per_hh.csv`.
- **EUROMOD consoles:** `outputs/welfare/stage1_w3/stage2_chosen_task1_euromod_console.log`,
  `outputs/welfare/stage1_w3/stage2_chosen_measure_euromod_console.log`.

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. Nothing was
re-estimated; no `V_i^dir` was computed; no redrawn node was priced; and no engine-ready /
priced / precompute / chunk parquet was written or overwritten. EUROMOD was run only on
bounded clean-reprice subsets of existing couples nodes. Repair of the stored couples
baseline, resolution of the singleton stored-target gap, and any re-estimation remain out
of scope and require separate authorisation.
