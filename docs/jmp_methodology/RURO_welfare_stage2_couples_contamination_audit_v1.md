# RURO Welfare — Stage Two, Increment Two-F: couples collision-exposure audit

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-F only — audit of couples collision exposure in
the stored baseline. **Audit-only.**
**Status:** complete. **Materiality verdict: POTENTIALLY MATERIAL (bounded).** Exposure
is *structurally universal* at the alternative level (every couple's chosen alternative
is collision-exposed) but *numerically tiny* in count (0.222 % of alternatives); the
model-implied probability mass on exposed alternatives is small for most households with
a non-negligible right tail; and a bounded clean reprice shows the stored value on
exposed nodes is *frequently and materially* wrong (household-joint disposable income off
by a median ≈ €245/month on chosen-exposed nodes). A residual, non-collision baseline of
stored-vs-clean couples non-reproducibility also exists and is not fully explained here.

> **No W^3 welfare finding is produced and no measure beyond W^3 is touched.** Nothing
> was re-estimated; no redrawn node was priced; no `V_i^dir` was computed; no 2×/4×
> growth was run; and no storage/precompute/priced/chunk/engine-ready parquet was
> written. EUROMOD was run only on a bounded clean-reprice sample of **existing** couples
> nodes (Task 3). Not committed automatically.

---

## 0. Definitions, mapping, and the no-STOP determination

**Full couples node key:** `(data_year, stacked_hh_uid, draw_joint, draw_male, draw_female)`.
**Collision block:** a `(data_year, stacked_hh_uid, draw_joint)` group containing **more
than one** distinct `(draw_male, draw_female)` pair. Every alternative in a collision
block is **collision-exposed** (production `_stamp_draw_ids` stamps couples on
`draw_joint`, so the distinct alternatives in such a block collapse onto the same stamped
`idperson`).

**Build provenance (not inferred — documented):** `build_bpool_precompute.py` gate G2
states verbatim *"draw_joint=0 intentionally shared by chosen+first sim cell."* So the
collision is a **known build convention**: each household's chosen alternative and the
first simulated cell share `draw_joint=0`.

**Mapping determination (no STOP):** the audit node key is present **in both** the
priced/precompute parquets **and** the engine-ready couples parquet
(`fr_p3a_bpool_engine_ready__couples.parquet`). The likelihood machinery
(`welfare_core` → `build_data_objects` → `precompute_data_couples`) orders couples rows by
`sort_values(["stacked_hh_uid","draw_joint"])` then a stable `sort_values(["idhh","year_tag"])`;
both are reproduced here exactly, and an **alignment gate** asserts that the reproduced
order's `c_norm` equals the data object's `consumption` to machine tolerance. The gate
passed with **max abs = 0.0**, so the V grid maps to node keys **unambiguously**. No STOP.

Terminology discipline (per the increment): nodes are **collision-exposed /
potentially contaminated** until a clean reprice confirms a nonzero stored-vs-clean
difference. Not every exposed node is materially contaminated.

---

## 1. Alternative-level prevalence (no EUROMOD)

Engine-ready couples baseline: **7,438 households × 901 alternatives = 6,701,638
alternatives**.

| year | households | alternatives | exposed alts | share exposed | hh w/ collision | chosen-alt exposed |
|---|---|---|---|---|---|---|
| 2015 | 2,566 | 2,311,966 | 5,132 | 0.222 % | 2,566 (100 %) | 2,566 / 2,566 (100 %) |
| 2016 | 2,577 | 2,321,877 | 5,154 | 0.222 % | 2,577 (100 %) | 2,577 / 2,577 (100 %) |
| 2017 | 2,295 | 2,067,795 | 4,590 | 0.222 % | 2,295 (100 %) | 2,295 / 2,295 (100 %) |
| **pooled** | **7,438** | **6,701,638** | **14,876** | **0.222 %** | **7,438 (100 %)** | **7,438 / 7,438 (100 %)** |

**Distribution of alternatives per `draw_joint` block (pooled):** 6,686,762 blocks carry
exactly 1 alternative; **7,438 blocks carry exactly 2** — i.e. **every household has
exactly one collision block, always at `draw_joint=0`, always with two alternatives.**
Exposed alternatives = 2 × 7,438 = 14,876.

**Observed/chosen-node exposure (reported separately):** the chosen alternative
(`is_chosen_joint=1`) is collision-exposed for **100 % of households** — it is always one
of the two members of the `draw_joint=0` block (build convention). The
`(draw_male=0, draw_female=0, draw_joint=0)` node is exposed for all 7,438 households.

**Reading:** exposure is *universal per household but minimal per household* — exactly two
of 901 alternatives, and one of them is the alternative the household actually chose.

---

