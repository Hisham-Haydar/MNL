# RURO Project Hygiene Cleanup Recommendations

Generated on: 2026-05-11  
Basis: `RURO_MNL_project_files_structure.md`, selected README files, `.gitignore`, and git status.  
Scope: project hygiene and clarity, not primarily disk-size reduction.  
Cleanup status: the first reversible hygiene pass was applied on 2026-05-11; see `docs/France_case/RURO_PROJECT_HYGIENE_CLEANUP_LOG_2026-05-11.md`.

## Executive Recommendation

The project should be cleaned by making one active path obvious and moving everything else into clearly named archive/reference buckets. The main problem is not storage size. The main problem is ambiguity: there are multiple generations of RURO scripts, many root-level runners, many YAML specs, many result folders, and documentation split across root, `docs/`, `notes/`, `scripts/`, and `scratch/`.

Do not run `cleanup_final.ps1` as-is. It is too broad for research-project hygiene because it archives nearly all root markdown and removes `check_*.py`, `diagnose_*.py`, `fix_*.py`, and `test_*.py` patterns without checking whether they are still useful diagnostics. Replace it with a staged cleanup script only after the buckets below are approved.

The clean project should have:

- one canonical continuous-RURO pipeline: `scripts/enhanced/`
- one canonical job-choice RURO pipeline: `scripts/Job_model/`
- one reference folder for the R reference's work: `ruro/`
- one active documentation folder: `docs/`
- one clearly documented results registry for the few outputs that matter
- old scripts, old specs, temporary checks, and experiments moved into archive folders instead of mixed with active work

## Hygiene Goals

1. Make it obvious which scripts should be used for future work.
2. Make it difficult to accidentally run old code.
3. Preserve research history without keeping it in the active path.
4. Keep the R reference work intact as a reference baseline.
5. Keep only a small set of named estimation runs as current baselines.
6. Avoid deleting anything scientifically meaningful before it is labeled and recorded.

## Current Active Core

Keep these as the active project backbone.

### Root

Keep:

- `README.md`
- `requirements.txt`
- `pyproject.toml`
- `.gitignore`

Review but probably keep:

- `TODO.md`: currently useful because it names job-choice next priorities. It should eventually move into `docs/ROADMAP.md` or be linked from `README.md`.
- `DONE.md`: useful implementation history, but better as `docs/archive/implementation_history/DONE.md` after the active README is updated.

Root should not contain many one-off scripts, old design docs, or runner variants. Those make the project look less stable than it is.

### Active Continuous RURO Pipeline

Keep as active:

