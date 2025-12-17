#!/usr/bin/env python
"""
Analyzer for the pooled gender-split Box-Cox specification.

This script reuses the rich diagnostics pipeline from analyze_dcm_results.py
to generate the full HTML/PNG/JSON assets for the pooled run written by
scripts/DCM1_boxcox_gender_split.py.
"""

from __future__ import annotations

import argparse
import logging
from collections import OrderedDict
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from analyze_dcm_results import (
    process_gender,
    set_data_dir,
    load_parameters,
    _load_json_if_exists,
    load_dataset_for_gender,
    detect_labels,
    ensure_columns,
    plot_mu_norm,
    plot_indifference_contours_boxcox,
)
from path_helpers import reports_root

DEFAULT_BASE = reports_root() / "mle_dcm" / "boxcox"
MODEL_PREFIX = "boxcox_pooled_genderSplit"


def reparam_gender_split_boxcox(params: dict) -> dict:
    """
    Given a parameter dict from the pooled gender-split Box-Cox estimation,
    construct a baseline + male-deviation representation:

        alpha_c(g) = alpha_c + alpha_c_m * dgn
        alpha_l(g) = alpha_l + alpha_l_m * dgn
        beta_c(g)  = beta_c  + beta_c_m  * dgn
        beta_l0(g) = beta_l0 + beta_l0_m * dgn
        delta_z(g) = delta_z + delta_z_m * dgn

    where dgn = 1 for male, 0 for female.

    We take the female parameters as the baseline:
        alpha_c   := alpha_c_f
        alpha_c_m := alpha_c_m - alpha_c_f
    etc.
    """
    out: dict[str, float] = {}

    # Curvature
    if "alpha_c_f" in params and "alpha_c_m" in params:
        alpha_c_f = float(params["alpha_c_f"])
        alpha_c_m = float(params["alpha_c_m"])
        out["alpha_c"] = alpha_c_f
        out["alpha_c_m"] = alpha_c_m - alpha_c_f

    if "alpha_l_f" in params and "alpha_l_m" in params:
        alpha_l_f = float(params["alpha_l_f"])
        alpha_l_m = float(params["alpha_l_m"])
        out["alpha_l"] = alpha_l_f
        out["alpha_l_m"] = alpha_l_m - alpha_l_f

    # Consumption scale
    if "beta_c_f" in params and "beta_c_m" in params:
        beta_c_f = float(params["beta_c_f"])
        beta_c_m = float(params["beta_c_m"])
        out["beta_c"] = beta_c_f
        out["beta_c_m"] = beta_c_m - beta_c_f

    # Leisure intercept
    if "beta_l0_f" in params and "beta_l0_m" in params:
        beta_l0_f = float(params["beta_l0_f"])
        beta_l0_m = float(params["beta_l0_m"])
        out["beta_l0"] = beta_l0_f
        out["beta_l0_m"] = beta_l0_m - beta_l0_f

    # Leisure shifters (age_norm, age2_norm, child_norm, dch, etc.)
    for base in ("age_norm", "age2_norm", "child_norm", "dch"):
        f_name = f"delta_{base}_f"
        m_name = f"delta_{base}_m"
        if f_name in params and m_name in params:
            delta_f = float(params[f_name])
            delta_m = float(params[m_name])
            out[f"delta_{base}"] = delta_f
            out[f"delta_{base}_m"] = delta_m - delta_f

    return out


def compute_Z_medians_gender(df_src: pd.DataFrame, z_cols: list[str], gender_col: str = "dgn"):
    """
    Compute medians of Z shifters for:
      - pooled sample,
      - females (dgn == 0),
      - males   (dgn == 1).
    Returns three dicts: Z_pooled, Z_f, Z_m.
    """
    Z_pooled: dict[str, float] = {}
    Z_f: dict[str, float] = {}
    Z_m: dict[str, float] = {}

    def _median(series: pd.Series) -> float:
        return float(np.nanmedian(pd.to_numeric(series, errors="coerce")))

    mask_f = df_src[gender_col] == 0
    mask_m = df_src[gender_col] == 1

    for col in z_cols:
        if col not in df_src.columns:
            continue
        s = df_src[col]
        Z_pooled[col] = _median(s)
        Z_f[col] = _median(s[mask_f])
        Z_m[col] = _median(s[mask_m])

    return Z_pooled, Z_f, Z_m


