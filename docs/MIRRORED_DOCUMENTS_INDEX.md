# Mirrored Documents Index

**Purpose:** central index for important project documentation that originally
lives outside `docs/` but has been copied into `docs/` for easier sharing and
paper-writing.

These are mirrors, not moves. The original files remain in their original
locations so existing scripts, notes, and references keep working.

## Mirror Policy

- Treat the original file as the operational source when a script or workflow
  expects it at the original path.
- Treat the mirrored file as the documentation bundle copy.
- If an original changes, refresh the mirror and update this index if the path
  changes.

**2026-05-25 reorganization note:** France-specific mirrors moved from their
original top-level `docs/euromod_reference/`, `docs/canary_reports/`, `docs/job_choice/`,
`docs/notes/`, `docs/results/` locations into the matching `docs/France_case/<subdir>/`
locations (collapsed model: one copy per file, not a separate mirror tier).
See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

## Root Project Mirror

| Original | Mirror |
| --- | --- |
| `README.md` | `docs/mirrored/root/README.md` |

## EUROMOD Reference Mirrors

| Original | Mirror |
| --- | --- |
| `Data/documentation/euromod_fr_2015_2017_input_output_reference.md` | `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_output_reference.md` |
| `Data/documentation/euromod_fr_2015_2017_input_variables.csv` | `docs/France_case/euromod_reference/euromod_fr_2015_2017_input_variables.csv` |
| `Data/documentation/euromod_fr_2015_2017_output_variable_index.csv` | `docs/France_case/euromod_reference/euromod_fr_2015_2017_output_variable_index.csv` |
| `Data/documentation/euromod_fr_2015_2017_standard_income_concepts.csv` | `docs/France_case/euromod_reference/euromod_fr_2015_2017_standard_income_concepts.csv` |
| `Data/documentation/FR_2015_index.md` | `docs/France_case/_shared/euromod_reference/FR_2015_index.md` |
| `Data/documentation/FR_2015_all_tables_compact.md` | `docs/France_case/_shared/euromod_reference/FR_2015_all_tables_compact.md` |
| `Data/documentation/FR_2015_index.jsonl` | `docs/France_case/_shared/euromod_reference/FR_2015_index.jsonl` |
| `Data/documentation/DRD_FR_2016_a3_export.txt` | `docs/France_case/euromod_reference/DRD_FR_2016_a3_export.txt` |
| `Data/documentation/DRD_FR_2016_index.jsonl` | `docs/France_case/euromod_reference/DRD_FR_2016_index.jsonl` |

## Canary Report Mirrors

| Original | Mirror |
| --- | --- |
| `Results/RURO_ruro_occ_M0_rebuild_canary_report_v1.md` | `docs/France_case/P3a/canary_reports/RURO_ruro_occ_M0_rebuild_canary_report_v1.md` |

## Job-Choice Documentation Mirrors

| Original | Mirror |
| --- | --- |
| `scripts/Job_model/README_job_model.md` | `docs/France_case/job_model/README_job_model.md` |
| `scripts/Job_model/ACCEPTANCE_TESTS.md` | `docs/France_case/job_model/ACCEPTANCE_TESTS.md` |
| `scripts/Job_model/Commands_job.txt` | `docs/France_case/job_choice/Commands_job.txt` |

## Result And Notes Mirrors

| Original | Mirror |
| --- | --- |
| `outputs/KEEP_RESULTS.md` | `docs/France_case/_shared/results/KEEP_RESULTS.md` |
| `notes/EUROMO_sys_france_2015.md` | `docs/France_case/_shared/notes/EUROMO_sys_france_2015.md` |
| `notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md` | `docs/France_case/_shared/notes/R_REFERENCE_vs_PYTHON_SPECIFICATION.md` |

## Recommended Reading Bundle For France 2016

For writing about France 2016 data, cleaning, estimation, and methodology, use:

1. `docs/methods/RURO_METHODS_AND_PIPELINE_MANUAL_v1.md`
2. `docs/methods/RURO_PREFERENCE_ESTIMATION_CAPABILITIES.md`
3. `docs/methods/RURO_CURRENT_STATE_AND_IDENTIFICATION.md`
4. `docs/methods/RURO_COMMANDS_JOB_MODEL_VS_CONTINUOUS.md`
5. `docs/estimation/RURO_ACTIVE_RESULTS_REGISTRY.md`
6. `docs/France_case/_shared/euromod_reference/euromod_fr_2015_2017_input_output_reference.md`
7. `docs/France_case/euromod_reference/euromod_fr_2015_2017_input_variables.csv`
8. `docs/France_case/euromod_reference/euromod_fr_2015_2017_output_variable_index.csv`
9. `docs/France_case/euromod_reference/euromod_fr_2015_2017_standard_income_concepts.csv`

For the RURO occupation-opportunity baseline, also use:

1. `docs/France_case/P3a/design/RURO_ruro_occ_baseline_spec_v1.md`
2. `docs/France_case/P3a/design/RURO_ruro_occ_baseline_implementation_report_v1.md`
3. `docs/France_case/P3a/design/RURO_ruro_occ_M0_rebuild_command_plan_v1.md`
4. `docs/France_case/P3a/canary_reports/RURO_ruro_occ_M0_rebuild_canary_report_v1.md`

For the GSUR build chain (France), use the consolidated docs:

1. `docs/France_case/_shared/gsur/RURO_GSUR_external_acquisition_consolidated_v1.md`
2. `docs/France_case/P3a/consolidated/RURO_GSUR_rebuild_consolidated_v1.md`
3. `docs/France_case/_shared/gsur/RURO_GSUR_rebuild_specification_v2_1.md` (governing spec, kept standalone)