- `scripts/enhanced/run_enhanced_pipeline.ps1`
- `scripts/enhanced/enh_pipeline.ps1`
- `scripts/enhanced/enh_france_data_prep.py`
- `scripts/enhanced/enh_prepare_FR_gsur.py`
- `scripts/enhanced/enh_RURO_prep.py`
- `scripts/enhanced/enh_RURO_draws.py`
- `scripts/enhanced/enh_RURO_euromod.py`
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py`
- `scripts/enhanced/enh_RURO_estimate_FR.py`
- `scripts/enhanced/enh_RURO_post_estimation.py`
- `scripts/enhanced/RURO_post_estimation_styled.py`

Keep as active shared estimation infrastructure:

- `scripts/enhanced/gamspy_estimation_vectorized.py`
- `scripts/enhanced/gamspy_estimation.py`
- `scripts/enhanced/estimation_engine.py`
- `scripts/enhanced/estimation_utils.py`
- `scripts/enhanced/estimation_spec_parser.py`
- `scripts/enhanced/expression_constraints.py`
- `scripts/enhanced/path_helpers.py`
- `scripts/enhanced/sanity_checks.py`
- `scripts/enhanced/validate_specs.py`
- `scripts/enhanced/compute_standard_errors.py`

Keep as supporting utilities:

- `scripts/enhanced/reduce_draws_files.py`
- `scripts/enhanced/reduce_mnl_columns.py`
- `scripts/enhanced/quick_verify.py`
- `scripts/enhanced/diagnostic_consumption_variation.py`
- `scripts/enhanced/fix_spec_initial_values.py`

Review whether still active:

- `scripts/enhanced/estimation_utils_AC2013.py`
- `scripts/enhanced/mcfadden_sampler.py`
- `scripts/enhanced/occupation_choice_utils.py`
- `scripts/enhanced/parallel_estimation.py`
- `scripts/enhanced/checking.ipynb`

These are not necessarily bad files, but they should be labeled as active, experimental, or archived.

### Active Job-Choice RURO Pipeline

Keep as active:

- `scripts/Job_model/run_job_ruro_pipeline.py`
- `scripts/Job_model/enh_job_universe.py`
- `scripts/Job_model/enh_job_draws.py`
- `scripts/Job_model/sanity_checks_job.py`
- `scripts/Job_model/README_job_model.md`
- `scripts/Job_model/ACCEPTANCE_TESTS.md`

Review:

- `scripts/Job_model/Commands_job.txt`: move into README or `docs/archive/commands/`.
- `scripts/Job_model/New Text Document.txt`: rename if useful, otherwise archive/remove.
- `scripts/Job_model/plot_loc_by_dehde.py`: keep if still used for diagnostics; otherwise move to `scripts/diagnostics/`.

### Current Estimation Specs

Keep these immediately visible:

- `scripts/enhanced/estimation_spec_job_M2h_pruned.yaml`: current best job-choice/pruned spec candidate.
- `scripts/enhanced/estimation_spec_job_M2e_a.yaml`: important parent/warm-start/comparison spec.
- `scripts/enhanced/estimation_spec_v3.yaml`: current richer continuous RURO exploratory spec.
- `scripts/enhanced/estimation_spec_v2.yaml`: important previous continuous RURO reference.
- `scripts/enhanced/estimation_spec.yaml`: historical/default continuous spec, but clarify whether it is still canonical.

Recommended hygiene change:

Create:

```text
scripts/enhanced/specs/
  active/
  archive/
  experiments/
```

Then move or copy specs into those buckets. The current flat list has too many similarly named YAML files, making it easy to use the wrong model.

Suggested active spec bucket:

```text
scripts/enhanced/specs/active/
  estimation_spec_job_M2h_pruned.yaml
  estimation_spec_job_M2e_a.yaml
  estimation_spec_v3.yaml
  estimation_spec_v2.yaml
```

Suggested archive/spec-history bucket:

```text
scripts/enhanced/specs/archive/
  estimation_spec_job_choice_v0_*.yaml
  estimation_spec_job_M0.yaml
  estimation_spec_job_M1.yaml
  estimation_spec_job_M2*.yaml except the active M2 specs
  estimation_spec_minimal*.yaml
  estimation_spec_pooled_*.yaml
  estimation_spec_simple.yaml
  estimation_spec_ultra_minimal.yaml
```

Do not delete old specs before adding a short `specs/README.md` explaining what each active spec is for.

### Data and Reference Inputs

Keep:

- `Data/external/`
- `Data/documentation/`
- `Data/README.md`
- `literature/`
- `ruro/`

Rationale:

- `Data/external/` contains small input/reference files such as GSUR, CPI, and SMIC files.
- `Data/documentation/` contains extracted EUROMOD documentation and indexes.
- `literature/` is reference material.
- `ruro/` is the reference implementation and should stay intact.

Do not mix generated processed datasets into this project folder. The large processed data should remain on `Z:/Hisham` or `U:/EUROMOD-STORAGE` and be referenced by path.

## Current Output Baselines to Keep

The project should keep only a small, named set of output runs as active baselines. Everything else can stay archived for now, but future work should point to the registry instead of browsing hundreds of timestamp folders.

Create:

```text
outputs/KEEP_RESULTS.md
```

Recommended active baseline entries:

1. Job-choice current candidate:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/
```

