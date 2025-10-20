from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_ENV_HINTS = ("MNL_STORAGE_ROOT", "MNL_DATA_ROOT", "MNL_ROOT")


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

    Resolution order:
    1. Environment hints (MNL_STORAGE_ROOT, MNL_DATA_ROOT, MNL_ROOT)
    2. U:/EUROMOD-STORAGE (network stash)
    3. Repo-adjacent directories
    """
    preferred: list[Path] = []
    for candidate in _collect_candidates():
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
    for rel in (
        Path("EUROMOD_RELEASES_J1.0+") / "EUROMOD_RELEASES_J1.0+",
        Path("EUROMOD_RELEASES_J1.0+"),
    ):
        candidate = storage / rel
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "EUROMOD release directory not found. "
        "Set MNL_EUROMOD_ROOT to the extracted release folder."
    )


def ensure_dir(path: Path) -> Path:
    """Create the directory if it does not exist and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
