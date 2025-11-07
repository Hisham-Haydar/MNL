#!/usr/bin/env python
"""
Post-estimation diagnostics for the Biogeme DCM translog utility model.

This script reads the estimated parameters and corresponding wide-format dataset
for a selected gender, computes marginal utilities, produces diagnostics plots,
evaluates predictive accuracy, and exports an HTML report consolidating the
findings together with the generated figures.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import re
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from path_helpers import data_root, reports_root

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "The 'matplotlib' package is required to run this script. "
        "Install it via 'pip install matplotlib'."
    ) from exc

import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from scipy.special import logsumexp

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Resolve storage-aware paths for data and reports.
DATA_DIR = data_root() / "processed" / "scenarios"
BIOGEME_REPORT_DIR = reports_root() / "biogeme"
MLE_REPORT_DIR = reports_root() / "mle_dcm"

LABELS: tuple[str, ...] = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")


def _load_json_if_exists(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _unique_path(path: Path) -> Path:
    """Return a path with ~01, ~02, ... suffix if needed to avoid overwriting existing files."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem}~{counter:02d}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


EFFECT_INTERACTION_PATTERNS: tuple[str, ...] = (
    "{}_m",
    "{}_g",
    "{}_G",
    "{}_dgn",
    "{}:gender",
)


def load_dataset_for_gender(gender: str) -> pd.DataFrame:
    """Load the analysis dataset for a gender or pooled configuration."""
    if gender == "pooled":
        male_path = DATA_DIR / "heads_wide_single_male_dcm.parquet"
        female_path = DATA_DIR / "heads_wide_single_female_dcm.parquet"
        if not male_path.exists():
            raise FileNotFoundError(f"Missing male pooled dataset: {male_path}")
        if not female_path.exists():
            raise FileNotFoundError(f"Missing female pooled dataset: {female_path}")

        male = pd.read_parquet(male_path).copy()
        female = pd.read_parquet(female_path).copy()

        male["dgn"] = pd.to_numeric(male.get("dgn"), errors="coerce").fillna(1.0)
        female["dgn"] = pd.to_numeric(female.get("dgn"), errors="coerce").fillna(0.0)
        male["dgn"] = 1.0
        female["dgn"] = 0.0

        common_columns = sorted(set(male.columns).intersection(female.columns))
        if not common_columns:
            raise ValueError("Male and female pooled datasets share no common columns.")
        pooled = pd.concat(
            [male[common_columns], female[common_columns]],
            ignore_index=True,
            sort=False,
        )
        return pooled

    dataset_path = DATA_DIR / f"heads_wide_single_{gender}_dcm.parquet"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Missing wide dataset: {dataset_path}")
    return pd.read_parquet(dataset_path)


def _bc(x: np.ndarray, alpha: float) -> np.ndarray:
    x = np.clip(np.asarray(x, dtype=float), 1e-12, None)
    if abs(alpha) < 1e-8:
        return np.log(x)
    return (np.power(x, alpha) - 1.0) / alpha


def muc_boxcox(params: Mapping[str, float], consumption: np.ndarray, y_ref: float) -> np.ndarray:
    c_norm = np.clip(np.asarray(consumption, dtype=float) / y_ref, 1e-6, 1.0)
    alpha_c = float(params.get("alpha_c", 0.0))
    beta_c = float(params.get("beta_c", 0.0))
    return beta_c * np.power(c_norm, alpha_c - 1.0) / y_ref


def mul_boxcox(
    params: Mapping[str, float],
    leisure: np.ndarray,
    Z: Mapping[str, float],
    *,
    T_endow: float = 80.0,
) -> np.ndarray:
    l_norm = np.clip(np.asarray(leisure, dtype=float) / T_endow, 1e-6, 1.0)
    alpha_l = float(params.get("alpha_l", 0.0))
    beta_l = float(params.get("beta_l0", 0.0))
    for key, value in Z.items():
        beta_l += float(params.get(f"delta_{key}", 0.0)) * float(value)
    return beta_l * np.power(l_norm, alpha_l - 1.0) / T_endow


def uij_boxcox(
    params: Mapping[str, float],
    asc_j: float,
    C_norm: float,
    L_norm: float,
    Z: Mapping[str, float],
) -> float:
    beta_c = float(params.get("beta_c", 0.0))
    alpha_c = float(params.get("alpha_c", 0.0))
    alpha_l = float(params.get("alpha_l", 0.0))
    beta_l = float(params.get("beta_l0", 0.0))
    for key, value in Z.items():
        beta_l += float(params.get(f"delta_{key}", 0.0)) * float(value)
    return (
        asc_j
        + beta_c * _bc(C_norm, alpha_c)
        + beta_l * _bc(L_norm, alpha_l)
    )


def eff(
    params: Mapping[str, float],
    base: str,
    dgn: float | np.ndarray,
    *,
    patterns: tuple[str, ...] = EFFECT_INTERACTION_PATTERNS,
) -> float | np.ndarray:
    """Return base + interaction*dgn for the requested parameter."""
    d_arr = np.asarray(dgn, dtype=float)
    base_val = float(params.get(base, 0.0))
    interaction = 0.0
    for pattern in patterns:
        name = pattern.format(base)
        if name in params:
            interaction = float(params[name])
            break
    result = base_val + interaction * d_arr
    if np.ndim(result) == 0:
        return float(result)
    return result


def _broadcast_like(value: float | np.ndarray, template: np.ndarray) -> np.ndarray:
    """Ensure value is an ndarray compatible with template."""
    arr = np.asarray(value, dtype=float)
    if np.ndim(arr) == 0:
        arr = np.full_like(template, float(arr))
    return arr


# ---------------------------------------------------------------------------
# CLI / Variant helpers
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Biogeme DCM results (ASC-aware).")
    parser.add_argument(
        "--genders",
        nargs="+",
        default=["male", "female"],
        choices=["male", "female", "pooled"],
        help="Which genders to analyze.",
    )
    parser.add_argument(
        "--variant",
        default="auto",
        help=(
            "Which parameter variant to analyze (e.g., ascsON, ascsON_center_ys1000). "
            "Use 'auto' to pick the most recent available variant."
        ),
    )
    parser.add_argument(
        "--source",
        default="biogeme",
        choices=("biogeme", "mle"),
        help="Which estimator output to analyze (default: biogeme).",
    )
    parser.add_argument(
        "--annotate-biogeme-html",
        action="store_true",
        help="Annotate Biogeme HTML report by wrapping parameter names with tooltip spans.",
    )
    return parser.parse_args()


def _report_base_dir(source: str) -> Path:
    if source == "biogeme":
        return BIOGEME_REPORT_DIR
    if source == "mle":
        return MLE_REPORT_DIR
    raise ValueError(f"Unsupported source: {source}")


def _candidate_param_dirs(gender: str, variant: str, source: str) -> List[Path]:
    base_dir = _report_base_dir(source)
    candidates = [base_dir / f"{gender}_{variant}"]
    sub_map = {
        "biogeme": ("boxcox", "boxcox_biogeme"),
        "mle": ("boxcox",),
    }
    for sub in sub_map.get(source, ()):
        candidates.append(base_dir / sub / f"{gender}_{variant}")
    return candidates


def param_dir_for(gender: str, variant: str, source: str) -> Path:
    for candidate in _candidate_param_dirs(gender, variant, source):
        if candidate.exists():
            return candidate
    return _candidate_param_dirs(gender, variant, source)[0]


def param_csv_for(gender: str, variant: str, source: str) -> Path:
    if source == "biogeme":
        prefixes = [f"dcm_{gender}_{variant}", f"boxcox_{gender}_{variant}"]
    elif source == "mle":
        prefixes = [f"mle_{gender}_{variant}", f"boxcox_{gender}_{variant}"]
    else:
        prefixes = [f"{gender}_{variant}"]

    for directory in _candidate_param_dirs(gender, variant, source):
        if not directory.exists():
            continue
        for prefix in prefixes:
            candidate = directory / f"{prefix}_parameters.csv"
            if candidate.exists():
                return candidate
        generic = sorted(directory.glob("*_parameters.csv"))
        if generic:
            return generic[0]

    directory = _candidate_param_dirs(gender, variant, source)[0]
    fallback_prefix = prefixes[0] if prefixes else f"{gender}_{variant}"
    return directory / f"{fallback_prefix}_parameters.csv"


def resolve_variant(gender: str, requested: str, source: str) -> tuple[str, Path]:
    if requested != "auto":
        csv_path = param_csv_for(gender, requested, source)
        if csv_path.exists():
            return requested, csv_path
        raise FileNotFoundError(
            f"No parameter file for {gender} variant '{requested}' at {csv_path}"
        )

    candidates: list[tuple[str, Path, float]] = []
    base_dir = _report_base_dir(source)
    prefix = f"{gender}_"
    search_roots: List[Path] = [base_dir]
    if source == "biogeme":
        for sub in ("boxcox", "boxcox_biogeme"):
            sub_dir = base_dir / sub
            if sub_dir.exists():
                search_roots.append(sub_dir)

    seen: set[str] = set()
    for root in search_roots:
        for folder in root.glob(f"{gender}_*"):
            if not folder.is_dir():
                continue
            name = folder.name
            if not name.startswith(prefix):
                continue
            variant = name[len(prefix) :]
            if variant in seen:
                continue
            csv_path = param_csv_for(gender, variant, source)
            if not csv_path.exists():
                continue
            seen.add(variant)
            try:
                mtime = csv_path.stat().st_mtime
            except OSError:
                mtime = -1.0
            candidates.append((variant, csv_path, mtime))

    if candidates:
        variant, path, _ = max(candidates, key=lambda item: item[2])
        return variant, path

    if source == "biogeme":
        legacy = BIOGEME_REPORT_DIR / gender / f"dcm_{gender}_parameters.csv"
        if legacy.exists():
            return "ascsOFF", legacy
    if source == "mle":
        legacy = MLE_REPORT_DIR / f"mle_{gender}_ascsOFF.csv"
        if legacy.exists():
            return "ascsOFF", legacy
    raise FileNotFoundError(
        f"No parameter file for {gender} (source={source})."
    )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_parameters(path: Path) -> tuple[pd.DataFrame, dict[str, float], dict[str, float]]:
    """Robust Biogeme parameter parser with name recovery."""
    if not path.exists():
        raise FileNotFoundError(f"Missing parameter CSV: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Parameter file {path} is empty.")

    name_col = None
    for c in ("Parameter", "parameter", "Name", "name", "Unnamed: 0"):
        if c in df.columns:
            col = df[c]
            if col.dtype == object or col.astype(str).str.contains("[A-Za-z_]").any():
                name_col = c
                break
    if name_col is not None:
        df = df.set_index(name_col)

    value_col = None
    for candidate in ("Value", "value", "Estimate", "Coefficient", "Est.", "coef"):
        if candidate in df.columns:
            value_col = candidate
            break
    if value_col is None:
        candidates = [c for c in df.columns if c not in df.index.names]
        value_col = candidates[0] if candidates else df.columns[0]

    if (df.index.dtype != object) or df.index.astype(str).str.fullmatch(r"\d+").all():
        for cand in ("Parameter", "parameter", "Name", "name"):
            if cand in df.columns:
                params = dict(zip(df[cand].astype(str), df[value_col].astype(float)))
                break
        else:
            raise ValueError(
                "Parameter names not found in CSV. Expected a 'Name' or 'Parameter' column."
            )
    else:
        params = df[value_col].astype(float).to_dict()

    asc_params = {k: v for k, v in params.items() if k.startswith("ASC_")}
    return df, params, asc_params