2. Job-choice parent/comparison:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46/
```

3. Continuous RURO v3 exploratory baseline:

```text
outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
```

For each registry entry, record:

- model family: continuous RURO or job-choice RURO
- spec file used
- MNL base path
- solver
- whether vectorized GAMSPy was used
- whether proposal correction was active
- final log likelihood
- convergence status
- known warnings
- matching post-estimation report path

This is a hygiene step, not a size step. The point is to make the relevant scientific results discoverable.

## Move to Archive, Not Delete

These should be moved out of the active path but preserved.

### Old Script Generations

Move:

```text
scripts/Old_Script_ruro(not well)/
```

to something like:

```text
scripts/archive/old_ruro_pre_enhanced/
```

Reason: the name itself signals that it is not active, but its current location under `scripts/` makes it look like a peer of the active pipeline.

Keep `scripts/archive/` but add:

```text
scripts/archive/README.md
```

with this rule:

> Files in this folder are not active pipeline entrypoints. They are retained for provenance and comparison only.

### Legacy Root Pipeline Scripts

Move these from root into `scripts/archive/root_runners_legacy/` or `scripts/runners/legacy/`:

- `run_gamspy_estimation.ps1`
- `RUN_NOW.ps1`
- `RUN_OPTIMIZED_ESTIMATION.ps1`
- `RUN_PIPELINE_WITH_REDUCED_FILES.ps1`
- `RUN_POST_ESTIMATION_STYLED.ps1`
- `RUN_WITH_SCIPY.ps1`

Reason: future work should use `scripts/enhanced/run_enhanced_pipeline.ps1` for the continuous pipeline and `scripts/Job_model/run_job_ruro_pipeline.py` for the job-choice pipeline. Multiple root-level runners make it unclear which path is official.

If one root runner is kept for convenience, keep only one, name it clearly, and make it call the canonical script.

### Root Diagnostic Scripts

Move to `scripts/diagnostics/` if still useful, otherwise archive:

- `check_nchildren_simple.py`
- `check_nchildren_variation.py`
- `check_nchildren_variation_v2.py`
- `check_preference_diagnostics.py`
- `check_type_ids.py`
- `compare_scipy_gamspy.py`
- `test_gamspy_vs_scipy.py`

Reason: these are useful research diagnostics, but root-level placement makes them look like part of the main pipeline. They should be explicitly diagnostics or tests.

Possible target:

```text
scripts/diagnostics/
  check_preference_diagnostics.py
  compare_scipy_gamspy.py
  check_type_ids.py
  check_nchildren_*.py
```

If `test_gamspy_vs_scipy.py` is intended as an automated test, move it to:

```text
tests/test_gamspy_vs_scipy.py
```

If it is a manual comparison script, move it to:

```text
scripts/diagnostics/compare_gamspy_scipy.py
```

### Root Documentation

Move old implementation/design notes from root into `docs/archive/` or `docs/design/`.

Likely archive:

- `IMPLEMENTATION_SUMMARY.md`
- `JOB_CHOICE_MODEL_DIAGNOSIS.md`
- `JOB_CHOICE_PIPELINE.md`
- `JOB_CHOICE_PIPELINE_WALKTHROUGH.md`
- `OCCUPATION_CHOICE_AGNOSTIC_DESIGN.md`
- `OCCUPATION_CHOICE_DESIGN.md`
- `OCCUPATION_CHOICE_MATHEMATICAL_SPECIFICATION.md`
- `OCCUPATION_CHOICE_SUMMARY.md`
- `OCCUPATION_VS_EDUCATION_CHOICE.md`
- `POST_ESTIMATION_IMPROVEMENTS.md`
- `VECTORIZED_IMPLEMENTATION_STATUS.md`

Suggested structure:

```text
docs/
  README.md
  current/
  design/
  archive/
    implementation_history/
    old_job_choice_notes/
    occupation_choice_notes/
