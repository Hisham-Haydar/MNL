"""
m1_identity_validation.py
=========================

Stage M1 — repeated-person and repeated-household identity diagnostics.

Reads a stacked-raw pooled parquet (output of m1_stack_years.py) and runs
identity-validation checks on all year-pairs that share observations.
Produces Results/M1_identity_validation_summary.md.

All country/year/config-specific values are read from a stage-config YAML.
Pass --stage-config config/multi_year/fr_p3a_stage_m1.yaml or use the
backward-compatible shortcut --config p3a.

Reference: docs/JMP_multi_year_stage_M1_implementation_plan_v2.md §13, 18.
           docs/JMP_multi_year_stage_M1_generalization_report_v1.md

Thresholds (§13 — read from config):
    sex_stability    >= sex_stability_min      warn if below; do not block
    age_progression  >= age_progression_min    warn if below; do not block
    suspicious       <= suspicious_warn_max    warn if exceeded
                     >  suspicious_block_max   block (exit 1)
    hh_continuity    >= hh_continuity_min      warn if below; do not block

Diagnostics are computed on raw_person_id_col and raw_household_id_col,
exactly as done in addendum v2.

Usage
-----
    python scripts/multi_year/m1_identity_validation.py --config p3a
    python scripts/multi_year/m1_identity_validation.py \\
        --stage-config config/multi_year/fr_p3a_stage_m1.yaml
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

# Ensure repo root is on sys.path so this script runs without PYTHONPATH set.
_SCRIPT_REPO = Path(__file__).resolve().parents[2]
if str(_SCRIPT_REPO) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_REPO))

from scripts.multi_year.m1_config import StageConfig, load_stage_config  # noqa: E402

LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-pair diagnostics
# ---------------------------------------------------------------------------

def _diagnose_pair(
    df: pd.DataFrame,
    yr1: int,
    yr2: int,
    cfg: StageConfig,
) -> dict:
    """
    Run identity diagnostics on one year pair.

    Returns a dict with all metrics and pass/fail/warn outcomes.
    """
    tag1 = cfg.year_tags[yr1]
    tag2 = cfg.year_tags[yr2]
    thr = cfg.identity_thresholds
    raw_person = cfg.raw_person_id_col
    raw_hh = cfg.raw_household_id_col

    sub1 = df[df["year_tag"] == tag1].copy()
    sub2 = df[df["year_tag"] == tag2].copy()

    persons1: set = set(sub1[raw_person].tolist())
    persons2: set = set(sub2[raw_person].tolist())
    repeat_persons = persons1 & persons2
    n_repeat = len(repeat_persons)

    hh1: set = set(sub1[raw_hh].tolist())
    hh2: set = set(sub2[raw_hh].tolist())
    repeat_hh = len(hh1 & hh2)

    overlap_key: Tuple[int, int] = (min(yr1, yr2), max(yr1, yr2))
    expected_overlap = cfg.expected_overlap_counts.get(overlap_key, "unknown")

    result: dict = {
        "pair": f"{yr1}->{yr2}",
        "yr1": yr1,
        "yr2": yr2,
        "n_persons_yr1": len(sub1),
        "n_persons_yr2": len(sub2),
        "n_repeat_persons": n_repeat,
        "n_repeat_households": repeat_hh,
        "expected_repeat_hh": expected_overlap,
        "outcomes": [],
        "warnings": [],
        "blocked": False,
    }

    if n_repeat == 0:
        result["outcomes"].append("PASS (no repeat persons -- disjoint panel)")
        return result

    # Build aligned repeat-person sub-DataFrames
    s1 = sub1[sub1[raw_person].isin(repeat_persons)].set_index(raw_person)
    s2 = sub2[sub2[raw_person].isin(repeat_persons)].set_index(raw_person)
    common_idx = s1.index.intersection(s2.index)
    s1 = s1.loc[common_idx]
    s2 = s2.loc[common_idx]

    gap = yr2 - yr1
    result["expected_age_gap"] = gap

    # Sex stability
    if "dgn" in s1.columns and "dgn" in s2.columns:
        sex_ok = float((s1["dgn"] == s2["dgn"]).mean())
        result["sex_stability"] = sex_ok
        if sex_ok < thr["sex_stability_min"]:
            result["warnings"].append(
                f"sex_stability {sex_ok:.4f} < {thr['sex_stability_min']}"
            )
        else:
            result["outcomes"].append(f"sex_stability={sex_ok:.4f}")
    else:
        result["sex_stability"] = None
        result["warnings"].append("'dgn' column missing; sex stability not checked")
        sex_ok = 1.0

    # Age progression
    if "dag" in s1.columns and "dag" in s2.columns:
        delta_dag = s2["dag"] - s1["dag"]
        pct_exact = float((delta_dag == gap).mean())
        pct_within1 = float(((delta_dag - gap).abs() <= 1).mean())
        result["age_pct_exact"] = pct_exact
        result["age_pct_within1"] = pct_within1

        result["delta_dag_dist"] = (
            delta_dag.value_counts().sort_index().head(10).to_dict()
        )

        if pct_within1 < thr["age_progression_min"]:
            result["warnings"].append(
                f"age_progression within_1: {pct_within1:.4f} < "
                f"{thr['age_progression_min']}"
            )
        else:
            result["outcomes"].append(
                f"age_progression_within1={pct_within1:.4f}"
            )

        # Suspicious records
        sex_mismatch = (
            (s1["dgn"] != s2["dgn"])
            if "dgn" in s1.columns
            else pd.Series(False, index=s1.index)
        )
        age_off = (delta_dag - gap).abs() > 1
        suspicious = sex_mismatch | age_off
        susp_rate = float(suspicious.mean())
        result["suspicious_rate"] = susp_rate
        result["suspicious_count"] = int(suspicious.sum())

        if susp_rate > thr["suspicious_block_max"]:
            result["blocked"] = True
            result["outcomes"].append(
                f"FAIL: suspicious_rate={susp_rate:.4f} > BLOCK threshold "
                f"{thr['suspicious_block_max']}"
            )
        elif susp_rate > thr["suspicious_warn_max"]:
            result["warnings"].append(
                f"suspicious_rate={susp_rate:.4f} > warn threshold "
                f"{thr['suspicious_warn_max']}"
            )
            result["outcomes"].append(f"suspicious_rate={susp_rate:.4f} WARN")
        else:
            result["outcomes"].append(f"suspicious_rate={susp_rate:.4f}")
    else:
        result["age_pct_within1"] = None
        result["warnings"].append("'dag' column missing; age progression not checked")

    # Education stability (working-age 25-60)
    if "deh" in s1.columns and "deh" in s2.columns:
        wa_mask = (
            (s1["dag"] >= 25) & (s1["dag"] <= 60)
            if "dag" in s1.columns
            else pd.Series(True, index=s1.index)
        )
        if wa_mask.sum() > 0:
            educ_ok = float((s1.loc[wa_mask, "deh"] == s2.loc[wa_mask, "deh"]).mean())
            result["educ_stability_wa"] = educ_ok
            result["outcomes"].append(
                f"educ_stability (age 25-60)={educ_ok:.4f}"
            )

    # Household continuity
    if raw_hh in s1.columns and raw_hh in s2.columns:
        hh_cont = float((s1[raw_hh] == s2[raw_hh]).mean())
        result["hh_continuity"] = hh_cont
        if hh_cont < thr["hh_continuity_min"]:
            result["warnings"].append(
                f"hh_continuity={hh_cont:.4f} < {thr['hh_continuity_min']}"
            )
        else:
            result["outcomes"].append(f"hh_continuity={hh_cont:.4f}")

    return result


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _write_markdown(
    results: List[dict],
    out_path: Path,
    config_name: str,
    file_path: Path,
    cfg: StageConfig,
    ts: str,
) -> None:
    thr = cfg.identity_thresholds
    lines = [
        "# M1 Identity Validation Summary",
        "",
        f"**Config:** {config_name}",
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
        f"| Sex stability (dgn) | >= {thr['sex_stability_min']:.4f} | warn |",
        f"| Age progression within +/-1 | >= {thr['age_progression_min']:.4f} | warn |",
        f"| Suspicious records (warn) | <= {thr['suspicious_warn_max']:.4f} | warn |",
        f"| Suspicious records (block) | > {thr['suspicious_block_max']:.4f} | BLOCK |",
        f"| Household continuity | >= {thr['hh_continuity_min']:.4f} | warn |",
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
        status = (
            "BLOCKED" if r["blocked"]
            else ("PASS" if not r["warnings"] else "PASS (with warnings)")
        )
        if r["blocked"]:
            any_blocked = True

        lines.append(f"### {pair}")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Repeat persons | {n_repeat:,} |")
        lines.append(f"| Repeat households | {r['n_repeat_households']:,} |")
        lines.append(f"| Expected repeat hh (addendum v2) | {r['expected_repeat_hh']} |")

        for key in ["sex_stability", "age_pct_within1", "suspicious_rate",
                    "hh_continuity", "educ_stability_wa"]:
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
    config_name: Optional[str] = None,
    stage_config_path: Optional[str] = None,
    file_path: Optional[str] = None,
) -> bool:
    cfg = load_stage_config(config_name, stage_config_path)

    if file_path:
        in_path = Path(file_path)
    else:
        in_path = cfg.stacked_raw_path()

    if not in_path.exists():
        raise FileNotFoundError(
            f"Stacked-raw parquet not found: {in_path}\n"
            "Run m1_stack_years.py first."
        )

    LOGGER.info("Loading: %s", in_path)
    df = pd.read_parquet(in_path)
    LOGGER.info("Loaded %d rows.", len(df))

    for col in [cfg.raw_person_id_col, cfg.raw_household_id_col, "year_tag"]:
        if col not in df.columns:
            raise KeyError(
                f"Required column '{col}' not found. "
                "Ensure m1_stack_years.py preserved raw IDs."
            )

    tags_present: List[int] = sorted(int(t) for t in df["year_tag"].unique())
    years_present = [cfg.tag_year.get(t, t) for t in tags_present]
    LOGGER.info("Years in pooled file: %s", years_present)

    pair_results: List[dict] = []
    for i, t1 in enumerate(tags_present):
        for t2 in tags_present[i+1:]:
            yr1 = cfg.tag_year.get(t1, t1)
            yr2 = cfg.tag_year.get(t2, t2)
            if yr1 not in cfg.year_tags or yr2 not in cfg.year_tags:
                LOGGER.warning(
                    "year_tags mapping missing for year %s or %s -- skipping pair",
                    yr1, yr2,
                )
                continue
            LOGGER.info("Diagnosing pair %d->%d ...", yr1, yr2)
            r = _diagnose_pair(df, yr1, yr2, cfg)
            pair_results.append(r)
            LOGGER.info(
                "  repeat_persons=%d  suspicious_rate=%s  blocked=%s",
                r["n_repeat_persons"],
                (f"{r['suspicious_rate']:.4f}"
                 if isinstance(r.get("suspicious_rate"), float)
                 else r.get("suspicious_rate", "N/A")),
                r["blocked"],
            )

    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = cfg.results_dir / "M1_identity_validation_summary.md"
    _write_markdown(
        pair_results, out_path,
        config_name or cfg.config_name,
        in_path, cfg, ts,
    )

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
            "households across years using raw person and household IDs. "
            "Writes Results/M1_identity_validation_summary.md.\n\n"
            "All thresholds and expected counts come from the stage-config YAML.\n"
            "Use --stage-config for an explicit path, or --config for a shortcut."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    config_group = ap.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config",
        type=str,
        help="Shortcut config name (e.g. p3a). Resolves to the canonical YAML.",
    )
    config_group.add_argument(
        "--stage-config",
        type=str,
        dest="stage_config",
        metavar="YAML_PATH",
        help="Explicit path to a stage-config YAML file.",
    )
    ap.add_argument(
        "--file",
        type=str,
        help="Explicit path to stacked-raw parquet (overrides config-derived path).",
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
    if not args.config and not args.stage_config and not args.file:
        LOGGER.error("Provide --config, --stage-config, or --file.")
        sys.exit(1)
    try:
        ok = run_identity_validation(
            config_name=getattr(args, "config", None),
            stage_config_path=getattr(args, "stage_config", None),
            file_path=getattr(args, "file", None),
        )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        LOGGER.error("%s", exc)
        sys.exit(1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()