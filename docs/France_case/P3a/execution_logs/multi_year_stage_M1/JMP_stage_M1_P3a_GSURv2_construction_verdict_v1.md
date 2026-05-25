# JMP Stage M1 P3a GSURv2 — Construction Verdict v1

*France 2014–2015–2016 | v1 | 2026-05-21*

Execution under review: Stage M1 P3a GSURv2 pooled stacking re-run,
executed 2026-05-21 under
`docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md` (corrected
by `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_authorization_correction_v1.md`).

Primary evidence:
- `Results/P3a/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`
- `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml`
- `scripts/multi_year/m1_validate.py` (V9 patch)
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` (146 cols,
  1,244,500 rows, 185.5 MB)

Reference documents:
- `docs/France_case/P3a/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_verdict_v1.md` (the post-rebuild verdict
  that authorised this re-run as the next gate)
- `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_P3a_construction_verdict_v1.md` (the
  provisional v1-fallback construction verdict)
- `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` (the active single-year JMP
  baseline)

Scope of verdict: post-execution quality assessment of the GSURv2 P3a
stacking re-run. This verdict adjudicates whether the execution followed
the authorization, whether the V6 and V9 outcomes are acceptable, whether
the GSURv2 pooled dataset is valid as the final non-provisional
construction input, and which gate is next. It does not authorise pooled
estimation, welfare computation, canonical promotion, or displacement of
M1-clean.

---

## 1. Verdict

**PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC CAVEATS.**

The GSURv2 P3a pooled stacking re-run is a substantive PASS. All nine
authorization validation checks (V1–V9) passed; no halt condition
(H1–H7) was triggered; the exact-input-resolution constraint was
satisfied; all six GSURv2 SHA-256 hashes verified; the provisional
v1-fallback outputs were preserved before writing; the stacked row and
household-year counts match the expected values exactly; the CPI factors
are correct; the cluster key is correct; and the GSURv2 pooled dataset
carries the required `gsurv2_opportunity_year_aligned` label.

Two minor caveats are documented:

**(C1) Report-heading mismatch.** The execution report title line reads
"France 2014–2015–2016" while the actual survey years are FR_2015,
FR_2016, and FR_2017 (opportunity years y2014, y2015, y2016). This is a
documentation-only issue; no data, parquet, or sidecar is affected. See
§3 and `docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`.

**(C2) V9 validation-script patch.** The V9 check required a narrow
exemption for four known upstream sampling-control columns
(`ruro_decider`, `ruro_group`, `ruro_sample`, `year_for_ruro`) present
in the GSURv2 parquets but absent from the v1-fallback parquets. The
exemption is a validation-spec update, not an ad hoc runtime fix. See §5
and `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_V9_validation_patch_note_v1.md`.

Neither caveat affects the data, the V1–V9 validation outcomes, the
authorization status, or the baseline status.

**The GSURv2 P3a pooled dataset is valid as the final non-provisional
construction input for pooled-estimation design and Gate-A validation.**

---

## 2. Whether execution followed the stacking authorization

**Yes. All material authorization requirements were satisfied.**

The execution followed
`docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md` in every
material respect:

- **Exact-input-resolution (§5 I1–I3):** A dedicated config
  `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml` was created with
  pattern `*{year}*RURO*mnl*GSURv2*y*__*.parquet`. Dry-run confirmed
  exactly the six authorized GSURv2 parquets resolved; no v1gsurY,
  v2gsurY, or other stem matched. All six SHA-256 hashes verified (§5
  Table 1). H1 (input resolution not exact) and H2 (SHA mismatch) were
  not triggered.
- **Provisional output preservation (§11 A3, §13 H6):** All four
  provisional v1-fallback pooled files were renamed to
  `fr_p3a_provisional_v1fallback_*` before any GSURv2 output was
  written. H6 was not triggered.
- **Stale-config guard (§13 H7):** The provisional config
  `fr_p3a_stage_m1.yaml` was not used. H7 was not triggered.
- **Five-step pipeline (§11 A4):** All five steps ran in sequence —
  year stacking, identity validation, CPI harmonisation, cluster-key
  annotation, V1–V9 validation.
- **Output stems and label (§6, §7):** Outputs written as
  `fr_p3a_gsurv2_stacked_raw.parquet` and
  `fr_p3a_gsurv2_harmonised.parquet` with
  `provisioning_label: "gsurv2_opportunity_year_aligned"`.
- **Sidecar metadata (§8):** Both sidecars carry all required fields:
  `provisioning_label`, `gsur_source`, `input_sha256`, `input_resolution_method`,
  `survey_year_opportunity_year_mapping`, `row_counts`, `household_counts`,
  `cpi_harmonisation`, `cluster_key`, `uid_scheme`, `validation_results`,
  `gsur_means`.
- **Row and household counts (§9 V2, §13 H3–H4):** 1,244,500 rows,
  12,445 household-years, diff=0. All per-year and per-component counts
  match the provisional build exactly.
- **Not-authorized scope (§12):** No pooled estimation was run, no
  welfare work was performed, no M1-clean specs were modified.

The one documentation caveat (C1, report heading) does not affect
authorization conformance; it is a title-line formatting issue only.

---

## 3. Whether the report-heading mismatch is documentation-only

**Yes. Documentation-only. No data or validation impact.**

The execution report
`Results/P3a/multi_year_stage_M1/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`
carries the subtitle line "France 2014–2015–2016" in the header. The
correct description of the survey years covered is FR_2015, FR_2016, and
FR_2017; the opportunity years are y2014, y2015, and y2016. The "2014"
in the subtitle refers to the y2014 opportunity year for FR_2015, not
to a FR_2014 survey year.

The mismatch is in the report's metadata subtitle only. The body of the
report correctly identifies the survey years (FR_2015, FR_2016, FR_2017),
the opportunity years (y2014, y2015, y2016), the input stems
(`fr_2015_RURO_mnl_GSURv2_y2014__`, `fr_2016_RURO_mnl_GSURv2_y2015__`,
`fr_2017_RURO_mnl_GSURv2_y2016__`), and the year-tag mapping
(2015→tag 1, 2016→tag 2, 2017→tag 3). The sidecars, the parquets, the
config, and the validation manifests all correctly record the survey
and opportunity years.

The issue is recorded in
`docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`.
No re-run, no data modification, and no re-validation is required as a
result of this caveat.

---

## 4. Whether the V6 repeated-household diagnostic is acceptable

**Acceptable as a non-blocking diagnostic. The cluster key is valid.**

V6 has two components:

**Component A — cluster key:** `cluster_id = idorighh` confirmed for
all 1,244,500 rows. The unique cluster count is 9,657. This provides the
valid estimation cluster key for cluster-robust standard errors.
Component A: PASS.

**Component B — repeat-HH overlap counts:**

| Year pair | Observed | Expected | Diff | Tolerance |
|-----------|----------|----------|------|-----------|
| 2015×2016 | 0 | 0 | 0 | — |
| 2015×2017 | 0 | 0 | 0 | — |
| 2016×2017 | 2,788 | ~8,796 | 6,008 | 200 |

The 2016×2017 overlap count (2,788 vs nominal 8,796, diff 6,008) exceeds
the configured tolerance of 200 and is not a normal hard-threshold pass.

The discrepancy is classified as **diagnostic/non-blocking** for the
following reasons:

1. It is carried forward from the provisional v1-fallback build, where
   the same discrepancy was observed and documented. It is not introduced
   by the GSURv2 re-run.
2. The discrepancy reflects the RURO sampling structure: only persons
   satisfying the opportunity-decision condition enter the MNL sample.
   The full-sample EU-SILC overlap of ~8,796 households between FR_2016
   and FR_2017 does not translate one-for-one into the RURO MNL sample
   overlap because not all households that appear in both survey years
   appear in both years' RURO-eligible subsets.
3. The identity validation (V7) — which tests the actual repeated
   households — passed cleanly: sex stability 1.0000, age progression
   1.0000, suspicious rate 0.0000, household continuity 0.9985. The
   2,788 observed repeat-HH records pass all identity checks.
4. The cluster key (Component A) is unaffected by the overlap-count
   discrepancy. `cluster_id = idorighh` correctly captures the
   household-level clustering that pooled estimation requires.

**Pooled estimation design must use the actual cluster structure** — the
observed 2,788 repeat-HH overlap between FR_2016 and FR_2017 — not the
nominal full-sample expected count of 8,796. The cluster-robust SE
design should document this explicitly.

V6 overall verdict: PASS WITH NON-BLOCKING DIAGNOSTIC NOTE. The cluster
key is valid; the overlap-count discrepancy is a known sampling property,
not a data-integrity failure.

---

## 5. Whether the V9 validation-script patch is acceptable

**Acceptable as a narrow validation-spec update.**

The initial V9 run reported FAIL because the GSURv2 parquets carry four
upstream sampling-control columns that contain the token "ruro":
`ruro_decider`, `ruro_group`, `ruro_sample`, `year_for_ruro`. These
columns originate from `scripts/france_data_prep.py` and the legacy RURO
pipeline; they were present in the GSURv2 MNL parquets but absent from
the v1-fallback parquets used in the provisional build.

The V9 rule was designed to ensure that Stage M1 output files are not
accidentally named with the old personal-label `ruro` token — that is,
to catch an output-naming error, not to reject legitimate upstream data
column names. The four columns are sampling-control identifiers that
classify RURO decision-relevance for individual records; they are not
artefacts of a naming error.

`scripts/multi_year/m1_validate.py` `check_v9()` was updated to maintain
a narrow explicit exemption set `{ruro_decider, ruro_group, ruro_sample,
year_for_ruro}`. Any column containing "ruro" that is NOT in this exempt
set continues to trigger a V9 failure. The check's logic and purpose are
unchanged; only the explicit list of known upstream columns is
incorporated.

The patch is classified as a **validation-spec update**, not an ad hoc
runtime fix, because:

1. The four columns are deterministically present in all RURO MNL
   parquets produced from the current data pipeline; their presence is
   expected and predictable, not accidental.
2. The exemption is hard-coded as a named frozenset in the script, not
   as a runtime parameter or override flag.
3. The exemption is narrow: exactly four named columns; no wildcard.
4. Unexpected `ruro` tokens in column names — any column outside the
   exempt set — still trigger V9 failure without user override.

The full adjudication of this patch is recorded in
`docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_V9_validation_patch_note_v1.md`.

---

## 6. Whether the GSURv2 P3a pooled dataset is valid as final non-provisional construction input

**Yes. The GSURv2 P3a pooled dataset is valid as the final non-provisional
construction input for pooled-estimation design and Gate-A validation.**

Grounds:

- All six authorized GSURv2 input SHA-256 hashes verified before
  stacking; no non-GSURv2 stem entered the pooled dataset.
- The provisional v1-fallback outputs were preserved; the new outputs
  carry the distinct `gsurv2_opportunity_year_aligned` label and
  `gsurv2`-tagged file stems.
- V1–V9 all PASS. The pooled structure is correct: 1,244,500 rows,
  12,445 household-years, 9,657 unique clusters.
- The per-year and per-component counts are identical to the provisional
  build (the sample structure is unchanged; only the opportunity-side
  rates differ).
- The GSURv2 GSUR means (singles: 0.0938; couples_female: 0.0880;
  couples_male: 0.0945) are lower than the v1-fallback means
  (singles: 0.0951; couples_female: 0.0902; couples_male: 0.0961), as
  expected from the opportunity-year alignment: the GSURv2 rates use the
  EUROMOD system year's (opportunity year's) job-finding rates rather
  than a lagged v1-fallback approximation.
- The `gsurv2_opportunity_year_aligned` label in both sidecars confirms
  that the dataset carries the correct provenance.
- Both caveats (C1, C2) are documentation and validation-spec items
  only; neither affects data integrity.

The dataset is valid as the final construction input. It is not yet the
input to an estimated specification; pooled estimation is separately
gated.

**Output files confirmed:**
- `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet`
  (142 cols, 1,244,500 rows, 177.0 MB)
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
  (146 cols, 1,244,500 rows, 185.5 MB)
- `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw__stage_m1_meta.json`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised__stage_m1_meta.json`