```

Do not delete these documents. They contain research and implementation history. The hygiene issue is that they are in the root and compete with the current README.

### Scratch

Move:

```text
scratch/
```

to:

```text
docs/archive/scratch_2026-05-11/
```

or:

```text
scripts/archive/scratch_2026-05-11/
```

Review contents first:

- `scratch/my_functions.py`
- `scratch/Ruro_estimation_new.Rmd`
- `scratch/RURO_post_estimation_OLD_backup_20251208.py`

Reason: `scratch/` is ambiguous. It includes a R reference Rmd copy and an old post-estimation backup. If the files are reference material, archive them with a note. If duplicated exactly elsewhere, they can later be deleted after comparison.

## Safe to Remove After Confirmation

These are hygiene removals because they are generated, accidental, or redundant. They should be deleted only after you approve.

### Accidental or Generated Local Files

Safe to remove from the project folder:

- `_gams_work/`: solver work directory, regenerable.
- `Microsoft/Windows/PowerShell/ModuleAnalysisCache`: appears accidentally created under the project root.
- `.ruff_cache/`: local cache.
- `.mplconfig/`: local matplotlib config/cache unless intentionally needed.
- `src/mnl.egg-info/`: generated package metadata.
- `reports/`: currently empty in the inventory.
- `logs/commands_20260122_143200.txt`: old command log, archive first if useful.

Keep local IDE folders only if you want machine-specific settings:

- `.vscode/`
- `.idea/`
- `.claude/`

If this project is shared through git, these should normally be ignored and not treated as project source.

### Backup Files

Review and then remove or archive:

- `scripts/enhanced/estimation_spec.yaml.backup`
- `scripts/enhanced/estimation_spec_loc_empirical.yaml.backup`
- `scripts/RURO_estimate_FR.py.backup_20251216_143415`

Hygiene rule: do not keep backup files next to active code. If the backup has unique historical value, move it to `scripts/archive/backups_2025_12/`; otherwise remove it.

### Generated Inventory

The file:

```text
RURO_MNL_project_files_structure.md
```

is useful for this cleanup session but should not remain as a root project artifact. After the cleanup is complete, either delete it or move it to:

```text
docs/archive/inventories/RURO_MNL_project_files_structure_2026-05-11.md
```

Also add this pattern to `.gitignore` if you keep regenerating it:

```gitignore
RURO_MNL_project_files_structure*.md
```

## Review Before Moving or Removing

These areas should not be cleaned mechanically.

### `src/`

Current status:

- `src/mnl/` is a small Python package skeleton.
- The real active pipeline currently lives mostly in `scripts/enhanced/` and `scripts/Job_model/`.

Recommendation:

Keep `src/`, but decide its role:

1. If the goal is a package-based project, gradually migrate stable utilities from `scripts/enhanced/` into `src/mnl/`.
2. If the goal is a script-based research project, mark `src/` as experimental/package skeleton and do not pretend it is the active pipeline.

Do not delete it now.

### `notebooks/`

Current:

- `notebooks/estimation_notebook.ipynb`
- `notebooks/README.md`

Recommendation:

Keep if it is used for interactive explanation or exploration. If it is stale, move to:

```text
docs/archive/notebooks/
```

Because notebooks are ignored by `.gitignore`, do not rely on them as the only record of important logic.

### `outputs/`

Do not bulk-delete outputs for hygiene. First create `outputs/KEEP_RESULTS.md`, then optionally archive or delete old runs. The hygiene problem is discoverability, not simply size.

Recommended output policy:

- Active/current runs: listed in `outputs/KEEP_RESULTS.md`.
- Old runs: remain in `outputs/archive/` or stay in place but are not referenced.
- Failed/incomplete runs: delete after confirmation if they contain only logs and no results.
- Huge logs: delete if the run has no scientific result.

The inventory shows one failed or runaway log:

```text
outputs/estimates/fr/2016_gamspy/run_2026-01-17_01-24-03/estimation.log
```

It is about 405 MB and contains no result files in the inventory. It is a good candidate for deletion after confirmation, but it is a size cleanup item rather than the main hygiene concern.

## Proposed Clean Layout

Target layout:

```text
MNL/
  README.md
  requirements.txt
  pyproject.toml
  configs/
  Data/
    external/
    documentation/
  docs/
    README.md
    current/
    design/
    archive/
  literature/
  scripts/
    enhanced/
      specs/
        active/
        experiments/
        archive/
    Job_model/
    diagnostics/
    runners/
    archive/
  src/
  ruro/
  tests/
  outputs/
    KEEP_RESULTS.md
