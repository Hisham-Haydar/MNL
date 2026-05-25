# JMP Single-Year FR_2016 — GSUR Opportunity-Year Aligned Rebuild Report v1

**Document:** Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md  
**Date:** 2026-05-20  
**Author:** Pipeline execution via Claude Code  
**Authorization:** `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` (Decision 2) + user authorization 2026-05-20  
**Output stem:** `fr_2016_RURO_mnl_v1gsurY2015`  
**GSUR decision memo:** `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md`  
**Readiness verdict:** `Results/JMP_single_year_consolidated_readiness_verdict_v1.md`

---

## 1. Rebuild verdict

**PASS — FR_2016 GSUR opportunity-year aligned MNL input constructed successfully.**

- Stage 5 only re-run using existing draws and EUROMOD combined output on Z:.
- GSUR opportunity year 2015 applied via `--gsur-year 2015 --year 2016`.
- Cell-level GSUR rate verification: 8 disambiguating cells all match v1 year=2015 exactly, none match year=2014 or year=2016.
- Zero missing `gsur` in singles and couples.
- All internal sanity checks passed.
- Sidecar patched with all required alignment fields.
- Local mirror in place; misaligned `GSURv2__` local copies removed; Z: originals untouched.
- Stage M1 P3a dry-run: **2015 FOUND, 2016 FOUND (v1gsurY2015), 2017 FOUND — Status: ready to run.**

---

## 2. Why rebuild was required

The prior operative FR_2016 MNL-input file (`fr_2016_RURO_mnl_GSURv2__`) used GSUR rates from v1 year=2016. Under the adopted alignment rule (GSUR key = EUROMOD system year), the correct opportunity year for FR_2016 is 2015 (EUROMOD system `FR_2015`). Cell-level verification confirmed:

- `fr_2016_RURO_mnl_GSURv2__` row0: rate=0.153 = v1 year=2016 (wrong)
- Correct cell rate for year=2015: 0.121 (13.7% lower for this cell)
- The misalignment was not a label error — it affected which cell rates were merged onto which deciders

Per `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` §5, proceeding to Stage M1 live stacking with this misalignment would contaminate GSUR-weighted opportunity terms without post-hoc correction. Option A (rebuild) was the recommended and authorized path.

---

## 3. Files inspected

| Document | Purpose |
| -------- | ------- |
| `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` | Misalignment diagnosis, Option A authorization |
| `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` | Alignment rule, Decision 2 |
| `docs/France_case/RURO_prep_mnl_gsur_year_support_report_v1.md` | `--gsur-year` flag implementation details |
| `Results/JMP_single_year_2016_local_mirror_report_v1.md` | Prior FR_2016 mirror state, file provenance |
| `docs/RURO_occ_M1_clean_verdict_v1.md` | M1-clean operative file identity; confirmed `GSURv2__` is M1-clean baseline |
| `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` | Draw parameters (binding); no-overwrite rules |
| `docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` | GSUR alignment rule; Option A specification |

---

## 4. Commands run

**Stage 5 only — MNL input construction:**

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\stijn_occ\scenarios\combined_draws_em.parquet" `
    --out-base         "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_v1gsurY2015" `
    --drawsmeta        "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file        "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --gsur-year 2015 `
    --year 2016