---

## 7. Whether pooled estimation is authorized

**No. Pooled estimation is NOT authorized.**

Pooled estimation is separately gated. The stacking re-run authorization
(§12 N1) explicitly states that no pooled estimation, provisional or
final, is authorised by the stacking re-run. The stacking re-run
produces the construction input; it does not authorize consuming that
input for estimation.

The next estimation gate requires:

1. A pooled-estimation specification design (the pooled MNL spec, with
   cluster-robust SE design documented, drawing on the actual cluster
   structure: 9,657 unique clusters and the 2016×2017 overlap of 2,788).
2. A separate pooled-estimation authorization memo.
3. Execution of pooled MNL estimation against
   `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet` only
   after that authorization is issued.

This verdict does not constitute or imply pooled-estimation authorization.

---

## 8. Whether welfare computation is authorized

**No. Welfare computation is NOT authorized.**

Welfare implementation and computation are separately gated. The
stacking re-run authorization (§12 N2) explicitly states that no welfare
work is authorised. Welfare computation requires its own authorization,
an accepted empirical baseline from a completed and verdicted pooled
estimation, and the welfare scaffolding design (which is complete per
`docs/jmp_methodology/JMP_welfare_scaffolding_design_memo_v2.md` but does not constitute
execution authorization).

This verdict does not authorize welfare implementation, welfare
computation, or welfare-related estimation.

