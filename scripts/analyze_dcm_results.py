#!/usr/bin/env python
"""
Post-estimation diagnostics for the Biogeme DCM translog utility model.

This script reads the estimated parameters and corresponding wide-format dataset
for a selected gender, computes marginal utilities, produces diagnostics plots,
evaluates predictive accuracy, and exports an HTML report consolidating the
findings together with the generated figures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

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

# Resolve project root even if the script resides in ``scripts/``.
_SCRIPT_DIR = Path(__file__).resolve().parent
_CANDIDATE_ROOTS = (
    _SCRIPT_DIR,
    _SCRIPT_DIR.parent,
    _SCRIPT_DIR.parent.parent,
)
for _candidate in _CANDIDATE_ROOTS:
    if (_candidate / "Data" / "processed" / "scenarios").exists():
        ROOT = _candidate
        break
else:
    ROOT = _SCRIPT_DIR

DATA_DIR = ROOT / "Data" / "processed" / "scenarios"
REPORT_DIR = ROOT / "reports" / "biogeme"

GENDER = "male"  # Set to "female" to analyse female heads instead
LABELS: tuple[str, ...] = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")

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


def muc(logy: pd.Series, logl: pd.Series, y: pd.Series, params: Mapping[str, float]) -> pd.Series:
    """Marginal utility of consumption."""
    alpha_1 = params.get("alpha_1", 0.0)
    beta_1 = params.get("beta_1", 0.0)
    gamma = params.get("gamma", 0.0)
    numerator = alpha_1 + 2.0 * beta_1 * logy + gamma * logl
    return numerator / y


def mul(
    logy: pd.Series,
    logl: pd.Series,
    l: pd.Series,
    params: Mapping[str, float],
    leila: pd.Series | None = None,
) -> pd.Series:
    """Marginal utility of leisure, including Leila = log(l)*log(age) when available."""
    a2, b2, g, a3 = (
        params.get("alpha_2", 0.0),
        params.get("beta_2", 0.0),
        params.get("gamma", 0.0),
        params.get("alpha_3", 0.0),
    )
    base = (a2 + 2 * b2 * logl + g * logy) / l
    if leila is not None and a3 != 0.0:
        log_age = np.where(np.abs(logl) > 1e-12, leila / logl, 0.0)
        base = base + (a3 * log_age) / l
    return pd.Series(base, index=logl.index)


def solve_zero_muc(logl_value: float, params: Mapping[str, float], guess: float) -> float:
    """Solve for the consumption level where MUC crosses zero (holding logℓ fixed)."""
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
    ax.set_ylabel("Leisure (ℓ)")
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


def build_html_report(
    params_table: pd.DataFrame,
    summary_stats: Mapping[str, object],
    muc_plot: Path,
    mul_plot: Path,
    contour_plot: Path,
    confusion_html: str,
    hit_rates_html: str,
    output_path: Path,
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
  <title>Biogeme DCM Diagnostics</title>
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
  <h1>DCM Diagnostics – {GENDER.capitalize()}</h1>
  <section>
    <h2>Parameter Summary</h2>
    {params_html}
  </section>
  <section>
    <h2>Key Statistics</h2>
    {summary_html}
  </section>
  <section>
    <h2>Marginal Utilities</h2>
    <figure>
      <figcaption>MUC as a function of consumption (median leisure)</figcaption>
      <img src="{muc_plot.name}" alt="MUC plot">
    </figure>
    <figure>
      <figcaption>MUL as a function of leisure (median consumption)</figcaption>
      <img src="{mul_plot.name}" alt="MUL plot">
    </figure>
  </section>
  <section>
    <h2>Indifference Curves</h2>
    <figure>
      <figcaption>Utility contours around median log-consumption and log-leisure</figcaption>
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


def main() -> None:
    report_gender_dir = REPORT_DIR / GENDER
    report_gender_dir.mkdir(parents=True, exist_ok=True)

    params_path = report_gender_dir / f"dcm_{GENDER}_parameters.csv"
    params_table, params_dict, asc_params = load_parameters(params_path)

    dataset_path = DATA_DIR / f"heads_wide_single_{GENDER}_dcm.parquet"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Missing wide dataset: {dataset_path}")
    df = pd.read_parquet(dataset_path)
    df = df.replace("", np.nan).infer_objects(copy=False)

    detected_labels = detect_labels(df)
    if set(LABELS).issubset(detected_labels):
        labels = LABELS
    else:
        labels = detected_labels
    df = harmonize_quadratic_columns(df, labels)
    ensure_columns(df, ["actual_choice"])

    logy_actual, logl_actual = compute_actual_logs(df, labels)
    y_actual = np.exp(logy_actual)
    l_actual = np.exp(logl_actual)

    leila_actual = pd.Series(0.0, index=df.index)
    for lab in labels:
        leila_col = f"Leila_{lab}"
        if leila_col in df.columns:
            mask = df["actual_choice"] == lab
            leila_actual.loc[mask] = df.loc[mask, leila_col]

    muc_series = muc(logy_actual, logl_actual, y_actual, params_dict)
    mul_series = mul(logy_actual, logl_actual, l_actual, params_dict, leila=leila_actual)

    df = df.assign(MUC=muc_series, MUL=mul_series)

    neg_muc_count = int((df["MUC"] < 0).sum())
    neg_mul_count = int((df["MUL"] < 0).sum())
    total_obs = len(df)
    muc_negative_share = neg_muc_count / total_obs if total_obs else np.nan
    mul_negative_share = neg_mul_count / total_obs if total_obs else np.nan

    logy_med = df[f"logy_{labels[0]}"].median()
    logl_med = df[f"logl_{labels[0]}"].median()
    y_zero = solve_zero_muc(logl_med, params_dict, guess=logy_med)
    l_zero = solve_zero_mul(logy_med, params_dict, guess=logl_med)

    print("=== Marginal Utility Diagnostics ===")
    print(f"Observations: {total_obs:,}")
    print(f"MUC < 0: {neg_muc_count:,} ({muc_negative_share:.2%})")
    print(f"MUL < 0: {neg_mul_count:,} ({mul_negative_share:.2%})")
    print(f"MUC zero at y ≈ {y_zero:,.2f} (holding logℓ at median)")
    print(f"MUL zero at ℓ ≈ {l_zero:,.2f} (holding log y at median)")

    y_range = np.linspace(np.exp(logy_med - 1.0), np.exp(logy_med + 1.0), 200)
    logy_range = np.log(y_range)
    muc_curve = muc(logy_range, np.full_like(logy_range, logl_med), y_range, params_dict)

    l_range = np.linspace(np.exp(logl_med - 1.0), np.exp(logl_med + 1.0), 200)
    logl_range = np.log(l_range)
    mul_curve = mul(np.full_like(logl_range, logy_med), logl_range, l_range, params_dict)

    muc_plot_path = report_gender_dir / f"dcm_{GENDER}_muc.png"
    mul_plot_path = report_gender_dir / f"dcm_{GENDER}_mul.png"
    contour_plot_path = report_gender_dir / f"dcm_{GENDER}_contours.png"

    plot_marginal_utility(
        y_range,
        muc_curve,
        xlabel="Consumption (y)",
        ylabel="MUC",
        title="Marginal Utility of Consumption",
        output_path=muc_plot_path,
    )
    plot_marginal_utility(
        l_range,
        mul_curve,
        xlabel="Leisure (ℓ)",
        ylabel="MUL",
        title="Marginal Utility of Leisure",
        output_path=mul_plot_path,
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        log_age_series = np.where(
            np.abs(logl_actual) > 1e-12, leila_actual / logl_actual, np.nan
        )
    typical_log_age = float(np.nanmedian(log_age_series))

    plot_indifference_contours(
        params=params_dict,
        logy_med=logy_med,
        logl_med=logl_med,
        output_path=contour_plot_path,
        typical_log_age=typical_log_age,
    )

    utils_df = utility_components(df, labels, params_dict, asc_params)
    predicted_choice = utils_df.idxmax(axis=1)
    df_pred = pd.DataFrame(
        {
            "actual_choice": df["actual_choice"],
            "predicted_choice": predicted_choice,
        }
    )
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

    print("\n=== Predictive Accuracy ===")
    print(cm)
    print(f"Overall accuracy: {accuracy:.2%}")
    if not hit_rates.empty:
        print("Hit rates by actual scenario:")
        for label, rate in hit_rates.items():
            print(f"  {label}: {rate:.2%}")

    confusion_html = dataframe_to_html(cm, caption="Confusion Matrix (Actual vs Predicted)")
    hit_rates_html = dataframe_to_html(hit_rates.to_frame(), caption="Hit Rates by Actual Scenario")

    summary_stats = {
        "Total observations": f"{total_obs:,}",
        "MUC < 0": f"{neg_muc_count:,} ({muc_negative_share:.2%})",
        "MUL < 0": f"{neg_mul_count:,} ({mul_negative_share:.2%})",
        "MUC zero crossing y": f"{y_zero:,.2f}",
        "MUL zero crossing ℓ": f"{l_zero:,.2f}",
        "Overall accuracy": f"{accuracy:.2%}",
    }

    report_path = report_gender_dir / f"dcm_{GENDER}_analysis.html"
    build_html_report(
        params_table=params_table,
        summary_stats=summary_stats,
        muc_plot=muc_plot_path,
        mul_plot=mul_plot_path,
        contour_plot=contour_plot_path,
        confusion_html=confusion_html,
        hit_rates_html=hit_rates_html,
        output_path=report_path,
    )

    print(f"\nHTML report saved to: {report_path}")


if __name__ == "__main__":
    main()
