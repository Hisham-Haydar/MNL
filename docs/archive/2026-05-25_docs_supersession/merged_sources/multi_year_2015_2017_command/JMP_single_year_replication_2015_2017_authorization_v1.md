> Merged into `docs/France_case/consolidated/JMP_multi_year_2015_2017_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# JMP Single-Year Replication — FR_2015 and FR_2017 — Execution Authorization

**Document:** docs/JMP_single_year_replication_2015_2017_authorization_v1.md
**Date:** 2026-05-19
**Author:** Hisham Haydar
**Status:** AUTHORIZATION MEMO — governs execution of the FR_2015 and FR_2017 single-year pipeline

---

## 1. Purpose of This Memo

This memo authorises execution of the five-stage single-year RURO pipeline for
**FR_2015** and **FR_2017**. It is the prerequisite document cited by
`docs/JMP_single_year_replication_2015_2017_command_plan_v2.md`. No pipeline command
for 2015 or 2017 may be run before this memo exists and is accepted.

The five stages covered are:

1. France data prep (`enh_france_data_prep.py`)
2. RURO prep (`enh_RURO_prep.py`)
3. RURO draws (`enh_RURO_draws.py`)
4. EUROMOD combined run (`enh_RURO_euromod.py`)
5. MNL-input parquet construction (`enh_RURO_prep_mnl_basic.py`)

This memo does **not** authorise pooled stacking, estimation, welfare computation,
or any write to canonical FR_2016 files.

---

## 2. Pipeline Goal

Produce the per-year MNL input parquets required by Stage M1:

- `fr_2015_RURO_mnl__singles.parquet` and `fr_2015_RURO_mnl__couples.parquet`
- `fr_2017_RURO_mnl__singles.parquet` and `fr_2017_RURO_mnl__couples.parquet`

These parquets are produced using the **v1 GSUR fallback** (`FR_gsur_ruro.parquet`)
because GSURv2 rates for 2015 and 2017 are not yet available. They are labelled
**pre-GSURv2 / not final for pooled estimation** (see §9). Their immediate use is:

- Enabling Stage M1 dry-run checks with all three years present in `Data/processed/fr/`.
- Supporting single-year sample-size and income-variable diagnostics.
- Unblocking the Stage M1 execution-readiness verdict once all three year parquets
  and the 2016 local mirror are in place.

---

## 3. Scope: What Is Authorised

| Action | Authorised |
| ------ | ---------- |
| Run `enh_france_data_prep.py` for FR_2015 | Yes |
| Run `enh_france_data_prep.py` for FR_2017 | Yes |
| Run `enh_RURO_prep.py` for FR_2015 | Yes |
| Run `enh_RURO_prep.py` for FR_2017 | Yes |
| Run `enh_RURO_draws.py` for FR_2015 (99 draws, vw, seed=17) | Yes |
| Run `enh_RURO_draws.py` for FR_2017 (99 draws, vw, seed=17) | Yes |
| Run `enh_RURO_euromod.py` for FR_2015 | Yes — after EUROMOD preflight confirms system/dataset |
| Run `enh_RURO_euromod.py` for FR_2017 | Yes — after EUROMOD preflight confirms system/dataset |
| Run `enh_RURO_prep_mnl_basic.py` for FR_2015 with v1 GSUR | Yes |
| Run `enh_RURO_prep_mnl_basic.py` for FR_2017 with v1 GSUR | Yes |
| Copy 2015/2017 parquets to `Data/processed/fr/` | Yes — after per-year validation checks |
| Copy 2016 `fr_2016_RURO_mnl_job_gmm__` to `Data/processed/fr/` | Yes |

---

## 4. Scope: What Is Not Authorised

| Action | Status |
| ------ | ------ |
| Run `m1_stack_years.py` (pooled stacking) | **NOT AUTHORISED** — requires separate Stage M1 execution authorisation |
| Run `enh_RURO_estimate_FR.py` (estimation) | **NOT AUTHORISED** |
| Compute welfare | **NOT AUTHORISED** |
| Overwrite `fr_2016_RURO_mnl_GSURv2__*.parquet` | **PROHIBITED** — canonical M1-clean operative files |
| Overwrite `fr_2016_RURO_mnl_job_gmm__*.parquet` | **PROHIBITED** — source for the 2016 local mirror |
| Label 2015/2017 parquets as GSURv2 or final | **PROHIBITED** — must carry pre-GSURv2 label |
| Use 2015/2017 v1-GSUR parquets in production P3a estimation | **PROHIBITED** |
| Run EUROMOD for 2015 or 2017 without completing the preflight check (§8) | **PROHIBITED** |

---

## 5. Input Files Confirmed Available

| Year | File | Path | Status |
| ---- | ---- | ---- | ------ |
| 2015 | EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2015_a2.txt` | Confirmed present |
| 2017 | EU-SILC raw microdata | `Z:\hisham\EUROMOD-STORAGE\Data\FR\FR_2017_a2.txt` | Confirmed present |
| All | v1 GSUR lookup | `Data/external/FR_gsur_ruro.parquet` | Confirmed present; contains 2015 and 2017 rows |
| All | CPI/HICP CSV | `Data/external/cpi_hicp_fr_harmonisation.csv` | Confirmed present (applied at Stage M1 only) |
| All | EUROMOD release | Auto-resolved from storage root via `_resolve_euromod_root()` | Present |

