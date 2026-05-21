# JMP Pooled P3a Estimation Design Memo — Review Addendum v1

Date: 2026-05-21

Document under review: `docs/JMP_pooled_P3a_estimation_design_memo_v1.md`
(the pooled P3a estimation design memo, 24 sections).

Review type: strict independent design review, producing a
correction/addendum rather than a full rewrite. The addendum
records the review verdict, the required corrections before Gate-A,
and the disposition of the Gate-A audit, without restating the
design memo's substance except where a correction is required.

Evidence consulted:
- `docs/JMP_pooled_P3a_estimation_design_memo_v1.md` (the memo
  under review)
- `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md` (the
  construction verdict establishing the pooled dataset as the final
  non-provisional construction input)
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`
  (the subtitle year-label correction, caveat C1)
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md`
  (the heading-template addendum)
- `docs/JMP_stage_M1_V9_validation_patch_note_v1.md` (the V9
  validation-spec patch, caveat C2)
- `docs/RURO_occ_M1_clean_verdict_v1.md` (the active single-year
  baseline)

Scope of addendum: the addendum reviews the pooled P3a estimation
design for internal consistency, evidence-chain completeness, and
Gate-A executability. It adjudicates whether the design memo is
acceptable as the pooled P3a design, what corrections are required
before the Gate-A YAML audit, whether the Gate-A audit may proceed,
and what remains not authorised. The addendum does not authorise
pooled estimation execution, welfare implementation, or welfare
computation; those steps are separately gated.

---

## 1. Review verdict

**ACCEPT WITH REQUIRED CORRECTIONS.**

The pooled P3a estimation design memo is a sound and substantially
complete design document. Its core design decisions are correct and
well-grounded: the pooled specification is derived from M1-clean by
adding exactly two year-dummy shifters in the market-opportunity
index with FR_2016 as the omitted reference (§8), the structural
preference and opportunity blocks are carried forward unchanged
(§11, §12), the GSURv2 opportunity rates are used from the active
`gsur` / `gsur_male` / `gsur_female` columns with the v1-fallback
columns preserved-but-unused (§9), the cluster-robust inference is
correctly specified at the `idorighh` level with a sandwich
estimator over 9,657 clusters (§15, §16), the 2,788 repeat-household
figure is correctly used rather than the nominal 8,796 (§17), and
the SA2 verdict criteria are a coherent pooled counterpart of the
M1-clean SA1 criteria (§21). On the substance of the pooled design,
the memo is acceptable.

The verdict is ACCEPT WITH REQUIRED CORRECTIONS, not unqualified
acceptance, because the memo contains one genuine internal
inconsistency and three smaller completeness or classification
items that must be corrected before the Gate-A YAML audit is issued
(§3). The decisive item is the inconsistency between the §24 Gate-A
prompt's instruction to "read column names only, do not load full
data" and the §19 Gate-A checks GA13–GA16, which require reading
column *values* (non-null checks, value-distinctness checks, and a
`cluster_id == idorighh` equality check). As written, the Gate-A
audit cannot both obey the read-column-names-only instruction and
execute GA13–GA16; the instruction and the checks contradict each
other, and the contradiction would either block the value checks or
license an unbounded full-data load. This must be resolved before
the audit runs (§3, §5).

