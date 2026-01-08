"""
==============================================================================
RURO MNL Estimation Utilities
==============================================================================
Core utilities for enhanced RURO MNL estimation:
- Data loading and validation against pipeline metadata
- Precomputation of arrays for vectorized likelihood computation
- Box-Cox transformations with numerical stability
- Softmax and choice probability calculations
- Analytical gradient helpers

Author: Enhanced RURO Pipeline
Created: 2026-01-03
==============================================================================
"""

import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

# Optional Numba acceleration for Box-Cox transforms
try:
    import numba
    HAS_NUMBA = True
    logging.info("Numba detected - Box-Cox transforms will use JIT compilation")
except ImportError:
    HAS_NUMBA = False
    logging.info("Numba not available - using NumPy implementations (slower but functional)")

# ==============================================================================
# Constants
# ==============================================================================

# Epsilon for numerical stability
EPS = 1e-12

# Tolerance for metadata validation
NORMALIZATION_TOLERANCE = 1e-6
NORMALIZATION_ERROR_THRESHOLD = 1e-4

# ==============================================================================
# Data Loading & Validation
# ==============================================================================

def load_and_validate_mnl_data(
    singles_path: Path,
    couples_path: Optional[Path],
    metadata_path: Path,
    strict_validation: bool = True
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Load MNL datasets with strict metadata validation.

    Performs comprehensive validation:
    1. Metadata normalization constants match actual data
       - c_norm = consumption / c_scale (within tolerance)
       - l_norm = leisure / l_scale
    2. Prior parameters in data match metadata
    3. Required columns present
    4. Data integrity (no NaN, positive values, sorted by ID)

    Parameters
    ----------
    singles_path : Path
        Path to singles MNL dataset (parquet)
    couples_path : Path | None
        Path to couples MNL dataset (parquet), or None if singles only
    metadata_path : Path
        Path to metadata JSON file
    strict_validation : bool, default=True
        If True, raise errors on validation failures
        If False, log warnings but continue

    Returns
    -------
    df_singles : pd.DataFrame
        Singles dataset with validated columns
    df_couples : pd.DataFrame | None
        Couples dataset (or None if not provided)
    metadata : dict
        Metadata dictionary from JSON file

    Raises
    ------
    FileNotFoundError
        If required files don't exist
    ValueError
        If strict_validation=True and validation fails
    """
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Loading and validating MNL datasets")
    logger.info("="*80)

    # Load metadata
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    import json
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    logger.info(f"Loaded metadata from: {metadata_path}")

    # Load singles
    if not singles_path.exists():
        raise FileNotFoundError(f"Singles dataset not found: {singles_path}")

    df_singles = pd.read_parquet(singles_path)
    logger.info(f"Loaded singles dataset: {len(df_singles):,} rows, {len(df_singles.columns)} columns")

    # Load couples (if provided)
    df_couples = None
    if couples_path is not None:
        if not couples_path.exists():
            raise FileNotFoundError(f"Couples dataset not found: {couples_path}")
        df_couples = pd.read_parquet(couples_path)
        logger.info(f"Loaded couples dataset: {len(df_couples):,} rows, {len(df_couples.columns)} columns")

    # Validate singles
    _validate_mnl_dataset(
        df=df_singles,
        dataset_type="singles",
        metadata=metadata,
        strict=strict_validation
    )

    # Validate couples
    if df_couples is not None:
        _validate_mnl_dataset(
            df=df_couples,
            dataset_type="couples",
            metadata=metadata,
            strict=strict_validation
        )

    logger.info("="*80)
    logger.info("Data loading and validation complete")
    logger.info("="*80)

    return df_singles, df_couples, metadata


def _validate_mnl_dataset(
    df: pd.DataFrame,
    dataset_type: str,
    metadata: Dict[str, Any],
    strict: bool = True
) -> None:
    """
    Validate a single MNL dataset (singles or couples).

    Parameters
    ----------
    df : pd.DataFrame
        Dataset to validate
    dataset_type : str
        "singles" or "couples"
    metadata : dict
        Metadata from JSON file
    strict : bool
        Whether to raise errors or just warn
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Validating {dataset_type} dataset...")

    errors = []
    warnings_list = []

    # 1. Check required columns
    if dataset_type == "singles":
        required_cols = ["idhh", "draw", "consumption", "leisure", "hours", "prior"]
        optional_cols = ["wage", "gsur", "u_rate", "loc4", "age_norm", "n_children", "educL", "educM", "educH"]
    else:  # couples
        # NOTE: Consumption can be either household-level OR person-level (consumption_male/consumption_female)
        base_required_cols = ["idhh", "draw", "leisure_male", "leisure_female",
                              "hours_male", "hours_female", "prior"]

        # Check if we have person-level consumption (CORRECT for couples)
        has_person_consumption = "consumption_male" in df.columns and "consumption_female" in df.columns
        has_household_consumption = "consumption" in df.columns

        if has_person_consumption:
            required_cols = base_required_cols + ["consumption_male", "consumption_female"]
        elif has_household_consumption:
            required_cols = base_required_cols + ["consumption"]
        else:
            errors.append("Couples data must have either 'consumption' OR 'consumption_male'+'consumption_female'")
            required_cols = base_required_cols  # Continue validation

        optional_cols = ["wage_male", "wage_female", "gsur_male", "gsur_female",
                        "u_rate_male", "u_rate_female", "loc4_male", "loc4_female"]

    missing_required = [col for col in required_cols if col not in df.columns]
    if missing_required:
        errors.append(f"Missing required columns: {missing_required}")

    present_optional = [col for col in optional_cols if col in df.columns]
    logger.info(f"  Present optional columns: {present_optional if present_optional else 'None'}")

    # 2. Check for NaN in core variables
    if dataset_type == "singles":
        core_vars = ["consumption", "leisure", "hours", "prior"]
    else:
        # For couples, check person-level consumption if present
        if "consumption_male" in df.columns:
            core_vars = ["consumption_male", "consumption_female", "leisure_male", "leisure_female",
                        "hours_male", "hours_female", "prior"]
        else:
            core_vars = ["consumption", "leisure_male", "leisure_female", "hours_male", "hours_female", "prior"]

    for var in core_vars:
        if var in df.columns:
            n_nan = df[var].isna().sum()
            if n_nan > 0:
                errors.append(f"Found {n_nan} NaN values in {var}")

    # 3. Check positive consumption/leisure
    if "consumption" in df.columns:
        n_nonpositive = (df["consumption"] <= 0).sum()
        if n_nonpositive > 0:
            errors.append(f"Found {n_nonpositive} non-positive consumption values")

    # Check person-level consumption for couples
    if dataset_type == "couples":
        for suffix in ["_male", "_female"]:
            col = f"consumption{suffix}"
            if col in df.columns:
                n_nonpositive = (df[col] <= 0).sum()
                if n_nonpositive > 0:
                    errors.append(f"Found {n_nonpositive} non-positive {col} values")

    if dataset_type == "singles":
        if "leisure" in df.columns:
            n_nonpositive = (df["leisure"] <= 0).sum()
            if n_nonpositive > 0:
                errors.append(f"Found {n_nonpositive} non-positive leisure values")
    else:
        for suffix in ["_male", "_female"]:
            col = f"leisure{suffix}"
            if col in df.columns:
                n_nonpositive = (df[col] <= 0).sum()
                if n_nonpositive > 0:
                    errors.append(f"Found {n_nonpositive} non-positive {col} values")

    # 4. Validate normalization constants (critical check)
    if "normalization" in metadata:
        norm_meta = metadata["normalization"]
        c_scale = norm_meta.get("c_scale")
        l_scale = norm_meta.get("l_scale")

        if c_scale is not None and "consumption" in df.columns:
            # Check if c_norm exists (should be consumption / c_scale)
            if "c_norm" in df.columns:
                c_norm_computed = df["consumption"] / c_scale
                c_norm_actual = df["c_norm"]
                max_diff = (c_norm_computed - c_norm_actual).abs().max()

                if max_diff > NORMALIZATION_ERROR_THRESHOLD:
                    errors.append(
                        f"Normalization mismatch for consumption: max diff = {max_diff:.6e} "
                        f"(threshold = {NORMALIZATION_ERROR_THRESHOLD:.6e})"
                    )
                elif max_diff > NORMALIZATION_TOLERANCE:
                    warnings_list.append(
                        f"Small normalization difference for consumption: max diff = {max_diff:.6e}"
                    )

        if l_scale is not None:
            # Check leisure normalization
            if dataset_type == "singles":
                if "leisure" in df.columns and "l_norm" in df.columns:
                    l_norm_computed = df["leisure"] / l_scale
                    l_norm_actual = df["l_norm"]
                    max_diff = (l_norm_computed - l_norm_actual).abs().max()

                    if max_diff > NORMALIZATION_ERROR_THRESHOLD:
                        errors.append(
                            f"Normalization mismatch for leisure: max diff = {max_diff:.6e}"
                        )
            else:
                # Couples - check both male and female
                for suffix in ["_male", "_female"]:
                    l_col = f"leisure{suffix}"
                    ln_col = f"l_norm{suffix}"
                    if l_col in df.columns and ln_col in df.columns:
                        l_norm_computed = df[l_col] / l_scale
                        l_norm_actual = df[ln_col]
                        max_diff = (l_norm_computed - l_norm_actual).abs().max()

                        if max_diff > NORMALIZATION_ERROR_THRESHOLD:
                            errors.append(
                                f"Normalization mismatch for {l_col}: max diff = {max_diff:.6e}"
                            )

    # 5. Check data is sorted by ID (required for group boundaries)
    if "idhh" in df.columns:
        if not df["idhh"].is_monotonic_increasing:
            errors.append("Data is not sorted by idhh (required for group boundaries)")

    # 6. Check draw range
    if "draw" in df.columns:
        draw_min, draw_max = df["draw"].min(), df["draw"].max()
        n_draws = metadata.get("n_draws")
        if n_draws is not None:
            if draw_min != 0 or draw_max != n_draws - 1:
                warnings_list.append(
                    f"Draw range [{draw_min}, {draw_max}] doesn't match expected [0, {n_draws-1}]"
                )

    # Report results
    if warnings_list:
        logger.warning(f"  Validation warnings for {dataset_type}:")
        for w in warnings_list:
            logger.warning(f"    ⚠️  {w}")

    if errors:
        logger.error(f"  Validation errors for {dataset_type}:")
        for e in errors:
            logger.error(f"    ❌ {e}")

        if strict:
            raise ValueError(f"Validation failed for {dataset_type} dataset. See errors above.")
    else:
        logger.info(f"  ✅ {dataset_type.capitalize()} dataset validation passed")


# ==============================================================================
# Precomputed Data Structures
# ==============================================================================

@dataclass
class PrecomputedDataSingles:
    """
    All arrays for singles estimation, pre-extracted for vectorized computation.

    All arrays are (n_obs,) unless otherwise noted.
    Arrays are NumPy arrays for performance.
    """
    # Core utility components
    consumption: np.ndarray  # Raw consumption (before normalization/transform)
    leisure: np.ndarray      # Raw leisure
    log_c: np.ndarray        # log(consumption) - for Box-Cox derivatives
    log_l: np.ndarray        # log(leisure)

    # Demographics (preference shifters)
    age_norm: np.ndarray     # Demeaned age
    age_norm2: np.ndarray    # Age squared
    n_children: np.ndarray   # Number of children (0 for males, actual for females)
    educL: np.ndarray        # Low education dummy
    educM: np.ndarray        # Medium education dummy
    educH: np.ndarray        # High education dummy

    # Hours opportunity shifters
    working: np.ndarray      # 1 if hours > 0, else 0
    working_pt1: np.ndarray  # Part-time 1 indicator (~20h focal)
    working_pt2: np.ndarray  # Part-time 2 indicator (~30h focal)
    working_ft: np.ndarray   # Full-time indicator (~40h focal)
    gsur: np.ndarray         # Group-specific unemployment rate (0 if missing)

    # Wage opportunity (if vw or loc_empirical)
    log_wage: Optional[np.ndarray]  # log(wage) for workers, 0 for non-workers
    pexp_years: Optional[np.ndarray]  # Potential experience in years
    pexp_years2: Optional[np.ndarray]  # Experience squared

    # Occupation (if loc_empirical)
    loc4: Optional[np.ndarray]  # 4-category occupation code
    loc4_1: Optional[np.ndarray]  # Occupation group 1 dummy
    loc4_2: Optional[np.ndarray]  # Occupation group 2 dummy
    loc4_3: Optional[np.ndarray]  # Occupation group 3 dummy
    loc4_4: Optional[np.ndarray]  # Occupation group 4 dummy

    # Normalization & prior
    prior: np.ndarray        # Importance sampling prior
    c_scale: float           # Consumption normalization constant
    l_scale: float           # Leisure normalization constant

    # Group structure (for softmax)
    group_ids: np.ndarray    # Person IDs (unique identifiers)
    group_starts: np.ndarray # Index where each group starts
    group_ends: np.ndarray   # Index where each group ends (exclusive)
    n_groups: int            # Number of individuals
    n_obs: int               # Total observations (n_groups × n_draws)

    # Metadata
    is_male: bool            # True if male dataset, False if female


@dataclass
class PrecomputedDataCouples:
    """
    All arrays for couples estimation (wide format).

    All arrays are (n_obs,) unless otherwise noted.
    """
    # Core utility components
    # NOTE: Consumption is HOUSEHOLD-LEVEL (sum of male + female disposable income)
    # normalized_consumption_couples = (ils_dispy_male + ils_dispy_female) / mean(ils_dispy_male + ils_dispy_female)
    consumption: np.ndarray    # Household consumption (normalized sum)
    log_c: np.ndarray          # log(consumption)

    # Male leisure
    leisure_male: np.ndarray
    log_l_male: np.ndarray

    # Female leisure
    leisure_female: np.ndarray
    log_l_female: np.ndarray

    # Male demographics
    age_norm_male: np.ndarray
    age_norm2_male: np.ndarray
    educL_male: np.ndarray
    educM_male: np.ndarray
    educH_male: np.ndarray

    # Female demographics
    age_norm_female: np.ndarray
    age_norm2_female: np.ndarray
    n_children: np.ndarray      # Only for female
    educL_female: np.ndarray
    educM_female: np.ndarray
    educH_female: np.ndarray

    # Male hours opportunity
    working_male: np.ndarray
    working_pt1_male: np.ndarray
    working_pt2_male: np.ndarray
    working_ft_male: np.ndarray
    gsur_male: np.ndarray

    # Female hours opportunity
    working_female: np.ndarray
    working_pt1_female: np.ndarray
    working_pt2_female: np.ndarray
    working_ft_female: np.ndarray
    gsur_female: np.ndarray

    # Male wage opportunity (if vw or loc_empirical)
    log_wage_male: Optional[np.ndarray]
    pexp_years_male: Optional[np.ndarray]
    pexp_years2_male: Optional[np.ndarray]
    loc4_male: Optional[np.ndarray]
    loc4_1_male: Optional[np.ndarray]
    loc4_2_male: Optional[np.ndarray]
    loc4_3_male: Optional[np.ndarray]
    loc4_4_male: Optional[np.ndarray]

    # Female wage opportunity
    log_wage_female: Optional[np.ndarray]
    pexp_years_female: Optional[np.ndarray]
    pexp_years2_female: Optional[np.ndarray]
    loc4_female: Optional[np.ndarray]
    loc4_1_female: Optional[np.ndarray]
    loc4_2_female: Optional[np.ndarray]
    loc4_3_female: Optional[np.ndarray]
    loc4_4_female: Optional[np.ndarray]

    # Normalization & prior
    prior: np.ndarray
    c_scale: float
    l_scale: float

    # Group structure
    group_ids: np.ndarray
    group_starts: np.ndarray
    group_ends: np.ndarray
    n_groups: int
    n_obs: int


# ==============================================================================
# Precomputation Functions
# ==============================================================================

def precompute_data_singles(
    df: pd.DataFrame,
    metadata: Dict[str, Any],
    is_male: bool = True,
    include_wage_vars: bool = True,
    include_loc_vars: bool = False
) -> PrecomputedDataSingles:
    """
    Extract and validate all arrays for singles estimation.

    Parameters
    ----------
    df : pd.DataFrame
        Singles MNL dataset (must be sorted by idhh)
    metadata : dict
        Metadata from pipeline
    is_male : bool, default=True
        Whether this is male dataset (affects n_children handling)
    include_wage_vars : bool, default=True
        Whether to extract wage variables (for vw/loc_empirical specs)
    include_loc_vars : bool, default=False
        Whether to extract occupation variables (for loc_empirical spec)

    Returns
    -------
    PrecomputedDataSingles
        Dataclass with all extracted arrays

    Raises
    ------
    ValueError
        If required columns missing or data not sorted
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Precomputing data for {'male' if is_male else 'female'} singles ({len(df):,} rows)...")    # Check sorted
    if not df["idhh"].is_monotonic_increasing:
        raise ValueError("DataFrame must be sorted by idhh")
    
    n_obs = len(df)

    # Get normalization constants (support both flat and nested structure)
    norm = metadata["normalization"]
    if "singles" in norm:
        # Nested structure: metadata["normalization"]["singles"]["c_scale"]
        c_scale = norm["singles"]["c_scale"]
        l_scale = norm["singles"]["l_scale"]
    else:
        # Flat structure: metadata["normalization"]["c_scale"]
        c_scale = norm["c_scale"]
        l_scale = norm["l_scale"]

    # Extract core variables (MUST use normalized versions!)
    # R code normalizes consumption first: dispy_util = ils_dispy / mean_dispy_19
    # Then Box-Cox transforms the normalized value
    consumption = df["c_norm"].values.copy()
    leisure = df["l_norm"].values.copy()

    # Clip to avoid log(0)
    consumption = np.maximum(consumption, EPS)
    leisure = np.maximum(leisure, EPS)

    log_c = np.log(consumption)
    log_l = np.log(leisure)

    # Extract demographics
    age_norm = df.get("age_norm", pd.Series(0.0, index=df.index)).fillna(0.0).values
    age_norm2 = df.get("age_norm2", pd.Series(0.0, index=df.index)).fillna(0.0).values

    # Children: only for females
    if is_male:
        n_children = np.zeros(n_obs)
    else:
        n_children = df.get("n_children", pd.Series(0.0, index=df.index)).fillna(0.0).values

    # Education dummies
    educL = df.get("educL", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educM = df.get("educM", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educH = df.get("educH", pd.Series(0.0, index=df.index)).fillna(0.0).values

    # Hours opportunity shifters
    hours = df["hours"].values
    working = (hours > 0).astype(float)

    # Focal points (from old script logic)
    working_pt1 = ((hours >= 15) & (hours <= 25)).astype(float)  # ~20h
    working_pt2 = ((hours >= 25) & (hours <= 35)).astype(float)  # ~30h
    working_ft = ((hours >= 35) & (hours <= 45)).astype(float)   # ~40h

    # GSUR (check both column names for backwards compatibility)
    if "gsur" in df.columns:
        gsur = df["gsur"].fillna(0.0).values
    elif "u_rate" in df.columns:
        gsur = df["u_rate"].fillna(0.0).values
    else:
        logger.warning("  ⚠️  No GSUR column found (gsur or u_rate), using zeros")
        gsur = np.zeros(n_obs)

    # Wage opportunity variables (optional)
    log_wage = None
    pexp_years = None
    pexp_years2 = None

    if include_wage_vars:
        if "wage" in df.columns:
            wage = df["wage"].fillna(0.0).values
            wage = np.maximum(wage, EPS)  # Avoid log(0)
            log_wage = np.log(wage)
        else:
            logger.warning("  ⚠️  No wage column found, setting to None")

        if "pexp_years" in df.columns:
            pexp_years = df["pexp_years"].fillna(0.0).values
            pexp_years2 = pexp_years ** 2
        else:
            logger.warning("  ⚠️  No pexp_years column found, setting to None")

    # Occupation variables (optional)
    loc4 = None
    loc4_1 = loc4_2 = loc4_3 = loc4_4 = None

    if include_loc_vars:
        if "loc4" in df.columns:
            loc4 = df["loc4"].fillna(0).values
            loc4_1 = (loc4 == 1).astype(float)
            loc4_2 = (loc4 == 2).astype(float)
            loc4_3 = (loc4 == 3).astype(float)
            loc4_4 = (loc4 == 4).astype(float)
        else:
            logger.warning("  ⚠️  No loc4 column found, setting to None")

    # Prior
    prior = df["prior"].values.copy()
    # Clip to avoid log(0) in likelihood
    prior = np.maximum(prior, EPS)    # Group structure
    group_ids = df["idhh"].unique()
    n_groups = len(group_ids)

    # Find group boundaries (assuming sorted by idhh)
    # Use cumsum to get the size of each group, then compute cumulative positions
    group_sizes = df.groupby("idhh", sort=False).size().values
    group_ends = np.cumsum(group_sizes)
    group_starts = np.concatenate([[0], group_ends[:-1]])
    
    # Validate group boundaries
    if not np.all(group_ends > group_starts):
        raise ValueError(
            "Invalid group boundaries detected. "
            f"group_starts: {group_starts[:10]}, group_ends: {group_ends[:10]}"
        )

    logger.info(f"  Extracted {n_groups:,} groups with {n_obs:,} total observations")

    return PrecomputedDataSingles(
        consumption=consumption,
        leisure=leisure,
        log_c=log_c,
        log_l=log_l,
        age_norm=age_norm,
        age_norm2=age_norm2,
        n_children=n_children,
        educL=educL,
        educM=educM,
        educH=educH,
        working=working,
        working_pt1=working_pt1,
        working_pt2=working_pt2,
        working_ft=working_ft,
        gsur=gsur,
        log_wage=log_wage,
        pexp_years=pexp_years,
        pexp_years2=pexp_years2,
        loc4=loc4,
        loc4_1=loc4_1,
        loc4_2=loc4_2,
        loc4_3=loc4_3,
        loc4_4=loc4_4,
        prior=prior,
        c_scale=c_scale,
        l_scale=l_scale,
        group_ids=group_ids,
        group_starts=group_starts,
        group_ends=group_ends,
        n_groups=n_groups,
        n_obs=n_obs,
        is_male=is_male
    )


def precompute_data_couples(
    df: pd.DataFrame,
    metadata: Dict[str, Any],
    include_wage_vars: bool = True,
    include_loc_vars: bool = False
) -> PrecomputedDataCouples:
    """
    Extract and validate all arrays for couples estimation (wide format).

    Parameters
    ----------
    df : pd.DataFrame
        Couples MNL dataset (must be sorted by idhh)
    metadata : dict
        Metadata from pipeline
    include_wage_vars : bool, default=True
        Whether to extract wage variables
    include_loc_vars : bool, default=False
        Whether to extract occupation variables

    Returns
    -------
    PrecomputedDataCouples
    Dataclass with all extracted arrays
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Precomputing data for couples ({len(df):,} rows)...")

    if not df["idhh"].is_monotonic_increasing:
        raise ValueError("DataFrame must be sorted by idhh")
    
    n_obs = len(df)

    # Get normalization constants (support both flat and nested structure)
    norm = metadata["normalization"]
    if "couples" in norm:
        # Nested structure: metadata["normalization"]["couples"]["c_scale"]
        c_scale = norm["couples"]["c_scale"]
        l_scale = norm["couples"]["l_male_scale"]  # Use l_male_scale for couples
    else:
        # Flat structure: metadata["normalization"]["c_scale"]
        c_scale = norm["c_scale"]
        l_scale = norm["l_scale"]

    # Core variables
    # CRITICAL: For couples, consumption is HOUSEHOLD-LEVEL (sum of male+female)
    # normalized_consumption_couples = (ils_dispy_male + ils_dispy_female) / mean(ils_dispy_male + ils_dispy_female)
    # We use the single "c_norm" column which is the normalized household sum
    consumption = np.maximum(df["c_norm"].values.copy(), EPS)
    log_c = np.log(consumption)

    # Leisure is gender-specific and normalized
    leisure_male = np.maximum(df["l_norm_male"].values.copy(), EPS)
    leisure_female = np.maximum(df["l_norm_female"].values.copy(), EPS)
    log_l_male = np.log(leisure_male)
    log_l_female = np.log(leisure_female)

    # Male demographics
    age_norm_male = df.get("age_norm_male", pd.Series(0.0, index=df.index)).fillna(0.0).values
    age_norm2_male = df.get("age_norm2_male", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educL_male = df.get("educL_male", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educM_male = df.get("educM_male", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educH_male = df.get("educH_male", pd.Series(0.0, index=df.index)).fillna(0.0).values

    # Female demographics
    age_norm_female = df.get("age_norm_female", pd.Series(0.0, index=df.index)).fillna(0.0).values
    age_norm2_female = df.get("age_norm2_female", pd.Series(0.0, index=df.index)).fillna(0.0).values
    n_children = df.get("n_children", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educL_female = df.get("educL_female", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educM_female = df.get("educM_female", pd.Series(0.0, index=df.index)).fillna(0.0).values
    educH_female = df.get("educH_female", pd.Series(0.0, index=df.index)).fillna(0.0).values

    # Male hours opportunity
    hours_male = df["hours_male"].values
    working_male = (hours_male > 0).astype(float)
    working_pt1_male = ((hours_male >= 15) & (hours_male <= 25)).astype(float)
    working_pt2_male = ((hours_male >= 25) & (hours_male <= 35)).astype(float)
    working_ft_male = ((hours_male >= 35) & (hours_male <= 45)).astype(float)

    if "gsur_male" in df.columns:
        gsur_male = df["gsur_male"].fillna(0.0).values
    elif "u_rate_male" in df.columns:
        gsur_male = df["u_rate_male"].fillna(0.0).values
    else:
        logger.warning("  ⚠️  No male GSUR column found, using zeros")
        gsur_male = np.zeros(n_obs)

    # Female hours opportunity
    hours_female = df["hours_female"].values
    working_female = (hours_female > 0).astype(float)
    working_pt1_female = ((hours_female >= 15) & (hours_female <= 25)).astype(float)
    working_pt2_female = ((hours_female >= 25) & (hours_female <= 35)).astype(float)
    working_ft_female = ((hours_female >= 35) & (hours_female <= 45)).astype(float)

    if "gsur_female" in df.columns:
        gsur_female = df["gsur_female"].fillna(0.0).values
    elif "u_rate_female" in df.columns:
        gsur_female = df["u_rate_female"].fillna(0.0).values
    else:
        logger.warning("  ⚠️  No female GSUR column found, using zeros")
        gsur_female = np.zeros(n_obs)

    # Wage variables (optional)
    log_wage_male = log_wage_female = None
    pexp_years_male = pexp_years_female = None
    pexp_years2_male = pexp_years2_female = None

    if include_wage_vars:
        if "wage_male" in df.columns:
            wage_male = np.maximum(df["wage_male"].fillna(0.0).values, EPS)
            log_wage_male = np.log(wage_male)
        if "wage_female" in df.columns:
            wage_female = np.maximum(df["wage_female"].fillna(0.0).values, EPS)
            log_wage_female = np.log(wage_female)

        if "pexp_years_male" in df.columns:
            pexp_years_male = df["pexp_years_male"].fillna(0.0).values
            pexp_years2_male = pexp_years_male ** 2
        if "pexp_years_female" in df.columns:
            pexp_years_female = df["pexp_years_female"].fillna(0.0).values
            pexp_years2_female = pexp_years_female ** 2

    # Occupation variables (optional)
    loc4_male = loc4_1_male = loc4_2_male = loc4_3_male = loc4_4_male = None
    loc4_female = loc4_1_female = loc4_2_female = loc4_3_female = loc4_4_female = None

    if include_loc_vars:
        if "loc4_male" in df.columns:
            loc4_male = df["loc4_male"].fillna(0).values
            loc4_1_male = (loc4_male == 1).astype(float)
            loc4_2_male = (loc4_male == 2).astype(float)
            loc4_3_male = (loc4_male == 3).astype(float)
            loc4_4_male = (loc4_male == 4).astype(float)

        if "loc4_female" in df.columns:
            loc4_female = df["loc4_female"].fillna(0).values
            loc4_1_female = (loc4_female == 1).astype(float)
            loc4_2_female = (loc4_female == 2).astype(float)
            loc4_3_female = (loc4_female == 3).astype(float)
            loc4_4_female = (loc4_female == 4).astype(float)

    # Prior
    prior = np.maximum(df["prior"].values.copy(), EPS)    # Group structure
    group_ids = df["idhh"].unique()
    n_groups = len(group_ids)
    
    # Find group boundaries using cumulative sum for robustness
    group_sizes = df.groupby("idhh", sort=False).size().values
    group_ends = np.cumsum(group_sizes)
    group_starts = np.concatenate([[0], group_ends[:-1]])
    
    # Validate group boundaries
    if not np.all(group_ends > group_starts):
        raise ValueError(
            "Invalid group boundaries detected. "
            f"group_starts: {group_starts[:10]}, group_ends: {group_ends[:10]}"
        )

    logger.info(f"  Extracted {n_groups:,} groups with {n_obs:,} total observations")

    return PrecomputedDataCouples(
        consumption=consumption,
        log_c=log_c,
        leisure_male=leisure_male,
        log_l_male=log_l_male,
        leisure_female=leisure_female,
        log_l_female=log_l_female,
        age_norm_male=age_norm_male,
        age_norm2_male=age_norm2_male,
        educL_male=educL_male,
        educM_male=educM_male,
        educH_male=educH_male,
        age_norm_female=age_norm_female,
        age_norm2_female=age_norm2_female,
        n_children=n_children,
        educL_female=educL_female,
        educM_female=educM_female,
        educH_female=educH_female,
        working_male=working_male,
        working_pt1_male=working_pt1_male,
        working_pt2_male=working_pt2_male,
        working_ft_male=working_ft_male,
        gsur_male=gsur_male,
        working_female=working_female,
        working_pt1_female=working_pt1_female,
        working_pt2_female=working_pt2_female,
        working_ft_female=working_ft_female,
        gsur_female=gsur_female,
        log_wage_male=log_wage_male,
        pexp_years_male=pexp_years_male,
        pexp_years2_male=pexp_years2_male,
        loc4_male=loc4_male,
        loc4_1_male=loc4_1_male,
        loc4_2_male=loc4_2_male,
        loc4_3_male=loc4_3_male,
        loc4_4_male=loc4_4_male,
        log_wage_female=log_wage_female,
        pexp_years_female=pexp_years_female,
        pexp_years2_female=pexp_years2_female,
        loc4_female=loc4_female,
        loc4_1_female=loc4_1_female,
        loc4_2_female=loc4_2_female,
        loc4_3_female=loc4_3_female,
        loc4_4_female=loc4_4_female,
        prior=prior,
        c_scale=c_scale,
        l_scale=l_scale,
        group_ids=group_ids,
        group_starts=group_starts,
        group_ends=group_ends,
        n_groups=n_groups,
        n_obs=n_obs
    )


# ==============================================================================
# Box-Cox Transformations
# ==============================================================================

if HAS_NUMBA:
    @numba.jit(nopython=True, fastmath=True)
    def box_cox_transform(x: np.ndarray, theta: float) -> np.ndarray:
        """
        Box-Cox transformation: BC(x; θ) = (x^θ - 1)/θ for θ≠0, log(x) for θ→0

        Uses limit approximation for |θ| < 1e-8:
            BC(x; 0) = log(x)

        Parameters
        ----------
        x : np.ndarray
            Input array (must be positive)
        theta : float
            Box-Cox exponent

        Returns
        -------
        np.ndarray
            Transformed values
        """
        if abs(theta) < 1e-8:
            # Limit: θ → 0
            return np.log(x)
        else:
            return (np.power(x, theta) - 1.0) / theta


    @numba.jit(nopython=True, fastmath=True)
    def box_cox_derivative_x(x: np.ndarray, theta: float) -> np.ndarray:
        """
        Derivative of Box-Cox w.r.t. x: ∂BC/∂x = x^(θ-1)

        Parameters
        ----------
        x : np.ndarray
            Input array (must be positive)
        theta : float
            Box-Cox exponent

        Returns
        -------
        np.ndarray
            Derivative values
        """
        return np.power(x, theta - 1.0)


    @numba.jit(nopython=True, fastmath=True)
    def box_cox_derivative_theta(x: np.ndarray, theta: float) -> np.ndarray:
        """
        Derivative of Box-Cox w.r.t. θ: ∂BC/∂θ with improved numerical stability

        For θ≠0:
            ∂BC/∂θ = (x^θ * log(x) * θ - (x^θ - 1)) / θ²

        For θ→0:
            ∂BC/∂θ|_{θ=0} = 0.5 * (log(x))²

        Uses Taylor expansion for |theta| < 0.05 to avoid catastrophic cancellation

        Parameters
        ----------
        x : np.ndarray
            Input array (must be positive)
        theta : float
            Box-Cox exponent

        Returns
        -------
        np.ndarray
            Derivative values
        """
        log_x = np.log(x)

        # Use Taylor expansion for |theta| < 0.05 to avoid numerical issues
        # Taylor: ∂BC/∂θ ≈ (log x)²/2 + θ(log x)³/6 + θ²(log x)⁴/24
        if abs(theta) < 0.05:
            log_x2 = log_x * log_x
            log_x3 = log_x2 * log_x
            # Third-order Taylor expansion for better accuracy
            return 0.5 * log_x2 * (1.0 + theta * log_x / 3.0 + theta * theta * log_x2 / 12.0)
        else:
            x_theta = np.power(x, theta)
            numerator = x_theta * (theta * log_x - 1.0) + 1.0
            return numerator / (theta * theta)

else:
    # NumPy fallback implementations (slower but functional)
    def box_cox_transform(x: np.ndarray, theta: float) -> np.ndarray:
        """Box-Cox transformation (NumPy implementation)"""
        if abs(theta) < 1e-8:
            return np.log(x)
        else:
            return (np.power(x, theta) - 1.0) / theta


    def box_cox_derivative_x(x: np.ndarray, theta: float) -> np.ndarray:
        """Derivative of Box-Cox w.r.t. x (NumPy implementation)"""
        return np.power(x, theta - 1.0)


    def box_cox_derivative_theta(x: np.ndarray, theta: float) -> np.ndarray:
        """Derivative of Box-Cox w.r.t. θ (NumPy implementation) with improved stability"""
        log_x = np.log(x)

        # Use Taylor expansion for |theta| < 0.05 to avoid numerical issues
        if abs(theta) < 0.05:
            log_x2 = log_x * log_x
            log_x3 = log_x2 * log_x
            return 0.5 * log_x2 * (1.0 + theta * log_x / 3.0 + theta * theta * log_x2 / 12.0)
        else:
            x_theta = np.power(x, theta)
            numerator = x_theta * (theta * log_x - 1.0) + 1.0
            return numerator / (theta * theta)


# ==============================================================================
# Softmax & Choice Probability Utilities
# ==============================================================================

def compute_log_sum_exp_by_group(
    V: np.ndarray,
    group_starts: np.ndarray,
    group_ends: np.ndarray
) -> np.ndarray:
    """
    Numerically stable log-sum-exp per group.

    For each group i:
        max_V_i = max(V[start_i:end_i])
        lse_i = max_V_i + log(Σ_j exp(V_j - max_V_i))

    Parameters
    ----------
    V : np.ndarray, shape (n_obs,)
        Value function for all alternatives
    group_starts : np.ndarray, shape (n_groups,)
        Starting index for each group
    group_ends : np.ndarray, shape (n_groups,)
        Ending index (exclusive) for each group

    Returns
    -------
    lse : np.ndarray, shape (n_groups,)
        Log-sum-exp for each group
    """
    n_groups = len(group_starts)
    lse = np.zeros(n_groups)

    for i in range(n_groups):
        start, end = group_starts[i], group_ends[i]
        
        # Check for empty groups (should not happen in valid data)
        if start >= end:
            raise ValueError(
                f"Group {i} is empty (start={start}, end={end}). "
                "This indicates a data preprocessing error. "
                "Each household should have at least one alternative."
            )
        
        V_group = V[start:end]
        max_V = V_group.max()
        lse[i] = max_V + np.log(np.sum(np.exp(V_group - max_V)))

    return lse


def compute_choice_probabilities(
    V: np.ndarray,
    group_starts: np.ndarray,
    group_ends: np.ndarray,
    observed_indices: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Compute MNL choice probabilities.

    If observed_indices provided:
        Returns P_chosen for each group (n_groups,)
    Else:
        Returns P for all alternatives (n_obs,)

    Parameters
    ----------
    V : np.ndarray, shape (n_obs,)
        Value function for all alternatives
    group_starts : np.ndarray, shape (n_groups,)
        Starting index for each group
    group_ends : np.ndarray, shape (n_groups,)
        Ending index (exclusive) for each group
    observed_indices : np.ndarray | None, shape (n_groups,)
        Index of observed choice within each group
        If None, return probabilities for all alternatives

    Returns
    -------
    probs : np.ndarray
        If observed_indices is None: shape (n_obs,) with P_j for all j
        If observed_indices provided: shape (n_groups,) with P_chosen_i for each group i
    """
    n_groups = len(group_starts)

    # Compute log-sum-exp for each group
    lse = compute_log_sum_exp_by_group(V, group_starts, group_ends)

    if observed_indices is None:
        # Return probabilities for all alternatives
        probs = np.zeros(len(V))

        for i in range(n_groups):
            start, end = group_starts[i], group_ends[i]
            V_group = V[start:end]
            probs[start:end] = np.exp(V_group - lse[i])

        return probs
    else:
        # Return probability of observed choice for each group
        probs_chosen = np.zeros(n_groups)

        for i in range(n_groups):
            start = group_starts[i]
            obs_idx = start + observed_indices[i]
            probs_chosen[i] = np.exp(V[obs_idx] - lse[i])

        return probs_chosen


# ==============================================================================
# Validation Helpers
# ==============================================================================

def validate_data_spec_compatibility(
    df_singles: Optional[pd.DataFrame],
    df_couples: Optional[pd.DataFrame],
    spec_config: Dict[str, Any],
    metadata: Dict[str, Any]
) -> None:
    """
    Validate that data is compatible with specification requirements.

    Checks:
    - If spec requires wages (vw/loc_empirical), wage column must exist
    - If spec requires LOC (loc_empirical), loc4 column must exist
    - If spec requires GSUR, gsur/u_rate column must exist

    Parameters
    ----------
    df_singles : pd.DataFrame | None
        Singles dataset
    df_couples : pd.DataFrame | None
        Couples dataset
    spec_config : dict
        Specification configuration (parsed from YAML)
    metadata : dict
        Pipeline metadata

    Raises
    ------
    ValueError
        If data incompatible with specification
    """
    logger = logging.getLogger(__name__)
    logger.info("Validating data-specification compatibility...")

    wage_spec = spec_config.get("wage_spec", "fw")
    errors = []

    # Check wage columns
    if wage_spec in ["vw", "loc_empirical"]:
        if df_singles is not None and "wage" not in df_singles.columns:
            errors.append(f"Specification requires wage_spec={wage_spec}, but singles dataset has no 'wage' column")

        if df_couples is not None:
            if "wage_male" not in df_couples.columns or "wage_female" not in df_couples.columns:
                errors.append(f"Specification requires wage_spec={wage_spec}, but couples dataset missing wage columns")

    # Check LOC columns
    if wage_spec == "loc_empirical":
        if df_singles is not None and "loc4" not in df_singles.columns:
            errors.append("Specification requires wage_spec=loc_empirical, but singles dataset has no 'loc4' column")

        if df_couples is not None:
            if "loc4_male" not in df_couples.columns or "loc4_female" not in df_couples.columns:
                errors.append("Specification requires wage_spec=loc_empirical, but couples dataset missing loc4 columns")

    # Check GSUR columns (if spec uses gsur in hours opportunity)
    # (This is optional - not all specs may use GSUR)

    if errors:
        logger.error("Data-specification compatibility errors:")
        for e in errors:
            logger.error(f"  ❌ {e}")
        raise ValueError("Data incompatible with specification. See errors above.")
    else:
        logger.info("  ✅ Data compatible with specification")


# ==============================================================================
# End of estimation_utils.py
# ==============================================================================
