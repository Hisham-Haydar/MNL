# %% Imports and path setup
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:  # Running from an interactive cell where __file__ is undefined
    PROJECT_ROOT = Path.cwd()
    if not (PROJECT_ROOT / "scripts").exists() and (PROJECT_ROOT.parent / "scripts").exists():
        PROJECT_ROOT = PROJECT_ROOT.parent

SCRIPTS_DIR = PROJECT_ROOT / "scripts"
for path in (PROJECT_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from path_helpers import data_root  # noqa: E402

LOGGER = logging.getLogger("old_biogeme.load_only")
if not LOGGER.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER.setLevel(logging.INFO)


# %% Configuration
GENDER = "male"
GENDER_COLUMN = "dgn"
LABELS_OVERRIDE: Sequence[str] | None = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")


# %% Constants shared with the original DCM1 loader
SCENARIO_DIR = data_root() / "processed" / "scenarios"
SCENARIO_VARIABLES: Sequence[str] = (
    "logy",
    "logl",
    "Leila",
    "Leila2",
    "lochi",
    "logdc",
    "log2y",
    "log2l",
    "logyl",
)


# %% Internal helpers (trimmed from scripts/DCM1.py)
def _detect_labels_from_df(df: pd.DataFrame) -> tuple[str, ...]:
    labels = [c.split("logy_", 1)[1] for c in df.columns if c.startswith("logy_")]
    labels = sorted(set(labels), key=lambda s: (len(s), s))
    return tuple(labels)


def _load_dataset(
    path: Path,
    labels: Sequence[str] | None,
    *,
    auto_labels: bool = False,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing wide DCM dataset: {path}. Run scripts/scenarios.py first."
        )

    df = pd.read_parquet(path)
    df = df.replace("", np.nan)

    if auto_labels or labels is None:
        labels_tuple = _detect_labels_from_df(df)
        if not labels_tuple:
            raise ValueError("Could not detect scenario labels (expected columns like logy_h0).")
        LOGGER.info("Auto-detected scenario labels: %s", ", ".join(labels_tuple))
    else:
        labels_tuple = tuple(labels)

    df_columns = set(df.columns)
    missing: set[str] = set()
    for col in ("idperson", "idhh", "actual_choice"):
        if col not in df_columns:
            missing.add(col)

    for label in labels_tuple:
        for base in SCENARIO_VARIABLES:
            canonical = f"{base}_{label}"
            alt_name = None
            if base == "log2y":
                alt_name = f"logy2_{label}"
            elif base == "log2l":
                alt_name = f"logl2_{label}"
            if canonical in df_columns:
                continue
            if alt_name and alt_name in df_columns:
                continue
            missing.add(canonical if not alt_name else f"{canonical} (or {alt_name})")

    if missing:
        raise KeyError(f"Dataset is missing required columns: {sorted(missing)}")

    rename_map: dict[str, str] = {}
    for label in labels_tuple:
        if f"logy2_{label}" in df.columns and f"log2y_{label}" not in df.columns:
            rename_map[f"logy2_{label}"] = f"log2y_{label}"
        if f"logl2_{label}" in df.columns and f"log2l_{label}" not in df.columns:
            rename_map[f"logl2_{label}"] = f"log2l_{label}"
    if rename_map:
        df = df.rename(columns=rename_map)

    return df, labels_tuple


def _ensure_gender_flag(df: pd.DataFrame, gender: str, gender_col: str) -> pd.DataFrame:
    result = df.copy()
    if gender_col not in result.columns:
        result[gender_col] = 1 if gender == "male" else 0
    result[gender_col] = (result[gender_col] > 0).astype(int)
    return result


# %% Public helper
def load_dataset(
    gender: str = GENDER,
    labels: Sequence[str] | None = LABELS_OVERRIDE,
) -> tuple[pd.DataFrame, tuple[str, ...], Path]:
    dataset_path = SCENARIO_DIR / f"heads_wide_single_{gender}_dcm.parquet"
    df, detected_labels = _load_dataset(
        dataset_path,
        labels,
        auto_labels=labels is None,
    )
    df = _ensure_gender_flag(df, gender, GENDER_COLUMN)
    LOGGER.info("Loaded %d rows from %s", len(df), dataset_path.name)
    LOGGER.info("Scenario labels: %s", ", ".join(detected_labels))
    return df, detected_labels, dataset_path


# %% Interactive entry point (no estimation)
df, scenario_labels, dataset_path = load_dataset()
LOGGER.info("Data ready: shape=%s, columns=%d", df.shape, len(df.columns))
df.head()

#%%
# ============================================================================
# EXPLICIT ESTIMATION: Male singles with centering, scaling, and ASCs ON
# ============================================================================
# This mirrors DCM1.py specification with include_ascs=True, center_logs=True, 
# y_scale=1.0, but written explicitly in detail similar to test_biogeme.py

import biogeme.database as db
import biogeme.biogeme as bio
import biogeme.models as models
from biogeme.expressions import Beta, Variable
from math import log as ln

# Configuration for this estimation
INCLUDE_ASCS = True
CENTER_LOGS = True
Y_SCALE = 1.0
POOLED = False  # Single gender (male), not pooled

# %% Step 1: Compute actual choice log values for centering
def compute_actual_choice_logs(df: pd.DataFrame, labels: Sequence[str]) -> tuple[float, float]:
    """Compute mean logy and logl at actual choice for centering."""
    logy_actual = pd.Series(np.nan, index=df.index)
    logl_actual = pd.Series(np.nan, index=df.index)
    actual_choice = df["actual_choice"]
    
    for label in labels:
        mask = actual_choice == label
        if mask.any():
            logy_actual.loc[mask] = df.loc[mask, f"logy_{label}"]
            logl_actual.loc[mask] = df.loc[mask, f"logl_{label}"]
    
    mean_logy = logy_actual.mean()
    mean_logl = logl_actual.mean()
    
    LOGGER.info("Mean logy at actual choice: %.6f", mean_logy)
    LOGGER.info("Mean logl at actual choice: %.6f", mean_logl)
    
    return float(mean_logy), float(mean_logl)

mean_logy_actual, mean_logl_actual = compute_actual_choice_logs(df, scenario_labels)

# %% Step 2: Prepare Biogeme database
LOGGER.info("Preparing Biogeme database for %d observations", len(df))

df_bio = df.copy()
alt_ids = {label: idx + 1 for idx, label in enumerate(scenario_labels)}
df_bio["choice_id"] = df_bio["actual_choice"].map(alt_ids)

if df_bio["choice_id"].isna().any():
    raise ValueError("Encountered invalid actual_choice values")

# Select columns for Biogeme
keep_columns = ["choice_id"]
for label in scenario_labels:
    for var in SCENARIO_VARIABLES:
        keep_columns.append(f"{var}_{label}")

# Ensure gender column is included
if GENDER_COLUMN in df_bio.columns:
    keep_columns.append(GENDER_COLUMN)

numeric_df = df_bio[keep_columns].apply(pd.to_numeric, errors="coerce")
numeric_df["choice_id"] = numeric_df["choice_id"].astype(int)

if numeric_df.isna().any().any():
    LOGGER.warning("NaN values detected in numeric data")

database = db.Database("labour_supply", numeric_df)
LOGGER.info("Database created: %d observations", len(numeric_df))

# %% Step 3: Define Beta parameters (detailed)
LOGGER.info("Defining Beta parameters for utility specification")

# Main coefficients on log(consumption) and log(leisure)
alpha_1 = Beta("beta_log_consumption", 0.0, None, None, 0)
alpha_2 = Beta("beta_log_leisure", 0.0, None, None, 0)
alpha_3 = Beta("beta_leila", 0.0, None, None, 0)
alpha_4 = Beta("beta_log2_leila", 0.0, None, None, 0)
alpha_5 = Beta("beta_log_leisure_children_total", 0.0, None, None, 0)
alpha_6 = Beta("beta_log_leisure_child_lt6_dummy", 0.0, None, None, 0)

# Quadratic and interaction terms
beta_1 = Beta("beta_log2_consumption", 0.0, None, None, 0)
beta_2 = Beta("beta_log2_leisure", 0.0, None, None, 0)
gamma = Beta("beta_logy_logl", 0.0, None, None, 0)

# Centering and scaling parameters (fixed = 1)
C_LOGY = Beta("C_LOGY", mean_logy_actual, None, None, 1)
C_LOGL = Beta("C_LOGL", mean_logl_actual, None, None, 1)
LN_SCALE = Beta("LN_SCALE", 0.0, None, None, 1)

LOGGER.info("Parameters defined: alpha_1-6, beta_1-2, gamma, centering/scaling terms")

# Define ASCs for each alternative (if INCLUDE_ASCS is True)
asc_dict = {}
if INCLUDE_ASCS:
    for idx, label in enumerate(scenario_labels):
        if idx == 0:  # Base alternative (normalized to 0)
            asc_dict[label] = Beta(f"ASC_{label}", 0.0, None, None, 1)
        else:
            asc_dict[label] = Beta(f"ASC_{label}", 0.0, None, None, 0)
    LOGGER.info("ASCs included for all %d alternatives", len(scenario_labels))

# %% Step 4: Define Variables from the database
LOGGER.info("Creating Variable expressions for all regressors")

var_dict = {}
for label in scenario_labels:
    for var_name in SCENARIO_VARIABLES:
        var_dict[f"{var_name}_{label}"] = Variable(f"{var_name}_{label}")

# %% Step 5: Build utility expressions for each alternative
LOGGER.info("Building utility functions for %d alternatives", len(scenario_labels))

V = {}
av = {}

for label in scenario_labels:
    alt_id = alt_ids[label]
    
    # Extract regressors for this alternative
    logy_raw = var_dict[f"logy_{label}"]
    logl_raw = var_dict[f"logl_{label}"]
    leila = var_dict[f"Leila_{label}"]
    leila2 = var_dict[f"Leila2_{label}"]
    lochi = var_dict[f"lochi_{label}"]
    logdc = var_dict[f"logdc_{label}"]
    
    # Apply centering and scaling transformation
    # logy* = logy - ln(y_scale) - c_logy
    # logl* = logl - c_logl
    logy_centered = logy_raw - (LN_SCALE + C_LOGY)
    logl_centered = logl_raw - C_LOGL
    
    # Compute squared and interaction terms from centered variables
    log2y_term = logy_centered * logy_centered
    log2l_term = logl_centered * logl_centered
    logyl_term = logy_centered * logl_centered
    
    # Build base utility (without ASC)
    utility = (
        alpha_1 * logy_centered
        + alpha_2 * logl_centered
        + alpha_3 * leila
        + alpha_4 * leila2
        + alpha_5 * lochi
        + alpha_6 * logdc
        + beta_1 * log2y_term
        + beta_2 * log2l_term
        + gamma * logyl_term
    )
    
    # Add ASC if included
    if INCLUDE_ASCS:
        utility = utility + asc_dict[label]
    
    V[alt_id] = utility
    av[alt_id] = 1  # All alternatives available
    
    LOGGER.info(
        "Alternative %s (id=%d): utility function with %d regressors%s",
        label, alt_id, len(SCENARIO_VARIABLES), " + ASC" if INCLUDE_ASCS else ""
    )

# %% Step 6: Define the log-likelihood
LOGGER.info("Creating logit model specification")

choice = Variable("choice_id")
logprob = models.loglogit(V, av, choice)

# %% Step 7: Create Biogeme model and estimate
LOGGER.info("Initializing Biogeme model")

model_name = "dcm_male_explicit"
if INCLUDE_ASCS:
    model_name += "_ascsON"
if CENTER_LOGS:
    model_name += "_centered"

# Set output directory
output_dir = PROJECT_ROOT / "reports" / "biogeme" / "male_explicit"
output_dir.mkdir(parents=True, exist_ok=True)

biogeme_model = bio.BIOGEME(database, logprob)  # type: ignore

# Try to set model name (different attribute names in different versions)
if hasattr(biogeme_model, "model_name"):
    biogeme_model.model_name = model_name  # type: ignore
else:
    try:
        biogeme_model.modelName = model_name  # type: ignore
    except (AttributeError, TypeError):
        pass

# Try to set output directory
if hasattr(biogeme_model, "set_output_directory"):
    try:
        biogeme_model.set_output_directory(str(output_dir))  # type: ignore
    except (AttributeError, TypeError):
        pass

LOGGER.info("Running estimation with model name: %s", model_name)
LOGGER.info("Output directory: %s", output_dir)

# Estimate the model
results = biogeme_model.estimate()  # type: ignore

# %% Step 8: Extract and display results
LOGGER.info("Estimation completed")

# Get estimated parameters
try:
    if hasattr(results, "get_pandas_estimated_parameters"):
        params_df = results.get_pandas_estimated_parameters()
    else:
        params_df = results.getEstimatedParameters()
except Exception as e:
    LOGGER.error("Could not extract parameters: %s", e)
    params_df = None

if params_df is not None:
    LOGGER.info("\n=== ESTIMATED PARAMETERS ===")
    print(params_df)
    
    # Save parameters to CSV
    params_path = output_dir / f"{model_name}_parameters.csv"
    params_df.to_csv(params_path)
    LOGGER.info("Parameters saved to: %s", params_path)

# Extract and display fit statistics
try:
    opt_ll = results.getLogLikelihood()
    LOGGER.info("Optimized log-likelihood: %.4f", opt_ll)
except Exception as e:
    LOGGER.warning("Could not extract log-likelihood: %s", e)

try:
    null_ll = results.getLLNull()
    rho2 = results.getRho2()
    rho2_adj = results.getRho2Adjusted()
    LOGGER.info("Null log-likelihood: %.4f", null_ll)
    LOGGER.info("Rho-squared: %.6f", rho2)
    LOGGER.info("Adjusted Rho-squared: %.6f", rho2_adj)
except Exception as e:
    LOGGER.warning("Could not extract fit statistics: %s", e)

LOGGER.info("Estimation and results extraction complete")
# %%
df.head()
#%% 

# Rescale data
def rescale_column(df, col):
    mean = df[col].mean()
    std = df[col].std()
    df[col] = (df[col] - mean) / std
    return df

#%% 
# Apply rescaling to relevant columns (example)
# Create the Biogeme database
import os 
import pandas as pd 
import numpy as np 
import biogeme.database as db
import biogeme.biogeme as bio 
import biogeme.models as models 
import biogeme.version as ver 
from biogeme.expressions import Beta, log,Variable, bioMultSum
import pandas as pd
#%%
# 
# Ensure pandas will print all columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 2000)

# Print columns as a readable list (one per line)
for col in df.columns.tolist():
    print(col)

#%% 
required_columns = [
    "idperson",
    "idhh",
    "actual_choice",
    "lhw_h0",
    "yem_h0",
    "ils_dispy_h0",
    "consumption_h0",
    "other_members_income_h0",
    "lhw_h1",
    "yem_h1",
    "ils_dispy_h1",
    "consumption_h1",
    "other_members_income_h1",
    "lhw_h2",
    "yem_h2",
    "ils_dispy_h2",
    "consumption_h2",
    "other_members_income_h2",
    "lhw_h3",
    "yem_h3",
    "ils_dispy_h3",
    "consumption_h3",
    "other_members_income_h3",
    "lhw_h4",
    "yem_h4",
    "ils_dispy_h4",
    "consumption_h4",
    "other_members_income_h4",
    "lhw_h5",
    "yem_h5",
    "ils_dispy_h5",
    "consumption_h5",
    "other_members_income_h5",
    "lhw_h6",
    "yem_h6",
    "ils_dispy_h6",
    "consumption_h6",
    "other_members_income_h6",
    "is_actual_h0",
    "is_actual_h1",
    "is_actual_h2",
    "is_actual_h3",
    "is_actual_h4",
    "is_actual_h5",
    "is_actual_h6",
    "Lage",
    "l2age",
    "DCH",
    "logy_h0",
    "logl_h0",
    "log2y_h0",
    "log2l_h0",
    "logyl_h0",
    "Leila_h0",
    "Leila2_h0",
    "lochi_h0",
    "logdc_h0",
    "logy_h1",
    "logl_h1",
    "log2y_h1",
    "log2l_h1",
    "logyl_h1",
    "Leila_h1",
    "Leila2_h1",
    "lochi_h1",
    "logdc_h1",
    "logy_h2",
    "logl_h2",
    "log2y_h2",
    "log2l_h2",
    "logyl_h2",
    "Leila_h2",
    "Leila2_h2",
    "lochi_h2",
    "logdc_h2",
    "logy_h3",
    "logl_h3",
    "log2y_h3",
    "log2l_h3",
    "logyl_h3",
    "Leila_h3",
    "Leila2_h3",
    "lochi_h3",
    "logdc_h3",
    "logy_h4",
    "logl_h4",
    "log2y_h4",
    "log2l_h4",
    "logyl_h4",
    "Leila_h4",
    "Leila2_h4",
    "lochi_h4",
    "logdc_h4",
    "logy_h5",
    "logl_h5",
    "log2y_h5",
    "log2l_h5",
    "logyl_h5",
    "Leila_h5",
    "Leila2_h5",
    "lochi_h5",
    "logdc_h5",
    "logy_h6",
    "logl_h6",
    "log2y_h6",
    "log2l_h6",
    "logyl_h6",
    "Leila_h6",
    "Leila2_h6",
    "lochi_h6",
    "logdc_h6",
]
#%% 

df_filtered = df[required_columns].copy()


#%% 

# Create a mapping from 'h0'..'h6' -> 1..7  (1-based IDs)
choice_labels = [f"h{i}" for i in range(7)]
choice_map = {label: i + 1 for i, label in enumerate(choice_labels)}  # <-- +1

df_filtered["choice_id"] = df_filtered["actual_choice"].map(choice_map)
if df_filtered["choice_id"].isnull().any():
    raise ValueError("Some actual_choice values could not be mapped. Check your data.")

print(df_filtered[["actual_choice", "choice_id"]])

# Now you can drop the original actual_choice column if you want
df_filtered = df_filtered.drop(columns=["actual_choice"])

#%% 
# Now you can drop the original actual_choice column if you want
df_filtered = df_filtered.drop(columns=["actual_choice"])

#%% 
database = db.Database('labour_supply', df_filtered)


#%% 
logy_vars = {f'logy_h{i}': Variable(f'logy_h{i}') for i in range(7)}
logl_vars = {f'logl_h{i}': Variable(f'logl_h{i}') for i in range(7)}
log2y_vars = {f'log2y_h{i}': Variable(f'log2y_h{i}') for i in range(7)}
log2l_vars = {f'log2l_h{i}': Variable(f'log2l_h{i}') for i in range(7)}
logyl_vars = {f'logyl_h{i}': Variable(f'logyl_h{i}') for i in range(7)}
leila_vars = {f'Leila_h{i}': Variable(f'Leila_h{i}') for i in range(7)}
leila2_vars = {f'Leila2_h{i}': Variable(f'Leila2_h{i}') for i in range(7)}
lochi_vars = {f'lochi_h{i}': Variable(f'lochi_h{i}') for i in range(7)}
logdc_vars = {f'logdc_h{i}': Variable(f'logdc_h{i}') for i in range(7)} 

choice = Variable('choice_id')
#%%# Define the parameters to be estimated with realistic boundaries
alpha = Beta('alpha', 0, None, None, 0)
beta = Beta('beta', 0, None, None, 0)
gamma_yy = Beta('gamma_yy', 0, None, None, 0)
gamma_ll = Beta('gamma_ll', 0, None, None, 0)
gamma_yl = Beta('gamma_yl', 0, None, None, 0)

gamma_leila = Beta('gamma_leila', 0, None, None, 0)
gamma_leila2 = Beta('gamma_leila2', 0, None, None, 0)
gamma_lochi = Beta('gamma_lochi', 0, None, None, 0)
gamma_logdc = Beta('gamma_logdc', 0, None, None, 0)
# Base alternative is 1, fixed to 0
ascs = {
    1: 0,  # base alternative, not estimated
    2: Beta('ASC_h1', 0, None, None, 0),
    3: Beta('ASC_h2', 0, None, None, 0),
    4: Beta('ASC_h3', 0, None, None, 0),
    5: Beta('ASC_h4', 0, None, None, 0),
    6: Beta('ASC_h5', 0, None, None, 0),
    7: Beta('ASC_h6', 0, None, None, 0),
}

#%%
# Helper function to create utility (now includes ASC)
def create_utility(
    logy, logl, logy2, logl2, logyl,
    leila, leila2, lochi, logdc,
    alpha, beta, gamma_yy, gamma_ll, gamma_yl,
    gamma_leila, gamma_leila2, gamma_lochi, gamma_logdc,
    asc=0,
):
    return (
        asc
        + alpha * logy
        + beta * logl
        + gamma_yy * logy2
        + gamma_ll * logl2
        + gamma_yl * logyl
        + gamma_leila  * leila     # <-- use Leila, not logy
        + gamma_leila2 * leila2    # <-- use Leila2, not log2y
        + gamma_lochi  * lochi     # <-- use lochi, not logl
        + gamma_logdc  * logdc     # <-- use logdc, not log2l
    )


#%% 
V = {}
for i in range(1, 8):           # alt IDs: 1..7
    s = i - 1                   # column suffix: h0..h6
    V[i] = create_utility(
        logy_vars[f'logy_h{s}'],
        logl_vars[f'logl_h{s}'],
        log2y_vars[f'log2y_h{s}'],
        log2l_vars[f'log2l_h{s}'],
        logyl_vars[f'logyl_h{s}'],
        leila_vars[f'Leila_h{s}'],
        leila2_vars[f'Leila2_h{s}'],
        lochi_vars[f'lochi_h{s}'],
        logdc_vars[f'logdc_h{s}'],
        alpha, beta, gamma_yy, gamma_ll, gamma_yl,
        gamma_leila, gamma_leila2, gamma_lochi, gamma_logdc,
        asc=ascs.get(i, 0),
    )


#%% 
# Define the availability of each choice (all choices are available)
# If your dataframe has availability columns, use them; else assume 1
av = {}
for i in range(1, 8):
    s = i - 1
    col = f'avail_h{s}'
    if col in df_filtered.columns:
        av[i] = Variable(col)
    else:
        av[i] = 1
#%%
choice = Variable('choice_id')
logprob = models.loglogit(V, av, choice)

biogeme_model = bio.BIOGEME(database, logprob)
biogeme_model.model_name = 'optimized_model_unbounds22'
biogeme_model.choice = choice
biogeme_model.algorithm_parameters = {'tolerance': 1e-6, 'maxIter': 2000}

results = biogeme_model.estimate()
print(results.get_estimated_parameters())

# %%
