"""
Interactive runner that mirrors the RURO_prep → RURO_draws → RURO_euromod
function calls, but exposes each helper function as a separate cell.

Use in an IDE that supports #%% cells (VS Code, Spyder, PyCharm). Execute the
cells in order to reproduce Steps 2–4 of run_fr_2016_joint_only.ps1 while
inspecting intermediate outputs.
"""

#%% Imports and sys.path setup
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

if "__file__" in globals():
    SCRIPT_DIR = Path(__file__).resolve().parent
else:
    SCRIPT_DIR = Path.cwd()

if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


#%% Configuration (edit paths/parameters as needed)
PROJECT_ROOT = Path(r"U:\Desktop\Nizam_Hisham\MNL").resolve()
DATA_ROOT = Path(r"U:\EUROMOD-STORAGE\Data").resolve()
PROC = DATA_ROOT / "processed" / "fr" / "2016"
SCENARIO_DIR = Path(r"U:\EUROMOD-STORAGE\interim\ruro\fr\scenarios_2016")
RAW_MICRODATA = DATA_ROOT / "raw" / "FR_2016.txt"
EUROMOD_ROOT = Path(r"U:\EUROMOD-STORAGE\EUROMOD_RELEASES_J1.0+\EUROMOD_RELEASES_J1.0+")

YEAR = 2016
SYSTEM_YEAR = 2015
COUNTRY = "FR"
N_DRAWS = 99
WAGE_SPEC = "vw"

SCENARIO_DIR.mkdir(parents=True, exist_ok=True)


#%% RURO_prep – resolve processed directory
from RURO_prep import (
    _resolve_processed_dir,
    _load_filtered_data,
    _add_ruro_variables_basic,
    _maybe_add_column,
)

processed_dir = _resolve_processed_dir(PROC, base_year=YEAR)
print("Resolved processed dir:", processed_dir)


#%% RURO_prep – load singles/couples parquet files
singles_df, couples_df = _load_filtered_data(processed_dir)
print(f"Loaded singles: {singles_df.shape}, couples: {couples_df.shape}")


#%% RURO_prep – add RURO variables (singles)
singles_ruro = _add_ruro_variables_basic(singles_df.copy(), default_year=YEAR)
_maybe_add_column(singles_ruro, "ruro_sample", 1)
print("Singles RURO columns:", singles_ruro.columns.tolist()[:15])


#%% RURO_prep – add RURO variables (couples)
couples_ruro = _add_ruro_variables_basic(couples_df.copy(), default_year=YEAR)
_maybe_add_column(couples_ruro, "ruro_sample", 1)
print("Couples RURO columns:", couples_ruro.columns.tolist()[:15])


#%% RURO_prep – write RURO_ready parquet files
singles_out = processed_dir / "singles_RURO_ready.parquet"
couples_out = processed_dir / "couples_RURO_ready.parquet"
singles_ruro.to_parquet(singles_out, index=False)
couples_ruro.to_parquet(couples_out, index=False)
print("Wrote:", singles_out, couples_out)


#%% RURO_draws – prepare singles draws step-by-step
from RURO_draws import _attach_other_members_income, generate_draws_long

singles_ready = pd.read_parquet(singles_out)
singles_ready = _attach_other_members_income(singles_ready)
singles_draws = generate_draws_long(
    singles_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=12345,
)
singles_draws_out = processed_dir / "singles_RURO_ready_RURO_draws.parquet"
singles_draws.to_parquet(singles_draws_out, index=False)
print(f"Singles draws rows: {len(singles_draws):,}")


#%% RURO_draws – prepare couples draws step-by-step
couples_ready = pd.read_parquet(couples_out)
couples_ready = _attach_other_members_income(couples_ready)
couples_draws = generate_draws_long(
    couples_ready,
    n_draws=N_DRAWS,
    wage_spec=WAGE_SPEC,
    rng_seed=67890,
)
couples_draws_out = processed_dir / "couples_RURO_ready_RURO_draws.parquet"
couples_draws.to_parquet(couples_draws_out, index=False)
print(f"Couples draws rows: {len(couples_draws):,}")


#%% RURO_euromod – read draws and prepare combined DataFrame
from RURO_euromod import run_euromod_for_draws, _read_microdata_file

singles_draws_df = pd.read_parquet(singles_draws_out)
couples_draws_df = pd.read_parquet(couples_draws_out)
combined_draws_df = pd.concat([singles_draws_df, couples_draws_df], ignore_index=True)
print("Combined draws shape:", combined_draws_df.shape)


#%% RURO_euromod – inspect baseline microdata columns
micro_template_df = _read_microdata_file(RAW_MICRODATA)
print("EUROMOD template columns (sample):", micro_template_df.columns[:10])


#%% RURO_euromod – run EUROMOD using helper function
combined_output_path = run_euromod_for_draws(
    combined_draws_df,
    RAW_MICRODATA,
    country=COUNTRY,
    system_code=f"{COUNTRY}_{SYSTEM_YEAR}",
    dataset_name=f"{COUNTRY}_{YEAR}",
    em_root=EUROMOD_ROOT,
    scenario_dir=SCENARIO_DIR,
)
print("EUROMOD combined output:", combined_output_path)
