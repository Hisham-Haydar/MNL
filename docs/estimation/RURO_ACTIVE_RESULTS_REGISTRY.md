# RURO Active Results Registry

This file identifies the estimation outputs that are currently meaningful for interpretation and comparison. The goal is to avoid browsing many timestamped output folders to guess which run matters.

> **Certified baseline (updated 2026-07-22).** The **sole certified baseline** is `joint_pooled_v1_bll0_tlmpin` — 47-param, France 2015–2017 pooled, **JAX**, singles 101 / couples 901, **negLL 238504.6360973987**, synthetic-recovery certified, real-data Hessian positive definite, clustered on `idorighh`. Provenance: `docs/France_case/P3a/execution_logs/Bpool/RURO_realdata_2016_2017_joint_901_v1.md`; spec `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`; theta `scripts/bpool/specs/theta_hat_realdata_901_v1.csv`.
>
> **The GAMSPy job-choice and continuous-RURO runs listed below are LEGACY / provenance**, superseded by the certified JAX baseline. They are retained for history and comparison only and must **not** be read as the active baseline. This registry predates the certified baseline and has not otherwise been rewritten.
>
> The FR-2016 singles **P2a** track (`outputs/p2a_singles2016/`) is a **separate provisional** track, not the certified pooled baseline; its region-live result (negLL ~19053.4655) is awaiting a production rebuild (see `dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md`).

## Current Baseline Runs (LEGACY — see certified-baseline banner above)

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

## Candidate Runs To Review Before Cleanup

### Job-Choice RURO: Later M2e_b Candidate

Path:

```text
outputs/estimates/fr/spec/job_choice/gamspy/estimation_spec_job_M2e_b/run_2026-02-20_11-24-37/
```

Observed in the 2026-05-12 storage audit:

- timestamp in `estimation_results.json`: `2026-02-20T11:51:26`
- spec: `scripts/enhanced/estimation_spec_job_M2e_b.yaml`
- joint log-likelihood: `-22161.05`
- complete result folder with summary and diagnostics

Role:

- Later than the currently registered M2h pruned run.
- Do not delete during cleanup until it is reviewed.
- Promotion should not be based on log-likelihood alone; check identification diagnostics, bound hits, Hessian, parameter interpretation, and whether it matches the intended opportunity specification.

## Full Result Inventory

The 2026-05-12 audit summarized repository estimation outputs in:

```text
docs/archive/inventories/external_storage_2026-05-12/repo_estimation_results_summary_2026-05-12.csv
docs/archive/inventories/external_storage_2026-05-12/repo_estimation_runs_inventory_2026-05-12.csv
```

Observed counts:

```text
estimation run directories: 168
runs with estimation_results.json summarized: 115
```

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
