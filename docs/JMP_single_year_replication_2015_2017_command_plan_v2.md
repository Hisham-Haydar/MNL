# JMP Single-Year Replication — FR_2015 and FR_2017 Command Plan v2

**Document:** docs/JMP_single_year_replication_2015_2017_command_plan_v2.md
**Date:** 2026-05-19
**Author:** Hisham Haydar
**Supersedes:** docs/JMP_single_year_replication_2015_2017_command_plan_v1.md
**Revision summary:** CLI arguments corrected against actual script argparse definitions
and `run_enhanced_pipeline.ps1`. v1 used inferred flags (`--input`, `--year/--input`
for `enh_RURO_prep.py`) that do not exist. EUROMOD preflight check added as a mandatory
gate before Step 4. All other content (paths, prohibitions, labelling rules, validation
checks) is preserved from v1 with minor clarifications.

---

## 1. Purpose

This document specifies the exact commands required to produce single-year MNL input
parquets for **FR_2015** and **FR_2017**, following the pipeline used for FR_2016. It also
documents the local-mirroring command to copy the canonical 2016 parquet from Z: to
the repo-local path that Stage M1 requires.

**Scope:** Data-engineering only. This plan covers the five-stage pipeline that produces
the per-year `fr_{year}_RURO_mnl__{singles,couples}.parquet` files required as inputs
to `m1_stack_years.py`.

**Execution requires prior authorisation.**
`docs/JMP_single_year_replication_2015_2017_authorization_v1.md` must exist and be
accepted before any command in this plan is run. That document now exists (created
2026-05-19).

**Actions prohibited in all cases:**
- Do not overwrite `fr_2016_RURO_mnl_GSURv2__*.parquet` (canonical M1-clean files).
- Do not overwrite `fr_2016_RURO_mnl_job_gmm__*.parquet` (source for 2016 local mirror).
- Do not run pooled stacking (`m1_stack_years.py`).
- Do not run estimation (`enh_RURO_estimate_FR.py`).
- Do not compute welfare.
- Do not run EUROMOD (Step 4) before completing the mandatory preflight check (§8).

---

## 2. Files and Scripts Inspected

| File | Purpose |
| ---- | ------- |
| `docs/JMP_single_year_replication_2015_2017_command_plan_v1.md` | Prior version; source of corrections |
| `scripts/enhanced/run_enhanced_pipeline.ps1` | Authoritative source for actual CLI calls to each script |
| `scripts/enhanced/enh_france_data_prep.py` (argparse, lines 2460–2552) | Confirmed: `--year`, `--raw-dir`, `--raw-filename`, `--out-dir`, `--system-year`, `--export-format` |
| `scripts/enhanced/enh_RURO_prep.py` (argparse, lines 1284–1319) | Confirmed: `--processed-dir`, `--base-year`, `--export-format` |
| `scripts/enhanced/enh_RURO_draws.py` (argparse, lines 1362–1453) | Confirmed: `--singles-path`, `--couples-path`, `--n-draws`, `--wage-spec`, `--occ-spec`, `--occ-strata`, `--pi0-m`, `--pi0-f`, `--h-min`, `--h-max`, `--w-min`, `--w-max`, `--rng-seed` |
| `scripts/enhanced/enh_RURO_euromod.py` (argparse, lines 1135–1146) | Confirmed: `--singles-draws`, `--couples-draws`, `--microdata-template`, `--euromod-root`, `--euromod-system`, `--euromod-dataset`, `--scenario-dir` |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (argparse, lines 1981–2097) | Confirmed: `--singles-draws`, `--couples-draws`, `--euromod-combined`, `--out-base`, `--drawsmeta`, `--gsur-file`, `--year` |
| `docs/PIPELINE_ENTRYPOINTS.md` | Active entrypoint registry |
| Z: drive metadata files | `combined_draws_em__euromodmeta.json`, `singles_RURO_ready_RURO_draws__drawsmeta.json`, `fr_2016_RURO_mnl_job_gmm__mnlmeta.json` |

---

## 3. Existing 2016 Workflow (Reconstructed)

