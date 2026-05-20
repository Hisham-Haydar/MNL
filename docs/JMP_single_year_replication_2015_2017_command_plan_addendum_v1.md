# JMP Single-Year Replication Command Plan — Addendum v1

**Document:** docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md  
**Date:** 2026-05-20  
**Amends:** docs/JMP_single_year_replication_2015_2017_command_plan_v2.md  
**Companion:** Results/JMP_single_year_FR2015_replication_addendum_v1.md  
**Author:** Hisham Haydar

---

## 1. Purpose

This addendum corrects the GSUR keying convention for the FR_2015 and FR_2017
single-year replications. It formalizes the **opportunity-year alignment rule**
and specifies the required changes to FR_2017 Step 5 (MNL prep) before execution.

The addendum does not alter the five-stage command sequence, the draw parameters,
the EUROMOD system/dataset values, or the pre-GSURv2 labelling policy in the parent
command plan v2. All other sections of command plan v2 remain in force.

---

## 2. GSUR opportunity-year rule

**Rule:**

The GSUR year used when merging job-acceptance rates in
`enh_RURO_prep_mnl_basic.py` (Step 5) should correspond to the **EUROMOD system
year**, not the survey data year. The EUROMOD system determines the tax-benefit
and labour-market environment against which draws are evaluated; the GSUR rate
should reflect the same opportunity environment.

**Formal mapping:**

| Data year | EUROMOD system | Correct GSUR year |
|-----------|----------------|-------------------|
| 2015 | `FR_2014` | **2014** |
| 2016 | `FR_2015` | **2015** |
| 2017 | `FR_2016` | **2016** |
| 2018 | `FR_2017` | **2017** |

**This rule is binding from this addendum forward**, unless a subsequent memo
explicitly overturns it with documented rationale.

---

## 3. Required change to FR_2015 interpretation

FR_2015 has already been executed. Parquet inspection confirmed that the `gsur`
column in `fr_2015_RURO_mnl__singles.parquet` matches the v1 GSUR table at
`year=2015` exactly (mean abs diff = 0.000000), while `year=2014` differs by
approximately 0.010 (≈ 10% of mean GSUR ≈ 0.095).

**FR_2015 output is GSUR-year-misaligned.** The parquet used the data year (2015)
as the GSUR key; the correct opportunity year is 2014.

**Required action:**
1. Both copies of the sidecar (`Data/processed/fr/fr_2015_RURO_mnl__mnlmeta.json`
   and `Z:\...\fr\2015\fr_2015_RURO_mnl__mnlmeta.json`) have been patched with:
   - `gsur_alignment_status: misaligned`
   - `gsur_opportunity_year: 2014`
   - `gsur_data_year: 2015`
   - `gsur_alignment_rule: opportunity_year = euromod_system_year`
2. The parquets are labelled pre-GSURv2 / not final for pooled estimation.
3. Re-running Stage 5 for FR_2015 with `year=2014` as the GSUR key is a future
   task, requiring a separate authorization once `enh_RURO_prep_mnl_basic.py`
   supports a `--gsur-year` argument or an equivalent keying override.

**FR_2015 remains valid for Stage M1 dry-run and single-year diagnostics.**

---

## 4. Required change to FR_2017 command plan

The parent command plan v2 §5b and §11 specify Step 5 for FR_2017 as:

```powershell
& python enh_RURO_prep_mnl_basic.py `
    ...
    --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2017
```

If `enh_RURO_prep_mnl_basic.py` keys the GSUR merge on `--year` (the data year),
this command will merge GSUR rates from `year=2017` in the v1 table. Under the
opportunity-year rule, the correct year is **2016** (EUROMOD system `FR_2016`).

**Required change — two options:**

**Option A (preferred): Add `--gsur-year` argument**

Before executing FR_2017 Step 5, verify whether `enh_RURO_prep_mnl_basic.py`
supports a `--gsur-year` argument. If it does (or after adding it):

```powershell
& python enh_RURO_prep_mnl_basic.py `
    --singles-draws   "Z:\...\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws   "Z:\...\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\...\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base        "Z:\...\fr\2017\fr_2017_RURO_mnl" `
    --drawsmeta       "Z:\...\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file       "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2017 `
    --gsur-year 2016
```

**Option B (fallback): Execute with data year, patch sidecar post-run**

If `--gsur-year` is not available, execute Step 5 as specified in command plan v2
(using `--year 2017`, which will key GSUR to year=2017). After the run, patch the
sidecar to record the misalignment explicitly:

```json
"gsur_alignment_rule":   "opportunity_year = euromod_system_year",
"gsur_opportunity_year": 2016,
"gsur_data_year":        2017,
"gsur_alignment_status": "misaligned",
"gsur_note": "GSUR keyed to data year 2017; opportunity year (EUROMOD system FR_2016) is 2016. Not final for pooled estimation."
```

**In either case, the FR_2017 output must be explicitly labelled as:**
- pre-GSURv2 (as already required by command plan v2 §19)
- AND either GSUR-year-aligned (if Option A) or GSUR-year-mismatched (if Option B)

---

## 5. Required preflight before FR_2017 execution

In addition to the EUROMOD system/dataset preflight already required by command
plan v2 §8, the following must be confirmed before FR_2017 Step 5:

1. **Determine `--gsur-year` support:** inspect `enh_RURO_prep_mnl_basic.py`
   argparse to confirm whether a `--gsur-year` or equivalent argument exists.
   If absent, use Option B.

2. **Confirm GSUR year=2016 rows exist in v1 file:** confirmed in this session —
   `FR_gsur_ruro.parquet` contains `year=2016` rows (2,160 total rows across
   2007–2024; year=2016 present). This is sufficient for the merge.

3. **Record the chosen option** (A or B) in the FR_2017 execution prompt and
   in `Results/JMP_FR_2017_single_year_pipeline_log_v1.md`.

4. **Sidecar must record** at minimum:
   - `gsur_version: v1_fallback`
   - `gsur_alignment_rule: opportunity_year = euromod_system_year`
   - `gsur_opportunity_year: 2016`
   - `gsur_data_year: 2017`
   - `gsur_alignment_status: aligned` (if Option A) or `misaligned` (if Option B)

---

## 6. What remains blocked

| Item | Blocker | Required action |
|------|---------|-----------------|
| FR_2017 replication | Must cite this addendum; GSUR-year handling must be determined | Inspect argparse; choose Option A or B; proceed |
| FR_2015 GSUR-year correction | Requires `--gsur-year` support in `enh_RURO_prep_mnl_basic.py`; separate authorization | New task after script is parameterized |
| FR_2016 GSUR provenance resolution | Requires reading `FR_gsur_ruro_v2_stageA.parquet` and confirming year keying | Separate task; does not block FR_2017 dry-run |
| Stage M1 P3a live run | FR_2017 still absent; GSURv2/alignment issues unresolved for production use | Complete FR_2017; then issue Stage M1 execution authorization |
| Production P3a estimation (final pooled) | GSUR-year alignment unresolved for 2015 (and potentially 2017 if Option B); GSURv2 absent for 2015/2017 | Requires full GSUR resolution and new authorization memo |

**The immediate unblocking path:**
1. Inspect `enh_RURO_prep_mnl_basic.py` for `--gsur-year` support.
2. Execute FR_2017 replication per command plan v2, modified per §4 above.
3. Mirror FR_2017 parquets to `Data/processed/fr/`.
4. Confirm Stage M1 P3a dry-run: all three years FOUND.
5. Update Stage M1 execution-readiness verdict.