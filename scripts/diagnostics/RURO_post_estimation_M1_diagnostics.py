"""
RURO occ M1-clean supplementary diagnostics.

Three diagnostics specific to M1-clean's region-dummy block:

  D1. Joint Wald test  H0: beta_E_drgn2 = ... = beta_E_drgn8 = 0  (7 d.f.)
  D2. 7x7 region covariance / correlation sub-block with collinearity flags
  D3. Eigenvalues of the 8x8 region-conditional GSUR+drgn Hessian sub-matrix

The full 53x53 numerical Hessian is not saved by the main estimation script,
so this script recomputes it via central-difference finite differences on the
joint gradient.

Usage
-----
  python scripts/enhanced/RURO_post_estimation_M1_diagnostics.py
      --params-csv   <path to params.csv from post-estimation>
      --results-json <path to estimation_results.json>
      --mnl-base     <path prefix for __singles.parquet / __couples.parquet>
      --spec         <path to estimation_spec_ruro_occ_M1_clean.yaml>
      --output-dir   <Results/ or wherever>
      [--eps FLOAT]  (finite-difference step; default 1e-5)

Outputs
-------
  <output-dir>/RURO_occ_M1_clean_supplementary_diagnostics_v1.md
  <output-dir>/RURO_occ_M1_clean_hessian_region_block_<UTC>.csv
  <output-dir>/RURO_occ_M1_clean_vcv_region_block_<UTC>.csv

The markdown report is the primary deliverable; CSVs hold the raw matrices.
"""

import argparse
import logging
import os
import sys
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

# ---------------------------------------------------------------------------
# Path setup: add scripts/enhanced to sys.path so local modules are importable
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

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
# Region parameter names (order matters: must match spec / params.csv)
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

GSUR_REGION_PARAMS = ["joint.beta_E_gsur"] + REGION_PARAMS  # 8-param block for D3


# ===========================================================================
# Numerical Hessian (central differences)
# ===========================================================================

def compute_numerical_hessian(
    theta: np.ndarray,
    grad_func,
    free_idx: np.ndarray,
    eps: float = 1e-5,
) -> np.ndarray:
    """
    Compute H[i,j] = d²(-LL)/dtheta_i dtheta_j  for i,j in free_idx.

    Uses central differences on the gradient:
        H[:, col] = (g(theta + eps*e_i)[free_idx] - g(theta - eps*e_i)[free_idx]) / (2*eps)

    Returns
    -------
    H : ndarray, shape (n_free, n_free)
    """
    n_free = len(free_idx)
    H = np.zeros((n_free, n_free))

    for col_idx, i in enumerate(free_idx):
        theta_p = theta.copy()
        theta_m = theta.copy()
        theta_p[i] += eps
        theta_m[i] -= eps

        g_p = grad_func(theta_p)
        g_m = grad_func(theta_m)

        H[:, col_idx] = (g_p[free_idx] - g_m[free_idx]) / (2.0 * eps)

        if (col_idx + 1) % 10 == 0:
            logger.info("  Hessian column %d / %d", col_idx + 1, n_free)

    H = 0.5 * (H + H.T)  # symmetrise
    return H


# ===========================================================================
# Core diagnostics
# ===========================================================================