```

**Post-run sidecar patch (two fields the script does not write):**

```python
meta["gsur_version"] = "v1_fallback_opportunity_year_aligned"
meta["gsur_opportunity_year"] = 2015
```

Applied to Z: sidecar at `Z:\...\fr\2016\fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json`.

**Stage M1 dry-run:**

```powershell
& python "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_stack_years.py" --config p3a --dry-run
```

---

## 5. Existing inputs reused

No new draws or EUROMOD run was performed. All upstream files were reused from Z:

| Input | Path | Size (bytes) | Status |
| ----- | ---- | ------------ | ------ |
| Singles draws | `Z:\...\fr\2016\singles_RURO_ready_RURO_draws.parquet` | 13,247,981 | Present, unchanged |
| Couples draws | `Z:\...\fr\2016\couples_RURO_ready_RURO_draws.parquet` | 35,898,906 | Present, unchanged |
| EUROMOD combined | `Z:\...\fr\2016\stijn_occ\scenarios\combined_draws_em.parquet` | 487,855,335 | Present, unchanged |
| Drawsmeta | `Z:\...\fr\2016\singles_RURO_ready_RURO_draws__drawsmeta.json` | 11,630 | Present, unchanged |
| GSUR v1 lookup | `Data/external/FR_gsur_ruro.parquet` | 11,688 | Present; year=2015 filter applied |

Drawsmeta confirmed: n_draws=99, wage_spec=vw, occ_spec=empirical, h_min=5.0, h_max=70.0, w_min=2.0, w_max=170.0, pi0_m=0.1. All match binding draw parameters from `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` §6.

---

## 6. GSUR year used

| Parameter | Value |
| --------- | ----- |
| `--gsur-year` (opportunity year) | **2015** |
| `--year` (data year) | **2016** |
| EUROMOD system | `FR_2015` |
| GSUR source file | `Data/external/FR_gsur_ruro.parquet` (v1 fallback) |
| GSUR rows after year=2015 filter | 120 rows |
| Year column overwrite in merge key | `gsur_df["year"] = 2016` (merge resolves against draws data year) |

**Alignment rule applied:** GSUR opportunity year = EUROMOD system year = 2015.

The script logs:
```
GSUR filtered to opportunity year 2015: 120 rows
GSUR lookup year column set to data year 2016 for merge-key alignment (opportunity year: 2015).
```

---

## 7. Output files created

| File | Path (Z:) | Size (bytes) | Rows | Cols |
| ---- | --------- | ------------ | ---- | ---- |
| `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | `Z:\...\fr\2016\` | 21,500,531 | 167,600 | 75 |
| `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | `Z:\...\fr\2016\` | 43,108,696 | 257,700 | 93 |
| `fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json` | `Z:\...\fr\2016\` | 58,442 | — | — |

Script output (verbatim):
```
Wrote singles MNL: ...\fr_2016_RURO_mnl_v1gsurY2015__singles.parquet (167,600 rows, 75 cols, 20.5 MB)
Wrote couples MNL: ...\fr_2016_RURO_mnl_v1gsurY2015__couples.parquet (257,700 rows, 93 cols, 41.1 MB)
Wrote metadata sidecar: ...\fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json
```

---

## 8. Local mirror files created

Copied to `Data/processed/fr/` after patching Z: sidecar. All three size-match confirmed.

| File | Destination | Size (bytes) | Size match |
| ---- | ----------- | ------------ | ---------- |
| `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | `Data/processed/fr/` | 21,500,531 | SIZE_MATCH ✓ |
| `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | `Data/processed/fr/` | 43,108,696 | SIZE_MATCH ✓ |
| `fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json` | `Data/processed/fr/` | 58,442 | SIZE_MATCH ✓ |

Misaligned local copies removed from `Data/processed/fr/`:

| File removed | Reason | Z: original status |
| ------------ | ------ | ------------------ |
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | GSUR-year-misaligned; replaced by `v1gsurY2015` | Intact on Z: (21,510,188 bytes) |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | GSUR-year-misaligned | Intact on Z: (43,130,386 bytes) |
| `fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | GSUR-year-misaligned | Intact on Z: (57,973 bytes) |

---

## 9. Metadata sidecar fields

All required alignment fields verified in `fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json` (Z: and local copies are identical):

| Field | Value |
| ----- | ----- |
| `year` | `2016` |
| `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| `gsur_opportunity_year` | `2015` |
| `gsur_data_year` | `2016` |
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` |
| `gsur_alignment_status` | `aligned` |
| `gsur_note` | `GSUR filtered to opportunity year 2015 (EUROMOD system year) before merge. Data year: 2016. v1_fallback_opportunity_year_aligned / not final for pooled estimation until GSURv2 opportunity-year-aligned rates are available.` |
| `sample_sizes.singles_deciders` | 1,676 |
| `sample_sizes.couples_deciders` | 2,577 |
| `sample_sizes.singles_total_rows` | 167,600 |
| `sample_sizes.couples_total_rows` | 257,700 |
| `sample_sizes.n_draws` | 100 |
| `normalization.singles.c_scale` | 7,590.29 |
| `normalization.couples.c_scale` | 15,106.18 |

`gsur_version` and `gsur_opportunity_year` were patched manually after the script run (the script writes `gsur_data_year`, `gsur_alignment_rule`, `gsur_alignment_status`, `gsur_note` but not these two fields).

---

## 10. Row counts

