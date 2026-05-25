# JMP Single-Year Replication — FR_2015 and FR_2017 Command Plan

**Document:** docs/JMP_single_year_replication_2015_2017_command_plan_v1.md
**Date:** 2026-05-19
**Author:** Hisham Haydar
**Status:** COMMAND PLAN — not an execution authorisation

---

## 1. Purpose

This document specifies the exact commands required to produce single-year MNL input
parquets for **FR_2015** and **FR_2017**, following the pipeline used for FR_2016. It also
documents the local-mirroring command to copy the canonical 2016 parquet from Z: to
the repo-local path that Stage M1 requires.

**Scope:** Data-engineering only. This plan covers the RURO-draws, EUROMOD, and
MNL-prep pipeline stages that produce the per-year `fr_{year}_RURO_mnl__{singles,couples}.parquet`
files required as inputs to `m1_stack_years.py`.

**This plan does NOT authorise execution.** Execution requires:
1. A separate authorisation document (`docs/JMP_single_year_replication_2015_2017_authorization_v1.md`),
   which does not yet exist. It must be written before any command in this plan is run.
2. EUROMOD outputs for FR_2015 and FR_2017 (not yet produced).
3. EU-SILC microdata files `FR_2015_a2.txt` and `FR_2017_a2.txt` accessible from Z:
   (confirmed present; see §4–5).

**Actions prohibited in all cases:**
- Do not overwrite `fr_2016_RURO_mnl_GSURv2__*.parquet` (canonical M1-clean operative files).
- Do not overwrite `fr_2016_RURO_mnl_job_gmm__*.parquet` (original 2016 stage-A parquets).
- Do not run pooled stacking (`m1_stack_years.py`) until all year parquets are present and authorised.
- Do not run estimation (`enh_RURO_estimate_FR.py`).
- Do not compute welfare.
- Do not update the Stage M1 execution-readiness report without explicit authorisation.

---

## 2. Files and Scripts Inspected

The following were read in constructing this plan:

| File | Purpose |
| ---- | ------- |
| `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | Execution-readiness verdict and open gaps |
| `Results/JMP_multi_year_stage_M1_readiness_addendum_v2.md` | tpr/twl clarification; Issue 3 recommendation |
| `Results/JMP_multi_year_external_assets_inventory_v1.md` | Eurostat/INSEE asset status |
| `Results/JMP_multi_year_EUROMOD_output_readiness_v1.md` | EUROMOD run status per year |
| `Results/JMP_multi_year_single_year_MNL_readiness_v1.md` | Local-path parquet status |
| `docs/France_case/_shared/governance/JMP_multi_year_CPI_HICP_source_decision_v1.md` | φ_t values adopted |
| `docs/France_case/P3a/execution_logs/multi_year_stage_M1/JMP_multi_year_stage_M1_implementation_plan_v2.md` | Condition table and input manifest |
| `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_occ_M1_clean_verdict_v1.md` | M1-clean specification; GSURv2 file names |
| `scripts/enhanced/enh_RURO_draws.py` | Draws argparse and defaults |
| `scripts/enhanced/enh_RURO_euromod.py` | EUROMOD argparse and metadata structure |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | MNL-prep argparse |
| `scripts/enhanced/enh_prepare_FR_gsur_v2.py` | GSURv2 year parameterization |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\` (directory listing) | Chronological 2016 pipeline artefacts |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | 2016 MNL sidecar (run 2026-02-19) |
| `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready_RURO_draws__drawsmeta.json` | 2016 draws sidecar (run 2026-05-13) |
| `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2016\stijn_occ\scenarios\combined_draws_em__euromodmeta.json` | EUROMOD system/dataset used for 2016 (run 2026-05-13) |

**Note:** `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` does **not exist** as of 2026-05-19. It must be created before any step in this plan is executed.

---

## 3. Existing 2016 Workflow (Reconstructed)

The canonical 2016 pipeline was executed in five stages across dates 2026-02-04 to 2026-05-17:

| Stage | Script | Run date | Key output on Z: |
| ----- | ------ | --------- | ---------------- |
| 0. Data prep | `enh_france_data_prep.py` | ~2026-02-04 | `outputs/prep/fr/2016/fr_2016_meta.json`, `fr_2016.parquet`, `fr_2016_singles.parquet`, `fr_2016_couples.parquet` |
| 1. RURO prep | `enh_RURO_prep.py` | ~2026-02-05 | `Data/processed/fr/2016/singles_RURO_ready.parquet`, `couples_RURO_ready.parquet` |
| 2. Draws | `enh_RURO_draws.py` | 2026-05-13 | `singles_RURO_ready_RURO_draws.parquet` + `__drawsmeta.json` |
| 3. EUROMOD | `enh_RURO_euromod.py` | 2026-05-13 | `interim/ruro/fr/2016/ruro_occ/scenarios/combined_draws_em.parquet` |
| 4. GSUR lookup | `enh_prepare_FR_gsur_v2.py` | 2026-05-17 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` (2016 only) |
| 5. MNL prep | `enh_RURO_prep_mnl_basic.py` | 2026-05-17 | `fr_2016_RURO_mnl_GSURv2__singles.parquet` + `couples.parquet` |