The other three corrections are smaller: the evidence chain (§1 of
the memo) omits the heading-template addendum (§4 of this addendum);
the GA17 cluster-robust-SE check is classified inconsistently
between §19 (which requires it "confirmed callable," a PASS
condition) and the §24 prompt (which asks only to "note whether...
record the finding even if not yet implemented"), and the design's
own §3 P3 and §15 establish that the infrastructure is *pending*
(§6 of this addendum); and the GA13–GA16 value checks need an
explicit narrow-read scope so the audit reads only the required
columns and a bounded row sample (§3, §5).

None of the four corrections requires a full rewrite (§7). All four
are localised edits to the design memo and its embedded Gate-A
prompt. With the corrections applied, the design memo is acceptable
as the pooled P3a design and the Gate-A YAML audit may proceed (§8).

The single-year M1-clean 2016 specification remains the active JMP
baseline throughout (§9).

---

## 2. Whether the design memo is acceptable as the pooled P3a design

**Yes, subject to the four required corrections (§3). The 24-section
design memo is acceptable as the pooled P3a estimation design.**

The memo is acceptable as the pooled P3a design because it
specifies, completely and correctly, the elements a pooled
estimation design must fix before a YAML can be written and a Gate-A
audit run. Six design elements are correct and require no change.

First, the pooled specification mapping (§6, §7, §8) is the minimal
correct extension of M1-clean: it changes the observation scope
(three years instead of one) and adds two year-dummy shifters
(`beta_E_y2015`, `beta_E_y2017`) in the market-opportunity index,
with FR_2016 as the omitted reference, and carries everything else
forward unchanged. The 53 → 55 parameter-count adjustment is correct
and explicit. The choice of FR_2016 as the reference year is
well-justified: it anchors the pooled `beta_E` and region-dummy
estimates to the same year as the M1-clean estimates and makes the
pooled FR_2016 posterior directly comparable to the M1-clean
posterior, which is the natural SA2 comparison.

Second, the GSURv2 treatment (§9) correctly uses the active GSUR
columns, correctly excludes them from CPI deflation (they are
proportions), and correctly designates the v1-fallback columns as
preserved-but-unused. This is consistent with the K2 decision
carried through the GSURv2 extension and the rebuild.

Third, the cluster-robust inference design (§15, §16, §17) is
correct. The clustering is at `idorighh` (the raw household
identifier that persists across waves), not the engineered stacked
identifier; the sandwich estimator sums score contributions across
all household-year appearances of each cluster; the relevant
asymptotic quantity is the cluster count (9,657), and the design
correctly uses the RURO-sample repeat-household figure (2,788)
rather than the nominal EU-SILC figure (8,796). These are the
correct inference-design decisions for a pooled dataset with a
rotational-panel overlap.

Fourth, the preference and opportunity treatments (§11, §12, §13)
correctly maintain the time-invariant-preference assumption, carry
the singles-consumption identification limitation forward as an
inherited limitation (the three near-singular parameters), and
maintain the joint singles-couples estimation with the household-
type-specific variable resolver.

Fifth, the draw-expanded structure (§14) is correctly described, and
the SA2 verdict criteria (§21) are a coherent pooled counterpart of
the M1-clean SA1 criteria, with the singles-consumption sub-block
diagnostic carried forward and sensible thresholds (S1–S11) for the
pooled stability tests.

Sixth, the not-authorised scope (§23) is correctly drawn: the memo
is explicit that it is a design document, not an authorization, and
that pooled estimation, welfare, canonical promotion, and M1-clean
displacement remain gated.

The memo is acceptable as the pooled P3a design. The four required
corrections (§3) are refinements to the Gate-A executability and the
evidence chain, not changes to the design's substance.

---

## 3. Required corrections before Gate-A

Four corrections are required before the Gate-A YAML audit is issued.
Each is a localised edit to the design memo or its embedded Gate-A
prompt (§24).

(C1) **Resolve the read-column-names-only versus GA13–GA16 value-
check inconsistency.** The §24 Gate-A prompt instructs the audit to
read the pooled parquet with "read column names only, do not load
full data," but the §19 checks GA13–GA16 require reading column
*values*: GA13 requires resolving `year_2015_indicator` and
`year_2017_indicator` (which requires reading `year_tag` values);
GA14 requires confirming `gsur` / `gsur_male` / `gsur_female` are
*non-null* for their household types (which requires reading those
column values); GA15 requires confirming `ils_dispy_real` is
*non-null* and *distinct from* `ils_dispy` (which requires reading
both columns' values); GA16 requires confirming `cluster_id ==
idorighh` (which requires reading both columns' values). Reading
column names alone cannot satisfy GA13–GA16. The correction is to
replace the "read column names only" instruction with a bounded-
read instruction (C2) that permits reading the specific columns and
a bounded row sample required for GA13–GA16, while still prohibiting
a full-data load, any data modification, and any estimation. This is
the decisive correction; without it, the Gate-A audit either cannot
execute GA13–GA16 or must violate the stated read constraint.

(C2) **Specify the Gate-A read scope explicitly.** The corrected
read instruction must state precisely what Gate-A may read: the
parquet schema (all column names and dtypes); the specific columns
required for GA13–GA16 (`year_tag`, `gsur`, `gsur_male`,
`gsur_female`, `ils_dispy_real`, `ils_dispy`, `cluster_id`,
`idorighh`, `household_type`); and a bounded row sample or selected
row groups sufficient to confirm the non-null, distinctness, and
equality checks (for instance, a per-household-type sample, or the
parquet row-group metadata where it suffices). The instruction must
continue to prohibit loading the full 1,244,500-row dataset into
memory unnecessarily, modifying any data, and running any
estimation. The §8 of this addendum specifies the permitted-read
boundary in full.

(C3) **Reclassify GA17 as a status-record check, not a PASS
condition, and define the Gate-A verdict semantics when GA17 is
pending.** The §19 table states GA17 as "Cluster-robust SE
implementation confirmed callable on the pooled parquet with 9,657
clusters" — a PASS condition — and §19 states "All checks must PASS
before the pooled-estimation authorization memo is issued." But the
design's own §3 P3 and §15 establish that the cluster-robust SE
infrastructure is *pending* confirmation, and the §24 prompt's GA17
asks only to "note whether the estimation engine exposes a
`cluster_id` parameter or cluster-robust SE method; record the
finding even if the method is not yet implemented." The §19 GA17
(confirmed callable) and the §24 GA17 (record the finding) are
inconsistent, and the §19 "all must PASS" rule combined with the
pending infrastructure would make Gate-A unpassable as written. The
correction is specified in §6 of this addendum: GA17 is a status-
record check at Gate-A (record whether the infrastructure exists),
and the Gate-A verdict is **PASS WITH BLOCKER** when GA1–GA16 pass
but GA17 records the cluster-robust SE infrastructure as pending.
The §19 "all must PASS before authorization" rule is corrected to
distinguish the Gate-A-passing condition (GA1–GA16 pass, GA17
recorded) from the execution-authorization condition (GA17 cleared,
i.e. the cluster-robust SE infrastructure confirmed callable).

(C4) **Add the heading-template addendum to the evidence chain.**
The memo's §1 evidence chain cites the construction verdict, the
M1-clean verdict, the stacking execution-report correction (the
subtitle year-label issue, C1), and the V9 validation patch note
(C2). It does not cite
`docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md`,
the heading-template addendum that records the second documentation
observation on the execution report. The correction is to add the
heading addendum to the evidence chain (§4 of this addendum
specifies the citation), so that the evidence chain is complete with
respect to all recorded documentation items on the execution report.

The four corrections are localised. C1 and C2 edit the §24 Gate-A
prompt's read instruction and add the read-scope specification. C3
edits the §19 GA17 row and the §19 "all must PASS" rule, and aligns
the §24 prompt's GA17 wording. C4 adds one citation to the §1
evidence chain. None changes the pooled design's substance.

---

## 4. Evidence-chain completeness

**The evidence chain is substantially complete but omits one
documentation item: the heading-template addendum. The correction
(C4) adds it.**

The memo's §1 evidence chain cites four documents: the construction
verdict (establishing the pooled dataset as the final non-
provisional construction input, PASS WITH MINOR DOCUMENTATION AND
VALIDATION-SPEC CAVEATS), the M1-clean verdict (the active baseline),
the stacking execution-report correction (the subtitle year-label
issue), and the V9 validation patch note (the upstream-ruro-column
exemption). These four correctly establish the dataset's validity
and the two construction-verdict caveats (C1 subtitle, C2 V9 patch).

The evidence chain omits
`docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_heading_addendum_v1.md`.
The heading addendum records a second documentation observation on
the execution report: the report's 27 section headings, while
correct in count, deviate in title from the originally requested
27-heading template. The heading addendum establishes that this is
documentation-only — the heading titles appear in no parquet,
sidecar, config, or validation manifest, and all substantive content
required by the authorization (R1–R10) is present in the report —
and that it does not rise to a construction-verdict C-series caveat.

**Should the heading addendum be cited?** Yes. The heading addendum
should be cited in the design memo's evidence chain, for two reasons.
First, completeness: the evidence chain documents the validity of the
pooled construction input, and the heading addendum is one of the two
documentation observations on the execution report that produced that
input; citing the subtitle correction but not the heading addendum
leaves the evidence chain partially documenting the report's
documentation history. Second, auditability: a reader verifying that
all documentation items on the execution report have been dispositioned
should find both the subtitle correction and the heading addendum in
the evidence chain, with the heading addendum's disposition
(documentation-only, no C-series caveat, no re-run) recorded.

The citation does not change the dataset's validity or any design
decision. The heading addendum is documentation-only and confirms
that the execution report's substance is complete and correct; citing
it strengthens the evidence chain's completeness without altering the
design. The correction (C4) adds the citation with its disposition:
the heading addendum is a documentation-only item on the execution
report, requiring no re-run and not affecting the construction-input
validity, complementing the subtitle correction (C1) and the V9 patch
(C2) already cited.

With the heading addendum added, the evidence chain is complete: it
cites the construction verdict, the M1-clean baseline, and all three
documentation/validation-spec items on the execution report (the
subtitle correction, the heading addendum, and the V9 patch).

---

## 5. Gate-A prompt consistency

**The §24 Gate-A prompt is internally inconsistent on the read scope
and must be corrected (C1, C2). With the read scope corrected, the
prompt is consistent and executable.**

The §24 Gate-A prompt instructs the audit to read the pooled parquet
with the parenthetical "(the pooled data input — read column names
only, do not load full data)." The prompt's own task steps then
require value reads that this instruction forbids:

- Step 3 GA13: "confirm that `year_tag == 1` and `year_tag == 3`
  resolve to non-empty subsets on the pooled parquet" — requires
  reading `year_tag` values.
- Step 3 GA14: "confirm `gsur` non-null for singles rows,
  `gsur_female` and `gsur_male` non-null for couples rows" — requires
  reading those columns' values and the `household_type` values.
- Step 3 GA15: "confirm `ils_dispy_real` present and non-null;
  confirm `ils_dispy_real != ils_dispy` for at least one non-FR_2016
  row" — requires reading both columns' values.
- Step 3 GA16: "confirm `cluster_id == idorighh` for all rows (sample
  check, not full scan)" — requires reading both columns' values
  (and the "sample check, not full scan" qualifier already
  acknowledges a value read, contradicting "read column names only").

The "read column names only" instruction and the GA13–GA16 value
checks cannot both be obeyed. The inconsistency is internal to the
prompt: the read constraint forbids exactly the reads the checks
require.

**Clarification: Gate-A may read selected columns and bounded row
samples for static validation, while still not modifying data or
running estimation.** The correct read scope for a static validation
audit is a *bounded* read, not a column-names-only read and not a
full-data load. Gate-A is a static-validation gate: it confirms the
YAML and the data input are structurally correct before estimation,
without estimating. Static validation of the data input legitimately
requires reading the specific columns and a bounded row sample that
the checks reference, because the checks are about column values
(non-null, distinct, equal), not merely column presence. Reading
selected columns and a bounded row sample (or selected row groups)
is consistent with the static-validation purpose: it confirms the
data input's structural validity without loading the full dataset,
without modifying any data, and without running any estimation.

The corrected read scope (C2) is therefore: Gate-A may read (a) the
full parquet schema (column names and dtypes); (b) the specific
columns required for GA13–GA16 (`year_tag`, `gsur`, `gsur_male`,
`gsur_female`, `ils_dispy_real`, `ils_dispy`, `cluster_id`,
`idorighh`, `household_type`); and (c) a bounded row sample or
selected row groups sufficient to confirm the non-null, distinctness,
and equality checks. Gate-A may not (d) load the full 1,244,500-row
dataset into memory when a bounded sample suffices; (e) modify any
column, row, or file; or (f) run any estimation, precompute beyond
the smoke-test indicator construction, or solver call.

The bounded-read scope resolves the inconsistency: the GA13–GA16
checks are executable (they read the columns and sample they need),
and the read constraint is meaningful (no full-data load, no
modification, no estimation). The "read column names only" phrasing
is replaced by the bounded-read scope; the GA16 "sample check, not
full scan" qualifier is retained and generalised to GA14 and GA15
(the non-null checks may be confirmed on a per-household-type sample
or via the column's null-count metadata where the parquet exposes
it). With this correction, the §24 prompt is internally consistent
and executable.

---

## 6. GA17 cluster-robust SE interpretation

**GA17 is a status-record check at Gate-A, not a PASS condition. If
the cluster-robust SE infrastructure is pending at Gate-A, Gate-A
returns PASS WITH BLOCKER: GA1–GA16 pass, GA17 records the
infrastructure as pending, and the blocker (the cluster-robust SE
infrastructure) must be cleared before the pooled-estimation
authorization memo is issued.**

The design memo treats GA17 inconsistently. The §19 table states GA17
as "Cluster-robust SE implementation confirmed callable on the pooled
parquet with 9,657 clusters" and the §19 closing rule states "All
checks must PASS before the pooled-estimation authorization memo is
issued" — together implying GA17 is a PASS condition that gates
Gate-A. But the design's own §3 P3 establishes the cluster-robust SE
infrastructure as a pending precondition ("This confirmation is
required before execution authorization is issued"), §15 states the
implementation prerequisite must be "confirmed in the execution
authorization memo before pooled estimation is authorised," and the
§24 prompt's GA17 asks only to "note whether the estimation engine
exposes a `cluster_id` parameter or cluster-robust SE method; record
the finding even if the method is not yet implemented." The §24
prompt treats GA17 as a status-record check; the §19 table treats it
as a PASS condition.

The inconsistency must be resolved, and the resolution is to treat
GA17 as a status-record check at Gate-A, for three reasons.

First, the design's logical structure already places the cluster-
robust SE confirmation at the *execution-authorization* gate, not the
Gate-A gate. §3 P3 and §15 both locate the confirmation "before
execution authorization," which is downstream of Gate-A. Gate-A is
the YAML-and-data static-validation gate; the cluster-robust SE
infrastructure is an estimator-engine capability whose confirmation
is naturally part of the execution-authorization review, not the YAML
parse audit. Requiring GA17 to PASS at Gate-A would conflate the two
gates.

Second, the cluster-robust SE infrastructure is genuinely pending
(§3 P3): the single-year engine uses a standard GAMSPy/CONOPT solver,
and the sandwich estimator at the `idorighh` cluster level — the score
matrix computation and the meat-matrix assembly over 9,657 clusters
(§15) — is not yet confirmed to exist in the estimation engine. A
Gate-A audit run now would find GA17 pending, and the §19 "all must
PASS" rule would make Gate-A unpassable, blocking the entire
downstream pipeline on an infrastructure item that Gate-A is not the
right gate to clear.

Third, the §24 prompt's GA17 wording ("record the finding even if the
method is not yet implemented") is the operationally correct
treatment: the Gate-A audit records whether the infrastructure exists,
and the finding (exists / pending) informs the execution-authorization
memo. The §24 prompt's report template (heading 6, "Cluster-robust SE
infrastructure status") and its required final statement ("State
whether cluster-robust SE infrastructure is confirmed or pending")
are both consistent with GA17 as a status-record check.

**The Gate-A verdict semantics are therefore:**

- **Gate-A PASS:** GA1–GA16 all pass, and GA17 records the cluster-
  robust SE infrastructure as confirmed callable. The pooled
  specification is fully Gate-A-clear, and the execution-authorization
  memo may proceed without a cluster-robust-SE blocker.

- **Gate-A PASS WITH BLOCKER:** GA1–GA16 all pass, and GA17 records
  the cluster-robust SE infrastructure as *pending*. The pooled YAML
  and data input are structurally validated (the Gate-A static checks
  pass), but the cluster-robust SE infrastructure must be built and
  confirmed before the pooled-estimation authorization memo is issued.
  This is the expected Gate-A outcome given the current pending
  infrastructure (§3 P3).

- **Gate-A FAIL:** any of GA1–GA16 fails. The pooled YAML or data
  input is structurally invalid and must be corrected before Gate-A
  is re-run.

The corrected §19 rule (C3) is: Gate-A passes (PASS or PASS WITH
BLOCKER) when GA1–GA16 pass; the pooled-estimation *authorization*
memo requires both Gate-A passing and GA17 cleared (the cluster-robust
SE infrastructure confirmed callable). The distinction separates the
YAML-and-data static-validation gate (Gate-A, GA1–GA16) from the
estimator-engine-capability gate (the cluster-robust SE
infrastructure, GA17), which is correctly located at the execution-
authorization review.

Under this interpretation, the expected Gate-A outcome on the current
codebase is **PASS WITH BLOCKER**: the YAML and data input are
expected to validate (GA1–GA16), and GA17 is expected to record the
cluster-robust SE infrastructure as pending, identifying the build-
the-sandwich-estimator task as the blocker between Gate-A and
execution authorization.

---

## 7. Whether a full design memo rewrite is needed

**No. A full rewrite is not needed. The four required corrections
(§3) are localised edits to the design memo and its embedded Gate-A
prompt.**

The design memo's substance — the pooled specification, the year-
effect treatment, the GSURv2 treatment, the cluster-robust inference
design, the SA2 criteria, the not-authorised scope — is correct and
requires no change. The four corrections are confined to:

- The §24 Gate-A prompt's read instruction (C1, C2): replace "read
  column names only, do not load full data" with the bounded-read
  scope (§5), and add the explicit read-scope list. This is an edit
  to one parenthetical and one added paragraph in the §24 prompt.

- The §19 GA17 row and the §19 "all must PASS" rule (C3): restate
  GA17 as a status-record check, and split the passing condition
  (GA1–GA16) from the execution-authorization condition (GA17
  cleared). Align the §24 prompt's GA17 wording (already close) and
  the §24 report template's verdict semantics to admit PASS WITH
  BLOCKER. This is an edit to one table row, one rule sentence, and
  the §24 verdict-statement wording.

- The §1 evidence chain (C4): add the heading-template addendum
  citation with its disposition. This is one added bullet.

These edits are localised and do not propagate to the design
decisions. The parameter count (55), the year-dummy specification,
the cluster-robust VCV formula, the SA2 thresholds, and the
diagnostic protocol are all unchanged. A full rewrite would be
disproportionate to four localised corrections and would risk
disturbing the correct substance.

The recommended mechanism is a correction note (paralleling the
construction-verdict and execution-report corrections in this
project's discipline) or a v2 of the design memo applying the four
edits, with this addendum recording the review verdict and the
required corrections. Either mechanism preserves the v1 memo's
correct substance and applies the four localised corrections.

---

## 8. Whether Gate-A YAML audit may proceed

**Yes, the Gate-A YAML audit may proceed, once the four corrections
(§3) are applied to the design memo and the embedded Gate-A prompt.
The corrected prompt is internally consistent and executable, and the
Gate-A audit is a static-validation step that does not estimate or
modify data.**

The Gate-A YAML audit may proceed because it is the correct next step
and because, with the corrections applied, it is executable within a
clear static-validation boundary. The audit (a) derives the pooled
YAML from the M1-clean YAML with the two year-dummy additions, (b)
parses it with `estimation_spec_parser.py`, and (c) runs the GA1–GA17
checks, producing the Gate-A parse report.

The audit operates within the following static-validation boundary,
which the corrections establish:

*Permitted.* Reading the pooled parquet schema; reading the specific
columns required for GA13–GA16 (`year_tag`, `gsur`, `gsur_male`,
`gsur_female`, `ils_dispy_real`, `ils_dispy`, `cluster_id`,
`idorighh`, `household_type`); reading a bounded row sample or
selected row groups sufficient for the non-null, distinctness, and
equality checks; constructing the `year_2015_indicator` and
`year_2017_indicator` as `(year_tag == 1)` and `(year_tag == 3)` for
the GA13 smoke test; deriving and writing the pooled YAML; parsing
the YAML; and recording the GA1–GA17 results and the GA17 cluster-
robust-SE-infrastructure status.

*Prohibited.* Loading the full 1,244,500-row dataset into memory when
a bounded sample suffices; modifying any column, row, parquet,
sidecar, or config; modifying the M1-clean or M1-naive
specifications; running any estimation, solver call, or precompute
beyond the GA13 indicator-construction smoke test; and issuing any
execution authorization.

The Gate-A audit is expected to return **PASS WITH BLOCKER** (§6):
GA1–GA16 are expected to pass (the YAML derivation is mechanical and
the data input is the validated construction output), and GA17 is
expected to record the cluster-robust SE infrastructure as pending,
identifying the sandwich-estimator build as the blocker between
Gate-A and execution authorization. A PASS WITH BLOCKER outcome is
the expected and acceptable Gate-A result; it advances the pipeline
to the cluster-robust-SE infrastructure task without authorising
estimation.

The Gate-A audit does not authorise pooled estimation (§9). It
produces the Gate-A parse report and the pooled YAML; the execution-
authorization memo, gated behind both Gate-A passing and the GA17
blocker cleared, is a separate downstream document.

---

## 9. What remains not authorized

The addendum authorises only the corrected Gate-A YAML audit (§8). It
does not authorise the following; each is separately gated.

(N1) **Pooled estimation execution.** No pooled estimation is
authorised. The pooled estimation requires the Gate-A audit to pass,
the GA17 cluster-robust SE infrastructure blocker to be cleared, and
a separate pooled-estimation authorization memo. The design memo's
§23 and §3 establish this gating, and the addendum reaffirms it.

(N2) **Cluster-robust SE infrastructure as a fait accompli.** The
addendum does not authorise or pre-approve the cluster-robust SE
implementation; it identifies the infrastructure as the GA17 blocker
(§6). The implementation is a separate task (the sandwich-estimator
build over 9,657 clusters), and its confirmation is part of the
execution-authorization review, not this addendum or the Gate-A
audit.

(N3) **Welfare implementation or welfare computation.** No welfare
work is authorised. Welfare computation requires an accepted SA2
verdict on a pooled specification and a separate welfare-computation
authorization (design memo §23).

(N4) **Canonical promotion.** No canonical promotion of the pooled
YAML, the pooled dataset, or any pooled output is authorised.

(N5) **M1-clean displacement.** The pooled specification does not
displace M1-clean. M1-clean 2016 remains the active JMP baseline,
displaced only by a future SA2 verdict on an estimated pooled
specification (design memo §23; M1-clean verdict).

(N6) **P3b, P4, or alternative pooled specifications.** P3b (hard-
blocked pending the ISF gate), P4 (not a priority), and the year-
interacted or other alternative pooled specifications (post-SA2
sensitivities) are not authorised.

The addendum authorises the corrected Gate-A YAML audit and nothing
downstream of it.

---

## 10. Exact next task

**The immediate next task is to apply the four corrections (§3) to
the design memo and its embedded Gate-A prompt, then issue the
corrected Gate-A YAML audit.**

The task sequence from the current point is:

1. *Apply the four corrections* (Claude Project chat or a direct
   edit). Apply C1 and C2 (the bounded-read scope replacing "read
   column names only," with the explicit read-scope list) to the §24
   Gate-A prompt; apply C3 (GA17 as a status-record check, the
   PASS / PASS WITH BLOCKER / FAIL verdict semantics, and the split
   between the Gate-A-passing condition and the execution-
   authorization condition) to §19 and the §24 prompt and report
   template; apply C4 (the heading-addendum citation) to the §1
   evidence chain. The mechanism is a design-memo v2 or a correction
   note recording the four edits, with this addendum as the review
   record. This is the immediate next task.

2. *Issue the corrected Gate-A YAML audit* (Claude Code Sonnet),
   using the corrected §24 prompt. The audit derives the pooled YAML,
   parses it, runs GA1–GA17 within the static-validation boundary
   (§8), and produces
   `Results/RURO_occ_P3a_pooled_gate_A_parse_report_v1.md` with the
   Gate-A verdict (expected PASS WITH BLOCKER, §6).

3. *Cluster-robust SE infrastructure* (Claude Code Sonnet),
   conditional on the Gate-A audit identifying it as the blocker. The
   sandwich-estimator build over the 9,657 `idorighh` clusters, with
   the score-matrix and meat-matrix computation (§15), confirmed
   callable on the pooled parquet. This clears the GA17 blocker.

4. *Pooled-estimation authorization memo* (Claude Project chat),
   conditional on the Gate-A audit passing and the GA17 blocker
   cleared. The memo that authorises the pooled estimation execution,
   specifying the estimation scope, the three-start protocol, and the
   cluster-robust inference.

5. *Pooled estimation and SA2 verdict*, conditional on the execution
   authorization. The three-start estimation, the post-estimation
   diagnostics (D1–D12), and the SA2 verdict (S1–S11) that determines
   whether the pooled specification is accepted and whether it
   displaces M1-clean.

The corrected Gate-A YAML audit (step 2) is the immediate next
execution task, after the four corrections (step 1) are applied. The
audit does not authorise pooled estimation; it produces the pooled
YAML and the Gate-A parse report, and identifies the cluster-robust
SE infrastructure as the blocker between Gate-A and execution.

Tasks explicitly not authorised, and not the next task: pooled
estimation execution (N1), the cluster-robust SE implementation as
an authorised build under this addendum (N2 — it is the identified
blocker, sequenced at step 3, but not authorised by this addendum),
welfare implementation or computation (N3), canonical promotion (N4),
and M1-clean displacement (N5).

**Required final statements**

- **Pooled estimation execution is NOT authorized.** The corrected
  Gate-A YAML audit is the authorised next step; pooled estimation
  requires the Gate-A audit to pass, the GA17 cluster-robust SE
  infrastructure blocker to be cleared, and a separate pooled-
  estimation authorization memo.

- **Welfare implementation and welfare computation are NOT
  authorized.** Separately gated behind an accepted SA2 verdict and a
  welfare-computation authorization.

- **M1-clean 2016 remains the active JMP baseline.** The pooled P3a
  design, the Gate-A audit, and the pooled specification do not
  displace M1-clean; displacement requires a future SA2 verdict on an
  estimated pooled specification.
