# JMP Single-Year FR_2015 — GSUR Opportunity-Year-Aligned Rebuild Report v1

**Document:** Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md  
**Date:** 2026-05-20  
**Author:** Pipeline execution via Claude Code  
**Authorization:** `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` (Decision 1)  
**Script:** `scripts/enhanced/enh_RURO_prep_mnl_basic.py`  
**Output stem:** `fr_2015_RURO_mnl_v1gsurY2014`

---

## 1. Purpose

This report documents the rebuild of the FR_2015 MNL-input parquets using the
correct GSUR opportunity year (2014), replacing the previously misaligned parquets
that had keyed GSUR rates to the survey data year (2015). The rebuild is authorized
by `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md` Decision 1 and required by the
opportunity-year alignment rule formalized in
`docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` §2.

---

## 2. Authorization and scope

**Authorized action (Decision 1):** Rebuild the FR_2015 MNL-input parquet using
GSUR year=2014 from `FR_gsur_ruro.parquet` (v1 fallback). Source file is
`Data/external/FR_gsur_ruro.parquet`.

**Scope of this task:**
- Re-run only `enh_RURO_prep_mnl_basic.py` (Stage 5) for FR_2015.
- Reuse existing draws and EUROMOD combined outputs from Z: (no re-run of upstream stages).
- Write to a versioned output stem (`fr_2015_RURO_mnl_v1gsurY2014`) — do NOT overwrite
  the prior misaligned `fr_2015_RURO_mnl__` files on Z:.
- Patch sidecar with `gsur_version`, `gsur_opportunity_year`, and alignment fields.
- Copy rebuilt files to `Data/processed/fr/`.
- Remove old misaligned local copies so Stage M1 stacker picks only the aligned files.

**Not authorized (this task):** re-run data prep, draws, or EUROMOD; run FR_2017;
pooled estimation; GSURv2 year parameterization.

---

## 3. Input files used

All inputs reused from the original FR_2015 replication without modification.

| Input | Path | Status |
|-------|------|--------|
| Singles draws | `Z:\...\fr\2015\singles_RURO_ready_RURO_draws.parquet` | Present (13.2 MB) |
| Couples draws | `Z:\...\fr\2015\couples_RURO_ready_RURO_draws.parquet` | Present (35.7 MB) |
| EUROMOD combined | `Z:\...\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet` | Present (493.9 MB, 1,086,700 rows) |
| Draws metadata | `Z:\...\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json` | Present |
| GSUR lookup | `Data/external/FR_gsur_ruro.parquet` | Present (2,160 rows, years 2007–2024) |

GSUR year 2014 confirmed present: 120 rows covering all `(drgn1, dgn, educ3)` key
combinations. See `docs/France_case/RURO_prep_mnl_gsur_year_support_report_v1.md` §6.

---

## 4. Script version and patch

`enh_RURO_prep_mnl_basic.py` was patched with `--gsur-year` support prior to this
rebuild, per `docs/France_case/RURO_prep_mnl_gsur_year_support_report_v1.md`. Three edits were
applied:

1. **Argparse**: new `--gsur-year <int>` flag (default `None`).
2. **GSUR load section**: after loading the lookup file, filter to `args.gsur_year`
   rows, then overwrite `gsur_df["year"] = args.year` so the merge key
   `(year, drgn1, dgn, educ3)` resolves against the draws data year.
3. **Metadata sidecar**: four new fields written when `--gsur-year` is supplied:
   `gsur_data_year`, `gsur_alignment_rule`, `gsur_alignment_status`, `gsur_note`.

The patch was fully tested (6 unit tests, all PASS) before this rebuild.

---

## 5. Command executed

```powershell
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "\\crc\users\hisham\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base         "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_v1gsurY2014" `
    --drawsmeta        "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file        "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --gsur-year 2014 `
    --year 2015
```

Run completed successfully with exit code 0. No errors or warnings (one
`DeprecationWarning` about `datetime.utcnow()` — pre-existing, not related to this
task).

---

## 6. GSUR filtering log

The script emitted:

```
Loaded GSUR lookup: 2,160 rows
GSUR filtered to opportunity year 2014: 120 rows
GSUR lookup year column set to data year 2015 for merge-key alignment (opportunity year: 2014).
```