def diagnostic_d1_wald_test(
    theta: np.ndarray,
    vcv_full: np.ndarray,
    param_names: list[str],
    region_params: list[str],
    original_se: np.ndarray | None = None,
    original_pval: np.ndarray | None = None,
) -> dict:
    """
    Joint Wald test H0: all region coefficients = 0.

    W = theta_R' * inv(V_RR) * theta_R  ~  chi2(k)  under H0.

    The Wald statistic uses the recomputed VCV.  Individual z-stats and p-values
    use ``original_se`` / ``original_pval`` from the estimation run if supplied
    (more precise, from the GAMSPy solver's internal Hessian), otherwise fall
    back to the recomputed SE diagonal.
    """
    idx = [param_names.index(p) for p in region_params]
    theta_r = theta[idx]
    vcv_r = vcv_full[np.ix_(idx, idx)]

    try:
        vcv_r_inv = np.linalg.inv(vcv_r)
        W = float(theta_r @ vcv_r_inv @ theta_r)
    except np.linalg.LinAlgError:
        logger.warning("VCV sub-block singular; trying pseudo-inverse for Wald stat")
        vcv_r_inv = np.linalg.pinv(vcv_r, rcond=1e-10)
        W = float(theta_r @ vcv_r_inv @ theta_r)

    df = len(region_params)
    p_val = float(1.0 - chi2.cdf(W, df))

    # Individual statistics: prefer original estimation SEs
    if original_se is not None:
        se_r = original_se[idx]
    else:
        se_r = np.sqrt(np.diag(vcv_r))

    if original_pval is not None:
        p_indiv = original_pval[idx]
    else:
        z_vals = theta_r / se_r
        p_indiv = 1.0 - chi2.cdf(z_vals ** 2, 1)  # chi2(1) p-value = 2-sided normal p-value

    z_vals = theta_r / se_r

    return {
        "W_stat": W,
        "df": df,
        "p_value": p_val,
        "theta_r": theta_r.tolist(),
        "se_r": se_r.tolist(),
        "z_vals": z_vals.tolist(),
        "p_indiv": p_indiv.tolist() if hasattr(p_indiv, "tolist") else list(p_indiv),
        "param_names": region_params,
        "se_source": "original_estimation" if original_se is not None else "recomputed_hessian",
    }


def diagnostic_d2_region_vcv(
    vcv_full: np.ndarray,
    param_names: list[str],
    region_params: list[str],
    corr_flag_threshold: float = 0.7,
) -> dict:
    """
    Extract the 7x7 region covariance / correlation sub-block.

    Returns dict with VCV matrix, correlation matrix, and flags for |corr| > threshold.
    """
    idx = [param_names.index(p) for p in region_params]
    vcv_r = vcv_full[np.ix_(idx, idx)]
    se_r = np.sqrt(np.diag(vcv_r))

    # Correlation matrix
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = np.outer(se_r, se_r)
        corr_r = np.divide(vcv_r, denom, out=np.full_like(vcv_r, np.nan), where=denom > 0)
    np.fill_diagonal(corr_r, 1.0)

    # Flag high off-diagonal correlations
    flags = []
    k = len(region_params)
    for i in range(k):
        for j in range(i + 1, k):
            if abs(corr_r[i, j]) > corr_flag_threshold:
                flags.append({
                    "param_i": region_params[i],
                    "param_j": region_params[j],
                    "corr": float(corr_r[i, j]),
                })

    return {
        "vcv": vcv_r,
        "corr": corr_r,
        "se": se_r,
        "flags": flags,
        "param_names": region_params,
    }


def diagnostic_d3_gsur_region_hessian(
    H_free: np.ndarray,
    free_idx: np.ndarray,
    param_names_full: list[str],
    gsur_region_params: list[str],
) -> dict:
    """
    Eigenvalue decomposition of the 8x8 GSUR+region Hessian sub-matrix.

    H_free is indexed over free parameters (shape n_free × n_free).
    We locate GSUR+drgn2-8 within the free-parameter indices, extract
    the sub-block, and compute eigenvalues.
    """
    # Map param names to full-param index, then to free-param index
    full_to_free = {fi: i for i, fi in enumerate(free_idx)}

    sub_idx_in_free = []
    for pname in gsur_region_params:
        full_i = param_names_full.index(pname)
        if full_i in full_to_free:
            sub_idx_in_free.append(full_to_free[full_i])
        else:
            logger.warning("Parameter %s not in free set; skipping from D3 sub-block", pname)

    H_sub = H_free[np.ix_(sub_idx_in_free, sub_idx_in_free)]
    eigenvalues = np.linalg.eigvalsh(H_sub)

    return {
        "eigenvalues": eigenvalues.tolist(),
        "n_negative": int(np.sum(eigenvalues < 0)),
        "min_eig": float(eigenvalues.min()),
        "max_eig": float(eigenvalues.max()),
        "param_names": gsur_region_params,
        "H_sub": H_sub,
    }


# ===========================================================================
# Report writer
# ===========================================================================

