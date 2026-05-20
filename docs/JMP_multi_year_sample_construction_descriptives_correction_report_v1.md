# JMP Multi-Year Sample Construction — Correction Report v1

*France 2015–2016–2017 | v1 | 2026-05-20*

---

## 1. Correction verdict

Four corrections applied to `docs/JMP_multi_year_sample_construction_descriptives_report_v1.md`. No data were rebuilt, no tables regenerated, no figures changed. All corrections are textual; the underlying numbers remain unchanged.

| # | Issue | Location | Action |
|---|-------|----------|--------|
| C1 | Extra `##` heading demoted | Line 2 of original | Demoted to plain italic text |
| C2 | Education-filter described as missing-data quality filter | §§3, 4, 6, 12, 18 | Replaced with correct `dec == 0` / enrolment-status wording throughout |
| C3 | LES step described as head-only for couples | §3 couples branch step 5 | Corrected to "all deciders' (head and partner)" |
| C4 | Household drop at final step attributed to "budget-constraint inconsistency" | §6 | Replaced with code-verified description: wage-bounds filter on `wage_unbounded` |

---

## 2. Files inspected

| File | Purpose |
|------|---------|
| `docs/JMP_multi_year_sample_construction_descriptives_report_v1.md` | Report subject to correction |
| `scripts/enhanced/enh_france_data_prep.py` | Authoritative source for all cleaning rules; used to verify C2, C3, C4 |
| `Results/JMP_multi_year_cleaning_attrition_table_v1.csv` | Confirmed step labels and magnitudes; verified no numerical correction needed |
| `Results/JMP_multi_year_descriptive_stats_v1.csv` | Confirmed descriptive-statistics values; no correction needed |

Specific code locations verified:

| Issue | File location | Code |
|-------|--------------|------|
| Education filter | `enh_france_data_prep.py` line 781–786 | `edu_mask = (df_work["hh_IsHead"] == 1) & (df_work["dec"] == 0)` |
| Partner education filter | `enh_france_data_prep.py` line 844–847 | `partner_edu_mask = (df_work["hh_IsPartner"] == 1) & (df_work["dec"] == 0)` |
| LES filter (deciders) | `enh_france_data_prep.py` lines 804–828 | `decider_mask` covers both head and partner via `ruro_decider == 1` |
| Wage drop condition | `enh_france_data_prep.py` lines 956–967 | `wage_abnormal_mask` on `wage_unbounded` outside `wage_bounds` |
| Hours drop path | `enh_france_data_prep.py` lines 908–937 | `must_filter_out` requires LES ∉ {3,5,7} — empty post-step-4 |

---

## 3. Heading correction

**Problem:** The original file had 23 `##`-level headings: 22 numbered sections plus `## France 2015–2016–2017 | v1 | 2026-05-20` at line 2. The request specifies exactly 22 `##` headings.

**Fix:** Demoted the version/date line from a `##` heading to plain italic text immediately below the `#` title:

```
Before:
  # JMP Multi-Year Sample Construction and Descriptive Statistics Report
  ## France 2015–2016–2017 | v1 | 2026-05-20

After:
  # JMP Multi-Year Sample Construction and Descriptive Statistics Report

  *France 2015–2016–2017 | v1 | 2026-05-20*
```

The 22 numbered `##` headings (§§1–22) are preserved exactly as specified.

---

## 4. Education-filter wording correction

**Problem:** Five passages in the original report described the "Education (Head)" and "Education (Partner)" pipeline steps as filtering on missing or invalid education-attainment data. This is factually wrong. The code tests `dec == 0`, where `dec` is the EUROMOD variable for current enrolment in education (`dec == 1` = currently in education). The step excludes individuals who are currently students, not individuals with missing education records.

**Specific errors in original:**

| Location | Original (wrong) | Corrected |
|----------|-----------------|-----------|
| §3, couples step 3 | "Education: head education observed and non-missing" | "Not in education (Head): head not currently enrolled in education (`dec == 0`)" |
| §3, couples step 7 | "Education: partner education observed" | "Not in education (Partner): partner not currently enrolled in education (`dec == 0`)" |
| §3, singles step 3 | "Education: head education observed" | "Not in education (Head): head not currently enrolled in education (`dec == 0`)" |
| §4, table row | "Education observed" / "Households with missing education cannot be assigned predicted wages" | "Not currently in education (`dec == 0`)" / correct modelling-scope rationale |
| §6 | "**Education missing** — households where … education recorded as missing, implausible, or zero" | "**Currently in education (`dec == 1` excluded)** — households where … currently enrolled in education" |
| §12 | "Education is required to be observed and valid (non-missing, non-zero)" | "Not currently in education (`dec == 0`): … tests enrolment status, not whether education-attainment data are present or valid" |
| §18 | "Education missing (§12) \| Imputation rather than exclusion is feasible …" | "Currently-in-education exclusion (§12) \| No change. Correctly excluded …" |