---

## 6. Draw Parameters — Binding Specification

All draw parameters below are **binding**: the `enh_RURO_draws.py` command must use
exactly these values for both 2015 and 2017. They match the canonical 2016 run
(drawsmeta timestamp 2026-05-13).

| Parameter | Binding value | CLI flag |
| --------- | ------------- | -------- |
| n_draws | 99 | `--n-draws 99` |
| wage_spec | vw | `--wage-spec vw` |
| occ_spec | empirical | `--occ-spec empirical` |
| occ_strata | `__all__` | `--occ-strata __all__` |
| pi0_m, pi0_f | 0.1 | `--pi0-m 0.1 --pi0-f 0.1` |
| h_min, h_max | 5.0, 70.0 | `--h-min 5.0 --h-max 70.0` |
| w_min, w_max | 2.0, 170.0 | `--w-min 2.0 --w-max 170.0` |
| rng_seed | 17 | `--rng-seed 17` |

Rationale: comparability across years for Stage M1 pooled estimation requires
identical draw-generation settings. Deviation from these values requires a new
authorisation memo.

---

## 7. EUROMOD System/Dataset Convention

The pipeline runner (`run_enhanced_pipeline.ps1`) constructs EUROMOD arguments as:
```
EUROMOD_SYSTEM = FR_{data_year - 1}   (e.g. FR_2015 for data year 2016)
EUROMOD_DATASET = FR_{data_year}      (e.g. FR_2016 for data year 2016)
```

Applying this convention:

| Data year | `--euromod-system` | `--euromod-dataset` |
| --------- | ------------------ | ------------------- |
| 2015 | `FR_2014` | `FR_2015` |
| 2016 (reference) | `FR_2015` ✓ confirmed | `FR_2016` ✓ confirmed |
| 2017 | `FR_2016` | `FR_2017` |

**These values are tentative.** They follow the established convention and match
the confirmed 2016 run, but must be verified against the EUROMOD release directory
before executing the EUROMOD step for each year (see §8). If the EUROMOD model does
not contain a system named `FR_2014`, the correct system name must be determined
before running.

---

## 8. EUROMOD Preflight Check (Mandatory Before Step 4)

Before running `enh_RURO_euromod.py` for either year, execute the following
preflight check and record the output:

```python
# Preflight: confirm EUROMOD systems and datasets for 2015 and 2017
import euromod as em
from path_helpers import euromod_root

model = em.Model(str(euromod_root()))
fr = model["FR"]

# Print all available systems and their datasets
for sys_name, sys_obj in fr.items():
    datasets = getattr(sys_obj, "datasets", {})
    ds_names = [getattr(d, "name", str(d)) for d in (datasets.values() if hasattr(datasets, "values") else datasets)]
    print(f"System: {sys_name} | Datasets: {ds_names}")
```