**Draws parameters used in the operative 2016 run (from drawsmeta 2026-05-13):**

| Parameter | Value |
| --------- | ----- |
| `n_draws` | 99 |
| `seed` | 17 |
| `wage_spec` | `vw` |
| `pi0_m`, `pi0_f` | 0.1 |
| `h_min`, `h_max` | 5.0, 70.0 |
| `w_min`, `w_max` | 2.0, 170.0 |
| `occ_spec` | `empirical` |
| `occ_strata` | `__all__` |
| `id_multiplier` | 1000 |

**EUROMOD system/dataset used (from euromodmeta 2026-05-13):**

| Parameter | Value |
| --------- | ----- |
| `--euromod-system` | `FR_2015` |
| `--euromod-dataset` | `FR_2016` |

**GSUR file used in canonical MNL prep:** `Data/external/FR_gsur_ruro_v2_stageA.parquet`
(2016-only GSURv2 lookup; 54 rows).

---

## 4. Required FR_2015 Inputs

| Input | Path | Status |
| ----- | ---- | ------ |
| EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` | **Present** |
| EUROMOD system | EUROMOD release (auto-resolved from storage root) | System `FR_2014` or `FR_2015` — **to confirm** |
| EUROMOD dataset name | To read from EUROMOD model for 2015 | **Unknown — confirm before run** |
| RURO-ready parquet | `Z:\...\Data\processed\fr\2015\singles_RURO_ready.parquet` | **Absent** (stages 0–1 not run) |
| RURO draws parquet | `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet` | **Absent** |
| EUROMOD combined output | `Z:\...\interim\ruro\fr\2015\{scenario}\scenarios\combined_draws_em.parquet` | **Absent** |
| GSUR file for 2015 | `Data/external/FR_gsur_ruro.parquet` (v1 fallback, rows for 2015 present) | **Present (v1)** |
| GSURv2 for 2015 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` extended to 2015 | **Absent** |
| Eurostat D2 denominators 2015 | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | **Absent** |
| Eurostat D1 denominators 2015 | `Data/external/lfst_r_lfp2acedu_FR_2015.tsv` | **Absent** |
| INSEE BDM benchmark 2015 | BDM series 001688526, annual average | **Absent** |

**Blocking gap:** EUROMOD outputs for FR_2015 do not exist. Stages 2–5 cannot run
until Stage 3 (EUROMOD) is completed. Stage 3 requires stages 0–1 (data prep, RURO prep).

---

## 5. Required FR_2017 Inputs

| Input | Path | Status |
| ----- | ---- | ------ |
| EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` | **Present** |
| EUROMOD system | `FR_2016` or `FR_2017` — **to confirm** | **Unknown** |
| EUROMOD dataset name | To read from EUROMOD model for 2017 | **Unknown — confirm before run** |
| RURO-ready parquet | `Z:\...\Data\processed\fr\2017\singles_RURO_ready.parquet` | **Absent** |
| RURO draws parquet | `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet` | **Absent** |
| EUROMOD combined output | `Z:\...\interim\ruro\fr\2017\{scenario}\scenarios\combined_draws_em.parquet` | **Absent** |
| GSUR file for 2017 | `Data/external/FR_gsur_ruro.parquet` (v1 fallback, rows for 2017 present) | **Present (v1)** |
| GSURv2 for 2017 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` extended to 2017 | **Absent** |
| Eurostat D2 denominators 2017 | `Data/external/lfst_r_lfsd2pop_FR_2017.tsv` | **Absent** |
| Eurostat D1 denominators 2017 | `Data/external/lfst_r_lfp2acedu_FR_2017.tsv` | **Absent** |
| INSEE BDM benchmark 2017 | BDM series 001688526, annual average | **Absent** |

