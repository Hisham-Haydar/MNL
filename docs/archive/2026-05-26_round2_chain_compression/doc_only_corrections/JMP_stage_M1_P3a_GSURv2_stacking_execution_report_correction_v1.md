> Archived on 2026-05-26 as a documentation-only correction (the correction itself states "no edit to the report or any other file is required").
> Base report (kept active in Results/): `Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Stage M1 P3a GSURv2 Stacking Execution Report — Correction v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This document records a narrow documentation-only issue identified in
`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md` after
execution. No authorization scope, input requirements, output
requirements, validation requirements, halt conditions, data, parquets,
sidecars, or substantive text was changed.

| # | Issue | Action |
|---|-------|--------|
| C1 | The execution report's subtitle metadata line reads "France 2014–2015–2016", which could be read as implying that FR_2014 is a survey year in the dataset | Recorded here as documentation-only; no edit to the report or any other file is required |

---

## 2. Report-heading issue

The execution report
`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`
carries the following header line:

```
*France 2014–2015–2016 | v1 | 2026-05-21*
```

The three survey years covered by the Stage M1 P3a GSURv2 pooled dataset
are **FR_2015, FR_2016, and FR_2017**. The three opportunity years are
**y2014, y2015, and y2016** (the EUROMOD system year, which lags the
survey year by one). The "2014" in the subtitle refers to the y2014
opportunity year for the FR_2015 survey year, not to a FR_2014 survey
year.

**Before (report subtitle line 3):**

```
*France 2014–2015–2016 | v1 | 2026-05-21*
```

**Correct description:**

The dataset covers survey years FR_2015, FR_2016, and FR_2017, with
opportunity years y2014 (for FR_2015), y2015 (for FR_2016), and y2016
(for FR_2017). The subtitle "2014–2015–2016" reflects the opportunity
years rather than the survey years.

The report body correctly identifies the survey years, opportunity years,
input stems, and year-tag mapping throughout. The issue is confined to
the subtitle metadata line only.

---

## 3. Why the issue is documentation-only

The subtitle metadata line is a formatting label. The following are
confirmed unaffected:

- The six GSURv2 input parquets and their SHA-256 hashes (§3 of the
  report).
- The input stems: `fr_2015_RURO_mnl_GSURv2_y2014__`,
  `fr_2016_RURO_mnl_GSURv2_y2015__`, `fr_2017_RURO_mnl_GSURv2_y2016__`.
- The stacked-raw parquet:
  `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet`.
- The harmonised parquet:
  `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`.
- Both Stage M1 metadata sidecars and their `provisioning_label`,
  `gsur_alignment_per_year`, and `survey_year_opportunity_year_mapping`
  fields.
- The V1–V9 validation results (all PASS).
- The row count (1,244,500), household-year count (12,445), and unique
  cluster count (9,657).
- The year-tag mapping (2015→tag 1, 2016→tag 2, 2017→tag 3) and the UID
  scheme.
- The CPI factors (φ₂₀₁₅=1.0031, φ₂₀₁₆=1.0000, φ₂₀₁₇=0.9886).
- The cluster key (`cluster_id = idorighh`).
- The authorization reference and authorization scope.
- The baseline status (M1-clean 2016 remains the active JMP baseline).
- The not-authorized scope (pooled estimation not authorized; welfare
  not authorized).

No data was modified. No parquet was rewritten. No script was re-run.
No sidecar was modified.

---

## 4. Correct construction status

The correct description of the Stage M1 P3a GSURv2 construction is:

**Survey years:** FR_2015, FR_2016, FR_2017.

**Opportunity years:** y2014 (for FR_2015), y2015 (for FR_2016), y2016
(for FR_2017).

**Input stems:**
- `fr_2015_RURO_mnl_GSURv2_y2014__singles.parquet`
- `fr_2015_RURO_mnl_GSURv2_y2014__couples.parquet`
- `fr_2016_RURO_mnl_GSURv2_y2015__singles.parquet`
- `fr_2016_RURO_mnl_GSURv2_y2015__couples.parquet`
- `fr_2017_RURO_mnl_GSURv2_y2016__singles.parquet`
- `fr_2017_RURO_mnl_GSURv2_y2016__couples.parquet`

**Output files:**
- `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`

**Construction verdict:** PASS WITH MINOR DOCUMENTATION AND
VALIDATION-SPEC CAVEATS (per
`docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md`).

---

## 5. Data and validation impact

No data impact. No validation impact.

| Item | Impact |
|------|--------|
| Input parquets | None — not modified |
| Output parquets (stacked_raw, harmonised) | None — not modified |
| Sidecar JSON files | None — not modified; survey/opportunity years correctly recorded |
| V1–V9 results | None — all PASS, unchanged |
| Authorization status | None — stacking re-run remains authorized and complete |
| Baseline status | None — M1-clean 2016 remains the active JMP baseline |
| Pooled estimation authorization | None — pooled estimation remains NOT authorized |

---

## 6. Files not changed

The following are confirmed unchanged by this correction record:

- `Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`
  (the report is not edited; this note accompanies it)
- `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw.parquet`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised.parquet`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_stacked_raw__stage_m1_meta.json`
- `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised__stage_m1_meta.json`
- `config/multi_year/fr_p3a_gsurv2_stage_m1.yaml`
- `scripts/multi_year/m1_validate.py` (V9 patch was committed in the
  execution run; no further change)
- `docs/JMP_stage_M1_P3a_GSURv2_stacking_authorization_v1.md`
- `docs/RURO_occ_M1_clean_verdict_v1.md`

No data was modified. No script was re-run. No parquet was written.

---

## 7. Final status

**The Stage M1 P3a GSURv2 stacking re-run construction verdict remains
fully in effect.**

The subtitle heading issue is documentation-only. The execution report
body, the parquets, the sidecars, the validation results, and the
authorization status are all correct and unchanged.

The GSURv2 P3a pooled dataset is valid as the final non-provisional
construction input for pooled-estimation design and Gate-A validation,
as stated in `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md`.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.**