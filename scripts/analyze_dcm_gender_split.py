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
from pathlib import Path
from typing import List

from analyze_dcm_results import process_gender
from path_helpers import reports_root

DEFAULT_BASE = reports_root() / "mle_dcm" / "boxcox" / "pooled_genderSplit"
MODEL_PREFIX = "boxcox_pooled_genderSplit"


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
    return parser.parse_args()


def analyze_gender(
    gender: str,
    variant: str,
    source: str,
    base_dir: Path,
    annotate_flag: bool,
) -> dict[str, object]:
    if gender != "pooled":
        raise ValueError("Gender-split analyzer only supports the pooled output.")

    out_dir = base_dir / f"{gender}_{variant}"
    model_name = f"{MODEL_PREFIX}_{variant}".replace(".", "_")
    param_csv = out_dir / f"{model_name}_parameters.csv"
    if not param_csv.exists():
        raise FileNotFoundError(f"Parameter file not found: {param_csv}")

    return process_gender(
        gender=gender,
        variant=variant,
        param_csv=param_csv,
        out_dir=out_dir,
        source=source,
        annotate_biogeme_html_flag=annotate_flag,
    )


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

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