---

## 6. First EUROMOD/Data-Prep Stage Commands (Stages 0–1)

These commands replicate the data-prep and RURO-prep stages for each year. They must be
run before draws or EUROMOD.

**Prerequisite:** Confirm the EUROMOD system code for each year by inspecting the EUROMOD
release directory before running. The 2016 run used `FR_2015`/`FR_2016`; for 2015 the
correct pair is likely `FR_2014`/`FR_2015`; for 2017 likely `FR_2016`/`FR_2017`.

### Stage 0 — France data prep (run once per year)

```powershell
# FR_2015
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_france_data_prep.py" `
    --year 2015 `
    --input "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt" `
    --out-dir "Z:\hisham\EUROMOD-STORAGE\outputs\prep\fr\2015"

# FR_2017
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_france_data_prep.py" `
    --year 2017 `
    --input "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt" `
    --out-dir "Z:\hisham\EUROMOD-STORAGE\outputs\prep\fr\2017"
```

*Note: Verify the exact CLI argument names for `enh_france_data_prep.py` before running;
the script was not read in this plan and the flags shown above are inferred from the
2016 artefact structure.*

### Stage 1 — RURO prep (run once per year)

```powershell
# FR_2015
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep.py" `
    --year 2015 `
    --input "Z:\hisham\EUROMOD-STORAGE\outputs\prep\fr\2015\fr_2015.parquet" `
    --out-dir "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015"

# FR_2017
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep.py" `
    --year 2017 `
    --input "Z:\hisham\EUROMOD-STORAGE\outputs\prep\fr\2017\fr_2017.parquet" `
    --out-dir "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017"
```

*Note: Verify CLI flags for `enh_RURO_prep.py` before running; the script was not read
in full in this plan.*

Expected outputs:
- `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready.parquet`
- `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready.parquet`
- (and corresponding files under `2017\`)

---

## 7. Draw-Generation Commands

Use the same parameters as the canonical 2016 run. The `--occ-spec empirical` and
`--rng-seed 17` values must match to ensure comparability across years.

```powershell
# FR_2015 — singles draws
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_draws.py" `
    --singles-path "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready.parquet" `
    --couples-path "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready.parquet" `
    --n-draws 99 `
    --wage-spec vw `
    --occ-spec empirical `
    --occ-strata __all__ `
    --pi0-m 0.1 `
    --pi0-f 0.1 `
    --h-min 5.0 `
    --h-max 70.0 `
    --w-min 2.0 `
    --w-max 170.0 `
    --rng-seed 17

# FR_2017 — singles draws
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_draws.py" `
    --singles-path "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready.parquet" `
    --couples-path "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\couples_RURO_ready.parquet" `
    --n-draws 99 `
    --wage-spec vw `
    --occ-spec empirical `
    --occ-strata __all__ `
    --pi0-m 0.1 `
    --pi0-f 0.1 `
    --h-min 5.0 `
    --h-max 70.0 `
    --w-min 2.0 `
    --w-max 170.0 `
    --rng-seed 17
```

Expected outputs:
- `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet` + `__drawsmeta.json`
- `Z:\...\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet` + `__drawsmeta.json`
- (and corresponding files under `2017\`)

---

## 8. Second RURO EUROMOD Pass Commands

The EUROMOD system and dataset names must be confirmed before running. The 2016 run used
`--euromod-system FR_2015 --euromod-dataset FR_2016`. The corresponding values for 2015
and 2017 must be inspected from the EUROMOD release directory.

**Likely values (to verify):**
- FR_2015: `--euromod-system FR_2014 --euromod-dataset FR_2015`
- FR_2017: `--euromod-system FR_2016 --euromod-dataset FR_2017`

```powershell
# FR_2015 — EUROMOD combined run
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --microdata-template "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt" `
    --euromod-system FR_2014 `
    --euromod-dataset FR_2015 `
    --scenario-dir "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios"

# FR_2017 — EUROMOD combined run
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --microdata-template "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt" `
    --euromod-system FR_2016 `
    --euromod-dataset FR_2017 `
    --scenario-dir "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\ruro_occ\scenarios"
