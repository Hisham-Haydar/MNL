"""
m1_identity_validation.py
=========================

Stage M1 — repeated-person and repeated-household identity diagnostics.

Reads a stacked-raw pooled parquet (output of m1_stack_years.py) and runs
identity-validation checks on all year-pairs that share observations.
Produces Results/M1_identity_validation_summary.md.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §13, 18.

Thresholds (§13):
    sex_stability    >= 99.90%  repeat persons    warn if below; do not block
    age_progression  >= 99.50%  within ±1 of gap  warn if below; do not block
    suspicious       <= 0.20%   sex|age off       warn if exceeded
                     >  1.00%                     block (exit 1)
    hh_continuity    >= 97.00%  idorighh stable   warn if below; do not block

Diagnostics are computed on idorigperson (person key) and idorighh
(household key), exactly as done in addendum v2.

Usage
-----
    python scripts/multi_year/m1_identity_validation.py --config p3a
    python scripts/multi_year/m1_identity_validation.py \\
        --file path/to/fr_p3a_stacked_raw.parquet [--config p3a]
    python scripts/multi_year/m1_identity_validation.py --help
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
POOLED_DIR = REPO / "Data" / "processed" / "fr" / "pooled"
RESULTS_DIR = REPO / "Results"

YEAR_TAG: Dict[int, int] = {2015: 1, 2016: 2, 2017: 3, 2018: 4}
TAG_YEAR: Dict[int, int] = {v: k for k, v in YEAR_TAG.items()}

# §13 thresholds
THRESHOLDS = {
    "sex_stability_min":      0.9990,
    "age_progression_min":    0.9950,
    "suspicious_warn_max":    0.0020,
    "suspicious_block_max":   0.0100,
    "hh_continuity_min":      0.9700,
}

# Expected overlap counts from addendum v2 (for reference / sanity)
EXPECTED_OVERLAPS: Dict[Tuple[int, int], int] = {
    (2015, 2016): 0,
    (2015, 2017): 0,
    (2015, 2018): 0,
    (2016, 2017): 8_796,
    (2016, 2018): 7_065,
    (2017, 2018): 8_521,
}


# ---------------------------------------------------------------------------
# Per-pair diagnostics
# ---------------------------------------------------------------------------

def _diagnose_pair(
    df: pd.DataFrame,
    yr1: int,
    yr2: int,
) -> dict:
    """
    Run identity diagnostics on one year pair.

    Returns a dict with all metrics and pass/fail/warn outcomes.
    """
    tag1 = YEAR_TAG[yr1]
    tag2 = YEAR_TAG[yr2]

    sub1 = df[df["year_tag"] == tag1].copy()
    sub2 = df[df["year_tag"] == tag2].copy()

    persons1 = set(sub1["idorigperson"])
    persons2 = set(sub2["idorigperson"])
    repeat_persons = persons1 & persons2
    n_repeat = len(repeat_persons)

    hh1 = set(sub1["idorighh"])
    hh2 = set(sub2["idorighh"])
    repeat_hh = len(hh1 & hh2)

    result: dict = {
        "pair": f"{yr1}→{yr2}",
        "yr1": yr1,
        "yr2": yr2,
        "n_persons_yr1": len(sub1),
        "n_persons_yr2": len(sub2),
        "n_repeat_persons": n_repeat,
        "n_repeat_households": repeat_hh,
        "expected_repeat_hh": EXPECTED_OVERLAPS.get((yr1, yr2), "unknown"),
        "outcomes": [],
        "warnings": [],
        "blocked": False,
    }

    if n_repeat == 0:
        result["outcomes"].append("PASS (no repeat persons — disjoint panel)")
        return result

    # Build aligned repeat-person sub-DataFrames
    s1 = sub1[sub1["idorigperson"].isin(repeat_persons)].set_index("idorigperson")
    s2 = sub2[sub2["idorigperson"].isin(repeat_persons)].set_index("idorigperson")
    common_idx = s1.index.intersection(s2.index)
    s1 = s1.loc[common_idx]
    s2 = s2.loc[common_idx]

    gap = yr2 - yr1
    result["expected_age_gap"] = gap

    # Sex stability
    if "dgn" in s1.columns and "dgn" in s2.columns:
        sex_ok = float((s1["dgn"] == s2["dgn"]).mean())
        result["sex_stability"] = sex_ok
        if sex_ok < THRESHOLDS["sex_stability_min"]:
            result["warnings"].append(
                f"sex_stability {sex_ok:.4f} < {THRESHOLDS['sex_stability_min']}"
            )
        else:
            result["outcomes"].append(f"sex_stability={sex_ok:.4f} ✓")
    else:
        result["sex_stability"] = None
        result["warnings"].append("'dgn' column missing; sex stability not checked")
        sex_ok = 1.0  # treat as stable for suspicious-record calculation

    # Age progression
    if "dag" in s1.columns and "dag" in s2.columns:
        delta_dag = s2["dag"] - s1["dag"]
        pct_exact = float((delta_dag == gap).mean())
        pct_within1 = float(((delta_dag - gap).abs() <= 1).mean())
        result["age_pct_exact"] = pct_exact
        result["age_pct_within1"] = pct_within1

        # Δdag distribution
        result["delta_dag_dist"] = (
            delta_dag.value_counts().sort_index().head(10).to_dict()
        )

        if pct_within1 < THRESHOLDS["age_progression_min"]:
            result["warnings"].append(
                f"age_progression within±1: {pct_within1:.4f} < "
                f"{THRESHOLDS['age_progression_min']}"
            )
        else:
            result["outcomes"].append(
                f"age_progression_within1={pct_within1:.4f} ✓"
            )

        # Suspicious records
        sex_mismatch = (s1["dgn"] != s2["dgn"]) if "dgn" in s1.columns else pd.Series(False, index=s1.index)
        age_off = (delta_dag - gap).abs() > 1
        suspicious = sex_mismatch | age_off
        susp_rate = float(suspicious.mean())
        result["suspicious_rate"] = susp_rate
        result["suspicious_count"] = int(suspicious.sum())

        if susp_rate > THRESHOLDS["suspicious_block_max"]:
            result["blocked"] = True
            result["outcomes"].append(
                f"FAIL: suspicious_rate={susp_rate:.4f} > BLOCK threshold "
                f"{THRESHOLDS['suspicious_block_max']}"
            )
        elif susp_rate > THRESHOLDS["suspicious_warn_max"]:
            result["warnings"].append(
                f"suspicious_rate={susp_rate:.4f} > warn threshold "
                f"{THRESHOLDS['suspicious_warn_max']}"
            )
            result["outcomes"].append(f"suspicious_rate={susp_rate:.4f} WARN")
        else:
            result["outcomes"].append(f"suspicious_rate={susp_rate:.4f} ✓")
    else:
        result["age_pct_within1"] = None
        result["warnings"].append("'dag' column missing; age progression not checked")

    # Education stability (working-age 25–60)
    if "deh" in s1.columns and "deh" in s2.columns:
        wa_mask = (s1["dag"] >= 25) & (s1["dag"] <= 60) if "dag" in s1.columns else pd.Series(True, index=s1.index)
        if wa_mask.sum() > 0:
            educ_ok = float((s1.loc[wa_mask, "deh"] == s2.loc[wa_mask, "deh"]).mean())
            result["educ_stability_wa"] = educ_ok
            result["outcomes"].append(
                f"educ_stability (age 25-60)={educ_ok:.4f}"
            )

    # Household continuity
    if "idorighh" in s1.columns and "idorighh" in s2.columns:
        hh_cont = float((s1["idorighh"] == s2["idorighh"]).mean())
        result["hh_continuity"] = hh_cont
        if hh_cont < THRESHOLDS["hh_continuity_min"]:
            result["warnings"].append(
                f"hh_continuity={hh_cont:.4f} < {THRESHOLDS['hh_continuity_min']}"
            )
        else:
            result["outcomes"].append(f"hh_continuity={hh_cont:.4f} ✓")

    return result


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _write_markdown(
    results: List[dict],
    out_path: Path,
    config: str,
    file_path: Path,
    ts: str,
) -> None:
    lines = [
        "# M1 Identity Validation Summary",
        "",
        f"**Config:** {config}",
        f"**Source:** {file_path}",
        f"**Generated:** {ts}",
        f"**Reference:** §13 of JMP_multi_year_stage_M1_implementation_plan_v2.md",
        "",
        "---",
        "",
        "## Thresholds Applied",
        "",
        "| Criterion | Threshold | Action |",
        "| --- | --- | --- |",
        f"| Sex stability (`dgn`) | ≥ {THRESHOLDS['sex_stability_min']:.4f} | warn |",
        f"| Age progression within ±1 | ≥ {THRESHOLDS['age_progression_min']:.4f} | warn |",
        f"| Suspicious records (warn) | ≤ {THRESHOLDS['suspicious_warn_max']:.4f} | warn |",
        f"| Suspicious records (block) | > {THRESHOLDS['suspicious_block_max']:.4f} | BLOCK |",
        f"| Household continuity | ≥ {THRESHOLDS['hh_continuity_min']:.4f} | warn |",
        "",
        "---",
        "",
        "## Results by Year Pair",
        "",
    ]

    any_blocked = False

    for r in results:
        pair = r["pair"]
        n_repeat = r["n_repeat_persons"]
        status = "BLOCKED" if r["blocked"] else ("PASS" if not r["warnings"] else "PASS (with warnings)")
        if r["blocked"]:
            any_blocked = True

        lines.append(f"### {pair}")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Repeat persons | {n_repeat:,} |")
        lines.append(f"| Repeat households | {r['n_repeat_households']:,} |")
        lines.append(f"| Expected repeat hh (addendum v2) | {r['expected_repeat_hh']} |")

        for key in ["sex_stability", "age_pct_within1", "suspicious_rate", "hh_continuity", "educ_stability_wa"]:
            if key in r and r[key] is not None:
                lines.append(f"| {key} | {r[key]:.4f} |")

        lines.append(f"| Overall status | **{status}** |")
        lines.append("")

        if r["outcomes"]:
            lines.append("**Outcomes:**")
            lines.append("")
            for o in r["outcomes"]:
                lines.append(f"- {o}")
            lines.append("")

        if r["warnings"]:
            lines.append("**Warnings:**")
            lines.append("")
            for w in r["warnings"]:
                lines.append(f"- {w}")
            lines.append("")

    lines.append("---")
    lines.append("")
    final_status = "BLOCKED" if any_blocked else "PASS"
    lines.append(f"## Final Status: {final_status}")
    lines.append("")
    if any_blocked:
        lines.append(
            "One or more year-pairs exceeded the block threshold for suspicious records. "
            "Do not proceed with pooled estimation."
        )
    else:
        lines.append(
            "All year-pairs passed the block threshold. "
            "Warnings (if any) are noted above and should be reviewed."
        )
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("Identity validation summary written: %s", out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_identity_validation(
    config: Optional[str] = None,
    file_path: Optional[str] = None,
) -> bool:
    if file_path:
        in_path = Path(file_path)
    elif config:
        in_path = POOLED_DIR / f"fr_{config.lower()}_stacked_raw.parquet"
    else:
        raise ValueError("Provide either --config or --file.")

    if not in_path.exists():
        raise FileNotFoundError(
            f"Stacked-raw parquet not found: {in_path}\n"
            "Run m1_stack_years.py first."
        )

    for col in ["idorigperson", "idorighh", "year_tag"]:
        pass  # checked after load

    LOGGER.info("Loading: %s", in_path)
    df = pd.read_parquet(in_path)
    LOGGER.info("Loaded %d rows.", len(df))

    for col in ["idorigperson", "idorighh", "year_tag"]:
        if col not in df.columns:
            raise KeyError(
                f"Required column '{col}' not found. "
                "Ensure m1_stack_years.py preserved raw IDs."
            )

    tags_present = sorted(df["year_tag"].unique())
    years_present = [TAG_YEAR.get(int(t), int(t)) for t in tags_present]
    LOGGER.info("Years in pooled file: %s", years_present)

    pair_results: List[dict] = []
    for i, t1 in enumerate(tags_present):
        for t2 in tags_present[i+1:]:
            yr1 = TAG_YEAR.get(int(t1), int(t1))
            yr2 = TAG_YEAR.get(int(t2), int(t2))
            LOGGER.info("Diagnosing pair %d→%d ...", yr1, yr2)
            r = _diagnose_pair(df, yr1, yr2)
            pair_results.append(r)
            LOGGER.info(
                "  repeat_persons=%d  suspicious_rate=%s  blocked=%s",
                r["n_repeat_persons"],
                f"{r.get('suspicious_rate', 'N/A'):.4f}" if isinstance(r.get('suspicious_rate'), float) else r.get('suspicious_rate', 'N/A'),
                r["blocked"],
            )

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / "M1_identity_validation_summary.md"
    _write_markdown(pair_results, out_path, config or "custom", in_path, ts)

    any_blocked = any(r["blocked"] for r in pair_results)
    if any_blocked:
        LOGGER.error("Identity validation BLOCKED: see %s", out_path)
        return False

    LOGGER.info("Identity validation PASSED.")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Stage M1 identity validation. Validates repeated persons and "
            "households across years using idorigperson and idorighh. "
            "Writes Results/M1_identity_validation_summary.md."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        choices=["p2", "p3a", "p3b", "p4"],
        help="Config (resolves to canonical stacked-raw parquet).",
    )
    group.add_argument(
        "--file",
        type=str,
        help="Explicit path to stacked-raw parquet.",
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
        ok = run_identity_validation(
            config=getattr(args, "config", None),
            file_path=getattr(args, "file", None),
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()