"""Helpers to load discrete-choice datasets into canonical dataframes."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def load_raw_choice_data(path: str | Path, *, columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Load tabular choice data from CSV or TSV into a dataframe."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Choice dataset not found: {path}")

    sep = "\t" if path.suffix.lower() in {".tsv", ".txt"} else ","
    return pd.read_csv(path, sep=sep, usecols=list(columns) if columns else None)


def prepare_panel_data(
    df: pd.DataFrame,
    *,
    individual_id: str,
    choice_column: str,
    alternative_id: str,
) -> pd.DataFrame:
    """Validate and sort panel data in long format ready for estimation."""
    required = {individual_id, choice_column, alternative_id}
    missing = required - set(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df.copy()
    df.sort_values(by=[individual_id, alternative_id], inplace=True)
    return df.reset_index(drop=True)


