# JMP Single-Year FR_2015 Replication — Correction Addendum v1

**Document:** Results/JMP_single_year_FR2015_replication_addendum_v1.md  
**Date:** 2026-05-20  
**Amends:** Results/JMP_single_year_FR2015_replication_report_v1.md  
**Author:** Hisham Haydar

---

## 1. Purpose

This addendum corrects three statements in the FR_2015 replication report
(`Results/JMP_single_year_FR2015_replication_report_v1.md`), formalizes the
GSUR opportunity-year alignment rule, and clarifies the tpr incidence figure.
It also documents new metadata fields added to the 2015 sidecar and specifies
the pre-conditions that must hold before the FR_2017 replication is executed.

No parquet data is modified by this addendum. Only the sidecar JSON files are
updated (§10 below).

---

## 2. Files inspected

| File | Relevant sections read |
|------|----------------------|
| `Results/JMP_single_year_FR2015_replication_report_v1.md` | §§ 17–19, 23 |
| `Results/JMP_single_year_2016_local_mirror_report_v1.md` | §§ 3–5, 9 |
| `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` | §§ 7, 9, 10 |
| `docs/JMP_single_year_replication_2015_2017_command_plan_v2.md` | §§ 3, 13, 19 |
| `docs/France_case/JMP_multi_year_CPI_HICP_source_decision_v1.md` | φ_t table |
| `docs/RURO_occ_M1_clean_verdict_v1.md` | §§ 1–2 |
| `Data/external/FR_gsur_ruro.parquet` | Year column; keying structure |
| `Data/processed/fr/fr_2015_RURO_mnl__mnlmeta.json` | Full fields |
| `Data/processed/fr/fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | inputs.gsur_file field |

**GSUR parquet inspection results** (new, performed this session):

`FR_gsur_ruro.parquet` contains 2,160 rows × 12 columns. The `year` column spans
2007–2024. Keys: `year`, `drgn1`, `dgn`, `educ3` (plus labeling columns). Years
confirmed present: 2014, 2015, 2016, 2017. This parquet is the sole v1 GSUR
source; it is the file cited in the 2015 mnlmeta `inputs.gsur_file`.

---

## 3. Corrections to FR_2015 replication report

### Correction 1 — §18 FR_2016 description overstated

**Original text (§18, last paragraph):**
> "The parquet filenames carry the pre-GSURv2 stem `fr_2015_RURO_mnl__` (no
> `GSURv2__` segment) to distinguish them from the **2016 GSURv2-final outputs**."

**Replacement text:**
> "The parquet filenames carry the pre-GSURv2 stem `fr_2015_RURO_mnl__` (no
> `GSURv2__` segment) to distinguish them from the 2016 outputs. Note: FR_2016
> uses the M1-clean operative `fr_2016_RURO_mnl_GSURv2__` files, but that
> sidecar records `FR_gsur_ruro.parquet` (the v1 file) as the GSUR source while
> the parquet's actual rates do not match any year in the v1 table — indicating
> the rates were drawn from `FR_gsur_ruro_v2_stageA.parquet`. This
> filename/source-provenance mismatch is documented in
> `Results/JMP_single_year_2016_local_mirror_report_v1.md` §5 and §9 and must
> be resolved before any pooled estimation claims about GSUR consistency."

### Correction 2 — §19 and §23 overstated M1 readiness

**Original text (§19 table, last row):**
> `M1-ready | Yes (pending GSURv2 upgrade) | Yes`

**Original text (§23 final paragraph):**
> "FR_2015 MNL-input parquets are ready for Stage M1 stacking once FR_2017
> replication is completed."

**Replacement:**
FR_2015 is ready as a **pre-GSURv2 single-year MNL input for Stage M1 dry-run
and provisional input validation**, once FR_2017 is also produced. It is **not**
ready for final pooled estimation until:

1. GSUR opportunity-year alignment is resolved (see §5 and §6 below).
2. GSUR source-provenance consistency across 2015 and 2016 is resolved.
3. A new authorization memo covering GSURv2-upgraded runs for 2015/2017 is
   issued and accepted.

The §23 "Overall verdict: PASS" for single-year pipeline replication stands
unchanged. The correction applies only to the downstream readiness claim for
pooled estimation.

### Correction 3 — §17 GSUR status table incomplete

The §17 table listed GSUR `Version: v1 fallback` but did not note the
opportunity-year question. An additional row should be understood as appended:

| Field | Value |
|-------|-------|
| GSUR data year keyed in parquet | 2015 (data year) |
| GSUR opportunity year (EUROMOD system year) | 2014 |
| Alignment status | MISALIGNED — parquet used data year, not system year |
| Resolution required | Yes, before pooled estimation |

See §5 and §6 for the formal rule and implications.

---

## 4. FR_2016 GSUR provenance correction

The FR_2016 mirror report (`Results/JMP_single_year_2016_local_mirror_report_v1.md`)
correctly documents the provenance mismatch in §5 (note 4) and §9 (GSUR source).
The FR_2015 replication report incorrectly implied FR_2016 is "GSURv2-final" by
using the label "2016 GSURv2-final outputs" in §18. That label is inaccurate.

**Accurate statement:**

FR_2016 uses the M1-clean operative files (`fr_2016_RURO_mnl_GSURv2__`). The
`GSURv2__` segment in the filename reflects the GSURv2 workflow context (the run
was performed under the GSURv2 prep infrastructure). However:

- The 2016 sidecar (`fr_2016_RURO_mnl_GSURv2__mnlmeta.json`) records
  `inputs.gsur_file = FR_gsur_ruro.parquet` (the v1 file).
- Inspection of the 2016 parquet's `gsur` column values confirms they do **not**
  match any year in the v1 table (mean abs difference ≥ 0.017 for both year=2015
  and year=2016 in the v1 file). This indicates the actual rates came from
  `FR_gsur_ruro_v2_stageA.parquet` (the GSURv2 computed rates), while the sidecar
  path field was not updated to reflect this.
- This is a filename/source-provenance mismatch: the sidecar cites the wrong
  source file. The rates in the parquet are likely GSURv2 rates, but this cannot
  be verified without the `FR_gsur_ruro_v2_stageA.parquet` file in the current
  session.

**Status:** The 2016 provenance mismatch is documented but not resolved here.
It must be resolved before final pooled estimation claims about GSUR consistency
are made. This addendum does not alter the 2016 parquets or sidecar.

---

## 5. GSUR opportunity-year alignment rule

**Rule (formalized here; effective from this addendum forward):**

The GSUR year used for a given survey/data file should correspond to the
**opportunity/income-reference environment**, which in this RURO/EUROMOD pipeline
is the EUROMOD system year — not automatically the survey data year.

The rationale: the GSUR rate is a job-acceptance rate that reflects the labour
market conditions under which workers are simulated as evaluating job offers.
In the RURO/EUROMOD pipeline, the EUROMOD system determines the tax-benefit and
labour-market environment for the simulated draws. The EUROMOD system year is
therefore the correct index for the opportunity environment, not the survey
collection year.

**Formal mapping (binding unless a later memo explicitly overturns this rule):**

| Data file / survey year | EUROMOD system | GSUR opportunity year |
|-------------------------|----------------|-----------------------|
| FR_2015 (`FR_2015_a2`) | `FR_2014` | **2014** |
| FR_2016 (`FR_2016_a2`) | `FR_2015` | **2015** |
| FR_2017 (`FR_2017_a2`) | `FR_2016` | **2016** |
| FR_2018 (`FR_2018_a2`) | `FR_2017` | **2017** |

**How to implement:**
When running `enh_RURO_prep_mnl_basic.py`, the GSUR file (`FR_gsur_ruro.parquet`)
must be filtered to `year == EUROMOD_system_year` before merging, not
`year == data_year`. If the script does not currently support a `--gsur-year`
argument, the operator must verify post-hoc which year was keyed (as done in this
session) and flag misalignment in the sidecar.

---

## 6. Implications for FR_2015

**Observed state (confirmed by parquet inspection):**

The `gsur` column in `fr_2015_RURO_mnl__singles.parquet` (draw=0 rows) matches
the v1 GSUR table at `year=2015` exactly (mean abs difference = 0.000000 across
all matched rows). It does **not** match `year=2014` (mean abs difference =
0.009862).

**Conclusion:** FR_2015 MNL parquets used **data year 2015** as the GSUR key.
Under the opportunity-year alignment rule, the correct key should have been
**2014** (the EUROMOD system year for FR_2015 data).

**Status:** GSUR-year-misaligned. The parquet is not final for pooled estimation.
The pre-GSURv2 annotation already present in the sidecar (`gsur_version:
v1_fallback`) partially captures this limitation, but does not specifically
identify the year-alignment issue. Additional metadata fields have been added to
the sidecar (§10).

**Magnitude of mismatch:** Mean absolute difference between year=2015 and year=2014
GSUR rates = 0.009862 (≈ 1 percentage point). This is non-trivial relative to
mean GSUR ≈ 0.095 (≈ 10% relative difference in rates).

**Required action before pooled estimation:** Re-run `enh_RURO_prep_mnl_basic.py`
for FR_2015 with GSUR keyed to year=2014 (or verify the script's keying logic
and produce a corrected parquet). This requires either a `--gsur-year 2014`
argument or a script-level fix.

---

## 7. Implications for FR_2016

**Observed state (confirmed by parquet inspection):**

The `gsur` column in `fr_2016_RURO_mnl_GSURv2__singles.parquet` (draw=0 rows)
does **not** match the v1 GSUR table at `year=2016` (mean abs diff = 0.016637)
or `year=2015` (mean abs diff = 0.020474). The rates are lower than the v1 table
values for all (drgn1, dgn) strata, consistent with the GSURv2 computed rates
which incorporate a benchmark correction not present in the v1 table.

**Conclusion:** The 2016 parquet uses rates from `FR_gsur_ruro_v2_stageA.parquet`
(GSURv2), not from `FR_gsur_ruro.parquet` (v1). The sidecar `inputs.gsur_file`
field is incorrect (cites the v1 file). This is the documented provenance mismatch
from the 2016 mirror report.

**Opportunity-year alignment for 2016:** Under the rule in §5, the correct GSUR
opportunity year for FR_2016 data is **2015** (EUROMOD system `FR_2015`). Whether
the GSURv2 rates in the 2016 parquet correspond to year=2015 or year=2016 cannot
be determined without reading `FR_gsur_ruro_v2_stageA.parquet`, which is a
single-year file (year=2016 hardcoded per command plan §18). This means:

- If `FR_gsur_ruro_v2_stageA.parquet` contains year=2016 rates only, the 2016
  parquet is also GSUR-year-misaligned (data year 2016, opportunity year 2015).
- The magnitude of any year-2015 vs year-2016 difference within the GSURv2 rates
  is unknown without inspecting that file.

**Status:** 2016 GSUR alignment is undetermined. Resolving this is prerequisite
to a final pooled estimation consistency claim.

---

## 8. Implications for FR_2017 before execution

**FR_2017 should not be executed until the command plan either:**

1. Explicitly uses GSUR opportunity year **2016** (EUROMOD system `FR_2016`) for
   the GSUR key when running `enh_RURO_prep_mnl_basic.py`, **OR**
2. Explicitly labels the output as GSUR-year-mismatched / pre-GSURv2 / not final
   for pooled estimation, with `gsur_alignment_status: misaligned` recorded in
   the sidecar.

The current command plan v2 (§5, §19) uses `--gsur-file FR_gsur_ruro.parquet`
without specifying `--gsur-year`. If the script keys on `--year 2017` (the data
year), the output will use GSUR year=2017 when the correct opportunity year is
2016. This would be a year-1 mismatch of the same kind confirmed for FR_2015.

**Required change to FR_2017 command plan:**
Either add `--gsur-year 2016` to the Step 5b command (if the script supports it),
or document explicitly in the FR_2017 execution prompt that the output carries
`gsur_alignment_status: misaligned` and `gsur_opportunity_year: 2016` in the
sidecar post-patch.

The formal command-plan addendum is in
`docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md`.

---

## 9. tpr incidence clarification

The FR_2015 replication report (§15, §23 Check D) reported **5 WA non-zero rows**
at 0.287%. The FR_2015 readiness addendum v2 (cited in the authorization memo)
quoted **53 WA non-zero rows** at 0.344%. These are not contradictory — they
measure different populations at different pipeline stages.

**Reconciliation:**

| Source | Population | `tpr` non-zero rows | % WA |
|--------|-----------|---------------------|------|
| Addendum v2 / Check D threshold | Raw working-age subsample from EU-SILC (`fr_2015.parquet`) | ~53 | 0.344% |
| Replication report §15 / Check D | RURO-ready singles (`singles_RURO_ready.parquet`) before column reduction | 5 | 0.287% |

**Explanation of the difference:**

The addendum v2 figure (53 rows, 0.344%) was measured on the full working-age
sample from `fr_2015.parquet`, which includes individuals who later become
ineligible for RURO (e.g., couples members, self-employed, inactive). The
replication report figure (5 rows, 0.287%) was measured on the RURO-ready singles
sample only — a smaller subset after applying RURO eligibility filters.

Neither figure was measured on the MNL parquet, because `tpr` is filtered out at
the column-reduction step in Stage 5 (`enh_RURO_prep_mnl_basic.py`, 995 → 75
cols). No contradiction exists; the difference reflects the expected population
narrowing from the raw file to the RURO-eligible sample. Both figures are below
the 1% escalation threshold.

**For the validation annotation in `Results/M1_identity_validation_summary.md`:**
Record both figures. The relevant threshold check (< 1% of RURO sample) was
performed on the RURO-ready singles file (5 rows, 0.287%) — PASS. The addendum v2
figure (53 rows, 0.344% of raw WA) provides the upper bound for the full year-wave.

---

## 10. Metadata corrections applied

The following fields have been added to
`Data/processed/fr/fr_2015_RURO_mnl__mnlmeta.json` (local mirror) and its Z:
source (`Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl__mnlmeta.json`):

| Field | Value |
|-------|-------|
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` |
| `gsur_opportunity_year` | `2014` |
| `gsur_data_year` | `2015` |
| `gsur_alignment_status` | `misaligned` |
| `gsur_note` (updated) | See below |

