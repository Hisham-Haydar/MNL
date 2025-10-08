"""Top-level package for structural discrete-choice estimation."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mnl")
except PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.0.0"

__all__ = ["__version__"]

