# RURO Welfare — Stage Two, Increment Two-O: baseline-provenance / controlled-re-estimation decision memo

**Date:** 2026-06-03
**Increment:** STAGE TWO, INCREMENT TWO-O only — decision memo for the failed Two-N
full-scale headline-parity gate and the corrected-baseline / controlled-re-estimation
decision.
**Audience:** supervisor (decision-making).
**Sources read:** the Two-N validation report and its two provenance JSONs
(`RURO_welfare_stage2_full_rebuild_validation_v1.md`, `stage2_full_rebuild_staging.json`,
`stage2_full_rebuild_validation.json`); the Two-L cross-track diagnosis
(`RURO_welfare_stage2_cross_track_benefit_residual_diagnosis_v1.md`); the Two-M
write-back-fix validation (`RURO_welfare_stage2_chunk_writeback_fix_validation_v1.md`); the
certified baseline spec `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`
and its recovery-gate docs (`RURO_jax_recovery_gate_tlmpin_901_v1.md`).

---

## 1. Purpose and document class

**This is a decision memo, not an implementation contract and not an authorisation.** It does
not authorise — and must not be read as authorising — a production rebuild, a swap of staging
into production, a re-estimation, an EUROMOD re-execution, the computation of `V_i^dir`, the
pricing of any redrawn node, or the promotion of `W^3` or any measure beyond `W^3`. Its sole
function is to convert the Two-N finding into a clear decision record: what is now known, what
is excluded, what consequence it has for the certified estimate, the available options, the
common test that adjudicates between them, and a recommended next decision **to be separately
authorised**. Nothing in this memo has been executed.

---

## 2. What Two-N proved

Two-N ran the full production rebuild under the Two-M-patched chunk worker (all-simulated-output
write-back) to a required staging directory, then gated it against the existing stored
production at full scale. The established facts:

- **The full staging rebuild completed.** 21/21 chunk runs OK, 0 failed, 0 timed out; every
  chunk matched the stored production **row count exactly** (e.g. 2015 couples c0 = 1,276,554;
  2017 couples c0 = 1,139,446); ~22.5 M rows; wall ≈ 2.17 h; output to
  `…/EUROMOD-STORAGE/new_data/staging_twoN/` only.
- **No production parquet was swapped, overwritten, moved, or deleted.** All rebuild output
  went to staging; the production priced files are untouched.
- **Component coherence was FIXED by the all-simulated-output write-back.** On the rebuilt
  data, `ils_ben = ils_pen + ils_benmt + ils_bennt` and the `ils_dispy` identity hold with
  **0 violations** in every cell (the stored data violated these on 58–59 % of singles /
  32–40 % of couples decider rows), and the simulated components now **vary across draws**
  (94–98 % of households). The Two-L/Two-M staleness bug is repaired.
- **Full-scale headline parity FAILED.** In every cell — singles and couples — the rebuilt
  headline `ils_ben` / `ils_dispy` / `ils_dispy_real` differ from the stored production above
  machine tolerance on the benefit-recipient rows: singles ≈ 2.0–4.3 %, couples ≈ 4.5–8.4 % of
  decider rows; max |Δ| up to **€1,161** (`ils_ben`, 2015 couples). Crucially, **income and
  contributions reproduce exactly**: `ils_origy` and `ils_sicdy` are machine-zero on every row.
  The divergence is **exclusively the means-tested benefit**.
- **The stored production `ils_ben` / `ils_dispy` are not reproducible from current inputs and
  current EUROMOD execution.** The rebuild is **deterministic** (a re-run reproduces it to 0.0)
  and **internally coherent**, so the mismatch is a stable property of the stored target, not of
  the rebuild.
- **The staged coherent rebuild would change `ils_dispy_real` on benefit-recipient rows.**
  Because `ils_dispy_real` (and hence `c_norm`) is the estimator's consumption input, the
  rebuilt value differs from the stored value precisely on those rows.
- **Therefore no production swap is allowed.** Swapping staging into production would move the
  certified estimator's consumption input on benefit-recipient rows — exactly the failure mode
  the headline-invariance gate exists to prevent. Two-N stopped at the gate; no swap was
  performed; `singles_ready = couples_ready = overall_ready_for_separate_swap = false`.

---

## 3. What explanations were tested and rejected

Two-N and Two-L between them tested, and the evidence rejects, every reproducible cause:

