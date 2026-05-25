# M1 Identity Validation Summary

**Config:** p3a
**Source:** \\crc\users\hisham\Desktop\Nizam_Hisham\MNL\Data\processed\fr\pooled\fr_p3a_gsurv2_stacked_raw.parquet
**Generated:** 20260520_223645
**Reference:** §13 of JMP_multi_year_stage_M1_implementation_plan_v2.md

---

## Thresholds Applied

| Criterion | Threshold | Action |
| --- | --- | --- |
| Sex stability (dgn) | >= 0.9990 | warn |
| Age progression within +/-1 | >= 0.9950 | warn |
| Suspicious records (warn) | <= 0.0020 | warn |
| Suspicious records (block) | > 0.0100 | BLOCK |
| Household continuity | >= 0.9700 | warn |

---

## Results by Year Pair

### 2015->2016

| Metric | Value |
| --- | --- |
| Repeat persons | 0 |
| Repeat households | 0 |
| Expected repeat hh (addendum v2) | 0 |
| Overall status | **PASS** |

**Outcomes:**

- PASS (no repeat persons -- disjoint panel)

### 2015->2017

| Metric | Value |
| --- | --- |
| Repeat persons | 0 |
| Repeat households | 0 |
| Expected repeat hh (addendum v2) | 0 |
| Overall status | **PASS** |

**Outcomes:**

- PASS (no repeat persons -- disjoint panel)

### 2016->2017

| Metric | Value |
| --- | --- |
| Repeat persons | 2,743 |
| Repeat households | 2,788 |
| Expected repeat hh (addendum v2) | 8796 |
| sex_stability | 1.0000 |
| age_pct_within1 | 1.0000 |
| suspicious_rate | 0.0000 |
| hh_continuity | 0.9985 |
| educ_stability_wa | 0.9754 |
| Overall status | **PASS** |

**Outcomes:**

- sex_stability=1.0000
- age_progression_within1=1.0000
- suspicious_rate=0.0000
- educ_stability (age 25-60)=0.9754
- hh_continuity=0.9985

---

## Final Status: PASS

All year-pairs passed the block threshold. Warnings (if any) are noted above and should be reviewed.
