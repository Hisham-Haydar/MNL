# Stage A MNL Rebuild Prompt — Corrected

For use with Claude Code Sonnet against the local RURO/MNL codebase.
Corrections applied to the original prompt:
1. Explicit instruction to read v1 `gsur` from canonical parquet
   into `gsur_legacy_misaligned`.
2. Discard the reconstructed `gsur_legacy_misaligned` from the lookup.
3. Explicit couples merge specification (twice per couple).
4. Age-65 `gsur_age_band_used` override.
5. v2.1 §14 validation gates M1–M10 cited explicitly.
6. Extended reading list including the O7 sign-off request and
   Stage A authorization memos.

---

```text
Work locally in my RURO/MNL codebase.

This task is the Stage A MNL rebuild that writes the versioned GSURv2
parquets using the corrected GSUR lookup. It is the implementation step
authorized by docs/RURO_GSUR_StageA_authorization_v1.md and gated by
the O7 crosswalk sign-off in docs/RURO_GSUR_O7_crosswalk_signoff_v1.md.

Read (in this order):
- docs/RURO_GSUR_StageA_authorization_v1.md
- docs/RURO_GSUR_O7_crosswalk_signoff_v1.md
- docs/RURO_GSUR_O7_crosswalk_signoff_request_v1.md (especially §6, §8)
- docs/RURO_GSUR_v2_stageA_implementation_report_v1.md (especially the
  corrected §8 merge procedure — note that §8 explicitly supersedes the
  earlier incorrect description in the same section)
- Results/RURO_GSUR_v2_stageA_lookup_validation_report_v1.md
- docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md §8 (output schema),
  §9 (Stage A), §12 (F6 versioned paths, F6-promote canonical
  promotion - NOT authorized in this task), §14 (M1–M10 validation
  checks), §16 (what must not be changed)
- docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md

Task:
Rebuild versioned France 2016 continuous RURO MNL parquets using the
Stage A broad-age GSUR lookup. Write only to versioned GSURv2 paths.
Run all M1–M10 validation checks from v2.1 §14. Produce the rebuild
validation report.

---

Inputs to use:
- Canonical MNL parquets (read-only, NOT to be overwritten):
  Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet
  Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet
- Stage A lookup (read-only):
  Data/external/FR_gsur_ruro_v2_stageA.parquet
- Crosswalk file (already consumed at lookup-build time; do not
  re-apply):
  Data/external/fr_drgn1_to_nuts2_crosswalk.csv

Outputs to write:
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet
- Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__couples.parquet
- Results/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md

---

Merge procedure (singles):

1. Read the canonical singles parquet at
   fr_2016_RURO_mnl__singles.parquet. This is the source of truth for
   all non-GSUR columns and for the v1 `gsur` audit-trail value.

2. **Capture the v1 `gsur` column before any modification.** Rename
   the canonical `gsur` column to `gsur_legacy_misaligned`. This is
   the actual v1 value that becomes the audit-trail record. Do NOT
   bring the `gsur_legacy_misaligned` column from
   `FR_gsur_ruro_v2_stageA.parquet` — the value there is a
   reconstruction from FR_gsur.xlsx Sheet 5 and is not the actual
   v1 parquet value. Drop that column from the lookup before merging.

3. Join the lookup `FR_gsur_ruro_v2_stageA.parquet` to the singles
   parquet on the key (drgn1, educ3, sex).
   - lookup columns to bring in: gsur, weighting_source,
     gsur_age_band_used, denom_flag, gsur_unreliable, n_components
   - rename `weighting_source` to `gsur_weighting_source` per v2.1
     §8.1 schema if not already named that way

4. **Apply the O3 age-65 override.** For every singles row with
   `dag == 65`, overwrite `gsur_age_band_used` with the string
   `"Y20-64_fallback_age65"`. Other columns (gsur,
   gsur_weighting_source, etc.) are unchanged for age-65 rows
   because the Stage A lookup uses Y20-64 for all drgn1=1..8 rows
   anyway.

5. For any singles row with `drgn1 == 9`, all GSUR columns
   (`gsur`, `gsur_weighting_source`, `gsur_age_band_used`,
   `gsur_legacy_misaligned`, etc.) become NaN per O5 resolution.
   In the France 2016 metropolitan sample this should be zero rows.

6. Write the result to
   fr_2016_RURO_mnl_GSURv2__singles.parquet at the versioned path
   above. Do NOT overwrite the canonical path.

Merge procedure (couples):

The couples merge is applied **twice per couple**, once per partner:

1. Read the canonical couples parquet
   (fr_2016_RURO_mnl__couples.parquet).

2. **Capture v1 audit-trail values.** Rename the canonical
   `gsur_male` column to `gsur_male_legacy_misaligned`, and rename
   `gsur_female` to `gsur_female_legacy_misaligned`. Discard the
   `gsur_legacy_misaligned` column from the lookup (reconstructed
   value, not the actual v1 audit trail).

3. **Male partner merge**: Join the lookup
   `FR_gsur_ruro_v2_stageA.parquet` on the key
   `(drgn1, educ3_male, sex=='M')`. The result column names get
   `_male` suffix:
   - `gsur` → `gsur_male`
   - `gsur_weighting_source` → `gsur_male_weighting_source`
   - `gsur_age_band_used` → `gsur_male_age_band_used`
   - similarly for `denom_flag`, `gsur_unreliable`, `n_components`

4. **Female partner merge**: Same as step 3 but on the key
   `(drgn1, educ3_female, sex=='F')`. Result columns get `_female`
   suffix.

5. **Apply the O3 age-65 override per partner.** For rows with
   `dag_male == 65`, set `gsur_male_age_band_used` to
   `"Y20-64_fallback_age65"`. Same for `dag_female == 65` and
   `gsur_female_age_band_used`. (The expectation is zero couples
   rows with either partner at age 65, but the override must be
   coded correctly regardless.)

6. For any row with `drgn1 == 9`, all GSUR columns for both
   partners become NaN (zero rows expected).

7. Write the result to
   fr_2016_RURO_mnl_GSURv2__couples.parquet at the versioned path.
   Do NOT overwrite the canonical path.

---

Validation report — apply v2.1 §14 checks M1–M10:

The report must run and document each of these checks explicitly,
in this order. Use the exact M-numbering from v2.1 §14.

**M1 — Value-identical non-GSUR columns under schema-aligned
comparison.** Every non-GSUR column in the GSURv2 parquets has values
identical to the v1 canonical parquets at the same row position when
compared via column-wise pandas comparison (NOT file-byte hashing,
which is wrong per v2.1 §14 M1). Use `pandas.testing.assert_series_equal`
or `DataFrame.equals` with appropriate dtype handling, or per-column
boolean comparison with NaN-safe equality. Report PASS for every
non-GSUR column.

The non-GSUR columns to check are all columns except:
  - For singles: `gsur`, and any newly added GSUR-related columns
    (`gsur_weighting_source`, `gsur_age_band_used`,
    `gsur_legacy_misaligned`, `denom_flag`, `gsur_unreliable`,
    `n_components`).
  - For couples: similarly, all `gsur_*` columns and their `_male`/
    `_female` suffixed variants.

**M2 — GSUR column schema.** All columns listed in v2.1 §8.1 (singles)
and §8.2 (couples) are present in the versioned parquets. Report
column names found vs expected.

Note: Stage A is broad-age only; do NOT compute `gsur_age`,
`gsur_y15_24`, `gsur_y25_34`, `gsur_y35_44`, `gsur_y45_54`,
`gsur_y55_64`. Those are Stage B columns. The Stage A schema may
omit them entirely or include them with NaN values; if included,
mark them as "Stage B placeholder, NaN" in the report.

**M3 — No missing values in `gsur`.** Confirm `gsur` (or
`gsur_male` / `gsur_female`) has no NaN values for any household in
the sample. Age-65 households should have `gsur` non-NaN (they get
the Y20-64 broad value); only the `gsur_age_band_used` label
differs.

**M4 — Île-de-France parity.** For all households with `drgn1 == 1`,
compute the absolute difference between `gsur` (new Stage A value)
and `gsur_legacy_misaligned` (v1 audit-trail value, the actual
canonical `gsur` value before rebuild). Per O8 resolution the
tolerance is 0.001 absolute.

Important caveat: M4 expects `gsur_legacy_misaligned` to be the v1
parquet's `gsur` column. The v1 `gsur` was a TOTAL-sex / TOTAL-educ3
collapsed value, while the new `gsur` is education- and sex-
stratified. **Substantial differences between the two are expected**,
not failures. M4 PASS criterion in v2.1 §14 is for Île-de-France
specifically because it's the only unambiguous region (one NUTS-2
component, FR10). Even there, the new gsur is stratified by educ3 and
sex while the v1 was not, so M4 should be interpreted as a
**diagnostic check**, not a hard pass/fail.

Report: per drgn1=1 row, the absolute difference and whether it
exceeds 0.001. Document the expected stratification difference. If
the report shows large differences for Île-de-France, this is the
expected stratification effect, not a failure.

**M5 — Age-band assignment.** For each singles row, verify
`gsur_age_band_used` matches `"Y20-64"` for ages 16-64 and
`"Y20-64_fallback_age65"` for `dag == 65`. Report the cross-tab of
(`dag`, `gsur_age_band_used`).

For couples, the analogous check on `gsur_male_age_band_used` and
`gsur_female_age_band_used`.

**M6 — Partner-specific consistency in couples.** Per v2.1 audit, only
~15% of couples have identical male/female GSUR values (driven mostly
by sex-difference in unemployment rates across cells). Report the
fraction of couples rows where `gsur_male == gsur_female`. The
expected fraction is around 15% but the criterion is just that they
are not all identical (i.e., the merge correctly applied two
independent joins).

**M7 — Row count preservation.** Row counts in versioned parquets
match v1 canonical parquets exactly:
  - Singles: 167,600 rows / 1,676 households (per audit)
  - Couples: 257,700 rows / 2,577 households (per audit)
No row multiplication from the merge, no row loss.

**M8 — Forensic record preservation.** `gsur_legacy_misaligned` (or
`gsur_male_legacy_misaligned` and `gsur_female_legacy_misaligned` in
couples) equals the v1 `gsur` values under value-identical
column-wise comparison. This is the key check that the audit trail
to v1 is preserved.

**M9 — Cross-stage compatibility.** The versioned parquets are
readable by the existing engine (`scripts/enhanced/gamspy_estimation_
vectorized.py`) and post-estimator (`scripts/enhanced/RURO_post_
estimation_styled.py`) without code changes. Specifically: the `gsur`
column is found by name and used by the engine without error.
Do NOT run estimation; just confirm the parquet is structurally
loadable and that `gsur` is accessible as a numeric column. A
simple `pd.read_parquet(path)` followed by `df['gsur'].dtype` check
suffices.

**M10 — Versioned path location.** Explicitly confirm:
  - The versioned files exist at the versioned paths.
  - The canonical files at fr_2016_RURO_mnl__singles.parquet and
    fr_2016_RURO_mnl__couples.parquet have NOT been modified.
  - Compare canonical file modification timestamps before and after
    the task: they must be unchanged.

---

Additional diagnostic content for the report (M11-M12 from v2.1
§14.2, optional but recommended):

**M11-diag — GSUR value distribution comparison.** Summary statistics
(min, mean, median, max, p25, p75) of `gsur` and
`gsur_legacy_misaligned` by drgn1 × dgn × educ3. Document the
expected pattern: legacy values are unstratified, new values are
stratified, so large per-cell differences are expected and represent
the correction. Compare to the validation report's existing legacy
comparison (§9 of the lookup validation report).

**M12-diag — Household-level constancy check.** Within each
household (identified by `idhh` or equivalent), `gsur` should be
constant across all alternative rows for the same individual. (It's
a person-level covariate, not an alternative-level covariate.)
Specifically: per (idhh, person_id, sex, educ3, drgn1) group, the
`gsur` should be identical across all alternative rows. Verify this
holds.

Note: this is an MNL-structure property (the GSUR is a household-
person-level invariant across alternatives) not strictly a v2.1 §14
check, but it's a useful sanity check that the merge applied
correctly at the household level. If `gsur` varies within a
household, the merge has a bug.

---

What this task does NOT do:

- Does NOT overwrite canonical MNL parquets (M10 enforces this).
- Does NOT activate age-specific `gsur_age` or any narrow age-band
  column. Stage B is deferred per v2.1 §10 and O6 resolution.
- Does NOT run any RURO estimation. Stage A re-estimation is the
  next task (separate prompt).
- Does NOT modify the engine, post-estimator, parser, or any YAML
  spec. v2.1 §16 N1-N12 enforces this.
- Does NOT approve canonical promotion (F6-promote in v2.1 §12).
  Promotion requires Stage A verdict (SA-STANDS or SA-REVISION) and
  separate explicit user approval per O10. This task is versioned-
  parquet-write only.
- Does NOT run welfare computation.

---

Final pass/fail criterion for the rebuild report:

The rebuild is **ready for Stage A re-estimation** if and only if:
- M1 PASS (value-identical non-GSUR columns)
- M2 PASS (schema correct)
- M3 PASS (no NaN in `gsur` for the metropolitan sample)
- M4 documented (large stratification differences expected; not a
  hard fail)
- M5 PASS (age-band assignment correct, including age-65 override)
- M6 documented (fraction of identical male/female values is non-100%)
- M7 PASS (row counts preserved)
- M8 PASS (forensic record preserved)
- M9 PASS (parquets loadable by engine)
- M10 PASS (canonical files untouched)
- M11-diag and M12-diag documented

If any of M1, M2, M3, M5, M7, M8, M9, M10 FAILS, the rebuild is NOT
ready for re-estimation. Stop and flag the failure in the report.

---

Deliverable:

Save the rebuild validation report to:
Results/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md

The report must contain:
1. Commands run (the actual Python commands or script reference)
2. Input MNL files (paths, sizes, row counts, household counts,
   modification timestamps before the task)
3. Output versioned MNL files (paths, sizes, row counts, household
   counts, modification timestamps after the task)
4. Modification timestamps of canonical files before and after the
   task (M10 check)
5. The lookup file used and its row count
6. Each M1-M10 check result with explicit PASS/FAIL/DOCUMENTED label
7. M11-diag and M12-diag findings
8. Cross-tabs and summary statistics referenced in the checks
9. Final pass/fail verdict for re-estimation readiness
10. Recommended next action: proceed to Stage A re-estimation (only
    if all hard checks PASS), or stop and diagnose (if any hard
    check fails)

Do NOT estimate.
Do NOT promote to canonical paths.
Do NOT run welfare computation.
Stop after the report is written.
```

