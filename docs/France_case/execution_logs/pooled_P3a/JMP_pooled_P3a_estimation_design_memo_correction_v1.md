# JMP Pooled P3a Estimation Design Memo — Correction v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This document is a documentation-only correction note for
`docs/JMP_pooled_P3a_estimation_design_memo_v1.md` (the pooled P3a
estimation design memo, 24 sections). It records four localised
corrections identified in the design review
(`docs/JMP_pooled_P3a_estimation_design_memo_review_addendum_v1.md`,
§3) and provides the corrected Gate-A implementation-audit prompt for
immediate use.

**The design memo remains accepted. No full rewrite is required.**
The 24-section memo's core design decisions — the pooled specification,
the year-effect treatment, the GSURv2 treatment, the cluster-robust
inference design, the SA2 verdict criteria, and the not-authorised
scope — are correct and unchanged. The four corrections are localised
to the evidence chain (§1 of the memo), the Gate-A check table (§19),
and the embedded Gate-A prompt (§24). With these corrections applied,
the design memo is fully accepted as the pooled P3a estimation design
and the Gate-A YAML audit may proceed.

This correction note does not authorise pooled estimation execution,
welfare implementation, welfare computation, canonical promotion, or
displacement of M1-clean.

---

## 2. Corrections applied

Four corrections identified in the review addendum are applied by
this note. Each is localised; none changes the pooled design's
substance.

| # | Correction | Scope |
|---|-----------|-------|
| C1 | Resolve the read-column-names-only vs GA13–GA16 value-check inconsistency | §24 Gate-A prompt, read instruction |
| C2 | Specify the Gate-A read scope explicitly as a bounded-read rule | §24 Gate-A prompt, read-scope list |
| C3 | Reclassify GA17 as a cluster-robust SE infrastructure status check; define Gate-A verdict semantics | §19 GA17 row and verdict rule; §24 prompt GA17 and report template |
| C4 | Add the heading-template addendum to the evidence chain | §1 evidence chain |

No other field, table, formula, or section of the design memo is
modified. The parameter count (55), the year-dummy specification
(`beta_E_y2015`, `beta_E_y2017`, FR_2016 omitted reference), the
cluster-robust VCV formula, the SA2 thresholds (S1–S11), and all
other design decisions are carried forward unchanged.

---

## 3. Evidence-chain correction

**Correction C4.** The design memo's §1 evidence chain is corrected
to add the heading-template addendum.

**Original evidence chain (§1 of the memo):**

- `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` —
  PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC CAVEATS.
- `docs/RURO_occ_M1_clean_verdict_v1.md` — M1-clean is the active
  JMP structural specification.
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`
  and `docs/JMP_stage_M1_V9_validation_patch_note_v1.md` — minor
  documentation and validation-spec items resolved.

**Corrected evidence chain (replaces §1 of the memo):**

- `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` —
  PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC CAVEATS;
  establishes the GSURv2 P3a pooled dataset as the final non-
  provisional construction input for pooled-estimation design and
  Gate-A validation.
- `docs/RURO_occ_M1_clean_verdict_v1.md` — M1-clean is the active
  JMP structural specification; pooled specification must be grounded
  in M1-clean parameter structure.
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`
  — subtitle year-label correction (caveat C1); documentation-only;
  no impact on construction input validity.
- `docs/JMP_stage_M1_V9_validation_patch_note_v1.md` — V9
  validation-spec patch (caveat C2); exemption for four known upstream
  sampling-control columns; documentation-only; no impact on
  construction input validity.
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md`
  — heading-template addendum; records that the execution report's
  27 section titles diverge from the originally requested template
  while the count (27) and all required substance are present;
  documentation-only, no C-series caveat in the construction verdict;
  no impact on construction input validity.
- `docs/JMP_pooled_P3a_estimation_design_memo_review_addendum_v1.md`
  — design review; verdict ACCEPT WITH REQUIRED CORRECTIONS; four
  localised corrections (C1–C4) required before Gate-A; design
  substance correct and accepted.

With the heading addendum added, the evidence chain is complete: it
cites the construction verdict, the M1-clean baseline, all three
documentation and validation-spec items on the execution report
(subtitle correction, heading addendum, V9 patch), and the design
review that produced this correction note.

---

## 4. Gate-A data-read boundary correction

**Corrections C1 and C2.** The §24 Gate-A prompt's read instruction
is replaced.

**Original instruction (§24 of the memo, read list, fourth item):**

> - `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
>   (the pooled data input — read column names only, do not load full
>   data)

**Corrected instruction:**