- **A year/system-only explanation is rejected.** The `ils_ben` failure rate does not isolate
  to the non-2016 (lagged FR_2015 / FR_2016) systems: it is 2.0 % / 2.0 % / 4.3 % (singles) and
  4.5 % / 4.6 % / 8.4 % (couples) for 2015 / 2016 / 2017. The latest system (2017 → FR_2016) is
  the *worst*, and 2015 ≈ 2016 — a rising-by-year gradient driven by population/benefit-mix, not
  a single defective policy system. Two-L separately repriced failing nodes under all three
  available systems (FR_2014/2015/2016) with the dataset fixed: the stored value reproduced
  under **none** of them.

- **CPI / uprating / real-wage deflation as the cause is rejected.** Two checks: (a) the
  rebuilt/stored `ils_ben` ratio on failing rows is **not constant** (median 0.71, std 0.28,
  range 0–0.92); a scalar uprate or deflation factor would give a tight constant ratio (~0.9886),
  so the gap is **structural, not scaling**. (b) The EUROMOD earnings inputs fed by the rebuild
  are **identical** to production (`yem`, `yem00`, `yivwg`, `lhw`, `bch00` match the stored priced
  values exactly), and the current precompute-long equals its own `.pre_wage_deflation.bak` to
  **ratio 1.00000 over 3.73 M rows**. The two-deflation architecture is the reason: the wage
  deflation only ever touched the *estimator-facing* wage columns, never the *nominal* EUROMOD
  inputs (build-confirmed: keep EUROMOD earnings nominal upstream to prevent double deflation).
  A pre-EUROMOD uprate rewind would therefore move inputs that **already match** production and
  would not close the gap.

- **Missing household roster members is rejected.** The failing couples node
  (HH 300001801900) carries its **complete 5-member roster** (2 adults + 3 children) in the
  EUROMOD input across all draws; no members are missing.

- **Stamping / chunking differences are rejected.** The single-pass pricer
  (`run_bpool_euromod.py`) and the chunk worker (`run_bpool_euromod_chunk.py`) use
  **byte-identical `_stamp_draw_ids` logic** and the **same 6-band `[0,150)…[750,900)`** chunking.
  The stored priced `idperson` is the un-stamped original (IDs restored post-pricing),
  consistent across both runners. Neither stamping nor granularity explains the gap.

- **Nondeterminism is rejected.** Re-running a cell reproduces the staging `ils_ben` /
  `ils_dispy` to **max abs 0.0**. The mismatch vs stored is stable, not run-to-run variation.

- **Silent drift between `.pre_wage_deflation.bak` and the current on-disk files is rejected.**
  The backups of both precompute and priced are **byte-identical to the current files** (0
  differing columns; priced `ils_ben`/`ils_dispy`/`ils_dispy_real` max diff 0.0). The current
  on-disk inputs and the stored priced ARE the production artefacts — there is no hidden input
  substitution to recover.

**Narrowed conclusion.** Every reproducible cause is excluded. The stored production
`ils_ben` / `ils_dispy` are not reproducible from the current inputs by any faithful EUROMOD run
(isolated, bounded, population-scale, full-chunk, or single-pass). The means-tested divergence
originates **inside EUROMOD's tax-unit / assessment-unit resolution under the original production
execution**, whose exact state (EUROMOD model version, dataset vintage, or a transient run
condition) the current repository and data do not reconstruct. This is a **stored-target
reproducibility gap at the EUROMOD-execution level** — not an input, uprating, roster, stamping,
chunking, or determinism bug.

---

## 4. Consequence for the certified estimate

- The certified estimate (47-param `joint_pooled_v1_bll0_tlmpin`, recovery-gate-certified at
  901 draws) was **fit on the old stored `ils_dispy_real` → household-joint sum → `c_norm`**. The
  likelihood consumes headline consumption only, and `ils_dispy` is among the columns the old
  build *did* overwrite per draw — so the certified estimate was fit on a draw-specific (if
  component-incoherent) consumption series.
- **The coherent staged rebuild changes that estimator input on benefit-recipient rows.** The
  rebuilt `ils_dispy_real` differs from the stored value precisely where the means-tested benefit
  diverges (singles ≈ 2–4 %, couples ≈ 4.5–8.4 % of decider rows, up to €1,161).
- **A naive swap would invalidate the certified estimate** by silently moving its consumption
  input out from under the certified `theta_hat` and its standard errors, with no re-estimation
  to re-establish the fit, identification, or inference.
- **Redrawn-node welfare pricing cannot be certified against an unreproducible old EUROMOD
  target.** `V_i^dir` requires pricing redrawn welfare nodes through the *same* EUROMOD pipeline
  that produced the baseline; if that baseline target cannot be reproduced, a redrawn-node price
  has no certified reference to be validated against. This is why `V_i^dir` remains blocked.