| Stage | Script | Run date | Key output on Z: |
| ----- | ------ | --------- | ---------------- |
| 1. Data prep | `enh_france_data_prep.py` | ~2026-02-04 | `outputs/prep/fr/2016/fr_2016.parquet`, `fr_2016_singles.parquet`, `fr_2016_couples.parquet` |
| 2. RURO prep | `enh_RURO_prep.py` | ~2026-02-05 | `Data/processed/fr/2016/singles_RURO_ready.parquet`, `couples_RURO_ready.parquet` |
| 3. Draws | `enh_RURO_draws.py` | 2026-05-13 | `singles_RURO_ready_RURO_draws.parquet` + `__drawsmeta.json` |
| 4. EUROMOD | `enh_RURO_euromod.py` | 2026-05-13 | `interim/ruro/fr/2016/ruro_occ/scenarios/combined_draws_em.parquet` + `__euromodmeta.json` |
| 5. GSUR v2 | `enh_prepare_FR_gsur_v2.py` | 2026-05-17 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` (2016 only; YEAR=2016 hardcoded) |
| 6. MNL prep | `enh_RURO_prep_mnl_basic.py` | 2026-05-17 | `Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet` + `__couples.parquet` + `__mnlmeta.json` |

**Confirmed 2016 draw parameters** (from `singles_RURO_ready_RURO_draws__drawsmeta.json`, 2026-05-13):

| Parameter | Value |
| --------- | ----- |
| `n_draws` | 99 |
| `seed` | 17 |
| `wage_spec` | `vw` |
| `occ_spec` | `empirical` |
| `occ_strata` | `__all__` |
| `pi0_m`, `pi0_f` | 0.1 |
| `h_min`, `h_max` | 5.0, 70.0 |
| `w_min`, `w_max` | 2.0, 170.0 |
| `id_multiplier` | 1000 |

**Confirmed 2016 EUROMOD parameters** (from `combined_draws_em__euromodmeta.json`, 2026-05-13):

| Parameter | Value |
| --------- | ----- |
| `--euromod-system` | `FR_2015` |
| `--euromod-dataset` | `FR_2016` |

**Note on `run_enhanced_pipeline.ps1` convention:**
The ps1 derives these as `${COUNTRY}_${SYSTEM_YEAR}` and `${COUNTRY}_${YEAR}` where
`SYSTEM_YEAR = YEAR - 1`. For data year 2016: `FR_2015` / `FR_2016` ✓ matches confirmed.
Applied to 2015: `FR_2014` / `FR_2015`; to 2017: `FR_2016` / `FR_2017`.
These are **tentative** — verify via preflight check in §8 before executing Step 4.

---

## 4. Required FR_2015 Inputs

| Input | Path | Status |
| ----- | ---- | ------ |
| EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` | **Present** |
| EUROMOD system | Tentatively `FR_2014` — confirm via preflight | **Tentative** |
| EUROMOD dataset | Tentatively `FR_2015` — confirm via preflight | **Tentative** |
| RURO-ready parquet | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready.parquet` | **Absent** (Steps 1–2 not run) |
| RURO draws parquet | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet` | **Absent** |
| EUROMOD combined output | `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet` | **Absent** |
| v1 GSUR file | `Data/external/FR_gsur_ruro.parquet` | **Present** (2015 rows confirmed) |
| GSURv2 for 2015 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` extended to 2015 | **Absent** |
| Eurostat D2 denominators 2015 | `Data/external/lfst_r_lfsd2pop_FR_2015.tsv` | **Absent** |
| INSEE BDM benchmark 2015 | BDM series 001688526 annual average | **Absent** |

---

## 5. Required FR_2017 Inputs

| Input | Path | Status |
| ----- | ---- | ------ |
| EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` | **Present** |
| EUROMOD system | Tentatively `FR_2016` — confirm via preflight | **Tentative** |
| EUROMOD dataset | Tentatively `FR_2017` — confirm via preflight | **Tentative** |
| RURO-ready parquet | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready.parquet` | **Absent** |
| RURO draws parquet | `Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet` | **Absent** |
| EUROMOD combined output | `Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet` | **Absent** |
| v1 GSUR file | `Data/external/FR_gsur_ruro.parquet` | **Present** (2017 rows confirmed) |
| GSURv2 for 2017 | `Data/external/FR_gsur_ruro_v2_stageA.parquet` extended to 2017 | **Absent** |
| Eurostat D2 denominators 2017 | `Data/external/lfst_r_lfsd2pop_FR_2017.tsv` | **Absent** |
| INSEE BDM benchmark 2017 | BDM series 001688526 annual average | **Absent** |

---

## 6. Step 1 — France Data Prep Commands

**Script:** `scripts/enhanced/enh_france_data_prep.py`

**Actual arguments** (confirmed from argparse and `run_enhanced_pipeline.ps1` line 490):
- `--year` (required): data year integer
- `--raw-dir`: directory containing the raw `.txt` file (not the full file path)
- `--raw-filename`: override the filename within `--raw-dir` (default: `FR_{year}.txt`; must be set because the file is named `FR_2015_a2.txt`, not `FR_2015.txt`)
- `--out-dir`: output directory
- `--system-year`: EUROMOD system year stamped into outputs (default: `year - 1`)
- `--export-format parquet`

**v1 error:** v1 used `--input` for the full file path, which does not exist in this
script. The correct pattern separates `--raw-dir` from `--raw-filename`.

```powershell
# ── Step 1a: FR_2015 data prep ──────────────────────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_france_data_prep.py" `
    --year 2015 `
    --raw-dir  "Z:\hisham\EUROMOD-STORAGE\Data\FR" `
    --raw-filename "FR_2015_a2.txt" `
    --out-dir  "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015" `
    --system-year 2014 `
    --export-format parquet

# ── Step 1b: FR_2017 data prep ──────────────────────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_france_data_prep.py" `
    --year 2017 `
    --raw-dir  "Z:\hisham\EUROMOD-STORAGE\Data\FR" `
    --raw-filename "FR_2017_a2.txt" `
    --out-dir  "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017" `
    --system-year 2016 `
    --export-format parquet
```