def build_boxcox_mu_and_contours_gender_split(
    params: dict,
    meta: dict,
    Z_pooled: dict,
    Z_f: dict,
    Z_m: dict,
    grid_points: int = 400,
):
    """
    Construct c,l grids and MUC/MUL curves for:
      - general (baseline, evaluated at pooled Z medians),
      - female (female-specific params, Z_f),
      - male   (male-specific params, Z_m),

    plus a utility grid U(c,l) for each of the three.
    """
    y_ref = float(meta.get("y_ref", 1.0))
    if not np.isfinite(y_ref) or y_ref <= 0:
        y_ref = 1.0
    T_ENDOW = float(meta.get("T", 80.0))

    c_grid = np.linspace(1e-6, 1.0, grid_points)
    l_grid = np.linspace(1e-6, 1.0, grid_points)
    C, L = np.meshgrid(c_grid, l_grid)

    alpha_c_f = float(params.get("alpha_c_f", 0.0))
    alpha_l_f = float(params.get("alpha_l_f", 0.0))
    beta_c_f = float(params.get("beta_c_f", 0.0))
    beta_l0_f = float(params.get("beta_l0_f", 0.0))

    alpha_c_m = float(params.get("alpha_c_m", alpha_c_f))
    alpha_l_m = float(params.get("alpha_l_m", alpha_l_f))
    beta_c_m = float(params.get("beta_c_m", beta_c_f))
    beta_l0_m = float(params.get("beta_l0_m", beta_l0_f))

    def beta_l_from_Z(prefix: str, Z: dict) -> float:
        if prefix == "f":
            beta = beta_l0_f
        else:
            beta = beta_l0_m
        for base in ("age_norm", "age2_norm", "child_norm", "dch"):
            zval = float(Z.get(base, 0.0))
            key = f"delta_{base}_{prefix}"
            if key in params:
                beta += float(params[key]) * zval
        return beta

    beta_l_f = beta_l_from_Z("f", Z_f)
    beta_l_m = beta_l_from_Z("m", Z_m)

    reparam = reparam_gender_split_boxcox(params)
    alpha_c_gen = float(reparam.get("alpha_c", alpha_c_f))
    alpha_l_gen = float(reparam.get("alpha_l", alpha_l_f))
    beta_c_gen = float(reparam.get("beta_c", beta_c_f))
    beta_l_gen = float(reparam.get("beta_l0", beta_l0_f))
    for base in ("age_norm", "age2_norm", "child_norm", "dch"):
        key = f"delta_{base}"
        if key in reparam:
            beta_l_gen += float(reparam[key]) * float(Z_pooled.get(base, 0.0))

    def _bc(x, a):
        x = np.clip(np.asarray(x, float), 1e-6, None)
        if abs(a) < 1e-8:
            return np.log(x)
        return (np.power(x, a) - 1.0) / a

    muc_gen = beta_c_gen * np.power(c_grid, alpha_c_gen - 1.0)
    mul_gen = beta_l_gen * np.power(l_grid, alpha_l_gen - 1.0)
    muc_f = beta_c_f * np.power(c_grid, alpha_c_f - 1.0)
    mul_f = beta_l_f * np.power(l_grid, alpha_l_f - 1.0)
    muc_m = beta_c_m * np.power(c_grid, alpha_c_m - 1.0)
    mul_m = beta_l_m * np.power(l_grid, alpha_l_m - 1.0)

    U_gen = beta_c_gen * _bc(C, alpha_c_gen) + beta_l_gen * _bc(L, alpha_l_gen)
    U_f = beta_c_f * _bc(C, alpha_c_f) + beta_l_f * _bc(L, alpha_l_f)
    U_m = beta_c_m * _bc(C, alpha_c_m) + beta_l_m * _bc(L, alpha_l_m)

    return {
        "c_grid": c_grid,
        "l_grid": l_grid,
        "U_gen": U_gen,
        "U_f": U_f,
        "U_m": U_m,
        "muc_gen": muc_gen,
        "mul_gen": mul_gen,
        "muc_f": muc_f,
        "mul_f": mul_f,
        "muc_m": muc_m,
        "mul_m": mul_m,
        "alpha_c_gen": alpha_c_gen,
        "alpha_l_gen": alpha_l_gen,
        "beta_c_gen": beta_c_gen,
        "beta_l_gen": beta_l_gen,
        "alpha_c_f": alpha_c_f,
        "alpha_l_f": alpha_l_f,
        "beta_c_f": beta_c_f,
        "beta_l_f": beta_l_f,
        "alpha_c_m": alpha_c_m,
        "alpha_l_m": alpha_l_m,
        "beta_c_m": beta_c_m,
        "beta_l_m": beta_l_m,
    }
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze pooled gender-split Box-Cox results.")
    parser.add_argument("--variant", default="ascsOFF_q99", help="Variant tag (e.g., ascsOFF_q99).")
    parser.add_argument("--genders", nargs="+", default=["pooled"], help="Which gender tags to process.")
    parser.add_argument("--source", default="gender_split", help="Logical source label (default: gender_split).")
    parser.add_argument(
        "--base",
        type=Path,
        default=DEFAULT_BASE,
        help="Base directory containing pooled_{variant} subfolders.",
    )
    parser.add_argument(
        "--annotate-biogeme-html",
        action="store_true",
        help="Kept for interface parity; ignored for this analyzer.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing the wide DCM datasets (default: Data/processed/scenarios).",
    )
    return parser.parse_args()


