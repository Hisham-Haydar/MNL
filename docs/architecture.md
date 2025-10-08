# Architecture Overview

```text
┌───────────────────────────────┐
│           notebooks           │  Exploratory analysis and reporting
└──────────────┬────────────────┘
               │
┌──────────────▼──────────────┐
│          configs            │  YAML configs describing experiments
└──────────────┬──────────────┘
               │ loads
┌──────────────▼──────────────┐       ┌──────────────────────┐
│    src/mnl/config.py        │──────▶│  dataclasses config   │
└──────────────┬──────────────┘       └─────────┬────────────┘
               │ orchestrates                  │
┌──────────────▼──────────────┐       ┌─────────▼────────────┐
│ src/mnl/pipelines/estimation│──────▶│ src/mnl/models/mnl.py│
└──────────────┬──────────────┘       └──────────────────────┘
               │ produces
┌──────────────▼──────────────┐
│   outputs / reports         │
└─────────────────────────────┘

## Packages

- `mnl.data`: readers and preprocessing helpers for panel datasets.
- `mnl.models`: modelling abstractions (MNL now, expandable to nested logit, mixed logit).
- `mnl.pipelines`: orchestration of estimation and evaluation.
- `mnl.evaluation`: reusable metrics.
- `mnl.integration`: bridges to external simulators (EUROMOD connector, future engines).

## Automation

- `scripts/`: command-line entry points for reproducible runs.
- `tests/`: guard rails via `pytest`.

Extend the layout as you add simulation tools (`mnl.simulation`), counterfactual analysis,
and reporting utilities.