**Expected outputs** (inside each `--out-dir`):
- `fr_{year}.parquet` — full individual dataset
- `fr_{year}_singles.parquet`, `fr_{year}_couples.parquet`
- `fr_{year}_meta.json`, stats CSVs

---

## 7. Step 2 — RURO Prep Commands

**Script:** `scripts/enhanced/enh_RURO_prep.py`

**Actual arguments** (confirmed from argparse and `run_enhanced_pipeline.ps1` line 516):
- `--processed-dir`: absolute path to the directory written by Step 1
- `--base-year`: the data year integer
- `--export-format parquet`

**v1 error:** v1 used `--year` and `--input` flags that do not exist in this script.
The correct flag is `--processed-dir` pointing at the Step 1 output directory.

```powershell
# ── Step 2a: FR_2015 RURO prep ───────────────────────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep.py" `
    --processed-dir "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015" `
    --base-year 2015 `
    --export-format parquet

# ── Step 2b: FR_2017 RURO prep ───────────────────────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep.py" `
    --processed-dir "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017" `
    --base-year 2017 `
    --export-format parquet
```

**How `--processed-dir` is used:** the script reads `singles_filtering_final.parquet`
and `couples_filtering_final.parquet` from that directory, or falls back to
`fr_{year}_singles.parquet` / `fr_{year}_couples.parquet` if the filtering files are
absent. Passing the absolute Z: path bypasses the auto-detect logic that would
otherwise search storage roots.

**Expected outputs** (written to `--processed-dir`):
- `singles_RURO_ready.parquet`
- `couples_RURO_ready.parquet`

---

## 8. EUROMOD Preflight Check (Mandatory Before Step 4)

**This check must be completed before Step 4 commands are run for either year.**
Record the output in the per-year execution log.

```python
# Run interactively or as a standalone script before Step 4
import euromod as em
from path_helpers import euromod_root   # resolves to EUROMOD_RELEASES_J1.0+ under storage root

model = em.Model(str(euromod_root()))
fr = model["FR"]

for sys_name in sorted(fr.keys() if hasattr(fr, "keys") else [s for s in fr]):
    sys_obj = fr[sys_name]
    datasets = getattr(sys_obj, "datasets", {})
    try:
        ds_names = [getattr(d, "name", str(d)) for d in
                    (datasets.values() if hasattr(datasets, "values") else datasets)]
    except Exception:
        ds_names = ["(cannot enumerate)"]
    print(f"System: {sys_name:12s} | Datasets: {ds_names}")
```

From the output:
1. Find the system whose dataset list includes `FR_2015` → record as `SYSTEM_2015`.
2. Find the system whose dataset list includes `FR_2017` → record as `SYSTEM_2017`.
3. If names differ from `FR_2014`/`FR_2016` (the ps1 formula), update the Step 4
   commands accordingly before executing.
4. Paste the relevant lines into `Results/JMP_FR_{year}_single_year_pipeline_log_v1.md`.

**Do not proceed to Step 4 without completing this check and confirming the system names.**

---

## 9. Step 3 — Draw-Generation Commands

**Script:** `scripts/enhanced/enh_RURO_draws.py`

Arguments match v1 (verified against argparse). All parameter values are binding per
the authorization memo §6: same seed, same draw count, same support bounds as the
canonical 2016 run.

```powershell
# ── Step 3a: FR_2015 draws ──────────────────────────────────────────────────
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

