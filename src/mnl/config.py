"""Utilities for loading and validating experiment configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


@dataclass
class EstimationConfig:
    """Typed configuration for an estimation experiment."""

    data_path: Path
    features: list[str]
    choice_column: str
    individual_id_column: str
    alternative_id_column: str
    weights_column: str | None = None


def load_config(path: str | Path) -> EstimationConfig:
    """Load a YAML config file into an `EstimationConfig` instance."""
    raw = _read_yaml(path)
    try:
        return EstimationConfig(
            data_path=Path(raw["data"]["preprocessed_path"]),
            features=list(raw["model"]["features"]),
            choice_column=str(raw["model"]["choice_column"]),
            individual_id_column=str(raw["model"]["individual_id_column"]),
            alternative_id_column=str(raw["model"]["alternative_id_column"]),
            weights_column=raw["model"].get("weights_column"),
        )
    except KeyError as exc:  # pragma: no cover - defensive programming
        missing = exc.args[0]
        raise KeyError(f"Missing required config field: {missing}") from exc


def _read_yaml(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