| File | Total rows | n_draws | Rows/draw | Check |
| ---- | ---------- | ------- | --------- | ----- |
| Singles | 167,600 | 100 | 1,676 | 167,600 / 100 = 1,676 ✓ |
| Couples | 257,700 | 100 | 2,577 | 257,700 / 100 = 2,577 ✓ |

Draw index: 0–99 in both files. `draw=0` is the observed/chosen state (decider row).

---

## 11. Household counts

| File | Unique `idhh` (decider households) | Matches sidecar `sample_sizes` |
| ---- | ---------------------------------- | ------------------------------ |
| Singles | 1,676 | ✓ |
| Couples | 2,577 | ✓ |

---

## 12. Identifier checks

All four Stage M1 raw-ID columns present in both files:

| Column | Singles | Couples |
| ------ | ------- | ------- |
| `idhh` | ✓ | ✓ |
| `idperson` | ✓ | ✓ |
| `idorighh` | ✓ | ✓ |
| `idorigperson` | ✓ | ✓ |

---

## 13. Key variables present

| Variable | Singles | Couples | Notes |
| -------- | ------- | ------- | ----- |
| `dag` | ✓ | absent (gender-specific: `dag_male`, `dag_female`) | Age |
| `dgn` | ✓ | ✓ | Sex |
| `drgn1` | ✓ | ✓ | NUTS1 region |
| `ils_dispy` | ✓ | absent (gender-specific: `ils_dispy_male`, `ils_dispy_female`) | Disposable income |
| `ils_earns` | ✓ | ✓ | Earnings |
| `year` | ✓ (values: [2016]) | ✓ (values: [2016]) | Calendar year tag |
| `draw` | ✓ (min=0, max=99) | ✓ (min=0, max=99) | Draw index |
| `dwt` | ✓ | absent (gender-specific: `dwt_male`, `dwt_female`) | Design weight |
| `educ3` | ✓ | absent (couples uses gender-specific education vars) | Education (3-level) |
| `educL`, `educM`, `educH` | ✓ | absent (singles only) | Education dummies |

---

## 14. GSUR non-missingness

| Column | File | Non-zero rows | Missing | Mean |
| ------ | ---- | ------------- | ------- | ---- |
| `gsur` | Singles | 167,600 (100%) | 0 | 0.095206 |
| `gsur_male` | Couples | 257,700 (100%) | 0 | — |
| `gsur_female` | Couples | 257,700 (100%) | 0 | — |

Zero missing `gsur` in both files. The script log confirms: `GSUR merge (singles): filled 167400 rows using fallback age_group=Y20-64`.

---

## 15. Comparison to M1-clean operative FR_2016 files

The M1-clean verdict (`docs/RURO_occ_M1_clean_verdict_v1.md`) remains valid and unmodified. Its operative data is `fr_2016_RURO_mnl_GSURv2__{singles,couples}.parquet`, which is preserved unchanged on Z:. The new `v1gsurY2015` files are a **separate** MNL input set for the provisional multi-year pooled route only.

| Dimension | M1-clean operative (`GSURv2__`) | Pooled-route (`v1gsurY2015`) |
| --------- | -------------------------------- | ----------------------------- |
| GSUR opportunity year | 2016 (misaligned per rule; produced before rule adoption) | **2015** (correct, aligned) |
| GSUR source | `FR_gsur_ruro.parquet` v1, filtered to year=2016 | `FR_gsur_ruro.parquet` v1, filtered to year=2015 |
| Singles deciders | 1,676 | **1,676** (same) |
| Couples deciders | 2,577 | **2,577** (same) |
| Singles total rows | 167,600 | **167,600** (same) |
| Couples total rows | 257,700 | **257,700** (same) |
| Singles cols | 75 | **75** (same) |
| Couples cols | 93 | **93** (same) |
| Singles c_scale | 7,590.29 | **7,590.29** (identical) |
| Couples c_scale | 15,106.18 | **15,106.18** (identical) |
| Singles gsur mean | 0.092740 | 0.095206 (different — year=2015 rates) |
| File size singles | 21,510,188 bytes | 21,500,531 bytes (slightly smaller due to different float values) |

The M1-clean LL (−6487.5522) was estimated on the `GSURv2__` data and corresponds to year=2016 GSUR rates. The P3a pooled estimation will use the `v1gsurY2015` data; any future single-year FR_2016 estimation that re-uses the `v1gsurY2015` parquet would produce different LL and parameters from the M1-clean results.

