# JMP Single-Year Consolidated Readiness Verdict v1

**Document:** Results/JMP_single_year_consolidated_readiness_verdict_v1.md  
**Date:** 2026-05-20  
**Author:** Pipeline execution via Claude Code  
**Scope:** FR_2015, FR_2016, FR_2017 MNL inputs — GSUR alignment audit and Stage M1 authorization gate  
**Depends on:**
- `docs/JMP_GSUR_year_alignment_decision_v1.md` (alignment rule)
- `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md` (FR_2015 rebuild)
- `Results/JMP_single_year_FR2017_replication_report_v1.md` (FR_2017 replication)
- `Results/JMP_single_year_2016_local_mirror_report_v1.md` (FR_2016 mirror)

---

## 1. Purpose

This document answers one question: **Can Stage M1 (P3a) live stacking proceed given the current MNL input files for FR_2015, FR_2016, and FR_2017?**

Three subsidiary questions must be answered first:

1. What GSUR opportunity year does each file actually use?
2. What GSUR opportunity year does the alignment rule require?
3. For any mismatch: is Option A (rebuild) or Option B (proceed under explicit restriction) the appropriate resolution?

---

## 2. GSUR alignment rule (adopted)

Per `docs/JMP_GSUR_year_alignment_decision_v1.md` Decision 2:

> **GSUR key = EUROMOD system year (opportunity year), NOT survey data year.**

Mapping:

| Survey data year | EUROMOD system | GSUR opportunity year (correct) |
| ---------------- | -------------- | -------------------------------- |
| 2015             | FR_2014        | 2014                             |
| 2016             | FR_2015        | 2015                             |
| 2017             | FR_2016        | 2016                             |

---

## 3. GSUR alignment status — all three years

| Year | Current file stem | GSUR rates actually used | Correct opp. year | Aligned? | Evidence |
| ---- | ----------------- | ------------------------ | ----------------- | -------- | -------- |
| 2015 | `fr_2015_RURO_mnl_v1gsurY2014__` | year=2014 | 2014 | **✓ aligned** | Cell check: row0 rate=0.061 = v1 year=2014 ✓; sidecar `gsur_opportunity_year: 2014` |
| 2016 | `fr_2016_RURO_mnl_GSURv2__` | year=2016 | 2015 | **✗ misaligned** | Cell check: row0 rate=0.153 = v1 year=2016 ✓, ≠ v1 year=2015 (0.121); sidecar has no alignment fields |
| 2017 | `fr_2017_RURO_mnl_v1gsurY2016__` | year=2016 | 2016 | **✓ aligned** | Cell check: row0 rate=0.103 = v1 year=2016 ✓; sidecar `gsur_opportunity_year: 2016` |

### FR_2015 detail

- File: `Data/processed/fr/fr_2015_RURO_mnl_v1gsurY2014__singles.parquet`  
- Built with `--gsur-year 2014 --year 2015` via patched `enh_RURO_prep_mnl_basic.py`  
- Singles mean gsur: 0.094059  
- Sidecar: `gsur_version=v1_fallback_opportunity_year_aligned`, `gsur_alignment_status=aligned`  
- Report: `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md`

### FR_2016 detail

- File: `Data/processed/fr/fr_2016_RURO_mnl_GSURv2__singles.parquet`  
- Built on 2026-05-13 (M1-clean operative run)  
- The name segment `GSURv2__` refers to the workflow context (GSURv2 infrastructure), not the GSUR rates source — actual source is `FR_gsur_ruro.parquet` (v1 fallback), cited correctly in sidecar `inputs.gsur_file`  
- However, the v1 filter year applied during that run was **2016** (data year), not 2015 (correct opportunity year)  
- Cell check (performed 2026-05-20): row0 drgn1=1, dgn=0, educ3=0; observed rate=0.153  
  - v1 year=2014: 0.121 — no match  
  - v1 year=2015: 0.121 — no match  
  - v1 year=2016: 0.153 — **exact match**  
  - v1 year=2017: 0.151 — no match  
- Singles mean gsur: 0.092740  
- Sidecar has no `gsur_opportunity_year`, `gsur_alignment_status`, or `gsur_alignment_rule` fields  
- Provenance mismatch: sidecar cites `FR_gsur_ruro.parquet` (v1) as `inputs.gsur_file`, which is correct as the data source, but the year=2016 filter was applied to it — not the correct year=2015 filter  
- **Verdict: MISALIGNED under the adopted alignment rule**

