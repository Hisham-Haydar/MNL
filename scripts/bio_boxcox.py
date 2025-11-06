#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2025-11-06 09:29:50
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scripts/bio_bocox.py — Minimal Box–Cox MNL in Biogeme, analyzer-ready.

Utility (alternative j):
  U_ij = ASC_j
         + beta_c * BC(C_norm_ij; alpha_c)
         + [beta_l0 + delta_age*age_norm_i + delta_age2*age2_norm_i
            + delta_child*child_norm_i + delta_dch*dch_i (+ delta_gender*dgn_i if pooled)]
           * BC(L_norm_ij; alpha_l)

Where:
  C_norm_ij = clip(consumption_ij / y_ref, 1e-6, ∞)       # <-- no upper cap
  L_norm_ij = clip((80 - lhw_ij) / 80,        1e-6, 1.0)
  y_ref     = 99th pct of actual-choice consumption (fallback 95/90/max)

Outputs (per run folder):
  <model_name>_parameters.csv
  <model_name>_robust_vcov.csv (if available)
  <model_name>_vcov.csv        (if available)
  <model_name>_meta.json
  <model_name>_confusion.csv
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd

import biogeme.biogeme as bio
import biogeme.database as db
from biogeme.expressions import Beta, Variable
from biogeme.models import boxcox, loglogit

# Project helpers (provided in your repo)
from path_helpers import data_root, reports_root

LOGGER = logging.getLogger("bio_bocox")

T_ENDOW: float = 80.0
EPS: float = 1e-6
DEFAULT_LABELS: Tuple[str, ...] = ("h0", "h1", "h2", "h3", "h4", "h5", "h6")


# ------------------------------ utils --------------------------------------
def ensure(df: pd.DataFrame, cols: Iterable[str]) -> None:
    miss = [c for c in cols if c not in df.columns]
    if miss:
        raise KeyError(f"Missing required column(s): {miss}")

def detect_labels(df: pd.DataFrame, labels: Sequence[str] | None) -> Tuple[str, ...]:
    if labels:
        L = tuple(labels)
        for lab in L:
            ensure(df, [f"consumption_{lab}", f"lhw_{lab}"])
        return L
    labs = [c.split("consumption_", 1)[1] for c in df.columns if c.startswith("consumption_")]
    labs = sorted(set(labs), key=lambda s: (len(s), s))
    if not labs:
        raise ValueError("Could not detect scenario labels (expected consumption_*)")
    for lab in labs:
        ensure(df, [f"lhw_{lab}"])
    return tuple(labs)

def compute_y_ref(consumption: np.ndarray, actual_idx: np.ndarray, quantile: float = 0.99) -> float:
    cons_actual = consumption[np.arange(len(consumption)), actual_idx]
    cons_actual = cons_actual[np.isfinite(cons_actual) & (cons_actual > 0)]
    if cons_actual.size == 0:
        raise ValueError("No valid consumption values to compute y_ref.")
    for q in (quantile, 0.95, 0.90):
        y_ref = float(np.quantile(cons_actual, q))
        if np.isfinite(y_ref) and y_ref > 0:
            return y_ref
    return float(np.max(cons_actual))

def build_Z(df: pd.DataFrame, gender_column: str, pooled: bool) -> List[str]:
    # normalized shifters (non-dummies)
    age = pd.to_numeric(df["dag"], errors="coerce").fillna(16.0)
    age_norm = np.clip((age - 16.0) / (65.0 - 16.0), 0.0, 1.0)
    df["age_norm"] = age_norm
    df["age2_norm"] = age_norm ** 2
    df["child_norm"] = np.clip(pd.to_numeric(df["num_children_total"], errors="coerce").fillna(0.0) / 5.0, 0.0, 1.0)
    if "DCH" in df.columns:
        df["dch"] = pd.to_numeric(df["DCH"], errors="coerce").fillna(0.0).clip(0.0, 1.0)
    else:
        df["dch"] = 0.0
    z_names = ["age_norm", "age2_norm", "child_norm", "dch"]
    if pooled and (gender_column in df.columns):
        gv = pd.to_numeric(df[gender_column], errors="coerce").fillna(0.0)
        if gv.nunique() > 1:
            z_names.append(gender_column)
    return z_names