**Verification:** `enh_france_data_prep.py` line 781 comment reads `# Step 2: Education (Head) - dec == 0 means not currently in education`. The filter mask is `(df_work["hh_IsHead"] == 1) & (df_work["dec"] == 0)`. The equivalent for the partner is at line 844–847.

---

## 5. LES wording correction

**Problem:** Section 3 (couples branch), step 5 read "Allowed LES: **head's** labour status in {3, 5, 7}". For couples, the filter applies to all RURO deciders simultaneously — both head and partner — not head-only.

**Code evidence** (`enh_france_data_prep.py` lines 804–828):

```python
# Step 4: Allowed LES (RURO deciders: Head + Partner)
#   This enforces that ALL deciders (head + partner) have les in allowed_les
if "ruro_decider" in df_work.columns:
    decider_mask = df_work["ruro_decider"].eq(1)   # covers both head and partner
else:
    decider_mask = df_work["hh_IsHead"].eq(1)
    if household_type == "couples" and "hh_IsPartner" in df_work.columns:
        decider_mask = decider_mask | df_work["hh_IsPartner"].eq(1)

bad_hh = df_work.loc[
    decider_mask & ~df_work[les_col].isin(config["allowed_les"]), "idhh"
].unique()
```

The step runs before the partner-specific age and education filters (steps 6–7), so both head and partner rows are present in `df_work` when this mask is applied. A household is dropped if **either** the head or the partner has LES ∉ {3, 5, 7}.

**Fix:** Changed §3 couples step 5 from "Allowed LES: head's labour status in {3, 5, 7}" to "Allowed LES: all deciders' (head and partner) labour status in {3, 5, 7}".

**Singles branch unaffected:** For singles, only the head is present as a decider, so "head's labour status" remains correct at singles step 5.

---

## 6. Wage and hours wording correction

**Problem:** Section 6 contained this sentence at the end of the hours-capping description:

> "Only households where the reclassification triggers a budget-constraint inconsistency are dropped."

This phrase is not supported by the code. The code does not test for budget-constraint inconsistency. The actual household-dropping logic in the final pipeline step is:

1. **`must_filter_out` path** (hours-driven): drops households where a decider has `lhw ≤ 5` (the inactive threshold) **and** their LES is not in {3, 5, 7}. Since step 4 (Allowed LES) has already restricted all deciders to LES ∈ {3, 5, 7}, this path is effectively empty by the time step 10 runs. It does not explain the observed household losses.

2. **Wage-bounds path** (actual cause): drops households where an employed decider has `wage_unbounded` (the pre-clipping wage) outside the [€2, €170] per-hour interval.

**Fix:** Replaced the single unsupported sentence with a precise description of both paths, identifying the wage-bounds filter as the operative cause:

> "Households are **dropped** only when an employed decider's pre-clipping wage (`wage_unbounded`) falls outside the [€2, €170] per-hour bounds. The hours-driven drop path (`must_filter_out` in the code) applies to cases where a very-low-hours decider has LES outside {3, 5, 7}; since step 4 already screens all deciders to LES ∈ {3, 5, 7}, this path is effectively empty by the time the final step runs."

The recoding descriptions (capping, reclassification as inactive) were retained and corrected to use "recoded" rather than "filtered" language consistently.

---

## 7. Files modified

| File | Change type | Summary |
|------|-------------|---------|
| `docs/JMP_multi_year_sample_construction_descriptives_report_v1.md` | Text correction | Heading demoted; §§3, 4, 6, 12, 18 education wording corrected; §3 couples LES step corrected; §6 wage/hours drop rationale corrected |
| `docs/JMP_multi_year_sample_construction_descriptives_correction_report_v1.md` | New file | This report |

No other files were modified.

---

## 8. Whether tables changed

**No tables changed.** The attrition tables in §§14–16 and the descriptive-statistics table in §17 are untouched. All numerical values, step labels, and table structure are identical to the original. The step labels "Education (Head)" and "Education (Partner)" in the attrition tables come directly from the pipeline-generated stats CSVs and are preserved as-is; the corrected prose now explains that these step names reflect enrolment-status tests, not education-data-quality checks.

---

## 9. Whether figures changed

**No figures changed.** The 18 PNG files in `Results/figures/multi_year_descriptives/` are untouched. No figure captions in the report needed correction.

---

## 10. Final status

The corrected report `docs/JMP_multi_year_sample_construction_descriptives_report_v1.md` now:

- Has exactly **22 `##`-level headings** (§§1–22); the version/date line is plain italic text.
- Correctly describes the education-filter step as an **enrolment-status exclusion** (`dec == 0`, not currently in education) throughout §§3, 4, 6, 12, and 18. No passage refers to missing or invalid education data.
- Correctly describes the **Allowed LES step for couples** as applying to all deciders (head and partner), not head-only. The singles description is unchanged.
- Correctly describes the **household drop** at the final pipeline step as arising from the wage-bounds filter on `wage_unbounded`, without unsupported claims about budget-constraint inconsistency.

No data were rebuilt. No tables were regenerated. No figures were changed. No cleaning rules were altered.