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
REPORT_DIR = reports_root() / "biogeme"

LABELS: tuple[str, ...] = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")


# ---------------------------------------------------------------------------
# CLI / Variant helpers
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Biogeme DCM results (ASC-aware).")
    parser.add_argument(
        "--genders",
        nargs="+",
        default=["male", "female"],
        choices=["male", "female"],
        help="Which genders to analyze.",
    )
    parser.add_argument(
        "--variant",
        default="auto",
        choices=["ascsON", "ascsOFF", "auto"],
        help="Which parameter variant to analyze (default: auto).",
    )
    return parser.parse_args()


def param_dir_for(gender: str, variant: str) -> Path:
    return REPORT_DIR / f"{gender}_{variant}"


def param_csv_for(gender: str, variant: str) -> Path:
    return param_dir_for(gender, variant) / f"dcm_{gender}_{variant}_parameters.csv"


def resolve_variant(gender: str, requested: str) -> tuple[str, Path]:
    if requested in ("ascsON", "ascsOFF"):
        return requested, param_csv_for(gender, requested)

    on_csv = param_csv_for(gender, "ascsON")
    off_csv = param_csv_for(gender, "ascsOFF")
    if on_csv.exists():
        return "ascsON", on_csv
    if off_csv.exists():
        return "ascsOFF", off_csv
    legacy = REPORT_DIR / gender / f"dcm_{gender}_parameters.csv"
    if legacy.exists():
        return "ascsOFF", legacy
    raise FileNotFoundError(
        f"No parameter file for {gender}. Looked in {on_csv}, {off_csv}, {legacy}"
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


def compute_actual_logs(df: pd.DataFrame, labels: Iterable[str]) -> tuple[pd.Series, pd.Series]:
    """Extract log-consumption and log-leisure for each observation's actual choice."""
    logy_actual = pd.Series(0.0, index=df.index)
    logl_actual = pd.Series(0.0, index=df.index)
    actual_choice = df["actual_choice"]
    for lab in labels:
        mask = actual_choice == lab
        if not mask.any():
            continue
        logy_actual.loc[mask] = df.loc[mask, f"logy_{lab}"]
        logl_actual.loc[mask] = df.loc[mask, f"logl_{lab}"]
    return logy_actual, logl_actual


def muc(logy: pd.Series, logl: pd.Series, y: pd.Series, params: Mapping[str, float]) -> pd.Series | np.ndarray:
    """Marginal utility of consumption."""
    alpha_1 = params.get("alpha_1", 0.0)
    beta_1 = params.get("beta_1", 0.0)
    gamma = params.get("gamma", 0.0)

    logy_arr = np.asarray(logy)
    logl_arr = np.asarray(logl)
    y_arr = np.clip(np.asarray(y), 1e-3, None)

    numerator = alpha_1 + 2.0 * beta_1 * logy_arr + gamma * logl_arr
    result = numerator / y_arr
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
) -> pd.Series | np.ndarray:
    """Marginal utility of leisure, including Leila = log(l)*log(age) when available."""
    a2, b2, g, a3 = (
        params.get("alpha_2", 0.0),
        params.get("beta_2", 0.0),
        params.get("gamma", 0.0),
        params.get("alpha_3", 0.0),
    )
    logy_arr = np.asarray(logy)
    logl_arr = np.asarray(logl)
    l_arr = np.clip(np.asarray(l), 1e-3, 168.0)

    numerator = a2 + 2 * b2 * logl_arr + g * logy_arr
    if leila is not None and a3 != 0.0:
        leila_arr = np.asarray(leila)
        log_age = np.where(np.abs(logl_arr) > 1e-12, leila_arr / logl_arr, 0.0)
        numerator = numerator + a3 * log_age

    finite_num = numerator[np.isfinite(numerator)]
    if finite_num.size:
        print(f"MUL range (raw numerator): {np.nanmin(finite_num):.3f} -> {np.nanmax(finite_num):.3f}")

    result = numerator / l_arr

    if isinstance(logl, pd.Series):
        return pd.Series(result, index=logl.index)
    return result


