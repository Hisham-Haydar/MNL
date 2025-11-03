#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple MLE for a translog labour-supply DCM (no Biogeme).

- Uses the same *wide* data structure as your existing pipeline.
- Utility per alternative a in {h0..h6}:
    U_a = α1·logy*_a + α2·logl*_a + α3·Leila_a + α4·Leila2_a
          + α5·lochi_a + α6·logdc_a
          + β1·(logy*_a)^2 + β2·(logl*_a)^2 + γ·logy*_a·logl*_a
          + ASC_a (if enabled; base ASC fixed at 0)
  where logy* = logy - C_LOGY - ln(y_scale) and logl* = logl - C_LOGL (if center/scale flags set)

- Optimizes the (negative) sum of individual log-likelihoods via L-BFGS-B.
- Exports CSV with estimates and (optional) robust SE.

This is intentionally compact and dependency-light.
"""

from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Dict, Tuple, List

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp

from path_helpers import data_root, reports_root

# ------------------------------
# Paths (adapt to your project)
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = data_root() / "processed" / "scenarios"
OUT_DIR = reports_root() / "mle_dcm"

DEFAULT_LABELS = ("h0","h1","h2","h3","h4","h5","h6")

# Human-readable labels/descriptions (mirrors dcm estimator)
PARAM_NAME_MAP: dict[str, str] = {
    "alpha_1": "beta_log_consumption",
    "alpha_2": "beta_log_leisure",
    "alpha_3": "beta_leila",
    "alpha_4": "beta_log2_leila",
    "alpha_5": "beta_log_childcare_cost",
    "alpha_6": "beta_log_disutility_cost",
    "beta_1": "beta_log2_consumption",
    "beta_2": "beta_log2_leisure",
    "gamma": "beta_logy_logl",
}

PARAM_DESC_MAP: dict[str, str] = {
    "alpha_1": "Slope on log(consumption): dU/d log y (linear term).",
    "alpha_2": "Slope on log(leisure): dU/d log l (linear term).",
    "alpha_3": "Effect of Leila (log l * log age) interaction.",
    "alpha_4": "Quadratic in Leila (curvature on log l * log age).",
    "alpha_5": "Effect of log(childcare cost) or related disutility shifter.",
    "alpha_6": "Effect of log(disutility cost) or travel/time cost proxy.",
    "beta_1": "Curvature of consumption: coefficient on (log y)^2.",
    "beta_2": "Curvature of leisure: coefficient on (log l)^2.",
    "gamma": "Interaction between consumption and leisure: log y * log l.",
    "__ASC__": "Alternative-specific constant for this scenario (captures baseline preference).",
}

# ------------------------------
# Utilities
# ------------------------------

def _detect_labels(df: pd.DataFrame) -> Tuple[str, ...]:
    labs = [c.split("logy_",1)[1] for c in df.columns if c.startswith("logy_")]
    return tuple(sorted(set(labs), key=lambda s:(len(s), s)))

def _actual_choice_logs(df: pd.DataFrame, labels: Sequence[str]) -> Tuple[pd.Series,pd.Series]:
    logy = pd.Series(np.nan, index=df.index, dtype=float)
    logl = pd.Series(np.nan, index=df.index, dtype=float)
    ac = df["actual_choice"]
    for lab in labels:
        m = (ac == lab)
        if m.any():
            logy.loc[m] = df.loc[m, f"logy_{lab}"]
            logl.loc[m] = df.loc[m, f"logl_{lab}"]
    return logy, logl

def _prep_df(df: pd.DataFrame, labels: Sequence[str]) -> pd.DataFrame:
    # Harmonize quadratic names => log2y_, log2l_
    ren = {}
    for lab in labels:
        if f"logy2_{lab}" in df.columns and f"log2y_{lab}" not in df.columns:
            ren[f"logy2_{lab}"] = f"log2y_{lab}"
        if f"logl2_{lab}" in df.columns and f"log2l_{lab}" not in df.columns:
            ren[f"logl2_{lab}"] = f"log2l_{lab}"
    if ren:
        df = df.rename(columns=ren)
    # Drop missing required columns
    req = []
    bases = ["logy","logl","Leila","Leila2","lochi","logdc","log2y","log2l","logyl"]
    for lab in labels:
        req.extend([f"{b}_{lab}" for b in bases])
    req.append("actual_choice")
    df = df.replace("", np.nan).dropna(subset=req).reset_index(drop=True)
    return df

# ------------------------------
# Model containers
# ------------------------------

@dataclass
class Spec:
    labels: Tuple[str, ...]
    include_ascs: bool = False
    center_logs: bool = False
    y_scale: float = 1.0
    C_LOGY: float = 0.0   # computed from actual choices if center_logs
    C_LOGL: float = 0.0

    @property
    def k_base(self) -> int:
        # α1..α6, β1, β2, γ => 9
        return 9

    @property
    def k_asc(self) -> int:
        # with ASCs: fix first to 0, estimate the rest
        return max(0, len(self.labels)-1) if self.include_ascs else 0

    @property
    def k_total(self) -> int:
        return self.k_base + self.k_asc


def pack_theta(theta_dict: Dict[str, float], spec: Spec) -> np.ndarray:
    keys = ["alpha_1","alpha_2","alpha_3","alpha_4","alpha_5","alpha_6",
            "beta_1","beta_2","gamma"]
    v = [theta_dict.get(k, 0.0) for k in keys]
    if spec.include_ascs:
        # ASC for labels[0] fixed at 0; pack the rest in order
        for lab in spec.labels[1:]:
            v.append(theta_dict.get(f"ASC_{lab}", 0.0))
    return np.array(v, dtype=float)

def unpack_theta(theta: np.ndarray, spec: Spec) -> Dict[str, float]:
    out = {}
    base = ["alpha_1","alpha_2","alpha_3","alpha_4","alpha_5","alpha_6","beta_1","beta_2","gamma"]
    for i, k in enumerate(base):
        out[k] = float(theta[i])
    idx = len(base)
    if spec.include_ascs:
        out[f"ASC_{spec.labels[0]}"] = 0.0
        for lab in spec.labels[1:]:
            out[f"ASC_{lab}"] = float(theta[idx]); idx += 1
    return out

# ------------------------------
# Likelihood building
# ------------------------------

def utilities_matrix(df: pd.DataFrame, spec: Spec, par: Dict[str,float]) -> np.ndarray:
    """
    Returns U (N x A) for A=len(labels).
    Applies centering & y-scale inside utility if requested.
    """
    N = len(df); A = len(spec.labels)
    U = np.zeros((N,A), dtype=float)

    # transformed logs
    ln_scale = 0.0 if np.isclose(spec.y_scale,1.0) else np.log(spec.y_scale)

    for j, lab in enumerate(spec.labels):
        logy = df[f"logy_{lab}"].to_numpy(float)
        logl = df[f"logl_{lab}"].to_numpy(float)
        if spec.center_logs or (not np.isclose(ln_scale,0.0)):
            logy_star = logy - (spec.C_LOGY + ln_scale)
            logl_star = logl - spec.C_LOGL
            log2y = logy_star * logy_star
            log2l = logl_star * logl_star
            logyl = logy_star * logl_star
            a1y = par["alpha_1"] * logy_star
            a2l = par["alpha_2"] * logl_star
        else:
            log2y = df[f"log2y_{lab}"].to_numpy(float)
            log2l = df[f"log2l_{lab}"].to_numpy(float)
            logyl = df[f"logyl_{lab}"].to_numpy(float)
            a1y = par["alpha_1"] * logy
            a2l = par["alpha_2"] * logl

        base = (
            a1y
            + a2l
            + par["alpha_3"] * df[f"Leila_{lab}"].to_numpy(float)
            + par["alpha_4"] * df[f"Leila2_{lab}"].to_numpy(float)
            + par["alpha_5"] * df[f"lochi_{lab}"].to_numpy(float)
            + par["alpha_6"] * df[f"logdc_{lab}"].to_numpy(float)
            + par["beta_1"] * log2y
            + par["beta_2"] * log2l
            + par["gamma"]  * logyl
        )
        asc = par.get(f"ASC_{lab}", 0.0)
        U[:, j] = base + asc

        # availability (if present) → knock out with -inf
        av_col = f"avail_{lab}"
        if av_col in df.columns:
            mask0 = (df[av_col].to_numpy() == 0)
            U[mask0, j] = -np.inf

    return U

def individual_loglike(df: pd.DataFrame, spec: Spec, theta: np.ndarray) -> np.ndarray:
    """Vector of individual log-likelihoods (length N)."""
    par = unpack_theta(theta, spec)
    U = utilities_matrix(df, spec, par)  # N x A
    # choice indices
    # map actual_choice string → column index in U
    lab2idx = {lab:j for j, lab in enumerate(spec.labels)}
    jstar = df["actual_choice"].map(lab2idx).to_numpy(int)
    # logit LL_i = U_i,j* - logsumexp(U_i,:)
    lse = logsumexp(U, axis=1)
    ll_i = U[np.arange(U.shape[0]), jstar] - lse
    return ll_i

def total_nll(df: pd.DataFrame, spec: Spec, theta: np.ndarray) -> float:
    """Negative total log-likelihood (for minimizer)."""
    ll_i = individual_loglike(df, spec, theta)
    # handle -inf (should not occur if each row has ≥1 available alt)
    if not np.isfinite(ll_i).all():
        return 1e12
    return -float(ll_i.sum())

# ------------------------------
# Estimation
# ------------------------------

def estimate_dcm(df: pd.DataFrame, spec: Spec, theta0: np.ndarray) -> dict:
    res = minimize(
        fun=lambda th: total_nll(df, spec, th),
        x0=theta0,
        method="L-BFGS-B",
        options=dict(maxiter=1000, disp=True),
    )
    out = {
        "success": bool(res.success),
        "message": str(res.message),
        "theta_hat": res.x.copy(),
        "nll": float(res.fun),
        "nit": int(res.nit),
        "status": int(res.status),
        "hess_inv": getattr(res, "hess_inv", None),
    }
    return out

def sandwich_se(df: pd.DataFrame, spec: Spec, theta_hat: np.ndarray) -> Tuple[np.ndarray,np.ndarray]:
    """
    Very light-weight robust SE:
    - Approximates Hessian by finite-diff of gradient (via autograd-like trick w/ eps).
    - Outer product of gradients for meat. (Crude but useful baseline.)
    """
    eps = 1e-5
    k = len(theta_hat)
    # Score matrix (N x k)
    # central finite diff gradient per obs
    ll0 = individual_loglike(df, spec, theta_hat)  # N
    S = np.zeros((len(ll0), k))
    for j in range(k):
        ej = np.zeros(k); ej[j] = eps
        llp = individual_loglike(df, spec, theta_hat + ej)
        llm = individual_loglike(df, spec, theta_hat - ej)
        S[:, j] = (llp - llm) / (2*eps)
    # Meat = sum_i s_i s_i'
    Meat = S.T @ S
    # Hessian (numerical, total LL)
    H = np.zeros((k,k))
    f0 = -ll0.sum()
    for j in range(k):
        ej = np.zeros(k); ej[j] = eps
        for m in range(k):
            em = np.zeros(k); em[m] = eps
            fpp = total_nll(df, spec, theta_hat + ej + em)
            fpm = total_nll(df, spec, theta_hat + ej - em)
            fmp = total_nll(df, spec, theta_hat - ej + em)
            fmm = total_nll(df, spec, theta_hat - ej - em)
            H[j,m] = (fpp - fpm - fmp + fmm) / (4*eps*eps)
    # Sandwich variance
    try:
        Hinv = np.linalg.inv(H)
        V = Hinv @ Meat @ Hinv
        se = np.sqrt(np.clip(np.diag(V), 0, np.inf))
    except np.linalg.LinAlgError:
        V = np.full_like(H, np.nan)
        se = np.full(k, np.nan)
    return V, se

# ------------------------------
# CLI
# ------------------------------

def main():
    ap = argparse.ArgumentParser(description="MLE for translog labour-supply DCM (no Biogeme).")
    ap.add_argument("--gender", choices=("male","female"), required=True)
    ap.add_argument("--labels", nargs="+", default=list(DEFAULT_LABELS))
    ap.add_argument("--include-ascs", action="store_true")
    ap.add_argument("--center-logs", action="store_true")
    ap.add_argument("--y-scale", type=float, default=1.0)
    ap.add_argument("--robust-se", action="store_true", help="Compute sandwich SE (slow).")
    args = ap.parse_args()

    if args.y_scale <= 0:
        raise ValueError("--y-scale must be positive.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    path = DATA_DIR / f"heads_wide_single_{args.gender}_dcm.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_parquet(path)
    labels = tuple(args.labels) if args.labels else _detect_labels(df)
    df = _prep_df(df, labels)

    # Centering constants (from actual choices)
    logy_act, logl_act = _actual_choice_logs(df, labels)
    C_LOGY = float(np.nanmean(logy_act)) if args.center_logs else 0.0
    C_LOGL = float(np.nanmean(logl_act)) if args.center_logs else 0.0

    spec = Spec(
        labels=labels,
        include_ascs=args.include_ascs,
        center_logs=args.center_logs,
        y_scale=args.y_scale,
        C_LOGY=C_LOGY,
        C_LOGL=C_LOGL,
    )

    variant_tag = "ascsON" if spec.include_ascs else "ascsOFF"
    if spec.center_logs:
        variant_tag += "_center"
    if not np.isclose(spec.y_scale, 1.0):
        variant_tag += f"_ys{int(spec.y_scale)}"
    variant_dir = OUT_DIR / f"{args.gender}_{variant_tag}"
    variant_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"mle_{args.gender}_{variant_tag}"

    # Init: zeros is fine; small jitter helps curvature
    theta0_dict = {
        "alpha_1": 0.0, "alpha_2": 0.0, "alpha_3": 0.0, "alpha_4": 0.0,
        "alpha_5": 0.0, "alpha_6": 0.0, "beta_1": 0.0, "beta_2": 0.0, "gamma": 0.0
    }
    if spec.include_ascs:
        for lab in spec.labels[1:]:
            theta0_dict[f"ASC_{lab}"] = 0.0
    theta0 = pack_theta(theta0_dict, spec)

    # Estimate
    res = estimate_dcm(df, spec, theta0)
    theta_hat = res["theta_hat"]
    par_hat = unpack_theta(theta_hat, spec)

    # Metrics
    ll_star = -res["nll"]
    n = len(df)
    k = len(theta_hat)
    # Null LL (all utilities = 0 ⇒ uniform over available alts row by row)
    # (exact uniform only if all avails = 1; otherwise use per-row count)
    A_i = np.zeros(n, dtype=int)
    for i in range(n):
        cnt = 0
        for lab in labels:
            av = df.get(f"avail_{lab}", None)
            cnt += 1 if (av is None or av.iloc[i] != 0) else 0
        A_i[i] = max(cnt, 1)
    ll0 = -np.log(A_i).sum()
    rho2 = 1 - ll_star/ll0 if ll0 != 0 else np.nan
    rho2_adj = 1 - (ll_star - k)/ll0 if ll0 != 0 else np.nan
    aic = 2*k - 2*ll_star
    bic = k*np.log(max(n,1)) - 2*ll_star

    # (Optional) robust SE
    V, se = (np.full((k,k), np.nan), np.full(k, np.nan))
    if args.robust_se:
        V, se = sandwich_se(df, spec, theta_hat)

    # Save CSV
    rows = []
    order = ["alpha_1","alpha_2","alpha_3","alpha_4","alpha_5","alpha_6","beta_1","beta_2","gamma"]
    if spec.include_ascs:
        order += [f"ASC_{lab}" for lab in spec.labels]  # includes base ASC=0 reported
    for idx, name in enumerate(order):
        val = par_hat.get(name, 0.0)
        # base ASC fixed = 0, no SE
        if name == f"ASC_{spec.labels[0]}":
            rows.append(dict(Parameter=name, Value=0.0, StdErr=np.nan, t=np.nan))
        else:
            j = idx if name != f"ASC_{spec.labels[0]}" else None
            serr = (se[j] if (args.robust_se and j is not None and j < len(se)) else np.nan)
            tval = (val/serr) if (serr and np.isfinite(serr) and serr>0) else np.nan
            rows.append(dict(Parameter=name, Value=val, StdErr=serr, t=tval))

    out_csv = variant_dir / f"{base_name}_parameters.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)

    meta = {
        "include_ascs": bool(spec.include_ascs),
        "center_logs": bool(spec.center_logs),
        "y_scale": float(spec.y_scale),
        "C_LOGY": float(spec.C_LOGY if spec.center_logs else 0.0),
        "C_LOGL": float(spec.C_LOGL if spec.center_logs else 0.0),
        "LN_SCALE": float(np.log(spec.y_scale) if not np.isclose(spec.y_scale, 1.0) else 0.0),
        "labels": list(spec.labels),
        "estimator": "mle",
    }
    meta_path = variant_dir / f"{base_name}_transform_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        label_map_path = variant_dir / f"{base_name}_param_labels.json"
        desc_map_path = variant_dir / f"{base_name}_param_descriptions.json"
        label_map_path.write_text(json.dumps(PARAM_NAME_MAP, indent=2), encoding="utf-8")
        desc_map = PARAM_DESC_MAP.copy()
        if spec.include_ascs:
            for lab in spec.labels:
                key = f"ASC_{lab}"
                desc_map[key] = PARAM_DESC_MAP.get(
                    "__ASC__", "Alternative-specific constant."
                )
        desc_map_path.write_text(json.dumps(desc_map, indent=2), encoding="utf-8")
    except Exception:
        pass

    # Confusion (argmax U)
    Uhat = utilities_matrix(df, spec, par_hat)
    pred_idx = np.argmax(Uhat, axis=1)
    lab_by_idx = list(spec.labels)
    pred_lab = pd.Series([lab_by_idx[j] for j in pred_idx], index=df.index, name="predicted_choice")
    cm = pd.crosstab(df["actual_choice"], pred_lab, margins=True, margins_name="Total")
    acc = (pred_lab == df["actual_choice"]).mean()

    print("\n=== Estimation summary (no Biogeme) ===")
    print(f"success={res['success']}  status={res['status']}  iters={res['nit']}")
    print(f"LL*={ll_star:.3f}  LL0={ll0:.3f}  rho2={rho2:.4f}  rho2_adj={rho2_adj:.4f}")
    print(f"AIC={aic:.1f}  BIC={bic:.1f}  N={n}  K={k}")
    print(f"CSV: {out_csv}")
    print(f"Meta: {meta_path}")
    print("\nConfusion matrix:")
    print(cm)
    print(f"Accuracy: {acc:.2%}")

if __name__ == "__main__":
    main()
