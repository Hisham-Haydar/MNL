> Archived on 2026-05-26 as a documentation-only addendum (observes section-title divergence from a template; no edit required).
> Base report (kept active in Results/): `Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Stage M1 P3a GSURv2 Stacking Execution Report — Heading Addendum v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

---

## 1. Purpose

This document records a documentation-only correction addendum
covering the heading-template mismatch in
`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`.
It supplements the earlier subtitle year-label correction recorded in
`docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`.

No authorization scope, input requirements, output requirements,
validation requirements, halt conditions, data, parquets, sidecars,
or substantive text was changed. This document is documentation-only.

---

## 2. Heading-template mismatch

The original execution task specified an exact 27-heading template for
the execution report. The report as written
(`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`)
contains 27 numbered sections (§1–§27) but the heading titles deviate
from the originally requested template in several places.

**Actual headings in the report (§1–§27):**

| § | Actual heading title |
|---|----------------------|
| 1 | Execution verdict |
| 2 | Authorization reference |
| 3 | Input resolution and SHA verification |
| 4 | Provisional v1-fallback output archival |
| 5 | Step 1 — Year stacking |
| 6 | Step 2 — Cross-year identity validation |
| 7 | Step 3 — CPI/HICP harmonisation |
| 8 | Step 4 — Cluster-key annotation |
| 9 | Step 5 — V1–V9 validation battery |
| 10 | V1 detail — stacked-ID uniqueness |
| 11 | V2 detail — row-count agreement |
| 12 | V5 detail — CPI harmonisation check |
| 13 | V6 detail — cluster key and overlap counts |
| 14 | V9 detail — upstream ruro columns |
| 15 | GSURv2 vs v1-fallback GSUR means |
| 16 | V9 fix — m1_validate.py update |
| 17 | Output inventory |
| 18 | Preserved provisional outputs |
| 19 | Config handling |
| 20 | Sidecar metadata confirmation |
| 21 | Scripts run — summary |
| 22 | Manifests and run artifacts |
| 23 | What was not executed |
| 24 | M1-clean baseline status |
| 25 | Authorization status after this execution |
| 26 | Halt conditions status |
| 27 | Final statements |

The report does not exactly follow the originally requested
27-heading template. The count of headings (27) matches, but the
heading titles were written by the executing agent at the time of the
run and diverge from the originally requested template.

---

## 3. Why the mismatch is documentation-only

The heading titles are section labels in the execution report
document. They do not appear in any parquet, sidecar, config, or
validation manifest. They do not affect:

- The inputs resolved (six GSURv2 parquets, SHA-256 verified).
- The outputs produced (`fr_p3a_gsurv2_stacked_raw.parquet`,
  `fr_p3a_gsurv2_harmonised.parquet`, both sidecars).
- The V1–V9 validation results (all PASS).
- The `provisioning_label` (`gsurv2_opportunity_year_aligned`).
- The cluster key (`cluster_id = idorighh`, 9,657 unique clusters).
- The row counts (1,244,500 rows, 12,445 household-years).
- The CPI factors (φ₂₀₁₅=1.0031, φ₂₀₁₆=1.0000, φ₂₀₁₇=0.9886).
- The GSUR means (singles: 0.0938, couples_female: 0.0880,
  couples_male: 0.0945).
- The authorization status (stacking re-run: COMPLETE).
- The construction verdict
  (`docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md`:
  PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC CAVEATS).
- The baseline status (M1-clean 2016 remains the active JMP baseline).
- The not-authorized scope (pooled estimation not authorized; welfare
  not authorized).

The heading-title mismatch is a formatting issue in the report
document only. The mismatch does not require a re-run, a re-validation,
or any modification to data, scripts, configs, or authorization
documents. No re-run is required.

---

## 4. Required substance present in the report

All substantive content requirements specified in the original task
and in the authorization §14 (R1–R10) are present in the report. The
following topics are confirmed covered:

| Topic | Authorization requirement | Where in report |
|-------|--------------------------|-----------------|
| Authorization scope | R2, §14 | §2 |
| Input resolution and SHA verification | R1, §14 | §3 |
| Provisional v1-fallback output archival | R2, §14 | §4 |
| Year stacking (Step 1) | R3, §14 | §5, §11 |
| Cross-year identity validation (Step 2) | R4, §14 | §6 |
| CPI/HICP harmonisation (Step 3) | R5, §14 | §7, §12 |
| Cluster-key annotation (Step 4) | R6, §14 | §8, §13 |
| V1–V9 validation battery (Step 5) | R4, §14 | §9 |
| V1 stacked-ID uniqueness detail | R4 | §10 |
| V2 row-count agreement detail | R3 | §11 |
| V5 CPI harmonisation check detail | R5 | §12 |
| V6 cluster key and overlap counts detail | R6 | §13 |
| V9 upstream ruro columns detail | R4 | §14 |
| GSUR means (GSURv2 vs v1-fallback) | R7, §14 | §15 |
| V9 validation-script patch record | R4 | §16 |
| Output inventory | R8, §14 | §17 |
| Preserved provisional outputs | R2, §14 | §18 |
| Config handling | R1, §14 | §19 |
| Sidecar metadata confirmation | R8, §14 | §20 |
| Scripts run — summary | R3, §14 | §21 |
| Manifests and run artifacts | R8, §14 | §22 |
| What was not executed | R10, §14 | §23 |
| M1-clean baseline status | R10, §14 | §24 |
| Authorization status after execution | R9, R10, §14 | §25 |
| Halt conditions status | R9, §13 | §26 |
| Final statements | R10, §14 | §27 |

Every substantive topic required by the authorization — authorization
scope, input resolution, provisional output archival, year stacking,
cross-year identity validation, CPI/HICP harmonisation, cluster-key
annotation, V1–V9 validation, output inventory, sidecar metadata,
GSUR means comparison, what was not executed, halt condition status,
and final authorization status — is present and correctly recorded in
the report body.

---

## 5. Relationship to the subtitle year-label correction

The subtitle year-label correction
(`docs/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_correction_v1.md`)
records a separate documentation issue: the report subtitle reads
"France 2014–2015–2016" while the correct description is survey years
FR_2015, FR_2016, FR_2017 with opportunity years y2014, y2015, y2016.

The heading-template mismatch and the subtitle year-label issue are
two distinct, independent documentation observations about the
execution report:

- The subtitle issue concerns the metadata line in the report header
  (the "France 2014–2015–2016" label).
- The heading-template mismatch concerns the section titles (§1–§27)
  diverging from the originally requested template.

Neither issue affects the other. Both are documentation-only. Both
are on the same report
(`Results/JMP_stage_M1_P3a_GSURv2_stacking_execution_report_v1.md`).
Neither requires a re-run. Neither affects data, parquets, sidecars,
validation results, authorization status, or baseline status.

The construction verdict
(`docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md`) already
classified the subtitle year-label issue as caveat C1. The
heading-template mismatch is an additional documentation observation
that does not rise to the level of a C-series caveat in the
construction verdict, because the section count (27) is correct and
all required substance is present.

---

## 6. Data and validation impact

No data impact. No validation impact.

| Item | Impact |
|------|--------|
| Input parquets | None — not modified |
| Output parquets (stacked_raw, harmonised) | None — not modified |
| Sidecar JSON files | None — not modified |
| V1–V9 results | None — all PASS, unchanged |
| Construction verdict | None — PASS WITH MINOR DOCUMENTATION AND VALIDATION-SPEC CAVEATS, unchanged |
| Authorization status | None — stacking re-run remains COMPLETE |
| Baseline status | None — M1-clean 2016 remains the active JMP baseline |
| Pooled estimation authorization | None — pooled estimation remains NOT authorized |
| Welfare authorization | None — welfare remains NOT authorized |

No parquet was rewritten. No sidecar was modified. No script was
re-run. No re-validation is required.

---

## 7. Final status

**The Stage M1 P3a GSURv2 stacking re-run construction verdict remains
fully in effect.**

The heading-template mismatch is documentation-only. The execution
report body, the parquets, the sidecars, the validation results, and
the authorization status are all correct and unchanged.

The GSURv2 P3a pooled dataset is valid as the final non-provisional
construction input for pooled-estimation design and Gate-A validation,
as stated in `docs/JMP_stage_M1_P3a_GSURv2_construction_verdict_v1.md`.

**Pooled estimation is NOT authorized.** Separately gated.

**Welfare computation is NOT authorized.** Separately gated.

**M1-clean 2016 remains the active JMP baseline.** Displaced only by
a future SA2 verdict explicitly promoting a final pooled specification.