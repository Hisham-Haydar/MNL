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
from pathlib import Path
import re
from typing import Iterable, Mapping

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


def param_dir_for(gender: str, variant: str, source: str) -> Path:
    return _report_base_dir(source) / f"{gender}_{variant}"


def param_csv_for(gender: str, variant: str, source: str) -> Path:
    prefix = "dcm" if source == "biogeme" else "mle"
    return param_dir_for(gender, variant, source) / f"{prefix}_{gender}_{variant}_parameters.csv"


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
    file_prefix = "dcm" if source == "biogeme" else "mle"
    for folder in base_dir.glob(f"{gender}_*"):
        if not folder.is_dir():
            continue
        name = folder.name
        if not name.startswith(prefix):
            continue
        variant = name[len(prefix) :]
        csv_path = folder / f"{file_prefix}_{gender}_{variant}_parameters.csv"
        if not csv_path.exists():
            continue
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
    ax.set_title("Utility Contours around Median (log scale ±1)")
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
    logy_hist: Path,
    logl_hist: Path,
    gender: str,
    variant: str,
    subgroup_accuracy_html: str | None = None,
    subgroup_mu_html: str | None = None,
    subgroup_plots_html: str | None = None,
) -> None:
    """Compose and write the HTML report."""
    param_cols = ["Value"]
    if "Value" not in params_table.columns:
        param_cols = params_table.columns.tolist()
    else:
        for extra in ("robust t-test", "t-test", "Std err", "p-value"):
            if extra in params_table.columns:
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

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Biogeme DCM Diagnostics - {gender.capitalize()} ({variant})</title>
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
  <h1>DCM Diagnostics - {gender.capitalize()} ({variant})</h1>
  <section>
    <h2>Parameter Summary</h2>
    {params_html}
    <p style="color:#555;margin-top:-0.75em;">
      <em>Tip:</em> hover over a parameter name to see a short description (e.g.,
      <span title="Curvature of leisure: coefficient on (log l)^2." style="border-bottom:1px dotted #777;cursor:help;">beta_log2_leisure</span>
      = curvature of leisure term).
    </p>
  </section>
  <section>
    <h2>Key Statistics</h2>
    {summary_html}
  </section>
  <section>
    <h2>Observed log-level Distributions</h2>
    <figure>
      <figcaption>Distribution of log(y) at actual choice - {gender.capitalize()} ({variant})</figcaption>
      <img src="{logy_hist.name}" alt="Histogram log(y)">
    </figure>
    <figure>
      <figcaption>Distribution of log(l) at actual choice - {gender.capitalize()} ({variant})</figcaption>
      <img src="{logl_hist.name}" alt="Histogram log(l)">
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
    output_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def process_gender(
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

    logy_hist = out_dir / f"{base_name}_logy_hist.png"
    logl_hist = out_dir / f"{base_name}_logl_hist.png"
    _save_hist(
      logy_actual,
      f"Distribution of log(y) at actual choice - {gender.capitalize()} ({variant})",
      logy_hist,
      xlabel="log(y)",
      alpha=0.7,
  )
    _save_hist(
      logl_actual,
      f"Distribution of log(l) at actual choice - {gender.capitalize()} ({variant})",
      logl_hist,
      xlabel="log(l)",
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
        logy_hist=logy_hist,
        logl_hist=logl_hist,
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