## 2. Likelihood-relevance at theta_hat (reuse of V machinery; NO re-estimation)

Using the estimator/welfare couples V-extractor at `theta_hat` (47 params,
`theta_hat_realdata_901_v1.csv`), the per-household model-implied probability mass on the
two collision-exposed alternatives (alignment gate max abs = 0.0):

| statistic | collision-exposed prob mass |
|---|---|
| mean | 1.045 × 10⁻³ |
| median | 1.591 × 10⁻⁴ |
| 90th pct | 1.85 × 10⁻³ |
| 99th pct | 1.57 × 10⁻² |
| 99.9th pct | 5.38 × 10⁻² |
| max | 1.286 × 10⁻¹ |

**Share / count of households above probability-mass thresholds:**

| threshold | share of households | count |
|---|---|---|
| 1 × 10⁻⁶ | 99.80 % | 7,423 |
| 1 × 10⁻⁴ | 59.65 % | 4,437 |
| 1 × 10⁻³ | 17.10 % | 1,272 |
| 1 × 10⁻² | 1.82 % | 135 |

(10 households exceed 5 %; 3 exceed 10 %.)

**Chosen-alt exposure:** 7,438 / 7,438 households have their **chosen** alternative
exposed. This is the load-bearing fact for likelihood relevance: the chosen alternative's
consumption enters the log-likelihood **directly** through `V_obs,i` (not only through the
softmax denominator), so any contamination of the chosen node's consumption perturbs the
likelihood of **every** couple, weighted by how much the rest of the response depends on
it.

**Caution (per the increment):** this is a likelihood-**relevance** screen, not proof
that `theta_hat` moves. Most households carry tiny exposed mass; the relevance is
concentrated in (a) the universal chosen-node channel and (b) a thin right tail of
households with non-negligible exposed mass.

---

## 3. Bounded clean-reprice magnitude check (EUROMOD, existing nodes only)

Deterministic stratified sample (first-by-uid within stratum), per year ×
{2015, 2016, 2017}, clean-repriced **in isolation** with the correct full node key and
original household relationships (no stamping collision): **72 nodes** total —
24 chosen-exposed, 24 nonchosen-exposed, 24 singleton-`draw_joint` controls.

Clean vs **stored nominal**, `|clean − stored|` (tol = 1 × 10⁻⁶):

| stratum | nodes | clean=stored (PASS) | FAIL | `ils_ben` median / max | `ils_tax` median / max | joint-dispy median / max |
|---|---|---|---|---|---|---|
| **chosen-exposed** | 24 | 8 (33 %) | 16 | 130.0 / 626.2 | 69.5 / 477.7 | **245.0 / 1270.1** |
| **nonchosen-exposed** | 24 | 6 (25 %) | 18 | 92.3 / 361.5 | 1.6 / 441.7 | 118.1 / 778.9 |
| **singleton control** | 24 | 21 (87.5 %) | 3 | 0.0 / 262.2 | 0.0 / 1.3 | 0.0 / 260.9 |

`ils_origy` and `ils_sicdy` reproduce to **machine zero** in every stratum — income and
contributions reprice faithfully; the divergence is localised to **`ils_ben`** (and the
benefit-dependent `ils_tax`), exactly as Two-D/Two-E found.

**Interpretation:**
- On **collision-exposed** nodes the stored value is **frequently (~70 %) and materially**
  wrong: household-joint disposable income differs by a median ≈ €245/month
  (chosen-exposed), up to €1,270/month. These nodes' stored benefits are
  collision-contaminated, confirming Two-E at population-sample scale.
- **Singleton controls mostly reproduce (87.5 %)**, confirming that clean isolated
  repricing of a *non-collision* couples node generally recovers the stored value — so the
  contamination is **specifically associated with collision exposure**: exposure roughly
  **triples** the clean-reprice failure rate (≈ 67–75 % vs 12.5 %).

**A residual, non-collision baseline (reported, not overstated).** 3 of 24 singleton
controls (all `draw_joint=1`, **zero TUDef warnings**, block has a single alternative)
also fail, localised to `ils_ben` on **one** of the two deciders (e.g. stored 432.83 vs
clean 170.59). A minimal two-`draw_joint` stamped-batch reconstruction did **not**
reproduce the stored contaminated value (it returned the clean value), so the exact
production mechanism for these singleton failures is **not pinned down by this bounded
audit** — the stored values were produced inside a full production draw-band chunk that
this audit does not reconstruct. Candidate (unproven) explanation: batch-level
assessment-unit corruption spilling from the household's `draw_joint=0` collision onto its
other nodes priced in the same chunk. This residual means **not all** stored-vs-clean
couples divergence is attributable to the collision per se; a ~12 % baseline of
non-reproducibility exists independently in this sample.

