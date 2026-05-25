# Stage A MNL Rebuild Prompt — Corrected v2

For use with Claude Code Sonnet against the local RURO/MNL codebase.
v2 corrections (relative to v1):
- **M4 rewritten** as a hard pass/fail check against the validated
  Stage A lookup (not against v1 legacy values).
- New **M4-diag** records the expected difference between new `gsur`
  and `gsur_legacy_misaligned` as a separate diagnostic, not as M4.
- **M11-diag rewritten** with separate grouping rules: singles use
  `drgn1 × dgn × educ3`; couples use partner-specific
  `drgn1 × educ3_male` (male) and `drgn1 × educ3_female` (female).
- **M12-diag rewritten** to use `idhh` only, with partner-specific
  constancy rules for couples. No assumption of `person_id` column.

All other content (singles merge procedure, couples merge procedure,
age-65 override, audit-trail preservation, prohibitions on promotion
and estimation) is unchanged from the v1 corrected prompt.

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
- Results/P3a/gsurv2/RURO_GSUR_v2_stageA_lookup_validation_report_v1.md
- docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md §8 (output schema),
  §9 (Stage A), §12 (F6 versioned paths, F6-promote canonical
  promotion — NOT authorized in this task), §14 (M1–M10 validation
  checks), §16 (what must not be changed)
- docs/RURO_GSUR_v2_1_open_decisions_resolution_v1.md

Task:
Rebuild versioned France 2016 continuous RURO MNL parquets using the
Stage A broad-age GSUR lookup. Write only to versioned GSURv2 paths.
Run all M1–M10 validation checks from v2.1 §14 plus diagnostic
M4-diag, M11-diag, M12-diag. Produce the rebuild validation report.

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
- Results/P3a/gsurv2/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md

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

Validation report — apply v2.1 §14 checks M1–M10 plus diagnostics:

The report must run and document each of these checks explicitly,
in this order. Use the exact M-numbering from v2.1 §14 for the hard
pass/fail gates. Diagnostics are numbered M4-diag, M11-diag,
M12-diag.

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

**M4 — Île-de-France parity (lookup propagation, hard pass/fail).**

This check confirms that the **rebuilt `gsur` column in the versioned
parquet equals the validated Stage A lookup value** for Île-de-France
households (drgn1 = 1). It verifies the merge propagated the lookup
values correctly into the parquet; it does NOT compare against v1
legacy values.

Procedure:
  1. For each Île-de-France row (`drgn1 == 1`) in the versioned
     singles parquet, look up the expected `gsur` value from
     `FR_gsur_ruro_v2_stageA.parquet` keyed on `(drgn1, educ3, sex)`.
     There are 6 distinct lookup values for drgn1=1 (3 educ3 ×
     2 sex).
  2. Compute the absolute difference between the parquet's
     `gsur` value and the expected lookup value, per row.
  3. PASS criterion: `max(|gsur_parquet - gsur_lookup_expected|)`
     across all drgn1=1 rows ≤ **0.001** (per O8 resolution).
  4. Report the per-(educ3, sex) cell parquet value, expected
     value, and difference.

For couples:
  1. For each drgn1=1 row, compute the same check for `gsur_male`
     against the lookup keyed on `(1, educ3_male, 'M')`, and for
     `gsur_female` against `(1, educ3_female, 'F')`.
  2. PASS criterion: max absolute difference ≤ 0.001 across all
     drgn1=1 rows and both partners.

This is a hard pass/fail check. The Stage A lookup has already been
validated against the source workbook (per the lookup validation
report §10). M4 here verifies the rebuild propagated those validated
values correctly. There is no expected stratification difference at
this stage; we are comparing the parquet against the lookup it was
built from.

**M4-diag — Old vs corrected GSUR comparison (diagnostic, not
pass/fail).**

This is a separate diagnostic, **not** part of M4. Its purpose is
to document the expected magnitude of the v1→v2 correction.

Procedure:
  1. For all rows in the versioned singles parquet, compute
     `gsur - gsur_legacy_misaligned` per row.
  2. Report summary statistics by drgn1: mean absolute difference,
     max absolute difference, count of rows.
  3. For drgn1 = 1 specifically: the v2 `gsur` is stratified by
     educ3 and sex; the v1 `gsur_legacy_misaligned` was not. Large
     per-cell differences (up to several percentage points) are
     **expected and correct** — they reflect the education and sex
     stratification that v1 lacked. This is a feature of the
     correction, not a bug.
  4. The mean absolute difference should be in the same magnitude
     as the lookup validation report §9 (~3.6 ppt). The max should
     be in the same magnitude as the lookup validation report §9
     (~8.1 ppt).

This diagnostic confirms that the audit trail captures the full
v1→v2 change. It does not gate the rebuild.

For couples: same procedure on `gsur_male - gsur_male_legacy_
misaligned` and `gsur_female - gsur_female_legacy_misaligned`.

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

Additional diagnostic content for the report (M11-diag, M12-diag —
optional but recommended; not pass/fail):

**M11-diag — GSUR value distribution by demographic cell
(diagnostic).** Summary statistics of `gsur` and
`gsur_legacy_misaligned`, with different grouping rules for singles
and couples:

For singles parquet:
  - Group by: `drgn1 × dgn × educ3` (the singles parquet has `dgn`
    indicating sex, where 1 = male, 0 = female per project convention)
  - Report per group: count, mean(`gsur`), mean(`gsur_legacy_
    misaligned`), mean diff, max abs diff
  - Use `dgn` as it appears in the parquet (do not invent a `sex`
    column for singles if `dgn` is the actual column name)