def detect_labels(df: pd.DataFrame) -> tuple[str, ...]:
    """Infer available scenario suffixes in natural order (h0, h1, ...)."""
    labs = [col.split("logy_", 1)[1] for col in df.columns if col.startswith("logy_")]
    labs = sorted(set(labs), key=lambda s: (len(s), s))
    if not labs:
        raise ValueError("Could not detect scenario labels (expected columns logy_*).")
    return tuple(labs)


def harmonize_quadratic_columns(df: pd.DataFrame, labels: Iterable[str]) -> pd.DataFrame:
    """Rename logy2_/logl2_ variants to log2y_/log2l_ for internal consistency."""
    rename_map: dict[str, str] = {}
    for lab in labels:
        if f"logy2_{lab}" in df.columns and f"log2y_{lab}" not in df.columns:
            rename_map[f"logy2_{lab}"] = f"log2y_{lab}"
        if f"logl2_{lab}" in df.columns and f"log2l_{lab}" not in df.columns:
            rename_map[f"logl2_{lab}"] = f"log2l_{lab}"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    """Validate that all required columns exist in the dataframe."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Dataset missing required columns: {missing}")


def get_series(df: pd.DataFrame, column: str) -> pd.Series:
    """Return dataframe column if present, otherwise a zero series placeholder."""
    if column in df.columns:
        return df[column]
    return pd.Series(0.0, index=df.index)


def annotate_biogeme_html(html_path: Path, label_map: dict, desc_map: dict):
    try:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    # Build map from readable label (value) to wrapped HTML span with description.
    reverse = {}
    for raw, readable in (label_map or {}).items():
        desc = (desc_map or {}).get(raw)
        reverse[str(readable)] = _tooltip_html(readable, desc)
    # Replace occurrences in table cells only: > name <
    for readable, wrapped in reverse.items():
        try:
            pattern = rf">(\s*){re.escape(readable)}(\s*)<"
            replacement = rf"> \1{wrapped}\2 <"
            html = re.sub(pattern, replacement, html)
        except re.error:
            continue
    try:
        html_path.write_text(html, encoding="utf-8")
    except Exception:
        pass


def compute_actual_logs(df: pd.DataFrame, labels: Iterable[str]) -> tuple[pd.Series, pd.Series]:
    """Extract log-consumption and log-leisure for each observation's actual choice."""
    logy_actual = pd.Series(np.nan, index=df.index)
    logl_actual = pd.Series(np.nan, index=df.index)
    actual_choice = df["actual_choice"]
    for lab in labels:
        mask = actual_choice == lab
        if not mask.any():
            continue
        logy_actual.loc[mask] = df.loc[mask, f"logy_{lab}"]
        logl_actual.loc[mask] = df.loc[mask, f"logl_{lab}"]
    return logy_actual.astype(float), logl_actual.astype(float)


def muc(
    logy: pd.Series,
    logl: pd.Series,
    y: pd.Series,
    params: Mapping[str, float],
    children: pd.Series | np.ndarray | float | None = None,
    dch: pd.Series | np.ndarray | float | None = None,
    *,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
    dgn: pd.Series | np.ndarray | float | None = None,
) -> pd.Series | np.ndarray:
    """Marginal utility of consumption."""
    logy_arr = np.asarray(logy, dtype=float)
    logl_arr = np.asarray(logl, dtype=float)
    y_arr = np.clip(np.asarray(y, dtype=float), 1e-3, None)

    if dgn is None:
        d_arr = np.zeros_like(logy_arr, dtype=float)
    else:
        d_arr = np.asarray(dgn, dtype=float)
        if np.ndim(d_arr) == 0:
            d_arr = np.full_like(logy_arr, float(d_arr))

    a1 = _broadcast_like(eff(params, "alpha_1", d_arr), logy_arr)
    b1 = _broadcast_like(eff(params, "beta_1", d_arr), logy_arr)
    g = _broadcast_like(eff(params, "gamma", d_arr), logy_arr)

    dU_dlogy = (
        a1
        - 2.0 * b1 * (C_LOGY + LN_SCALE)
        - g * C_LOGL
        + 2.0 * b1 * logy_arr
        + g * logl_arr
    )
    result = dU_dlogy / y_arr
    finite_mask = np.isfinite(result)
    if finite_mask.any():
        finite_vals = result[finite_mask]
        print(f"MUC range: {np.nanmin(finite_vals):.3f} -> {np.nanmax(finite_vals):.3f}")

    if isinstance(y, pd.Series):
        return pd.Series(result, index=y.index)
    return result


def mul(
    logy: pd.Series,
    logl: pd.Series,
    l: pd.Series,
    params: Mapping[str, float],
    leila: pd.Series | None = None,
    children: pd.Series | np.ndarray | float | None = None,
    dch: pd.Series | np.ndarray | float | None = None,
    *,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
    dgn: pd.Series | np.ndarray | float | None = None,
) -> pd.Series | np.ndarray:
    """Marginal utility of leisure, including Leila = log(l)*log(age) when available."""
    logy_arr = np.asarray(logy, dtype=float)
    logl_arr = np.asarray(logl, dtype=float)
    l_arr = np.clip(np.asarray(l, dtype=float), 1e-3, 168.0)

    if dgn is None:
        d_arr = np.zeros_like(logl_arr, dtype=float)
    else:
        d_arr = np.asarray(dgn, dtype=float)
        if np.ndim(d_arr) == 0:
            d_arr = np.full_like(logl_arr, float(d_arr))

    a2 = _broadcast_like(eff(params, "alpha_2", d_arr), logl_arr)
    b2 = _broadcast_like(eff(params, "beta_2", d_arr), logl_arr)
    g = _broadcast_like(eff(params, "gamma", d_arr), logl_arr)
    a3 = _broadcast_like(eff(params, "alpha_3", d_arr), logl_arr)
    a4 = _broadcast_like(eff(params, "alpha_4", d_arr), logl_arr)
    a5 = _broadcast_like(eff(params, "alpha_5", d_arr), logl_arr)
    a6 = _broadcast_like(eff(params, "alpha_6", d_arr), logl_arr)

    dU_dlogl = (
        a2
        - 2.0 * b2 * C_LOGL
        - g * C_LOGY
        - g * LN_SCALE
        + 2.0 * b2 * logl_arr
        + g * logy_arr
    )
    if leila is not None:
        leila_arr = np.asarray(leila, dtype=float)
        log_age = np.where(np.abs(logl_arr) > 1e-12, leila_arr / logl_arr, 0.0)
        if np.any(np.isfinite(log_age)):
            dU_dlogl = dU_dlogl + a3 * log_age + a4 * (log_age**2)

    if children is not None:
        children_arr = np.asarray(children, dtype=float)
        if children_arr.shape != logl_arr.shape and np.ndim(children_arr) == 0:
            children_arr = np.full_like(logl_arr, float(children_arr))
        dU_dlogl = dU_dlogl + a5 * children_arr

    if dch is not None:
        dch_arr = np.asarray(dch, dtype=float)
        if dch_arr.shape != logl_arr.shape and np.ndim(dch_arr) == 0:
            dch_arr = np.full_like(logl_arr, float(dch_arr))
        dU_dlogl = dU_dlogl + a6 * dch_arr

    finite_num = dU_dlogl[np.isfinite(dU_dlogl)]
    if finite_num.size:
        print(f"MUL range (raw numerator): {np.nanmin(finite_num):.3f} -> {np.nanmax(finite_num):.3f}")

    result = dU_dlogl / l_arr

    if isinstance(logl, pd.Series):
        return pd.Series(result, index=logl.index)
    return result


def solve_zero_muc(
    logl_value: float,
    params: Mapping[str, float],
    guess: float,
    *,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
    dgn_val: float = 0.0,
) -> float:
    """Solve for the consumption level where MUC crosses zero (holding logl fixed)."""
    if not np.isfinite(logl_value):
        return float("nan")
    if not np.isfinite(guess):
        guess = 0.0

    def equation(logy: float) -> float:
        gamma = eff(params, "gamma", dgn_val)
        alpha_1 = eff(params, "alpha_1", dgn_val)
        beta_1 = eff(params, "beta_1", dgn_val)
        return (
            alpha_1
            - 2.0 * beta_1 * (C_LOGY + LN_SCALE)
            - gamma * C_LOGL
            + 2.0 * beta_1 * logy
            + gamma * logl_value
        )

    try:
        logy_root = fsolve(equation, x0=guess, xtol=1e-10, maxfev=200)[0]
    except Exception:
        return float("nan")
    if not np.isfinite(logy_root):
        return float("nan")
    return float(np.exp(logy_root))