# ── Step 3b: FR_2017 draws ──────────────────────────────────────────────────
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

**Expected outputs** (in same directory as `--singles-path`):
- `singles_RURO_ready_RURO_draws.parquet` + `singles_RURO_ready_RURO_draws__drawsmeta.json`
- `couples_RURO_ready_RURO_draws.parquet` + `couples_RURO_ready_RURO_draws__drawsmeta.json`

---

## 10. Step 4 — EUROMOD Combined Run Commands

**Script:** `scripts/enhanced/enh_RURO_euromod.py`

**Prerequisite:** EUROMOD preflight check (§8) must be completed first. Replace
`<SYSTEM_2015>` and `<SYSTEM_2017>` below with the confirmed system names.

Arguments confirmed against argparse (lines 1135–1146). The `--euromod-root` flag
is optional (the script auto-resolves from storage root or `MNL_EUROMOD_ROOT` env
var); pass it explicitly to avoid ambiguity.

```powershell
# ── Step 4a: FR_2015 EUROMOD run ─────────────────────────────────────────────
# Replace <SYSTEM_2015> with the value confirmed by the preflight check (§8)
# Expected: FR_2014
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
    --singles-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --microdata-template "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt" `
    --euromod-root    "Z:\hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
    --euromod-system  <SYSTEM_2015> `
    --euromod-dataset FR_2015 `
    --scenario-dir    "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios"

# ── Step 4b: FR_2017 EUROMOD run ─────────────────────────────────────────────
# Replace <SYSTEM_2017> with the value confirmed by the preflight check (§8)
# Expected: FR_2016
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_euromod.py" `
    --singles-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --microdata-template "Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt" `
    --euromod-root    "Z:\hisham\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+" `
    --euromod-system  <SYSTEM_2017> `
    --euromod-dataset FR_2017 `
    --scenario-dir    "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\ruro_occ\scenarios"
```

**Expected outputs** (in `--scenario-dir`):
- `combined_draws_em.parquet`
- `combined_draws_em__euromodmeta.json` — read this to confirm system/dataset before MNL prep

---

## 11. Step 5 — MNL-Input Parquet Construction Commands

**Script:** `scripts/enhanced/enh_RURO_prep_mnl_basic.py`

Arguments confirmed against argparse (lines 1981–2097). Using v1 GSUR fallback
(`FR_gsur_ruro.parquet`) because GSURv2 is not available for 2015 and 2017 (see §16).
The `--drawsmeta` flag passes the singles drawsmeta sidecar so the MNL-prep script
inherits draw parameters automatically.

```powershell
# ── Step 5a: FR_2015 MNL prep (v1 GSUR fallback) ────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base        "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\fr_2015_RURO_mnl" `
    --drawsmeta       "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file       "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2015

# ── Step 5b: FR_2017 MNL prep (v1 GSUR fallback) ────────────────────────────
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\enh_RURO_prep_mnl_basic.py" `
    --singles-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet" `
    --couples-draws   "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet" `
    --euromod-combined "Z:\hisham\EUROMOD-STORAGE\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet" `
    --out-base        "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\fr_2017_RURO_mnl" `
    --drawsmeta       "Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json" `
    --gsur-file       "U:\Desktop\Nizam_Hisham\MNL\Data\external\FR_gsur_ruro.parquet" `
    --year 2017
```

**Expected outputs** (derived from `--out-base`):
- `fr_{year}_RURO_mnl__singles.parquet`
- `fr_{year}_RURO_mnl__couples.parquet`
- `fr_{year}_RURO_mnl__mnlmeta.json`

**The output names intentionally omit the `GSURv2` segment.** This distinguishes
them from future GSURv2-upgraded versions. See §17 for the labelling policy.

---

## 12. Metadata Sidecar Handling

### drawsmeta JSON
Written by `enh_RURO_draws.py` as `{stem}__drawsmeta.json` in the same directory as
the draws parquet. Fields: `n_draws`, `max_draw`, `seed`, `id_multiplier`,
`household_type`, `distributional_params`, `input_file`, `output_schema`, `timestamp`,
`script`.