```

Expected outputs:
- `Z:\...\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet` + `__euromodmeta.json`
- `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet` + `__euromodmeta.json`

---

## 9. Single-Year MNL-Input Parquet Construction Commands

These commands run `enh_RURO_prep_mnl_basic.py` for 2015 and 2017. Because GSURv2 is
not available for these years (see §16), the **v1 GSUR fallback** must be used and
outputs labelled accordingly (see §17).

The `--drawsmeta` flag enables automatic prior-parameter inheritance from the draws
sidecar, ensuring consistency with the draw-generation step.

```powershell
# FR_2015 — MNL prep (using v1 GSUR fallback)
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl" `
    --drawsmeta "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2015

# FR_2017 — MNL prep (using v1 GSUR fallback)
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl" `
    --drawsmeta "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2017
```

Expected outputs:
- `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__singles.parquet` + `__mnlmeta.json`
- `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__couples.parquet`
- (and corresponding files under `2017\`)

**The output file names intentionally omit the `GSURv2` segment** (they use the double
underscore convention `fr_{year}_RURO_mnl__` rather than `fr_{year}_RURO_mnl_GSURv2__`)
to distinguish them from future GSURv2-upgraded versions. See §17 for labelling policy.

---

## 10. Metadata Sidecar Handling

### drawsmeta JSON
`enh_RURO_draws.py` writes `{stem}__drawsmeta.json` in the same directory as the
draws parquet. Content fields: `n_draws`, `max_draw`, `seed`, `id_multiplier`,
`household_type`, `distributional_params` (all draw parameters), `input_file`,
`output_schema`, `timestamp`, `script`.

Pass the singles drawsmeta to `enh_RURO_prep_mnl_basic.py` via `--drawsmeta`. This
causes the MNL-prep script to inherit draw parameters automatically (overriding
`--wage-spec`, `--pi0-m`, etc. with values that match the actual draws).

### EUROMOD metadata
`enh_RURO_euromod.py` writes `combined_draws_em__euromodmeta.json` alongside the
combined output parquet. It records `system`, `dataset`, `n_rows`, `n_draws`,
`id_multiplier`, `carried_columns`, `timestamp`, `script`. Read this file after
the EUROMOD run to confirm the system/dataset combination was correctly applied.

### MNL metadata (mnlmeta)
`enh_RURO_prep_mnl_basic.py` writes `{out-base}__mnlmeta.json` with inputs,
prior parameters, sample sizes, normalization constants, and column lists. This
sidecar is the Stage M1 input-readiness record for each year. The Stage M1 script
`m1_stack_years.py` reads it to verify compatibility before stacking.

After running each year, confirm the mnlmeta JSON contains:
- `"script": "enh_RURO_prep_mnl_basic.py"`
- `"year": <year>`
- `"gsur_file"` pointing to the v1 file (not GSURv2)

---

## 11. 2016 Local Mirroring Command

The 2016 MNL parquet exists on Z: but is not present in the repo-local path
`Data/processed/fr/` that Stage M1 requires. This copy command must be run
**before** Stage M1 stacking.

Per addendum v2 §Issue 3 (Option L): copy files locally; do not change the YAML
`input_parquet_dir`. The Z: originals are retained as the authoritative storage copy.

```powershell
# Copy 2016 MNL input parquets to repo-local Stage M1 input directory
Copy-Item `
    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet" `
    "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\"

Copy-Item `
    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet" `
    "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\"

Copy-Item `
    "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json" `
    "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\"