def augment_gender_split_report(
    *,
    gender: str,
    variant: str,
    param_csv: Path,
    out_dir: Path,
) -> None:
    base_name = param_csv.stem.replace("_parameters", "")
    report_path = out_dir / f"{base_name}_analysis.html"
    if not report_path.exists():
        return

    params_table, params_dict, _ = load_parameters(param_csv)
    meta_path = param_csv.with_name(f"{base_name}_meta.json")
    meta = _load_json_if_exists(meta_path)

    required_keys = {"alpha_c_f", "alpha_c_m", "beta_c_f", "beta_c_m"}
    if not required_keys.issubset(params_dict.keys()):
        return

    df_src = load_dataset_for_gender(gender).copy()
    df_src = df_src.replace("", np.nan).infer_objects(copy=False)
    if "dgn" in df_src.columns:
        df_src["dgn"] = pd.to_numeric(df_src["dgn"], errors="coerce").fillna(0.0).clip(0.0, 1.0)
    else:
        df_src["dgn"] = 0.0

    labels = detect_labels(df_src)
    ensure_columns(df_src, ["actual_choice"])
    label_to_idx = {lab: idx for idx, lab in enumerate(labels)}
    act_idx = df_src["actual_choice"].astype(str).map(label_to_idx).to_numpy(dtype=int)

    T_ENDOW = float(meta.get("T", 80.0)) if meta else 80.0
    consumption_matrix = np.column_stack(
        [pd.to_numeric(df_src[f"consumption_{lab}"], errors="coerce").to_numpy(float) for lab in labels]
    )
    lhw_matrix = np.column_stack(
        [pd.to_numeric(df_src[f"lhw_{lab}"], errors="coerce").to_numpy(float) for lab in labels]
    )
    cons_act = consumption_matrix[np.arange(len(df_src)), act_idx]
    leisure_act = T_ENDOW - lhw_matrix[np.arange(len(df_src)), act_idx]

    y_ref = float(meta.get("y_ref", np.nan)) if meta else np.nan
    if not np.isfinite(y_ref) or y_ref <= 0:
        cons_valid = cons_act[np.isfinite(cons_act) & (cons_act > 0)]
        if cons_valid.size:
            y_ref = float(np.quantile(cons_valid, 0.99))
        else:
            y_ref = 1.0

    c_norm_act = np.clip(cons_act / y_ref, 1e-6, 1.0)
    l_norm_act = np.clip(leisure_act / T_ENDOW, 1e-6, 1.0)
    df_src = df_src.copy()
    df_src["c_norm_actual"] = c_norm_act
    df_src["l_norm_actual"] = l_norm_act

    mask_f = df_src["dgn"] == 0
    mask_m = df_src["dgn"] == 1

    def _quartiles(series: pd.Series) -> list[float]:
        vals = pd.to_numeric(series, errors="coerce")
        if vals.dropna().empty:
            return [float("nan")] * 4
        return [float(np.nanpercentile(vals, q)) for q in (25.0, 50.0, 75.0, 99.0)]

    c_marks_gen = _quartiles(df_src["c_norm_actual"])
    l_marks_gen = _quartiles(df_src["l_norm_actual"])
    c_marks_f = _quartiles(df_src.loc[mask_f, "c_norm_actual"])
    l_marks_f = _quartiles(df_src.loc[mask_f, "l_norm_actual"])
    c_marks_m = _quartiles(df_src.loc[mask_m, "c_norm_actual"])
    l_marks_m = _quartiles(df_src.loc[mask_m, "l_norm_actual"])

    z_cols = [col for col in ("age_norm", "age2_norm", "child_norm", "dch") if col in df_src.columns]
    Z_pooled, Z_f, Z_m = compute_Z_medians_gender(df_src, z_cols, gender_col="dgn")

    meta_for_curves = dict(meta or {})
    meta_for_curves["y_ref"] = y_ref
    meta_for_curves["T"] = T_ENDOW
    bc_curves = build_boxcox_mu_and_contours_gender_split(
        params=params_dict,
        meta=meta_for_curves,
        Z_pooled=Z_pooled,
        Z_f=Z_f,
        Z_m=Z_m,
        grid_points=400,
    )

    muc_gen_png = out_dir / f"{base_name}_gender_muc_general.png"
    mul_gen_png = out_dir / f"{base_name}_gender_mul_general.png"
    ctr_gen_png = out_dir / f"{base_name}_gender_contours_general.png"

    muc_f_png = out_dir / f"{base_name}_gender_muc_female.png"
    mul_f_png = out_dir / f"{base_name}_gender_mul_female.png"
    ctr_f_png = out_dir / f"{base_name}_gender_contours_female.png"

    muc_m_png = out_dir / f"{base_name}_gender_muc_male.png"
    mul_m_png = out_dir / f"{base_name}_gender_mul_male.png"
    ctr_m_png = out_dir / f"{base_name}_gender_contours_male.png"

    plot_mu_norm(
        bc_curves["c_grid"],
        bc_curves["muc_gen"],
        "c_norm",
        "MUC (normalized)",
        f"MUC vs c_norm — pooled baseline ({variant})",
        muc_gen_png,
        marks=c_marks_gen,
        endpoint=bc_curves["beta_c_gen"],
    )
    plot_mu_norm(
        bc_curves["l_grid"],
        bc_curves["mul_gen"],
        "l_norm",
        "MUL (normalized)",
        f"MUL vs l_norm — pooled baseline ({variant})",
        mul_gen_png,
        marks=l_marks_gen,
        endpoint=bc_curves["beta_l_gen"],
    )
    plot_indifference_contours_boxcox(
        {"alpha_c": bc_curves["alpha_c_gen"], "alpha_l": bc_curves["alpha_l_gen"], "beta_c": bc_curves["beta_c_gen"]},
        bc_curves["beta_l_gen"],
        ctr_gen_png,
        (25, 50, 75, 99),
    )

    plot_mu_norm(
        bc_curves["c_grid"],
        bc_curves["muc_f"],
        "c_norm",
        "MUC (normalized)",
        f"MUC vs c_norm — female ({variant})",
        muc_f_png,
        marks=c_marks_f,
        endpoint=bc_curves["beta_c_f"],
    )
    plot_mu_norm(
        bc_curves["l_grid"],
        bc_curves["mul_f"],
        "l_norm",
        "MUL (normalized)",
        f"MUL vs l_norm — female ({variant})",
        mul_f_png,
        marks=l_marks_f,
        endpoint=bc_curves["beta_l_f"],
    )
    plot_indifference_contours_boxcox(
        {"alpha_c": bc_curves["alpha_c_f"], "alpha_l": bc_curves["alpha_l_f"], "beta_c": bc_curves["beta_c_f"]},
        bc_curves["beta_l_f"],
        ctr_f_png,
        (25, 50, 75, 99),
    )

    plot_mu_norm(
        bc_curves["c_grid"],
        bc_curves["muc_m"],
        "c_norm",
        "MUC (normalized)",
        f"MUC vs c_norm — male ({variant})",
        muc_m_png,
        marks=c_marks_m,
        endpoint=bc_curves["beta_c_m"],
    )
    plot_mu_norm(
        bc_curves["l_grid"],
        bc_curves["mul_m"],
        "l_norm",
        "MUL (normalized)",
        f"MUL vs l_norm — male ({variant})",
        mul_m_png,
        marks=l_marks_m,
        endpoint=bc_curves["beta_l_m"],
    )
    plot_indifference_contours_boxcox(
        {"alpha_c": bc_curves["alpha_c_m"], "alpha_l": bc_curves["alpha_l_m"], "beta_c": bc_curves["beta_c_m"]},
        bc_curves["beta_l_m"],
        ctr_m_png,
        (25, 50, 75, 99),
    )

    reparam = reparam_gender_split_boxcox(params_dict)
    display_order = OrderedDict([
        ("alpha_c", "alpha_c"),
        ("alpha_l", "alpha_l"),
        ("beta_c", "beta_c"),
        ("beta_l0", "beta_l0"),
        ("delta_age_norm", "delta_age"),
        ("delta_age2_norm", "delta_age2"),
        ("delta_child_norm", "delta_child"),
        ("delta_dch", "delta_dch"),
    ])

    rows = []
    for raw_key, label in display_order.items():
        base_val = reparam.get(raw_key)
        dev_val = reparam.get(f"{raw_key}_m")
        if base_val is None and dev_val is None:
            continue
        pretty = label.replace("_", " ").replace("norm", "").strip()
        rows.append(
            {
                "Parameter": pretty,
                "Female baseline": base_val,
                "Male deviation": dev_val,
            }
        )

    if rows:
        split_df = pd.DataFrame(rows).set_index("Parameter")
        split_table_html = split_df.to_html(border=0, classes="table table-sm", float_format="%.6g")
    else:
        split_table_html = "<p>No gender-specific parameters detected.</p>"

    extra_section = f"""
  <section>
    <h2>Box-Cox (baseline + male deviation)</h2>
    {split_table_html}
    <table class="table table-sm" style="text-align:center;">
      <tr>
        <th></th>
        <th>MUC(c_norm)</th>
        <th>MUL(l_norm)</th>
        <th>Utility contours</th>
      </tr>
      <tr>
        <td><strong>Pooled (baseline)</strong></td>
        <td><img src="{muc_gen_png.name}" alt="MUC pooled"></td>
        <td><img src="{mul_gen_png.name}" alt="MUL pooled"></td>
        <td><img src="{ctr_gen_png.name}" alt="Contours pooled"></td>
      </tr>
      <tr>
        <td><strong>Female</strong></td>
        <td><img src="{muc_f_png.name}" alt="MUC female"></td>
        <td><img src="{mul_f_png.name}" alt="MUL female"></td>
        <td><img src="{ctr_f_png.name}" alt="Contours female"></td>
      </tr>
      <tr>
        <td><strong>Male</strong></td>
        <td><img src="{muc_m_png.name}" alt="MUC male"></td>
        <td><img src="{mul_m_png.name}" alt="MUL male"></td>
        <td><img src="{ctr_m_png.name}" alt="Contours male"></td>
      </tr>
    </table>
  </section>
"""

    try:
        html = report_path.read_text(encoding="utf-8")
    except Exception:
        return
    if "</body>" in html:
        html = html.replace("</body>", f"{extra_section}\n</body>", 1)
    else:
        html = html + extra_section
    report_path.write_text(html, encoding="utf-8")