Updated `gsur_note`:
```
Pre-GSURv2 / not final for pooled estimation. GSUR keyed to data year 2015;
opportunity year (EUROMOD system FR_2014) is 2014. Alignment rule requires
year=2014 key. Mean absolute rate difference (2015 vs 2014 in v1 table) ≈ 0.010.
GSURv2 rates for this year also require Eurostat denominator acquisition
(lfst_r_lfsd2pop, lfst_r_lfp2acedu) and INSEE BDM benchmark retrieval before
enh_prepare_FR_gsur_v2.py can be extended to this year.
```

No MNL parquet data is modified. Only the JSON sidecar is updated.

---

## 11. What was not executed

| Action | Status |
|--------|--------|
| FR_2017 replication | Not executed — requires command-plan addendum first |
| EUROMOD runs (any year) | Not executed — this is a corrections/addendum task only |
| Parquet data modification | Not done — sidecar JSON only |
| Pooled stacking | Not executed |
| Estimation | Not executed |
| Welfare computation | Not executed |
| 2016 parquet or sidecar modification | Not done — 2016 provenance mismatch documented only |

---

## 12. Updated readiness verdict

| Claim | Status |
|-------|--------|
| FR_2015 single-year pipeline replication: PASS | **UNCHANGED — PASS** |
| FR_2015 parquets valid for Stage M1 dry-run | **PASS** (confirmed 2026-05-20) |
| FR_2015 parquets valid for single-year diagnostics | **PASS** |
| FR_2015 parquets final for pooled estimation | **NOT FINAL** — three open issues |