### FR_2017 detail

- File: `Data/processed/fr/fr_2017_RURO_mnl_v1gsurY2016__singles.parquet`  
- Built with `--gsur-year 2016 --year 2017`  
- Singles mean gsur: 0.084 (observed in run output)  
- Sidecar: `gsur_version=v1_fallback_opportunity_year_aligned`, `gsur_opportunity_year: 2016`, `gsur_alignment_status: aligned`  
- Report: `Results/JMP_single_year_FR2017_replication_report_v1.md`

---

## 4. GSUR source summary

| Year | v1 GSUR year filter | GSUR source file | Sidecar alignment fields | Aligned per rule? |
| ---- | ------------------- | ---------------- | ------------------------ | ----------------- |
| 2015 | 2014 | `FR_gsur_ruro.parquet` (v1 fallback) | ✓ present | ✓ |
| 2016 | 2016 (wrong: should be 2015) | `FR_gsur_ruro.parquet` (v1 fallback) | ✗ absent | ✗ |
| 2017 | 2016 | `FR_gsur_ruro.parquet` (v1 fallback) | ✓ present | ✓ |

---

## 5. Stage M1 authorization verdict

**Stage M1 (P3a) live stacking is NOT yet authorized.**

The current FR_2016 MNL input (`fr_2016_RURO_mnl_GSURv2__`) is misaligned under the adopted alignment rule. Proceeding with pooled stacking that includes this file would produce a P3a stacked dataset with inconsistent GSUR definitions across years:

- 2015: job-entry rates for year 2014 (age/sex/region/education cells from survey year 2014)
- 2016: job-entry rates for year 2016 (wrong year — should reflect labor market conditions in 2015 when opportunities were observed)
- 2017: job-entry rates for year 2016 ✓

Mixed GSUR-year data in the stacked file would contaminate the GSUR-weighted opportunity terms in M0 estimation without any way to correct post hoc. The misalignment is not a label error — it affects which cell rates are merged onto which deciders.

---

## 6. Option A vs Option B

### Option A — Rebuild FR_2016 MNL input as `v1gsurY2015` (RECOMMENDED)

Re-run Stage 5 only for FR_2016, using existing draws and EUROMOD combined output on Z:, with `--gsur-year 2015 --year 2016`. All upstream files are present:

- Draws: `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\singles_RURO_ready_RURO_draws.parquet` and couples equivalent
- EUROMOD combined: `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\ruro_occ\scenarios\combined_draws_em.parquet`
- GSUR source: `Data/external/FR_gsur_ruro.parquet` (v1; already used by existing file)
- `--gsur-year` flag: already implemented in `enh_RURO_prep_mnl_basic.py`

Output stem: `fr_2016_RURO_mnl_v1gsurY2015`  
Output location: `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_v1gsurY2015__{singles,couples,mnlmeta}.*`

After building: patch sidecar with alignment fields, copy to `Data/processed/fr/`, remove or shadow the current misaligned `fr_2016_RURO_mnl_GSURv2__` local copy, re-run dry-run to confirm all three FOUND.

**Consequence for M1-clean verdict file (`docs/RURO_occ_M1_clean_verdict_v1.md`):** The M1-clean verdict used `fr_2016_RURO_mnl_GSURv2__` as its operative data. A rebuild to `v1gsurY2015` changes the GSUR rates for FR_2016 deciders. This affects LL and parameter estimates for the M1-clean model. **The M1-clean verdict LL figure (−6487.5522) would no longer correspond to the pooled dataset's FR_2016 slice under Option A.** This is noted as a known consequence; the verdict remains valid for the `GSURv2__` data, but the P3a pooled estimation will be conducted on the GSUR-aligned `v1gsurY2015` data.

**Option A is the recommended path.** It produces a fully consistent three-year dataset, takes less than one hour (Stage 5 only, no EUROMOD run needed), and avoids any prohibition on empirical interpretation of misaligned results.

### Option B — Provisional dry-run with mixed GSUR alignment (NOT RECOMMENDED for live execution)

Proceed to Stage M1 P3a live run using existing files (2015: aligned, 2016: misaligned, 2017: aligned). Permitted only if:

1. Output is labelled `provisional_mixed_gsur_alignment`
2. Empirical interpretation of any GSUR-weighted quantity is prohibited
3. FR_2016 misalignment is disclosed in every output file sidecar
4. Option A rebuild is committed to before any JMP-facing analysis