---

## 4. Approximate likelihood-impact screen (first-order; NO re-estimation)

For the clean-repriced sample only (a transparent, bounded diagnostic — **not** a
re-estimated likelihood and **not** proof of parameter movement):

- **Chosen-exposed nodes (24):** median `|Δ ils_dispy|` = €245.0, max €647.1. Because the
  chosen node enters `V_obs,i` directly, this magnitude is a **first-order, per-household**
  perturbation of the observed alternative's consumption for the (universal) chosen
  channel.
- **Nonchosen-exposed nodes (24):** median `|Δ ils_dispy|` = €176.5, max €483.6; weighting
  each by its household's `theta_hat` exposed-probability mass gives a
  mass-weighted `|Δ ils_dispy|` with **median ≈ 0.019** and **max ≈ 1.10** — i.e. for
  *nonchosen* nodes the contribution is throttled by the small choice probability, so the
  nonchosen channel is **likely small** for most households.

**Bounded plausibility statement:** the nonchosen channel is, for most households, small
(tiny probability weight). The **chosen channel is the concern**: it is universal (every
couple), enters the likelihood directly, and carries a clean-vs-stored consumption error
of order €100–250/month at the median (up to ~€650–1270). Whether this moves `theta_hat`
materially cannot be settled without a re-estimation (explicitly out of scope here), but
the magnitude × universality of the chosen channel makes a **non-negligible** influence
**plausible** rather than dismissible — hence the "potentially material" verdict.

---

## 5. Materiality assessment

**POTENTIALLY MATERIAL (bounded).** Evidence:

- *Prevalence:* exposure is **count-tiny (0.222 % of alternatives)** but **household-universal
  (100 %)** and, critically, **always includes the chosen alternative**.
- *Likelihood relevance:* exposed probability mass is small for most households (median
  1.6 × 10⁻⁴) with a thin tail (135 hh > 1 %; max 12.9 %), **plus** a universal direct
  chosen-node channel.
- *Magnitude:* on collision-exposed nodes the stored benefit is wrong frequently (~70 %)
  and materially (joint-dispy median ≈ €245/month, max ≈ €1,270/month); singleton controls
  mostly reproduce (87.5 %), tying the contamination to exposure.

It is **not negligible** (the chosen node is universally exposed and materially mis-priced)
and **not proven material** (no re-estimation; nonchosen mass is mostly tiny). It is also
**not unresolved** as to mechanism for the *collision* nodes (clean ≠ stored, exposure-tied)
— though the *singleton* residual is unresolved.

**Repair-vs-rebuild implication (stated, not actioned):** because the contamination is
**one collision block per household at `draw_joint=0`, always two alternatives, always
including the chosen one**, it is *structurally localised and uniform* — a targeted repair
(re-pricing each household's `draw_joint=0` pair under a collision-free full-node-key
stamping) is well-scoped, **but** the residual singleton-control failures warn that a
repair must be **validated by an all-nodes clean-reprice parity gate**, not assumed to be
confined to the `draw_joint=0` pair. Whether to repair locally or rebuild couples priced
storage with collision-free stamping is a **separate authorised decision**; this audit
only quantifies exposure and materiality.

---

## 6. Files

- **Audit source:** `scripts/welfare/welfare_couples_contamination_audit.py`
  (Task 1 prevalence + Task 2 likelihood-relevance, with the alignment gate),
  `scripts/welfare/run_stage2_couples_audit.py` (Tasks 1–2 runner),
  `scripts/welfare/run_stage2_couples_reprice.py` (Task 3 clean-reprice + Task 4 screen;
  reuses the Two-E ladder helpers).
- **Config block:** `welfare.stage2.couples_contamination_audit` in
  `scripts/welfare/configs/welfare_stage1_w3.yaml`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage2_couples_contamination_audit.json`
  (prevalence + likelihood-relevance) and
  `outputs/welfare/stage1_w3/stage2_couples_reprice.json` (Task 3/4).
- **Diagnostic CSV:** `outputs/welfare/stage1_w3/stage2_couples_exposed_mass_per_hh.csv`
  (per-household exposed probability mass + chosen-exposed flag).
- **EUROMOD console:** `outputs/welfare/stage1_w3/stage2_couples_reprice_euromod_console.log`.

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. Nothing was
re-estimated; no redrawn node was priced; no `V_i^dir` was computed; no 2×/4× growth was
run; and no storage/precompute/priced/chunk/engine-ready parquet was written. EUROMOD was
run only on a bounded clean-reprice sample of existing couples nodes. Production
redrawn-node pricing, repair of the stored couples baseline, and any re-estimation remain
**out of scope** and require separate authorisation.