From the output:
1. Identify the system name that contains dataset `FR_2015` → use as `--euromod-system` for data year 2015.
2. Identify the system name that contains dataset `FR_2017` → use as `--euromod-system` for data year 2017.
3. If the exact dataset names differ from `FR_2015` / `FR_2017`, record the correct names.
4. Paste the relevant output lines into the execution log (`Results/JMP_FR_{year}_single_year_pipeline_log_v1.md`).

**Do not proceed to the EUROMOD step for any year until this preflight is complete
and the correct system/dataset names are confirmed.**

---

## 9. Output Labelling Rule (Binding)

All MNL parquets produced by this authorisation carry the **pre-GSURv2** label.

**File naming:** `fr_{year}_RURO_mnl__singles.parquet` and `fr_{year}_RURO_mnl__couples.parquet`
(double underscore, no `GSURv2` segment).

**Sidecar annotation:** after running `enh_RURO_prep_mnl_basic.py`, the
`__mnlmeta.json` sidecar must contain:

```json
"gsur_version": "v1_fallback",
"gsur_note": "Pre-GSURv2 / not final for pooled estimation. GSURv2 rates for this year require Eurostat denominator acquisition (lfst_r_lfsd2pop, lfst_r_lfp2acedu) and INSEE BDM benchmark retrieval before enh_prepare_FR_gsur_v2.py can be extended to this year."
```

If the sidecar does not contain these fields after the run, add them manually before
copying to the Stage M1 input directory.

**Consequence:** these parquets may be used for Stage M1 dry-run checks and
single-year diagnostics. They must not be used as inputs for a production P3a
estimation run. A future authorisation memo — contingent on GSURv2 extension to
2015/2017 — is required before production use.

---

## 10. Validation Checks Required Before Stage M1 Copy

The following checks must be completed and recorded for each year before copying
parquets to `Data/processed/fr/`:

**Check A — drawsmeta digest**
```python
import json
dm = json.load(open("...singles_RURO_ready_RURO_draws__drawsmeta.json"))
assert dm["n_draws"] == 99
assert dm["distributional_params"]["wage_spec"] == "vw"
assert dm["distributional_params"]["occ_spec"] == "empirical"
assert dm["distributional_params"]["h_min"] == 5.0
assert dm["distributional_params"]["w_min"] == 2.0
```

**Check B — EUROMOD system confirmation**
```python
em_meta = json.load(open("...combined_draws_em__euromodmeta.json"))
print(f"System: {em_meta['system']}, Dataset: {em_meta['dataset']}")
# Must match the values confirmed in the EUROMOD preflight (§8)
```

**Check C — draw count uniformity**
```python
import pandas as pd
s = pd.read_parquet("...fr_{year}_RURO_mnl__singles.parquet")
assert s["draw"].nunique() == 100   # draws 0..99
assert (s["draw"] == 0).sum() > 0   # at least one decider per year
print(f"Deciders: {(s['draw'] == 0).sum()}, Draws 1-99: {(s['draw'] > 0).sum()}")
```

**Check D — tpr/twl incidence**

| Year | Variable | Expected WA non-zero rows | Escalation threshold |
| ---- | -------- | ------------------------- | -------------------- |
| 2015 | `tpr` | ≤ 55 rows (0.344% WA in raw file) | > 1% of RURO sample |
| 2017 | `twl` | ≤ 55 rows (0.295% WA in raw file) | > 1% of RURO sample |

If any year exceeds the escalation threshold, stop and create a formal comparability
check memo before proceeding to Stage M1.

**Check E — no-overwrite guard**
```powershell
# Verify target files do not already exist before copying
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2015_RURO_mnl__singles.parquet"
Test-Path "U:\Desktop\Nizam_Hisham\MNL\Data\processed\fr\fr_2017_RURO_mnl__singles.parquet"
# Both must return False before copying
```

