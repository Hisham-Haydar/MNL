# RURO Pipeline Entrypoints

This file defines the active paths for future work. If another script can do a similar job but is not listed here, treat it as legacy, diagnostic, or experimental until it is promoted here.

For a topic-by-topic memory map of GMM, GSUR, job-choice, commands, and current result baselines, see `docs/RURO_PROJECT_MEMORY_MAP.md`.

Focused method notes:

- `docs/RURO_RETURN_GUIDE_DATA_RESULTS_AND_CLEANUP.md`
- `docs/RURO_EXTERNAL_STORAGE_HYGIENE_AUDIT_2026-05-12.md`
- `docs/RURO_JOB_MODEL_GMM_METHOD_NOTE.md`
- `docs/RURO_GSUR_DATA_AND_MERGE_NOTE.md`

## Active Continuous RURO Pipeline

Main runner:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

Main step scripts:

- `scripts/enhanced/enh_france_data_prep.py`
- `scripts/enhanced/enh_RURO_prep.py`
- `scripts/enhanced/enh_RURO_draws.py`
- `scripts/enhanced/enh_RURO_euromod.py`
- `scripts/enhanced/enh_prepare_FR_gsur.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/enh_RURO_estimate_FR.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`

Current continuous-RURO spec candidates:

- `scripts/enhanced/estimation_spec_v3.yaml`
- `scripts/enhanced/estimation_spec_v2.yaml`
- `scripts/enhanced/estimation_spec.yaml`

## Active Job-Choice RURO Pipeline

Main runner:

```powershell
python scripts/Job_model/run_job_ruro_pipeline.py
```

Main step scripts:

- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/enhanced/enh_RURO_euromod.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/enh_RURO_estimate_FR.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`

Current job-choice spec candidates:

- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml`
- `scripts/enhanced/estimation_spec_job_M2e_a.yaml`
- `scripts/enhanced/estimation_spec_job_M2g_unified_opportunity.yaml`

## Reference Implementation

Keep Stijn's R files unchanged as reference material:

- `stijn/Ruro_estimation_H.Rmd`
- `stijn/Ruro_estimation_new.Rmd`
- `stijn/Ruro_functions_EMRWS.R`
- `stijn/Ruro_simulation_H.Rmd`

## Diagnostics

Manual diagnostic scripts belong in:

```text
scripts/diagnostics/
```

They are useful for investigation, but they are not pipeline entrypoints.

## Legacy Runners

Old root-level PowerShell runners belong in:

```text
scripts/runners/legacy/
```

They are retained for provenance only. Prefer the active runners listed above.