Pass to `enh_RURO_prep_mnl_basic.py` via `--drawsmeta` so draw parameters are
inherited automatically rather than re-specified manually.

### EUROMOD metadata
Written by `enh_RURO_euromod.py` as `combined_draws_em__euromodmeta.json` alongside
the combined parquet. Fields: `system`, `dataset`, `n_rows`, `n_draws`,
`id_multiplier`, `carried_columns`, `timestamp`, `script`.

Read immediately after Step 4 to confirm the system/dataset combination was applied:
```python
import json
em = json.load(open("...combined_draws_em__euromodmeta.json"))
print(f"System: {em['system']}, Dataset: {em['dataset']}")
# Must match the preflight-confirmed values from §8
```

### MNL metadata (mnlmeta)
Written by `enh_RURO_prep_mnl_basic.py` as `{out-base}__mnlmeta.json`. Contains
inputs, prior parameters, sample sizes, normalization constants, and column list.
Used by `m1_stack_years.py` to verify year-compatibility before stacking.

After Step 5, confirm the sidecar contains:
- `"script": "enh_RURO_prep_mnl_basic.py"`
- `"year": <year>`
- `"gsur_file"` pointing to the v1 file (`FR_gsur_ruro.parquet`)

Then add manually (if not auto-populated):
```json
"gsur_version": "v1_fallback",
"gsur_note": "Pre-GSURv2 / not final for pooled estimation. GSURv2 requires Eurostat denominator acquisition."
```

---

## 13. 2016 Local Mirroring Command

The 2016 MNL parquet exists on Z: but is absent from `Data/processed/fr/` (the
repo-local path that `m1_stack_years.py` scans). Per addendum v2 §Issue 3 (Option L):
copy locally; do not change the YAML `input_parquet_dir`.

