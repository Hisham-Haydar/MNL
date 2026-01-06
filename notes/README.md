# Structural Discrete-Choice Modelling Toolkit

This repository provides a reproducible starting point for estimating structural discrete-choice
models (multinomial logit, mixed logit, BLP) on panel data. It emphasises traceability of data
transformations, modular pipelines, and automation-friendly tooling.

## Repository Layout

```text
├── Data/                 # Raw/interim/processed datasets (kept out of version control)
├── configs/              # YAML experiment definitions
├── docs/                 # Architecture notes, data catalogue, research diary
├── notebooks/            # Exploratory analysis and reporting notebooks
├── scripts/              # CLI entry points for end-to-end runs
├── src/mnl/              # Python package with reusable modelling code
└── tests/                # Pytest-based regression checks
```

Extend the layout with `reports/`, `dashboards/`, or `experiments/` as your workflow evolves.

## Getting Started

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
   ```

2. **Install the project in editable mode**

   ```bash
   pip install --upgrade pip
   pip install -e ".[dev,notebook,advanced,euromod]"
   ```

   - Add the `advanced` extra for industrial-scale solvers such as `pyblp` and `pybiogeme`.
   - Add the `euromod` extra for the official EUROMOD Python bindings (requires the desktop app).

3. **Register the IPython kernel** (optional)

   ```bash
   python -m ipykernel install --user --name mnl --display-name "MNL"
   ```

## Data Management

- Store source files in `Data/raw/`. Keep them immutable and document provenance in
  `docs/data_catalog.md`.
- Place intermediate outputs in `Data/interim/` and publish analysis-ready panels to
  `Data/processed/`.
- Update `configs/default.yaml` (or a new config file) with the processed dataset path.
- Consider creating lightweight `pandas`-based data validation scripts and committing summary
  statistics to `docs/`.

> ⚠️ The repository `.gitignore` excludes interim and processed data to avoid leaking proprietary
> datasets. Version CSV schemas and documentation instead of the raw files.

## Running the Pipeline

With the environment activated and `Data/processed/choice_panel.csv` prepared:

```bash
python scripts/train_mnl.py \
  --config configs/default.yaml \
  --save-probabilities outputs/probabilities.csv
```

The script outputs core metrics to stdout and writes predicted probabilities when requested.
Adapt the pipeline by creating a new config file (e.g. `configs/mixed_logit.yaml`) or by
subclassing/adding estimators under `src/mnl/models/`.

## Development Workflow

- **Lint & format**: `ruff check src tests` (add `--fix` to auto-format).
- **Type-check**: `mypy src`.
- **Test**: `pytest`.
- **Pre-commit**: Install hooks via `pre-commit install` to enforce checks locally.
- **EUROMOD runs**: `python scripts/run_euromod.py --model-dir <release> --country DE --system DE_2023 --dataset EU_SILC --output-dir outputs/euromod`.

Configure Continuous Integration (e.g. GitHub Actions) to run the same commands on every push.

## Next Steps

1. Profile and clean the delivered dataset into `Data/processed/choice_panel.csv`.
2. Expand `src/mnl/data/` with feature engineering pipelines tailored to your instruments.
3. Implement richer models (nested logit, mixed logit) and corresponding evaluation suites.
4. Add experiment tracking (Weights & Biases, MLflow, or simple CSV logs) for transparency.
5. Layer reproducible reporting via Jupyter Book, Quarto, or a lightweight dashboard framework.

Track open questions and modelling decisions in `docs/` so research context remains discoverable.