- **The component-staleness fix is correct but cannot be shipped by swapping staged data.** The
  write-back patch genuinely repairs `ils_benmt`/`ils_bennt`/`ils_pen`/`*_s` (Two-M Gate A1: the
  patch is headline-invariant to machine zero *on the same sim*). But shipping it via a swap is
  blocked **not by the patch** — it is blocked because the swap simultaneously replaces the
  headline consumption series with one the certified estimate was not fit on. The fix and the
  estimate decision are coupled and must be resolved together.

---

## 5. Decision options

**Option A — Freeze the old certified estimate; defer / caveat welfare that requires
redrawn-node pricing.**
Keep the certified `joint_pooled_v1_bll0_tlmpin` estimate and the stored production data exactly
as they are. Ship results that depend only on the certified estimate and on already-validated
laissez-faire `W^3` quantities. Explicitly caveat — and defer — any welfare measure that requires
faithful redrawn-node EUROMOD pricing (`V_i^dir` and anything built on it).
- *Preserves:* the certified estimate untouched, all existing certification, full reproducibility
  of every result already produced, and zero risk of silently moving the estimator input.
- *Cannot support:* any redrawn-node welfare priced against the baseline; auditability of the
  benefit decomposition (the stored components remain stale); a defensible claim that the stored
  headline is *correct* rather than merely *fixed* — only that the irreproducibility's effect on
  the estimate has not yet been shown to matter (see §6).

**Option B — Treat the coherent staged rebuild as the corrected reproducible baseline; run a
separately authorised controlled re-estimation / recovery gate.**
Adopt the staging rebuild (deterministic, internally coherent, component-correct) as the new
*reproducible* baseline, then re-establish the estimate on it under a separately authorised
controlled re-estimation.
- *Would require:* a pinned, reproducible EUROMOD execution with all-component write-back; a full
  staging rebuild; a full-scale determinism/reproducibility gate; a controlled re-estimation
  starting from the certified `theta_hat`; and a re-run of the synthetic recovery gate on the new
  baseline. (Outlined in §8; **not** authorised here.)
- *Would settle:* whether a reproducible, component-coherent baseline yields essentially the same
  estimate (in which case the irreproducibility was immaterial and the corrected data can be
  adopted with the estimate intact) or a materially different one (in which case the certified
  estimate is replaced by the re-estimate on the reproducible baseline). It also unblocks
  redrawn-node pricing, because the new baseline IS reproducible.

**Option C — Attempt to recover the exact old EUROMOD execution environment.**
Try to reconstruct the precise EUROMOD model version / dataset vintage / run state that produced
the stored headline, to reproduce the stored target directly.
- This is worth only a **bounded forensic attempt, and only if cheap.** Two-N already walked the
  `.pre_wage_deflation.bak` trail and found it **byte-identical** to the current files, with both
  pricers' stamping byte-identical — i.e. the obvious provenance leads are exhausted. **C should
  not delay the A/B path** unless new evidence (e.g. an archived EUROMOD model build or a
  pinned dataset snapshot not yet examined) appears. A standalone time-boxed check of whether such
  an archive exists is acceptable; an open-ended reconstruction effort is not.

---

## 6. Common dispositive test beneath A and B

**Options A and B share a single dispositive test:** a **controlled re-estimation on the
reproducible rebuilt baseline**, compared against the certified estimate **parameter-by-parameter,
against its cluster-robust standard errors and against the synthetic-recovery standard.**

- **Under A**, this test establishes whether the irreproducibility is **immaterial**: if the
  re-estimate on the coherent baseline lands within the certified estimate's clustered-SE band
  and the synthetic-recovery tolerance, then the benefit-row differences do not move the estimate,
  the certified estimate stands, and Option A is licensed *with an explicit caveat* documenting
  the irreproducibility and the test that bounded its effect.
- **Under B**, this same test **is** the re-estimation step: if the re-estimate departs materially
  from the certified estimate, the reproducible baseline replaces the old one and the re-estimate
  becomes the certified estimate.

**Recommended sequence (this is the crux):** regenerate the baseline under a **pinned EUROMOD
execution with all-component write-back**, run the **controlled re-estimation**, and **let the
result decide** whether the old baseline stands with a caveat (A) or is replaced (B). A and B are
therefore not a fork to be chosen up front — they are the two outcomes of one test, and the test
is the next thing to authorise.

---

## 7. Recommendation

**Recommend authorising, as a separate increment, the §6 dispositive test — a pinned, reproducible
baseline regeneration followed by a controlled re-estimation from the certified `theta_hat`,
compared against the certified estimate's clustered SEs and the synthetic-recovery standard — and
let its result select between A and B.** Run only a **cheap, time-boxed** Option-C archive check
in parallel, abandoning it the moment it is not immediately conclusive.