---

## 11. No-Overwrite Rules

1. `fr_2016_RURO_mnl_GSURv2__singles.parquet` and `*__couples.parquet` — **must not be
   touched**. These are the M1-clean canonical operative files.

2. `fr_2016_RURO_mnl_job_gmm__singles.parquet` and `*__couples.parquet` — **must not be
   overwritten**. They are the source of the 2016 local mirror.

3. Any existing file in `Data/processed/fr/` that already carries a year tag for 2015
   or 2017 — must be inspected before overwriting. If it exists, document why the
   re-run is needed in the execution log.

4. Z: originals are retained. Local copies in `Data/processed/fr/` are supplementary;
   the Z: path is the authoritative storage copy.

---

## 12. Required Post-Execution Reports

After completing all five stages for each year and before any Stage M1 run:

| Report | Path | Required content |
| ------ | ---- | ---------------- |
| 2015 pipeline log | `Results/JMP_FR_2015_single_year_pipeline_log_v1.md` | EUROMOD preflight output; confirmed system/dataset; sample sizes from Check C; drawsmeta digest; tpr incidence from Check D |
| 2017 pipeline log | `Results/JMP_FR_2017_single_year_pipeline_log_v1.md` | Same structure |
| tpr/twl annotation | New section in `Results/M1_identity_validation_summary.md` | Per-year non-zero counts from Check D; comparison against addendum v2 thresholds |

These reports are prerequisite to updating the Stage M1 execution-readiness verdict.

---

## 13. GSURv2 Upgrade Path (Out of Scope Here)

This authorisation covers only the v1 GSUR fallback. The GSURv2 upgrade path for
2015 and 2017 requires:

1. Acquiring `lfst_r_lfsd2pop_FR_{year}.tsv` and `lfst_r_lfp2acedu_FR_{year}.tsv`
   from the Eurostat API for each year.
2. Retrieving INSEE BDM 001688526 annual averages for 2015 and 2017.
3. Adding `--year`, `--tsv-d2`, `--tsv-d1`, and `--benchmark-pct` CLI arguments to
   `enh_prepare_FR_gsur_v2.py` (currently hard-coded to `YEAR = 2016`).
4. Running the extended script to produce `FR_gsur_ruro_v2_stageA_{year}.parquet`.
5. Re-running `enh_RURO_prep_mnl_basic.py` with the GSURv2 file and writing
   `fr_{year}_RURO_mnl_GSURv2__singles.parquet`.
6. A new authorisation memo covering the GSURv2-upgraded runs.

None of steps 1–6 are authorised here.

---

## 14. Relationship to Other Documents

| Document | Role |
| -------- | ---- |
| `docs/JMP_single_year_replication_2015_2017_command_plan_v2.md` | Command-plan; provides exact commands; cites this memo as prerequisite |
| `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | Stage M1 readiness verdict (currently NOT AUTHORIZED); updated after 2015/2017 parquets are in place |
| `Results/JMP_multi_year_stage_M1_readiness_addendum_v2.md` | tpr/twl clarification; defines validation annotation requirements |
| `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md` | CPI φ_t values; applied at Stage M1, not here |
| `docs/RURO_occ_M1_clean_verdict_v1.md` | Defines canonical 2016 files that must not be overwritten |

---

## 15. Authorization Statement

The pipeline steps described in §3 are hereby authorised for execution, subject to:

- The EUROMOD preflight check (§8) being completed and recorded before the EUROMOD
  step for each year.
- All validation checks in §10 being completed and recorded before copying parquets
  to `Data/processed/fr/`.
- All output files carrying the pre-GSURv2 label per §9.
- All reports in §12 being created after execution.
- All prohibitions in §4 and §11 being observed throughout.

**This authorisation covers FR_2015 and FR_2017 only.** FR_2018 single-year
replication requires a separate authorisation (contingent on the ISF/`tpr`
comparability check referenced in the Stage M1 execution-readiness report).

Stage M1 pooled stacking remains separately gated by
`docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md`.