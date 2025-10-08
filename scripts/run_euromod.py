"""CLI helper to run EUROMOD systems via the official Python bindings."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Any

import pandas as pd

from mnl.integration import EuromodConnector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a EUROMOD system simulation.")
    parser.add_argument(
        "--model-dir",
        type=Path,
        required=True,
        help="Path to the EUROMOD installation or release folder (e.g. C:/EUROMOD_RELEASE).",
    )
    parser.add_argument("--country", type=str, required=True, help="ISO country code (e.g. DE, FR).")
    parser.add_argument(
        "--system",
        type=str,
        required=True,
        help="System identifier within the country (e.g. DE_2023).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset name as registered in EUROMOD (e.g. EU-SILC_2021).",
    )
    parser.add_argument(
        "--input-data",
        type=Path,
        default=None,
        help="Optional CSV/TSV file overriding the EUROMOD dataset contents.",
    )
    parser.add_argument(
        "--data-sep",
        type=str,
        default=None,
        help="Column separator for --input-data (auto-detected by extension when omitted).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Custom directory to read EUROMOD datasets from (defaults to <model-dir>/Input).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to store EUROMOD outputs (passed as `outputpath` to the simulation).",
    )
    parser.add_argument(
        "--option",
        action="append",
        default=[],
        help="Additional key=value pairs forwarded to `System.run`.",
    )
    return parser.parse_args()


def parse_options(items: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"Invalid option `{item}`. Expected key=value.")
        key, value = item.split("=", 1)
        raw_value = value.strip()
        try:
            parsed_value = ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            parsed_value = raw_value
        options[key.strip()] = parsed_value
    return options


def load_override(path: Path, sep: str | None) -> pd.DataFrame:
    if sep is None:
        if path.suffix.lower() in {".tsv", ".txt"}:
            sep = "\t"
        else:
            sep = ","
    return pd.read_csv(path, sep=sep)


def main() -> None:
    args = parse_args()
    options = parse_options(args.option)
    data = load_override(args.input_data, args.data_sep) if args.input_data else None
    connector = EuromodConnector(model_directory=args.model_dir)
    simulation = connector.run_system(
        country_code=args.country,
        system_name=args.system,
        dataset_name=args.dataset,
        data=data,
        data_directory=args.data_dir,
        output_directory=args.output_dir,
        run_kwargs=options,
    )
    output_keys = list(simulation.outputs.keys())
    print(f"EUROMOD simulation completed. Outputs available: {output_keys}")


if __name__ == "__main__":
    main()