---

## Notes on what this prompt does that the original did not

| Issue | Original prompt | Corrected prompt |
|---|---|---|
| `gsur_legacy_misaligned` source | "keep it" (ambiguous) | Read v1 `gsur` from canonical parquet into `gsur_legacy_misaligned`; discard reconstructed value from lookup |
| Couples merge | "checks if relevant" | Twice per couple: male on (drgn1, educ3_male, 'M'); female on (drgn1, educ3_female, 'F') |
| Age-65 override | Not mentioned | Set `gsur_age_band_used` to `"Y20-64_fallback_age65"` for `dag == 65` rows |
| Validation rigor | "PASS/FAIL for re-estimation readiness" | Explicit M1-M10 from v2.1 §14, with the M1 "value-identical, not byte-equivalent" rule called out |
| What's NOT authorized | Not estimate, not welfare | Adds: not promote, not modify code/specs, not activate Stage B |
| Couples partner-specific check | Not mentioned | M6 verifies the ~15% identical-rate property |
| Engine compatibility | Not mentioned | M9 confirms parquet loadable by engine without estimation |
| Canonical safety check | Implicit | M10 explicit: timestamp comparison before/after |
| Reading list | 4 files | 9 files including the authorization memo and the corrected-merge-procedure §8 of the implementation report |
