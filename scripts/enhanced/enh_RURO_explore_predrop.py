#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
enh_RURO_explore_predrop.py

Pre-drop data exploration for the France RURO MNL pipeline.

PURPOSE
-------
enh_RURO_prep_mnl_basic.py builds a ~900-column frame AFTER EUROMOD has been run
on all draws and AFTER GSUR has been merged, then keeps only ~100 "essential"
columns via filter_to_essential_columns() before writing the estimation parquets.
This script profiles the FULL frame at that point so you can see what is being
dropped and judge, on ECONOMIC grounds, whether any dropped variable should be
promoted into a candidate for:
    - preferences (taste shifters), or
    - hours opportunity, or
    - wage opportunity (Mincer mean), or
    - occupation opportunity.

DISCIPLINE (read this)
----------------------
This tool answers ONLY the questions data can answer:
  (1) coverage / feasibility  -> is a variable usable at all (missingness, variation)?
  (2) choice-space shape       -> where are the hours/wage focal points and the h=0 mass?
  (3) within-role redundancy   -> are candidate shifters INSIDE one role collinear?
It does NOT, and cannot, tell you whether a variable belongs in preferences vs
opportunities. That split is identified by model structure + exclusion restrictions,
NOT by correlations (a raw correlation fuses both channels). Use this report to
decide which dropped variables to PROMOTE into get_essential_columns_for_estimation(),
with a written economic reason per promoted variable. The final identification check
is the Monte Carlo recovery test, not this report.

USAGE
-----
Run on the unfiltered dumps produced by the --explore-dump-dir hook added to
enh_RURO_prep_mnl_basic.py main():

    python enh_RURO_explore_predrop.py \
        --full-singles  <dir>/predrop_full__singles.parquet \
        --full-couples  <dir>/predrop_full__couples.parquet \
        --out-dir       <dir>/explore \
        --audit-out     docs/RURO_data_audit_v1.md