---

## 16. Files not modified

| File | Status |
| ---- | ------ |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_GSURv2__singles.parquet` | **Untouched** — Z: canonical M1-clean operative |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_GSURv2__couples.parquet` | **Untouched** |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_GSURv2__mnlmeta.json` | **Untouched** |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet` | **Untouched** |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet` | **Untouched** |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | **Untouched** |
| `Z:\...\fr\2016\singles_RURO_ready_RURO_draws.parquet` | **Untouched** — reused as input |
| `Z:\...\fr\2016\couples_RURO_ready_RURO_draws.parquet` | **Untouched** — reused as input |
| `Z:\...\fr\2016\stijn_occ\scenarios\combined_draws_em.parquet` | **Untouched** — reused as input |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | **Untouched** — no code changes |
| `docs/RURO_occ_M1_clean_verdict_v1.md` | **Untouched** — verdict remains valid for GSURv2__ data |

---

## 17. What was not executed

| Action | Status |
| ------ | ------ |
| FR_2016 data prep (`enh_france_data_prep.py`) | NOT run |
| FR_2016 draw generation (`enh_RURO_draws.py`) | NOT run |
| FR_2016 EUROMOD (`enh_RURO_euromod.py`) | NOT run |
| Pooled stacking (live) | NOT run — dry-run only |
| P3a/P3b/P4 pooled parquets | NOT written |
| P2/P3 estimation | NOT run |
| Welfare computation | NOT run |
| M1-clean or M1-naive spec modification | NOT done |
| FR_2015 or FR_2017 pipeline | NOT re-run |

---

## 18. Whether FR_2016 is now opportunity-year aligned

**YES — FR_2016 is now opportunity-year aligned for the pooled-panel route.**

The `fr_2016_RURO_mnl_v1gsurY2015__` files use GSUR rates from v1 year=2015 as required by the alignment rule:

| Year | EUROMOD system | Correct opp. year | File | GSUR year used | Aligned? |
| ---- | -------------- | ----------------- | ---- | -------------- | -------- |
| 2015 | FR_2014 | 2014 | `fr_2015_RURO_mnl_v1gsurY2014__` | 2014 | ✓ |
| 2016 | FR_2015 | 2015 | `fr_2016_RURO_mnl_v1gsurY2015__` | **2015** | **✓** |
| 2017 | FR_2016 | 2016 | `fr_2017_RURO_mnl_v1gsurY2016__` | 2016 | ✓ |

All three years are now GSUR-opportunity-year-aligned. The misalignment identified in `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` §3 is resolved.

Cell-level verification of year=2015 (8 cells where year=2015 and year=2014 differ):

| Cell | Obs rate | v1 yr=2014 | v1 yr=2015 | v1 yr=2016 | Match yr=2015 |
| ---- | -------- | ---------- | ---------- | ---------- | ------------- |
| drgn1=1,dgn=0,educ3=2 | 0.0590 | 0.0690 | 0.0590 | — | ✓ |
| drgn1=1,dgn=0,educ3=1 | 0.1000 | 0.1010 | 0.1000 | — | ✓ |
| drgn1=1,dgn=1,educ3=2 | 0.0760 | 0.0710 | 0.0760 | — | ✓ |
| drgn1=2,dgn=1,educ3=2 | 0.0670 | 0.0460 | 0.0670 | — | ✓ |
| drgn1=2,dgn=1,educ3=1 | 0.1020 | 0.0930 | 0.1020 | — | ✓ |
| (3 additional cells) | — | no match | match | — | ✓ (×3) |

All 8 disambiguating cells match year=2015 and do not match year=2014 or year=2016.

Singles gsur mean: 0.095206. v1 year=2015 unweighted mean: 0.113449. (The observed sample mean differs from the GSUR table mean because the sample is not uniformly distributed across cells.)

---

## 19. Stage M1 dry-run result

```
======================================================================
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml
======================================================================

Inputs:
  [2015]  FOUND  ...\Data\processed\fr\fr_2015_RURO_mnl_v1gsurY2014__couples.parquet  (41.0 MB)
  [2016]  FOUND  ...\Data\processed\fr\fr_2016_RURO_mnl_v1gsurY2015__couples.parquet  (41.1 MB)
  [2017]  FOUND  ...\Data\processed\fr\fr_2017_RURO_mnl_v1gsurY2016__couples.parquet  (37.2 MB)

