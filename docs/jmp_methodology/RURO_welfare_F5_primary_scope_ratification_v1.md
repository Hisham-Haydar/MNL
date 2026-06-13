# RURO Welfare — F5 Primary Cross-Section Scope Ratification

**Date:** 2026-06-13 · **Type:** governance ratification record (documentation only; no calculations,
no output rewrites, no commit). Operator sign-off captured verbatim and reconciled with the F5-R
cross-section reconciliation (`RURO_welfare_F5R_crosssection_scope_reconciliation_v1.md`) and the
decisions-memo §13 pooled-case rule.

---

## 1. Ratified primary scope

- **Primary singles welfare distribution = the 2016 cross-section** (`year_tag == 2`, **n = 1,676**
  households), evaluated at the certified pooled `theta_hat` (`theta_hat_realdata_901_v1.csv`,
  spec `joint_pooled_v1_bll0_tlmpin`).
- This is decisions-memo `JMP_welfare_measurement_decisions_memo_v2.md` §13 option **(b)**: the 2016
  distribution computed from the pooled `theta_hat` but evaluated on the 2016 cross-section.
- **Sensitivities (not headline):** pooled 2015–2017 (option (a)) and the separate 2015 and 2017
  single-year distributions.

## 2. Primary headline figures (frozen, from F5-R recomputation)

| Measure | Primary 2016 survey-weighted Gini |
|---|---|
| W1 (equal-pay over own set) | **0.173** |
| W4 (staying-home full-compensation) | **0.329** |
| W6 (min-of-equal-pay, universal grid) | **0.337** |

- **Across-measure bracket = [0.173, 0.337]; spread = 0.164.** (min = W1, max = W6.)
- These values are the 2016 rows already present in
  `outputs/welfare/fastlane/singles_measure_family_F5R_crosssection_v1.parquet`; this ratification
  changes only their governance **label**, not the numbers.

## 3. Status of generated artifacts (immutable)

- `singles_measure_family_F5R_crosssection_v1.parquet`, `F5R_crosssection_manifest_v1.json`, and
  `RURO_welfare_F5R_crosssection_scope_reconciliation_v1.md` **remain immutable**. Their
  `primary_candidate_UNRATIFIED` / `PRIMARY CROSS-SECTION STATUS: UNRATIFIED` labels reflect the
  as-of-run state and are **superseded by this artifact**. No generated report, manifest, or parquet
  is edited.
- The F5 point estimates and F4C measures they consume remain **valid**. Conference-final confidence
  intervals are **pending** (see §4).

## 4. Inference cluster contract (terminology correction — load-bearing)

The welfare-output cluster count is **not** the bootstrap resampling unit. Precise terms:

- **Welfare evaluation sample:** the primary **2016 singles cross-section** (n = 1,676 households),
  the scope on which the headline inequality indices are reported.
- **Pooled singles welfare-output clusters:** **3,902 `idorighh`** — a descriptive property of the
  pooled (2015–2017) singles output set; **not** the bootstrap resampling unit.
- **Structural re-estimation bootstrap sample:** the **full certified joint estimation sample**
  (singles + couples), **9,657 `idorighh` clusters** — the resampling unit for inference.
- **Procedure (pre-registered, B = 200; decisions-memo §21):** each replicate resamples `idorighh`
  clusters from the **full joint estimation sample**, **re-estimates `theta`** on the resampled
  estimation sample (boundary pins held), then **recomputes the F4C measures on the ratified 2016
  singles evaluation scope**, then recomputes the weighted inequality indices. 95% CIs are the
  2.5th/97.5th percentiles across the 200 replicates.
- **Fixed-`theta` household resampling alone is NOT sufficient** and is not the pre-registered
  inference: it omits the dominant uncertainty channel (estimation uncertainty in `theta_hat`).

No bootstrap is run here; this section records the contract only.

## 5. Documentation updated for consistency

Dated addenda appended to the governing documents (generated reports/manifests/parquets untouched):

- `docs/jmp_methodology/JMP_welfare_measurement_decisions_memo_v2.md`
- `docs/jmp_methodology/JMP_measure_mapping_memo_v1.md`
- `docs/JMP_results_campaign_roadmap_v1.md`

---

PRIMARY CROSS-SECTION: 2016 RATIFIED
INFERENCE CLUSTER CONTRACT: FULL JOINT SAMPLE — 9,657 idorighh
F3-F5 DOCUMENTATION: CONSISTENT
READY FOR F6 DESIGN MEMO: yes
