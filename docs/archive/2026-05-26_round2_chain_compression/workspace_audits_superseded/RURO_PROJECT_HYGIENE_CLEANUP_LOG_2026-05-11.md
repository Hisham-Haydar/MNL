> Archived on 2026-05-26 — pre-cleanup hygiene log from 2026-05-11, superseded by the Round-1 manifest which is now the canonical hygiene record for the 2026-05-25 docs/ reorganization.
> Canonical hygiene record (kept active): `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# RURO Project Hygiene Cleanup Log

Date: 2026-05-11  
Scope: reversible project-hygiene cleanup.  
Deletion status: no files were deleted.

## Added

- `docs/PIPELINE_ENTRYPOINTS.md`
- `docs/estimation/RURO_ACTIVE_RESULTS_REGISTRY.md`
- `docs/France_case/RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md`
- `outputs/KEEP_RESULTS.md`
- `scripts/archive/README.md`
- `scripts/diagnostics/README.md`
- `scripts/runners/legacy/README.md`
- `docs/archive/README.md`

## Updated

- `.gitignore`
- `README.md`
- `scripts/Job_model/README_job_model.md`
- `scripts/enhanced/README.md`
- `scripts/enhanced/run_diagnostics.ps1`
- `scripts/enhanced/enh_RURO_prep.py`
- `docs/package/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md`

The previous root `README.md` was preserved as:

```text
docs/archive/implementation_history/README_legacy_2026-05-11.md
```

## Moved Root Documentation

Implementation history:

- `DONE.md` -> `docs/archive/implementation_history/DONE.md`
- `IMPLEMENTATION_SUMMARY.md` -> `docs/archive/implementation_history/IMPLEMENTATION_SUMMARY.md`
- `POST_ESTIMATION_IMPROVEMENTS.md` -> `docs/archive/implementation_history/POST_ESTIMATION_IMPROVEMENTS.md`
- `VECTORIZED_IMPLEMENTATION_STATUS.md` -> `docs/archive/implementation_history/VECTORIZED_IMPLEMENTATION_STATUS.md`

Roadmap:

- `TODO.md` -> `docs/ROADMAP.md`

Job-choice notes:

- `JOB_CHOICE_MODEL_DIAGNOSIS.md` -> `docs/archive/job_choice_notes/JOB_CHOICE_MODEL_DIAGNOSIS.md`
- `JOB_CHOICE_PIPELINE.md` -> `docs/archive/job_choice_notes/JOB_CHOICE_PIPELINE.md`
- `JOB_CHOICE_PIPELINE_WALKTHROUGH.md` -> `docs/archive/job_choice_notes/JOB_CHOICE_PIPELINE_WALKTHROUGH.md`

Occupation-choice notes:

- `OCCUPATION_CHOICE_AGNOSTIC_DESIGN.md` -> `docs/archive/occupation_choice_notes/OCCUPATION_CHOICE_AGNOSTIC_DESIGN.md`
- `OCCUPATION_CHOICE_DESIGN.md` -> `docs/archive/occupation_choice_notes/OCCUPATION_CHOICE_DESIGN.md`
- `OCCUPATION_CHOICE_MATHEMATICAL_SPECIFICATION.md` -> `docs/archive/occupation_choice_notes/OCCUPATION_CHOICE_MATHEMATICAL_SPECIFICATION.md`
- `OCCUPATION_CHOICE_SUMMARY.md` -> `docs/archive/occupation_choice_notes/OCCUPATION_CHOICE_SUMMARY.md`
- `OCCUPATION_VS_EDUCATION_CHOICE.md` -> `docs/archive/occupation_choice_notes/OCCUPATION_VS_EDUCATION_CHOICE.md`

## Moved Root Scripts

Diagnostics:

- `check_nchildren_simple.py` -> `scripts/diagnostics/check_nchildren_simple.py`
- `check_nchildren_variation.py` -> `scripts/diagnostics/check_nchildren_variation.py`
- `check_nchildren_variation_v2.py` -> `scripts/diagnostics/check_nchildren_variation_v2.py`
- `check_preference_diagnostics.py` -> `scripts/diagnostics/check_preference_diagnostics.py`
- `check_type_ids.py` -> `scripts/diagnostics/check_type_ids.py`
- `compare_scipy_gamspy.py` -> `scripts/diagnostics/compare_scipy_gamspy.py`
- `test_gamspy_vs_scipy.py` -> `scripts/diagnostics/test_gamspy_vs_scipy.py`

Legacy runners:

- `cleanup_final.ps1` -> `scripts/runners/legacy/cleanup_final.ps1`
- `run_gamspy_estimation.ps1` -> `scripts/runners/legacy/run_gamspy_estimation.ps1`
- `RUN_NOW.ps1` -> `scripts/runners/legacy/RUN_NOW.ps1`
- `RUN_OPTIMIZED_ESTIMATION.ps1` -> `scripts/runners/legacy/RUN_OPTIMIZED_ESTIMATION.ps1`
- `RUN_PIPELINE_WITH_REDUCED_FILES.ps1` -> `scripts/runners/legacy/RUN_PIPELINE_WITH_REDUCED_FILES.ps1`
- `RUN_POST_ESTIMATION_STYLED.ps1` -> `scripts/runners/legacy/RUN_POST_ESTIMATION_STYLED.ps1`
- `RUN_WITH_SCIPY.ps1` -> `scripts/runners/legacy/RUN_WITH_SCIPY.ps1`

## Moved Legacy and Scratch Material

- `scripts/Old_Script_ruro(not well)` -> `scripts/archive/old_ruro_pre_enhanced`
- `scratch` -> `docs/archive/scratch_2026-05-11`

Backups:

- `scripts/enhanced/estimation_spec.yaml.backup` -> `scripts/archive/backups_2025_12/estimation_spec.yaml.backup`
- `scripts/enhanced/estimation_spec_loc_empirical.yaml.backup` -> `scripts/archive/backups_2025_12/estimation_spec_loc_empirical.yaml.backup`
- `scripts/RURO_estimate_FR.py.backup_20251216_143415` -> `scripts/archive/backups_2025_12/RURO_estimate_FR.py.backup_20251216_143415`

Generated inventory and command logs:

- `RURO_MNL_project_files_structure.md` -> `docs/archive/inventories/RURO_MNL_project_files_structure_2026-05-11.md`
- `commands.txt` -> `docs/archive/commands/commands_legacy.txt`
- `logs/commands_20260122_143200.txt` -> `docs/archive/commands/commands_20260122_143200.txt`

## Remaining Manual Decisions

- Whether to delete generated/local clutter such as `_gams_work/`, `Microsoft/`, `.ruff_cache/`, `.mplconfig/`, `src/mnl.egg-info/`, empty `reports/`, and empty `logs/`.
- Whether to reorganize the many YAML specs into `active`, `experiments`, and `archive` subfolders.
- Whether to reduce old `outputs/` folders after the result registry is complete.