```

**Note on the 2016 file choice:** The command above copies `fr_2016_RURO_mnl_job_gmm__`
(the Stage-A parquet from 2026-02-19, which uses the v1 GSUR). An alternative is to copy
`fr_2016_RURO_mnl_GSURv2__` (the M1-clean canonical). The choice must be made explicitly
before Stage M1 is run: mixing GSURv2 for 2016 with v1 GSUR for 2015/2017 introduces an
asymmetry. See §17 for the labelling and consistency policy.

---

## 12. Output Paths for 2015

All outputs are written to Z: during pipeline execution and then copied to repo-local for
Stage M1.

| Stage | Output path (Z:) | Description |
| ----- | ---------------- | ----------- |
| Prep | `Z:\...\outputs\prep\fr\2015\fr_2015.parquet` | Cleaned individual-level dataset |
| RURO-ready | `Z:\...\Data\processed\fr\2015\singles_RURO_ready.parquet` | Singles RURO input |
| RURO-ready | `Z:\...\Data\processed\fr\2015\couples_RURO_ready.parquet` | Couples RURO input |
| Draws | `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet` | Long draws (singles) |
| Draws | `Z:\...\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet` | Long draws (couples) |
| Draws | `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json` | Draws sidecar |
| EUROMOD | `Z:\...\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet` | EUROMOD output |
| EUROMOD | `Z:\...\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em__euromodmeta.json` | EUROMOD sidecar |
| MNL prep | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__singles.parquet` | MNL input (pre-GSURv2) |
| MNL prep | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__couples.parquet` | MNL input (pre-GSURv2) |
| MNL prep | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__mnlmeta.json` | MNL sidecar |
| Stage M1 (repo-local) | `Data/processed/fr/fr_2015_RURO_mnl__singles.parquet` | Copied from Z: for M1 |
| Stage M1 (repo-local) | `Data/processed/fr/fr_2015_RURO_mnl__couples.parquet` | Copied from Z: for M1 |

---

## 13. Output Paths for 2017

| Stage | Output path (Z:) | Description |
| ----- | ---------------- | ----------- |
| Prep | `Z:\...\outputs\prep\fr\2017\fr_2017.parquet` | Cleaned individual-level dataset |
| RURO-ready | `Z:\...\Data\processed\fr\2017\singles_RURO_ready.parquet` | Singles RURO input |
| RURO-ready | `Z:\...\Data\processed\fr\2017\couples_RURO_ready.parquet` | Couples RURO input |
| Draws | `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet` | Long draws (singles) |
| Draws | `Z:\...\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet` | Long draws (couples) |
| Draws | `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json` | Draws sidecar |
| EUROMOD | `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet` | EUROMOD output |
| EUROMOD | `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em__euromodmeta.json` | EUROMOD sidecar |
| MNL prep | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__singles.parquet` | MNL input (pre-GSURv2) |
| MNL prep | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__couples.parquet` | MNL input (pre-GSURv2) |
| MNL prep | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__mnlmeta.json` | MNL sidecar |
| Stage M1 (repo-local) | `Data/processed/fr/fr_2017_RURO_mnl__singles.parquet` | Copied from Z: for M1 |
| Stage M1 (repo-local) | `Data/processed/fr/fr_2017_RURO_mnl__couples.parquet` | Copied from Z: for M1 |

---

## 14. Output Paths for Mirrored 2016

The canonical 2016 parquet on Z: is copied to the repo-local Stage M1 input directory.
No new 2016 pipeline runs are made.

| Source (Z:) | Destination (repo-local) | Notes |
| ----------- | ------------------------ | ----- |
| `Z:\...\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__singles.parquet` | Stage M1 key: `fr_2016_RURO_mnl_job_gmm` |
| `Z:\...\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__couples.parquet` | |
| `Z:\...\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | Sidecar for M1 validation |

The M1 YAML key for 2016 is `fr_2016_RURO_mnl_job_gmm`, which matches the file-name
stem. The Stage M1 script discovers files by scanning for parquets whose stem begins
with the key; the sidecar JSON is auto-detected.

---

## 15. Versioning and No-Overwrite Rules

1. **Canonical 2016 files must not be overwritten.** The files
   `fr_2016_RURO_mnl_GSURv2__singles.parquet` and `fr_2016_RURO_mnl_GSURv2__couples.parquet`
   are the M1-clean operative files (RURO_occ_M1_clean_verdict_v1.md). No script in this
   plan writes to those paths.

2. **`fr_2016_RURO_mnl_job_gmm__` files must not be overwritten.** These are the
   original Stage-A parquets, the source for the local-mirror copy in §11.

3. **New 2015 and 2017 parquets use the naming stem `fr_{year}_RURO_mnl__`** (double
   underscore, no GSURv2 segment). This distinguishes them from any future GSURv2-upgraded
   versions. If GSURv2 is later extended to 2015/2017 (see §16), the upgraded files would
   be named `fr_{year}_RURO_mnl_GSURv2__singles.parquet`.

4. **The Z: originals are retained.** Copying to repo-local `Data/processed/fr/` does not
   delete or modify the Z: files. The Z: path is the authoritative storage copy.

