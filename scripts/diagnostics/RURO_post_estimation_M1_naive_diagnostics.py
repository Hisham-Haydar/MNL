"""
RURO occ M1-naive supplementary diagnostics.

Four diagnostics for the M1-naive extended opportunity block:

  D1. Joint Wald test  H0: beta_E_drgn2 = ... = beta_E_drgn8 = 0  (7 d.f.)
  D2. 7x7 region covariance / correlation sub-block with collinearity flags
  D3. 9x9 GSUR+educH+region Hessian sub-block eigenvalues (M1-naive extension
      of the M1-clean 8x8 block — adds beta_E_educH)
  D4. beta_E_educH cross-correlations with beta_E_gsur and beta_E_drgn2..8

Research-only script.  Classification: scripts/diagnostics/, not package-core.
See docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md.

Usage
-----
  python scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py
      --params-csv   <path to params.csv from post-estimation>
      --results-json <path to estimation_results.json>
      --mnl-base     <path prefix for __singles.parquet / __couples.parquet>
      --spec         <path to estimation_spec_ruro_occ_M1_naive.yaml>
      --output-dir   <Results/ or wherever>
      [--eps FLOAT]  (finite-difference step; default 1e-5)

Outputs
-------
  <output-dir>/RURO_occ_M1_naive_supplementary_diagnostics_v1.md
  <output-dir>/RURO_occ_M1_naive_vcv_region_block_<UTC>.csv
  <output-dir>/RURO_occ_M1_naive_vcv_educ_gsur_region_block_<UTC>.csv
  <output-dir>/RURO_occ_M1_naive_hessian_gsur_educ_region_block_<UTC>.csv
"""

import argparse
import csv
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