Either --full-singles or --full-couples may be omitted.
"""
from __future__ import annotations

import argparse
import datetime
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Focal hours bands, kept identical to enh_RURO_prep_mnl_basic._build_mnl_block
PT1 = (18.5, 21.5)
PT2 = (29.5, 30.5)
FT = (37.5, 40.5)

# Candidate WITHIN-ROLE shifter sets (singles naming; couples handled with suffixes).
# NOTE: a variable may appear in more than one list (e.g. educH). That is intentional:
# the within-role blocks only check redundancy INSIDE a role. Which role educ belongs
# to is a theory decision, not something this script resolves.
PREF_CANDIDATES = ["age_norm", "age_norm2", "educH", "educL", "n_children"]
OPP_WAGE_CANDIDATES = ["educL", "educH", "pexp_years", "pexp_years2"]
OPP_HOURS_CANDIDATES = ["gsur", "educH"]

# Polynomial pairs that are mechanically collinear — report in VIF NOTE, not as
# prunable redundancy.
POLY_PAIRS = [("age_norm", "age_norm2"), ("pexp_years", "pexp_years2")]

MISSING_OK = 20.0  # % missingness threshold for a "usable" dropped variable


# ---------------------------------------------------------------------------
# Whitelist (kept vs dropped) — imported from the prep script if available
# ---------------------------------------------------------------------------
def load_kept_columns(prep_dir: Path | None) -> set[str] | None:
    candidates = []
    if prep_dir is not None:
        candidates.append(prep_dir)
    candidates.append(Path(__file__).resolve().parent)
    for d in candidates:
        try:
            sys.path.insert(0, str(d))
            from enh_RURO_prep_mnl_basic import get_essential_columns_for_estimation  # type: ignore
            return set(get_essential_columns_for_estimation())
        except Exception:
            continue
    logging.warning(
        "Could not import get_essential_columns_for_estimation; "
        "kept/dropped labels will read 'unknown'. Pass --prep-dir to fix."
    )
    return None


# ---------------------------------------------------------------------------
# 1. Per-variable inventory (coverage / feasibility)
# ---------------------------------------------------------------------------
def profile_columns(df: pd.DataFrame, kept: set[str] | None) -> pd.DataFrame:
    n = len(df)
    rows = []
    for c in df.columns:
        s = df[c]
        nonnull = int(s.notna().sum())
        pct_missing = round(100.0 * (1 - nonnull / n), 2) if n else 100.0
        nunique = int(s.nunique(dropna=True))
        is_num = pd.api.types.is_numeric_dtype(s)
        if kept is None:
            status = "unknown"
        else:
            status = "kept" if c in kept else "dropped"
        # Category: tag _em columns explicitly so they are never buried in "dropped"
        if c.endswith("_em"):
            category = "euromod_output"
        elif status == "kept":
            category = "kept_whitelist"
        else:
            category = "dropped_other"
        rec = {
            "column": c,
            "dtype": str(s.dtype),
            "status": status,
            "category": category,
            "pct_missing": pct_missing,
            "n_unique": nunique,
            "is_constant": nunique <= 1,
        }
        if is_num and nonnull > 0:
            v = pd.to_numeric(s, errors="coerce").to_numpy(dtype="float64")
            v = v[np.isfinite(v)]
            if v.size:
                rec["mean"] = round(float(np.mean(v)), 4)
                rec["std"] = round(float(np.std(v)), 4)
                rec["min"] = round(float(np.min(v)), 4)
                rec["p50"] = round(float(np.median(v)), 4)
                rec["max"] = round(float(np.max(v)), 4)
        else:
            top = s.dropna().astype(str).value_counts().head(3)
            rec["top_values"] = "; ".join(f"{k}({int(v)})" for k, v in top.items())
        # Promotion candidate: currently dropped, usable coverage, real variation.
        rec["promote_candidate"] = (
            status == "dropped" and pct_missing <= MISSING_OK and nunique > 1
        )
        rows.append(rec)
    out = pd.DataFrame(rows)
    sort_cols = [c for c in ["status", "promote_candidate", "pct_missing"] if c in out.columns]
    return out.sort_values(sort_cols, ascending=[True, False, True][: len(sort_cols)])


# ---------------------------------------------------------------------------
# 1b. EUROMOD output columns section
# ---------------------------------------------------------------------------
# EUROMOD outputs are the counterfactual tax-benefit calculations run on every
# draw alternative.  The `_em` suffix marks them.  Only `ils_dispy_em` enters
# the estimation whitelist (it becomes `consumption`); all others are the
# accounting decomposition.  This section makes them visible in the audit
# rather than silently lumping them with "dropped other".

_ILS_IDENTITY = ("ils_dispy_em",
                 "ils_origy_em", "ils_ben_em", "ils_sicdy_em", "ils_tax_em")

# Key _em columns that are worth surfacing explicitly, with human labels.
_EM_LABELS = {
    "ils_dispy_em":     "Disposable income (EUROMOD counterfactual) → consumption in model",
    "ils_origy_em":     "Original income (pre-tax+benefit, counterfactual)",
    "ils_earns_em":     "Gross earnings (counterfactual)",
    "ils_ben_em":       "Total benefits (counterfactual)",
    "ils_bennt_em":     "Non-means-tested benefits (counterfactual)",
    "ils_benmt_em":     "Means-tested benefits (counterfactual)",
    "ils_tax_em":       "Total taxes (counterfactual)",
    "ils_taxin_em":     "Income tax (counterfactual)",
    "ils_taxwl_em":     "Wealth/other tax (counterfactual)",
    "ils_sicdy_em":     "Employee social insurance contributions (counterfactual)",
    "ils_sicee_em":     "Employer social insurance contributions (counterfactual)",
    "ils_sicot_em":     "Other social insurance (counterfactual)",
    "ils_b1_bun_em":    "Unemployment benefit (counterfactual)",
    "ils_b1_bfa_em":    "Family/child benefit (counterfactual)",
    "ils_b1_bsa_em":    "Social assistance (counterfactual)",
    "ils_b1_bho_em":    "Housing benefit (counterfactual)",
    "ils_b1_bhl_em":    "Health/sickness benefit (counterfactual)",
    "ils_b1_bdi_em":    "Disability benefit (counterfactual)",
    "ils_b1_bed_em":    "Education benefit (counterfactual)",
    "ils_b2_bfaed_em":  "Family+education aggregate (counterfactual)",
    "ils_b2_bsaho_em":  "Social assistance+housing aggregate (counterfactual)",
    "ils_b2_bunwk_em":  "Unemployment+in-work aggregate (counterfactual)",
}


def euromod_outputs_section(df: pd.DataFrame, kept: set[str] | None,
                             group: str, suffix: str = "") -> str:
    """
    Produce a markdown block listing all _em EUROMOD counterfactual output
    columns: which are kept, their stats on chosen rows, and the
    ils_dispy accounting identity check.

    `suffix` is '' for singles, '_male'/'_female' for couples.
    """
    if "is_chosen" in df.columns:
        chosen = df[df["is_chosen"] == 1]
    else:
        chosen = df

    # Collect _em columns (with suffix for couples)
    if suffix:
        em_cols = [c for c in df.columns if c.endswith(f"_em{suffix}") or
                   (c.endswith("_em") and f"{c[:-3]}{suffix}_em"[:] in df.columns)]
        # For couples the columns are like ils_dispy_em_male — check actual pattern
        em_cols = [c for c in df.columns if "_em" in c and c.endswith(suffix)]
    else:
        em_cols = [c for c in df.columns if c.endswith("_em")]

    if not em_cols:
        return f"_No `_em` EUROMOD output columns found for {group}{suffix}._\n"

    em_kept   = [c for c in em_cols if kept and c in kept]
    em_dropped = [c for c in em_cols if not kept or c not in kept]

    label_tag = f"{group}" + (f" ({suffix.strip('_')})" if suffix else "")
    lines = [
        f"### EUROMOD counterfactual output columns — {label_tag}",
        "",
        f"Total `_em` columns: **{len(em_cols)}**  |  "
        f"Kept in whitelist: **{len(em_kept)}**  |  "
        f"Dropped (decomposition): **{len(em_dropped)}**",
        "",
        "> All `_em` columns are EUROMOD's tax-benefit calculations on each draw "
        "alternative (counterfactual). Only `ils_dispy_em` enters the estimation "
        "whitelist — it becomes `consumption` after normalisation. The remaining "
        "338 columns are the accounting decomposition (earnings, taxes, benefits, "
        "social contributions) which sum back to `ils_dispy_em` via the identity "
        "below. They are dropped for estimation but available for welfare "
        "decomposition analysis.",
        "",
    ]

    # Accounting identity check (singles naming; skip for couples unless cols exist)
    id_cols = [c for c in _ILS_IDENTITY if c in chosen.columns]
    if len(id_cols) == len(_ILS_IDENTITY):
        resid = (chosen["ils_dispy_em"]
                 - chosen["ils_origy_em"]
                 - chosen["ils_ben_em"]
                 + chosen["ils_sicdy_em"]
                 + chosen["ils_tax_em"])
        max_resid = float(resid.abs().max())
        lines += [
            "**Accounting identity** (chosen rows):",
            "",
            "```",
            "ils_dispy_em = ils_origy_em + ils_ben_em - ils_sicdy_em - ils_tax_em",
            f"Max absolute residual: {max_resid:.8f}  {'✓ holds' if max_resid < 1e-4 else '✗ FAILS'}",
            "```",
            "",
        ]

    # Table of named key columns
    lines += [
        "**Key columns (named):**",
        "",
        "| Column | Status | Mean (chosen) | Label |",
        "|---|---|---|---|",
    ]
    for col, label in _EM_LABELS.items():
        actual = col + suffix if suffix else col
        if actual not in df.columns:
            # Try without suffix for columns that don't get suffixed in couples
            actual = col if col in df.columns else None
        if actual is None:
            continue
        stat_val = chosen[actual].mean() if actual in chosen.columns else float("nan")
        status_str = "**KEPT**" if (kept and actual in kept) else "dropped"
        lines.append(f"| `{actual}` | {status_str} | {stat_val:.1f} | {label} |")

    lines += [""]

    # Full table of ALL _em columns (compact)
    lines += [
        "<details><summary>All _em columns (click to expand)</summary>",
        "",
        "| Column | Status | Mean | Std | Min | Max |",
        "|---|---|---|---|---|---|",
    ]
    for c in sorted(em_cols):
        if c not in chosen.columns:
            continue
        v = pd.to_numeric(chosen[c], errors="coerce").dropna()
        status_str = "**KEPT**" if (kept and c in kept) else "dropped"
        if v.size:
            lines.append(
                f"| `{c}` | {status_str} | {v.mean():.1f} | {v.std():.1f} | "
                f"{v.min():.1f} | {v.max():.1f} |"
            )
        else:
            lines.append(f"| `{c}` | {status_str} | — | — | — | — |")
    lines += ["", "</details>", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Choice-space shape (validate focal bins + h=0 mass)
# ---------------------------------------------------------------------------
def _band(h: np.ndarray, lo: float, hi: float) -> float:
    return float(np.mean((h >= lo) & (h <= hi))) if h.size else float("nan")


def choice_space(df: pd.DataFrame, hours_col: str, wage_col: str | None, label: str) -> str:
    if "is_chosen" in df.columns:
        chosen = df[df["is_chosen"] == 1]
    else:
        chosen = df
    lines = [f"### Choice space — {label} (chosen alternatives, n={len(chosen):,})", ""]
    if hours_col not in chosen.columns:
        return "\n".join(lines + [f"_hours column `{hours_col}` not found._", ""])
    h = pd.to_numeric(chosen[hours_col], errors="coerce").fillna(0.0).to_numpy()
    employed = float(np.mean(h > 0)) if h.size else float("nan")
    pt1_share = _band(h, *PT1)
    pt2_share = _band(h, *PT2)
    ft_share = _band(h, *FT)
    lines += [
        f"- Employment rate (h>0): **{employed:.3f}**",
        f"- Mass at h=0: **{float(np.mean(h == 0)):.3f}**",
        f"- In PT1 {PT1}: {pt1_share:.3f}   |   "
        f"PT2 {PT2}: {pt2_share:.3f}   |   FT {FT}: {ft_share:.3f}",
    ]
    # Flag mismatch with spec-contract bins
    if pt1_share == 0 and pt2_share == 0 and ft_share == 0 and employed > 0:
        lines.append("  > **FLAG: No observations in any contract focal bin. "
                     "Check hours column units or focal-bin definitions.**")
    hw = h[h > 0]
    if hw.size:
        qs = np.percentile(hw, [10, 25, 50, 75, 90])
        lines.append(
            "- Hours | working, quantiles "
            f"[p10,p25,p50,p75,p90]: {np.round(qs, 1).tolist()}"
        )
        # Coarse histogram to eyeball where peaks really are
        edges = [0.1, 10, 15, 18.5, 21.5, 25, 29.5, 30.5, 35, 37.5, 40.5, 45, 1e9]
        hist, _ = np.histogram(hw, bins=edges)
        share = np.round(hist / hw.size, 3)
        labels = ["0-10", "10-15", "15-18.5", "PT1", "21.5-25", "25-29.5",
                  "PT2", "30.5-35", "35-37.5", "FT", "40.5-45", "45+"]
        lines.append("- Hours histogram (working): "
                     + ", ".join(f"{l}:{s}" for l, s in zip(labels, share)))
        # Empirical peak detection — compare to contract bins
        max_idx = int(np.argmax(share))
        emp_peak_label = labels[max_idx]
        contract_peaks = {"PT1", "PT2", "FT"}
        if emp_peak_label not in contract_peaks:
            lines.append(
                f"  > **FLAG: Empirical peak bin is '{emp_peak_label}', not in "
                f"contract focal bins {{PT1, PT2, FT}}. "
                f"Report this mismatch; do NOT silently change the bins.**"
            )
    if wage_col and wage_col in chosen.columns:
        w = pd.to_numeric(chosen.loc[chosen[hours_col].astype(float) > 0, wage_col],
                          errors="coerce")
        w = w[np.isfinite(w)]
        if w.size:
            qs = np.percentile(w, [10, 25, 50, 75, 90])
            lines.append(
                "- Hourly wage | working, quantiles "
                f"[p10,p25,p50,p75,p90]: {np.round(qs, 2).tolist()}"
            )
    lines.append("")
    return "\n".join(lines)


def choice_space_info(df: pd.DataFrame, hours_col: str, label: str) -> dict:
    """Return dict with employment rate and focal-bin shares (for stdout summary)."""
    if "is_chosen" in df.columns:
        chosen = df[df["is_chosen"] == 1]
    else:
        chosen = df
    if hours_col not in chosen.columns:
        return {}
    h = pd.to_numeric(chosen[hours_col], errors="coerce").fillna(0.0).to_numpy()
    return {
        "label": label,
        "emp_rate": float(np.mean(h > 0)),
        "pt1": _band(h, *PT1),
        "pt2": _band(h, *PT2),
        "ft": _band(h, *FT),
    }


# ---------------------------------------------------------------------------
# 3. Within-role redundancy (NOT cross-role)
# ---------------------------------------------------------------------------
def within_role_corr(df: pd.DataFrame, cands: list[str], suffix: str = "") -> pd.DataFrame | None:
    cols = [c + suffix for c in cands]
    present = [c for c in cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    present = [c for c in present if df[c].nunique(dropna=True) > 1]
    if len(present) < 2:
        return None
    base = df[df["is_chosen"] == 1] if "is_chosen" in df.columns else df
    return base[present].corr().round(3)


# ---------------------------------------------------------------------------
# 4a. VIF per within-role block (NEW)
# ---------------------------------------------------------------------------
def _vif_numpy(X: np.ndarray) -> np.ndarray:
    """VIF via numpy OLS: for each column j, regress col j on all others, VIF = 1/(1-R^2)."""
    n, k = X.shape
    vifs = np.full(k, np.nan)
    for j in range(k):
        y = X[:, j]
        others_idx = [i for i in range(k) if i != j]
        if not others_idx:
            vifs[j] = 1.0
            continue
        Xo = np.column_stack([np.ones(n), X[:, others_idx]])
        try:
            coef, *_ = np.linalg.lstsq(Xo, y, rcond=None)
            y_hat = Xo @ coef
            ss_res = np.sum((y - y_hat) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            r2 = max(0.0, min(r2, 1.0 - 1e-12))
            vifs[j] = 1.0 / (1.0 - r2)
        except Exception:
            pass
    return vifs


def _poly_note(cols: list[str]) -> str | None:
    found = []
    for a, b in POLY_PAIRS:
        if a in cols and b in cols:
            found.append(f"`{a}` vs `{b}`")
    if found:
        return ("NOTE: Polynomial pairs " + ", ".join(found) +
                " are mechanically collinear — high VIF expected and acceptable.")
    return None


def within_role_vif(
    df: pd.DataFrame, cands: list[str], suffix: str = "", role_label: str = ""
) -> str:
    """Return a markdown block with VIF table for the given candidate set."""
    cols = [c + suffix for c in cands]
    base = df[df["is_chosen"] == 1] if "is_chosen" in df.columns else df
    present = [c for c in cols if c in base.columns and pd.api.types.is_numeric_dtype(base[c])]
    present = [c for c in present if base[c].nunique(dropna=True) > 1]
    if len(present) < 2:
        return f"_VIF [{role_label}]: fewer than 2 variables present — skipped._\n"

    arr = base[present].dropna().to_numpy(dtype=float)
    if arr.shape[0] < arr.shape[1] + 1:
        return f"_VIF [{role_label}]: insufficient observations — skipped._\n"

    vifs = _vif_numpy(arr)
    rows_md = []
    for col, vif in zip(present, vifs):
        flag = " ⚠ HIGH" if vif > 10 else ""
        rows_md.append(f"| {col} | {vif:.2f}{flag} |")

    note = _poly_note(present)
    lines = [
        f"**VIF — {role_label}** (n_obs={arr.shape[0]:,})",
        "",
        "| Variable | VIF |",
        "|---|---|",
    ] + rows_md + [""]
    if note:
        lines.append(note)
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4b. GSUR strength check (LPM) (NEW)
# ---------------------------------------------------------------------------
def gsur_strength_lpm(
    df: pd.DataFrame,
    emp_col: str,
    gsur_col: str,
    pref_shifters: list[str],
    label: str,
) -> str:
    """
    On chosen rows only: regress emp_col on gsur_col + pref_shifters via OLS (LPM).
    Reports coefficient, SE, t-stat, and sign for gsur_col.
    INTERPRETATION: strength check only — does gsur retain a meaningful,
    correctly-signed (negative) association with employment, conditional on
    preference shifters? This is NOT an identification claim.
    """
    if "is_chosen" in df.columns:
        base = df[df["is_chosen"] == 1].copy()
    else:
        base = df.copy()

    all_cols = [emp_col, gsur_col] + pref_shifters
    missing = [c for c in all_cols if c not in base.columns]
    if missing:
        return (f"_GSUR strength [{label}]: columns not found: "
                f"{missing} — skipped._\n")

    sub = base[all_cols].dropna()
    if len(sub) < 30:
        return f"_GSUR strength [{label}]: too few observations ({len(sub)}) — skipped._\n"

    y = sub[emp_col].to_numpy(dtype=float)
    regressors = [gsur_col] + pref_shifters
    X_raw = sub[regressors].to_numpy(dtype=float)
    # Drop constant shifters (edge case)
    var_mask = np.std(X_raw, axis=0) > 1e-10
    X_raw = X_raw[:, var_mask]
    regressors_kept = [r for r, m in zip(regressors, var_mask) if m]
    X = np.column_stack([np.ones(len(y)), X_raw])

    try:
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        y_hat = X @ coef
        resid = y - y_hat
        n, p = X.shape
        sigma2 = np.sum(resid ** 2) / max(n - p, 1)
        xtx_inv = np.linalg.pinv(X.T @ X)
        se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0.0))
    except Exception as e:
        return f"_GSUR strength [{label}]: OLS failed ({e})._\n"

    # gsur_col is the first regressor (index 1 in X with intercept prepended)
    gsur_in_kept = gsur_col in regressors_kept
    if not gsur_in_kept:
        return f"_GSUR strength [{label}]: gsur_col had zero variance — skipped._\n"

    g_idx = 1 + regressors_kept.index(gsur_col)
    g_coef = coef[g_idx]
    g_se = se[g_idx]
    g_t = g_coef / g_se if g_se > 0 else float("nan")
    sign_ok = g_coef < 0
    sign_str = "negative ✓ (as expected)" if sign_ok else "positive ✗ (unexpected sign)"

    lines = [
        f"**GSUR strength check — {label}** (LPM, OLS, chosen rows, n={len(sub):,})",
        "",
        f"- Outcome: `{emp_col}`",
        f"- GSUR column: `{gsur_col}`",
        f"- Controls: {regressors_kept[1:] if len(regressors_kept) > 1 else '(none after variance filter)'}",
        "",
        "| Statistic | Value |",
        "|---|---|",
        f"| Coefficient | {g_coef:.6f} |",
        f"| SE | {g_se:.6f} |",
        f"| t-stat | {g_t:.3f} |",
        f"| Sign | {sign_str} |",
        "",
        "> **Interpretation:** this is a STRENGTH CHECK only. A negative coefficient "
        "indicates the opportunity shifter (gsur) retains a meaningful association "
        "with employment conditional on preference shifters. This is NOT evidence "
        "of identification — that requires the Monte Carlo recovery test (§17 of "
        "the model spec contract).",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Driver for one group
# ---------------------------------------------------------------------------
def explore_group(df: pd.DataFrame, group: str, kept: set[str] | None, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    inv = profile_columns(df, kept)
    inv.to_csv(out_dir / f"variable_inventory_{group}.csv", index=False)

    md = [f"## {group}: pre-drop exploration", "",
          f"- Total columns in full frame: **{len(df.columns)}**, rows: **{len(df):,}**"]
    if kept is not None:
        n_kept = int((inv["status"] == "kept").sum())
        n_drop = int((inv["status"] == "dropped").sum())
        n_prom = int(inv["promote_candidate"].sum())
        md += [f"- Kept by whitelist: **{n_kept}**  |  Dropped: **{n_drop}**",
               f"- Dropped variables that are usable (<= {MISSING_OK:.0f}% missing, non-constant): "
               f"**{n_prom}** (promotion candidates)"]
    md.append("")

    summary_info: dict = {
        "group": group,
        "n_cols": len(df.columns),
        "n_rows": len(df),
        "n_kept": int((inv["status"] == "kept").sum()) if kept else None,
        "n_dropped": int((inv["status"] == "dropped").sum()) if kept else None,
        "n_promotable": int(inv["promote_candidate"].sum()) if kept else None,
        "choice_space": [],
        "gsur_signs": [],
    }

    if group == "singles":
        cs_text = choice_space(df, "hours", "wage", "singles")
        md.append(cs_text)
        summary_info["choice_space"].append(choice_space_info(df, "hours", "singles"))

        # EUROMOD output columns — explicitly named section
        md.append(euromod_outputs_section(df, kept, "singles", suffix=""))

        for name, cset, suf in [("preference", PREF_CANDIDATES, ""),
                                ("wage-opportunity", OPP_WAGE_CANDIDATES, ""),
                                ("hours-opportunity", OPP_HOURS_CANDIDATES, "")]:
            cm = within_role_corr(df, cset, suf)
            if cm is not None:
                md += [f"#### Within-role correlation — {name} candidates", "",
                       cm.to_markdown(), ""]

        # VIF blocks
        md += ["### Within-role VIF — singles", ""]
        for name, cset in [("preference", PREF_CANDIDATES),
                            ("wage-opportunity", OPP_WAGE_CANDIDATES),
                            ("hours-opportunity", OPP_HOURS_CANDIDATES)]:
            md.append(within_role_vif(df, cset, suffix="", role_label=f"{name} (singles)"))

        # GSUR strength
        md += ["### GSUR strength check — singles", ""]
        emp_col = "working" if "working" in df.columns else "is_chosen"
        gsur_col = "gsur"
        pref_shifters = [c for c in ["age_norm", "age_norm2", "educH", "n_children"]
                         if c in df.columns]
        gstr = gsur_strength_lpm(df, emp_col, gsur_col, pref_shifters, "singles")
        md.append(gstr)
        # Extract sign for stdout summary
        if "negative ✓" in gstr:
            summary_info["gsur_signs"].append(("singles", "negative (expected)"))
        elif "positive ✗" in gstr:
            summary_info["gsur_signs"].append(("singles", "positive (unexpected)"))
        else:
            summary_info["gsur_signs"].append(("singles", "n/a"))

    else:  # couples
        for g in ["male", "female"]:
            hours_col = f"hours_{g}"
            wage_col = f"wage_{g}"
            cs_text = choice_space(df, hours_col, wage_col, f"couples ({g})")
            md.append(cs_text)
            summary_info["choice_space"].append(
                choice_space_info(df, hours_col, f"couples_{g}")
            )

            for name, cset in [("preference", PREF_CANDIDATES),
                               ("wage-opportunity", OPP_WAGE_CANDIDATES),
                               ("hours-opportunity", OPP_HOURS_CANDIDATES)]:
                cm = within_role_corr(df, cset, f"_{g}")
                if cm is not None:
                    md += [f"#### Within-role correlation — {name} candidates ({g})", "",
                           cm.to_markdown(), ""]

        # EUROMOD output columns — couples (no gender suffix on _em cols themselves)
        md.append(euromod_outputs_section(df, kept, "couples", suffix=""))

        # VIF blocks (couples — per gender suffix)
        md += ["### Within-role VIF — couples", ""]
        for g in ["male", "female"]:
            for name, cset in [("preference", PREF_CANDIDATES),
                                ("wage-opportunity", OPP_WAGE_CANDIDATES),
                                ("hours-opportunity", OPP_HOURS_CANDIDATES)]:
                md.append(within_role_vif(
                    df, cset, suffix=f"_{g}",
                    role_label=f"{name} ({g})"
                ))

        # GSUR strength (per gender)
        md += ["### GSUR strength check — couples", ""]
        for g in ["male", "female"]:
            emp_col = f"working_{g}" if f"working_{g}" in df.columns else "is_chosen"
            gsur_col = f"gsur_{g}"
            pref_shifters = [c for c in [
                f"age_norm_{g}", f"age_norm2_{g}", f"educH_{g}", "n_children"
            ] if c in df.columns]
            gstr = gsur_strength_lpm(df, emp_col, gsur_col, pref_shifters,
                                     f"couples ({g})")
            md.append(gstr)
            if "negative ✓" in gstr:
                summary_info["gsur_signs"].append((f"couples_{g}", "negative (expected)"))
            elif "positive ✗" in gstr:
                summary_info["gsur_signs"].append((f"couples_{g}", "positive (unexpected)"))
            else:
                summary_info["gsur_signs"].append((f"couples_{g}", "n/a"))

    # Promotion shortlist
    if kept is not None:
        short = inv[inv["promote_candidate"]].head(40)
        md += ["### Promotion shortlist (DROPPED but usable — decide role on ECONOMIC grounds)",
               "", short[["column", "dtype", "pct_missing", "n_unique"]].to_markdown(index=False),
               "", "_These are candidates only. Promote by editing the whitelist with a written "
               "economic reason; data cannot assign a variable to preferences vs opportunity._", ""]

    (out_dir / f"explore_{group}.md").write_text("\n".join(md), encoding="utf-8")
    return {"inventory": inv, "summary": summary_info, "md": "\n".join(md)}


# ---------------------------------------------------------------------------
# Consolidated audit report writer
# ---------------------------------------------------------------------------
def write_audit_report(
    audit_out: Path,
    singles_result: dict | None,
    couples_result: dict | None,
    singles_path: str | None,
    couples_path: str | None,
) -> None:
    today = datetime.date.today().isoformat()
    lines = [
        "# RURO Data Audit v1",
        "",
        f"**Date:** {today}",
        "",
        "## Paths",
        "",
        f"- Singles pre-drop dump: `{singles_path or 'not provided'}`",
        f"- Couples pre-drop dump: `{couples_path or 'not provided'}`",
        "",
        "## Spec-Contract Focal Bins (§5 of RURO_model_spec_contract_v1.md)",
        "",
        f"- PT1: h ∈ {PT1}  (20-hour peak)",
        f"- PT2: h ∈ {PT2}  (30-hour peak)",
        f"- FT:  h ∈ {FT}  (38-40 hour peak)",
        "",
        "---",
        "",
    ]

    # Per-group summary with explicit EUROMOD column breakdown
    lines += ["## Coverage Summary", ""]
    for res in [singles_result, couples_result]:
        if res is None:
            continue
        s = res["summary"]
        inv = res["inventory"]
        n_em = int((inv.get("category", pd.Series()) == "euromod_output").sum()) if "category" in inv.columns else "?"
        n_em_kept = int(((inv.get("category", pd.Series()) == "euromod_output") & (inv["status"] == "kept")).sum()) if "category" in inv.columns else "?"
        n_other_dropped = int((inv.get("category", pd.Series()) == "dropped_other").sum()) if "category" in inv.columns else "?"
        lines += [
            f"### {s['group'].capitalize()}",
            "",
            f"- Total columns (unfiltered frame): **{s['n_cols']}**, rows: **{s['n_rows']:,}**",
            f"- Kept by whitelist: **{s['n_kept']}**",
            f"- EUROMOD counterfactual `_em` columns: **{n_em}** "
            f"(kept: **{n_em_kept}**, dropped decomposition: **{n_em - n_em_kept if isinstance(n_em, int) and isinstance(n_em_kept, int) else '?'}**)",
            f"- Other dropped (EUROMOD inputs, pipeline intermediates): **{n_other_dropped}**",
            f"- Promotable (dropped_other, usable, non-constant): **{s['n_promotable']}**",
            "",
            "> **EUROMOD `_em` columns** are the tax-benefit calculations run on every "
            "draw alternative. Only `ils_dispy_em` (→ `consumption`) enters the "
            "estimation whitelist. The other `_em` columns are the accounting "
            "decomposition (earnings, taxes, benefits, social contributions); they "
            "are kept in the pre-drop dump for welfare analysis but dropped from "
            "the estimation parquet.",
            "",
        ]

    lines += ["---", "", "## Choice-Space and Full Group Blocks", ""]
    for res in [singles_result, couples_result]:
        if res is None:
            continue
        lines.append(res["md"])
        lines.append("")

    lines += ["---", ""]

    audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit_out.write_text("\n".join(lines), encoding="utf-8")
    logging.info("Wrote consolidated audit report: %s", audit_out)


# ---------------------------------------------------------------------------
# Self-check on synthetic data (run before real data)
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """Quick smoke-test of all functions on a tiny synthetic frame."""
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "is_chosen": ([1] + [0] * 99) * 2,  # 2 households, 100 alternatives each
        "idhh": np.repeat([1, 2], 100),
        "hours": np.concatenate([
            np.array([0.0] * 20 + [20.0] * 10 + [30.0] * 10 + [38.0] * 60),
            np.array([0.0] * 20 + [20.0] * 10 + [30.0] * 10 + [38.0] * 60),
        ]),
        "wage": rng.uniform(8, 30, n),
        "age_norm": rng.standard_normal(n),
        "age_norm2": rng.standard_normal(n) ** 2,
        "educH": rng.integers(0, 2, n).astype(float),
        "educL": rng.integers(0, 2, n).astype(float),
        "n_children": rng.integers(0, 3, n).astype(float),
        "pexp_years": rng.uniform(0, 30, n),
        "pexp_years2": rng.uniform(0, 30, n) ** 2,
        "gsur": rng.uniform(0.05, 0.20, n),
        "working": (rng.uniform(size=n) > 0.3).astype(float),
    })

    # Profile
    inv = profile_columns(df, kept={"hours", "wage", "is_chosen", "idhh"})
    assert "column" in inv.columns
    assert "promote_candidate" in inv.columns

    # Choice space
    cs = choice_space(df, "hours", "wage", "synthetic")
    assert "Employment rate" in cs

    # Within-role corr
    cm = within_role_corr(df, PREF_CANDIDATES)
    assert cm is not None

    # VIF
    vif_txt = within_role_vif(df, PREF_CANDIDATES, suffix="", role_label="test")
    assert "VIF" in vif_txt

    # GSUR strength — run on a frame without is_chosen so the full n=200 is used
    df_nofilter = df.drop(columns=["is_chosen"])
    gs = gsur_strength_lpm(
        df_nofilter, "working", "gsur",
        ["age_norm", "age_norm2", "educH", "n_children"], "synthetic"
    )
    assert "Coefficient" in gs

    logging.info("Self-check passed on synthetic frame.")


def parse_args():
    p = argparse.ArgumentParser(description="Pre-drop RURO data exploration.")
    p.add_argument("--full-singles", default=None)
    p.add_argument("--full-couples", default=None)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--prep-dir", default=None,
                   help="Dir containing enh_RURO_prep_mnl_basic.py (for the whitelist).")
    p.add_argument("--audit-out", default=None,
                   help="If set, write ONE consolidated markdown audit report to this path.")
    return p.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()
    out_dir = Path(args.out_dir)
    kept = load_kept_columns(Path(args.prep_dir) if args.prep_dir else None)

    # Self-check before touching real data
    _self_check()

    singles_result = None
    couples_result = None

    for grp, path in [("singles", args.full_singles), ("couples", args.full_couples)]:
        if not path:
            continue
        p = Path(path)
        if not p.exists():
            logging.warning("Missing %s frame: %s", grp, p)
            continue
        df = pd.read_parquet(p)
        logging.info("Loaded %s: %d rows x %d cols", grp, len(df), len(df.columns))
        result = explore_group(df, grp, kept, out_dir)
        if grp == "singles":
            singles_result = result
        else:
            couples_result = result

    # Write per-group summary file (existing behaviour)
    summary_lines = ["# RURO pre-drop exploration", ""]
    for grp, res in [("singles", singles_result), ("couples", couples_result)]:
        if res is None:
            continue
        summary_lines.append(
            f"- {grp}: see `explore_{grp}.md` and `variable_inventory_{grp}.csv`"
        )
    (out_dir / "explore_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    logging.info("Wrote per-group exploration files to %s", out_dir)

    # Consolidated audit report
    if args.audit_out:
        write_audit_report(
            Path(args.audit_out),
            singles_result,
            couples_result,
            args.full_singles,
            args.full_couples,
        )

    # Stdout 10-line summary
    print("\n" + "=" * 70)
    print("RURO PRE-DROP AUDIT — STDOUT SUMMARY")
    print("=" * 70)
    for res in [singles_result, couples_result]:
        if res is None:
            continue
        s = res["summary"]
        kept_str = f"kept={s['n_kept']}" if s["n_kept"] is not None else "kept=?"
        drop_str = f"dropped={s['n_dropped']}" if s["n_dropped"] is not None else ""
        prom_str = f"promotable={s['n_promotable']}" if s["n_promotable"] is not None else ""
        print(f"[{s['group']:8s}] {kept_str}  {drop_str}  {prom_str}")
        for cs in s["choice_space"]:
            print(f"           choice-space {cs.get('label','')}: "
                  f"emp={cs.get('emp_rate', float('nan')):.3f}  "
                  f"PT1={cs.get('pt1', float('nan')):.3f}  "
                  f"PT2={cs.get('pt2', float('nan')):.3f}  "
                  f"FT={cs.get('ft', float('nan')):.3f}  "
                  f"(contract: PT1={PT1}, PT2={PT2}, FT={FT})")
        for label, sign in s["gsur_signs"]:
            print(f"           gsur [{label}]: {sign}")
    print("=" * 70)


if __name__ == "__main__":
    main()