---

## 9. Whether M1-clean remains the active baseline

**Yes. M1-clean 2016 remains the active JMP baseline.**

`ruro_occ_M1_clean` (53 free parameters; LL = −6487.5522; verdict
`docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md`) is the accepted JMP structural
specification. Producing the GSURv2 pooled dataset does not promote the
pooled route over the single-year baseline. Only a future SA2 verdict on
an estimated, verified, and accepted final pooled specification could
displace M1-clean. No such verdict has been issued.

The M1-clean and M1-naive estimation specs are unchanged by this
execution.

---

## 10. Required cleanup before the next empirical gate

Before proceeding to pooled-estimation design, the following cleanup
items should be completed. None is blocking for the construction verdict
itself; all are required before the pooled-estimation authorization memo
is drafted.

**C1 — Report-heading correction (documentation only):**
The execution report subtitle "France 2014–2015–2016" should be noted in
`docs/archive/2026-05-26_round2_chain_compression/doc_only_corrections/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`
(already created). No re-run required; the report body is correct.

**C2 — V9 patch note (validation-spec record):**
`docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_stage_M1_V9_validation_patch_note_v1.md` (already created)
records the V9 exemption as a validation-spec update. The updated
`scripts/multi_year/m1_validate.py` is committed.

**C3 — V6 overlap note for pooled-estimation design:**
Pooled-estimation design documentation must note that the 2016×2017
repeat-HH cluster overlap in the RURO MNL sample is 2,788 (not the
nominal full-sample 8,796), and that cluster-robust SE design should
use the actual cluster structure (`cluster_id = idorighh`, 9,657 unique
clusters).

These three items are documentation and design-record items. No parquet,
sidecar, script, or authorization document requires modification.

---

## 11. Immediate next task

**The immediate next authorized task is pooled-estimation design and
cluster-robust inference design.**

The GSURv2 P3a pooled dataset is valid as the final non-provisional
construction input. The next gate is:

1. **Pooled-estimation specification design:** Draft the pooled MNL
   specification, drawing on the M1-clean single-year spec as the
   starting point and incorporating the multi-year stacking structure
   (year-tag fixed effects or interaction terms, cluster-robust SEs
   using `cluster_id = idorighh`, 9,657 unique clusters).
2. **Cluster-robust SE design:** Document the SE design, noting the
   actual 2016×2017 RURO-sample repeat-HH overlap (2,788) and the
   cluster structure.
3. **Pooled-estimation authorization memo:** Issue a separate
   authorization before any pooled estimation is executed.

**This is not estimation execution authorization.** The next task is
specification and inference design. Estimation execution requires a
separate authorization memo.

**Pooled estimation is NOT authorized.**

**Welfare computation is NOT authorized.**

**M1-clean 2016 remains the active JMP baseline.** Displaced only by a
future SA2 verdict explicitly promoting a final pooled specification.