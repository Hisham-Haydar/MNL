#!/usr/bin/env python
"""
Estimate the Box–Cox labour-supply DCM using GAMSPy instead of SciPy.

This script mirrors `scripts/DCM1_boxcox.py`: same CLI, data preparation,
utility specification, and reporting. The only change is that the
maximum-likelihood problem is expressed as a GAMSPy nonlinear model and
solved with a user-selected NLP solver (ipopth default, or conopt/knitro).

# KNITRO Community limits:
#   - ≤300 constraints
#   - ≤300 variables
#   - ≤50 discrete variables
#   - ≤2000 nonzeros
#   - ≤1000 nonlinear nonzeros
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

try:
    from gamspy import Container, Model, Variable
    from gamspy.math import exp as gp_exp
    from gamspy.math import log as gp_log
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "GAMSPy is required for scripts/DCM1_gamspy.py. Install it via 'pip install gamspy'."
    ) from exc

from analyzer_runner import run_analyzer
from path_helpers import data_root, reports_root, ensure_local_workdir

try:
    import DCM1_boxcox as boxcox
except ImportError:  # pragma: no cover
    from scripts import DCM1_boxcox as boxcox

LOGGER = logging.getLogger(__name__)

SOLVER_MAP = {
    "ipopth": "ipopth",
    "conopt": "conopt",
    "knitro": "knitro",
}

EPS_ALPHA = 1e-6
LOG_EPS = 1e-12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate Box–Cox DCM with GAMSPy.")
    parser.add_argument("--genders", nargs="+", choices=("male", "female"), default=["male", "female"])
    parser.add_argument("--labels", nargs="+", help="Scenario labels to include (default: all detected).")
    parser.add_argument("--auto-labels", action="store_true", help="Detect scenario labels from dataset columns.")
    parser.add_argument("--include-ascs", action="store_true", help="Include ASC parameters (base fixed).")
    parser.add_argument("--pooled", action="store_true", help="Estimate pooled model with gender shifter.")
    parser.add_argument(
        "--gender-split",
        action="store_true",
        help="In --pooled mode, use gender-specific Box–Cox params (alpha/beta).",
    )
    parser.add_argument(
        "--z-by-gender",
        action="store_true",
        help="Also split Z shifters (delta_*) by gender when --gender-split is on.",
    )
    parser.add_argument("--gender-column", default="dgn", help="Gender column name (1=female, 0=male).")
    parser.add_argument("--c-scale-quantile", type=float, default=0.99, help="Quantile for consumption normalisation (default 0.99).")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=reports_root() / "gamspy" / "boxcox",
        help="Output directory base (default: reports/gamspy/boxcox).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=data_root() / "processed" / "scenarios",
        help="Input directory for wide datasets.",
    )
    parser.add_argument(
        "--solver",
        choices=tuple(SOLVER_MAP.keys()),
        default="ipopth",
        help="GAMSPy NLP solver (default: ipopth).",
    )
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"), help="Logging verbosity.")
    return parser.parse_args()


def _load_gender_df(data_dir: Path, gender: str, labels_cfg: Iterable[str] | None, auto_labels: bool) -> Tuple[pd.DataFrame, Tuple[str, ...]]:
    dataset_path = data_dir / f"heads_wide_single_{gender}_dcm.parquet"
    df = boxcox.load_wide_dataset(dataset_path)
    labels = boxcox.detect_labels(df, tuple(labels_cfg) if (labels_cfg and not auto_labels) else None)
    if not auto_labels and labels_cfg:
        labels = tuple(labels_cfg)
    df = boxcox.maybe_add_gender(df, 1.0 if gender == "female" else 0.0, "dgn")
    return df, labels


def boxcox_expr(value: float, alpha_var: Variable) -> gp.Expression:
    """
    Box–Cox transform using exp(alpha * log(val)) to respect GAMS' constant exponent requirement.
    """
    val = max(value, boxcox.EPS)
    log_val = math.log(val)
    num = gp_exp(alpha_var * log_val) - 1.0
    den = alpha_var + EPS_ALPHA
    return num / den


def _value_from_var(var: Variable) -> float:
    records = getattr(var, "records", None)
    if records is None:
        return float(getattr(var, "level", 0.0))
    if hasattr(records, "level"):
        level_series = records.level
        if hasattr(level_series, "iloc") and len(level_series):
            return float(level_series.iloc[0])
    if hasattr(records, "iloc") and len(records):
        last_col = records.columns[-1]
        return float(records.iloc[0][last_col])
    raise RuntimeError(f"Unable to extract level for variable {var.name}")


def build_and_solve_gamspy_model(
    data: boxcox.ModelData,
    structure: boxcox.ParamStructure,
    solver_key: str,
) -> Dict[str, object]:
    solver = SOLVER_MAP.get(solver_key)
    if not solver:
        raise ValueError(f"Unsupported solver '{solver_key}'. Choose from {tuple(SOLVER_MAP)}.")

    ensure_local_workdir()
    container = Container()
    scalar_vars: Dict[str, Variable] = {}
    delta_vars: Dict[str, Variable] = {}
    asc_vars: Dict[str, Variable] = {}

    for name in structure.param_names:
        if name in structure.delta_names or name.startswith("ASC_"):
            continue
        lb, ub = (None, None)
        if name.startswith("alpha_"):
            lb, ub = -2.0, 2.0
        var = Variable(container, name, type="free")
        if lb is not None:
            var.lo = lb
        if ub is not None:
            var.up = ub
        scalar_vars[name] = var

    for dname in structure.delta_names:
        delta_vars[dname] = Variable(container, dname, type="free")

    for lab in structure.asc_labels:
        asc_vars[lab] = Variable(container, f"ASC_{lab}", type="free")

    g_f_vec = data.features.get("gender", np.zeros(len(data.actual_idx)))
    g_m_vec = 1.0 - g_f_vec

    feature_vectors: Dict[str, np.ndarray] = {}
    for dname in structure.delta_names:
        feature_vectors[dname] = boxcox.feature_from_delta(data, dname)

    alt_labels = list(data.labels)
    objective_expr = 0.0
    gender_split = "alpha_c_f" in scalar_vars
    delta_split = any(name.endswith("_f") or name.endswith("_m") for name in structure.delta_names)

    def beta_l_expression(n_idx: int):
        if delta_split:
            f_terms = scalar_vars["beta_l0_f"]
            for dname in structure.delta_names:
                if dname.endswith("_f"):
                    f_terms += feature_vectors[dname][n_idx] * delta_vars[dname]
            m_terms = scalar_vars["beta_l0_m"]
            for dname in structure.delta_names:
                if dname.endswith("_m"):
                    m_terms += feature_vectors[dname][n_idx] * delta_vars[dname]
            return g_f_vec[n_idx] * f_terms + g_m_vec[n_idx] * m_terms
        beta_terms = scalar_vars["beta_l0"]
        for dname in structure.delta_names:
            beta_terms += feature_vectors[dname][n_idx] * delta_vars[dname]
        return beta_terms

    def beta_c_expression(n_idx: int):
        if gender_split:
            return g_f_vec[n_idx] * scalar_vars["beta_c_f"] + g_m_vec[n_idx] * scalar_vars["beta_c_m"]
        return scalar_vars["beta_c"]

    def asc_expression(label: str):
        return asc_vars.get(label, 0.0)

    def bc_c_term(n_idx: int, j_idx: int):
        value = data.C_norm[n_idx, j_idx]
        if gender_split:
            term_f = boxcox_expr(value, scalar_vars["alpha_c_f"])
            term_m = boxcox_expr(value, scalar_vars["alpha_c_m"])
            return g_f_vec[n_idx] * term_f + g_m_vec[n_idx] * term_m
        return boxcox_expr(value, scalar_vars["alpha_c"])

    def bc_l_term(n_idx: int, j_idx: int):
        value = data.L_norm[n_idx, j_idx]
        if gender_split:
            term_f = boxcox_expr(value, scalar_vars["alpha_l_f"])
            term_m = boxcox_expr(value, scalar_vars["alpha_l_m"])
            return g_f_vec[n_idx] * term_f + g_m_vec[n_idx] * term_m
        return boxcox_expr(value, scalar_vars["alpha_l"])

    for n_idx in range(len(data.actual_idx)):
        chosen_idx = data.actual_idx[n_idx]
        lognum_expr = 0.0
        denom_expr = 0.0
        beta_l_val = beta_l_expression(n_idx)
        beta_c_val = beta_c_expression(n_idx)
        for j_idx, label in enumerate(alt_labels):
            if not data.availability[n_idx, j_idx]:
                continue
            bc_c_val = bc_c_term(n_idx, j_idx)
            bc_l_val = bc_l_term(n_idx, j_idx)
            utility = beta_c_val * bc_c_val + beta_l_val * bc_l_val + asc_expression(label)
            if chosen_idx == j_idx:
                lognum_expr += utility
            denom_expr += gp_exp(utility)
        objective_expr += lognum_expr - gp_log(denom_expr + LOG_EPS)

    model = Model(
        container,
        "boxcox_gamspy",
        problem="NLP",
        objective=objective_expr,
        sense="max",
    )
    t0 = time.perf_counter()
    model.solve(solver=solver)
    solve_time = time.perf_counter() - t0
    LOGGER.info("[GAMSPy] Solver=%s runtime=%.3f seconds", solver, solve_time)

    theta_values: List[float] = []
    for name in structure.param_names:
        if name in scalar_vars:
            theta_values.append(_value_from_var(scalar_vars[name]))
        elif name in delta_vars:
            theta_values.append(_value_from_var(delta_vars[name]))
        elif name.startswith("ASC_"):
            lab = name.split("ASC_", 1)[1]
            theta_values.append(_value_from_var(asc_vars[lab]))
        else:
            raise KeyError(f"Unknown parameter '{name}' in GAMSPy solution.")

    return {
        "theta": np.array(theta_values, dtype=float),
        "solver": solver,
        "model_status": getattr(model, "model_status", None),
        "solver_status": getattr(model, "solver_status", None),
        "solve_time": solve_time,
    }


def estimate_with_gamspy(
    gender_key: str,
    df: pd.DataFrame,
    labels: Tuple[str, ...],
    *,
    include_ascs: bool,
    gender_column: str,
    output_dir: Path,
    log_level: int,
    c_scale_quantile: float,
    variant: str,
    gender_split: bool = False,
    z_by_gender: bool = False,
    model_prefix: str | None = None,
    analyzer_source: str = "gamspy",
    dataset_source_dir: Path | None = None,
    solver_name: str = "ipopth",
) -> None:
    if gender_key != "pooled":
        gender_split = False
        z_by_gender = False
    data = boxcox.prepare_dataset(df, labels, gender_column=gender_column, c_scale_quantile=c_scale_quantile)
    if gender_split and not data.has_gender_param:
        gender_split = False
        z_by_gender = False
    structure = boxcox.build_param_structure(
        labels,
        data,
        include_ascs=include_ascs,
        pooled=(gender_key == "pooled"),
        gender_split=gender_split,
        z_by_gender=z_by_gender,
    )

    def _is_binary01(arr: np.ndarray) -> bool:
        finite = arr[np.isfinite(arr)]
        if finite.size == 0:
            return False
        u = np.unique(finite)
        return len(u) <= 2 and set(np.round(u, 6)).issubset({0.0, 1.0})

    Z_stats: Dict[str, float] = {}
    _zmap = {
        "age_norm": "age",
        "age2_norm": "age2",
        "child_norm": "child",
        "dch": "dch",
        "gender": "gender",
    }
    for fk, arr in data.features.items():
        name = _zmap.get(fk, fk)
        a = np.asarray(arr, dtype=float)
        if _is_binary01(a):
            finite = a[np.isfinite(a)]
            if finite.size:
                vals, counts = np.unique(finite, return_counts=True)
                val = float(vals[np.argmax(counts)])
            else:
                val = 0.0
        else:
            val = float(np.nanmedian(a))
        Z_stats[name] = val

    idx = np.arange(len(data.actual_idx))
    C_norm_actual = data.C_norm[idx, data.actual_idx]
    L_norm_actual = data.L_norm[idx, data.actual_idx]
    c_norm_med = float(np.nanmedian(C_norm_actual))
    l_norm_med = float(np.nanmedian(L_norm_actual))

    LOGGER.info("[%s] Parameter vector: %s", gender_key, structure.param_names)

    solver_result = build_and_solve_gamspy_model(data, structure, solver_name)
    theta_hat = solver_result["theta"]
    ll_star = -boxcox.negative_log_likelihood(theta_hat, data, structure)
    ll_null = boxcox.compute_null_loglik(data)

    param_values = boxcox.flatten_params(theta_hat, structure)

    beta_l_med = float(param_values.get("beta_l0", 0.0))
    for dname in structure.delta_names:
        base = dname.replace("delta_", "")
        zval = Z_stats.get(base, 0.0)
        beta_l_med += float(param_values.get(dname, 0.0)) * float(zval)

    alpha_c = float(param_values.get("alpha_c", param_values.get("alpha_c_f", 0.0)))
    alpha_l = float(param_values.get("alpha_l", param_values.get("alpha_l_f", 0.0)))
    beta_c = float(param_values.get("beta_c", param_values.get("beta_c_f", 0.0)))

    muc_norm_med = beta_c * (c_norm_med ** (alpha_c - 1.0)) if c_norm_med > 0 else float("nan")
    mul_norm_med = beta_l_med * (l_norm_med ** (alpha_l - 1.0)) if l_norm_med > 0 else float("nan")

    mrs_norm_med = (
        mul_norm_med / muc_norm_med
        if (np.isfinite(mul_norm_med) and np.isfinite(muc_norm_med) and muc_norm_med != 0.0)
        else float("nan")
    )

    muc_norm_zero_c = None if beta_c != 0.0 else 0.0
    mul_norm_zero_l = None if beta_l_med != 0.0 else 0.0

    predicted = boxcox.predict_choices(theta_hat, data, structure)
    accuracy = float(np.mean(predicted == data.actual_idx))

    k_params = len(structure.param_names)
    n_obs = len(data.actual_idx)
    rho2 = float(1.0 - ll_star / ll_null) if ll_null != 0 else float("nan")
    rho2_adj = float(1.0 - (ll_star - k_params) / ll_null) if ll_null != 0 else float("nan")
    aic = 2 * k_params - 2 * ll_star
    bic = math.log(n_obs) * k_params - 2 * ll_star

    cm = boxcox.confusion_matrix(data.actual_choice, predicted, data.labels)

    scores = boxcox.score_matrix(theta_hat, data, structure)
    foc_norm = float(np.linalg.norm(scores.sum(axis=0)))

    H = boxcox.approximate_hessian(theta_hat, data, structure, eps=None)
    H = 0.5 * (H + H.T)
    ridge = 1e-8 * max(1.0, float(np.mean(np.abs(np.diag(H)))))
    H = H + ridge * np.eye(k_params)

    Hinv = np.linalg.inv(H)
    cov = Hinv.copy()

    G = scores.T @ scores
    cov_rob = Hinv @ G @ Hinv
    cov_rob = 0.5 * (cov_rob + cov_rob.T)

    w, _ = np.linalg.eigh(0.5 * (H + H.T))
    min_eig_H = float(np.min(w))
    max_eig_H = float(np.max(w))
    cond_H = float(max_eig_H / max(min_eig_H, 1e-16))
    LOGGER.info("[%s] Observed-Hessian eigs: min=%.3e  max=%.3e  cond≈%.3e", gender_key, min_eig_H, max_eig_H, cond_H)

    values_vector = np.array([param_values[name] for name in structure.param_names], dtype=float)

    diag_cov = np.diag(cov)
    diag_cov_rob = np.diag(cov_rob)
    se = np.sqrt(np.where(diag_cov >= 0, diag_cov, np.nan))
    se_rob = np.sqrt(np.where(diag_cov_rob >= 0, diag_cov_rob, np.nan))

    with np.errstate(divide="ignore", invalid="ignore"):
        t_values = np.divide(values_vector, se, out=np.full_like(values_vector, np.nan), where=se > 0)
        t_values_rob = np.divide(values_vector, se_rob, out=np.full_like(values_vector, np.nan), where=se_rob > 0)

    p_values = np.where(np.isnan(t_values), np.nan, 2.0 * boxcox.norm.sf(np.abs(t_values)))
    p_values_rob = np.where(np.isnan(t_values_rob), np.nan, 2.0 * boxcox.norm.sf(np.abs(t_values_rob)))

    param_df = boxcox.build_parameter_dataframe(
        param_values,
        structure,
        se=se,
        t_values=t_values,
        p_values=p_values,
        se_rob=se_rob,
        t_values_rob=t_values_rob,
        p_values_rob=p_values_rob,
    )

    draws_df, muc_summary = boxcox.generate_mucmul_draws(param_values, data)

    min_eig = float(np.min(np.linalg.eigvalsh(0.5 * (cov + cov.T))))

    LOGGER.info("[%s] Log-likelihood at optimum: %.4f", gender_key, ll_star)
    LOGGER.info("[%s] LL(null)=%.4f  rho²=%.4f  rho²_adj=%.4f", gender_key, ll_null, rho2, rho2_adj)
    LOGGER.info("[%s] AIC=%.2f  BIC=%.2f", gender_key, aic, bic)
    LOGGER.info("[%s] Accuracy=%.2f%%", gender_key, accuracy * 100.0)
    LOGGER.info("[%s] Confusion matrix:\n%s", gender_key, cm)
    LOGGER.info("[%s] FOC norm: %.3e", gender_key, foc_norm)
    LOGGER.info(
        "[%s] GAMSPy solver=%s status=(model=%s, solver=%s) time=%.3fs",
        gender_key,
        solver_result["solver"],
        solver_result["model_status"],
        solver_result["solver_status"],
        solver_result.get("solve_time", float("nan")),
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    base_prefix = model_prefix or f"boxcox_{gender_key}_gamspy"
    model_name = f"{base_prefix}_{variant}".replace(".", "_")
    meta = {
        "spec": "boxcox",
        "labels": list(labels),
        "include_ascs": include_ascs,
        "pooled": gender_key == "pooled",
        "variant": variant,
        "c_scale_quantile": c_scale_quantile,
        "log_likelihood": ll_star,
        "null_log_likelihood": ll_null,
        "rho2": rho2,
        "rho2_adj": rho2_adj,
        "aic": aic,
        "bic": bic,
        "accuracy": accuracy,
        "k_params": k_params,
        "min_eig_cov": min_eig,
        "y_ref": data.y_ref,
        "T": boxcox.T_HOURS,
        "parameters": param_values,
        "n_obs": n_obs,
        "solver": solver_result["solver"],
        "model_status": solver_result["model_status"],
        "solver_status": solver_result["solver_status"],
    }
    if dataset_source_dir is not None:
        meta["data_dir"] = str(dataset_source_dir)
    meta.update({k: float(v) for k, v in muc_summary.items()})
    meta.update({
        "parameters_csv": f"{model_name}_parameters.csv",
        "confusion_csv": f"{model_name}_confusion.csv",
        "Z_medians_or_modes": Z_stats,
        "c_norm_median": c_norm_med,
        "l_norm_median": l_norm_med,
        "MUC_norm_med": float(muc_norm_med),
        "MUL_norm_med": float(mul_norm_med),
        "MRS_norm_med": float(mrs_norm_med),
        "muc_norm_zero_c_norm": muc_norm_zero_c,
        "mul_norm_zero_l_norm": mul_norm_zero_l,
    })

    boxcox.write_parameter_metadata(output_dir, model_name, param_df, meta)

    cm_path = output_dir / f"{model_name}_confusion.csv"
    cm.to_csv(cm_path)

    draws_path = output_dir / f"{model_name}_mucmul_draws.csv"
    draws_df.to_csv(draws_path)

    muc_summary_path = output_dir / f"{model_name}_mucmul_summary.json"
    muc_summary_path.write_text(json.dumps(muc_summary, indent=2), encoding="utf-8")

    run_analyzer(analyzer_source, [gender_key], variant, data_dir=dataset_source_dir)


def run_estimation(args: argparse.Namespace) -> None:
    labels_cfg = tuple(args.labels) if args.labels and not args.auto_labels else None
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.pooled:
        male_path = args.data_dir / "heads_wide_single_male_dcm.parquet"
        female_path = args.data_dir / "heads_wide_single_female_dcm.parquet"
        male_df = boxcox.maybe_add_gender(boxcox.load_wide_dataset(male_path), 0.0, args.gender_column)
        female_df = boxcox.maybe_add_gender(boxcox.load_wide_dataset(female_path), 1.0, args.gender_column)

        labels_m = boxcox.detect_labels(male_df, labels_cfg)
        labels_f = boxcox.detect_labels(female_df, labels_m)
        if labels_m != labels_f:
            raise ValueError("Scenario labels differ between genders; align datasets before pooling.")

        common_cols = sorted(set(male_df.columns).intersection(female_df.columns))
        pooled_df = pd.concat([male_df[common_cols], female_df[common_cols]], ignore_index=True, sort=False)
        estimate_with_gamspy(
            "pooled",
            pooled_df,
            labels_m,
            include_ascs=args.include_ascs,
            gender_column=args.gender_column,
            output_dir=args.output_dir / f"pooled_{args.solver}_{('ascsON' if args.include_ascs else 'ascsOFF')}",
            log_level=getattr(logging, args.log_level.upper()),
            c_scale_quantile=args.c_scale_quantile,
            variant=f"{'ascsON' if args.include_ascs else 'ascsOFF'}_q{int(round(args.c_scale_quantile * 100))}",
            gender_split=bool(args.gender_split),
            z_by_gender=bool(args.z_by_gender),
            analyzer_source="gamspy",
            dataset_source_dir=args.data_dir,
            solver_name=args.solver,
        )
        return

    variant = f"{'ascsON' if args.include_ascs else 'ascsOFF'}_q{int(round(args.c_scale_quantile * 100))}"
    for gender in args.genders:
        try:
            dataset_path = args.data_dir / f"heads_wide_single_{gender}_dcm.parquet"
            df = boxcox.load_wide_dataset(dataset_path)
            labels = boxcox.detect_labels(df, labels_cfg)
            estimate_with_gamspy(
                gender,
                df,
                labels,
                include_ascs=args.include_ascs,
                gender_column=args.gender_column,
                output_dir=args.output_dir / f"{gender}_{variant}",
                log_level=getattr(logging, args.log_level.upper()),
                c_scale_quantile=args.c_scale_quantile,
                variant=variant,
                analyzer_source="gamspy",
                dataset_source_dir=args.data_dir,
                solver_name=args.solver,
            )
        except Exception as exc:  # pragma: no cover - defensive loop
            LOGGER.error("[%s] Estimation failed: %s", gender, exc, exc_info=True)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")
    run_estimation(args)


if __name__ == "__main__":  # pragma: no cover
    main()
