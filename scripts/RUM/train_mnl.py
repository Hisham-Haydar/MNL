"""CLI entry point to run the default estimation pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from mnl.config import load_config
from mnl.pipelines import run_estimation_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run discrete-choice estimation pipeline.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/default.yaml"),
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Override the data path specified in the config file.",
    )
    parser.add_argument(
        "--save-probabilities",
        type=Path,
        default=None,
        help="Optional path to persist predicted probabilities.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    metrics = run_estimation_pipeline(
        config=config,
        raw_data_path=args.data,
        save_probabilities_to=args.save_probabilities,
    )
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")


if __name__ == "__main__":
    main()

