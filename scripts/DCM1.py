#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Estimate labour-supply preference parameters with Biogeme (DCM stage).

This script reads the wide-format DCM datasets produced by ``scripts/scenarios.py``,
filters them for the required regressors, and estimates a multinomial logit model
separately for each gender. Results (parameter CSV only) are written under
``reports/biogeme/<gender>/``.

Example
-------
    # Estimate both genders (default)
    python scripts/DCM1.py

    # Estimate males only, storing outputs under a custom directory
    python scripts/DCM1.py --genders male --output-dir reports/custom_biogeme

"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Sequence

_JAXLIB_DIR = Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages" / "jaxlib"
if _JAXLIB_DIR.exists():
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(_JAXLIB_DIR))
    current_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{_JAXLIB_DIR}{os.pathsep}{current_path}"

os.environ.setdefault("BIOGEME_NO_JAX", "1")

import numpy as np
import pandas as pd

pd.set_option("future.no_silent_downcasting", True)

import biogeme.biogeme as bio
import biogeme.database as db
import biogeme.models as models
from biogeme.expressions import Beta, Variable
from biogeme.exceptions import BiogemeError

from path_helpers import data_root, reports_root

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = data_root() / "processed" / "scenarios"
DEFAULT_GENDERS: Sequence[str] = ("male", "female")
DEFAULT_LABELS: Sequence[str] = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")
DEFAULT_OUTPUT_DIR = reports_root() / "biogeme"

LOGGER = logging.getLogger(__name__)

# Scenario-specific regressors expected in the dataset
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_setattr(obj, attr: str, value) -> None:
    """Attempt to set an attribute on Biogeme objects, ignoring unsupported ones."""
    try:
        setattr(obj, attr, value)
    except (AttributeError, BiogemeError, TypeError):
        pass


def _detect_labels_from_df(df: pd.DataFrame) -> tuple[str, ...]:
    """Infer scenario labels from columns named ``logy_<label>`` in natural order (h0,h1,...)."""
    labs = [c.split("logy_", 1)[1] for c in df.columns if c.startswith("logy_")]
    labs = sorted(set(labs), key=lambda s: (len(s), s))
    return tuple(labs)


# ---------------------------------------------------------------------------
# Data preparation helpers
# ---------------------------------------------------------------------------

def _wide_dataset_path(gender: str) -> Path:
    return SCENARIO_DIR / f"heads_wide_single_{gender}_dcm.parquet"


def _load_dataset(
    path: Path,
    labels: Sequence[str] | None,
    *,
    auto_labels: bool = False,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Load and sanity-check the wide DCM dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing wide DCM dataset: {path}. Run scripts/scenarios.py first."
        )

    df = pd.read_parquet(path)
    df = df.replace("", np.nan)

    labels_tuple: tuple[str, ...]
    if auto_labels or labels is None:
        labels_tuple = _detect_labels_from_df(df)
        if not labels_tuple:
            raise ValueError(
                "Could not auto-detect scenario labels from columns (expected logy_*)"
            )
        LOGGER.info("Auto-detected scenario labels: %s", ", ".join(labels_tuple))
    else:
        labels_tuple = tuple(labels)

    # Harmonize quadratic names to canonical log2y_/log2l_
    ren: dict[str, str] = {}
    for lab in labels_tuple:
        if f"logy2_{lab}" in df.columns and f"log2y_{lab}" not in df.columns:
            ren[f"logy2_{lab}"] = f"log2y_{lab}"
        if f"logl2_{lab}" in df.columns and f"log2l_{lab}" not in df.columns:
            ren[f"logl2_{lab}"] = f"log2l_{lab}"
    if ren:
        df = df.rename(columns=ren)

    df_columns = set(df.columns)
    missing_columns: set[str] = set()

    for col in ("idperson", "idhh", "actual_choice"):
        if col not in df_columns:
            missing_columns.add(col)

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
            missing_columns.add(canonical if not alt_name else f"{canonical} (or {alt_name})")

    if missing_columns:
        raise KeyError(
            f"Dataset {path} is missing the following columns: {sorted(missing_columns)}"
        )

    mask_valid = df["actual_choice"].isin(labels_tuple)
    if not mask_valid.all():
        dropped = df.loc[~mask_valid, ["idperson", "actual_choice"]]
        LOGGER.warning(
            "Dropping %d head(s) with invalid actual_choice labels:\n%s",
            len(dropped),
            dropped.to_string(index=False),
        )
        df = df.loc[mask_valid].copy()

    regressor_columns = [
        f"{base}_{label}" for base in SCENARIO_VARIABLES for label in labels_tuple
    ]
    before = len(df)
    df = df.dropna(subset=regressor_columns + ["actual_choice"])
    dropped_rows = before - len(df)
    if dropped_rows:
        LOGGER.warning("Dropped %d head(s) with missing regressors.", dropped_rows)

    return df.reset_index(drop=True), labels_tuple