def solve_zero_muc(logl_value: float, params: Mapping[str, float], guess: float) -> float:
    """Solve for the consumption level where MUC crosses zero (holding logl fixed)."""
    gamma = params.get("gamma", 0.0)
    alpha_1 = params.get("alpha_1", 0.0)
    beta_1 = params.get("beta_1", 0.0)

    def equation(logy: float) -> float:
        return alpha_1 + 2.0 * beta_1 * logy + gamma * logl_value

    try:
        logy_root = fsolve(equation, x0=guess, xtol=1e-10, maxfev=200)[0]
    except Exception:
        logy_root = guess
    return float(np.exp(logy_root))


def solve_zero_mul(logy_value: float, params: Mapping[str, float], guess: float) -> float:
    """Solve for the leisure level where MUL crosses zero (holding log y fixed)."""
    gamma = params.get("gamma", 0.0)
    alpha_2 = params.get("alpha_2", 0.0)
    beta_2 = params.get("beta_2", 0.0)

    def equation(logl: float) -> float:
        return alpha_2 + 2.0 * beta_2 * logl + gamma * logy_value

    try:
        logl_root = fsolve(equation, x0=guess, xtol=1e-10, maxfev=200)[0]
    except Exception:
        logl_root = guess
    return float(np.exp(logl_root))


def utility_components(
    df: pd.DataFrame,
    labels: Iterable[str],
    params: Mapping[str, float],
    asc_params: Mapping[str, float],
) -> pd.DataFrame:
    """Compute scenario utilities for each observation."""
    coeff = params
    utils = pd.DataFrame(index=df.index)
    for lab in labels:
        base = (
            coeff.get("alpha_1", 0.0) * df[f"logy_{lab}"]
            + coeff.get("alpha_2", 0.0) * df[f"logl_{lab}"]
            + coeff.get("alpha_3", 0.0) * get_series(df, f"Leila_{lab}")
            + coeff.get("alpha_4", 0.0) * get_series(df, f"Leila2_{lab}")
            + coeff.get("alpha_5", 0.0) * get_series(df, f"lochi_{lab}")
            + coeff.get("alpha_6", 0.0) * get_series(df, f"logdc_{lab}")
            + coeff.get("beta_1", 0.0) * df[f"log2y_{lab}"]
            + coeff.get("beta_2", 0.0) * df[f"log2l_{lab}"]
            + coeff.get("gamma", 0.0) * df[f"logyl_{lab}"]
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
) -> None:
    """Plot utility contours around the median log consumption and leisure."""
    ly = np.linspace(logy_med - 1.0, logy_med + 1.0, 80)
    ll = np.linspace(logl_med - 1.0, logl_med + 1.0, 80)
    ly_grid, ll_grid = np.meshgrid(ly, ll)
    alpha_1 = params.get("alpha_1", 0.0)
    alpha_2 = params.get("alpha_2", 0.0)
    beta_1 = params.get("beta_1", 0.0)
    beta_2 = params.get("beta_2", 0.0)
    gamma = params.get("gamma", 0.0)

    utility = (
        alpha_1 * ly_grid
        + alpha_2 * ll_grid
        + beta_1 * ly_grid**2
        + beta_2 * ll_grid**2
        + gamma * ly_grid * ll_grid
    )

    if typical_log_age is not None and params.get("alpha_3", 0.0) != 0.0:
        utility += params["alpha_3"] * typical_log_age * ll_grid

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
    html = df.to_html(classes="table table-striped", float_format="{:,.4f}".format, border=0)
    if caption:
        return f"<figure><figcaption><strong>{caption}</strong></figcaption>{html}</figure>"
    return html


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
  </style>
