from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Resolution order (see docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md):
#   1. ~/.mnl/config.yaml          (user-level, machine-specific, never committed)
#   2. Environment variables        (MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT)
#   3. ~/EUROMOD-STORAGE            (legacy fallback — if it exists on disk)
#   4. FileNotFoundError            (clear error with setup instructions)
#
# Scripts must NEVER hardcode drive letters, UNC paths, or absolute paths.
# Use resolve_storage_root() / data_root() everywhere.
# ---------------------------------------------------------------------------

_USER_CONFIG = Path.home() / ".mnl" / "config.yaml"
_ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")


# Default mapping: input microdata year -> EUROMOD policy system year
DE_DEFAULT_SYSTEMS = {
    2014: 2013,
    2015: 2014,
    2016: 2015,
}

# Map microdata input year -> underlying income year
DE_INCOME_YEAR = {
    2014: 2013,
    2015: 2014,
    2016: 2015,
}


def _load_user_config() -> dict[str, Any]:
    """Read ~/.mnl/config.yaml if it exists; return empty dict otherwise."""
    if not _USER_CONFIG.exists():
        return {}
    try:
        import yaml  # type: ignore[import]
        with _USER_CONFIG.open() as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _candidate_is_storage_root(path: Path) -> bool:
    """Return True if path looks like a valid EUROMOD-STORAGE root."""
    data_dir = path / "Data"
    if data_dir.exists():
        return (data_dir / "processed").exists() or (data_dir / "raw").exists()
    if path.name.lower() == "data" and path.exists():
        return (path / "processed").exists() or (path / "raw").exists()
    return False


@lru_cache(maxsize=1)
def resolve_repo_root() -> Path:
    """Locate the repository root (directory containing .git)."""
    script_dir = Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if (parent / ".git").exists():
            return parent
    return script_dir.parent


@lru_cache(maxsize=1)
def resolve_storage_root() -> Path:
    """
    Locate the EUROMOD-STORAGE root containing Data/, interim/, etc.

    Resolution order:
      1. ~/.mnl/config.yaml  →  storage_root key
      2. Environment variables: MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT
      3. ~/EUROMOD-STORAGE   (legacy fallback)

    To configure, run:  mnl-setup
    To override ad-hoc: set MNL_STORAGE_ROOT=<path> before running.
    """
    candidates: list[Path] = []

    # 1) User config file
    cfg = _load_user_config()
    for key in ("storage_root", "data_root"):
        val = cfg.get(key)
        if val:
            p = Path(val).expanduser()
            if key == "data_root" and p.name.lower() == "data":
                p = p.parent  # normalise: config may point at .../Data directly
            candidates.append(p)

    # 2) Environment variables
    for env in _ENV_HINTS:
        raw = os.environ.get(env)
        if raw:
            p = Path(raw).expanduser()
            candidates.append(p)
            candidates.append(p.parent)

    # 3) Legacy ~/EUROMOD-STORAGE fallback
    candidates.append(Path.home() / "EUROMOD-STORAGE")

    seen: set[Path] = set()
    preferred: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=False)
        except OSError:
            resolved = candidate
        if resolved in seen:
            continue
        seen.add(resolved)
        if _candidate_is_storage_root(candidate):
            return candidate
        if candidate.exists():
            preferred.append(candidate)

    if preferred:
        return preferred[0]

    raise FileNotFoundError(
        "Cannot locate EUROMOD-STORAGE root.\n"
        "Run  mnl-setup  to configure your local data path, or set:\n"
        "  MNL_STORAGE_ROOT=<path/to/EUROMOD-STORAGE>\n"
        "See docs/package/RURO_DATA_STORAGE_AND_PATH_RESOLUTION.md for details."
    )