Rationale: every reproducible cause is excluded (§3), so further diagnosis of the *current* data
will not move the question; the decision is now a build/estimate-policy one. The single fact that
governs the choice between A and B — does the coherent, reproducible baseline change the estimate
or not — is unknown and is answered by exactly one test, which both options need. Running it first
is strictly more informative than committing to A or B blind, and it does not pre-commit to a
swap: if the estimate is unchanged, the corrected components ship with the estimate intact (A with
caveat); if it changes, the reproducible baseline is adopted with its re-estimate (B). This memo
**does not authorise that test**; it recommends it as the next decision for supervisor approval.

Until that test is authorised and run: **freeze the certified estimate and the production data as
they stand, do not swap staging, and defer any welfare requiring redrawn-node pricing.**

---

## 8. Outline of the next technical contract (only if the controlled re-estimation path is chosen)

*Outline only — not the contract, not an authorisation.* If the §6 path is authorised, the next
technical contract must specify at least:

- **Pinned EUROMOD execution** — fix and record the EUROMOD model version, dataset vintage, and
  run configuration so the baseline is reproducible and re-runnable.
- **All-simulated-output write-back** — the Two-M patch (write every simulated `ils_*` / `*_s`
  per draw, not only the five headline columns) so each row is one coherent draw-specific
  scenario.
- **Full staging rebuild** — at exact production granularity (year/mode, chunk IDs, draw bands,
  system pairing, CPI), to a staging path, never overwriting production.
- **Full-scale determinism / reproducibility gate** — re-run reproduces to 0.0; component
  identities hold (`ils_ben = ils_pen + ils_benmt + ils_bennt`; `ils_dispy` identity); components
  draw-specific. (Headline parity vs the *old* stored target is **not** expected to pass — that
  is the established finding; the gate is on internal reproducibility/coherence of the new
  baseline.)
- **Controlled re-estimation starting from the certified `theta_hat`** — initialise at the
  certified 47-param `joint_pooled_v1_bll0_tlmpin` solution on the new reproducible baseline.
- **Comparison against clustered SEs and the synthetic-recovery standard** — parameter-by-parameter
  vs the certified estimate, judged against its cluster-robust standard errors and re-run against
  the synthetic-recovery gate (PD Hessian + recovery within tolerance) on the new baseline.
- **No welfare promotion until the estimate decision is settled** — no `V_i^dir`, no redrawn-node
  pricing, no `W^3` promotion, nothing beyond `W^3`, until A-vs-B is resolved by the test.

**Two-deflation architecture (must be honoured by that contract):**

- EUROMOD inputs remain **nominal** and **system-year consistent**; they are never wage-deflated
  (the wage deflation is estimator-facing only — the two-deflation rule that prevents double
  deflation).
- The **data year remains one year ahead of the EUROMOD policy system** as specified by the
  build — one system per data year (lagged pairing: data 2015 → system `FR_2014` (dataset
  `FR_2015_a2`), data 2016 → system `FR_2015` (dataset `FR_2016_a3`), data 2017 → system
  `FR_2016` (dataset `FR_2017_a2`)).
- **Estimation-facing real-wage deflation is separate from post-EUROMOD CPI conversion**: the
  former produces the estimator's real wage; the latter (`_CPI` per data year) converts priced
  `ils_dispy` to `ils_dispy_real`. The two must not be conflated or applied twice.
- **Counterfactual wages must be expressed in the draw's nominal frame before pricing** (so
  EUROMOD sees nominal earnings consistent with its system year) and **returned to real terms via
  the configured `phi_y`** after pricing.
- **System pairing, CPI factors, schemas, base year, and assessment-unit definitions must be
  config-driven, not hardcoded** (the standing package-agnosticism requirement: agnostic on
  country, year, and specification).

---

## 9. Explicit non-execution statement

This increment is a decision memo only. In producing it:

- **No `W^3` welfare finding is produced**, and no measure beyond `W^3` is touched.
- **No `V_i^dir` is computed.**
- **No redrawn node is priced.**
- **Nothing is re-estimated.**
- **No production parquet is swapped, overwritten, moved, or deleted** (the staging rebuild from
  Two-N is untouched and remains in staging; production priced files are unchanged).
- **This memo does not authorise implementation.** The §6 dispositive test, any rebuild, any
  re-estimation, any EUROMOD re-execution, and any swap each require separate supervisor
  authorisation.

---

`docs/jmp_methodology/RURO_welfare_stage2_baseline_provenance_decision_memo_v1.md`