def solve_zero_mul(
    logy_value: float,
    params: Mapping[str, float],
    guess: float,
    *,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
    dgn_val: float = 0.0,
) -> float:
    """Solve for the leisure level where MUL crosses zero (holding log y fixed)."""
    if not np.isfinite(logy_value):
        return float("nan")
    if not np.isfinite(guess):
        guess = 0.0

    def equation(logl: float) -> float:
        gamma = eff(params, "gamma", dgn_val)
        alpha_2 = eff(params, "alpha_2", dgn_val)
        beta_2 = eff(params, "beta_2", dgn_val)
        return (
            alpha_2
            - 2.0 * beta_2 * C_LOGL
            - gamma * C_LOGY
            - gamma * LN_SCALE
            + 2.0 * beta_2 * logl
            + gamma * logy_value
        )

    try:
        logl_root = fsolve(equation, x0=guess, xtol=1e-10, maxfev=200)[0]
    except Exception:
        return float("nan")
    if not np.isfinite(logl_root):
        return float("nan")
    return float(np.exp(logl_root))


def utility_components(
    df: pd.DataFrame,
    labels: Iterable[str],
    params: Mapping[str, float],
    asc_params: Mapping[str, float],
    *,
    center_logs: bool = False,
    y_scale: float = 1.0,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
) -> pd.DataFrame:
    """Compute scenario utilities for each observation."""
    utils = pd.DataFrame(index=df.index)
    y_scale_val = float(y_scale)
    ln_scale_val = float(LN_SCALE)
    if np.isclose(ln_scale_val, 0.0) and not np.isclose(y_scale_val, 1.0):
        try:
            ln_scale_val = float(np.log(y_scale_val))
        except Exception:
            ln_scale_val = 0.0
    use_star = bool(center_logs) or not np.isclose(ln_scale_val, 0.0)

    if "dgn" in df.columns:
        dgn_values = np.asarray(pd.to_numeric(df["dgn"], errors="coerce").fillna(0.0), dtype=float)
    else:
        dgn_values = np.zeros(len(df), dtype=float)

    alpha_1_eff = pd.Series(eff(params, "alpha_1", dgn_values), index=df.index)
    alpha_2_eff = pd.Series(eff(params, "alpha_2", dgn_values), index=df.index)
    alpha_3_eff = pd.Series(eff(params, "alpha_3", dgn_values), index=df.index)
    alpha_4_eff = pd.Series(eff(params, "alpha_4", dgn_values), index=df.index)
    alpha_5_eff = pd.Series(eff(params, "alpha_5", dgn_values), index=df.index)
    alpha_6_eff = pd.Series(eff(params, "alpha_6", dgn_values), index=df.index)
    beta_1_eff = pd.Series(eff(params, "beta_1", dgn_values), index=df.index)
    beta_2_eff = pd.Series(eff(params, "beta_2", dgn_values), index=df.index)
    gamma_eff = pd.Series(eff(params, "gamma", dgn_values), index=df.index)

    for lab in labels:
        logy_raw = df[f"logy_{lab}"]
        logl_raw = df[f"logl_{lab}"]

        if use_star:
            logy_star = logy_raw - (ln_scale_val + C_LOGY)
            logl_star = logl_raw - C_LOGL
            log2y_term = logy_star * logy_star
            log2l_term = logl_star * logl_star
            logyl_term = logy_star * logl_star
            logy_term = logy_star
            logl_term = logl_star
        else:
            log2y_term = df[f"log2y_{lab}"]
            log2l_term = df[f"log2l_{lab}"]
            logyl_term = df[f"logyl_{lab}"]
            logy_term = logy_raw
            logl_term = logl_raw

        base = (
            alpha_1_eff * logy_term
            + alpha_2_eff * logl_term
            + alpha_3_eff * get_series(df, f"Leila_{lab}")
            + alpha_4_eff * get_series(df, f"Leila2_{lab}")
            + alpha_5_eff * get_series(df, f"lochi_{lab}")
            + alpha_6_eff * get_series(df, f"logdc_{lab}")
            + beta_1_eff * log2y_term
            + beta_2_eff * log2l_term
            + gamma_eff * logyl_term
        )
        asc_term = asc_params.get(f"ASC_{lab}", 0.0)
        utils[lab] = base + asc_term
        avail_col = f"avail_{lab}"
        if avail_col in df.columns:
            utils.loc[df[avail_col] == 0, lab] = -np.inf
    return utils


def utility_components_boxcox(
    df: pd.DataFrame,
    labels: Sequence[str],
    params: Mapping[str, float],
    *,
    y_ref: float,
    Z_columns: Mapping[str, np.ndarray],
    T_endow: float = 80.0,
) -> pd.DataFrame:
    utils = pd.DataFrame(index=df.index)
    beta_c = float(params.get("beta_c", 0.0))
    alpha_c = float(params.get("alpha_c", 0.0))
    alpha_l = float(params.get("alpha_l", 0.0))

    beta_l_row = np.full(len(df), float(params.get("beta_l0", 0.0)))
    for key, arr in Z_columns.items():
        beta_l_row += float(params.get(f"delta_{key}", 0.0)) * arr

    for lab in labels:
        asc_val = float(params.get(f"ASC_{lab}", 0.0))
        C_norm = np.clip(
            pd.to_numeric(df[f"consumption_{lab}"], errors="coerce").to_numpy(dtype=float) / y_ref,
            1e-6,
            1.0,
        )
        L_norm = np.clip(
            (T_endow - pd.to_numeric(df[f"lhw_{lab}"], errors="coerce").to_numpy(dtype=float)) / T_endow,
            1e-6,
            1.0,
        )
        utility = asc_val + beta_c * _bc(C_norm, alpha_c) + beta_l_row * _bc(L_norm, alpha_l)
        avail_col = f"avail_{lab}"
        if avail_col in df.columns:
            available = pd.to_numeric(df[avail_col], errors="coerce").fillna(0.0).to_numpy(dtype=float) > 0
            utility = np.where(available, utility, -np.inf)
        utils[lab] = utility
    return utils


