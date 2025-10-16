#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-10-16 18:07:35
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0


# %% Bootstrap (Interactive Window friendly paths and helpers)



import os
import sys
from pathlib import Path
import euromod as em
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    # Fallback when running cells interactively without __file__
    SCRIPT_DIR = Path.cwd() / "scripts"

PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()
os.chdir(PROJECT_ROOT)

SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

try:
    from scratch.my_functions import (
        apply_abnormal_filter,
        compute_wage_recon,
        correct_labor_status,
        apply_filtering_pipeline,
        apply_other_members_filter,
        check_data_quality,
        create_income_columns,
        create_stats_entry,
        export_gender_split_data,
        export_household_data,
        get_head_counts,
        identify_extreme_households,
        log_filtering_step,
        process_couples_data,
        process_singles_data,
        setup_logging,
        validate_household_integrity,
        validate_required_columns,
    )  # type: ignore
except ImportError as e:
    raise ImportError(
        "Missing helpers 'create_income_columns' and 'get_head_counts' in scratch/my_functions.py."
    ) from e

# Canonical project paths
DATA_ROOT = PROJECT_ROOT / "Data"
RAW_DIR = (DATA_ROOT / "raw") if (DATA_ROOT / "raw").exists() else DATA_ROOT
PROCESSED_DIR = DATA_ROOT / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = PROJECT_ROOT / "EUROMOD_RELEASES_J1.0+" / "EUROMOD_RELEASES_J1.0+"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "prep"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = OUTPUTS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

#%% 