</head>
<body>
  <h1>DCM Diagnostics - {gender.capitalize()} ({variant})</h1>
  <section>
    <h2>Parameter Summary</h2>
    {params_html}
  </section>
  <section>
    <h2>Key Statistics</h2>
    {summary_html}
  </section>
  <section>
    <h2>Observed log-level Distributions</h2>
    <figure>
      <figcaption>Distribution of log(y) - {gender.capitalize()} ({variant})</figcaption>
      <img src="{logy_hist.name}" alt="Histogram log(y)">
    </figure>
    <figure>
      <figcaption>Distribution of log(l) - {gender.capitalize()} ({variant})</figcaption>
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
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def process_gender(gender: str, variant: str, param_csv: Path, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    params_table, params_dict, asc_params = load_parameters(param_csv)

    dataset_path = DATA_DIR / f"heads_wide_single_{gender}_dcm.parquet"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Missing wide dataset: {dataset_path}")

    df = pd.read_parquet(dataset_path)
    df = df.replace("", np.nan).infer_objects(copy=False)

    labels = detect_labels(df)
    df = harmonize_quadratic_columns(df, labels)
    ensure_columns(df, ["actual_choice"])

    logy_actual, logl_actual = compute_actual_logs(df, labels)
    y_actual = np.exp(logy_actual).clip(lower=1e-3)
    l_actual = np.exp(logl_actual).clip(lower=1e-3, upper=168)

    logy_hist = out_dir / f"dcm_{gender}_{variant}_logy_hist.png"
    logl_hist = out_dir / f"dcm_{gender}_{variant}_logl_hist.png"
    _save_hist(
        logy_actual,
        f"Distribution of log(y) - {gender.capitalize()} ({variant})",
        logy_hist,
        xlabel="log(y)",
        alpha=0.7,
    )
    _save_hist(
        logl_actual,
        f"Distribution of log(l) - {gender.capitalize()} ({variant})",
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

    muc_series = muc(logy_actual, logl_actual, y_actual, params_dict)
    mul_no_leila = mul(logy_actual, logl_actual, l_actual, params_dict)
    mul_with_leila = mul(logy_actual, logl_actual, l_actual, params_dict, leila=leila_actual)
    share_no = float((mul_no_leila < 0).mean())
    share_with = float((mul_with_leila < 0).mean())
    print(f"[{gender}/{variant}] Share MUL<0 without Leila: {share_no:.2%}")
    print(f"[{gender}/{variant}] Share MUL<0 with Leila: {share_with:.2%}")
    mul_series = mul_with_leila
    if share_with >= 0.99 and share_no < share_with:
        mul_series = mul_no_leila
        print(f"[{gender}/{variant}] Selected MUL without Leila for downstream diagnostics.")

    df = df.assign(MUC=muc_series, MUL=mul_series)
    if (df["MUL"] < 0).all():
        print(f"[{gender}/{variant}] WARNING: All MUL values are negative - check coefficients or Leila sign.")

    neg_muc_count = int((df["MUC"] < 0).sum())
    neg_mul_count = int((df["MUL"] < 0).sum())
    total_obs = len(df)
    muc_negative_share = neg_muc_count / total_obs if total_obs else np.nan
    mul_negative_share = neg_mul_count / total_obs if total_obs else np.nan

    logy_med = logy_actual.median()
    logl_med = logl_actual.median()
    y_zero = solve_zero_muc(logl_med, params_dict, guess=logy_med)
    l_zero = solve_zero_mul(logy_med, params_dict, guess=logl_med)

    print(f"\n[{gender}/{variant}] === Marginal Utility Diagnostics ===")
    print(f"[{gender}/{variant}] Observations: {total_obs:,}")
    print(f"[{gender}/{variant}] MUC < 0: {neg_muc_count:,} ({muc_negative_share:.2%})")
    print(f"[{gender}/{variant}] MUL < 0: {neg_mul_count:,} ({mul_negative_share:.2%})")
    print(f"[{gender}/{variant}] MUC zero at y ~ {y_zero:,.2f} (holding logl at median)")
    print(f"[{gender}/{variant}] MUL zero at l ~ {l_zero:,.2f} (holding log y at median)")

    y_valid = y_actual.dropna()
    if y_valid.empty:
        raise ValueError("No valid consumption values to evaluate MUC curves.")
    y_min = max(float(y_valid.min()), 1e-3)
    y_max = max(float(y_valid.max()), y_min * 1.001 if y_min > 0 else y_min + 1e-3)
    if np.isclose(y_min, y_max):
        y_max = y_min * 1.01 if y_min > 0 else y_min + 1e-3
    y_range = np.linspace(y_min, y_max, 200)
    logy_range = np.log(y_range)
    muc_curve = muc(logy_range, np.full_like(logy_range, logl_med), y_range, params_dict)

    l_valid = l_actual.dropna()
    if l_valid.empty:
        raise ValueError("No valid leisure values to evaluate MUL curves.")
    l_min = max(float(l_valid.min()), 1e-3)
    l_max = max(float(l_valid.max()), l_min * 1.001 if l_min > 0 else l_min + 1e-3)
    if np.isclose(l_min, l_max):
        l_max = l_min * 1.01 if l_min > 0 else l_min + 1e-3
    l_range = np.linspace(l_min, l_max, 200)
    logl_range = np.log(l_range)
    mul_curve = mul(np.full_like(logl_range, logy_med), logl_range, l_range, params_dict)

    muc_plot = out_dir / f"dcm_{gender}_{variant}_muc.png"
    mul_plot = out_dir / f"dcm_{gender}_{variant}_mul.png"
    contour_plot = out_dir / f"dcm_{gender}_{variant}_contours.png"
    muc_hist = out_dir / f"dcm_{gender}_{variant}_muc_hist.png"
    mul_hist = out_dir / f"dcm_{gender}_{variant}_mul_hist.png"

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
        params=params_dict,
        logy_med=logy_med,
        logl_med=logl_med,
        output_path=contour_plot,
        typical_log_age=typical_log_age,
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

    utils_df = utility_components(df, labels, params_dict, asc_params)
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

    print(f"\n[{gender}/{variant}] === Predictive Accuracy ===")
    print(cm)
    print(f"[{gender}/{variant}] Overall accuracy: {accuracy:.2%}")
    if not hit_rates.empty:
        print(f"[{gender}/{variant}] Hit rates by actual scenario:")
        for label, rate in hit_rates.items():
            print(f"  {label}: {rate:.2%}")

    confusion_html = dataframe_to_html(cm, caption="Confusion Matrix (Actual vs Predicted)")
    hit_rates_html = dataframe_to_html(hit_rates.to_frame(), caption="Hit Rates by Actual Scenario")

    summary_stats = {
        "Total observations": f"{total_obs:,}",
        "MUC < 0": f"{neg_muc_count:,} ({muc_negative_share:.2%})",
        "MUL < 0": f"{neg_mul_count:,} ({mul_negative_share:.2%})",
        "MUC zero crossing y": f"{y_zero:,.2f}",
        "MUL zero crossing l": f"{l_zero:,.2f}",
        "Overall accuracy": f"{accuracy:.2%}",
    }

    report_path = out_dir / f"dcm_{gender}_{variant}_analysis.html"
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
    )

    print(f"[{gender}/{variant}] HTML report saved to: {report_path}")

    return {
        "gender": gender,
        "variant": variant,
        "accuracy": float(accuracy),
        "muc_share": float((df["MUC"] < 0).mean()),
        "mul_share": float((df["MUL"] < 0).mean()),
    }


def main() -> None:
    args = parse_args()
    summary: list[dict[str, float]] = []
    for gender in args.genders:
        try:
            variant, param_csv = resolve_variant(gender, args.variant)
            out_dir = param_dir_for(gender, variant)
            metrics = process_gender(gender, variant, param_csv, out_dir)
            summary.append(metrics)
        except Exception as exc:
            print(f"[{gender}] Analysis failed: {exc}")

    if summary:
        print("=== Comparative Summary ===")
        for m in summary:
            print(
                f"{m['gender']:<6} {m['variant']:<7} accuracy={m['accuracy']:.2%}  "
                f"MUC<0={m['muc_share']:.2%}  MUL<0={m['mul_share']:.2%}"
            )


if __name__ == "__main__":
    main()