def _prepare_biogeme_database(
    df: pd.DataFrame,
    labels: Sequence[str],
) -> tuple[db.Database, dict[str, int], list[str]]:
    """Construct a Biogeme database in the current (wide) format."""
    alt_ids = {label: idx + 1 for idx, label in enumerate(labels)}
    df = df.copy()
    df["choice_id"] = df["actual_choice"].map(alt_ids)
    if df["choice_id"].isna().any():
        raise ValueError(
            "Encountered household(s) with actual_choice outside the provided labels."
        )

    numeric_df = df.drop(columns=["actual_choice"], errors="ignore")
    avail_columns = [f"avail_{label}" for label in labels if f"avail_{label}" in df.columns]
    keep_columns = ["choice_id"] + [
        f"{base}_{label}" for label in labels for base in SCENARIO_VARIABLES
    ] + avail_columns
    missing_keep = set(keep_columns) - set(numeric_df.columns)
    if missing_keep:
        raise KeyError(f"Missing required columns for DCM: {sorted(missing_keep)}")

    numeric_df = numeric_df[keep_columns].apply(pd.to_numeric, errors="coerce")
    numeric_df["choice_id"] = numeric_df["choice_id"].astype(int)
    for col in avail_columns:
        numeric_df[col] = (numeric_df[col] != 0).astype(int)
    if numeric_df.isna().any().any():
        raise ValueError("Unexpected NaN values remain in numeric dataset for Biogeme.")

    database = db.Database("labour_supply", numeric_df)
    return database, alt_ids, avail_columns


# ---------------------------------------------------------------------------
# Model specification
# ---------------------------------------------------------------------------

def _build_utility_expressions(
    labels: Sequence[str],
    alt_ids: dict[str, int],
    df: pd.DataFrame,
    *,
    include_ascs: bool = False,
) -> tuple[dict[int, object], dict[int, object], dict[str, Beta], list[str]]:
    """Create utility expressions and availability dictionary."""
    coeffs = {
        "alpha_1": Beta("alpha_1", 0.0, None, None, 0),
        "alpha_2": Beta("alpha_2", 0.0, None, None, 0),
        "alpha_3": Beta("alpha_3", 0.0, None, None, 0),
        "alpha_4": Beta("alpha_4", 0.0, None, None, 0),
        "alpha_5": Beta("alpha_5", 0.0, None, None, 0),
        "alpha_6": Beta("alpha_6", 0.0, None, None, 0),
        "beta_1": Beta("beta_1", 0.0, None, None, 0),
        "beta_2": Beta("beta_2", 0.0, None, None, 0),
        "gamma": Beta("gamma", 0.0, None, None, 0),
    }

    if include_ascs:
        base_label = labels[0]
        coeffs[f"ASC_{base_label}"] = Beta(f"ASC_{base_label}", 0.0, None, None, 1)
        for lab in labels[1:]:
            coeffs[f"ASC_{lab}"] = Beta(f"ASC_{lab}", 0.0, None, None, 0)

    V: dict[int, object] = {}
    av: dict[int, object] = {}
    avail_cols_used: list[str] = []
    for label in labels:
        alt = alt_ids[label]
        logy = Variable(f"logy_{label}")
        logl = Variable(f"logl_{label}")
        leila = Variable(f"Leila_{label}")
        leila2 = Variable(f"Leila2_{label}")
        lochi = Variable(f"lochi_{label}")
        logdc = Variable(f"logdc_{label}")
        log2y = Variable(f"log2y_{label}")
        log2l = Variable(f"log2l_{label}")
        logyl = Variable(f"logyl_{label}")

        asc_term = coeffs.get(f"ASC_{label}", 0) if include_ascs else 0

        V[alt] = asc_term + (
            coeffs["alpha_1"] * logy
            + coeffs["alpha_2"] * logl
            + coeffs["alpha_3"] * leila
            + coeffs["alpha_4"] * leila2
            + coeffs["alpha_5"] * lochi
            + coeffs["alpha_6"] * logdc
            + coeffs["beta_1"] * log2y
            + coeffs["beta_2"] * log2l
            + coeffs["gamma"] * logyl
        )

        avail_name = f"avail_{label}"
        if avail_name in df.columns:
            av[alt] = Variable(avail_name)
            avail_cols_used.append(avail_name)
        else:
            av[alt] = 1

    return V, av, coeffs, avail_cols_used