```

This keeps the research history but makes the active path visible.

## Recommended Staged Cleanup Plan

### Stage 1: Label the Active Pipeline

Create or update:

- `docs/PIPELINE_ENTRYPOINTS.md`
- `outputs/KEEP_RESULTS.md`
- `scripts/enhanced/specs/README.md`

These files should answer:

- Which script do I run for continuous RURO?
- Which script do I run for job-choice RURO?
- Which YAML spec is current?
- Which output run is the current baseline?
- Which output run is the comparison baseline?

### Stage 2: Move Root Clutter

Move root runner scripts into `scripts/runners/legacy/` unless one is kept as a convenience wrapper.

Move root diagnostic scripts into `scripts/diagnostics/`.

Move root design/implementation markdown into `docs/archive/` or `docs/design/`.

After this stage, the root should mainly contain:

```text
README.md
requirements.txt
pyproject.toml
TODO.md or docs/ROADMAP.md
```

### Stage 3: Clean Script Namespaces

Move:

```text
scripts/Old_Script_ruro(not well)/
```

into:

```text
scripts/archive/old_ruro_pre_enhanced/
```

Add archive README files so future readers know these are not active.

### Stage 4: Organize Specs

Create spec buckets and move YAML files into:

```text
scripts/enhanced/specs/active/
scripts/enhanced/specs/experiments/
scripts/enhanced/specs/archive/
```

Then update commands and README references so active commands do not point to stale spec paths.

### Stage 5: Mark Outputs

Create `outputs/KEEP_RESULTS.md`.

Only after that, archive/delete older runs if desired.

### Stage 6: Remove Generated/Accidental Files

Remove or ignore:

- `_gams_work/`
- `Microsoft/`
- `.ruff_cache/`
- `.mplconfig/`
- `src/mnl.egg-info/`
- empty `reports/`
- old generated inventory files

This is the only stage where deletion is straightforward.

## `.gitignore` Hygiene

The current `.gitignore` already ignores many generated and data-heavy artifacts, including `.venv/`, `outputs/`, `logs/`, `Data/`, images, PDFs, CSVs, Excel files, notebooks, and logs.

Recommended additions:

```gitignore
# generated project inventories
RURO_MNL_project_files_structure*.md

# solver working directories
_gams_work/

# accidental local cache/config folders
Microsoft/
.mplconfig/
.claude/
.idea/
.vscode/

# generated package metadata
src/*.egg-info/
```

Review before adding `.vscode/` if you intentionally want shared VS Code settings.

## Concrete Keep / Move / Remove Summary

### Keep Active

- `scripts/enhanced/`
- `scripts/Job_model/`
- `ruro/`
- `Data/external/`
- `Data/documentation/`
- `literature/`
- `docs/`
- `src/`
- `tests/`
- `README.md`
- `requirements.txt`
- `pyproject.toml`

### Move for Hygiene

- root `RUN_*.ps1` and old root runners
- root `check_*.py`, `compare_scipy_gamspy.py`, `test_gamspy_vs_scipy.py`
- root design/history markdown files
- `scripts/Old_Script_ruro(not well)/`
- `scratch/`
- backup files if they have historical value
- old specs after active specs are documented

### Remove After Confirmation

- `_gams_work/`
- `Microsoft/`
- `.ruff_cache/`
- `.mplconfig/`
- `src/mnl.egg-info/`
- empty `reports/`
- generated inventory file after archiving
- giant failed-run logs with no result files
- backup files after comparing them with current files

### Do Not Touch Yet

- `ruro/`
- active specs until commands are updated
- `outputs/` until `outputs/KEEP_RESULTS.md` exists
- `src/` until you decide whether the project is package-first or script-first

## My Suggested Next Action

The safest next action is to create the registry and labels first, then move files.

Recommended first commit of cleanup work:

1. Add `outputs/KEEP_RESULTS.md`.
2. Add `docs/PIPELINE_ENTRYPOINTS.md`.
3. Add `scripts/archive/README.md`.
4. Add `scripts/diagnostics/README.md`.
5. Add `.gitignore` hygiene patterns.

Only after that should files be moved. This avoids losing context and makes the cleanup auditable.
