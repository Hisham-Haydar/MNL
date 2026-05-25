# JMP GSUR Year Alignment Decision v1

**Project:** RURO / EUROMOD labour-supply pipeline (France)
**Date:** 2026-05-20
**Author:** Hisham Haydar
**Status:** Adopted

---

## 1. Decision summary

The GSUR opportunity year must equal the EUROMOD system year, not the survey data year. All MNL-input parquets must be rebuilt or flagged in accordance with this rule before any result enters the final pooled estimation.

---

## 2. Background

Each survey year's MNL-input parquet merges GSUR (job-acceptance rates) from a lookup table keyed by `(year, drgn1, dgn, educ3)`. The EUROMOD system year lags the survey data year by one:

| Survey data year | EUROMOD system year | Correct GSUR opportunity year |
|-----------------|--------------------|-----------------------------|
| FR_2015         | FR_2014            | 2014                        |
| FR_2016         | FR_2015            | 2015                        |
| FR_2017         | FR_2016            | 2016                        |

**Current state prior to this decision:**

- FR_2015 parquet: GSUR keyed to year=2015 (data year). Correct key is 2014. Mean absolute rate difference ≈ 0.010, approximately 10 % of mean GSUR 0.095. Sidecar patched with `gsur_alignment_status: misaligned`.
- FR_2016 parquet: GSUR from `FR_gsur_ruro_v2_stageA.parquet` with year=2016 hardcoded. Correct opportunity year is 2015. GSURv2 exists only for year=2016; extending it to earlier years requires Eurostat denominator acquisition and INSEE BDM retrieval, which is out of scope for the current task. Sidecar cites wrong source file.
- FR_2017: not yet executed. Without correction, the planned command would key GSUR to year=2017 (data year), which is incorrect.

`FR_gsur_ruro.parquet` (v1 fallback) contains rows for years 2007–2024, including 2014, 2015, and 2016. All needed opportunity years are present in v1.

---

## 3. Decision 1 — FR_2015 rebuild

**Verdict:** Rebuild the FR_2015 MNL-input parquet using GSUR year=2014 from `FR_gsur_ruro.parquet` (v1 fallback).

- Source: `FR_gsur_ruro.parquet`, key year=2014.
- Sidecar tag: `gsur_source: v1_fallback_opportunity_year_aligned`.
- Prior misaligned parquet must be retired and must not enter any pooled estimation run.

---

## 4. Decision 2 — FR_2017 execution

**Verdict:** Execute the FR_2017 preparation run with GSUR year=2016 from `FR_gsur_ruro.parquet` (v1 fallback).

- Source: `FR_gsur_ruro.parquet`, key year=2016.
- Sidecar tag: `gsur_source: v1_fallback_opportunity_year_aligned`.
- The command plan must be amended before execution; year=2017 keying is not acceptable.

---

## 5. Decision 3 — v1 fallback for provisional Stage M1 dry-run

**Verdict:** FR_2015 (rebuilt) and FR_2017 (new) may be used in a provisional Stage M1 pooled dry-run under the v1 fallback, subject to explicit labelling.

- All outputs must carry the label `provisional_v1_fallback` in filenames, sidecars, and any result tables.
- No parameter estimates from this dry-run may be reported as final in the paper.
- The dry-run serves only to validate pipeline mechanics and cross-year stability diagnostics.

---

## 6. Decision 4 — Final pooled construction requirement

**Verdict:** Final pooled estimation requires GSURv2 rebuilt for each opportunity year (2014, 2015, 2016) before any year's parquet is promoted to final status.

- GSURv2 for years 2014 and 2015 requires Eurostat denominator acquisition and INSEE BDM retrieval; this work is out of scope for the current sprint.
- Until GSURv2 opportunity-year-aligned parquets exist for all three survey years, no pooled result may be labelled final.
- FR_2016 sidecar must be corrected to reference the actual source file used.

---

## 7. Rationale

The GSUR rate proxies the probability that a randomly drawn job offer, within a cell defined by region, gender, and education, is acceptable to the worker. This probability is an equilibrium object from the same institutional environment that determines simulated net incomes — i.e., the EUROMOD system year, not the survey collection year. Keying GSUR to the data year rather than the opportunity year introduces a one-year lag error in the market conditions faced by the simulated agent. The error is small on average (≈ 1 percentage point) but is systematic and avoidable, and would compromise the internal consistency of the structural model.

---

## 8. Implications and constraints

- FR_2015 rebuild requires re-running the prep script with the year key corrected; no other pipeline changes are needed.
- FR_2017 command plan must be reviewed and amended before the first execution.
- GSURv2 extension to years 2014 and 2015 is a prerequisite for the final pooled build and must be scoped as a separate task.
- The FR_2016 sidecar correction is a documentation fix only and does not require a data rebuild.
- Provisional dry-run results must be clearly segregated from any final results registry entry.

---

## 9. What this decision does not cover

- The construction methodology for GSURv2 (denominator sources, aggregation rules, smoothing). That is governed by `RURO_GSUR_rebuild_specification_v2_1.md`.
- The schedule or resourcing for GSURv2 extension to years 2014 and 2015.
- Cross-year pooling weights, CPI deflation, or any other multi-year estimation design choice. Those are governed by the strategy memos in `docs/`.
- Any change to the GSUR merge logic, cell definitions, or variable construction.

---

## 10. Authorization

**Decision date:** 2026-05-20
**Author:** Hisham Haydar

This memo supersedes any prior implicit convention about GSUR year keying in the RURO/EUROMOD pipeline. All future MNL-input parquet builds must comply with the opportunity-year alignment rule stated in Section 2.