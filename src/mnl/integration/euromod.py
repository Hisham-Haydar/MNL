"""Utilities to interact with EUROMOD via the official Python package."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import Any

import pandas as pd


class EuromodConnectorError(RuntimeError):
    """Raised when the EUROMOD Python bindings are unavailable or misconfigured."""


def ensure_euromod_package() -> Any:
    """Import and return the `euromod` module, raising a friendly error otherwise."""

    try:
        return import_module("euromod")
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive guard
        raise EuromodConnectorError(
            "The `euromod` package is not installed. Install extras via "
            "`pip install -e '.[euromod]'` or `pip install euromod`."
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise EuromodConnectorError(
            "Failed to import the `euromod` package. Ensure the desktop EUROMOD application "
            "is installed and the DLL path is accessible (set `EUROMOD_PATH` if needed)."
        ) from exc


@dataclass
class EuromodConnector:
    """Thin wrapper around the official `euromod` package."""

    model_directory: Path
    _model: Any | None = field(default=None, init=False, repr=False)

    def _load_model(self, *, force_reload: bool = False) -> Any:
        module = ensure_euromod_package()
        if force_reload or self._model is None:
            try:
                model_cls = getattr(module, "Model")
            except AttributeError as exc:
                raise EuromodConnectorError(
                    "Installed `euromod` package does not expose `Model`. "
                    "Update the dependency or adjust the integration."
                ) from exc
            try:
                self._model = model_cls(str(self.model_directory))
            except Exception as exc:  # pragma: no cover - requires EUROMOD runtime
                raise EuromodConnectorError(
                    "Could not instantiate the EUROMOD model. Verify that the desktop EUROMOD "
                    "software is installed and `model_directory` points to a valid release."
                ) from exc
        return self._model

    def get_country(self, country_code: str) -> Any:
        """Return the `euromod.Country` instance for the given ISO country code."""

        model = self._load_model()
        try:
            return model[country_code]
        except KeyError as exc:
            raise EuromodConnectorError(
                f"Country `{country_code}` not found in EUROMOD model located at {self.model_directory}."
            ) from exc

    def get_system(self, country_code: str, system_name: str) -> Any:
        """Return a country-specific system (e.g. `DE_2023`)."""

        country = self.get_country(country_code)
        try:
            return country[system_name]
        except KeyError as exc:
            raise EuromodConnectorError(
                f"System `{system_name}` not available for country `{country_code}`."
            ) from exc

    def get_dataset(self, country_code: str, dataset_name: str) -> Any:
        """Return the dataset descriptor registered within the EUROMOD country model."""

        country = self.get_country(country_code)
        try:
            return country.datasets[dataset_name]
        except KeyError as exc:
            raise EuromodConnectorError(
                f"Dataset `{dataset_name}` not configured for country `{country_code}`."
            ) from exc

    def load_dataset_frame(
        self,
        country_code: str,
        dataset_name: str,
        *,
        data_directory: Path | None = None,
    ) -> pd.DataFrame:
        """Load a dataset into a pandas dataframe using EUROMOD readers."""

        country = self.get_country(country_code)
        dataset = self.get_dataset(country_code, dataset_name)
        try:
            source_identifier = getattr(dataset, "name", dataset_name)
            if data_directory is None:
                df = country.load_data(source_identifier)
            else:
                df = country.load_data(source_identifier, str(data_directory))
        except Exception as exc:  # pragma: no cover - depends on runtime data
            raise EuromodConnectorError(
                f"Failed to load dataset `{dataset_name}` (ID `{dataset.ID}`). "
                "Ensure the EUROMOD input files are accessible."
            ) from exc
        return df

    def run_system(
        self,
        *,
        country_code: str,
        system_name: str,
        dataset_name: str,
        data: pd.DataFrame | None = None,
        data_directory: Path | None = None,
        output_directory: Path | None = None,
        run_kwargs: dict[str, Any] | None = None,
    ) -> Any:
        """Execute a EUROMOD system simulation and return the `Simulation` object."""

        system = self.get_system(country_code, system_name)
        dataset = self.get_dataset(country_code, dataset_name)
        df = (
            data
            if data is not None
            else self.load_dataset_frame(country_code, dataset_name, data_directory=data_directory)
        )
        kwargs = dict(run_kwargs or {})
        if output_directory is not None:
            output_directory = output_directory.resolve()
            output_directory.mkdir(parents=True, exist_ok=True)
            kwargs.setdefault("outputpath", str(output_directory))
        try:
            return system.run(
                data=df,
                dataset_id=dataset.ID,
                **kwargs,
            )
        except Exception as exc:  # pragma: no cover - depends on EUROMOD runtime
            raise EuromodConnectorError(
                f"EUROMOD run failed for country `{country_code}`, system `{system_name}`, "
                f"dataset `{dataset_name}`."
            ) from exc