After filtering, `gsur_df["year"]` was overwritten to 2015 (data year) so the merge
key `(year, drgn1, dgn, educ3)` resolves against the draws data. The opportunity-year
selection (2014) is recorded in sidecar metadata, not in the merge key.

GSUR merge statistics from the run:

- Singles: `filled 166700 rows using fallback age_group=Y20-64`
- Couples male: `filled 256500 rows using fallback age_group=Y20-64`
- Couples female: `filled 256500 rows using fallback age_group=Y20-64`

Zero missing `gsur` in both singles and couples output.

---

## 7. Output file shapes and sizes

| File | Rows | Columns | Size |
|------|------|---------|------|
| `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | 166,900 | 75 | 20.5 MB |
| `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | 256,600 | 93 | 41.0 MB |
| `fr_2015_RURO_mnl_v1gsurY2014__mnlmeta.json` | — | — | ~59 KB |

Row counts are identical to the misaligned predecessor:
- Singles: 166,900 (1,669 decider households × 100 draws)
- Couples: 256,600 (2,566 decider households × 100 draws)

Column counts match the prior run (75 singles, 93 couples — post column-filter).

---

## 8. GSUR rate verification

Cell-level check at `(drgn1=8, dgn=0, educ3=2)` (first row of singles):

| Source | gsur rate |
|--------|-----------|
| `FR_gsur_ruro.parquet` year=2014, cell (8, 0, 2) | 0.061000 |
| `FR_gsur_ruro.parquet` year=2015, cell (8, 0, 2) | 0.052000 |
| New singles parquet, row 0 | **0.061000** (exact match to year=2014) |
| Old misaligned singles parquet, row 0 | 0.052000 (was year=2015) |

The cell-level check confirms the new parquet uses year=2014 rates exactly.

**Aggregate comparison:**

| Metric | Old (year=2015 keyed) | New (year=2014 keyed) |
|--------|----------------------|-----------------------|
| Singles gsur mean | 0.095492 | **0.094059** |
| Mean difference | — | −0.001433 |
| Rows where gsur changed | — | 164,300 / 166,900 (98.4%) |
| Missing gsur | 0 | **0** |

The mean GSUR rate decreased by 0.0014 (approximately 1.5 percentage points relative
to the prior value of ~0.095). This is consistent with the year=2014 v1 rates being
slightly lower than year=2015 rates in the FR region mix of the estimation sample.
98.4% of rows have different rates — only rows where the 2014 and 2015 table values
happen to coincide are unchanged.

---

## 9. Year-key alignment mechanism

**Problem:** After filtering `gsur_df` to `year=2014`, the merged lookup has
`year=2014` in its year column. The draws data carries `year=2015`. The merge key
`(year, drgn1, dgn, educ3)` would find no matches (100% missing gsur) without
correction.

**Fix applied (Edit 2 of the `--gsur-year` patch):** After filtering, the script
overwrites `gsur_df["year"] = args.year` (= 2015) so the merge key resolves
correctly. The year=2014 selection is preserved in sidecar metadata
(`gsur_opportunity_year: 2014`), not in the merge key. This is the correct
interpretation: the opportunity year controls *which rates* are used, while the
data year controls the merge key alignment.

**Verification:** 0 missing `gsur` in both singles and couples; rates match the
year=2014 table at the cell level.

---

## 10. Sidecar fields written

The `__mnlmeta.json` sidecar contains all prior fields plus the following
GSUR-alignment fields:

| Field | Value |
|-------|-------|
| `year` | `2015` |
| `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| `gsur_opportunity_year` | `2014` |
| `gsur_alignment_status` | `aligned` |
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` |
| `gsur_data_year` | `2015` |
| `gsur_note` | `GSUR filtered to opportunity year 2014 (EUROMOD system year) before merge. Data year: 2015. v1_fallback_opportunity_year_aligned / not final for pooled estimation until GSURv2 opportunity-year-aligned rates are available.` |