This option has no material advantage over Option A given that all upstream files are already present. It delays alignment correction while creating a labelling and documentation burden that must be carried through all downstream outputs.

**Option B is not recommended.** The infrastructure to execute Option A is already in place.

---

## 7. FR_2016 sidecar provenance issues (independent of GSUR alignment)

Two provenance issues in the current `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` sidecar are noted regardless of Option A/B:

| Issue | Current sidecar state | Correct state |
| ----- | --------------------- | ------------- |
| GSUR opportunity year | Field absent | Should record `gsur_opportunity_year: 2015` (after rebuild) or `2016` (as-built, with misalignment flag) |
| GSUR alignment status | Field absent | Should record `gsur_alignment_status: misaligned` (as-built) or `aligned` (after rebuild) |
| `effective_prior_source_singles` | `stijn_layered_log_q` | Legacy label from Z: source predating naming policy; cosmetic, does not affect data |

Under Option A the rebuilt sidecar will be written fresh by `enh_RURO_prep_mnl_basic.py` with correct alignment fields, resolving issues 1 and 2. Issue 3 (legacy label in Z: source) can be patched in the new sidecar or left as a Z: provenance note.

---

## 8. Stage M1 dry-run state (as of 2026-05-20)

The dry-run confirms all three years FOUND in `Data/processed/fr/`:

```
======================================================================
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
======================================================================

Inputs:
  [2015]  FOUND  ...\Data\processed\fr\fr_2015_RURO_mnl_v1gsurY2014__couples.parquet
  [2016]  FOUND  ...\Data\processed\fr\fr_2016_RURO_mnl_GSURv2__couples.parquet
  [2017]  FOUND  ...\Data\processed\fr\fr_2017_RURO_mnl_v1gsurY2016__couples.parquet

Status: READY (all inputs present)
```

The dry-run returning READY does not constitute Stage M1 authorization. The dry-run tests file presence and path resolution only; it does not validate GSUR alignment. The three-year set is structurally complete but GSUR-inconsistent until FR_2016 is rebuilt under Option A.

---

## 9. Required steps before Stage M1 live authorization

| Step | Action | Status |
| ---- | ------ | ------ |
| 1 | Rebuild FR_2016 MNL input with `--gsur-year 2015 --year 2016` → stem `fr_2016_RURO_mnl_v1gsurY2015` | **PENDING** |
| 2 | Patch rebuilt sidecar with alignment fields (`gsur_version`, `gsur_opportunity_year`, `gsur_alignment_status`, `gsur_alignment_rule`, `gsur_data_year`, `gsur_note`) | **PENDING** |
| 3 | Cell-level GSUR rate verification: confirm row0 rate matches v1 year=2015 table value | **PENDING** |
| 4 | Copy rebuilt files to `Data/processed/fr/` (with `fr_2016_RURO_mnl_v1gsurY2015__` stem) | **PENDING** |
| 5 | Remove or shadow misaligned `fr_2016_RURO_mnl_GSURv2__` local copies from `Data/processed/fr/` | **PENDING** |
| 6 | Re-run Stage M1 P3a dry-run; confirm 2016 resolves to `v1gsurY2015` file | **PENDING** |
| 7 | Write FR_2016 rebuild report (`Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md`) | **PENDING** |
| 8 | Update `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` verdict to AUTHORIZED | **PENDING** |

All of steps 1–6 are mechanically straightforward (no EUROMOD run needed). Estimated time: under 30 minutes.

---

## 10. Summary verdict

| Dimension | Status |
| --------- | ------ |
| FR_2015 GSUR alignment | **PASS** — year=2014, aligned |
| FR_2016 GSUR alignment | **FAIL** — year=2016 used; year=2015 required |
| FR_2017 GSUR alignment | **PASS** — year=2016, aligned |
| All three years structurally present (dry-run FOUND) | PASS |
| GSUR consistency across years | **FAIL** — FR_2016 misaligned |
| Stage M1 P3a live execution authorized | **NO** |
| Recommended resolution | **Option A: rebuild FR_2016 with `--gsur-year 2015`** |
| Infrastructure for Option A in place | **YES** — all upstream Z: files present; `--gsur-year` flag implemented |

---

*Prepared by pipeline execution. Authorisation of Stage M1 live run requires completion of all steps in §9 and amendment of `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md`.*