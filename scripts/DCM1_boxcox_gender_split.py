#!/usr/bin/env python
"""
Estimate the pooled Box-Cox MNL with fully gender-split parameters.

This is a thin wrapper around scripts/DCM1_boxcox.py that:
- pools male & female datasets (ensuring aligned labels/columns),
- forces the gender-split + z-by-gender specification,
- writes outputs under reports/mle_dcm/boxcox/pooled_genderSplit/,
- triggers the dedicated analyzer via analyzer_runner.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from DCM1_boxcox import (
    detect_labels,
    estimate,
    load_wide_dataset,
    maybe_add_gender,
)
from path_helpers import data_root, reports_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate a pooled gender-split Box-Cox MNL (all parameters by gender)."
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        help="Scenario labels to include (default: detect from male dataset).",
    )
    parser.add_argument(
        "--auto-labels",
        action="store_true",
        help="Force automatic label detection even if --labels is provided.",
    )
    parser.add_argument(
        "--include-ascs",
        action="store_true",
        help="Include alternative-specific constants (base fixed).",
    )
    parser.add_argument(
        "--gender-column",
        default="dgn",
        help="Column containing gender indicator (0=male, 1=female).",
    )
    parser.add_argument(
        "--c-scale-quantile",
        type=float,
        default=0.99,
        help="Quantile used for consumption normalisation (default: 0.99).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=data_root() / "processed" / "scenarios",
        help="Directory containing heads_wide_single_{gender}_dcm parquet files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=reports_root() / "mle_dcm" / "boxcox" / "pooled_genderSplit",
        help="Base output directory (default: reports/mle_dcm/boxcox/pooled_genderSplit).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Logging verbosity.",
    )
    return parser.parse_args()


def build_pooled_dataframe(args: argparse.Namespace, labels_arg: tuple[str, ...] | None) -> tuple[pd.DataFrame, tuple[str, ...]]:
    male_path = args.data_dir / "heads_wide_single_male_dcm.parquet"
    female_path = args.data_dir / "heads_wide_single_female_dcm.parquet"
    male_df = maybe_add_gender(load_wide_dataset(male_path), 0.0, args.gender_column)
    female_df = maybe_add_gender(load_wide_dataset(female_path), 1.0, args.gender_column)

    labels = detect_labels(male_df, labels_arg)
    labels_f = detect_labels(female_df, labels)
    if labels != labels_f:
        raise ValueError(
            "Scenario labels differ between male and female datasets; align before pooling."
        )

    common_cols = sorted(set(male_df.columns).intersection(female_df.columns))
    if not common_cols:
        raise ValueError("Male and female datasets do not share common columns.")

    pooled_df = pd.concat(
        [male_df[common_cols], female_df[common_cols]],
        ignore_index=True,
        sort=False,
    )
    return pooled_df, labels


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(message)s")

    labels_arg = tuple(args.labels) if args.labels and not args.auto_labels else None
    pooled_df, labels = build_pooled_dataframe(args, labels_arg)

    variant = f"{'ascsON' if args.include_ascs else 'ascsOFF'}_q{int(round(args.c_scale_quantile * 100))}"
    output_dir = args.output_dir / f"pooled_{variant}"

    estimate(
        gender_key="pooled",
        df=pooled_df,
        labels=labels,
        include_ascs=args.include_ascs,
        gender_column=args.gender_column,
        output_dir=output_dir,
        log_level=getattr(logging, args.log_level.upper()),
        c_scale_quantile=args.c_scale_quantile,
        variant=variant,
        gender_split=True,
        z_by_gender=True,
        model_prefix="boxcox_pooled_genderSplit",
        analyzer_source="gender_split",
    )


if __name__ == "__main__":
    main()