def estimate_model(
    gender: str,
    df: pd.DataFrame,
    labels: Sequence[str],
    output_dir: Path,
    *,
    include_ascs: bool = False,
) -> Path:
    """Estimate the multinomial logit model for the given gender."""
    database, alt_ids, _ = _prepare_biogeme_database(df, labels)
    V, av, coeffs, avail_cols_used = _build_utility_expressions(
        labels,
        alt_ids,
        df,
        include_ascs=include_ascs,
    )
    choice = Variable("choice_id")
    logprob = models.loglogit(V, av, choice)

    if avail_cols_used:
        LOGGER.info("[%s] Using availability columns: %s", gender, ", ".join(avail_cols_used))

    tag = "ascsON" if include_ascs else "ascsOFF"
    model_name = f"dcm_{gender}_{tag}"
    model_output_dir = output_dir / f"{gender}_{tag}"
    model_output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.info("[%s] include_ascs=%s  -> model=%s  out=%s", gender, include_ascs, model_name, model_output_dir)

    # Remove artefacts from previous runs to avoid versioned files (~01, ~02, ...).
    cleanup_patterns = (
        f"{model_name}*.html",
        f"{model_name}*.yaml",
        f"{model_name}*.tex",
        f"{model_name}*.estat",
        f"{model_name}*.log",
        f"__{model_name}.iter",
    )

    for pattern in cleanup_patterns:
        for file_path in model_output_dir.glob(pattern):
            try:
                file_path.unlink()
            except OSError:
                pass

    for pattern in cleanup_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            try:
                file_path.unlink()
            except OSError:
                pass

    biogeme_model = bio.BIOGEME(database, logprob)
    if hasattr(biogeme_model, "model_name"):
        _safe_setattr(biogeme_model, "model_name", model_name)
    else:  # pragma: no cover
        _safe_setattr(biogeme_model, "modelName", model_name)

    if hasattr(biogeme_model, "set_output_directory"):
        biogeme_model.set_output_directory(model_output_dir)

    LOGGER.info("[%s] Estimation started with %d heads.", gender, len(df))
    results = biogeme_model.estimate()

    param_path = model_output_dir / f"{model_name}_parameters.csv"
    if hasattr(results, "get_pandas_estimated_parameters"):
        params_df = results.get_pandas_estimated_parameters()
    elif hasattr(results, "get_estimated_parameters"):
        params_df = results.get_estimated_parameters()
    else:
        params_df = results.getEstimatedParameters()
    params_df.to_csv(param_path, index=True)

    opt_ll = None
    try:
        opt_ll = getattr(results, "log_likelihood", None)
        if opt_ll is None and hasattr(results, "data"):
            opt_ll = getattr(results.data, "logLike", opt_ll)
        if opt_ll is None and hasattr(results, "raw_estimation_results"):
            raw = results.raw_estimation_results
            opt_ll = getattr(raw, "log_likelihood", getattr(raw, "logLike", None))
    except Exception:  # pragma: no cover - fallback to None
        opt_ll = None

    null_ll = None
    try:
        null_ll = biogeme_model.nullLogLikelihood(av, choice)
    except Exception:
        try:
            null_ll = getattr(results, "nullLogLike", None)
            if null_ll is None and hasattr(results, "data"):
                null_ll = getattr(results.data, "nullLogLike", None)
        except Exception:
            null_ll = None

    rho2 = None
    rho2_adj = None
    if null_ll is not None and opt_ll is not None and null_ll != 0:
        k = 0
        try:
            beta_values = getattr(results, "getBetaValues", lambda: {})()
            if isinstance(beta_values, dict):
                k = len(beta_values)
            else:
                k = len(list(beta_values))
        except Exception:
            beta_values = None
        if not k:
            try:
                if isinstance(params_df, pd.DataFrame):
                    if "robust t-test" in params_df.columns:
                        k = int(params_df["robust t-test"].notna().sum())
                    else:
                        k = int(params_df.shape[0])
            except Exception:
                k = 0
        rho2 = 1 - opt_ll / null_ll
        rho2_adj = 1 - (opt_ll - k) / null_ll

    # Remove any reports Biogeme might have generated despite the flags.
    # Move Biogeme reports from project root (where they land by default) into the gender folder.
    transfer_patterns = (
        f"{model_name}*.html",
        f"{model_name}*.yaml",
        f"{model_name}*.tex",
        f"{model_name}*.log",
        f"__{model_name}.iter",
    )
    for pattern in transfer_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            target = model_output_dir / file_path.name
            try:
                if target.exists():
                    target.unlink()
                file_path.replace(target)
            except OSError:
                pass

    LOGGER.info("[%s] Estimation completed (%s). Parameters saved to %s", gender, model_name, param_path)
    if opt_ll is not None:
        LOGGER.info("[%s] [%s] Log-likelihood at optimum: %.4f", gender, model_name, opt_ll)
    if null_ll is not None and rho2 is not None and rho2_adj is not None:
        LOGGER.info(
            "[%s] [%s] LL(null)=%.6f  LL*=%.6f  rho2=%.4f  rho2_adj=%.4f",
            gender,
            model_name,
            null_ll,
            opt_ll,
            rho2,
            rho2_adj,
        )

    for method_name, suffix in (
        ("getVarCovar", "_vcov.csv"),
        ("getRobustVarCovar", "_robust_vcov.csv"),
    ):
        try:
            method = getattr(results, method_name, None)
            if method is None:
                continue
            matrix = method()
            if matrix is None:
                continue
            vcov_path = model_output_dir / f"{model_name}{suffix}"
            if hasattr(matrix, "to_csv"):
                matrix.to_csv(vcov_path)
            else:
                pd.DataFrame(matrix).to_csv(vcov_path, index=True)
        except Exception:
            continue

    LOGGER.info("[%s] Reports (if any) placed in %s", model_name, model_output_dir)
    return param_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate labour-supply DCM parameters using Biogeme."
    )
    parser.add_argument(
        "--genders",
        nargs="+",
        choices=DEFAULT_GENDERS,
        default=list(DEFAULT_GENDERS),
        help="Gender-specific datasets to estimate (default: both).",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        choices=DEFAULT_LABELS,
        default=list(DEFAULT_LABELS),
        help="Scenario labels to include in the model (default: all seven).",
    )
    parser.add_argument(
        "--auto-labels",
        action="store_true",
        help="Detect scenario labels from the dataset columns (ignores --labels).",
    )
    parser.add_argument(
        "--include-ascs",
        action="store_true",
        help="Include alternative-specific constants (default: disabled).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where estimation outputs are stored (default: reports/biogeme).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=SCENARIO_DIR,
        help="Directory containing the wide DCM datasets (default: Data/processed/scenarios).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity (default: INFO).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

    labels_cfg: Sequence[str] | None = None
    if not args.auto_labels:
        labels_cfg = tuple(args.labels)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for gender in args.genders:
        try:
            dataset_path = args.data_dir / f"heads_wide_single_{gender}_dcm.parquet"
            df, labels = _load_dataset(
                dataset_path,
                labels_cfg,
                auto_labels=args.auto_labels,
            )
            estimate_model(
                gender,
                df,
                labels,
                output_dir,
                include_ascs=args.include_ascs,
            )
        except Exception as exc:  # pragma: no cover - keep running other genders
            LOGGER.error("[%s] Estimation failed: %s", gender, exc, exc_info=True)


if __name__ == "__main__":
    main()