Fields `gsur_version` and `gsur_opportunity_year` were added by post-run sidecar
patch (not auto-written by the script). Fields `gsur_data_year`, `gsur_alignment_rule`,
`gsur_alignment_status`, and `gsur_note` are auto-written by Edit 3 of the
`--gsur-year` patch when the flag is supplied.

The sidecar timestamp is `2026-05-19T23:23:36.058450Z` (UTC, from the script run).

---

## 11. Z: storage

Output files written by the script to Z: (canonical storage):

```
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_v1gsurY2014__singles.parquet
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_v1gsurY2014__couples.parquet
Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl_v1gsurY2014__mnlmeta.json
```

The prior misaligned files (`fr_2015_RURO_mnl__*.parquet`,
`fr_2015_RURO_mnl__mnlmeta.json`) remain on Z: **unchanged** and must not enter any
pooled estimation run. Their sidecars carry `gsur_alignment_status: misaligned`.

---

## 12. Local mirror (Data/processed/fr/)

Three files copied from Z: to `Data/processed/fr/`. SIZE_MATCH confirmed for all
three:

| File | Size |
|------|------|
| `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | 21,467,197 bytes |
| `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | 42,977,905 bytes |
| `fr_2015_RURO_mnl_v1gsurY2014__mnlmeta.json` | 60,597 bytes |

**Old misaligned local copies removed:** The three old local files
(`fr_2015_RURO_mnl__singles.parquet`, `fr_2015_RURO_mnl__couples.parquet`,
`fr_2015_RURO_mnl__mnlmeta.json`) were removed from `Data/processed/fr/` to
prevent the Stage M1 stacker from picking them (see §13). Their Z: originals are
untouched.

---

## 13. Stage M1 glob conflict resolution

`m1_stack_years.py` uses glob pattern `*{year}*RURO*mnl*.parquet` and returns
`candidates[0]` (alphabetical first). Both the old stem (`fr_2015_RURO_mnl__`) and
the new stem (`fr_2015_RURO_mnl_v1gsurY2014__`) match for year=2015. Alphabetically,
`fr_2015_RURO_mnl__` sorts before `fr_2015_RURO_mnl_v1gsurY2014__`, so the stacker
would have picked the misaligned file had both been present.

**Resolution:** Old misaligned local copies removed from `Data/processed/fr/`. After
removal, only the aligned `v1gsurY2014` files are present locally for 2015.

Stage M1 P3a dry-run confirms:

```
[2015]  FOUND  .../fr_2015_RURO_mnl_v1gsurY2014__couples.parquet  (41.0 MB)
[2016]  FOUND  .../fr_2016_RURO_mnl_GSURv2__couples.parquet  (41.1 MB)
[2017]  NOT FOUND
Status: BLOCKED -- one or more inputs missing
```

2015 is now FOUND with the aligned file. P3a remains BLOCKED on 2017 only.

---

## 14. Sanity checks passed

All script-internal sanity checks passed during the run:

| Check | Singles | Couples |
|-------|---------|---------|
| Required columns present | PASS | PASS |
| No missing values in `(idhh, draw, consumption, leisure)` | PASS | PASS |
| All consumption and leisure values positive | PASS | PASS |
| Draw counts valid (all HHs have 100 draws) | PASS | PASS |
| Consumption variance nonzero | PASS (std=5946.85) | PASS (std=8460.71) |
| Leisure variance nonzero | PASS (std=21.02) | PASS (std=21.00) |
| Couples gender balance | — | PASS (all 256,600 HH-draws have 1M+1F) |

---

## 15. Normalization parameters

| Parameter | Singles | Couples |
|-----------|---------|---------|
| `c_scale` | 7,565.57 | 15,189.22 |
| `l_scale` | 10.00 | — |
| `l_male_scale` | — | 10.00 |
| `l_female_scale` | — | 10.00 |
| `n_chosen` (deciders) | 1,669 | 2,566 |

These match the original FR_2015 replication values. GSUR year correction does not
affect normalization parameters (normalization uses consumption and leisure draws,
not GSUR rates).

---

## 16. Backward compatibility

No existing code paths were modified by the `--gsur-year` patch. When `--gsur-year`
is omitted, the script behaves identically to the pre-patch version (full GSUR file
passed to merge functions; year keyed from draws data). The 2016 M1-clean run and all
other existing invocations are unaffected.