# ---------------------------------------------------------------------------
# Path setup: scripts/diagnostics -> add scripts/enhanced for local modules
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_ENHANCED_DIR = _SCRIPT_DIR.parent / "enhanced"
for _p in (_SCRIPT_DIR, _ENHANCED_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from estimation_spec_parser import parse_specification
from estimation_engine import compute_gradient_joint
from estimation_utils import (
    precompute_data_singles,
    precompute_data_couples,
    load_and_validate_mnl_data,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Parameter name sets (order matters: must match params.csv)
# ---------------------------------------------------------------------------
REGION_PARAMS = [
    "joint.beta_E_drgn2",
    "joint.beta_E_drgn3",
    "joint.beta_E_drgn4",
    "joint.beta_E_drgn5",
    "joint.beta_E_drgn6",
    "joint.beta_E_drgn7",
    "joint.beta_E_drgn8",
]

# 9-param block: GSUR + educH + 7 region dummies
GSUR_EDUC_REGION_PARAMS = (
    ["joint.beta_E_gsur", "joint.beta_E_educH"] + REGION_PARAMS
)

# D4: educH cross-partners
EDUC_PARAMS = ["joint.beta_E_educH"]
EDUC_CROSS_PARAMS = ["joint.beta_E_gsur"] + REGION_PARAMS  # 8 partners


# ===========================================================================
# Shared utilities (same logic as M1-clean script; kept local for isolation)
# ===========================================================================

def compute_numerical_hessian(
    theta: np.ndarray,
    grad_func,
    free_idx: np.ndarray,
    eps: float = 1e-5,
) -> np.ndarray:
    n_free = len(free_idx)
    H = np.zeros((n_free, n_free))
    for col_idx, i in enumerate(free_idx):
        theta_p = theta.copy(); theta_p[i] += eps
        theta_m = theta.copy(); theta_m[i] -= eps
        g_p = grad_func(theta_p)
        g_m = grad_func(theta_m)
        H[:, col_idx] = (g_p[free_idx] - g_m[free_idx]) / (2.0 * eps)
        if (col_idx + 1) % 10 == 0:
            logger.info("  Hessian column %d / %d", col_idx + 1, n_free)
    return 0.5 * (H + H.T)


def write_matrix_csv(matrix: np.ndarray, param_names: list, path: Path):
    short = [p.replace("joint.", "") for p in param_names]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + short)
        for i, row in enumerate(matrix):
            w.writerow([short[i]] + [f"{v:.8e}" for v in row])
    logger.info("Matrix CSV: %s", path)


def _fmt(x, d=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{x:.{d}f}"


# ===========================================================================
# D1 — Joint Wald test
# ===========================================================================

def diagnostic_d1_wald(theta, vcv_full, param_names, region_params,
                        orig_se=None, orig_pval=None):
    idx = [param_names.index(p) for p in region_params]
    theta_r = theta[idx]
    vcv_r = vcv_full[np.ix_(idx, idx)]
    try:
        W = float(theta_r @ np.linalg.inv(vcv_r) @ theta_r)
    except np.linalg.LinAlgError:
        W = float(theta_r @ np.linalg.pinv(vcv_r, rcond=1e-10) @ theta_r)
    df = len(region_params)
    pval = float(1.0 - chi2.cdf(W, df))

    se_r = orig_se[idx] if orig_se is not None else np.sqrt(np.diag(vcv_r))
    p_ind = orig_pval[idx] if orig_pval is not None else (
        1.0 - chi2.cdf((theta_r / se_r) ** 2, 1))
    z_r = theta_r / se_r

    return {
        "W": W, "df": df, "pval": pval,
        "theta_r": theta_r.tolist(), "se_r": se_r.tolist(),
        "z_r": z_r.tolist(),
        "p_ind": p_ind.tolist() if hasattr(p_ind, "tolist") else list(p_ind),
        "params": region_params,
        "se_source": "original" if orig_se is not None else "recomputed",
    }


# ===========================================================================
# D2 — 7×7 region VCV block
# ===========================================================================

def diagnostic_d2_region_vcv(vcv_full, param_names, region_params, flag_thr=0.7):
    idx = [param_names.index(p) for p in region_params]
    vcv_r = vcv_full[np.ix_(idx, idx)]
    se_r = np.sqrt(np.diag(vcv_r))
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = np.outer(se_r, se_r)
        corr_r = np.where(denom > 0, vcv_r / denom, np.nan)
    np.fill_diagonal(corr_r, 1.0)
    flags = [
        {"pi": region_params[i], "pj": region_params[j], "corr": float(corr_r[i, j])}
        for i in range(len(region_params))
        for j in range(i + 1, len(region_params))
        if abs(corr_r[i, j]) > flag_thr
    ]
    return {"vcv": vcv_r, "corr": corr_r, "se": se_r, "flags": flags, "params": region_params}


# ===========================================================================
# D3 — 9×9 GSUR+educH+region Hessian sub-block
# ===========================================================================

def diagnostic_d3_hessian_subblock(H_free, free_idx, param_names, block_params):
    full_to_free = {fi: i for i, fi in enumerate(free_idx)}
    sub_idx = []
    missing = []
    for pname in block_params:
        fi = param_names.index(pname)
        if fi in full_to_free:
            sub_idx.append(full_to_free[fi])
        else:
            missing.append(pname)
    if missing:
        logger.warning("Parameters not in free set (fixed at bounds): %s", missing)
    H_sub = H_free[np.ix_(sub_idx, sub_idx)]
    eigs = np.linalg.eigvalsh(H_sub)
    cond = float(np.linalg.cond(H_sub)) if len(sub_idx) > 1 else float("nan")
    return {
        "eigs": eigs.tolist(), "n_neg": int((eigs < 0).sum()),
        "min_eig": float(eigs.min()), "max_eig": float(eigs.max()),
        "cond": cond, "H_sub": H_sub, "params": block_params, "missing": missing,
    }


# ===========================================================================
# D4 — educH cross-correlations
# ===========================================================================

def diagnostic_d4_educ_cross_corr(vcv_full, param_names, educ_params, cross_params):
    """
    Extract correlations between each educH param and each cross_param.
    Returns a list of dicts {pi, pj, cov, se_i, se_j, corr}.
    """
    results = []
    for ep in educ_params:
        ei = param_names.index(ep)
        se_e = float(np.sqrt(vcv_full[ei, ei]))
        for cp in cross_params:
            ci = param_names.index(cp)
            se_c = float(np.sqrt(vcv_full[ci, ci]))
            cov = float(vcv_full[ei, ci])
            denom = se_e * se_c
            corr = cov / denom if denom > 0 and np.isfinite(denom) else float("nan")
            results.append({
                "pi": ep, "pj": cp,
                "cov": cov, "se_i": se_e, "se_j": se_c, "corr": corr,
            })
    return results


# ===========================================================================
# Markdown report writer
# ===========================================================================

def write_report(
    d1, d2, d3, d4,
    spec_name, run_folder, params_csv, mnl_base, eps,
    hessian_cond, n_neg_full, output_path,
    vcv_csv, vcv_educ_csv, hessian_csv,
    m1clean_d1_W=28.18, m1clean_d1_p=0.000204,
    m1clean_d3_min_eig=5.768, m1clean_d3_n_neg=0,
):
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = []

    L += [
        "# RURO occ M1-naive Supplementary Diagnostics v1",
        "",
        f"Date: {utc}  ",
        f"Spec: `{spec_name}`  ",
        f"Estimation run: `{run_folder}`  ",
        f"Parameters source: `{params_csv}`  ",
        f"MNL base: `{mnl_base}`  ",
        f"Hessian step (eps): {eps}",
        "",
        "---",
        "",
        "## Overview",
        "",
        "This report contains four diagnostics for the M1-naive extended opportunity",
        "block. The full 54×54 numerical Hessian was recomputed via central-difference",
        "finite differences on the joint gradient function.",
        "",
        f"Full-Hessian condition number (recomputed): {hessian_cond:.4e}  ",
        f"Negative eigenvalues in full Hessian: {n_neg_full}",
        "",
        "Comparison reference throughout: `ruro_occ_M1_clean`",
        "(M1-clean supplementary diagnostics: `Results/P3a/single_year_baseline/M1/RURO_occ_M1_clean_supplementary_diagnostics_v1.md`)",
        "",
        "---",
        "",
        "## D1 — Joint Wald test: β_E_drgn2 = … = β_E_drgn8 = 0",
        "",
        "**H₀**: β_E_drgn2 = β_E_drgn3 = β_E_drgn4 = β_E_drgn5 =",
        "       β_E_drgn6 = β_E_drgn7 = β_E_drgn8 = 0",
        "",
        f"**Test statistic**: W = {_fmt(d1['W'], 4)}",
        f"**Degrees of freedom**: {d1['df']}",
        f"**p-value**: {_fmt(d1['pval'], 6)}",
        "",
    ]

    if d1['pval'] < 0.001:
        interp = f"W = {_fmt(d1['W'], 2)} on {d1['df']} d.f. — highly significant (p < 0.001)."
    elif d1['pval'] < 0.05:
        interp = f"W = {_fmt(d1['W'], 2)} on {d1['df']} d.f. — significant at 5%."
    else:
        interp = f"W = {_fmt(d1['W'], 2)} on {d1['df']} d.f. — NOT significant at 5% (p = {_fmt(d1['pval'], 4)})."

    L += [
        f"**Interpretation**: {interp}",
        "",
        f"**Comparison to M1-clean**: M1-clean Wald = {m1clean_d1_W:.2f}, p = {m1clean_d1_p:.6f}.",
        f"M1-naive Wald = {_fmt(d1['W'], 2)}, p = {_fmt(d1['pval'], 6)}.",
        "",
        "### Individual region parameter table (SE source: " + d1['se_source'] + ")",
        "",
        "| Parameter | Estimate | SE | z | p | Sig | M1-clean p |",
        "|---|---|---|---|---|---|---|",
    ]

    # M1-clean individual p-values for comparison column
    m1clean_p = {
        "joint.beta_E_drgn2": 0.0026,
        "joint.beta_E_drgn3": 0.0394,
        "joint.beta_E_drgn4": 0.0001,
        "joint.beta_E_drgn5": 0.0045,
        "joint.beta_E_drgn6": 0.0192,
        "joint.beta_E_drgn7": 0.0399,
        "joint.beta_E_drgn8": 0.0974,
    }
    for i, pname in enumerate(d1["params"]):
        short = pname.replace("joint.", "")
        est = d1["theta_r"][i]; se = d1["se_r"][i]
        z = d1["z_r"][i]; p = d1["p_ind"][i]
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ("." if p < 0.10 else "")))
        m1p = m1clean_p.get(pname, float("nan"))
        L.append(
            f"| `{short}` | {_fmt(est)} | {_fmt(se)} | {_fmt(z)} | {_fmt(p, 4)} | {sig} | {_fmt(m1p, 4)} |"
        )

    L += [
        "",
        "*: p<0.05  **: p<0.01  ***: p<0.001  .: p<0.10",
        "",
        "---",
        "",
        "## D2 — 7×7 region covariance / correlation sub-block",
        "",
        "Extracted from the full 54×54 VCV (pseudo-inverse of the Hessian).",
        f"Raw VCV saved to: `{vcv_csv.name}`",
        "",
        "### Standard errors (M1-naive vs M1-clean)",
        "",
        "| Parameter | M1-naive SE | M1-clean SE | Δ |",
        "|---|---|---|---|",
    ]

    m1clean_se = {
        "joint.beta_E_drgn2": 0.2664,
        "joint.beta_E_drgn3": 0.3186,
        "joint.beta_E_drgn4": 0.4100,
        "joint.beta_E_drgn5": 0.2722,
        "joint.beta_E_drgn6": 0.3275,
        "joint.beta_E_drgn7": 0.3118,
        "joint.beta_E_drgn8": 0.2794,
    }
    for i, pname in enumerate(d2["params"]):
        short = pname.replace("joint.", "")
        se_n = d2["se"][i]
        se_c = m1clean_se.get(pname, float("nan"))
        delta = se_n - se_c if np.isfinite(se_c) else float("nan")
        L.append(f"| `{short}` | {_fmt(se_n)} | {_fmt(se_c)} | {_fmt(delta, 4)} |")

    L += [
        "",
        "### Correlation matrix (7×7)",
        "",
    ]
    short_names = [p.replace("joint.beta_E_", "") for p in d2["params"]]
    L.append("| " + " | ".join([""] + short_names) + " |")
    L.append("|" + "---|" * (len(short_names) + 1))
    for i in range(len(d2["params"])):
        row_cells = [f"`{short_names[i]}`"]
        for j in range(len(d2["params"])):
            v = d2["corr"][i, j]
            cell = _fmt(v, 3)
            if i != j and abs(v) > 0.7:
                cell = f"**{cell}**"
            row_cells.append(cell)
        L.append("| " + " | ".join(row_cells) + " |")

    if d2["flags"]:
        L += ["", f"**High-correlation flags** (|corr| > 0.70): {len(d2['flags'])} pair(s)", ""]
        for fl in d2["flags"]:
            pi = fl["pi"].replace("joint.", ""); pj = fl["pj"].replace("joint.", "")
            L.append(f"- `{pi}` × `{pj}`: corr = {_fmt(fl['corr'], 3)}")
    else:
        L += ["", "No high-correlation flags (all |corr| ≤ 0.70)."]

    L += [
        "",
        "**Comparison to M1-clean**: M1-clean had maximum pairwise region correlation ≈ 0.191.",
        "By construction (households in exactly one NUTS-1 region), cross-second-derivatives",
        "of drgn_i × drgn_j in the Hessian are zero; off-diagonal elements arise only through",
        "shared dependence on other parameters.",
        "",
        "---",
        "",
        "## D3 — 9×9 GSUR+educH+region Hessian sub-block eigenvalues",
        "",
        "Sub-block spanning {β_E_gsur, β_E_educH, β_E_drgn2, …, β_E_drgn8} extracted",
        "from the full numerical Hessian. This is the M1-naive extension of the",
        "M1-clean 8×8 {β_E_gsur, β_E_drgn2, …, β_E_drgn8} block.",
        f"Raw sub-matrix saved to: `{hessian_csv.name}`",
        "",
    ]

    if d3["missing"]:
        L += [
            f"**WARNING**: {len(d3['missing'])} parameter(s) were fixed at bounds and",
            f"excluded from the Hessian computation: {d3['missing']}.",
            f"The sub-block is {len(d3['params']) - len(d3['missing'])}×{len(d3['params']) - len(d3['missing'])} rather than 9×9.",
            "",
        ]

    L += [
        f"**Sub-block condition number**: {_fmt(d3['cond'], 4) if np.isfinite(d3['cond']) else 'NA'}",
        "",
        "**Eigenvalues** (ascending):",
        "",
        "| # | Eigenvalue | Sign |",
        "|---|---|---|",
    ]
    for idx_e, ev in enumerate(sorted(d3["eigs"])):
        sign = "negative" if ev < 0 else ("near-zero" if abs(ev) < 1e-4 else "positive")
        L.append(f"| {idx_e + 1} | {ev:.6e} | {sign} |")

    L += [
        "",
        f"Negative eigenvalues: {d3['n_neg']}  ",
        f"Minimum eigenvalue: {d3['min_eig']:.6e}  ",
        f"Maximum eigenvalue: {d3['max_eig']:.6e}",
        "",
    ]

    if d3["n_neg"] == 0:
        d3_interp = (
            "All eigenvalues of the 9×9 GSUR+educH+region Hessian sub-block are positive; "
            "the sub-block is locally convex and well-identified."
        )
    else:
        d3_interp = (
            f"{d3['n_neg']} negative eigenvalue(s) in the 9×9 GSUR+educH+region sub-block — "
            "saddle-point direction present; sub-block is NOT locally convex."
        )
    L.append(f"**Interpretation**: {d3_interp}")
    L += [
        "",
        f"**Comparison to M1-clean 8×8 block**: M1-clean minimum eigenvalue = {m1clean_d3_min_eig:.4f} "
        f"(all positive, {m1clean_d3_n_neg} negative). "
        f"M1-naive 9×9 minimum eigenvalue = {d3['min_eig']:.6e}.",
        "",
        "---",
        "",
        "## D4 — β_E_educH cross-correlations with GSUR and region parameters",
        "",
        "Extracted from the 54×54 VCV (pseudo-inverse). Reports the off-diagonal",
        "covariance and correlation between β_E_educH and each of β_E_gsur and",
        "β_E_drgn2 through β_E_drgn8.",
        f"Full educH+GSUR+region VCV block saved to: `{vcv_educ_csv.name}`",
        "",
        "| β_E_educH ↔ | Cov | SE(educH) | SE(partner) | Corr |",
        "|---|---|---|---|---|",
    ]
    for r in d4:
        pj_short = r["pj"].replace("joint.", "")
        L.append(
            f"| `{pj_short}` | {r['cov']:.4e} | {_fmt(r['se_i'])} | {_fmt(r['se_j'])} | {_fmt(r['corr'], 4)} |"
        )

    # Compute summary stats for narrative
    corrs = [r["corr"] for r in d4 if np.isfinite(r["corr"])]
    max_abs_corr = max(abs(c) for c in corrs) if corrs else float("nan")
    gsur_corr = next((r["corr"] for r in d4 if "gsur" in r["pj"]), float("nan"))

    L += [
        "",
        f"Maximum |corr| between β_E_educH and any region/GSUR partner: {_fmt(max_abs_corr, 4)}",
        f"Correlation β_E_educH ↔ β_E_gsur: {_fmt(gsur_corr, 4)}",
        "",
        "**Mechanical interpretation**: A large |corr| between β_E_educH and β_E_gsur would",
        "indicate that education mainly reallocates explanatory weight from GSUR rather than",
        "contributing distinct variation. A large |corr| with a specific region dummy would",
        "indicate that the education effect is concentrated in that region's households.",
        "Correlations ≤ 0.70 in absolute value are taken as evidence of distinct variation.",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    wald_s = (
        f"D1 (Wald, 7 d.f.): W = {_fmt(d1['W'], 2)}, p = {_fmt(d1['pval'], 6)} — "
        + ("jointly significant (p < 0.001)." if d1['pval'] < 0.001 else
           f"significant at 5% (p = {_fmt(d1['pval'], 4)})." if d1['pval'] < 0.05 else
           f"NOT significant at 5% (p = {_fmt(d1['pval'], 4)}).")
        + f" cf. M1-clean: W = {m1clean_d1_W:.2f}, p = {m1clean_d1_p:.6f}."
    )
    coll_s = (
        f"D2 (region collinearity): {len(d2['flags'])} high-correlation pair(s) flagged (threshold 0.70)."
        if d2["flags"] else
        "D2 (region collinearity): no high-correlation pairs (all |corr| ≤ 0.70)."
    )
    d3_s = (
        f"D3 (9×9 GSUR+educH+region sub-block): {d3['n_neg']} negative eigenvalue(s); "
        + ("sub-block locally convex." if d3["n_neg"] == 0 else "sub-block NOT locally convex.")
        + f" Min eigenvalue = {d3['min_eig']:.4e}. cf. M1-clean 8×8 min = {m1clean_d3_min_eig:.4f}."
    )
    d4_s = (
        f"D4 (β_E_educH cross-correlations): max |corr| with GSUR/region partners = {_fmt(max_abs_corr, 4)}; "
        f"β_E_educH ↔ β_E_gsur = {_fmt(gsur_corr, 4)}."
    )

    L += [
        f"- {wald_s}",
        f"- {coll_s}",
        f"- {d3_s}",
        f"- {d4_s}",
        "",
        "---",
        "",
        "*Generated by `scripts/diagnostics/RURO_post_estimation_M1_naive_diagnostics.py`*",
        "*Research-only: see `docs/France_case/P3a/execution_logs/single_year_baseline/M1/RURO_post_estimation_M1_naive_diagnostics_implementation_report_v1.md`*",
    ]

    output_path.write_text("\n".join(L), encoding="utf-8")
    logger.info("Report written: %s", output_path)


# ===========================================================================
# Main
# ===========================================================================

def parse_args():
    p = argparse.ArgumentParser(description="M1-naive supplementary diagnostics")
    p.add_argument("--params-csv", required=True)
    p.add_argument("--results-json", required=True)
    p.add_argument("--mnl-base", required=True)
    p.add_argument("--spec", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--eps", type=float, default=1e-5)
    return p.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    utc_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 1. Load parameters
    logger.info("Loading parameters from %s", args.params_csv)
    params_df = pd.read_csv(args.params_csv)
    param_names = params_df["parameter"].tolist()
    theta = params_df["estimate"].values.astype(float)
    logger.info("Loaded %d parameters", len(param_names))

    for rp in GSUR_EDUC_REGION_PARAMS:
        if rp not in param_names:
            logger.error("Required parameter '%s' missing from params.csv", rp)
            sys.exit(1)

    # 2. Parse spec and load data
    orig_dir = Path.cwd()
    try:
        os.chdir(_ENHANCED_DIR)
        spec = parse_specification(Path(args.spec))
    finally:
        os.chdir(orig_dir)
    logger.info("Spec: %s (%d params)", spec.name, len(spec.all_param_names))

    mnl_base = Path(args.mnl_base)
    singles_path = Path(str(mnl_base) + "__singles.parquet")
    couples_path = Path(str(mnl_base) + "__couples.parquet")
    metadata_path = Path(str(mnl_base) + "__mnlmeta.json")

    logger.info("Loading MNL data...")
    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=singles_path,
        couples_path=couples_path if couples_path.exists() else None,
        metadata_path=metadata_path,
        strict_validation=False,
    )

    # Extra precompute vars from spec
    extra_set = set()
    for sh in getattr(spec, "market_opportunity_shifters", []):
        if isinstance(sh, dict):
            if sh.get("variable"):
                extra_set.add(sh["variable"].strip())
            for iv in (sh.get("interaction") or []):
                if iv and iv != "working":
                    extra_set.add(iv.strip())
    for sh in getattr(spec, "utility_leisure_shifters", []):
        if isinstance(sh, dict) and sh.get("variable"):
            extra_set.add(sh["variable"].strip())
    extra_vars = sorted(extra_set)
    logger.info("Extra precompute vars: %s", extra_vars)

    include_wage = spec.wage_spec in ("vw", "loc_empirical")
    include_loc = spec.wage_spec == "loc_empirical"

    df_sm = df_singles[df_singles["dgn"] == 1]
    df_sf = df_singles[df_singles["dgn"] == 0]

    logger.info("Precomputing singles male (%d obs)...", len(df_sm))
    data_sm = precompute_data_singles(df_sm, metadata, is_male=True,
                                      include_wage_vars=include_wage,
                                      include_loc_vars=include_loc,
                                      include_extra_vars=extra_vars)
    logger.info("Precomputing singles female (%d obs)...", len(df_sf))
    data_sf = precompute_data_singles(df_sf, metadata, is_male=False,
                                      include_wage_vars=include_wage,
                                      include_loc_vars=include_loc,
                                      include_extra_vars=extra_vars)
    assert df_couples is not None
    logger.info("Precomputing couples (%d obs)...", len(df_couples))
    data_cou = precompute_data_couples(df_couples, metadata,
                                       include_wage_vars=include_wage,
                                       include_loc_vars=include_loc,
                                       include_extra_vars=extra_vars)

    # 3. Gradient function
    def grad_func(th):
        return compute_gradient_joint(th, data_sm, data_sf, data_cou, spec)

    # 4. Free parameter mask
    bounds = spec.get_bounds_tuple()
    bound_tol = 1e-6
    free_mask = np.ones(len(theta), dtype=bool)
    for i, (lb, ub) in enumerate(bounds):
        if lb is None and ub is None:
            continue
        if lb is not None and ub is not None and (ub - lb) <= bound_tol:
            free_mask[i] = False
            continue
        if lb is not None and abs(theta[i] - lb) <= bound_tol:
            free_mask[i] = False
        elif ub is not None and abs(theta[i] - ub) <= bound_tol:
            free_mask[i] = False

    free_idx = np.where(free_mask)[0]
    logger.info("Free params: %d / %d", len(free_idx), len(theta))

    # 5. Numerical Hessian
    logger.info("Computing %dx%d Hessian (eps=%.1e)...", len(free_idx), len(free_idx), args.eps)
    H_free = compute_numerical_hessian(theta, grad_func, free_idx, eps=args.eps)
    logger.info("Hessian done.")

    eigs_full = np.linalg.eigvalsh(H_free)
    n_neg_full = int((eigs_full < 0).sum())
    cond_full = float(np.linalg.cond(H_free))
    logger.info("Full Hessian: cond = %.4e, n_neg = %d", cond_full, n_neg_full)

    # 6. VCV
    logger.info("Computing VCV (pinv, rcond=1e-10)...")
    vcv_free = np.linalg.pinv(H_free, rcond=1e-10)
    n_params = len(theta)
    vcv_full = np.full((n_params, n_params), np.nan)
    vcv_full[np.ix_(free_idx, free_idx)] = vcv_free

    # 7. Original SEs / p-values from params.csv
    orig_se = params_df["std_error"].values.astype(float)
    orig_pval = params_df["p_value"].values.astype(float)

    # 8. Run diagnostics
    logger.info("D1: Wald test...")
    d1 = diagnostic_d1_wald(theta, vcv_full, param_names, REGION_PARAMS,
                             orig_se=orig_se, orig_pval=orig_pval)
    logger.info("W = %.4f, df = %d, p = %.6f", d1["W"], d1["df"], d1["pval"])

    logger.info("D2: region VCV block...")
    d2 = diagnostic_d2_region_vcv(vcv_full, param_names, REGION_PARAMS)
    logger.info("D2: %d high-corr flags", len(d2["flags"]))

    logger.info("D3: 9x9 Hessian sub-block...")
    d3 = diagnostic_d3_hessian_subblock(H_free, free_idx, param_names, GSUR_EDUC_REGION_PARAMS)
    logger.info("D3: min_eig = %.4e, n_neg = %d, cond = %.4e", d3["min_eig"], d3["n_neg"], d3["cond"])

    logger.info("D4: educH cross-correlations...")
    d4 = diagnostic_d4_educ_cross_corr(vcv_full, param_names, EDUC_PARAMS, EDUC_CROSS_PARAMS)

    # 9. Save CSVs
    vcv_csv = output_dir / f"RURO_occ_M1_naive_vcv_region_block_{utc_tag}.csv"
    write_matrix_csv(d2["vcv"], REGION_PARAMS, vcv_csv)

    # educH+GSUR+region VCV (10×10 block: educH + 8 cross-partners)
    educ_block_params = EDUC_PARAMS + EDUC_CROSS_PARAMS  # 1 + 8 = 9
    educ_idx = [param_names.index(p) for p in educ_block_params]
    vcv_educ = vcv_full[np.ix_(educ_idx, educ_idx)]
    vcv_educ_csv = output_dir / f"RURO_occ_M1_naive_vcv_educ_gsur_region_block_{utc_tag}.csv"
    write_matrix_csv(vcv_educ, educ_block_params, vcv_educ_csv)

    # D3 Hessian sub-block CSV
    full_to_free = {fi: i for i, fi in enumerate(free_idx)}
    hess_sub_idx = [full_to_free[param_names.index(p)]
                    for p in GSUR_EDUC_REGION_PARAMS
                    if param_names.index(p) in full_to_free]
    H_sub = H_free[np.ix_(hess_sub_idx, hess_sub_idx)]
    active_params = [p for p in GSUR_EDUC_REGION_PARAMS
                     if param_names.index(p) in full_to_free]
    hessian_csv = output_dir / f"RURO_occ_M1_naive_hessian_gsur_educ_region_block_{utc_tag}.csv"
    write_matrix_csv(H_sub, active_params, hessian_csv)

    # 10. Write report
    report_path = output_dir / "RURO_occ_M1_naive_supplementary_diagnostics_v1.md"
    write_report(
        d1=d1, d2=d2, d3=d3, d4=d4,
        spec_name=spec.name,
        run_folder=str(Path(args.results_json).parent.name),
        params_csv=args.params_csv,
        mnl_base=args.mnl_base,
        eps=args.eps,
        hessian_cond=cond_full,
        n_neg_full=n_neg_full,
        output_path=report_path,
        vcv_csv=vcv_csv,
        vcv_educ_csv=vcv_educ_csv,
        hessian_csv=hessian_csv,
    )
    logger.info("Done.")


if __name__ == "__main__":
    main()