def analyze_gender(
    gender: str,
    variant: str,
    source: str,
    base_dir: Path,
    annotate_flag: bool,
) -> dict[str, object]:
    if gender != "pooled":
        raise ValueError("Gender-split analyzer only supports the pooled output.")

    model_name = f"{MODEL_PREFIX}_{variant}".replace(".", "_")
    param_csv = None

    direct = base_dir / f"{gender}_{variant}" / f"{model_name}_parameters.csv"
    if direct.exists():
        param_csv = direct
    else:
        for candidate in base_dir.rglob(f"{model_name}_parameters.csv"):
            param_csv = candidate
            break
    if param_csv is None or not param_csv.exists():
        raise FileNotFoundError(f"Parameter file not found under {base_dir} (expected {model_name}_parameters.csv)")

    out_dir = param_csv.parent

    metrics = process_gender(
        gender=gender,
        variant=variant,
        param_csv=param_csv,
        out_dir=out_dir,
        source=source,
        annotate_biogeme_html_flag=annotate_flag,
    )
    augment_gender_split_report(
        gender=gender,
        variant=variant,
        param_csv=param_csv,
        out_dir=out_dir,
    )
    return metrics


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")
    set_data_dir(args.data_dir)

    summary: List[dict[str, object]] = []
    for gender in args.genders:
        try:
            metrics = analyze_gender(
                gender=gender,
                variant=args.variant,
                source=args.source,
                base_dir=args.base,
                annotate_flag=args.annotate_biogeme_html,
            )
            summary.append(metrics)
        except Exception as exc:
            logging.error("[%s] Analyzer failed: %s", gender, exc)

    if summary:
        print("=== Gender-Split Summary ===")
        for m in summary:
            print(
                f"{m['source']:<12} {m['gender']:<6} {m['variant']:<12} "
                f"accuracy={m['accuracy']:.2%}  MUC<0={m['muc_share']:.2%}  MUL<0={m['mul_share']:.2%}"
            )


if __name__ == "__main__":
    main()