@lru_cache(maxsize=1)
def data_root() -> Path:
    """Return the Data/ directory under the resolved storage root."""
    storage = resolve_storage_root()
    data_dir = storage / "Data"
    if data_dir.exists():
        return data_dir
    if storage.name.lower() == "data":
        return storage
    raise FileNotFoundError(
        f"Storage root {storage} does not contain a 'Data' subdirectory.\n"
        "Run  mnl-setup --verify  to diagnose."
    )


@lru_cache(maxsize=1)
def reports_root() -> Path:
    """Return the reports/ directory under storage root (created lazily by callers)."""
    return resolve_storage_root() / "reports"


@lru_cache(maxsize=1)
def outputs_root() -> Path:
    """Return the outputs/ directory under storage root (created lazily by callers)."""
    return resolve_storage_root() / "outputs"


@lru_cache(maxsize=1)
def backup_root() -> Path | None:
    """Return the backup root from ~/.mnl/config.yaml, or None if not configured."""
    cfg = _load_user_config()
    val = cfg.get("backup_root") or os.environ.get("MNL_BACKUP_ROOT")
    if val:
        return Path(val).expanduser()
    return None


def euromod_raw_root() -> Path:
    """Return the EUROMOD raw micro-data directory, honouring env override."""
    env = os.environ.get("EUROMOD_RAW")
    if env:
        return Path(env).expanduser()
    return data_root() / "raw"


@lru_cache(maxsize=1)
def euromod_root() -> Path:
    """Return the EUROMOD release directory, honouring env and config overrides."""
    # Config file
    cfg = _load_user_config()
    cfg_val = cfg.get("euromod_root")
    if cfg_val:
        p = Path(cfg_val).expanduser()
        if p.exists():
            return p

    # Environment variable
    env = os.environ.get("MNL_EUROMOD_ROOT")
    if env:
        p = Path(env).expanduser()
        if p.exists():
            return p

    # Auto-discover under storage root
    storage = resolve_storage_root()
    for rel in (
        Path("EUROMOD_RELEASES_J1.0+") / "EUROMOD_RELEASES_J1.0+",
        Path("EUROMOD_RELEASES_J1.0+"),
        Path("EUROMOD_RELEASES"),
        Path("euromod_releases"),
    ):
        candidate = storage / rel
        if candidate.exists():
            return candidate

    for root in (storage, storage / "Data"):
        if root.exists():
            for child in root.iterdir():
                if child.is_dir() and "euromod" in child.name.lower():
                    return child

    raise FileNotFoundError(
        "EUROMOD release directory not found.\n"
        "Set MNL_EUROMOD_ROOT or add  euromod_root:  to ~/.mnl/config.yaml.\n"
        "EUROMOD releases are not bundled with the package — install separately."
    )


def ensure_dir(path: Path) -> Path:
    """Create the directory if it does not exist and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_local_workdir() -> Path:
    r"""
    Ensure GAMSPy uses a local working directory, not a UNC network path.

    Sets GAMSPY_WORKING_DIR to a local directory so GAMS solver files stay
    local, but does NOT change the process CWD. Changing CWD would redirect
    all subsequent relative-path saves away from the UNC repo root.
    Use MNL_LOCAL_WORKDIR env-var to override the default local path.
    """
    cwd = Path.cwd()
    anchor = cwd.anchor
    if anchor.startswith("\\\\"):
        target_raw = os.environ.get("MNL_LOCAL_WORKDIR")
        if target_raw:
            target = Path(target_raw).expanduser()
        else:
            target = Path.home() / "MNL_LOCAL_WORKDIR"
        target.mkdir(parents=True, exist_ok=True)
        # Do NOT os.chdir here — that would redirect relative saves away
        # from the UNC repo root.  GAMSPY_WORKING_DIR is sufficient.
        os.environ["GAMSPY_WORKING_DIR"] = str(target)
        print(
            "[path_helpers] INFO: Current directory is a UNC share "
            f"({cwd}); GAMSPY_WORKING_DIR set to {target} (CWD unchanged)."
        )
        return target
    return cwd