def _fmt(x, decimals=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{x:.{decimals}f}"


def write_markdown_report(
    d1: dict,
    d2: dict,
    d3: dict,
    spec_name: str,
    run_folder: str,
    params_csv: str,
    mnl_base: str,
    eps: float,
    hessian_cond: float,
    n_negative_full: int,
    output_path: Path,
    vcv_csv: Path,
    hessian_csv: Path,
):
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []

    lines += [
        f"# RURO occ M1-clean Supplementary Diagnostics v1",
        "",
        f"Date: {utc_now}  ",
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
        "This report contains three diagnostics specific to the region-dummy block",
        "introduced in M1-clean. The full 53×53 numerical Hessian was recomputed",
        "via central-difference finite differences on the joint gradient function.",
        "",
        f"Full-Hessian condition number (recomputed): {hessian_cond:.4e}  ",
        f"Negative eigenvalues in full 53×53 Hessian: {n_negative_full}",
        "",
        "---",
        "",
        "## D1 — Joint Wald test: β_E_drgn2 = … = β_E_drgn8 = 0",
        "",
        "Tests whether the seven region dummies jointly contribute to the",
        "employment-opportunity index, conditional on all other parameters.",
        "",
        f"**H₀**: β_E_drgn2 = β_E_drgn3 = β_E_drgn4 = β_E_drgn5 =",
        f"       β_E_drgn6 = β_E_drgn7 = β_E_drgn8 = 0",
        "",
        f"**Test statistic**: W = {_fmt(d1['W_stat'], 4)}",
        f"**Degrees of freedom**: {d1['df']}",
        f"**p-value**: {_fmt(d1['p_value'], 6)}",
        "",
        "**Interpretation**: " + (
            f"W = {_fmt(d1['W_stat'], 2)} on {d1['df']} d.f. "
            + ("is highly significant (p < 0.001); the seven region dummies jointly"
               " improve fit." if d1['p_value'] < 0.001 else
               f"has p = {_fmt(d1['p_value'], 4)}; "
               + ("significant at 5%." if d1['p_value'] < 0.05 else
                  "not significant at 5%.")
               )
        ),
        "",
        "### Individual region parameter table",
        "",
        "| Parameter | Estimate | SE | z-stat | p-value | Sig |",
        "|---|---|---|---|---|---|",
    ]

    for i, pname in enumerate(d1["param_names"]):
        short = pname.replace("joint.", "")
        est = d1["theta_r"][i]
        se = d1["se_r"][i]
        z = d1["z_vals"][i]
        p = d1["p_indiv"][i]
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
        lines.append(
            f"| `{short}` | {_fmt(est)} | {_fmt(se)} | {_fmt(z)} | {_fmt(p, 4)} | {sig} |"
        )

    lines += [
        "",
        "*: p<0.05  **: p<0.01  ***: p<0.001",
        "",
        "---",
        "",
        "## D2 — 7×7 region covariance / correlation sub-block",
        "",
        "Extracted from the full 53×53 VCV (pseudo-inverse of the Hessian).",
        f"Raw VCV and correlation matrices saved to: `{vcv_csv.name}`",
        "",
        "### Standard errors",
        "",
        "| Parameter | SE |",
        "|---|---|",
    ]

    for i, pname in enumerate(d2["param_names"]):
        short = pname.replace("joint.", "")
        lines.append(f"| `{short}` | {_fmt(d2['se'][i])} |")

    lines += [
        "",
        "### Correlation matrix (7×7)",
        "",
    ]

    # Header row
    short_names = [p.replace("joint.beta_E_", "") for p in d2["param_names"]]
    lines.append("| " + " | ".join([""] + short_names) + " |")
    lines.append("|" + "---|" * (len(short_names) + 1))

    for i, pname in enumerate(d2["param_names"]):
        short_i = short_names[i]
        row = [f"`{short_i}`"]
        for j in range(len(d2["param_names"])):
            v = d2["corr"][i, j]
            cell = _fmt(v, 3)
            if i != j and abs(v) > 0.7:
                cell = f"**{cell}**"
            row.append(cell)
        lines.append("| " + " | ".join(row) + " |")

    if d2["flags"]:
        lines += [
            "",
            f"**High-correlation flags** (|corr| > 0.7): {len(d2['flags'])} pair(s)",
            "",
        ]
        for f in d2["flags"]:
            pi = f["param_i"].replace("joint.", "")
            pj = f["param_j"].replace("joint.", "")
            lines.append(f"- `{pi}` × `{pj}`: corr = {_fmt(f['corr'], 3)}")
    else:
        lines += [
            "",
            "No high-correlation flags (all |corr| ≤ 0.70).",
        ]

    lines += [
        "",
        "---",
        "",
        "## D3 — 8×8 GSUR+region Hessian sub-matrix eigenvalues",
        "",
        "Sub-block spanning {β_E_gsur, β_E_drgn2, …, β_E_drgn8} extracted from",
        "the full numerical Hessian (evaluated at the M1-clean solution).",
        f"Raw sub-matrix saved to: `{hessian_csv.name}`",
        "",
        f"**Eigenvalues** (ascending):  ",
        "",
        "| # | Eigenvalue | Sign |",
        "|---|---|---|",
    ]

    for i, ev in enumerate(sorted(d3["eigenvalues"])):
        sign = "negative" if ev < 0 else ("near-zero" if abs(ev) < 1e-4 else "positive")
        lines.append(f"| {i+1} | {ev:.6e} | {sign} |")

    lines += [
        "",
        f"Negative eigenvalues: {d3['n_negative']}  ",
        f"Minimum eigenvalue: {d3['min_eig']:.6e}  ",
        f"Maximum eigenvalue: {d3['max_eig']:.6e}",
        "",
        "**Interpretation**: " + (
            "All eigenvalues of the 8×8 GSUR+region Hessian sub-block are positive;"
            " the sub-block is locally convex and well-identified."
            if d3["n_negative"] == 0 else
            f"{d3['n_negative']} negative eigenvalue(s) in the GSUR+region sub-block "
            "indicate a saddle-point direction in the region parameters."
        ),
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    wald_verdict = (
        f"D1 (Wald, 7 d.f.): W = {_fmt(d1['W_stat'], 2)}, "
        f"p = {_fmt(d1['p_value'], 4)} — "
        + ("jointly significant (p < 0.001)." if d1['p_value'] < 0.001 else
           f"p = {_fmt(d1['p_value'], 4)}.")
    )

    flag_verdict = (
        f"D2 (collinearity): {len(d2['flags'])} high-correlation pair(s) flagged."
        if d2["flags"] else
        "D2 (collinearity): no high-correlation pairs (all |corr| ≤ 0.70)."
    )

    d3_verdict = (
        f"D3 (sub-block eigenvalues): {d3['n_negative']} negative eigenvalue(s) "
        f"in 8×8 GSUR+region block."
        if d3["n_negative"] > 0 else
        "D3 (sub-block eigenvalues): all 8 eigenvalues positive; sub-block locally convex."
    )

    lines += [
        f"- {wald_verdict}",
        f"- {flag_verdict}",
        f"- {d3_verdict}",
        "",
        "---",
        "",
        "*Generated by `scripts/enhanced/RURO_post_estimation_M1_diagnostics.py`*",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Report written: %s", output_path)


def write_matrix_csv(matrix: np.ndarray, param_names: list[str], path: Path):
    short_names = [p.replace("joint.", "") for p in param_names]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + short_names)
        for i, row in enumerate(matrix):
            w.writerow([short_names[i]] + [f"{v:.8e}" for v in row])
    logger.info("Matrix CSV written: %s", path)


# ===========================================================================
# Main
# ===========================================================================

def parse_args():
    p = argparse.ArgumentParser(description="M1-clean supplementary diagnostics")
    p.add_argument("--params-csv", required=True)
    p.add_argument("--results-json", required=True)
    p.add_argument(
        "--mnl-base",
        required=True,
        help="Path prefix for __singles.parquet and __couples.parquet",
    )
    p.add_argument(
        "--spec",
        required=True,
        help="Path to estimation_spec_ruro_occ_M1_clean.yaml",
    )
    p.add_argument("--output-dir", required=True)
    p.add_argument("--eps", type=float, default=1e-5)
    return p.parse_args()


def main():
    args = parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    utc_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ------------------------------------------------------------------
    # 1. Load parameters
    # ------------------------------------------------------------------
    logger.info("Loading parameters from %s", args.params_csv)
    params_df = pd.read_csv(args.params_csv)
    param_names_full = params_df["parameter"].tolist()
    theta_final = params_df["estimate"].values.astype(float)

    logger.info("Loaded %d parameters", len(param_names_full))

    # Verify region params are present
    for rp in GSUR_REGION_PARAMS:
        if rp not in param_names_full:
            logger.error("Expected parameter '%s' not found in params.csv", rp)
            sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Parse spec and load data
    # ------------------------------------------------------------------
    logger.info("Parsing spec: %s", args.spec)

    # Temporarily chdir to scripts/enhanced so spec parser can find includes
    orig_dir = Path.cwd()
    try:
        os.chdir(_SCRIPT_DIR)
        spec = parse_specification(Path(args.spec))
    finally:
        os.chdir(orig_dir)

    logger.info("Spec parsed: %s (%d params)", spec.name, len(spec.all_param_names))

    # Cross-check param count
    if len(spec.all_param_names) != len(param_names_full):
        logger.warning(
            "Spec has %d params but params.csv has %d — check alignment",
            len(spec.all_param_names),
            len(param_names_full),
        )

    # Load MNL data
    mnl_base = Path(args.mnl_base)
    singles_path = Path(str(mnl_base) + "__singles.parquet")
    couples_path = Path(str(mnl_base) + "__couples.parquet")
    metadata_path = Path(str(mnl_base) + "__mnlmeta.json")

    logger.info("Loading MNL data from %s", mnl_base)
    df_singles, df_couples, metadata = load_and_validate_mnl_data(
        singles_path=singles_path,
        couples_path=couples_path if couples_path.exists() else None,
        metadata_path=metadata_path,
        strict_validation=False,
    )

    # Determine extra precompute vars from spec
    extra_set = set()
    for shifter in getattr(spec, "market_opportunity_shifters", []):
        if not isinstance(shifter, dict):
            continue
        var = shifter.get("variable")
        if var:
            extra_set.add(var.strip())
        for iv in (shifter.get("interaction") or []):
            if iv and iv != "working":
                extra_set.add(iv.strip())
    for shifter in getattr(spec, "utility_leisure_shifters", []):
        if not isinstance(shifter, dict):
            continue
        var = shifter.get("variable")
        if var:
            extra_set.add(var.strip())
    extra_vars = sorted(extra_set)
    logger.info("Extra precompute vars: %s", extra_vars)

    include_wage = spec.wage_spec in ("vw", "loc_empirical")
    include_loc = spec.wage_spec == "loc_empirical"

    # Precompute
    df_sm = df_singles[df_singles["dgn"] == 1]
    df_sf = df_singles[df_singles["dgn"] == 0]

    logger.info("Precomputing singles male (%d obs)...", len(df_sm))
    data_sm = precompute_data_singles(
        df=df_sm,
        metadata=metadata,
        is_male=True,
        include_wage_vars=include_wage,
        include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )

    logger.info("Precomputing singles female (%d obs)...", len(df_sf))
    data_sf = precompute_data_singles(
        df=df_sf,
        metadata=metadata,
        is_male=False,
        include_wage_vars=include_wage,
        include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )

    assert df_couples is not None, "Couples parquet required for joint gradient"
    logger.info("Precomputing couples (%d obs)...", len(df_couples))
    data_cou = precompute_data_couples(
        df=df_couples,
        metadata=metadata,
        include_wage_vars=include_wage,
        include_loc_vars=include_loc,
        include_extra_vars=extra_vars,
    )

    # ------------------------------------------------------------------
    # 3. Build gradient function
    # ------------------------------------------------------------------
    def grad_func(theta):
        return compute_gradient_joint(theta, data_sm, data_sf, data_cou, spec)

    # ------------------------------------------------------------------
    # 4. Determine free parameters (exclude those at bounds)
    # ------------------------------------------------------------------
    bounds = spec.get_bounds_tuple()  # list of (lb, ub) per param
    bound_tol = 1e-6
    bound_range_tol = 1e-6

    free_mask = np.ones(len(theta_final), dtype=bool)
    for i, (lb, ub) in enumerate(bounds):
        if lb is None and ub is None:
            continue
        if lb is not None and ub is not None and (ub - lb) <= bound_range_tol:
            free_mask[i] = False
            continue
        if lb is not None and abs(theta_final[i] - lb) <= bound_tol:
            free_mask[i] = False
        elif ub is not None and abs(theta_final[i] - ub) <= bound_tol:
            free_mask[i] = False

    free_idx = np.where(free_mask)[0]
    n_free = len(free_idx)
    n_fixed = len(theta_final) - n_free
    logger.info(
        "Free parameters: %d / %d (%d fixed at bounds)", n_free, len(theta_final), n_fixed
    )

    # ------------------------------------------------------------------
    # 5. Compute numerical Hessian
    # ------------------------------------------------------------------
    logger.info("Computing %dx%d numerical Hessian (eps=%.1e)...", n_free, n_free, args.eps)
    H_free = compute_numerical_hessian(theta_final, grad_func, free_idx, eps=args.eps)
    logger.info("Hessian computed.")

    # Full-Hessian diagnostics
    eigenvalues_full = np.linalg.eigvalsh(H_free)
    n_neg_full = int(np.sum(eigenvalues_full < 0))
    cond_full = float(np.linalg.cond(H_free))
    logger.info("Full Hessian: cond = %.4e, n_negative = %d", cond_full, n_neg_full)

    # ------------------------------------------------------------------
    # 6. Compute VCV (pseudo-inverse for ill-conditioned Hessian)
    # ------------------------------------------------------------------
    logger.info("Computing VCV via pseudo-inverse (rcond=1e-10)...")
    vcv_free = np.linalg.pinv(H_free, rcond=1e-10)

    # Embed into full 53x53 VCV
    n_params = len(theta_final)
    vcv_full = np.full((n_params, n_params), np.nan)
    vcv_full[np.ix_(free_idx, free_idx)] = vcv_free

    # ------------------------------------------------------------------
    # 7. Run diagnostics
    # ------------------------------------------------------------------
    # Extract original SEs and p-values from params_df for individual table display
    orig_se_all = params_df["std_error"].values.astype(float)
    orig_pval_all = params_df["p_value"].values.astype(float)

    logger.info("Running D1 (Wald test)...")
    d1 = diagnostic_d1_wald_test(
        theta_final, vcv_full, param_names_full, REGION_PARAMS,
        original_se=orig_se_all, original_pval=orig_pval_all,
    )
    logger.info("Wald W = %.4f, df = %d, p = %.6f", d1["W_stat"], d1["df"], d1["p_value"])

    logger.info("Running D2 (region VCV block)...")
    d2 = diagnostic_d2_region_vcv(vcv_full, param_names_full, REGION_PARAMS)
    if d2["flags"]:
        logger.info("D2: %d high-correlation pair(s) flagged", len(d2["flags"]))
    else:
        logger.info("D2: no high-correlation pairs")

    logger.info("Running D3 (GSUR+region Hessian eigenvalues)...")
    d3 = diagnostic_d3_gsur_region_hessian(
        H_free, free_idx, param_names_full, GSUR_REGION_PARAMS
    )
    logger.info(
        "D3: min_eig = %.4e, max_eig = %.4e, n_neg = %d",
        d3["min_eig"],
        d3["max_eig"],
        d3["n_negative"],
    )

    # ------------------------------------------------------------------
    # 8. Save CSV outputs
    # ------------------------------------------------------------------
    vcv_csv = output_dir / f"RURO_occ_M1_clean_vcv_region_block_{utc_tag}.csv"
    hessian_csv = output_dir / f"RURO_occ_M1_clean_hessian_region_block_{utc_tag}.csv"

    write_matrix_csv(d2["vcv"], REGION_PARAMS, vcv_csv)

    # D3 Hessian sub-matrix: extract from H_free using free-param mapping
    full_to_free = {fi: i for i, fi in enumerate(free_idx)}
    gsur_sub_idx_in_free = []
    for pname in GSUR_REGION_PARAMS:
        fi = param_names_full.index(pname)
        if fi in full_to_free:
            gsur_sub_idx_in_free.append(full_to_free[fi])
    H_sub = H_free[np.ix_(gsur_sub_idx_in_free, gsur_sub_idx_in_free)]
    write_matrix_csv(H_sub, GSUR_REGION_PARAMS, hessian_csv)

    # ------------------------------------------------------------------
    # 9. Write markdown report
    # ------------------------------------------------------------------
    report_path = output_dir / "RURO_occ_M1_clean_supplementary_diagnostics_v1.md"
    write_markdown_report(
        d1=d1,
        d2=d2,
        d3=d3,
        spec_name=spec.name,
        run_folder=str(Path(args.results_json).parent.name),
        params_csv=args.params_csv,
        mnl_base=args.mnl_base,
        eps=args.eps,
        hessian_cond=cond_full,
        n_negative_full=n_neg_full,
        output_path=report_path,
        vcv_csv=vcv_csv,
        hessian_csv=hessian_csv,
    )

    logger.info("Done. Report: %s", report_path)


if __name__ == "__main__":
    main()