> - `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
>   (the pooled data input — apply the bounded-read rule below)
>
> **Gate-A bounded-read rule for the pooled parquet.** Gate-A may
> read:
>
> (a) The full parquet schema (all column names and dtypes) — required
>     for GA1–GA12.
>
> (b) The specific columns required for GA13–GA16: `year_tag`, `gsur`,
>     `gsur_male`, `gsur_female`, `ils_dispy_real`, `ils_dispy`,
>     `cluster_id`, `idorighh`, `household_type`.
>
> (c) A bounded row sample or selected row groups sufficient to confirm
>     the non-null, distinctness, and equality checks — for example,
>     a per-household-type stratified sample, or the parquet row-group
>     null-count metadata where it suffices. The GA16 "sample check,
>     not full scan" qualifier applies equally to GA14 and GA15.
>
> Gate-A must NOT:
>
> (d) Load the full 1,244,500-row dataset into memory when a bounded
>     sample or row-group metadata suffices.
>
> (e) Modify any column, row, parquet, sidecar, or config file.
>
> (f) Run any estimation, solver call, or precompute beyond the GA13
>     indicator-construction smoke test.

The rationale is stated in the review addendum §5: GA13–GA16 require
reading column values (value-distinctness, non-null, and equality
checks), not only column names. Reading column names alone cannot
satisfy GA13–GA16. The bounded-read rule permits the specific reads
the checks require while still prohibiting a full-data load, any data
modification, and any estimation. The rule is consistent with Gate-A's
purpose as a static-validation step.

---

## 5. GA17 interpretation correction

**Correction C3, part 1.** The §19 GA17 row and the §19 closing
verdict rule are corrected.

**Original §19 GA17 row:**

> | GA17 | Cluster-robust SE implementation confirmed callable on the
> pooled parquet with 9,657 clusters |

**Original §19 closing rule:**

> Gate-A must produce a parse report recording all 17 checks. All
> checks must PASS before the pooled-estimation authorization memo is
> issued.

**Corrected §19 GA17 row:**

> | GA17 | Cluster-robust SE infrastructure status: record whether the
> estimation engine exposes a `cluster_id` parameter or cluster-robust
> SE method callable on the pooled parquet; record the finding (exists
> / pending) even if the method is not yet implemented. GA17 is a
> status-record check, not a binary PASS condition at Gate-A. |

**Corrected §19 verdict rule:**

Gate-A PASS: GA1–GA16 all pass, and GA17 records the cluster-robust
SE infrastructure as confirmed callable. The pooled specification is
fully Gate-A-clear; the execution-authorization memo may proceed
without a cluster-robust-SE blocker.

Gate-A PASS WITH BLOCKER: GA1–GA16 all pass, and GA17 records the
cluster-robust SE infrastructure as pending. The pooled YAML and data
input are structurally validated (the static checks pass), but the
cluster-robust SE infrastructure must be built and confirmed callable
before the pooled-estimation authorization memo is issued. This is the
expected Gate-A outcome given the current pending infrastructure (design
memo §3 P3).

Gate-A FAIL: any of GA1–GA16 fails. The pooled YAML or data input is
structurally invalid and must be corrected before Gate-A is re-run.

The pooled-estimation authorization memo requires both Gate-A passing
(PASS or PASS WITH BLOCKER) and the GA17 blocker cleared (the
cluster-robust SE infrastructure confirmed callable). The distinction
separates the YAML-and-data static-validation gate (Gate-A, GA1–GA16)
from the estimator-engine-capability gate (cluster-robust SE
infrastructure, GA17), which is correctly located at the
execution-authorization review.

The rationale is stated in the review addendum §6: the design's own
§3 P3 and §15 establish the cluster-robust SE infrastructure as
pending; the §24 prompt already treats GA17 as a status-record check;
requiring GA17 to PASS at Gate-A would make Gate-A unpassable on the
current codebase, blocking the pipeline on an infrastructure item
that Gate-A is not the right gate to clear.

---

## 6. Corrected Gate-A verdict semantics

**Correction C3, part 2.** The Gate-A verdict semantics — corrected
in §5 above — are restated here in consolidated form for reference.

**Gate-A PASS:** GA1–GA16 all pass; GA17 records cluster-robust SE
infrastructure as confirmed callable.
- Meaning: the pooled YAML and data input are structurally valid; the
  cluster-robust SE infrastructure is confirmed. Gate-A is fully
  cleared. The execution-authorization memo may be drafted.

**Gate-A PASS WITH BLOCKER:** GA1–GA16 all pass; GA17 records
cluster-robust SE infrastructure as pending.
- Meaning: the pooled YAML and data input are structurally valid. The
  cluster-robust SE infrastructure must be built and confirmed callable
  before the execution-authorization memo is issued. The blocker is
  identified; the build task is sequenced. This is the expected outcome
  on the current codebase.

**Gate-A FAIL:** any of GA1–GA16 fails.
- Meaning: the pooled YAML or data input is structurally invalid. The
  failure must be diagnosed and corrected before Gate-A is re-run.
  GA17 status is not considered when GA1–GA16 has a failure.

The SA2 verdict criterion S9 (`Gate-A GA1–GA17: all PASS`, §21 of the
design memo) is interpreted under the corrected semantics: S9 requires
Gate-A PASS, not Gate-A PASS WITH BLOCKER. A pooled specification
estimated under a PASS WITH BLOCKER outcome (before the GA17 blocker
is cleared) would not satisfy S9. The SA2 verdict cannot be issued
until the cluster-robust SE infrastructure is confirmed and Gate-A
returns a full PASS.

---

## 7. What is not authorized

This correction note applies four localised corrections and provides
the corrected Gate-A prompt. It does not authorise any of the
following; each is separately gated.

**Pooled estimation execution is NOT authorized.** The corrected
Gate-A YAML audit is the authorised next step. Pooled estimation
requires the Gate-A audit to pass (PASS or PASS WITH BLOCKER), the
GA17 cluster-robust SE infrastructure blocker to be cleared, and a
separate pooled-estimation authorization memo. None of these
conditions has been met.

**Welfare implementation and welfare computation are NOT authorized.**
Welfare computation requires an accepted SA2 verdict on a pooled
specification and a separate welfare-computation authorization.

**Cluster-robust SE infrastructure as an authorised build under this
note.** This note identifies the cluster-robust SE infrastructure as
the expected GA17 blocker; it does not authorise the sandwich-estimator
build. The implementation is a separate task, sequenced after the Gate-A
parse report identifies it as the blocker.

**Canonical promotion.** No canonical promotion of the pooled YAML,
the pooled dataset, or any pooled output is authorised.

**M1-clean displacement.** `ruro_occ_M1_clean` remains the active
JMP baseline. The pooled specification does not displace M1-clean;
displacement requires a future SA2 verdict on an estimated pooled
specification.

**P3b, P4, or alternative pooled specifications.** P3b (hard-blocked
pending the ISF gate), P4 (not a priority), and year-interacted or
other alternative pooled specifications (post-SA2 sensitivities) are
not authorised.

---

## 8. Corrected Gate-A implementation-audit prompt

The following is the corrected Gate-A implementation-audit prompt,
incorporating all four corrections (C1–C4). It supersedes the §24
prompt in `docs/JMP_pooled_P3a_estimation_design_memo_v1.md` and
must be used verbatim in place of that prompt. The corrections from
§24 are: (a) the "read column names only" instruction is replaced by
the bounded-read rule (C1, C2); (b) the GA17 instruction is aligned
with the status-record classification and the PASS / PASS WITH BLOCKER
/ FAIL verdict semantics (C3); and (c) the read list cites this
correction note alongside the design memo (C4).

---

> Work locally in my RURO/MNL codebase.
>
> This is a Gate-A YAML implementation and static parse audit for the
> pooled P3a estimation specification. Do not run estimation. Do not
> modify the pooled parquet. Do not modify M1-clean or M1-naive specs.
>
> Read:
> - `docs/JMP_pooled_P3a_estimation_design_memo_v1.md` (the
>   authoritative pooled spec — 24 sections)
> - `docs/JMP_pooled_P3a_estimation_design_memo_correction_v1.md`
>   (this correction note — four corrections to the design memo;
>   the corrected Gate-A bounded-read rule and verdict semantics
>   supersede §24 and §19 of the design memo)
> - `scripts/enhanced/specifications/estimation_spec_ruro_occ_M1_clean.yaml`
>   (the source YAML to derive the pooled YAML from)
> - `scripts/enhanced/estimation_spec_parser.py`
>   (the parser to use for Gate-A static checks)
> - `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
>   (the pooled data input — apply the bounded-read rule below)
>
> **Gate-A bounded-read rule for the pooled parquet.** Gate-A may
> read:
>
> (a) The full parquet schema (all column names and dtypes) — required
>     for GA1–GA12.
>
> (b) The specific columns required for GA13–GA16: `year_tag`, `gsur`,
>     `gsur_male`, `gsur_female`, `ils_dispy_real`, `ils_dispy`,
>     `cluster_id`, `idorighh`, `household_type`.
>
> (c) A bounded row sample or selected row groups sufficient to confirm
>     the non-null, distinctness, and equality checks. The GA16 "sample
>     check, not full scan" qualifier applies equally to GA14 and GA15.
>
> Gate-A must NOT: load the full 1,244,500-row dataset into memory when
> a bounded sample or row-group metadata suffices; modify any column,
> row, parquet, sidecar, or config file; run any estimation, solver
> call, or precompute beyond the GA13 indicator-construction smoke test.
>
> Task:
>
> 1. Create
>    `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
>    by deriving from the M1-clean YAML with exactly these changes and
>    no others:
>    - `specification.name`: set to `ruro_occ_P3a_pooled`
>    - `specification.description`: update to describe the pooled
>      three-year P3a specification
>    - `market_opportunity.shifters`: add two new entries after the
>      last existing shifter entry:
>      `beta_E_y2015` (variable: `year_2015_indicator`,
>      applies_to: `household`) and
>      `beta_E_y2017` (variable: `year_2017_indicator`,
>      applies_to: `household`)
>    - `initial_values`: add `beta_E_y2015: 0.0` and
>      `beta_E_y2017: 0.0`
>    - `optimization.bounds`: add entries for `beta_E_y2015` and
>      `beta_E_y2017` with bounds `[-5.0, 5.0]`
>    - Do not change any other field. All other blocks must be
>      byte-identical to the M1-clean YAML.
>
> 2. Run `estimation_spec_parser.py` on the new YAML and confirm it
>    parses without error.
>
> 3. Run Gate-A checks GA1–GA17 as specified in
>    `docs/JMP_pooled_P3a_estimation_design_memo_v1.md` §19, with the
>    corrections from
>    `docs/JMP_pooled_P3a_estimation_design_memo_correction_v1.md` §5
>    applied to GA17.
>
>    For GA13 (precompute smoke test): read `year_tag` from the pooled
>    parquet (bounded sample sufficient) and confirm that `year_tag == 1`
>    and `year_tag == 3` resolve to non-empty subsets. Confirm that
>    `year_2015_indicator` and `year_2017_indicator` can be constructed
>    as `(year_tag == 1)` and `(year_tag == 3)` respectively on the
>    singles and couples subsets.
>
>    For GA14: read `gsur`, `gsur_female`, `gsur_male`, and
>    `household_type` from the pooled parquet (bounded per-household-type
>    sample sufficient). Confirm `gsur` non-null for singles rows;
>    confirm `gsur_female` and `gsur_male` non-null for couples rows.
>
>    For GA15: read `ils_dispy_real` and `ils_dispy` from the pooled
>    parquet (bounded sample sufficient). Confirm `ils_dispy_real`
>    present and non-null; confirm `ils_dispy_real != ils_dispy` for at
>    least one non-FR_2016 row (i.e. at least one row where `year_tag`
>    is 1 or 3).
>
>    For GA16: read `cluster_id` and `idorighh` from the pooled parquet
>    (bounded sample, not full scan). Confirm `cluster_id == idorighh`
>    for sampled rows.
>
>    For GA17 (cluster-robust SE infrastructure status check — not a
>    binary PASS condition): inspect the estimation engine
>    (`scripts/enhanced/estimation_engine.py`,
>    `scripts/enhanced/gamspy_estimation_vectorized.py`, and related
>    files) for any `cluster_id` parameter, sandwich-estimator method,
>    or cluster-robust SE computation. Record the finding as one of:
>    (i) CONFIRMED — a cluster-robust SE method callable on the pooled
>    parquet with 9,657 clusters exists and is callable; or
>    (ii) PENDING — no such method exists in the current codebase; the
>    sandwich-estimator build is the blocker between Gate-A and the
>    execution-authorization memo.
>    Record the finding even if the method is not yet implemented.
>
> 4. Create `Results/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md`
>    with exactly these headings:
>    1. Gate-A verdict
>    2. YAML derivation record
>    3. Parser output
>    4. GA1–GA17 check results
>    5. Precompute smoke test
>    6. Cluster-robust SE infrastructure status
>    7. What was not run
>    8. Immediate next step
>
> Required final statements in the report:
>
> - State the Gate-A verdict as one of: PASS, PASS WITH BLOCKER, or
>   FAIL, per the corrected verdict semantics in
>   `docs/JMP_pooled_P3a_estimation_design_memo_correction_v1.md` §6:
>   PASS = GA1–GA16 pass and GA17 confirmed; PASS WITH BLOCKER =
>   GA1–GA16 pass and GA17 pending; FAIL = any GA1–GA16 check fails.
> - State whether GA1–GA16 passed.
> - State the GA17 cluster-robust SE infrastructure finding (confirmed
>   or pending).
> - State that pooled estimation execution is NOT authorized by this
>   Gate-A audit.
> - State that pooled estimation execution requires both Gate-A passing
>   and the GA17 cluster-robust SE infrastructure blocker cleared, plus
>   a separate pooled-estimation authorization memo.
> - State that M1-clean 2016 remains the active JMP baseline.
> - State that pooled estimation is NOT authorized.
> - State that welfare computation is NOT authorized.

---

**Pooled estimation is NOT authorized.**

**Welfare computation is NOT authorized.**

**M1-clean 2016 remains the active JMP baseline.** Displaced only by
a future SA2 verdict explicitly promoting a final pooled specification.