def render_boxcox_sections(
    model_dir: Path,
    model_name: str,
    params: Mapping[str, float],
    labels: Tuple[str, ...],
    df_src: pd.DataFrame,
    *,
    y_ref: float | None,
    T_endow: float = 80.0,
) -> Tuple[str, str, Dict[str, float]]:
    consumption_matrix = np.column_stack(
        [pd.to_numeric(df_src[f"consumption_{lab}"], errors="coerce").to_numpy(dtype=float) for lab in labels]
    )
    lhw_matrix = np.column_stack(
        [pd.to_numeric(df_src[f"lhw_{lab}"], errors="coerce").to_numpy(dtype=float) for lab in labels]
    )

    actual_choice = df_src["actual_choice"].astype(str)
    label_to_idx = {lab: idx for idx, lab in enumerate(labels)}
    actual_idx = actual_choice.map(label_to_idx).to_numpy(dtype=int)

    if y_ref is None or not np.isfinite(y_ref) or y_ref <= 0:
        cons_actual = consumption_matrix[np.arange(len(df_src)), actual_idx]
        cons_valid = cons_actual[np.isfinite(cons_actual) & (cons_actual > 0)]
        if cons_valid.size == 0:
            raise ValueError("No valid consumption values to compute y_ref.")
        for q in (0.99, 0.95, 0.90):
            candidate = float(np.quantile(cons_valid, q))
            if np.isfinite(candidate) and candidate > 0:
                y_ref = candidate
                break
        else:
            y_ref = float(np.nanmax(cons_valid))

    y_ref = float(y_ref)

    rows: List[Dict[str, float]] = []
    for lab in labels:
        asc_val = float(params.get(f"ASC_{lab}", 0.0))
        C_med = float(np.nanmedian(pd.to_numeric(df_src[f"consumption_{lab}"], errors="coerce")))
        L_med = float(np.nanmedian(T_endow - pd.to_numeric(df_src[f"lhw_{lab}"], errors="coerce")))
        Cn = float(np.clip(C_med / y_ref, 1e-6, 1.0))
        Ln = float(np.clip(L_med / T_endow, 1e-6, 1.0))

        cons_term = float(params.get("beta_c", 0.0)) * float(_bc(Cn, float(params.get("alpha_c", 0.0))))
        beta_l_med = float(params.get("beta_l0", 0.0))
        for key, value in params.items():
            if str(key).startswith("delta_"):
                name = str(key).replace("delta_", "")
                col = "dgn" if name == "gender" else name
                med_value = float(np.nanmedian(pd.to_numeric(df_src[col], errors="coerce"))) if col in df_src.columns else 0.0
                beta_l_med += float(value) * med_value
        leis_term = beta_l_med * float(_bc(Ln, float(params.get("alpha_l", 0.0))))
        U_total = asc_val + cons_term + leis_term
        rows.append({
            "alt": lab,
            "ASC": asc_val,
            "cons_term": cons_term,
            "leis_term": leis_term,
            "U_total": U_total,
        })

    util_table = pd.DataFrame(rows).set_index("alt")
    if not util_table.empty:
        U_vec = util_table["U_total"].to_numpy(dtype=float)
        util_table["P_at_medians"] = np.exp(U_vec - logsumexp(U_vec))
    util_table.to_csv(model_dir / f"{model_name}_util_decomp.csv", float_format="%.6g")
    utility_html = util_table.to_html(index=True, float_format="%.6g", border=0, classes="table table-sm")

    C_actual = consumption_matrix[np.arange(len(df_src)), actual_idx]
    L_actual = T_endow - lhw_matrix[np.arange(len(df_src)), actual_idx]

    z_base_names = sorted({str(name).replace("delta_", "") for name in params if str(name).startswith("delta_")})
    Z_columns: Dict[str, np.ndarray] = {}
    for z in z_base_names:
        col = "dgn" if z == "gender" else z
        if col in df_src.columns:
            Z_columns[z] = pd.to_numeric(df_src[col], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        else:
            Z_columns[z] = np.zeros(len(df_src), dtype=float)

    muc_list: List[float] = []
    mul_list: List[float] = []
    mrs_list: List[float] = []
    for i in range(len(df_src)):
        Z_i = {name: float(Z_columns[name][i]) for name in Z_columns}
        muc_val = float(muc_boxcox(params, float(C_actual[i]), y_ref))
        mul_val = float(mul_boxcox(params, float(L_actual[i]), Z_i, T_endow=T_endow))
        muc_list.append(muc_val)
        mul_list.append(mul_val)
        mrs_list.append(mul_val / muc_val if muc_val != 0 else np.nan)

    mucmul_df = pd.DataFrame({
        "actual_choice": actual_choice,
        "MUC": muc_list,
        "MUL": mul_list,
        "MRS": mrs_list,
    })
    mucmul_df["MUC_sign"] = np.sign(mucmul_df["MUC"])
    mucmul_df["MUL_sign"] = np.sign(mucmul_df["MUL"])

    mucmul_df.to_csv(model_dir / f"{model_name}_mucmul_draws.csv", index=False, float_format="%.6g")

    share_table = pd.DataFrame({
        "count": [
            int((mucmul_df["MUC"] < 0).sum()),
            int((mucmul_df["MUC"] > 0).sum()),
            int((mucmul_df["MUL"] < 0).sum()),
            int((mucmul_df["MUL"] > 0).sum()),
        ],
        "share": [
            float((mucmul_df["MUC"] < 0).mean()),
            float((mucmul_df["MUC"] > 0).mean()),
            float((mucmul_df["MUL"] < 0).mean()),
            float((mucmul_df["MUL"] > 0).mean()),
        ],
    }, index=["MUC<0", "MUC>0", "MUL<0", "MUL>0"])
    mucmul_html = share_table.to_html(index=True, float_format="%.4f", border=0, classes="table table-sm")

    muc_summary = {
        "share_MUC_actual_neg": float(share_table.loc["MUC<0", "share"]),
        "share_MUL_actual_neg": float(share_table.loc["MUL<0", "share"]),
        "median_consumption_actual": float(np.nanmedian(C_actual)),
        "median_leisure_actual": float(np.nanmedian(L_actual)),
        "MUC_med": float(np.nanmedian(muc_list)),
        "MUL_med": float(np.nanmedian(mul_list)),
        "y_ref": float(y_ref),
        "T": float(T_endow),
    }

    return utility_html, mucmul_html, muc_summary


def plot_marginal_utility(
    x: np.ndarray,
    mu: np.ndarray,
    xlabel: str,
    ylabel: str,
    title: str,
    output_path: Path,
) -> None:
    """Line plot helper for marginal utilities."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, mu, color="#1f77b4", lw=2)
    ax.axhline(0.0, color="black", lw=1, linestyle="--")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _set_smart_yscale(ax, y):
    y = np.asarray(y, float)
    if np.any(y < 0):
        ax.set_yscale("symlog", linthresh=1e-6)
    else:
        positive = y[y > 0]
        ymin = float(np.nanmin(positive)) if positive.size else 1e-12
        ax.set_yscale("log")
        ax.set_ylim(bottom=max(ymin / 10.0, 1e-12))
    return ax


def plot_mu_norm(
    x: np.ndarray,
    mu: np.ndarray,
    xlabel: str,
    ylabel: str,
    title: str,
    output_path: Path,
    marks: list[float] | None = None,
    endpoint: float | None = None,
) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, mu, lw=2)
    ax.axhline(0.0, color="black", lw=1, ls="--", alpha=0.6)
    if marks:
        for m in marks:
            ax.axvline(m, color="black", lw=1, ls=":", alpha=0.5)
    if endpoint is not None:
        ax.axhline(endpoint, color="gray", lw=1, ls="-.", alpha=0.7)
        ax.scatter([1.0], [endpoint], s=20, color="gray")
        ax.text(1.0, endpoint, f"  @1 → {endpoint:.3g}", va="bottom", ha="left", fontsize=8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    _set_smart_yscale(ax, mu)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_indifference_contours_boxcox(
    params: Mapping[str, float],
    beta_l_med: float,
    output_path: Path,
    levels_from_percentiles: tuple[int, ...] = (25, 50, 75, 99),
    grid_points: int = 200,
) -> None:
    import matplotlib.pyplot as plt

    c = np.linspace(1e-3, 1.0, grid_points)
    l = np.linspace(1e-3, 1.0, grid_points)
    C, L = np.meshgrid(c, l)

    alpha_c = float(params.get("alpha_c", 0.0))
    alpha_l = float(params.get("alpha_l", 0.0))
    beta_c = float(params.get("beta_c", 0.0))

    U = beta_c * _bc(C, alpha_c) + beta_l_med * _bc(L, alpha_l)
    finite = np.isfinite(U)
    if not finite.any():
        return
    levels = np.unique(np.percentile(U[finite], list(levels_from_percentiles)))

    fig, ax = plt.subplots(figsize=(6, 5))
    cs = ax.contour(C, L, U, levels=levels)
    ax.clabel(cs, inline=True, fontsize=8)
    ax.set_xlabel("c_norm")
    ax.set_ylabel("l_norm")
    ax.set_title("Utility contours (normalized) at 25/50/75/99th percentiles")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_indifference_contours(
    params: Mapping[str, float],
    logy_med: float,
    logl_med: float,
    output_path: Path,
    *,
    typical_log_age: float | None = None,
    center_logs: bool = False,
    y_scale: float = 1.0,
    C_LOGY: float = 0.0,
    C_LOGL: float = 0.0,
    LN_SCALE: float = 0.0,
    dgn_value: float = 0.0,
) -> None:
    """Plot utility contours around the median log consumption and leisure."""
    ly = np.linspace(logy_med - 1.0, logy_med + 1.0, 80)
    ll = np.linspace(logl_med - 1.0, logl_med + 1.0, 80)
    ly_grid, ll_grid = np.meshgrid(ly, ll)
    alpha_1 = float(eff(params, "alpha_1", dgn_value))
    alpha_2 = float(eff(params, "alpha_2", dgn_value))
    beta_1 = float(eff(params, "beta_1", dgn_value))
    beta_2 = float(eff(params, "beta_2", dgn_value))
    gamma = float(eff(params, "gamma", dgn_value))
    alpha_3 = float(eff(params, "alpha_3", dgn_value))
    alpha_4 = float(eff(params, "alpha_4", dgn_value))

    y_scale_val = float(y_scale)
    ln_scale_val = float(LN_SCALE)
    if np.isclose(ln_scale_val, 0.0) and not np.isclose(y_scale_val, 1.0):
        try:
            ln_scale_val = float(np.log(y_scale_val))
        except Exception:
            ln_scale_val = 0.0
    use_star = bool(center_logs) or not np.isclose(ln_scale_val, 0.0)

    if use_star:
        ly_star = ly_grid - (ln_scale_val + C_LOGY)
        ll_star = ll_grid - C_LOGL
        utility = (
            alpha_1 * ly_star
            + alpha_2 * ll_star
            + beta_1 * ly_star**2
            + beta_2 * ll_star**2
            + gamma * ly_star * ll_star
        )
    else:
        utility = (
            alpha_1 * ly_grid
            + alpha_2 * ll_grid
            + beta_1 * ly_grid**2
            + beta_2 * ll_grid**2
            + gamma * ly_grid * ll_grid
        )

    if typical_log_age is not None and (alpha_3 != 0.0 or alpha_4 != 0.0):
        leila_term = typical_log_age * ll_grid
        utility += alpha_3 * leila_term
        if alpha_4 != 0.0:
            utility += alpha_4 * (leila_term**2)

    fig, ax = plt.subplots(figsize=(6, 5))
    utility_flat = utility.ravel()
    utility_flat = utility_flat[np.isfinite(utility_flat)]
    if utility_flat.size == 0:
        raise ValueError("Utility surface contains no finite values for contour plot.")
    u_min = np.nanmin(utility_flat)
    u_max = np.nanmax(utility_flat)
    if np.isclose(u_min, u_max):
        span = max(abs(u_min), 1.0)
        levels = u_min + span * np.linspace(-1, 1, 5)
    else:
        levels = np.linspace(u_min, u_max, 5)
    levels = np.unique(np.sort(levels))
    if levels.size < 2:
        levels = np.array([u_min, u_min + max(abs(u_min), 1.0)])

    cs = ax.contour(np.exp(ly_grid), np.exp(ll_grid), utility, levels=levels, cmap="viridis")
    ax.clabel(cs, inline=True, fontsize=8)
    ax.set_xlabel("Consumption (y)")
    ax.set_ylabel("Leisure (l)")
    ax.set_title("Utility Contours around Median (log scale +/-1)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def dataframe_to_html(df: pd.DataFrame, caption: str | None = None) -> str:
    """Convert a dataframe to an HTML table with optional caption."""
    html = df.to_html(
        classes="table table-striped",
        float_format="{:,.4f}".format,
        border=0,
        escape=False,
    )
    if caption:
        return f"<figure><figcaption><strong>{caption}</strong></figcaption>{html}</figure>"
    return html


def _tooltip_html(name: str, desc: str | None) -> str:
    safe_name = str(name)
    safe_title = (desc or "").replace('"', "&quot;")
    # dotted underline for discoverability
    return f'<span title="{safe_title}" style="border-bottom:1px dotted #777; cursor:help;">{safe_name}</span>'


def _save_hist(
    series: pd.Series | np.ndarray,
    title: str,
    path: Path,
    *,
    xlabel: str | None = None,
    ylabel: str = "Count",
    color: str = "#1f77b4",
    alpha: float | None = None,
    bins: int = 40,
) -> None:
    """Persist histogram plots if there is data available."""
    clean = pd.Series(series).replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return
    plt.figure(figsize=(4.5, 3.0))
    plt.hist(clean, bins=bins, color=color, edgecolor="white", alpha=alpha if alpha is not None else 1.0)
    plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def build_html_report(
    params_table: pd.DataFrame,
    summary_stats: Mapping[str, object],
    muc_plot: Path,
    mul_plot: Path,
    contour_plot: Path,
    confusion_html: str,
    hit_rates_html: str,
    output_path: Path,
    *,
    cons_hist: Path,
    leisure_hist: Path,
    gender: str,
    variant: str,
    subgroup_accuracy_html: str | None = None,
    subgroup_mu_html: str | None = None,
    subgroup_plots_html: str | None = None,
    utility_table_html: str | None = None,
    mucmul_summary_html: str | None = None,
    title_suffix: str | None = None,
) -> None:
    """Compose and write the HTML report."""
    param_cols = ["Value"]
    if "Value" not in params_table.columns:
        param_cols = params_table.columns.tolist()
    else:
        for extra in ("robust t-test", "t-test", "Std err", "p-value", "StdErr", "RobustSE", "Robust t", "Robust p"):
            if extra in params_table.columns and extra not in param_cols:
                param_cols.append(extra)
    params_html = dataframe_to_html(params_table[param_cols], caption="Estimated Parameters")

    summary_html_rows = "".join(
        f"<tr><th>{key}</th><td>{value}</td></tr>"
        for key, value in summary_stats.items()
    )
    summary_html = f"<table class='table table-sm'>{summary_html_rows}</table>"

    subgroup_accuracy_html = subgroup_accuracy_html or ""
    subgroup_mu_html = subgroup_mu_html or ""
    subgroup_plots_html = subgroup_plots_html or ""
    utility_table_html = utility_table_html or ""
    mucmul_summary_html = mucmul_summary_html or ""
    title_suffix = f" [{title_suffix}]" if title_suffix else ""

    utility_section = (
        f"""
  <section>
    <h2>Utility decomposition (medians)</h2>
    {utility_table_html}
  </section>"""
        if utility_table_html
        else ""
    )
    mucmul_section = (
        f"""
  <section>
    <h2>MUC/MUL summary</h2>
    {mucmul_summary_html}
  </section>"""
        if mucmul_summary_html
        else ""
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Biogeme DCM Diagnostics - {gender.capitalize()} ({variant}){title_suffix}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2em; }}
    h1, h2 {{ color: #333; }}
    .table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5em; }}
    .table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
    .table th {{ background-color: #f8f8f8; text-align: left; }}
    figure {{ margin: 1.5em 0; }}
    figcaption {{ font-weight: bold; margin-bottom: 0.5em; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
    .stats-table {{ width: auto; }}
    .param-name[title] {{ border-bottom: 1px dotted #777; cursor: help; }}
  </style>
</head>
<body>
  <h1>DCM Diagnostics - {gender.capitalize()} ({variant}){title_suffix}</h1>
  <section>
    <h2>Parameter Summary</h2>
    {params_html}
    <p style="color:#555;margin-top:-0.75em;">
      <em>Tip:</em> hover over a parameter name to see a short description.
    </p>
  </section>
  <section>
    <h2>Key Statistics</h2>
    {summary_html}
  </section>{utility_section}{mucmul_section}
  <section>
    <h2>Observed Consumption & Leisure</h2>
    <figure>
      <figcaption>Distribution of consumption at actual choice - {gender.capitalize()} ({variant})</figcaption>
      <img src="{cons_hist.name}" alt="Histogram consumption">
    </figure>
    <figure>
      <figcaption>Distribution of leisure (80 - lhw) at actual choice - {gender.capitalize()} ({variant})</figcaption>
      <img src="{leisure_hist.name}" alt="Histogram leisure">
    </figure>
  </section>
  <section>
    <h2>Marginal Utilities</h2>
    <figure>
      <figcaption>MUC as a function of consumption (median leisure) - {variant}</figcaption>
      <img src="{muc_plot.name}" alt="MUC plot">
    </figure>
    <figure>
      <figcaption>MUL as a function of leisure (median consumption) - {variant}</figcaption>
      <img src="{mul_plot.name}" alt="MUL plot">
    </figure>
  </section>
  <section>
    <h2>Indifference Curves</h2>
    <figure>
      <figcaption>Utility contours around median log-consumption and log-leisure - {variant}</figcaption>
      <img src="{contour_plot.name}" alt="Utility contour plot">
    </figure>
  </section>
  <section>
    <h2>Predictive Accuracy</h2>
    {confusion_html}
    {hit_rates_html}
  </section>
  {subgroup_accuracy_html}
  {subgroup_mu_html}
  {subgroup_plots_html}
</body>
</html>
"""
    output_path = _unique_path(output_path)
    output_path.write_text(html, encoding="utf-8")
    LOGGER.info("Analyzer report written to %s", output_path)
    return output_path


def _process_gender_boxcox(
    gender: str,
    variant: str,
    param_csv: Path,
    out_dir: Path,
    source: str,
    meta: Mapping[str, object],
    *,
    annotate_biogeme_html_flag: bool = False,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{source}:{gender}/{variant}"

    params_table, params_dict, asc_params = load_parameters(param_csv)
    base_name = param_csv.stem.replace("_parameters", "")
    model_dir = param_csv.parent

    labels_map_path = param_csv.with_name(f"{base_name}_param_labels.json")
    desc_map_path = param_csv.with_name(f"{base_name}_param_descriptions.json")
    LABEL_MAP = _load_json_if_exists(labels_map_path)
    DESC_MAP = _load_json_if_exists(desc_map_path)
    READABLE_TO_RAW = {str(v): str(k) for k, v in (LABEL_MAP or {}).items()}

    pretty_index: list[str] = []
    for raw_like in params_table.index:
        raw_key = READABLE_TO_RAW.get(str(raw_like), str(raw_like))
        pretty = (LABEL_MAP or {}).get(raw_key, str(raw_like))
        tip = (DESC_MAP or {}).get(raw_key)
        pretty_index.append(_tooltip_html(pretty, tip))
    params_table = params_table.copy()
    params_table.index = pretty_index

    params_for_calc: dict[str, float] = {}
    for k, v in params_dict.items():
        raw_k = READABLE_TO_RAW.get(str(k), str(k))
        params_for_calc[raw_k] = float(v)

    y_ref = float(meta.get("y_ref", np.nan)) if meta else np.nan
    T_ENDOW = float(meta.get("T", 80.0)) if meta else 80.0

    df = load_dataset_for_gender(gender)
    df = df.replace("", np.nan).infer_objects(copy=False)

    if "dgn" in df.columns:
        df["dgn"] = pd.to_numeric(df["dgn"], errors="coerce").fillna(0.0).clip(0.0, 1.0)
    else:
        df["dgn"] = 0.0

    labels = detect_labels(df)
    ensure_columns(df, ["actual_choice"])

    actual_choice_series = df["actual_choice"].astype(str)
    label_to_idx = {lab: idx for idx, lab in enumerate(labels)}
    actual_idx = actual_choice_series.map(label_to_idx).to_numpy(dtype=int)

    cons_hist = out_dir / f"{base_name}_cons_hist.png"
    leisure_hist = out_dir / f"{base_name}_leisure_hist.png"
    logy_actual, logl_actual = compute_actual_logs(df, labels)
    y_actual = np.exp(logy_actual).clip(lower=1e-3)
    l_actual = np.exp(logl_actual).clip(lower=1e-3, upper=T_ENDOW)
    _save_hist(
        y_actual,
        f"Distribution of consumption at actual choice - {gender.capitalize()} ({variant})",
        cons_hist,
        xlabel="consumption",
        alpha=0.7,
    )
    _save_hist(
        l_actual,
        f"Distribution of leisure (80 - lhw) at actual choice - {gender.capitalize()} ({variant})",
        leisure_hist,
        xlabel="leisure hours",
        alpha=0.7,
    )

    util_html, mucmul_html, muc_summary = render_boxcox_sections(
        model_dir,
        base_name,
        params_for_calc,
        labels,
        df,
        y_ref=y_ref,
        T_endow=T_ENDOW,
    )

    # === Normalized MU/Contours (Box–Cox) ===
    lab2idx = {lab: i for i, lab in enumerate(labels)}
    act_idx = actual_choice_series.map(lab2idx).to_numpy(int)

    T_ENDOW = float(meta.get("T", T_ENDOW)) if (meta and "T" in meta) else T_ENDOW
    y_ref = float(meta.get("y_ref", np.nan)) if meta else float("nan")

    C_mat = np.column_stack(
        [pd.to_numeric(df[f"consumption_{lab}"], errors="coerce").to_numpy(float) for lab in labels]
    )
    L_mat = np.column_stack(
        [pd.to_numeric(df[f"lhw_{lab}"], errors="coerce").to_numpy(float) for lab in labels]
    )

    if not np.isfinite(y_ref) or y_ref <= 0:
        cons_actual = C_mat[np.arange(len(df)), act_idx]
        cons_actual = cons_actual[np.isfinite(cons_actual) & (cons_actual > 0)]
        y_ref = float(np.quantile(cons_actual, 0.99)) if cons_actual.size else 1.0

    Z_stats = (meta or {}).get("Z_medians_or_modes", {}) or {}
    c_norm_med = (meta or {}).get("c_norm_median")
    l_norm_med = (meta or {}).get("l_norm_median")

    if (c_norm_med is None) or (l_norm_med is None) or (not Z_stats):
        C_act_recompute = C_mat[np.arange(len(df)), act_idx]
        L_act_recompute = T_ENDOW - L_mat[np.arange(len(df)), act_idx]
        c_norm_med = float(np.nanmedian(np.clip(C_act_recompute / y_ref, 1e-12, 1.0)))
        l_norm_med = float(np.nanmedian(np.clip(L_act_recompute / T_ENDOW, 1e-12, 1.0)))

        def _is_binary01(a: np.ndarray) -> bool:
            finite = a[np.isfinite(a)]
            if finite.size == 0:
                return False
            u = np.unique(np.round(finite, 6))
            return len(u) <= 2 and set(u).issubset({0.0, 1.0})

        Z_stats = {}
        for col in ("age_norm", "age2_norm", "child_norm", "dch", "dgn"):
            if col in df.columns:
                arr = pd.to_numeric(df[col], errors="coerce").to_numpy(float)
                key = "gender" if col == "dgn" else col
                if _is_binary01(arr):
                    finite = arr[np.isfinite(arr)]
                    if finite.size:
                        vals, cnt = np.unique(finite, return_counts=True)
                        Z_stats[key] = float(vals[np.argmax(cnt)])
                    else:
                        Z_stats[key] = 0.0
                else:
                    Z_stats[key] = float(np.nanmedian(arr))

    beta_l_med = float(params_for_calc.get("beta_l0", 0.0))
    for k, zval in Z_stats.items():
        dname = "delta_gender" if k == "gender" else f"delta_{k}"
        if dname in params_for_calc:
            beta_l_med += float(params_for_calc[dname]) * float(zval)

    alpha_c = float(params_for_calc.get("alpha_c", 0.0))
    alpha_l = float(params_for_calc.get("alpha_l", 0.0))
    beta_c = float(params_for_calc.get("beta_c", 0.0))

    C_act = C_mat[np.arange(len(df)), act_idx]
    L_act = T_ENDOW - L_mat[np.arange(len(df)), act_idx]
    C_norm_act = np.clip(C_act / y_ref, 1e-12, 1.0)
    L_norm_act = np.clip(L_act / T_ENDOW, 1e-12, 1.0)

    c_lo = float(np.nanpercentile(C_norm_act, 1)) if np.isfinite(np.nanpercentile(C_norm_act, 1)) else 1e-3
    l_lo = float(np.nanpercentile(L_norm_act, 1)) if np.isfinite(np.nanpercentile(L_norm_act, 1)) else 1e-3
    c_lo = max(1e-3, min(c_lo, 0.99))
    l_lo = max(1e-3, min(l_lo, 0.99))

    c_grid = np.linspace(c_lo, 1.0, 400)
    l_grid = np.linspace(l_lo, 1.0, 400)
    muc_curve = beta_c * np.power(c_grid, alpha_c - 1.0)
    mul_curve = beta_l_med * np.power(l_grid, alpha_l - 1.0)

    c_marks = [float(np.nanpercentile(C_norm_act, q)) for q in (25, 50, 75, 99)]
    l_marks = [float(np.nanpercentile(L_norm_act, q)) for q in (25, 50, 75, 99)]
    muc_at_1 = beta_c
    mul_at_1 = beta_l_med

    muc_norm_png = out_dir / f"{base_name}_muc_norm.png"
    mul_norm_png = out_dir / f"{base_name}_mul_norm.png"
    ctr_norm_png = out_dir / f"{base_name}_contours_norm.png"

    plot_mu_norm(
        c_grid,
        muc_curve,
        "c_norm",
        "MUC (normalized)",
        f"MUC vs c_norm - {gender.capitalize()} ({variant})",
        muc_norm_png,
        marks=c_marks,
        endpoint=muc_at_1,
    )
    plot_mu_norm(
        l_grid,
        mul_curve,
        "l_norm",
        "MUL (normalized)",
        f"MUL vs l_norm - {gender.capitalize()} ({variant})",
        mul_norm_png,
        marks=l_marks,
        endpoint=mul_at_1,
    )
    plot_indifference_contours_boxcox(params_for_calc, beta_l_med, ctr_norm_png, (25, 50, 75, 99))

    y_ref = float(y_ref)

    Z_columns = {}
    for key in sorted({str(name).replace("delta_", "") for name in params_for_calc if str(name).startswith("delta_")}):
        col = "dgn" if key == "gender" else key
        if col in df.columns:
            Z_columns[key] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        else:
            Z_columns[key] = np.zeros(len(df), dtype=float)

    utils_df = utility_components_boxcox(
        df,
        labels,
        params_for_calc,
        y_ref=y_ref,
        Z_columns=Z_columns,
        T_endow=T_ENDOW,
    )
    predicted_choice = utils_df.idxmax(axis=1)
    df_pred = pd.DataFrame({"actual_choice": df["actual_choice"], "predicted_choice": predicted_choice})
    df_pred["correct"] = (df_pred["actual_choice"] == df_pred["predicted_choice"]).astype(int)

    cm = pd.crosstab(
        df_pred["actual_choice"],
        df_pred["predicted_choice"],
        margins=True,
        margins_name="Total",
    )
    accuracy = float(df_pred["correct"].mean()) if len(df_pred) else float("nan")
    hit_rates = (
        df_pred["correct"].groupby(df_pred["actual_choice"]).mean().rename("Hit rate")
        if len(df_pred)
        else pd.Series(dtype=float)
    )

    confusion_html = dataframe_to_html(cm, caption="Confusion Matrix (Actual vs Predicted)")
    hit_rates_html = dataframe_to_html(hit_rates.to_frame(), caption="Hit Rates by Actual Scenario")

    muc_negative_share = float(muc_summary.get("share_MUC_actual_neg", 0.0))
    mul_negative_share = float(muc_summary.get("share_MUL_actual_neg", 0.0))

    summary_stats = {
        "Total observations": f"{len(df):,}",
        "MUC < 0": f"{int(muc_negative_share * len(df)):,} ({muc_negative_share:.2%})",
        "MUL < 0": f"{int(mul_negative_share * len(df)):,} ({mul_negative_share:.2%})",
        "MUC zero crossing y": "n/a",
        "MUL zero crossing l": "n/a",
        "Overall accuracy": f"{accuracy:.2%}",
    }

    # Use normalized MU/contour assets in the report
    report_path = out_dir / f"{base_name}_analysis.html"
    build_html_report(
        params_table=params_table,
        summary_stats=summary_stats,
        muc_plot=muc_norm_png,
        mul_plot=mul_norm_png,
        contour_plot=ctr_norm_png,
        confusion_html=confusion_html,
        hit_rates_html=hit_rates_html,
        output_path=report_path,
        cons_hist=cons_hist,
        leisure_hist=leisure_hist,
        gender=gender,
        variant=variant,
        utility_table_html=util_html,
        mucmul_summary_html=mucmul_html,
        title_suffix="Box-Cox (normalized MUs)",
    )

    if annotate_biogeme_html_flag and LABEL_MAP:
        for html_path in out_dir.glob("*.html"):
            try:
                annotate_biogeme_html(html_path, LABEL_MAP, DESC_MAP)
            except Exception:
                continue

    return {
        "gender": gender,
        "variant": variant,
        "source": source,
        "spec": "boxcox",
        "accuracy": float(accuracy),
        "muc_share": float(muc_negative_share),
        "mul_share": float(mul_negative_share),
    }


def _process_gender_translog(
    gender: str,
    variant: str,
    param_csv: Path,
    out_dir: Path,
    source: str,
    *,
    annotate_biogeme_html_flag: bool = False,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{source}:{gender}/{variant}"

    params_table, params_dict, asc_params = load_parameters(param_csv)

    base_name = param_csv.stem.replace("_parameters", "")

    # Load label and description maps (best-effort)
    labels_map_path = param_csv.with_name(f"{base_name}_param_labels.json")
    desc_map_path = param_csv.with_name(f"{base_name}_param_descriptions.json")
    LABEL_MAP = _load_json_if_exists(labels_map_path)
    DESC_MAP = _load_json_if_exists(desc_map_path)
    READABLE_TO_RAW = {str(v): str(k) for k, v in (LABEL_MAP or {}).items()}

    meta_path = out_dir / f"{base_name}_transform_meta.json"
    meta = _load_json_if_exists(meta_path)
    center_logs_flag = bool(meta.get("center_logs", False))
    y_scale_value = float(meta.get("y_scale", 1.0) or 1.0)
    C_LOGY = float(meta.get("C_LOGY", 0.0))
    C_LOGL = float(meta.get("C_LOGL", 0.0))
    LN_SCALE = float(meta.get("LN_SCALE", 0.0))

    # Wrap parameter names with tooltips for display in the HTML table
    pretty_index: list[str] = []
    for raw_like in params_table.index:
        raw_key = READABLE_TO_RAW.get(str(raw_like), str(raw_like))
        pretty = (LABEL_MAP or {}).get(raw_key, str(raw_like))
        tip = (DESC_MAP or {}).get(raw_key)
        pretty_index.append(_tooltip_html(pretty, tip))
    params_table = params_table.copy()
    params_table.index = pretty_index

    # Map names back to raw keys for numerical computations
    params_for_calc: dict[str, float] = {}
    for k, v in params_dict.items():
        raw_k = READABLE_TO_RAW.get(str(k), str(k))
        params_for_calc[raw_k] = float(v)

    df = load_dataset_for_gender(gender)
    df = df.replace("", np.nan).infer_objects(copy=False)

    default_dgn = 1.0 if gender == "male" else 0.0
    if "dgn" in df.columns:
        dgn_series = pd.to_numeric(df["dgn"], errors="coerce").fillna(default_dgn)
    else:
        dgn_series = pd.Series(default_dgn, index=df.index)
        df["dgn"] = dgn_series
    if gender == "pooled":
        # ensure clean binary indicator (1=male, 0=female)
        dgn_series = np.where(np.isclose(dgn_series, 1.0), 1.0, np.where(np.isclose(dgn_series, 0.0), 0.0, dgn_series))
        dgn_series = pd.Series(dgn_series, index=df.index)
    df["dgn"] = pd.to_numeric(dgn_series, errors="coerce").fillna(default_dgn).astype(float)
    dgn_series = df["dgn"]

    labels = detect_labels(df)
    df = harmonize_quadratic_columns(df, labels)
    ensure_columns(df, ["actual_choice"])

    logy_actual, logl_actual = compute_actual_logs(df, labels)
    y_actual = np.exp(logy_actual).clip(lower=1e-3)
    l_actual = np.exp(logl_actual).clip(lower=1e-3, upper=168)

    cons_hist = out_dir / f"{base_name}_cons_hist.png"
    leisure_hist = out_dir / f"{base_name}_leisure_hist.png"
    _save_hist(
        y_actual,
        f"Distribution of consumption at actual choice - {gender.capitalize()} ({variant})",
        cons_hist,
        xlabel="consumption",
        alpha=0.7,
    )
    _save_hist(
        l_actual,
        f"Distribution of leisure (80 - lhw) at actual choice - {gender.capitalize()} ({variant})",
        leisure_hist,
        xlabel="leisure hours",
        alpha=0.7,
    )

    leila_actual = pd.Series(0.0, index=df.index)
    for lab in labels:
        col = f"Leila_{lab}"
        if col in df.columns:
            mask = df["actual_choice"] == lab
            leila_actual.loc[mask] = df.loc[mask, col]

    lochi_actual = pd.Series(0.0, index=df.index)
    logdc_actual = pd.Series(0.0, index=df.index)
    for lab in labels:
        col_lochi = f"lochi_{lab}"
        col_logdc = f"logdc_{lab}"
        mask = df["actual_choice"] == lab
        if col_lochi in df.columns:
            lochi_actual.loc[mask] = df.loc[mask, col_lochi]
        if col_logdc in df.columns:
            logdc_actual.loc[mask] = df.loc[mask, col_logdc]

    with np.errstate(divide="ignore", invalid="ignore"):
        children_actual = pd.Series(
            np.where(np.abs(logl_actual) > 1e-12, lochi_actual / logl_actual, 0.0),
            index=df.index,
        ).fillna(0.0)
        dch_actual = pd.Series(
            np.where(np.abs(logl_actual) > 1e-12, logdc_actual / logl_actual, 0.0),
            index=df.index,
        ).fillna(0.0)

    children_median = float(np.nanmedian(children_actual)) if len(children_actual) else 0.0
    dch_median = float(np.nanmedian(dch_actual)) if len(dch_actual) else 0.0

    muc_series = muc(
        logy_actual,
        logl_actual,
        y_actual,
        params_for_calc,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn=dgn_series,
    )
    mul_no_leila = mul(
        logy_actual,
        logl_actual,
        l_actual,
        params_for_calc,
        children=children_actual,
        dch=dch_actual,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn=dgn_series,
    )
    mul_with_leila = mul(
        logy_actual,
        logl_actual,
        l_actual,
        params_for_calc,
        leila=leila_actual,
        children=children_actual,
        dch=dch_actual,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn=dgn_series,
    )
    share_no = float((mul_no_leila < 0).mean())
    share_with = float((mul_with_leila < 0).mean())
    print(f"[{tag}] Share MUL<0 without Leila: {share_no:.2%}")
    print(f"[{tag}] Share MUL<0 with Leila: {share_with:.2%}")
    mul_series = mul_with_leila
    if share_with >= 0.99 and share_no < share_with:
        mul_series = mul_no_leila
        print(f"[{gender}/{variant}] Selected MUL without Leila for downstream diagnostics.")

    df = df.assign(MUC=muc_series, MUL=mul_series)
    if (df["MUL"] < 0).all():
        print(f"[{tag}] WARNING: All MUL values are negative - check coefficients or Leila sign.")

    neg_muc_count = int((df["MUC"] < 0).sum())
    neg_mul_count = int((df["MUL"] < 0).sum())
    total_obs = len(df)
    muc_negative_share = neg_muc_count / total_obs if total_obs else np.nan
    mul_negative_share = neg_mul_count / total_obs if total_obs else np.nan

    logy_med = logy_actual.median()
    logl_med = logl_actual.median()
    dgn_mean = float(np.nanmean(dgn_series)) if len(dgn_series) else 0.0
    y_zero = solve_zero_muc(
        logl_med,
        params_for_calc,
        guess=logy_med,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn_val=dgn_mean,
    )
    l_zero = solve_zero_mul(
        logy_med,
        params_for_calc,
        guess=logl_med,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn_val=dgn_mean,
    )

    print(f"\n[{tag}] === Marginal Utility Diagnostics ===")
    print(f"[{tag}] Observations: {total_obs:,}")
    print(f"[{tag}] MUC < 0: {neg_muc_count:,} ({muc_negative_share:.2%})")
    print(f"[{tag}] MUL < 0: {neg_mul_count:,} ({mul_negative_share:.2%})")
    print(f"[{tag}] MUC zero at y ~ {y_zero:,.2f} (holding logl at median)")
    print(f"[{tag}] MUL zero at l ~ {l_zero:,.2f} (holding log y at median)")

    y_valid = y_actual.dropna()
    if y_valid.empty:
        raise ValueError("No valid consumption values to evaluate MUC curves.")
    desired_min_consumption = 100.0
    y_min = max(float(y_valid.min()), desired_min_consumption, 1e-3)
    raw_max = float(y_valid.max())
    if raw_max < y_min:
        y_max = max(y_min * 1.01, y_min + 1e-3)
    else:
        y_max = max(raw_max, y_min * 1.001 if y_min > 0 else y_min + 1e-3)
    if np.isclose(y_min, y_max):
        y_max = y_min * 1.01 if y_min > 0 else y_min + 1e-3
    y_range = np.linspace(y_min, y_max, 200)
    logy_range = np.log(y_range)
    muc_curve = muc(
        logy_range,
        np.full_like(logy_range, logl_med),
        y_range,
        params_for_calc,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn=np.full_like(logy_range, dgn_mean),
    )

    l_valid = l_actual.dropna()
    if l_valid.empty:
        raise ValueError("No valid leisure values to evaluate MUL curves.")
    l_min = max(float(l_valid.min()), 1e-3)
    l_max = max(float(l_valid.max()), l_min * 1.001 if l_min > 0 else l_min + 1e-3)
    if np.isclose(l_min, l_max):
        l_max = l_min * 1.01 if l_min > 0 else l_min + 1e-3
    l_range = np.linspace(l_min, l_max, 200)
    logl_range = np.log(l_range)
    mul_curve = mul(
        np.full_like(logl_range, logy_med),
        logl_range,
        l_range,
        params_for_calc,
        children=np.full_like(logl_range, children_median),
        dch=np.full_like(logl_range, dch_median),
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn=np.full_like(logl_range, dgn_mean),
    )

    muc_plot = out_dir / f"{base_name}_muc.png"
    mul_plot = out_dir / f"{base_name}_mul.png"
    contour_plot = out_dir / f"{base_name}_contours.png"
    muc_hist = out_dir / f"{base_name}_muc_hist.png"
    mul_hist = out_dir / f"{base_name}_mul_hist.png"

    plot_marginal_utility(
        y_range,
        muc_curve,
        xlabel="Consumption (y)",
        ylabel="MUC",
        title=f"Marginal Utility of Consumption - {gender.capitalize()} ({variant})",
        output_path=muc_plot,
    )
    plot_marginal_utility(
        l_range,
        mul_curve,
        xlabel="Leisure (l)",
        ylabel="MUL",
        title=f"Marginal Utility of Leisure - {gender.capitalize()} ({variant})",
        output_path=mul_plot,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        log_age_series = np.where(np.abs(logl_actual) > 1e-12, leila_actual / logl_actual, np.nan)
    typical_log_age = float(np.nanmedian(log_age_series))
    if not np.isfinite(typical_log_age):
        typical_log_age = None
    plot_indifference_contours(
        params=params_for_calc,
        logy_med=logy_med,
        logl_med=logl_med,
        output_path=contour_plot,
        typical_log_age=typical_log_age,
        center_logs=center_logs_flag,
        y_scale=y_scale_value,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
        dgn_value=dgn_mean,
    )

    _save_hist(
        df["MUC"],
        f"Distribution of MUC - {gender.capitalize()} ({variant})",
        muc_hist,
    )
    _save_hist(
        df["MUL"],
        f"Distribution of MUL - {gender.capitalize()} ({variant})",
        mul_hist,
    )

    utils_df = utility_components(
        df,
        labels,
        params_for_calc,
        asc_params,
        center_logs=center_logs_flag,
        y_scale=y_scale_value,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
        LN_SCALE=LN_SCALE,
    )
    predicted_choice = utils_df.idxmax(axis=1)
    df_pred = pd.DataFrame({"actual_choice": df["actual_choice"], "predicted_choice": predicted_choice})
    df_pred["correct"] = (df_pred["actual_choice"] == df_pred["predicted_choice"]).astype(int)

    cm = pd.crosstab(
        df_pred["actual_choice"],
        df_pred["predicted_choice"],
        margins=True,
        margins_name="Total",
    )
    accuracy = df_pred["correct"].mean() if len(df_pred) else np.nan
    hit_rates = (
        df_pred["correct"].groupby(df_pred["actual_choice"]).mean().rename("Hit rate")
        if len(df_pred)
        else pd.Series(dtype=float)
    )

    print(f"\n[{tag}] === Predictive Accuracy ===")
    print(cm)
    print(f"[{tag}] Overall accuracy: {accuracy:.2%}")
    if not hit_rates.empty:
        print(f"[{tag}] Hit rates by actual scenario:")
        for label, rate in hit_rates.items():
            print(f"  {label}: {rate:.2%}")

    confusion_html = dataframe_to_html(cm, caption="Confusion Matrix (Actual vs Predicted)")
    hit_rates_html = dataframe_to_html(hit_rates.to_frame(), caption="Hit Rates by Actual Scenario")

    subgroup_accuracy_section: str | None = None
    subgroup_mu_section: str | None = None
    subgroup_plot_sections: list[str] = []
    unique_dgn = df["dgn"].dropna().unique()
    if gender == "pooled" or unique_dgn.size > 1:
        subgroup_rows_acc: list[dict[str, str]] = []
        subgroup_rows_mu: list[dict[str, str]] = []
        subgroup_map = [(0.0, "Female"), (1.0, "Male")]
        for code, label_name in subgroup_map:
            mask = np.isclose(df["dgn"].to_numpy(dtype=float), code)
            if not mask.any():
                continue
            idx = df.index[mask]
            subset_df = df.loc[idx]
            subset_pred = df_pred.loc[idx]
            obs = len(subset_df)
            acc_val = subset_pred["correct"].mean() if obs else float("nan")
            hits = (
                subset_pred["correct"].groupby(subset_pred["actual_choice"]).mean()
                if obs
                else pd.Series(dtype=float)
            )
            acc_row: dict[str, str] = {
                "Group": label_name,
                "Observations": f"{obs:,}",
                "Accuracy": f"{acc_val:.2%}" if obs else "n/a",
            }
            for lab in labels:
                hit_val = hits.get(lab)
                acc_row[f"Hit {lab}"] = f"{hit_val:.2%}" if pd.notna(hit_val) else "n/a"
            subgroup_rows_acc.append(acc_row)

            muc_share_sub = subset_df["MUC"].lt(0).mean()
            mul_share_sub = subset_df["MUL"].lt(0).mean()
            logy_med_sub = float(logy_actual.loc[idx].median())
            logl_med_sub = float(logl_actual.loc[idx].median())
            y_zero_sub = solve_zero_muc(
                logl_med_sub,
                params_for_calc,
                guess=logy_med_sub,
                C_LOGY=C_LOGY,
                C_LOGL=C_LOGL,
                LN_SCALE=LN_SCALE,
                dgn_val=code,
            )
            l_zero_sub = solve_zero_mul(
                logy_med_sub,
                params_for_calc,
                guess=logl_med_sub,
                C_LOGY=C_LOGY,
                C_LOGL=C_LOGL,
                LN_SCALE=LN_SCALE,
                dgn_val=code,
            )
            mu_row = {
                "Group": label_name,
                "Observations": f"{obs:,}",
                "MUC < 0": f"{muc_share_sub:.2%}" if obs else "n/a",
                "MUL < 0": f"{mul_share_sub:.2%}" if obs else "n/a",
                "MUC zero y": f"{y_zero_sub:,.2f}" if np.isfinite(y_zero_sub) else "n/a",
                "MUL zero l": f"{l_zero_sub:,.2f}" if np.isfinite(l_zero_sub) else "n/a",
            }
            subgroup_rows_mu.append(mu_row)

            # Gender-specific marginal utility plots
            y_vals_sub = y_actual.loc[idx].dropna()
            l_vals_sub = l_actual.loc[idx].dropna()
            if obs and y_vals_sub.size and l_vals_sub.size:
                logy_med_sub = float(logy_actual.loc[idx].median())
                logl_med_sub = float(logl_actual.loc[idx].median())
                children_sub = children_actual.loc[idx]
                dch_sub = dch_actual.loc[idx]
                children_med_sub = float(np.nanmedian(children_sub)) if len(children_sub) else 0.0
                dch_med_sub = float(np.nanmedian(dch_sub)) if len(dch_sub) else 0.0
                if np.isfinite(logy_med_sub) and np.isfinite(logl_med_sub):
                    y_min_sub = max(float(y_vals_sub.min()), 1e-3)
                    y_max_sub = max(float(y_vals_sub.max()), y_min_sub * 1.001 if y_min_sub > 0 else y_min_sub + 1e-3)
                    if np.isclose(y_min_sub, y_max_sub):
                        y_max_sub = y_min_sub * 1.01 if y_min_sub > 0 else y_min_sub + 1e-3
                    y_range_sub = np.linspace(y_min_sub, y_max_sub, 200)
                    logy_range_sub = np.log(y_range_sub)
                    muc_curve_sub = muc(
                        logy_range_sub,
                        np.full_like(logy_range_sub, logl_med_sub),
                        y_range_sub,
                        params_for_calc,
                        C_LOGY=C_LOGY,
                        C_LOGL=C_LOGL,
                        LN_SCALE=LN_SCALE,
                        children=np.full_like(logy_range_sub, children_med_sub),
                        dch=np.full_like(logy_range_sub, dch_med_sub),
                        dgn=np.full_like(logy_range_sub, code),
                    )

                    l_min_sub = max(float(l_vals_sub.min()), 1e-3)
                    l_max_sub = max(float(l_vals_sub.max()), l_min_sub * 1.001 if l_min_sub > 0 else l_min_sub + 1e-3)
                    if np.isclose(l_min_sub, l_max_sub):
                        l_max_sub = l_min_sub * 1.01 if l_min_sub > 0 else l_min_sub + 1e-3
                    l_range_sub = np.linspace(l_min_sub, l_max_sub, 200)
                    logl_range_sub = np.log(l_range_sub)
                    mul_curve_sub = mul(
                        np.full_like(logl_range_sub, logy_med_sub),
                        logl_range_sub,
                        l_range_sub,
                        params_for_calc,
                        C_LOGY=C_LOGY,
                        C_LOGL=C_LOGL,
                        LN_SCALE=LN_SCALE,
                        children=np.full_like(logl_range_sub, children_med_sub),
                        dch=np.full_like(logl_range_sub, dch_med_sub),
                        dgn=np.full_like(logl_range_sub, code),
                    )

                    muc_plot_sub = out_dir / f"{base_name}_muc_{label_name.lower()}.png"
                    mul_plot_sub = out_dir / f"{base_name}_mul_{label_name.lower()}.png"

                    plot_marginal_utility(
                        y_range_sub,
                        muc_curve_sub,
                        xlabel="Consumption (y)",
                        ylabel="MUC",
                        title=f"MUC - {label_name} ({variant})",
                        output_path=muc_plot_sub,
                    )
                    plot_marginal_utility(
                        l_range_sub,
                        mul_curve_sub,
                        xlabel="Leisure (l)",
                        ylabel="MUL",
                        title=f"MUL - {label_name} ({variant})",
                        output_path=mul_plot_sub,
                    )

                    subgroup_plot_sections.append(
                        f"""
  <section>
    <h2>{label_name} Marginal Utilities</h2>
    <figure>
      <figcaption>MUC - {label_name} ({variant})</figcaption>
      <img src="{muc_plot_sub.name}" alt="MUC {label_name}">
    </figure>
    <figure>
      <figcaption>MUL - {label_name} ({variant})</figcaption>
      <img src="{mul_plot_sub.name}" alt="MUL {label_name}">
    </figure>
  </section>
"""
                    )

        if subgroup_rows_acc:
            acc_df = pd.DataFrame(subgroup_rows_acc).set_index("Group")
            subgroup_accuracy_section = (
                "<section><h2>By-gender Accuracy &amp; Hit Rates</h2>"
                f"{dataframe_to_html(acc_df, caption=None)}</section>"
            )
        if subgroup_rows_mu:
            mu_df = pd.DataFrame(subgroup_rows_mu).set_index("Group")
            subgroup_mu_section = (
                "<section><h2>By-gender MU Diagnostics</h2>"
                f"{dataframe_to_html(mu_df, caption=None)}</section>"
            )

    subgroup_plots_html = "".join(subgroup_plot_sections) if subgroup_plot_sections else None

    summary_stats = {
        "Total observations": f"{total_obs:,}",
        "MUC < 0": f"{neg_muc_count:,} ({muc_negative_share:.2%})",
        "MUL < 0": f"{neg_mul_count:,} ({mul_negative_share:.2%})",
        "MUC zero crossing y": f"{y_zero:,.2f}",
        "MUL zero crossing l": f"{l_zero:,.2f}",
        "Overall accuracy": f"{accuracy:.2%}",
    }

    report_path = out_dir / f"{base_name}_analysis.html"
    build_html_report(
        params_table=params_table,
        summary_stats=summary_stats,
        muc_plot=muc_plot,
        mul_plot=mul_plot,
        contour_plot=contour_plot,
        confusion_html=confusion_html,
        hit_rates_html=hit_rates_html,
        output_path=report_path,
        cons_hist=cons_hist,
        leisure_hist=leisure_hist,
        gender=gender,
        variant=variant,
        subgroup_accuracy_html=subgroup_accuracy_section,
        subgroup_mu_html=subgroup_mu_section,
        subgroup_plots_html=subgroup_plots_html,
    )

    print(f"[{tag}] HTML report saved to: {report_path}")

    # Optional: annotate Biogeme HTML table with tooltips
    if annotate_biogeme_html_flag and LABEL_MAP:
        try:
            for html_path in out_dir.glob("dcm_*.html"):
                annotate_biogeme_html(html_path, LABEL_MAP, DESC_MAP)
        except Exception:
            pass

    return {
        "gender": gender,
        "variant": variant,
        "source": source,
        "accuracy": float(accuracy),
        "muc_share": float((df["MUC"] < 0).mean()),
        "mul_share": float((df["MUL"] < 0).mean()),
    }


def process_gender(
    gender: str,
    variant: str,
    param_csv: Path,
    out_dir: Path,
    source: str,
    *,
    annotate_biogeme_html_flag: bool = False,
) -> dict[str, object]:
    base_name = param_csv.stem.replace("_parameters", "")
    meta_path = param_csv.parent / f"{base_name}_meta.json"
    meta = _load_json_if_exists(meta_path)
    spec = str(meta.get("spec", "translog")).lower() if meta else "translog"
    if spec == "translog":
        path_text = f"{param_csv.parent.as_posix()}/{param_csv.stem}".lower()
        if "boxcox" in path_text:
            spec = "boxcox"
    if spec == "boxcox":
        return _process_gender_boxcox(
            gender,
            variant,
            param_csv,
            out_dir,
            source,
            meta,
            annotate_biogeme_html_flag=annotate_biogeme_html_flag,
        )
    return _process_gender_translog(
        gender,
        variant,
        param_csv,
        out_dir,
        source,
        annotate_biogeme_html_flag=annotate_biogeme_html_flag,
    )


def main() -> None:
    args = parse_args()
    summary: list[dict[str, object]] = []
    for gender in args.genders:
        try:
            variant, param_csv = resolve_variant(gender, args.variant, args.source)
            out_dir = param_dir_for(gender, variant, args.source)
            metrics = process_gender(
                gender,
                variant,
                param_csv,
                out_dir,
                args.source,
                annotate_biogeme_html_flag=args.annotate_biogeme_html,
            )
            summary.append(metrics)
        except Exception as exc:
            print(f"[{gender}] Analysis failed: {exc}")

    if summary:
        print("=== Comparative Summary ===")
        for m in summary:
            print(
                f"{m['source']:<7} {m['gender']:<6} {m['variant']:<12} accuracy={m['accuracy']:.2%}  "
                f"MUC<0={m['muc_share']:.2%}  MUL<0={m['mul_share']:.2%}"
            )


if __name__ == "__main__":
    main()
