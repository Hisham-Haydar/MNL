# Environment Setup Guide

This project combines econometric estimation in Python with tax-benefit simulations using
EUROMOD. The steps below describe how to configure a reproducible environment on Windows.

## 1. Python Environment

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
2. Create and activate a virtual environment (PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   ```

3. Install the project in editable mode with all research extras (includes `pybiogeme` and the
   EUROMOD Python connector):

   ```powershell
   pip install -e ".[dev,notebook,advanced,euromod]"
   ```

   - `dev` installs linting (`ruff`), testing (`pytest`), typing (`mypy`).
   - `notebook` adds Jupyter tooling.
   - `advanced` brings in `pybiogeme` and `pyblp` for structural estimators.
   - `euromod` installs the official Python bindings (`euromod`), which require the desktop
     application and DLLs to be available.

4. (Optional) register a Jupyter kernel:

   ```powershell
   python -m ipykernel install --user --name mnl --display-name "MNL"
   ```

## 2. EUROMOD Installation

EUROMOD is a standalone microsimulation platform distributed by the EU Joint Research Centre.
It is not published on PyPI and must be obtained directly from the maintainers.

1. **Request EUROMOD access** (if you do not already have a licence) via the
   [JRC EUROMOD portal](https://euromod-web.jrc.ec.europa.eu/).
2. Download and install the latest EUROMOD release (Windows installer). The default installation
   path is typically `C:\Program Files\EUROMOD`.
3. During installation, enable the **Command-line interface** component so you can run batch
   simulations without the GUI.
4. Add the EUROMOD executable directory to your `PATH` so scripts can invoke it:

   ```powershell
   setx PATH "$Env:PATH;C:\Program Files\EUROMOD\bin"
   ```

5. If EUROMOD is installed in a non-default location, expose it to the Python package:

   ```powershell
   setx EUROMOD_PATH "D:\Tools\EUROMOD\Executable"
   ```

   When you rely on the wheel-bundled runtime (no desktop install), point the variable to the
   library folder shipped with the package:

   ```powershell
   setx EUROMOD_PATH "%CD%\.venv\Lib\site-packages\euromod\libs"
   ```

   (Replace `%CD%` with the absolute project path if you activate the environment elsewhere.)

6. Verify the installation:

   ```powershell
   euromod-cli --help
   ```

7. Document your country-specific policies, baseline input data, and output folders under
   `docs/euromod/` (create the directory if needed). Store the EUROMOD projects themselves outside
   the git repository because they often contain licensed microdata.

### Python ⇄ EUROMOD Bridge

EUROMOD can be automated from Python via command-line calls or (for some versions) the COM
interface. Plan to:

1. Export policy scenarios as EUROMOD release folders (model XML, Input, etc.).
2. Drive EUROMOD runs with the Python bindings:

   ```powershell
   python scripts/run_euromod.py `
     --model-dir "C:\EUROMOD_RELEASE" `
     --country DE `
     --system DE_2023 `
     --dataset EU_SILC_2021 `
     --output-dir outputs/euromod
   ```

   - Add `--input-data my_panel.csv` to override the official dataset with a cleaned dataframe.
   - Use repeated `--option key=value` flags to pass advanced arguments to `System.run`.
3. Collect EUROMOD outputs (typically CSV or text) into `Data/processed/` and merge the simulated
   disposable income with your labour-supply model inputs.

## 3. Biogeme

`pybiogeme` is installed via the `advanced` extra. Validate the installation with:

```powershell
python -c "import biogeme"
```

If you prefer a Conda environment (recommended when compiling large-scale estimators):

```powershell
conda create -n mnl python=3.10
conda activate mnl
pip install -e ".[dev,notebook,advanced,euromod]"
```

Biogeme also offers a standalone GUI for specification debugging—download it from
[biogeme.epfl.ch](https://biogeme.epfl.ch/) if desired.

## 4. Data Dictionary (DRD_DE_2015_a1.xls)

The `.xls` file describes the variables present in `Data/DE_2015_a1.txt`.

- Keep the raw dictionary under `docs/data_dictionary/` (create the folder and copy the file).
- Convert it to a CSV or Markdown summary for quick reference:

  ```powershell
  python scripts/extract_dictionary.py Data/DRD_DE_2015_a1.xls docs/data_dictionary/de_2015_dictionary.csv
  ```

  (Create `scripts/extract_dictionary.py` to parse the Excel workbook and export a clean
  column-reference table.)

- Track any transformations applied during preprocessing in `docs/data_catalog.md`.

## 5. Validation Checklist

After completing the installation:

- `python -c "import mnl, biogeme"` should terminate silently.
- `python -c "import euromod"` should succeed (set `EUROMOD_PATH` if DLLs cannot be located).
- `pytest` should succeed (initial suite is minimal).
- `euromod-cli` should launch from the terminal.
- Document software versions in `docs/environment_setup.md` to support reproducibility.

Once those items pass, you can start building the counterfactual income simulations and feeding
their outputs into the discrete-choice estimation pipelines.