Planned output: ...\Data\processed\fr\pooled\fr_p3a_stacked_raw.parquet

Status: all inputs present -- ready to run without --dry-run

UID scheme (B=100,000,000,000):
  year=2015  tag=1  stacked range = [100,000,000,001 to 199,999,999,999]
  year=2016  tag=2  stacked range = [200,000,000,001 to 299,999,999,999]
  year=2017  tag=3  stacked range = [300,000,000,001 to 399,999,999,999]
```

- 2015: **FOUND** → `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` (GSUR opp. year 2014, aligned)
- 2016: **FOUND** → `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` (GSUR opp. year 2015, aligned) ← new file
- 2017: **FOUND** → `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` (GSUR opp. year 2016, aligned)

All three years resolve to GSUR-opportunity-year-aligned files. No previous misaligned `fr_2016_RURO_mnl_GSURv2__` file appears in the dry-run (local copy removed).

---

## 20. PASS / FAIL for FR_2016 corrected MNL-input readiness

| Check | Result |
| ----- | ------ |
| Stage 5 completed without errors | **PASS** |
| GSUR opportunity year 2015 applied (`--gsur-year 2015`) | **PASS** |
| Cell-level GSUR year=2015 confirmed (8 disambiguating cells) | **PASS** |
| Year=2016 rates not present (0.153 ≠ obs) | **PASS** |
| Zero missing `gsur` in singles | **PASS** |
| Zero missing `gsur_male` / `gsur_female` in couples | **PASS** |
| Singles: 167,600 rows × 75 cols, 1,676 deciders | **PASS** |
| Couples: 257,700 rows × 93 cols, 2,577 deciders | **PASS** |
| Draw uniformity (100 draws per decider) | **PASS** |
| All four UID columns present | **PASS** |
| Key variables present (dag, dgn, drgn1, ils_dispy, etc.) | **PASS** |
| Sidecar: all 7 alignment fields populated | **PASS** |
| Z: originals of `GSURv2__` untouched | **PASS** |
| Z: originals of draws and EUROMOD combined untouched | **PASS** |
| Local `GSURv2__` misaligned copies removed | **PASS** |
| Local mirror size-match: singles, couples, sidecar | **PASS** |
| Stage M1 P3a dry-run: 2015 FOUND | **PASS** |
| Stage M1 P3a dry-run: 2016 FOUND → v1gsurY2015 | **PASS** |
| Stage M1 P3a dry-run: 2017 FOUND | **PASS** |
| No pooled stacking run | **PASS** |
| No estimation run | **PASS** |
| No welfare computed | **PASS** |
| M1-clean verdict and operative files unchanged | **PASS** |

**All checks PASS. FR_2016 corrected MNL-input readiness: PASS.**

---

## 21. Exact next task

**Update the Stage M1 execution-readiness document to AUTHORIZED.**

All three pre-conditions identified in `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` §9 are now complete:

| Step | Status |
| ---- | ------ |
| 1. Rebuild FR_2016 with `--gsur-year 2015` → `v1gsurY2015` | ✓ DONE |
| 2. Patch sidecar with alignment fields | ✓ DONE |
| 3. Cell-level GSUR rate verification | ✓ DONE |
| 4. Copy to `Data/processed/fr/` | ✓ DONE |
| 5. Remove misaligned `GSURv2__` local copies | ✓ DONE |
| 6. Re-run dry-run, confirm 2016 resolves to `v1gsurY2015` | ✓ DONE |
| 7. This report | ✓ DONE |
| 8. Update `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | **PENDING** |

The exact next task is: **Update `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md`** to change the verdict from NOT AUTHORIZED to AUTHORIZED (provisional, v1-fallback, opportunity-year-aligned). The update should note that all three years are GSUR-opportunity-year-aligned under the v1 fallback, that Stage M1 P3a live stacking may proceed, and that outputs must carry the `provisional_v1_fallback_opportunity_year_aligned` label per `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` Decision 3.

---

*Prepared by pipeline execution. The FR_2016 GSUR-year-aligned MNL input is ready for use in the provisional multi-year pooled estimation route. The M1-clean single-year structural baseline is unaffected.*