def add_norm_cols(df: pd.DataFrame, labels: Tuple[str, ...], y_ref: float) -> None:
    # add c_norm_* and l_norm_* + avail_*
    for lab in labels:
        c = pd.to_numeric(df[f"consumption_{lab}"], errors="coerce").to_numpy(float)
        h = pd.to_numeric(df[f"lhw_{lab}"], errors="coerce").to_numpy(float)
        # Keep both within [EPS, 1.0] to match MLE path and avoid tails
        c_norm = np.clip(c / y_ref, EPS, 1.0)     
        l_norm = np.clip((T_ENDOW - h) / T_ENDOW, EPS, 1.0)
        df[f"c_norm_{lab}"] = c_norm
        df[f"l_norm_{lab}"] = l_norm
        av = f"avail_{lab}"
        if av not in df.columns:
            df[av] = 1


# ------------------------------ core ---------------------------------------
def estimate_one(
    df_src: pd.DataFrame,
    labels: Tuple[str, ...],
    *,
    gender_key: str,
    pooled: bool,
    include_ascs: bool,
    gender_column: str,
    out_dir: Path,
) -> None:
    df = df_src.copy()
    ensure(df, ["actual_choice", "dag", "num_children_total"])
    df["actual_choice"] = df["actual_choice"].astype(str)

    lab2idx = {lab: i for i, lab in enumerate(labels)}
    if not df["actual_choice"].isin(lab2idx).all():
        bad = df.loc[~df["actual_choice"].isin(lab2idx), "actual_choice"].unique()
        raise ValueError(f"actual_choice contains unknown labels: {bad}")

    # Build Z_i columns
    z_cols = build_Z(df, gender_column=gender_column, pooled=pooled)

    # Stack raw arrays for y_ref computation
    cons_mat = np.stack([pd.to_numeric(df[f"consumption_{lab}"], errors="coerce").to_numpy(float) for lab in labels], axis=1)
    actual_idx = df["actual_choice"].map(lab2idx).to_numpy(int)
    y_ref = compute_y_ref(cons_mat, actual_idx, quantile=0.99)

    # Normalized per-alt inputs
    add_norm_cols(df, labels, y_ref)

    # Choice id (Biogeme alternatives are 1..J)
    df["choice_id"] = df["actual_choice"].map(lab2idx).astype(int) + 1

    # Keep only numeric columns Biogeme needs
    keep = ["choice_id"] + z_cols
    for lab in labels:
        keep += [f"c_norm_{lab}", f"l_norm_{lab}", f"avail_{lab}"]
    numeric = df[keep].apply(pd.to_numeric, errors="coerce")
    database = db.Database("boxcox_db", numeric)

    # ------------------------ Parameters -----------------------------------
    # Box–Cox powers & levels  (bounds tightened to [-2, 2], starts improved)
    alpha_c = Beta("alpha_c",  0.10, -2.0,  2.0, 0)
    alpha_l = Beta("alpha_l",  0.10, -2.0,  2.0, 0)
    beta_c  = Beta("beta_c",   1.00, None, None, 0)
    beta_l0 = Beta("beta_l0",  1.00, None, None, 0)

    # Leisure shifters (map to delta_* names in outputs)
    delta_age    = Beta("delta_age",    0.0, None, None, 0)
    delta_age2   = Beta("delta_age2",   0.0, None, None, 0)
    delta_child  = Beta("delta_child",  0.0, None, None, 0)
    delta_dch    = Beta("delta_dch",    0.0, None, None, 0)
    # Optional gender shifter if present in z_cols
    has_gender = gender_column in z_cols
    if has_gender:
        delta_gender = Beta("delta_gender", 0.0, None, None, 0)

    # Z variables
    age_n   = Variable("age_norm")
    age2_n  = Variable("age2_norm")
    child_n = Variable("child_norm")
    dch     = Variable("dch")
    if has_gender:
        gflag = Variable(gender_column)
        beta_l = beta_l0 + delta_age*age_n + delta_age2*age2_n + delta_child*child_n + delta_dch*dch + delta_gender*gflag
    else:
        beta_l = beta_l0 + delta_age*age_n + delta_age2*age2_n + delta_child*child_n + delta_dch*dch

    # ------------------------ Utilities ------------------------------------
    V: Dict[int, object] = {}
    AV: Dict[int, object] = {}
    for k, lab in enumerate(labels, start=1):
        c_n = Variable(f"c_norm_{lab}")
        l_n = Variable(f"l_norm_{lab}")
        asc = 0
        if include_ascs:
            if k == 1:
                asc = Beta(f"ASC_{lab}", 0.0, None, None, 1)  # base fixed
            else:
                asc = Beta(f"ASC_{lab}", 0.0, None, None, 0)
        V[k]  = asc + beta_c * boxcox(c_n, alpha_c) + beta_l * boxcox(l_n, alpha_l)
        AV[k] = Variable(f"avail_{lab}")

    choice = Variable("choice_id")
    logprob = loglogit(V, AV, choice)

    # ------------------------ Estimate -------------------------------------
    variant = f"{'ascsON' if include_ascs else 'ascsOFF'}_q99"
    model_name = f"boxcox_{gender_key}_{variant}"
    est_dir = out_dir / f"{gender_key}_{variant}"
    est_dir.mkdir(parents=True, exist_ok=True)

    bg = bio.BIOGEME(database, logprob)
    bg.model_name = model_name
    try:
        bg.set_output_directory(est_dir)
    except Exception:
        pass

    results = bg.estimate()

    # Parameters table (includes robust SE columns in Biogeme ≥3.x)
    params_df = results.get_estimated_parameters()
    params_df.to_csv(est_dir / f"{model_name}_parameters.csv")

    # Also save (robust) var-covar matrices if available
    try:
        rvc = results.getRobustVarCovar()
        if rvc is not None:
            (rvc if hasattr(rvc, "to_csv") else pd.DataFrame(rvc)).to_csv(est_dir / f"{model_name}_robust_vcov.csv")
    except Exception:
        pass
    try:
        vc = results.getVarCovar()
        if vc is not None:
            (vc if hasattr(vc, "to_csv") else pd.DataFrame(vc)).to_csv(est_dir / f"{model_name}_vcov.csv")
    except Exception:
        pass

    # Null LL (equal probs over available alts)
    try:
        ll_null = bg.nullLogLikelihood(AV, choice)
    except Exception:
        ll_null = None
    # Opt LL
    try:
        ll_star = float(getattr(results, "log_likelihood", results.data.logLike))
    except Exception:
        ll_star = None

    # ------------------------ Confusion (predictions) ----------------------
    betas = results.get_beta_values()
    def get(name, default=0.0): return float(betas[name]) if name in betas else float(default)

    # Head-level shifter scalars
    Z = np.column_stack([numeric[c] for c in z_cols]) if z_cols else np.zeros((len(numeric), 0))
    delta_vec = np.array(
        [get("delta_age"), get("delta_age2"), get("delta_child"), get("delta_dch")] + ([get("delta_gender")] if has_gender else []),
        dtype=float,
    )
    beta_l_np = get("beta_l0") + (Z @ delta_vec if delta_vec.size else 0.0)

    # Alt arrays
    J = len(labels)
    Cn = np.stack([numeric[f"c_norm_{lab}"].to_numpy(float) for lab in labels], axis=1)
    Ln = np.stack([numeric[f"l_norm_{lab}"].to_numpy(float) for lab in labels], axis=1)
    AVm = np.stack([numeric[f"avail_{lab}"].to_numpy(int).astype(bool) for lab in labels], axis=1)

    # Box–Cox transforms (numpy, with same limit behavior)
    def bc_np(x, a):
        x = np.clip(x, EPS, None)
        if abs(a) < 1e-8:
            return np.log(x)
        return (np.power(x, a) - 1.0) / a

    U = get("beta_c") * bc_np(Cn, get("alpha_c")) + beta_l_np[:, None] * bc_np(Ln, get("alpha_l"))

    # ASCs
    if include_ascs:
        asc_vec = np.zeros(J)
        for lab_idx, lab in enumerate(labels):
            if lab_idx == 0:
                continue  # base fixed to 0
            key = f"ASC_{lab}"
            if key in betas:
                asc_vec[lab_idx] = get(key)
        U = U + asc_vec

    U = np.where(AVm, U, -np.inf)
    pred_idx = np.argmax(U, axis=1)
    actual_idx_1based = numeric["choice_id"].to_numpy(int)
    actual_idx_0based = actual_idx_1based - 1

    # Confusion table
    cm = pd.crosstab(
        pd.Series([labels[i] for i in actual_idx_0based], name="actual"),
        pd.Series([labels[i] for i in pred_idx], name="predicted"),
        dropna=False,
    ).reindex(index=labels, columns=labels, fill_value=0)
    cm.to_csv(est_dir / f"{model_name}_confusion.csv")

    accuracy = float(np.mean(pred_idx == actual_idx_0based))

    # ------------------------ Meta JSON ------------------------------------
    k_params = int(params_df.shape[0])
    n_obs = int(numeric.shape[0])
    rho2 = float("nan")
    rho2_adj = float("nan")
    aic = float("nan")
    bic = float("nan")
    if (ll_star is not None) and (ll_null is not None) and (ll_null != 0):
        rho2 = 1.0 - ll_star / ll_null
        rho2_adj = 1.0 - (ll_star - k_params) / ll_null
        aic = 2 * k_params - 2 * ll_star
        bic = np.log(max(n_obs, 1)) * k_params - 2 * ll_star

    meta = {
        "spec": "boxcox",
        "labels": list(labels),
        "include_ascs": bool(include_ascs),
        "pooled": bool(pooled),
        "y_ref": float(y_ref),
        "T": float(T_ENDOW),
        "log_likelihood": float(ll_star) if ll_star is not None else None,
        "null_log_likelihood": float(ll_null) if ll_null is not None else None,
        "rho2": float(rho2),
        "rho2_adj": float(rho2_adj),
        "aic": float(aic),
        "bic": float(bic),
        "accuracy": float(accuracy),
        "parameters_csv": f"{model_name}_parameters.csv",
        "confusion_csv": f"{model_name}_confusion.csv",
        "model_name": model_name,
        "variant": variant,
        "c_scale_quantile": 0.99,
    }
    (est_dir / f"{model_name}_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Console summary
    print(results.short_summary())
    LOGGER.info("[%s] LL*=%s  LL0=%s  rho²=%.4f  rho²_adj=%.4f  AIC=%.2f  BIC=%.2f  Acc=%.2f%%",
                model_name,
                f"{ll_star:.4f}" if ll_star is not None else "NA",
                f"{ll_null:.4f}" if ll_null is not None else "NA",
                rho2, rho2_adj, aic, bic, 100*accuracy)
    LOGGER.info("[%s] Outputs -> %s", model_name, est_dir)


# ------------------------------ CLI ----------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Estimate Box–Cox MNL in Biogeme (leisure-only shifters).")
    p.add_argument("--genders", nargs="+", choices=("male", "female"), default=["male", "female"],
                   help="Gender-specific datasets to estimate (default: both).")
    p.add_argument("--pooled", action="store_true",
                   help="Pool male+female into one estimation and include an optional gender shifter.")
    p.add_argument("--labels", nargs="+", default=None,
                   help="Scenario labels to include (default: auto-detect from consumption_* columns).")
    p.add_argument("--include-ascs", action="store_true", help="Estimate ASCs (base alt fixed to 0).")
    p.add_argument("--gender-column", default="dgn", help="Gender column (1=female, 0=male).")
    p.add_argument("--output-dir", type=Path, default=reports_root() / "biogeme" / "boxcox_biogeme",
                   help="Output root directory.")
    p.add_argument("--data-dir", type=Path, default=data_root() / "processed" / "scenarios",
                   help="Input directory of wide datasets.")
    p.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"),
                   help="Logging verbosity.")
    return p.parse_args()

