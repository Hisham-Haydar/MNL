# RURO Active Results Registry

This file identifies the estimation outputs that are currently meaningful for interpretation and comparison. The goal is to avoid browsing many timestamped output folders to guess which run matters.

## Current Baseline Runs

### 1. Job-Choice RURO: Current Pruned Candidate

Path:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2h_pruned/run_2026-02-20_11-25-18/
```

Expected key files:

- `estimation_results.json`
- `estimation_summary.txt`
- `identification_diagnostics.txt`
- `specification_used.yaml`

Role:

- Current compact job-choice candidate.
- Useful baseline for future sector/opportunity extensions.

### 2. Job-Choice RURO: Parent / Comparison Candidate

Path:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_a/run_2026-02-20_10-04-46/
```

Expected key files:

- `estimation_results.json`
- `estimation_summary.txt`
- `identification_diagnostics.txt`
- `specification_used.yaml`

Role:

- Comparison run for the M2h pruned candidate.
- Useful warm-start/reference point for job-choice specification changes.

### 3. Continuous RURO: v3 Exploratory Baseline

Path:

```text
outputs/estimates/fr/spec/v3/gamspy/run_2026-02-05_14-11-43/
```

Expected key files:

- `estimation_results.json`
- `estimation_summary.txt`
- `specification_used.yaml`

Role:

- Rich continuous-RURO reference run.
- Useful when comparing the continuous opportunity approach with the job-choice/discrete opportunity approach.

## Registry Rules

For every run promoted to active status, record:

- model family: continuous RURO or job-choice RURO
- spec file used
- MNL base path
- solver
- vectorized or non-vectorized estimator
- proposal correction status
- final log likelihood
- convergence status
- known warnings
- matching post-estimation report path

Do not delete old output folders until the relevant baseline, comparison, and failed-run information has been recorded here or in a linked archive note.

