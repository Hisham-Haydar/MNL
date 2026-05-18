from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")


def euromod_raw_root() -> Path:
    """Return the EUROMOD raw micro-data directory, honouring env override."""
    env = os.environ.get("EUROMOD_RAW")
    if env:
        return Path(env).expanduser()
    # fall back to the resolved Data root
    return data_root() / "raw"


# Default mapping: input microdata year -> EUROMOD policy system year
DE_DEFAULT_SYSTEMS = {
    2014: 2013,
    2015: 2014,
    2016: 2015,
}

# Map microdata input year -> underlying income year (per your note)
DE_INCOME_YEAR = {
    2014: 2013,  # DE_2014_a3 reflects income 2013
    2015: 2014,  # DE_2015_a1 reflects income 2014
    2016: 2015,  # DE_2016_a1 reflects income 2015
}


def _collect_candidates() -> tuple[Path, ...]:
    """Return possible roots that might hold the heavy data/artifacts."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    seen: set[Path] = set()
    candidates: list[Path] = []

    def add(path: Path | str | None) -> None:
        if not path:
            return
        candidate = Path(path).expanduser()
        try:
            resolved = candidate.resolve(strict=False)
        except OSError:
            resolved = candidate
        if resolved in seen:
            return
        seen.add(resolved)
        candidates.append(resolved)

    add(repo_root)
    add(repo_root.parent)
    add(script_dir)
    add(script_dir.parent)

    for env in _ENV_HINTS:
        raw = os.environ.get(env)
        if raw:
            env_path = Path(raw).expanduser()
            add(env_path)
            add(env_path.parent)

    add("U:/EUROMOD-STORAGE")
    add(Path.home() / "EUROMOD-STORAGE")

    return tuple(candidates)


@lru_cache(maxsize=1)
def resolve_repo_root() -> Path:
    """Locate the repository root (where .git or scripts reside)."""
    script_dir = Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if (parent / ".git").exists():
            return parent
    return script_dir.parent


@lru_cache(maxsize=1)
def resolve_storage_root() -> Path:
    """
    Locate the external storage root that still contains the heavy data.

    Resolution order (prefer external shares before repo):
    1. Environment hints (MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT)
    2. U:/EUROMOD-STORAGE (network stash)
    3. ~/EUROMOD-STORAGE
    4. Repo-adjacent directories
    """
    preferred: list[Path] = []

    # 1) Environment hints first
    env_candidates: list[Path] = []
    for env in _ENV_HINTS:
        raw = os.environ.get(env)
        if raw:
            env_path = Path(raw).expanduser()
            env_candidates.append(env_path)
            env_candidates.append(env_path.parent)

    # 2) Explicit external locations
    explicit_candidates = [
        Path(r"U:/EUROMOD-STORAGE"),
        Path.home() / "EUROMOD-STORAGE",
    ]

    # 3) Repo-adjacent candidates (original order from _collect_candidates)
    repo_candidates = [c for c in _collect_candidates() if c not in env_candidates and c not in explicit_candidates]

    for candidate in env_candidates + explicit_candidates + repo_candidates:
        data_dir = candidate / "Data"
        if data_dir.exists():
            if (data_dir / "processed").exists() or (data_dir / "raw").exists():
                return candidate
            preferred.append(candidate)
        if candidate.name.lower() == "data" and candidate.exists():
            if (candidate / "processed").exists() or (candidate / "raw").exists():
                return candidate.parent
            preferred.append(candidate.parent)
    if preferred:
        return preferred[0]
    raise FileNotFoundError(
        "Unable to locate a storage root containing 'Data'. "
        "Set MNL_DATA_ROOT or MNL_STORAGE_ROOT to the base directory."
    )


@lru_cache(maxsize=1)
def data_root() -> Path:
    """Return the resolved Data directory."""
    storage = resolve_storage_root()
    data_dir = storage / "Data"
    if data_dir.exists():
        return data_dir
    if storage.name.lower() == "data":
        return storage
    raise FileNotFoundError("Resolved storage root does not contain 'Data'.")


@lru_cache(maxsize=1)
def reports_root() -> Path:
    """Return the reports directory (created lazily by callers)."""
    storage = resolve_storage_root()
    reports_dir = storage / "reports"
    return reports_dir


@lru_cache(maxsize=1)
def outputs_root() -> Path:
    """Return the outputs directory (created lazily by callers)."""
    storage = resolve_storage_root()
    return storage / "outputs"


@lru_cache(maxsize=1)
def euromod_root() -> Path:
    """Return the EUROMOD release directory, honouring env overrides."""
    env = os.environ.get("MNL_EUROMOD_ROOT")
    if env:
        env_path = Path(env).expanduser()
        if env_path.exists():
            return env_path
    storage = resolve_storage_root()
    # Common release layouts
    for rel in (
        Path("EUROMOD_RELEASES_J1.0+") / "EUROMOD_RELEASES_J1.0+",
        Path("EUROMOD_RELEASES_J1.0+"),
        Path("EUROMOD_RELEASES"),
        Path("euromod_releases"),
    ):
        candidate = storage / rel
        if candidate.exists():
            return candidate
    # Fallback: scan immediate subdirs of storage (and storage/Data) for anything containing 'euromod'
    search_roots = [storage, storage / "Data"]
    for root in search_roots:
        if root.exists():
            for child in root.iterdir():
                if child.is_dir() and "euromod" in child.name.lower():
                    return child
    raise FileNotFoundError(
        "EUROMOD release directory not found. "
        "Set MNL_EUROMOD_ROOT to the extracted release folder."
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