5. **Parquet files are git-ignored.** The repo's `.gitignore` excludes large binaries from
   `Data/processed/`. Sidecar JSON files (`__mnlmeta.json`, `__drawsmeta.json`) may be
   committed if small (< 1 MB).

---

## 16. GSURv2 Year-Parameterization Status

**Current script state:** `scripts/enhanced/enh_prepare_FR_gsur_v2.py` has
`YEAR = 2016` hard-coded at line 44. It accepts no `--year` CLI argument and writes
only to `Data/external/FR_gsur_ruro_v2_stageA.parquet` (2016 rates only; 54 rows).

**To run GSURv2 for 2015 and 2017**, the script requires modification:

1. Add a `--year` CLI argument (e.g., `argparse` `--year`, default 2016).
2. Add a `--tsv-d2` and `--tsv-d1` argument to point at the year-specific Eurostat TSV files.
3. Add a `--benchmark-pct` argument (or read the year-specific INSEE BDM value).
4. Change the output path to be year-parameterized:
   `Data/external/FR_gsur_ruro_v2_stageA_{year}.parquet`.

**Upstream prerequisites for GSURv2 2015/2017:**
- Eurostat `lfst_r_lfsd2pop_FR_{year}.tsv` — **absent** for 2015 and 2017.
- Eurostat `lfst_r_lfp2acedu_FR_{year}.tsv` — **absent** for 2015 and 2017.
- INSEE BDM 001688526 annual average for 2015 and 2017 — **absent**.

**Neither the script modification nor the upstream downloads are authorised by this
plan.** They are identified here as the blocking gap for GSURv2 in 2015/2017.

---

## 17. Non-GSURv2 Fallback Labelling Rule

When `enh_RURO_prep_mnl_basic.py` is run for FR_2015 or FR_2017 with
`--gsur-file Data/external/FR_gsur_ruro.parquet` (the v1 lookup), the resulting
parquets are:

- **Pre-GSURv2 / not final for pooled estimation.**
- They may be used for single-year diagnostics, dry-run Stage M1 checks, and
  sample-size validation.
- They must **not** be used as inputs for the final pooled P3a estimation.

**Labelling rule:** Use the file-name stem `fr_{year}_RURO_mnl__` (no `GSURv2` segment).
Do not name these files `fr_{year}_RURO_mnl_GSURv2__`. Reserve that naming convention for
future runs that use extended GSURv2 rates.

**MNL sidecar annotation:** After running MNL prep, manually add or confirm the following
field in the `__mnlmeta.json` sidecar:

```json
"gsur_version": "v1_fallback",
"gsur_note": "Pre-GSURv2 / not final for pooled estimation. GSURv2 rates for this year require Eurostat denominator acquisition."
```

**YAML cross-reference:** The Stage M1 YAML for P3a (`config/fr_p3a_stage_m1.yaml`) should
reference the final GSURv2-upgraded parquets when available, not the v1-fallback versions.
Using v1-fallback parquets in a P3a production run is not authorised.

---

## 18. CPI/HICP Handling

The CPI/HICP harmonisation step occurs in Stage M1 (`m1_harmonise_cpi.py`), not in
the single-year pipeline described here. This plan does not run harmonisation.

**For reference:** The adopted φ_t values (EUROMOD HICP, Option B, provisional) are:

| Year | φ_t |
| ---- | --- |
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |

Source: `Data/external/cpi_hicp_fr_harmonisation.csv`.
Decision memo: `docs/France_case/_shared/governance/JMP_multi_year_CPI_HICP_source_decision_v1.md`.
Addendum v2 §Issue 1: these values are execution-ready but provisional. If INSEE IPC is
later retrieved and any φ_t differs by ≥ 0.5 pp, the CSV must be rewritten and all
harmonised parquets rebuilt.

The single-year MNL parquets produced by this plan contain nominal income variables.
CPI deflation is applied only at the M1 harmonisation step, not during MNL prep.

---

## 19. Validation Checks After Each Year

After completing all five stages for each year, perform the following checks before
copying parquets to the repo-local Stage M1 input directory.

### Check A — drawsmeta consistency

```python
import json
dm = json.load(open("...singles_RURO_ready_RURO_draws__drawsmeta.json"))
assert dm["n_draws"] == 99
assert dm["distributional_params"]["wage_spec"] == "vw"
assert dm["distributional_params"]["occ_spec"] == "empirical"
assert dm["distributional_params"]["h_min"] == 5.0
assert dm["distributional_params"]["h_max"] == 70.0
assert dm["distributional_params"]["w_min"] == 2.0
assert dm["distributional_params"]["w_max"] == 170.0
```