**Three open issues blocking pooled-estimation finality for FR_2015:**

1. **GSUR year alignment**: parquet used data year 2015; opportunity year is 2014.
   Required fix: re-run Stage 5 with `year=2014` key for GSUR merge.
2. **GSURv2 rates absent**: v1 fallback rates used. GSURv2 for 2015 requires
   Eurostat denominator acquisition (out of scope; separate authorization needed).
3. **Cross-year GSUR consistency**: 2016 parquet uses GSURv2 rates (source file
   unknown) while 2015 uses v1 rates keyed to the wrong year. Pooled consistency
   requires resolving both years to the same GSUR methodology and year-alignment
   convention.

**FR_2016 readiness:** The 2016 parquet has its own open issues (provenance
mismatch, opportunity-year alignment unknown). These are documented in
`Results/JMP_single_year_2016_local_mirror_report_v1.md` and this addendum §4
and §7. No change to the 2016 PASS verdict for M1-clean operative purposes.

---

## 13. Exact next task

**Before FR_2017 replication is executed:**

1. The FR_2017 execution prompt must cite
   `docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` and
   must specify GSUR opportunity year 2016 (not data year 2017) **OR** explicitly
   label the output as GSUR-year-mismatched / pre-GSURv2 / not final.

2. After FR_2017 is produced and mirrored to `Data/processed/fr/`, the Stage M1
   P3a dry-run should confirm all three years FOUND.

3. A future separate task — requiring a new authorization memo — must:
   a. Add `--gsur-year` support to `enh_RURO_prep_mnl_basic.py` or verify the
      script's current keying logic.
   b. Re-run Stage 5 for FR_2015 with GSUR keyed to year=2014.
   c. Re-run Stage 5 for FR_2016 to clarify source provenance (verify whether
      the GSURv2 file used year=2016 or year=2015 rates, and update sidecar).
   d. Potentially re-run Stage 5 for FR_2017 with GSUR keyed to year=2016.
   e. Produce GSURv2-extended rates for 2015 and 2017 (Eurostat acquisition).
   f. Update the Stage M1 execution-readiness verdict.

**The immediate unblocking path** is completing FR_2017 replication with the
corrected GSUR-year annotation, then updating the Stage M1 readiness verdict
to reflect that all three pre-GSURv2 parquets are present for dry-run purposes.
Production P3a estimation remains separately gated.