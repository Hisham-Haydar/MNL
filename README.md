# RURO Labor Supply Model - France

This repository contains the Python implementation of the French RURO labor-supply work, including the continuous RURO pipeline, the job-choice RURO branch, GAMSPy estimation, post-estimation reporting, and references to Stijn's R implementation.

## Start Here

Active entrypoints:

- [docs/PIPELINE_ENTRYPOINTS.md](docs/PIPELINE_ENTRYPOINTS.md)
- [docs/RURO_ACTIVE_RESULTS_REGISTRY.md](docs/RURO_ACTIVE_RESULTS_REGISTRY.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [scripts/enhanced/README.md](scripts/enhanced/README.md)
- [scripts/Job_model/README_job_model.md](scripts/Job_model/README_job_model.md)

Cleanup rationale:

- [docs/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md](docs/RURO_PROJECT_HYGIENE_CLEANUP_RECOMMENDATIONS.md)

## Main Commands

Continuous RURO pipeline:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\enhanced\run_enhanced_pipeline.ps1
```

Job-choice RURO pipeline:

```powershell
python scripts\Job_model\run_job_ruro_pipeline.py
```

Post-estimation reporting:

```powershell
python scripts\enhanced\RURO_post_estimation_styled.py --help
```

## Project Layout

```text
MNL/
  configs/                 Configuration files
  Data/                    Small external/reference inputs and documentation
  docs/                    Current documentation and archived notes
  literature/              Papers and external references
  outputs/                 Ignored generated outputs; see KEEP_RESULTS.md
  scripts/enhanced/        Active continuous RURO pipeline and estimation code
  scripts/Job_model/       Active job-choice RURO pipeline
  scripts/diagnostics/     Manual checks and comparison scripts
  scripts/runners/legacy/  Old root-level runner scripts
  scripts/archive/         Legacy scripts, backups, and old approaches
  src/                     Package skeleton / reusable code area
  stijn/                   Stijn's R reference implementation
  tests/                   Automated tests
```

## Current Result Baselines

The active results are documented in:

- [docs/RURO_ACTIVE_RESULTS_REGISTRY.md](docs/RURO_ACTIVE_RESULTS_REGISTRY.md)

Do not infer the current baseline by browsing timestamped folders manually. Promote important runs into the registry first.

## Reference Work

Stijn's files are kept intact in `stijn/`:

- `stijn/Ruro_estimation_H.Rmd`
- `stijn/Ruro_estimation_new.Rmd`
- `stijn/Ruro_functions_EMRWS.R`
- `stijn/Ruro_simulation_H.Rmd`

Older Python design notes, implementation history, root runner scripts, and scratch files were moved to archive folders during the 2026-05-11 hygiene cleanup.

