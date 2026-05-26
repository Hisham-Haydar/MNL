"""
Shared path resolution for all bpool scripts.

All paths are resolved from ~/.mnl/config.yaml or MNL_STORAGE_ROOT env var
via path_helpers. No hardcoded drive letters or UNC paths here.

See docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make path_helpers importable whether bpool is run directly or as a module
_script_dir = Path(__file__).resolve().parent
_enhanced_dir = _script_dir.parent / "enhanced"
for _p in (_script_dir, _enhanced_dir, _script_dir.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from path_helpers import (  # noqa: E402
    data_root,
    resolve_storage_root,
    euromod_root,
    resolve_repo_root,
)


def bpool_dir() -> Path:
    """new_data/ directory under storage root — bpool intermediates live here."""
    return resolve_storage_root() / "new_data"


def em_root() -> Path:
    """EUROMOD release directory (user-installed; configured via mnl-setup)."""
    return euromod_root()


def raw_data_dir() -> Path:
    """Raw EUROMOD microdata directory (Data/FR under storage root)."""
    return data_root() / "FR"


def processed_fr(year: int) -> Path:
    """Convenience: Data/processed/fr/<year>/fr_<year>.parquet."""
    return data_root() / "processed" / "fr" / str(year) / f"fr_{year}.parquet"


FR_PARQUETS: dict[int, Path] = {
    2015: processed_fr(2015),
    2016: processed_fr(2016),
    2017: processed_fr(2017),
}

REPO_ROOT: Path = resolve_repo_root()
# Pooled stage-M1 data lives under the storage root (not the repo working tree),
# so the package contains no data. Migrated 2026-05-26 from
# <repo>/Data/processed/fr/pooled  ->  <storage>/Data/processed/fr/pooled.
POOLED_DATA_DIR: Path = data_root() / "processed" / "fr" / "pooled"