```powershell
# Verify no existing file will be overwritten first
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2016_RURO_mnl_job_gmm__singles.parquet"

# Copy 2016 MNL input parquets and sidecar to repo-local Stage M1 input directory
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

**Note on 2016 file choice:** The command above copies `fr_2016_RURO_mnl_job_gmm__`
(Stage-A parquet from 2026-02-19; uses v1 GSUR). For GSUR consistency across all three
years, this is the appropriate choice: 2015, 2016, and 2017 all use v1 GSUR in this
pre-GSURv2 staging run. Do not copy `fr_2016_RURO_mnl_GSURv2__` for a mixed-GSUR run.

---

## 14. Output Paths for 2015

| Stage | Output path (Z:) | Description |
| ----- | ---------------- | ----------- |
| Step 1 | `Z:\...\Data\processed\fr\2015\fr_2015.parquet` | Cleaned individual-level dataset |
| Step 2 | `Z:\...\Data\processed\fr\2015\singles_RURO_ready.parquet` | Singles RURO input |
| Step 2 | `Z:\...\Data\processed\fr\2015\couples_RURO_ready.parquet` | Couples RURO input |
| Step 3 | `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws.parquet` | Long draws (singles) |
| Step 3 | `Z:\...\Data\processed\fr\2015\singles_RURO_ready_RURO_draws__drawsmeta.json` | Draws sidecar |
| Step 3 | `Z:\...\Data\processed\fr\2015\couples_RURO_ready_RURO_draws.parquet` | Long draws (couples) |
| Step 4 | `Z:\...\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em.parquet` | EUROMOD output |
| Step 4 | `Z:\...\interim\ruro\fr\2015\ruro_occ\scenarios\combined_draws_em__euromodmeta.json` | EUROMOD sidecar |
| Step 5 | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__singles.parquet` | MNL input (pre-GSURv2) |
| Step 5 | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__couples.parquet` | MNL input (pre-GSURv2) |
| Step 5 | `Z:\...\Data\processed\fr\2015\fr_2015_RURO_mnl__mnlmeta.json` | MNL sidecar |
| Stage M1 copy | `Data/processed/fr/fr_2015_RURO_mnl__singles.parquet` | Repo-local; copied from Z: after validation |
| Stage M1 copy | `Data/processed/fr/fr_2015_RURO_mnl__couples.parquet` | Repo-local |

---

## 15. Output Paths for 2017

| Stage | Output path (Z:) | Description |
| ----- | ---------------- | ----------- |
| Step 1 | `Z:\...\Data\processed\fr\2017\fr_2017.parquet` | Cleaned individual-level dataset |
| Step 2 | `Z:\...\Data\processed\fr\2017\singles_RURO_ready.parquet` | Singles RURO input |
| Step 2 | `Z:\...\Data\processed\fr\2017\couples_RURO_ready.parquet` | Couples RURO input |
| Step 3 | `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws.parquet` | Long draws (singles) |
| Step 3 | `Z:\...\Data\processed\fr\2017\singles_RURO_ready_RURO_draws__drawsmeta.json` | Draws sidecar |
| Step 3 | `Z:\...\Data\processed\fr\2017\couples_RURO_ready_RURO_draws.parquet` | Long draws (couples) |
| Step 4 | `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em.parquet` | EUROMOD output |
| Step 4 | `Z:\...\interim\ruro\fr\2017\ruro_occ\scenarios\combined_draws_em__euromodmeta.json` | EUROMOD sidecar |
| Step 5 | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__singles.parquet` | MNL input (pre-GSURv2) |
| Step 5 | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__couples.parquet` | MNL input (pre-GSURv2) |
| Step 5 | `Z:\...\Data\processed\fr\2017\fr_2017_RURO_mnl__mnlmeta.json` | MNL sidecar |
| Stage M1 copy | `Data/processed/fr/fr_2017_RURO_mnl__singles.parquet` | Repo-local; copied from Z: after validation |
| Stage M1 copy | `Data/processed/fr/fr_2017_RURO_mnl__couples.parquet` | Repo-local |

---

## 16. Output Paths for Mirrored 2016

| Source (Z:) | Destination (repo-local) | Notes |
| ----------- | ------------------------ | ----- |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__singles.parquet` | Stage M1 key: `fr_2016_RURO_mnl_job_gmm` |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__couples.parquet` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__couples.parquet` | |
| `Z:\...\fr\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | `Data/processed/fr/fr_2016_RURO_mnl_job_gmm__mnlmeta.json` | Sidecar for M1 validation |

The M1 YAML key `fr_2016_RURO_mnl_job_gmm` matches the file-name stem. `m1_stack_years.py`
discovers files by scanning for parquets whose stem matches; the sidecar JSON is
auto-detected alongside.

---

## 17. Versioning and No-Overwrite Rules

1. **`fr_2016_RURO_mnl_GSURv2__*.parquet` must not be touched.** Canonical M1-clean
   operative files per `docs/RURO_occ_M1_clean_verdict_v1.md`.

2. **`fr_2016_RURO_mnl_job_gmm__*.parquet` must not be overwritten.** These are the
   source for the §13 local mirror.

3. **New 2015 and 2017 parquets use the naming stem `fr_{year}_RURO_mnl__`** (double
   underscore; no `GSURv2` segment). Future GSURv2-upgraded versions would be named
   `fr_{year}_RURO_mnl_GSURv2__*.parquet`.

4. **Z: originals are retained.** The repo-local `Data/processed/fr/` copies do not
   replace the Z: files.

5. **Parquet files are git-ignored.** Sidecar JSON files may be committed if small.

---

## 18. GSURv2 Year-Parameterization Status

`scripts/enhanced/enh_prepare_FR_gsur_v2.py` has `YEAR = 2016` hardcoded at line 44
and accepts no `--year` CLI argument. It writes only
`Data/external/FR_gsur_ruro_v2_stageA.parquet` (2016 rates; 54 rows).

To extend GSURv2 to 2015 and 2017, the script needs modification (add `--year`,
`--tsv-d2`, `--tsv-d1`, `--benchmark-pct`, year-parameterized output path) plus
upstream acquisition of Eurostat TSV files and INSEE BDM benchmarks for those years.
Neither the script modification nor the acquisition is authorised by this plan.

---

## 19. Non-GSURv2 Fallback Labelling Rule

When `enh_RURO_prep_mnl_basic.py` is run with
`--gsur-file Data/external/FR_gsur_ruro.parquet` (v1 lookup), the resulting parquets:

- Are **pre-GSURv2 / not final for pooled estimation**.
- May be used for single-year diagnostics and dry-run Stage M1 checks.
- Must **not** be used as inputs for the final pooled P3a estimation run.

File-name stems must be `fr_{year}_RURO_mnl__` (not `fr_{year}_RURO_mnl_GSURv2__`).

MNL sidecar must carry:
```json
"gsur_version": "v1_fallback",
"gsur_note": "Pre-GSURv2 / not final for pooled estimation. GSURv2 rates for this year require Eurostat denominator acquisition."
```

The Stage M1 YAML for P3a (`config/fr_p3a_stage_m1.yaml`) should reference
GSURv2-upgraded parquets when available. Using v1-fallback parquets in a production
P3a run is not authorised.

---

## 20. CPI/HICP Handling

The CPI/HICP harmonisation step occurs in Stage M1, not here. The single-year
parquets produced by this plan contain nominal income variables.

For reference, the adopted φ_t values (EUROMOD HICP, Option B, provisional):

| Year | φ_t |
| ---- | --- |
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |

Source: `Data/external/cpi_hicp_fr_harmonisation.csv`.
Decision memo: `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`.

---

## 21. Validation Checks After Each Year

Run before copying parquets to `Data/processed/fr/`.

**Check A — drawsmeta digest**
```python
import json
dm = json.load(open("Z:/.../fr/2015/singles_RURO_ready_RURO_draws__drawsmeta.json"))
assert dm["n_draws"] == 99
assert dm["distributional_params"]["wage_spec"] == "vw"
assert dm["distributional_params"]["occ_spec"] == "empirical"
assert dm["distributional_params"]["h_min"] == 5.0
assert dm["distributional_params"]["w_min"] == 2.0
```

**Check B — EUROMOD system confirmation**
```python
import json
em = json.load(open("Z:/.../fr/2015/ruro_occ/scenarios/combined_draws_em__euromodmeta.json"))
print(f"System: {em['system']}, Dataset: {em['dataset']}")
# Must match the values confirmed in the preflight check (§8)
```

**Check C — draw count uniformity**
```python
import pandas as pd
s = pd.read_parquet("Z:/.../fr/2015/fr_2015_RURO_mnl__singles.parquet")
assert s["draw"].nunique() == 100   # draws 0..99
n_deciders = (s["draw"] == 0).sum()
print(f"Singles deciders: {n_deciders}")
```

**Check D — tpr/twl incidence**

| Year | Variable | Expected WA non-zero (RURO sample) | Escalation threshold |
| ---- | -------- | ---------------------------------- | -------------------- |
| 2015 | `tpr` | ≤ 55 rows (0.344% WA in raw) | > 1% of RURO sample |
| 2017 | `twl` | ≤ 55 rows (0.295% WA in raw) | > 1% of RURO sample |

If either year exceeds the threshold, stop and escalate to a formal comparability
check before Stage M1. (Per addendum v2 §Issue 2.)

**Check E — no-overwrite guard**
```powershell
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2015_RURO_mnl__singles.parquet"
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2017_RURO_mnl__singles.parquet"
# Both must return False before copying
```

---

## 22. Expected Reports to Create

| Report | Path | Required content |
| ------ | ---- | ---------------- |
| 2015 pipeline log | `Results/JMP_FR_2015_single_year_pipeline_log_v1.md` | EUROMOD preflight output; confirmed system/dataset; sample sizes from Check C; drawsmeta digest; tpr incidence from Check D |
| 2017 pipeline log | `Results/JMP_FR_2017_single_year_pipeline_log_v1.md` | Same structure |
| tpr/twl annotation | New section in `Results/M1_identity_validation_summary.md` | Per-year non-zero counts from Check D vs. addendum v2 thresholds |
| Stage M1 readiness update | Addendum to `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | Re-run dry-run checks with all parquets in place; update verdict if all gaps closed |

---

## 23. Execution Readiness Verdict

**Single-year replication of FR_2015 and FR_2017 is AUTHORISED as of 2026-05-19,**
subject to the conditions in `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`.

**Remaining pre-execution gates:**

| # | Gate | Action |
|---|------|--------|
| 1 | EUROMOD system/dataset for 2015 and 2017 unconfirmed | Complete preflight check (§8) before Step 4 |
| 2 | GSURv2 not available for 2015/2017 | Accept v1 fallback with labelling rule in §19; defer GSURv2 upgrade |

**Non-blocking (handled by this plan):**
- 2016 local mirroring: command in §13; ready to execute.
- v1 GSUR fallback: acceptable for staging; labelling rule in §19 prevents production use.
- CPI/HICP values: present in CSV; applied at Stage M1 only.

**Once Steps 1–5 complete for both years and all validation checks pass, copy parquets
to `Data/processed/fr/` and proceed to update the Stage M1 execution-readiness verdict.**