def load_wide_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return pd.read_parquet(path)

def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

    if args.pooled:
        male_df = load_wide_dataset(args.data_dir / "heads_wide_single_male_dcm.parquet")
        female_df = load_wide_dataset(args.data_dir / "heads_wide_single_female_dcm.parquet")
        # Add gender flags if missing
        if args.gender_column not in male_df.columns:
            male_df[args.gender_column] = 0
        if args.gender_column not in female_df.columns:
            female_df[args.gender_column] = 1

        labels_m = detect_labels(male_df, args.labels)
        labels_f = detect_labels(female_df, labels_m)
        if labels_m != labels_f:
            raise ValueError(f"Scenario labels differ male={labels_m} vs female={labels_f}")
        labels = labels_m

        common = sorted(set(male_df.columns).intersection(female_df.columns))
        pooled_df = pd.concat([male_df[common], female_df[common]], ignore_index=True)

        estimate_one(
            pooled_df, labels,
            gender_key="pooled",
            pooled=True,
            include_ascs=args.include_ascs,
            gender_column=args.gender_column,
            out_dir=args.output_dir,
        )
        return

    for g in args.genders:
        try:
            df = load_wide_dataset(args.data_dir / f"heads_wide_single_{g}_dcm.parquet")
            labels = detect_labels(df, args.labels)
            estimate_one(
                df, labels,
                gender_key=g,
                pooled=False,
                include_ascs=args.include_ascs,
                gender_column=args.gender_column,
                out_dir=args.output_dir,
            )
        except Exception as exc:
            LOGGER.error("[%s] Estimation failed: %s", g, exc, exc_info=True)

if __name__ == "__main__":
    main()
