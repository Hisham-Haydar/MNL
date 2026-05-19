"""
m1_isf_check_2018.py
====================

FRANCE-2018-SPECIFIC RESEARCH WRAPPER
--------------------------------------
This script is intentionally country- and year-specific. It implements the
ISF / tpr comparability check that is required before activating the France
P3b robustness branch (2015+2016+2018). It is NOT a reusable Stage M1 script
and does NOT accept --stage-config. A corresponding country-agnostic version
would require a separate design for the ISF-concept check. This script will
remain France-specific until that design is undertaken.

Stage M1 — ISF / tpr comparability check for the 2018 robustness branch (P3b).

Implements the four required steps from §16 of the Stage M1 plan:

  1. Compute the distribution of tpr in the FR_2018 EUROMOD output for the
     RURO sample.  Report the share with tpr > 0 and the 90th / 95th / 99th
     percentile (in 2016 euros).

  2. Compute implied impact on ils_dispy: Δils_dispy = −tpr.  Report the
     share of households affected and the mean / maximum absolute impact.

  3. Re-run the ils_dispy comparability check comparing 2018 against 2016 and
     2017 after stripping tpr from 2018 ils_dispy.

  4. Write Results/M1_ISF_tpr_comparability_check_2018.md.  The memo must
     conclude with one of:
       - "ISF impact negligible: proceed with P3b."
       - "ISF impact non-negligible: P3b requires income-concept adjustment."
       - "ISF impact non-negligible: P3b not recommended."

IMPORTANT — gate condition:
    This script must NOT be run until the FR_2018 EUROMOD output parquet is
    available.  It will abort with a clear error if the 2018 file is missing.

    P3b remains blocked until this memo concludes "proceed with P3b".

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §16, 19.

Usage
-----
    python scripts/multi_year/m1_isf_check_2018.py \\
        --euromod-2018 path/to/fr_2018_RURO_mnl*.parquet \\
        [--euromod-2016 path/to/fr_2016_RURO_mnl*.parquet] \\
        [--euromod-2017 path/to/fr_2017_RURO_mnl*.parquet] \\
        [--phi-2018 0.9682]
    python scripts/multi_year/m1_isf_check_2018.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# Ensure stdout/stderr can handle UTF-8 symbols on Windows cp1252 consoles.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf-8-sig"):
    import io  # noqa: F811
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO / "Results"
POOLED_DIR = REPO / "Data" / "processed" / "fr" / "pooled"
EXTERNAL_DIR = REPO / "Data" / "external"

# HICP φ_2018 from HICPCONFIG.xml (base 2015=100): 100.31/103.60
# Used to convert 2018 nominal to 2016 prices if a CPI file is unavailable.
DEFAULT_PHI_2018 = 100.31 / 103.60  # 0.96825...

# Negligibility threshold: if mean |Δils_dispy/ils_dispy| < this, ISF is negligible
NEGLIGIBILITY_THRESHOLD = 0.005  # 0.5% of disposable income

# KS-test threshold for ils_dispy distribution comparison
# (not imported — we use a simple quantile comparison instead to avoid scipy dep)
QUANTILE_LEVELS = [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_parquet(year: int) -> Optional[Path]:
    """Search Data/processed/fr/ for the MNL parquet for a given year."""
    processed = REPO / "Data" / "processed" / "fr"
    patterns = [
        f"*{year}*RURO*mnl*job*gmm*.parquet",
        f"*{year}*RURO*mnl*job*.parquet",
        f"*{year}*RURO*mnl*.parquet",
    ]
    for pat in patterns:
        candidates = sorted(processed.glob(pat))
        combined = [p for p in candidates
                    if "combined" in p.name.lower()
                    or ("singles" not in p.name.lower()
                        and "couples" not in p.name.lower())]
        if combined:
            return combined[0]
        if candidates:
            return candidates[0]
    return None


def _load_ruro_sample(path: Path) -> pd.DataFrame:
    """Load MNL parquet and validate minimum required columns."""
    df = pd.read_parquet(path)
    required = {"idhh", "idperson"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Required columns missing from {path}: {missing}")
    return df


# ---------------------------------------------------------------------------
# Step 1 — tpr distribution
# ---------------------------------------------------------------------------

def _step1_tpr_distribution(df_2018: pd.DataFrame, phi_2018: float) -> dict:
    """
    Compute tpr distribution in the RURO 2018 sample.

    Returns dict with: n_hh, n_hh_tpr_positive, share_tpr_positive,
    percentiles (in 2016 euros), mean_tpr_real, max_tpr_real.
    """
    # tpr may be on person or household level; collapse to household
    if "tpr" not in df_2018.columns:
        return {
            "tpr_present": False,
            "note": "Column 'tpr' not found in 2018 parquet. "
                    "Check EUROMOD output; tpr should be present in FR_2018.",
        }

    hh_level = (
        df_2018.groupby("idhh")["tpr"]
        .first()  # tpr is household-level; take first person row
        .reset_index()
    )
    hh_level["tpr_real"] = hh_level["tpr"] * phi_2018

    n_hh = len(hh_level)
    pos = hh_level["tpr_real"] > 0
    n_pos = int(pos.sum())
    share_pos = float(n_pos / n_hh) if n_hh > 0 else 0.0

    quantiles = {}
    for q in [0.90, 0.95, 0.99]:
        quantiles[f"p{int(q*100)}"] = float(hh_level.loc[pos, "tpr_real"].quantile(q)) if n_pos > 0 else 0.0

    return {
        "tpr_present": True,
        "n_hh": n_hh,
        "n_hh_tpr_positive": n_pos,
        "share_tpr_positive": share_pos,
        "mean_tpr_real_all": float(hh_level["tpr_real"].mean()),
        "mean_tpr_real_affected": float(hh_level.loc[pos, "tpr_real"].mean()) if n_pos > 0 else 0.0,
        "max_tpr_real": float(hh_level["tpr_real"].max()),
        "quantiles_tpr_real_affected": quantiles,
    }


# ---------------------------------------------------------------------------
# Step 2 — impact on ils_dispy
# ---------------------------------------------------------------------------

def _step2_ils_dispy_impact(df_2018: pd.DataFrame, phi_2018: float) -> dict:
    """
    Compute Δils_dispy = −tpr impact on RURO-sample households.
    """
    if "tpr" not in df_2018.columns or "ils_dispy" not in df_2018.columns:
        return {
            "computable": False,
            "note": "Cannot compute ils_dispy impact: 'tpr' and/or 'ils_dispy' missing.",
        }

    hh = df_2018.groupby("idhh").first().reset_index()
    hh["tpr_real"] = hh["tpr"] * phi_2018
    hh["ils_dispy_real"] = hh["ils_dispy"] * phi_2018
    hh["ils_dispy_stripped_real"] = (hh["ils_dispy"] + hh["tpr"]) * phi_2018

    pos = hh["tpr_real"] > 0
    n_affected = int(pos.sum())
    n_hh = len(hh)

    if n_affected > 0:
        rel_impact = (
            hh.loc[pos, "tpr_real"] / hh.loc[pos, "ils_dispy_real"].abs()
        ).replace([np.inf, -np.inf], np.nan).dropna()
        mean_rel = float(rel_impact.mean())
        max_rel = float(rel_impact.max())
    else:
        mean_rel = 0.0
        max_rel = 0.0

    negligible = mean_rel < NEGLIGIBILITY_THRESHOLD

    return {
        "computable": True,
        "n_hh": n_hh,
        "n_hh_affected": n_affected,
        "share_affected": float(n_affected / n_hh) if n_hh > 0 else 0.0,
        "mean_abs_tpr_real": float(hh.loc[pos, "tpr_real"].mean()) if n_affected > 0 else 0.0,
        "max_abs_tpr_real": float(hh["tpr_real"].max()),
        "mean_rel_impact": mean_rel,
        "max_rel_impact": max_rel,
        "negligibility_threshold": NEGLIGIBILITY_THRESHOLD,
        "impact_negligible": negligible,
    }


# ---------------------------------------------------------------------------
# Step 3 — ils_dispy comparability
# ---------------------------------------------------------------------------

def _step3_comparability(
    df_2018: pd.DataFrame,
    df_2016: Optional[pd.DataFrame],
    df_2017: Optional[pd.DataFrame],
    phi_2018: float,
    phi_2016: float = 1.0000,
    phi_2017: float = 0.9886,
) -> dict:
    """
    Compare 2018 ils_dispy distribution (with and without tpr) against 2016/2017.
    """
    results: dict = {}

    if "ils_dispy" not in df_2018.columns:
        return {"computable": False, "note": "'ils_dispy' not found in 2018 parquet."}

    hh_2018 = df_2018.groupby("idhh").first().reset_index()
    hh_2018["ils_dispy_real_2018"] = hh_2018["ils_dispy"] * phi_2018
    if "tpr" in hh_2018.columns:
        hh_2018["ils_dispy_real_stripped"] = (hh_2018["ils_dispy"] + hh_2018["tpr"]) * phi_2018
    else:
        hh_2018["ils_dispy_real_stripped"] = hh_2018["ils_dispy_real_2018"]

    def _quantile_table(s: pd.Series, label: str) -> dict:
        return {
            f"{label}_q{int(q*100)}": float(s.quantile(q))
            for q in QUANTILE_LEVELS
        }

    results["2018_with_tpr"] = _quantile_table(hh_2018["ils_dispy_real_2018"], "q")
    results["2018_stripped"] = _quantile_table(hh_2018["ils_dispy_real_stripped"], "q")

    for yr, df_yr, phi_yr in [(2016, df_2016, phi_2016), (2017, df_2017, phi_2017)]:
        if df_yr is None:
            results[f"{yr}_available"] = False
            continue
        if "ils_dispy" not in df_yr.columns:
            results[f"{yr}_available"] = False
            results[f"{yr}_note"] = "'ils_dispy' not found"
            continue
        hh_yr = df_yr.groupby("idhh").first().reset_index()
        hh_yr["ils_dispy_real"] = hh_yr["ils_dispy"] * phi_yr
        results[f"{yr}_available"] = True
        results[f"{yr}_dist"] = _quantile_table(hh_yr["ils_dispy_real"], "q")

        # Median difference as comparability check
        med_2018_stripped = float(hh_2018["ils_dispy_real_stripped"].median())
        med_yr = float(hh_yr["ils_dispy_real"].median())
        diff_pct = (med_2018_stripped - med_yr) / med_yr * 100 if med_yr != 0 else float("nan")
        results[f"median_diff_2018_stripped_vs_{yr}_pct"] = diff_pct

    results["computable"] = True
    return results


# ---------------------------------------------------------------------------
# Conclusion
# ---------------------------------------------------------------------------

def _determine_conclusion(step2: dict) -> str:
    if not step2.get("computable", False):
        return "INCONCLUSIVE: Could not compute ISF impact (missing columns)."

    if step2.get("impact_negligible", False):
        return "ISF impact negligible: proceed with P3b."
    elif step2.get("share_affected", 0) < 0.01:
        return (
            "ISF impact non-negligible for the small fraction of affected households, "
            "but population-level impact is below 1%. "
            "Consider: ISF impact non-negligible: P3b requires income-concept adjustment "
            "(strip tpr from ils_dispy in 2018 before pooling)."
        )
    else:
        return (
            "ISF impact non-negligible: P3b requires income-concept adjustment "
            "(strip tpr from ils_dispy in 2018 before pooling, "
            "or exclude 2018 tpr-affected households from RURO sample)."
        )


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _write_report(
    step1: dict,
    step2: dict,
    step3: dict,
    conclusion: str,
    phi_2018: float,
    out_path: Path,
    ts: str,
) -> None:
    lines = [
        "# M1 ISF / tpr Comparability Check — FR_2018",
        "",
        f"**Generated:** {ts}",
        f"**φ_2018 used:** {phi_2018:.6f} (converts 2018 nominal to 2016 prices)",
        f"**Reference:** §16 of JMP_multi_year_stage_M1_implementation_plan_v2.md",
        "",
        "---",
        "",
        "## Step 1 — tpr Distribution in FR_2018 RURO Sample",
        "",
    ]

    if not step1.get("tpr_present", False):
        lines.append(f"> **{step1.get('note', 'tpr not present')}**")
    else:
        lines += [
            f"| Metric | Value |",
            "| --- | --- |",
            f"| Households in RURO sample | {step1['n_hh']:,} |",
            f"| Households with tpr > 0 | {step1['n_hh_tpr_positive']:,} "
            f"({step1['share_tpr_positive']:.4%}) |",
            f"| Mean tpr (all, 2016 €) | {step1['mean_tpr_real_all']:,.0f} |",
            f"| Mean tpr (affected, 2016 €) | {step1['mean_tpr_real_affected']:,.0f} |",
            f"| Max tpr (2016 €) | {step1['max_tpr_real']:,.0f} |",
        ]
        for k, v in step1.get("quantiles_tpr_real_affected", {}).items():
            lines.append(f"| {k} tpr (affected, 2016 €) | {v:,.0f} |")

    lines += [
        "",
        "---",
        "",
        "## Step 2 — Impact on ils_dispy",
        "",
    ]

    if not step2.get("computable", False):
        lines.append(f"> **{step2.get('note', 'Could not compute')}**")
    else:
        lines += [
            "| Metric | Value |",
            "| --- | --- |",
            f"| Households affected (tpr > 0) | {step2['n_hh_affected']:,} "
            f"({step2['share_affected']:.4%}) |",
            f"| Mean |Δils_dispy| (2016 €) | {step2['mean_abs_tpr_real']:,.0f} |",
            f"| Max |Δils_dispy| (2016 €) | {step2['max_abs_tpr_real']:,.0f} |",
            f"| Mean relative impact (affected) | {step2['mean_rel_impact']:.4%} |",
            f"| Max relative impact (affected) | {step2['max_rel_impact']:.4%} |",
            f"| Negligibility threshold | {step2['negligibility_threshold']:.4%} |",
            f"| Impact negligible? | {'YES' if step2['impact_negligible'] else 'NO'} |",
        ]

    lines += [
        "",
        "---",
        "",
        "## Step 3 — ils_dispy Comparability (2018 vs 2016 and 2017)",
        "",
    ]

    if not step3.get("computable", False):
        lines.append(f"> **{step3.get('note', 'Could not compute')}**")
    else:
        lines.append(
            "Quantile comparison of ils_dispy in 2016 prices. "
            "'2018 stripped' = 2018 ils_dispy with tpr added back (ISF removed)."
        )
        lines.append("")
        q_cols = [f"q{int(q*100)}" for q in QUANTILE_LEVELS]
        header = "| Quantile | 2018 with tpr | 2018 stripped |"
        sep = "| --- | --- | --- |"
        if step3.get("2016_available"):
            header += " 2016 |"
            sep += " --- |"
        if step3.get("2017_available"):
            header += " 2017 |"
            sep += " --- |"
        lines += [header, sep]

        for qc in q_cols:
            row = f"| {qc} |"
            row += f" {step3['2018_with_tpr'].get(f'q_{qc}', step3['2018_with_tpr'].get(qc, 'N/A')):,.0f} |"
            row += f" {step3['2018_stripped'].get(f'q_{qc}', step3['2018_stripped'].get(qc, 'N/A')):,.0f} |"
            if step3.get("2016_available"):
                row += f" {step3['2016_dist'].get(f'q_{qc}', step3['2016_dist'].get(qc, 'N/A')):,.0f} |"
            if step3.get("2017_available"):
                row += f" {step3['2017_dist'].get(f'q_{qc}', step3['2017_dist'].get(qc, 'N/A')):,.0f} |"
            lines.append(row)

        lines.append("")
        for yr in [2016, 2017]:
            key = f"median_diff_2018_stripped_vs_{yr}_pct"
            if key in step3:
                lines.append(
                    f"Median difference (2018 stripped vs {yr}): "
                    f"{step3[key]:+.2f}%"
                )
        lines.append("")

    lines += [
        "---",
        "",
        "## Conclusion",
        "",
        f"> {conclusion}",
        "",
        "---",
        "",
        "## P3b Activation Decision",
        "",
    ]

    if "proceed with p3b" in conclusion.lower():
        lines.append(
            "**P3b is cleared for activation.** "
            "Run `m1_stack_years.py --config p3b` after this memo is saved."
        )
    else:
        lines.append(
            "**P3b remains blocked.** "
            "Address the income-concept issue described in the conclusion above "
            "before running `m1_stack_years.py --config p3b`."
        )
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("ISF check report written: %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_isf_check(
    euromod_2018: str,
    euromod_2016: Optional[str] = None,
    euromod_2017: Optional[str] = None,
    phi_2018: float = DEFAULT_PHI_2018,
    phi_2016: float = 1.0000,
    phi_2017: float = 0.9886,
) -> None:
    path_2018 = Path(euromod_2018)
    if not path_2018.exists():
        raise FileNotFoundError(
            f"FR_2018 EUROMOD parquet not found: {path_2018}\n"
            "P3b activation is blocked until FR_2018 EUROMOD output is produced."
        )

    LOGGER.info("Loading FR_2018: %s", path_2018)
    df_2018 = _load_ruro_sample(path_2018)

    df_2016 = None
    df_2017 = None

    if euromod_2016:
        p = Path(euromod_2016)
        if p.exists():
            LOGGER.info("Loading FR_2016: %s", p)
            df_2016 = _load_ruro_sample(p)
        else:
            LOGGER.warning("FR_2016 path not found: %s — comparability step will skip 2016", p)
    else:
        # Try auto-detection
        p = _find_parquet(2016)
        if p:
            LOGGER.info("Auto-detected FR_2016: %s", p)
            df_2016 = _load_ruro_sample(p)

    if euromod_2017:
        p = Path(euromod_2017)
        if p.exists():
            LOGGER.info("Loading FR_2017: %s", p)
            df_2017 = _load_ruro_sample(p)
        else:
            LOGGER.warning("FR_2017 path not found: %s — comparability step will skip 2017", p)
    else:
        p = _find_parquet(2017)
        if p:
            LOGGER.info("Auto-detected FR_2017: %s", p)
            df_2017 = _load_ruro_sample(p)

    LOGGER.info("Running Step 1 — tpr distribution ...")
    step1 = _step1_tpr_distribution(df_2018, phi_2018)

    LOGGER.info("Running Step 2 — ils_dispy impact ...")
    step2 = _step2_ils_dispy_impact(df_2018, phi_2018)

    LOGGER.info("Running Step 3 — comparability ...")
    step3 = _step3_comparability(df_2018, df_2016, df_2017, phi_2018, phi_2016, phi_2017)

    conclusion = _determine_conclusion(step2)
    LOGGER.info("Conclusion: %s", conclusion)

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / "M1_ISF_tpr_comparability_check_2018.md"
    _write_report(step1, step2, step3, conclusion, phi_2018, out_path, ts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 ISF/tpr comparability check for 2018 (P3b gate). "
            "Writes Results/M1_ISF_tpr_comparability_check_2018.md. "
            "Do NOT run until FR_2018 EUROMOD output is available."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--euromod-2018",
        type=str,
        required=True,
        help="Path to FR_2018 RURO MNL parquet (EUROMOD output).",
    )
    ap.add_argument(
        "--euromod-2016",
        type=str,
        default=None,
        help="Path to FR_2016 RURO MNL parquet (for comparability step). "
             "Auto-detected if not supplied.",
    )
    ap.add_argument(
        "--euromod-2017",
        type=str,
        default=None,
        help="Path to FR_2017 RURO MNL parquet (for comparability step). "
             "Auto-detected if not supplied.",
    )
    ap.add_argument(
        "--phi-2018",
        type=float,
        default=DEFAULT_PHI_2018,
        help=f"CPI deflation factor phi_2018 (default: {DEFAULT_PHI_2018:.6f} from HICP). "
             "Override with the authorised value from cpi_hicp_fr_harmonisation.csv.",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging.",
    )
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(message)s",
    )
    try:
        run_isf_check(
            euromod_2018=args.euromod_2018,
            euromod_2016=args.euromod_2016,
            euromod_2017=args.euromod_2017,
            phi_2018=args.phi_2018,
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()