### Check B — EUROMOD metadata

```python
em = json.load(open("...combined_draws_em__euromodmeta.json"))
assert em["script"] == "enh_RURO_euromod.py"
assert "id_multiplier" in em
# Confirm system and dataset match expected year pair
print(f"System: {em['system']}, Dataset: {em['dataset']}")
```

### Check C — MNL parquet row counts

```python
import pandas as pd
s = pd.read_parquet("...fr_{year}_RURO_mnl__singles.parquet")
# Confirm n_draws = 99, draw counts uniform
assert s["draw"].nunique() == 100  # draws 0..99
n_deciders = (s["draw"] == 0).sum()
print(f"Singles deciders: {n_deciders}")  # expect ~1,600–1,700 for 2015; ~1,500–1,700 for 2017
```

### Check D — tpr/twl annotation

After building 2015 and 2017 parquets, confirm non-zero counts match expected values:

| Year | Variable | Expected non-zero rows (RURO sample) |
| ---- | -------- | ------------------------------------ |
| 2015 | `tpr` | ≤ 55 rows (raw-file incidence 0.344% WA; RURO sample is a subset) |
| 2016 | `twl` | ≤ 55 rows (raw-file incidence 0.286% WA) |
| 2017 | `twl` | ≤ 55 rows (raw-file incidence 0.295% WA) |

If any year's count exceeds 1% of the RURO sample, escalate to a formal comparability
check before Stage M1 execution. (Per addendum v2 §Issue 2.)

### Check E — pre-copy verification

Before copying to `Data/processed/fr/`:

```powershell
# Confirm no existing file will be overwritten
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2015_RURO_mnl__singles.parquet"
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2017_RURO_mnl__singles.parquet"
# Both should return False before first copy
```

---

## 20. Expected Reports to Create

After execution is complete and before Stage M1 is run, create the following documents:

| Report | Location | Content |
| ------ | -------- | ------- |
| Single-year execution log (2015) | `Results/JMP_FR_2015_single_year_pipeline_log_v1.md` | EUROMOD system/dataset used, sample sizes, drawsmeta digest, validation check outcomes |
| Single-year execution log (2017) | `Results/JMP_FR_2017_single_year_pipeline_log_v1.md` | Same structure as 2015 log |
| tpr/twl annotation | `Results/M1_identity_validation_summary.md` §tpr/twl | Per-year non-zero counts for `tpr` and `twl` in the RURO sample; match against addendum v2 expected values |
| Stage M1 readiness update | Addendum to `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | Re-run dry-run checks with parquets in place; update "NOT AUTHORIZED" verdict if all gaps closed |

These reports are required before the Stage M1 execution-readiness verdict can be updated
from "NOT AUTHORIZED" to "AUTHORIZED."

---

## 21. Execution Readiness Verdict

**Single-year replication of FR_2015 and FR_2017 is NOT AUTHORIZED as of 2026-05-19.**

Blocking reasons:

| # | Gap | Required action |
|---|-----|----------------|
| 1 | Authorization document absent | Create `docs/JMP_single_year_replication_2015_2017_authorization_v1.md` |
| 2 | EUROMOD not run for FR_2015 | Run stages 0–3 for 2015 |
| 3 | EUROMOD not run for FR_2017 | Run stages 0–3 for 2017 |
| 4 | EUROMOD system/dataset for 2015 and 2017 unconfirmed | Inspect EUROMOD release directory before running |
| 5 | GSURv2 not available for 2015/2017 | Either acquire Eurostat denominators + INSEE benchmarks and extend `enh_prepare_FR_gsur_v2.py`, or accept v1 fallback with labelling rule in §17 |

Non-blocking items (handled by this plan):

- 2016 local mirroring: command documented in §11; ready to execute once authorisation exists.
- v1 GSUR fallback: acceptable for staging and dry-run; labelling rule in §17 prevents
  its use in a production P3a run.
- CPI/HICP values: adopted (φ_t present in CSV); applied at Stage M1, not here.

**Once the authorization document is written and EUROMOD outputs for FR_2015 and FR_2017
are in hand, the commands in §6–§9 can be run sequentially to unblock Stage M1.**