For couples parquet — male partner:
  - Group by: `drgn1 × educ3_male`
  - Report per group: count, mean(`gsur_male`), mean(`gsur_male_
    legacy_misaligned`), mean diff, max abs diff
  - Do not use a single `dgn` column; the couples parquet has
    partner-specific columns, not a single sex indicator

For couples parquet — female partner:
  - Group by: `drgn1 × educ3_female`
  - Report per group: count, mean(`gsur_female`), mean(`gsur_female_
    legacy_misaligned`), mean diff, max abs diff

Expected pattern across all three groupings: legacy values are
unstratified, new values are stratified. Low-education cells should
show substantially higher v2 `gsur` than legacy; high-education cells
substantially lower. If the pattern is inverted or absent, the merge
has a bug.

**M12-diag — Household-level constancy check (diagnostic).**

Within each household, `gsur` should be constant across all
alternative rows for the same household. This catches the merge bug
where GSUR is incorrectly varied at the alternative level.

For singles parquet:
  - Group by `idhh` only.
  - Within each `idhh`, confirm `gsur` is constant across all rows
    (i.e., `gsur.nunique() == 1`).
  - Report: count of households where `gsur.nunique() > 1`. Expected
    value: 0.
  - Also confirm `gsur_legacy_misaligned`, `gsur_weighting_source`,
    `gsur_age_band_used` are each constant within `idhh`.

For couples parquet:
  - Group by `idhh` only.
  - Within each `idhh`, confirm `gsur_male` is constant across all
    rows, AND `gsur_female` is constant across all rows. (Each
    partner's value is constant within the household; male and female
    can differ from each other.)
  - Report: count of households where either `gsur_male.nunique()
    > 1` or `gsur_female.nunique() > 1`. Expected value: 0.
  - Also confirm `gsur_male_legacy_misaligned`, `gsur_female_legacy_
    misaligned`, `gsur_male_weighting_source`, `gsur_female_
    weighting_source`, `gsur_male_age_band_used`, `gsur_female_age_
    band_used` are each constant within `idhh`.

Do not assume a `person_id` column exists. Use `idhh` only as the
grouping key. If `idhh` does not exist in either parquet, identify
the actual household-level identifier from the existing schema (it
may be `idhh`, `hh_id`, `household_id`, or similar) and use that.

If `gsur` varies within `idhh` for any household, the merge has a
bug. Stop and report the failure.

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

The rebuild is **ready for Stage A re-estimation** if and only if all
of the following hard pass/fail checks PASS:
- M1 PASS (value-identical non-GSUR columns)
- M2 PASS (schema correct)
- M3 PASS (no NaN in `gsur` for the metropolitan sample)
- M4 PASS (drgn1=1 parquet values within 0.001 of validated lookup
  values — this is the hard propagation gate)
- M5 PASS (age-band assignment correct, including age-65 override)
- M6 documented (fraction of identical male/female values is non-100%
  — informational, not pass/fail)
- M7 PASS (row counts preserved)
- M8 PASS (forensic record preserved)
- M9 PASS (parquets loadable by engine)
- M10 PASS (canonical files untouched)

Diagnostics (informational, not pass/fail):
- M4-diag documented (large v1→v2 differences expected, especially
  for low-education and high-education cells)
- M11-diag documented (stratification pattern visible across
  groupings)
- M12-diag PASS (zero households where `gsur` varies within `idhh`
  — this IS a hard check despite being diagnostic-labeled, because
  variation within household would indicate a merge bug)

If any of M1, M2, M3, M4, M5, M7, M8, M9, M10, M12-diag FAILS, the
rebuild is NOT ready for re-estimation. Stop and flag the failure in
the report.

---

Deliverable:

Save the rebuild validation report to:
Results/P3a/gsurv2/RURO_GSUR_v2_stageA_MNL_rebuild_report_v1.md

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
7. M4-diag, M11-diag, M12-diag findings
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

## Summary of changes from v1 corrected prompt

| Check | v1 wording | v2 wording |
|---|---|---|
| M4 | Compared rebuilt `gsur` to `gsur_legacy_misaligned`, called large differences "expected"; flagged as diagnostic hybrid | Hard pass/fail check: rebuilt `gsur` for drgn1=1 within 0.001 of validated Stage A lookup value |
| M4-diag (NEW) | did not exist | Separate diagnostic for v1→v2 magnitudes, documents expected stratification differences |
| M11-diag (singles) | `drgn1 × dgn × educ3` | `drgn1 × dgn × educ3` (unchanged — was correct for singles) |
| M11-diag (couples) | Force `drgn1 × dgn × educ3` onto couples (would fail) | Separate male and female groupings: `drgn1 × educ3_male` and `drgn1 × educ3_female` |
| M12-diag (singles) | Group by `(idhh, person_id, sex, educ3, drgn1)` | Group by `idhh` only; check `gsur` constant within household |
| M12-diag (couples) | Same over-specified key | Group by `idhh` only; check `gsur_male` and `gsur_female` each constant within household |
| M12-diag fallback | Did not address missing `idhh` | Explicit instruction to identify actual household identifier from schema if `idhh` doesn't exist |
| Final pass/fail criterion | Listed M-criteria with M4 ambiguous | M4 is now a hard pass/fail with explicit 0.001 tolerance; M12-diag is a hard check despite diagnostic label |

The substantive merge procedure, audit-trail preservation, age-65
override, couples partner-specific joins, and the prohibitions on
canonical promotion / estimation / Stage B activation are unchanged
from v1. All other improvements from v1 are preserved.