Prior behavior: confirmed by unit test 4 (`--gsur-year` omitted → no filter applied;
backward compat PASS).

---

## 17. What this rebuild does not change

- **FR_2016:** Not rebuilt. Uses GSURv2 stageA rates (year=2016 hardcoded). Sidecar
  provenance mismatch (cites v1 file, used v2 stageA rates) is documented but not
  resolved. Decision 4 in the alignment memo requires GSURv2 for opportunity year 2015
  before FR_2016 can be promoted to final status.
- **FR_2017:** Not run. Requires EUROMOD FR_2017 execution first (gap 2, still open).
  Will use `--gsur-year 2016 --year 2017` per command plan addendum §4 Option A.
- **Prior misaligned FR_2015 on Z::** Not deleted. Retained for provenance. Sidecar
  carries `gsur_alignment_status: misaligned`. Must not enter pooled estimation.
- **GSURv2:** Not affected. GSURv2 extension to years 2014 and 2015 remains out of
  scope (requires Eurostat denominator acquisition and INSEE BDM retrieval).

---

## 18. Labelling policy

All outputs from this rebuild carry:

- Filename: `fr_2015_RURO_mnl_v1gsurY2014__*` (stem encodes GSUR source and
  opportunity year)
- Sidecar: `gsur_version: v1_fallback_opportunity_year_aligned`
- Sidecar: `gsur_opportunity_year: 2014`
- Sidecar: `gsur_alignment_status: aligned`

These outputs are **pre-GSURv2** and **not final for pooled estimation** per Decision 3
and Decision 4 of `docs/France_case/JMP_GSUR_year_alignment_decision_v1.md`. They may be used
for Stage M1 provisional dry-run under the `provisional_v1_fallback` label once FR_2017
is available.

---

## 19. Gates passed

| Gate | Status |
|------|--------|
| Authorization memo exists (`JMP_GSUR_year_alignment_decision_v1.md` Decision 1) | PASS |
| `--gsur-year` flag present in script argparse | PASS |
| GSUR year=2014 present in v1 file (120 rows) | PASS |
| Script run completed without errors | PASS |
| Zero missing gsur in singles | PASS |
| Zero missing gsur in couples | PASS |
| Cell-level rate check: new parquet matches year=2014 table exactly | PASS |
| Sidecar fields: `gsur_version`, `gsur_opportunity_year`, `gsur_alignment_status` | PASS |
| Z: output files written (SIZE_MATCH) | PASS |
| Local mirror copied (SIZE_MATCH, all 3 files) | PASS |
| Old misaligned local copies removed | PASS |
| Stage M1 P3a dry-run: 2015 FOUND with aligned file | PASS |

---

## 20. Next steps

| Step | Status | Required action |
|------|--------|-----------------|
| FR_2017 EUROMOD run | BLOCKED | Run 5-stage pipeline per `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`; EUROMOD must execute with system=FR_2016, dataset=FR_2017_a2 |
| FR_2017 MNL prep | BLOCKED on EUROMOD | After EUROMOD: run `enh_RURO_prep_mnl_basic.py` with `--gsur-year 2016 --year 2017` per command plan addendum §4 |
| Stage M1 P3a dry-run (all 3 years FOUND) | BLOCKED on FR_2017 | Mirror FR_2017 parquets to `Data/processed/fr/` then re-run dry-run |
| Stage M1 P3a live run | BLOCKED on FR_2017 + authorization | Requires new execution-readiness authorization once all three years present |
| FR_2016 sidecar provenance correction | Not blocked | Document actual GSURv2 stageA source file in sidecar; does not require data rebuild |
| GSURv2 extension to years 2014 and 2015 | Out of scope | Requires Eurostat denominators + INSEE BDM retrieval; prerequisite for final pooled build |

**Immediate unblocking path:** Execute FR_2017 single-year replication (5 stages)
per `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`, citing
`docs/JMP_single_year_replication_2015_2017_command_plan_addendum_v1.md` for the
`--gsur-year 2016` correction. Then mirror to `Data/processed/fr/` and confirm
Stage M1 P3a dry-run returns all three years FOUND.